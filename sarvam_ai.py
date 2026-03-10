"""
ArthSakshar AI – Sarvam AI Client (v3)
Text-to-Speech, Speech-to-Text, and Translation using Sarvam AI APIs.
Upgraded to bulbul:v3 (TTS) and saaras:v3 (STT).
"""

import httpx
import base64
import io
import logging
from config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "api-subscription-key": settings.SARVAM_API_KEY,
    "Content-Type": "application/json",
}


async def text_to_speech(text: str, language_code: str = "hi-IN", speaker: str = "meera") -> str | None:
    """
    Convert text to speech using Sarvam AI TTS API (bulbul:v3).
    Returns base64-encoded WAV audio string, or None on failure.

    Speakers: meera (female), arvind (male), amol, bhashini, diya, ...
    Language codes: hi-IN, mr-IN, en-IN, bn-IN, ta-IN, te-IN, etc.

    Note: bulbul:v3 does NOT support pitch/loudness params (v2 only).
    """
    payload = {
        "inputs": [text],
        "target_language_code": language_code,
        "speaker": speaker,
        "model": "bulbul:v3",
        "pace": 1.0,
        "enable_preprocessing": True,
        "sample_rate": 8000,  # 8kHz for telephony
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.SARVAM_TTS_URL,
                headers=HEADERS,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            audios = data.get("audios", [])
            if audios:
                logger.info(f"TTS success (bulbul:v3): {len(text)} chars → audio generated")
                return audios[0]
            return None
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None


async def text_to_speech_bytes(text: str, language_code: str = "hi-IN", speaker: str = "meera") -> bytes | None:
    """
    Convert text to speech and return raw WAV bytes (decoded from base64).
    Used by the /api/tts-audio endpoint to serve audio files to Twilio <Play>.
    """
    audio_b64 = await text_to_speech(text, language_code, speaker)
    if audio_b64:
        try:
            return base64.b64decode(audio_b64)
        except Exception as e:
            logger.error(f"Failed to decode TTS audio: {e}")
            return None
    return None


async def speech_to_text(audio_bytes: bytes, language_code: str | None = None) -> str | None:
    """
    Transcribe speech to text using Sarvam AI STT API (saaras:v3).
    Accepts raw audio bytes (WAV, MP3, etc.) and uploads as multipart file.
    Returns transcribed text string, or None on failure.

    If language_code is None, the API auto-detects the language.
    """
    try:
        headers = {
            "api-subscription-key": settings.SARVAM_API_KEY,
        }

        # Build multipart form data
        files = {
            "file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav"),
        }
        data = {
            "model": "saaras:v3",
            "with_timestamps": "false",
        }
        if language_code:
            data["language_code"] = language_code

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.SARVAM_STT_URL,
                headers=headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            result = response.json()
            transcript = result.get("transcript", "")
            detected_lang = result.get("language_code", "unknown")
            logger.info(f"STT success (saaras:v3): lang={detected_lang}, text='{transcript[:50]}...'")
            return transcript
    except Exception as e:
        logger.error(f"STT error: {e}")
        return None


async def transcribe_from_url(recording_url: str, language_code: str | None = None) -> str | None:
    """
    Download audio from a URL (e.g. Twilio recording) and transcribe it.
    Returns transcribed text string, or None on failure.
    """
    try:
        # Download the recording from Twilio
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Twilio recordings need auth
            resp = await client.get(
                recording_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            )
            resp.raise_for_status()
            audio_bytes = resp.content

        logger.info(f"Downloaded recording: {len(audio_bytes)} bytes from {recording_url[:60]}...")
        return await speech_to_text(audio_bytes, language_code)
    except Exception as e:
        logger.error(f"Transcribe from URL error: {e}")
        return None


async def translate_text(text: str, source_lang: str = "en-IN", target_lang: str = "hi-IN") -> str | None:
    """
    Translate text between languages using Sarvam AI Translate API.
    """
    payload = {
        "input": text,
        "source_language_code": source_lang,
        "target_language_code": target_lang,
        "model": "mayura:v1",
        "enable_preprocessing": True,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.SARVAM_TRANSLATE_URL,
                headers=HEADERS,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            translated = data.get("translated_text", "")
            logger.info(f"Translate success: '{text[:30]}' → '{translated[:30]}'")
            return translated
    except Exception as e:
        logger.error(f"Translate error: {e}")
        return None


async def generate_voice_response(text: str, language: str = "hindi") -> str | None:
    """
    High-level: generate a TTS audio for a given language name.
    Returns base64-encoded audio.
    """
    from scripts import LANGUAGE_CODES
    lang_code = LANGUAGE_CODES.get(language, "en-IN")

    # Choose appropriate speaker based on language
    speaker_map = {
        "mr-IN": "meera",
        "hi-IN": "meera",
        "en-IN": "meera",
    }
    speaker = speaker_map.get(lang_code, "meera")

    return await text_to_speech(text, lang_code, speaker)
