---
description: Analysis of MVP Stack vs Requested Stack and Next Steps to Scale
---

# Analysis of MVP Stack vs Master Prompt Stack

### 🛠️ 1. Stack Differences (Prompt vs. Actual Implementation)
| Component | Requested in Prompt | Currently Implemented in Code |
| :--- | :--- | :--- |
| **Telephony API** | Twilio / Exotel / Plivo | **Twilio** (Voice Webhooks) |
| **AI Brain / LLM** | GPT / Llama / Claude | **Keyword-based Intent Matching** (`faq_engine.py`) using Regex. *There is no actual LLM (like OpenAI/Claude) hooked up for dynamic conversation right now.* |
| **Speech-to-Text (STT)** | Deepgram / Whisper / Google | **Sarvam AI** (`saaras:v3`). It takes the Twilio recording URL and transcribes it. |
| **Text-to-Speech (TTS)** | ElevenLabs / Sarvam AI / Azure | **Twilio built-in TTS** (Google Wavenet & Amazon Polly). *Note: Sarvam AI TTS testing endpoints exist in the code, but the actual call flow uses Twilio's text-to-speech.* |
| **Database & Tracking** | PostgreSQL + Excel/Google Sheets | **SQLite** (`aiosqlite`) + **Local Excel** via `openpyxl` (`excel_manager.py`). |
| **Scale / Queueing** | Redis / RabbitMQ / Docker | **FastAPI `BackgroundTasks`**. (No Redis or external message brokers are being used yet). |

### ✅ 2. Functionalities That Are Ready (MVP Baseline)
You have successfully built the core mechanical pipeline. The following features are fully functional:
- **Twilio Voice Handshake:** Basic API `/voice` webhook handles incoming/outgoing call states correctly.
- **Language Selection:** DTMF keypad pressing (1 for Marathi, 2 for Hindi, 3 for English).
- **Call Flow & Scripts:** The standard civic pitch, introduction, and workshop details are being spoken aloud correctly using Twilio's TTS engines.
- **STT Processing:** Gathering user's spoken audio via Twilio `<Record>`, hitting the `/voice/process-speech` endpoint, and converting Marathi/Hindi audio to text using **Sarvam AI**.
- **Rule-based NLP (Intent Engine):** Recognizing basic FAQs, yes/no responses, and callback requests using keyword mapping.
- **Human Call Transfer:** Successfully identifies transfer requests and dials out to a predefined Human Agent number.
- **Tracking & Dashboard APIs:** Calls, campaign generation, and statuses are automatically saved to SQLite and logged synchronously to `call_responses.xlsx`.

### 🚀 3. Next Steps (What We Can Do Ahead)

**Phase 1: Polish the MVP (Before the 50-call trial)**
1. **Integrate an Actual LLM (Crucial):** Replace/supplement `detect_intent` with a call to OpenAI (GPT-4o-mini) or Claude 3.5 Haiku to answer queries dynamically and naturally.
2. **Switch TTS to a Premium Engine:** Weave **Sarvam AI TTS** (or ElevenLabs) into the call flow by streaming audio bytes instead of forcing Twilio to read text.
3. **Fix the Default Language:** Change the safety fallback from Hindi back to Marathi as requested in your prompt.

**Phase 2: Scale up for 65,000+ Calls**
1. **Queueing System:** Introduce **Redis** and **Celery** to pace the outbound calls correctly and respect Twilio's rate limits.
2. **Database Migration:** Move from SQLite (`aiosqlite`) to **PostgreSQL** to prevent locking issues when multiple worker nodes try to write call metrics simultaneously.
3. **Dockerization:** Containerize the application (`Dockerfile` and `docker-compose.yml`) so it can deploy on an AWS/GCP/Azure server easily.
