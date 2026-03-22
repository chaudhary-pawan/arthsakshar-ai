"""
ArthSakshar AI – Main FastAPI Application
Twilio voice webhooks with Sarvam AI STT (saaras:v3) for transcription
and Twilio built-in TTS for speech. API endpoints and campaign dashboard.
"""

import asyncio
import json
import logging
import base64
from datetime import datetime
from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather

from config import settings
from scripts import (
    LANGUAGE_GREETING, LANGUAGE_MAP, LANGUAGE_CODES,
    get_script, get_full_introduction, get_event_info,
)
from faq_engine import detect_intent, process_user_input, Intent
import sarvam_ai
import llm_agent
import database as db
import call_manager
import excel_manager

# ─── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("arthsakshar.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("arthsakshar")

# ─── In-memory session store (call_sid → session data) ──────────
call_sessions: dict[str, dict] = {}
excel_lock = asyncio.Lock()

async def log_to_excel_safe(**kwargs):
    """Safely log to Excel using a lock to prevent concurrent write corruption."""
    async with excel_lock:
        await asyncio.to_thread(excel_manager.log_call_response, **kwargs)

# ─── TTS Voice Config ──────────────────────────────────────────
# Twilio built-in voices for reliable TTS (no extra HTTP needed)
TTS_VOICES = {
    "marathi": ("Google.mr-IN-Wavenet-B", "mr-IN"),
    "hindi": ("Google.hi-IN-Wavenet-B", "hi-IN"),
    "english": ("Polly.Joanna", "en-US"),
}


def get_voice(language: str):
    """Get Twilio voice name and language code for the given language."""
    return TTS_VOICES.get(language, ("Google.hi-IN-Wavenet-B", "hi-IN"))


# ─── Lifespan ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 ArthSakshar AI starting up...")
    await db.init_db()
    logger.info("✅ Database initialized")
    yield
    logger.info("ArthSakshar AI shutting down...")


# ─── FastAPI App ────────────────────────────────────────────────
app = FastAPI(
    title="ArthSakshar AI",
    description="AI-powered multilingual civic calling network for Maharashtra",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")


# ═══════════════════════════════════════════════════════════════
# TWILIO VOICE WEBHOOKS (Twilio TTS + Sarvam AI STT)
# ═══════════════════════════════════════════════════════════════

@app.api_route("/voice", methods=["GET", "POST"])
async def voice_entry(request: Request):
    """
    Main entry point for inbound/outbound calls.
    Greets user and asks for language selection.
    """
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    from_number = form.get("From", "")

    logger.info(f"📞 Call started: {call_sid} from {from_number}")

    # Initialize session
    call_sessions[call_sid] = {
        "language": None,
        "state": "language_selection",
        "turn_count": 0,
        "interested": False,
        "messages": [],
    }

    # Log the call
    await db.log_call(call_sid=call_sid, phone_number=from_number)

    # Ask for language selection
    response = VoiceResponse()
    gather = Gather(
        input="dtmf speech",
        timeout=5,
        num_digits=1,
        action="/voice/language",
        method="POST",
        speech_timeout="auto",
        language="hi-IN",
    )
    gather.say(LANGUAGE_GREETING, voice="Polly.Aditi", language="hi-IN")
    response.append(gather)

    # If no input, default to Hindi
    response.redirect("/voice/language?Digits=2", method="POST")

    return Response(content=str(response), media_type="application/xml")


@app.api_route("/voice/language", methods=["GET", "POST"])
async def voice_language(request: Request):
    """
    Process language selection and deliver the introduction.
    Plays introduction via Twilio TTS, then records user response for Sarvam AI STT.
    """
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    digits = form.get("Digits", "")
    speech_result = form.get("SpeechResult", "")

    # Determine language from DTMF or speech
    language = "hindi"  # default
    if digits in LANGUAGE_MAP:
        language = LANGUAGE_MAP[digits]
    elif speech_result:
        speech_lower = speech_result.lower()
        if any(w in speech_lower for w in ["marathi", "मराठी", "1", "एक", "ek", "one"]):
            language = "marathi"
        elif any(w in speech_lower for w in ["hindi", "हिंदी", "2", "दो", "do", "don", "दोन", "two"]):
            language = "hindi"
        elif any(w in speech_lower for w in ["english", "इंग्लिश", "3", "तीन", "teen", "three"]):
            language = "english"

    logger.info(f"🌐 Language selected: {language} (Call: {call_sid})")

    # Update session
    if call_sid in call_sessions:
        call_sessions[call_sid]["language"] = language
        call_sessions[call_sid]["state"] = "introduction"

    # Update DB
    await db.update_call(call_sid, language=language)

    # Build introduction in smaller chunks to avoid Twilio TTS cut-offs
    voice_name, voice_lang = get_voice(language)

    response = VoiceResponse()

    # Play introduction via Twilio TTS in pieces
    for key in ["greeting", "introduction", "workshop_info", "ask_interest"]:
        part = get_script(language, key)
        if part:
            response.say(part, voice=voice_name, language=voice_lang)

    # Record user's speech response (Sarvam AI will transcribe it)
    response.record(
        action="/voice/process-speech",
        method="POST",
        max_length=15,
        timeout=2,
        play_beep=False,
        trim="trim-silence",
    )

    # Fallback if no recording
    fallback_text = get_script(language, "fallback")
    response.say(fallback_text, voice=voice_name, language=voice_lang)
    response.redirect("/voice/conversation", method="POST")

    return Response(content=str(response), media_type="application/xml")


@app.api_route("/voice/process-speech", methods=["GET", "POST"])
async def voice_process_speech(request: Request):
    """
    Process recorded speech using Sarvam AI STT (saaras:v3).
    Called by Twilio after <Record> completes.
    Downloads the recording, transcribes via Sarvam AI, then processes intent.
    """
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    recording_url = form.get("RecordingUrl", "")

    session = call_sessions.get(call_sid, {"language": "hindi", "turn_count": 0, "messages": []})
    language = session.get("language", "hindi")
    lang_code = LANGUAGE_CODES.get(language, "hi-IN")
    turn = session.get("turn_count", 0)
    voice_name, voice_lang = get_voice(language)

    logger.info(f"🎙️ Recording received for call {call_sid}, turn {turn + 1}")

    # Transcribe using Sarvam AI STT (saaras:v3)
    transcript = ""
    if recording_url:
        wav_url = f"{recording_url}.wav"
        transcript = await sarvam_ai.transcribe_from_url(wav_url, lang_code) or ""

    logger.info(f"💬 Sarvam STT result: '{transcript}' | Lang: {language}")

    # Process through intent detection
    if transcript:
        intent, response_text = process_user_input(transcript, language)
        
        if intent == Intent.UNKNOWN:
            messages = session.get("messages", [])
            response_text = await llm_agent.generate_response(transcript, language, messages)
            messages.append({"role": "user", "content": transcript})
            messages.append({"role": "assistant", "content": response_text})
            session["messages"] = messages
    else:
        intent = Intent.UNKNOWN
        response_text = get_script(language, "fallback")

    logger.info(f"🧠 Intent: {intent} | Response: '{response_text[:60]}...'")

    # Update session
    session["turn_count"] = turn + 1

    response = VoiceResponse()

    # Handle different intents
    if intent == Intent.TRANSFER:
        response.say(response_text, voice=voice_name, language=voice_lang)
        dial = response.dial(
            timeout=30,
            caller_id=settings.TWILIO_PHONE_NUMBER,
        )
        dial.number(settings.HUMAN_AGENT_NUMBER)
        await db.update_call(call_sid, transferred=1, status="transferred")
        
        call_info = await db.get_call(call_sid)
        await log_to_excel_safe(
            phone=call_info.get("phone_number", ""),
            name=call_info.get("ca_name", ""),
            status="Transferred",
            interest="Need More Information",
            transferred="Yes",
            notes="Transferred to human agent for complex query"
        )
        logger.info(f"📲 Call transferred: {call_sid}")

    elif intent == Intent.YES_INTERESTED:
        session["interested"] = True
        await db.update_call(call_sid, interested=1)
        
        call_info = await db.get_call(call_sid)
        await log_to_excel_safe(
            phone=call_info.get("phone_number", ""),
            name=call_info.get("ca_name", ""),
            status="Completed",
            interest="Interested",
            follow_up="Yes",
            notes="Agreed to participate"
        )

        city = session.get("city", "")
        event_text = ""
        if city:
            events = await db.get_events(city)
            if events:
                evt = events[0]
                event_text = " " + get_event_info(
                    language, evt["city"], evt["event_date"],
                    evt["venue"], evt["coordinator_name"]
                )

        response.say(response_text + event_text, voice=voice_name, language=voice_lang)
        await db.update_call(call_sid, status="completed")

    elif intent == Intent.NO_INTERESTED:
        response.say(response_text, voice=voice_name, language=voice_lang)
        await db.update_call(call_sid, status="completed")
        
        call_info = await db.get_call(call_sid)
        await log_to_excel_safe(
            phone=call_info.get("phone_number", ""),
            name=call_info.get("ca_name", ""),
            status="Completed",
            interest="Not Interested",
            notes="Declined participation"
        )

    elif intent == Intent.CALLBACK:
        await db.update_call(call_sid, callback_requested=1, status="callback")
        response.say(response_text, voice=voice_name, language=voice_lang)
        
        call_info = await db.get_call(call_sid)
        await log_to_excel_safe(
            phone=call_info.get("phone_number", ""),
            name=call_info.get("ca_name", ""),
            status="Callback Requested",
            interest="Need More Information",
            follow_up="Yes",
            notes="Asked to call back later"
        )

    else:
        # Continue conversation — max 5 turns
        if turn >= 5:
            ending = {
                "english": "Thank you for your time. If you have more questions, please call us back. Have a great day!",
                "hindi": "आपके समय के लिए धन्यवाद। अधिक जानकारी के लिए हमें कॉल करें। शुभ दिन!",
                "marathi": "आपल्या वेळेबद्दल धन्यवाद. अधिक माहितीसाठी आम्हाला कॉल करा. शुभ दिवस!",
            }
            response.say(
                ending.get(language, ending["english"]),
                voice=voice_name, language=voice_lang,
            )
            await db.update_call(call_sid, status="completed")
        else:
            # Speak the response, then record next user input
            response.say(response_text, voice=voice_name, language=voice_lang)
            response.record(
                action="/voice/process-speech",
                method="POST",
                max_length=15,
                timeout=2,
                play_beep=False,
                trim="trim-silence",
            )

    # Update session
    call_sessions[call_sid] = session

    return Response(content=str(response), media_type="application/xml")


@app.api_route("/voice/conversation", methods=["GET", "POST"])
async def voice_conversation(request: Request):
    """
    Fallback conversation handler — plays fallback message and records.
    """
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    session = call_sessions.get(call_sid, {"language": "hindi", "turn_count": 0, "messages": []})
    language = session.get("language", "hindi")
    voice_name, voice_lang = get_voice(language)

    response = VoiceResponse()
    response.say(
        get_script(language, "fallback"),
        voice=voice_name, language=voice_lang,
    )
    response.record(
        action="/voice/process-speech",
        method="POST",
        max_length=15,
        timeout=5,
        play_beep=False,
        trim="trim-silence",
    )

    return Response(content=str(response), media_type="application/xml")


@app.api_route("/voice/status", methods=["GET", "POST"])
async def voice_status(request: Request):
    """Handle Twilio call status callbacks."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    status = form.get("CallStatus", "")
    duration = form.get("CallDuration", "0")

    logger.info(f"📊 Call status: {call_sid} → {status} ({duration}s)")

    if status in ("completed", "no-answer", "busy", "failed", "canceled"):
        await db.update_call(call_sid, status=status, duration=int(duration or 0))
        
        # If call failed/busy, update Excel right away
        if status in ("no-answer", "busy", "failed", "canceled"):
            call_info = await db.get_call(call_sid)
            await log_to_excel_safe(
                phone=call_info.get("phone_number", ""),
                name=call_info.get("ca_name", ""),
                status=status.capitalize(),
                notes=f"Call ended with status: {status}"
            )
            
        call_sessions.pop(call_sid, None)

    return Response(content="<Response/>", media_type="application/xml")


# ═══════════════════════════════════════════════════════════════
# REST API ENDPOINTS (Dashboard)
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def dashboard():
    """Serve the dashboard HTML."""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.get("/api/stats")
async def api_stats():
    """Get dashboard statistics."""
    stats = await db.get_dashboard_stats()
    return JSONResponse(stats)


@app.get("/api/calls")
async def api_calls(limit: int = 50):
    """Get recent call logs."""
    calls = await db.get_calls(limit)
    for call in calls:
        for key in ("created_at", "updated_at"):
            if call.get(key) and not isinstance(call[key], str):
                call[key] = str(call[key])
    return JSONResponse(calls)


@app.get("/api/events")
async def api_events(city: str = None):
    """Get events, optionally filtered by city."""
    events = await db.get_events(city)
    return JSONResponse(events)


@app.get("/api/campaigns")
async def api_campaigns():
    """Get all campaigns."""
    campaigns = await db.get_campaigns()
    for c in campaigns:
        for key in ("created_at", "updated_at"):
            if c.get(key) and not isinstance(c[key], str):
                c[key] = str(c[key])
    return JSONResponse(campaigns)


@app.post("/api/campaigns/start")
async def api_start_campaign(request: Request, background_tasks: BackgroundTasks):
    """Start a new bulk calling campaign drawing directly from the Excel file."""
    body = await request.json()
    name = body.get("name", f"Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    campaign_id = await db.create_campaign(name, total_calls=0)
    # Defaulting to the central Excel file configured in call_manager
    background_tasks.add_task(call_manager.run_campaign, campaign_id)

    return JSONResponse({
        "status": "started",
        "campaign_id": campaign_id,
        "message": f"Campaign '{name}' started. Calls will begin shortly.",
    })


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "ArthSakshar AI",
        "version": "2.0.0",
        "tts_engine": "Twilio (Google Wavenet / Polly)",
        "stt_engine": "Sarvam AI saaras:v3",
        "timestamp": datetime.now().isoformat(),
    })


# ═══════════════════════════════════════════════════════════════
# SARVAM AI TEST ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/test-tts")
async def test_tts(text: str = "नमस्कार, मी अर्थसाक्षर AI बोलत आहे.", lang: str = "mr-IN"):
    """Test Sarvam AI Text-to-Speech."""
    audio_b64 = await sarvam_ai.text_to_speech(text, lang)
    if audio_b64:
        return JSONResponse({
            "status": "success",
            "model": "bulbul:v3",
            "text": text,
            "language": lang,
            "audio_length": len(audio_b64),
            "audio_preview": audio_b64[:100] + "...",
        })
    return JSONResponse({"status": "error", "message": "TTS failed"}, status_code=500)


@app.get("/api/tts-audio")
async def tts_audio(text: str, lang: str = "hi-IN"):
    """
    Generate TTS audio using Sarvam AI and return WAV file.
    Can be used for testing or direct audio playback.
    """
    audio_bytes = await sarvam_ai.text_to_speech_bytes(text, lang)
    if audio_bytes:
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=tts.wav"},
        )
    logger.error(f"TTS failed for text: '{text[:50]}...'")
    return Response(content=b"", media_type="audio/wav", status_code=500)


# ─── Entry Point ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
