# 🇮🇳 ArthSakshar AI — Project Workflow Analysis

## Project Overview

**ArthSakshar AI** is an AI-powered, multilingual voice outreach system for **Maharashtra's Budget Literacy Initiative**. It automatically calls **65,000+ Chartered Accountants**, explains budget workshops in **Marathi/Hindi/English**, answers FAQs using keyword-based intent detection, escalates complex queries to an **LLM (GPT-4o-mini)**, and transfers unresolvable questions to a **human agent**.

| Aspect | Details |
|---|---|
| **Backend** | FastAPI (Python), Uvicorn |
| **Voice Calling** | Twilio Voice API (outbound + inbound) |
| **Speech-to-Text** | Sarvam AI `saaras:v3` |
| **Text-to-Speech** | Twilio built-in (Google Wavenet / Polly) |
| **LLM Fallback** | OpenAI GPT-4o-mini |
| **FAQ Engine** | Keyword-based intent detection (Marathi/Hindi/English) |
| **Database** | SQLite (aiosqlite, WAL mode) |
| **Tracking** | Excel (openpyxl, call_responses.xlsx) |
| **Dashboard** | Vanilla HTML/CSS/JS (premium dark theme) |
| **Languages** | Marathi, Hindi, English |

---

## 1. System Architecture (High-Level)

```mermaid
graph TB
    subgraph External["☁️ External Services"]
        TW["📞 Twilio Voice API"]
        SAR["🧠 Sarvam AI<br/>STT: saaras:v3<br/>TTS: bulbul:v3<br/>Translate: mayura:v1"]
        OAI["🤖 OpenAI<br/>GPT-4o-mini"]
    end

    subgraph Server["🖥️ FastAPI Server (port 8000)"]
        APP["app.py<br/>Webhooks + REST API"]
        FAQ["faq_engine.py<br/>Intent Detection"]
        LLM["llm_agent.py<br/>LLM Fallback"]
        SCR["scripts.py<br/>Multilingual Scripts"]
        CM["call_manager.py<br/>Bulk Campaign"]
        DB["database.py<br/>SQLite Layer"]
        XL["excel_manager.py<br/>Excel Tracking"]
        CFG["config.py<br/>Environment"]
    end

    subgraph Storage["💾 Persistence"]
        SQLITE[("arthsakshar.db<br/>Calls · Campaigns · Events")]
        EXCEL[("call_responses.xlsx<br/>Live Tracking Sheet")]
    end

    subgraph Frontend["🌐 Dashboard"]
        HTML["index.html"]
        CSS["style.css"]
        JS["dashboard.js"]
    end

    TW <-->|Webhooks| APP
    APP --> FAQ
    FAQ --> LLM
    APP --> SCR
    APP --> CM
    APP --> DB
    APP --> XL
    LLM --> OAI
    APP -->|STT| SAR
    DB --> SQLITE
    XL --> EXCEL
    CM --> TW
    HTML --> APP
    JS -->|REST API| APP

    style External fill:#1a1a2e,stroke:#e94560,color:#fff
    style Server fill:#16213e,stroke:#0f3460,color:#fff
    style Storage fill:#0f3460,stroke:#53354a,color:#fff
    style Frontend fill:#53354a,stroke:#e94560,color:#fff
```

---

## 2. End-to-End Call Flow (Main Workflow)

This is the **core workflow** of the entire system — from call initiation to completion.

```mermaid
flowchart TD
    START(["🚀 Call Initiated<br/>(Inbound or Campaign Outbound)"])
    
    START --> ENTRY["/voice Webhook<br/>Initialize Session<br/>Log call to DB"]
    
    ENTRY --> LANG["🌐 Language Selection<br/>DTMF: 1=Marathi, 2=Hindi, 3=English<br/>Speech: auto-detect keywords<br/>Default: Hindi (timeout)"]
    
    LANG --> LANGPROC["/voice/language<br/>Update session & DB"]
    
    LANGPROC --> INTRO["📢 Play Introduction<br/>(greeting → introduction →<br/>workshop_info → ask_interest)<br/>via Twilio TTS"]
    
    INTRO --> REC1["🎙️ Record User Speech<br/>max 15s, trim silence"]
    
    REC1 --> STT["🧠 Sarvam AI STT<br/>/voice/process-speech<br/>Download .wav from Twilio<br/>Transcribe via saaras:v3"]
    
    STT --> INTENT{"🎯 Intent Detection<br/>(keyword matching)"}
    
    INTENT -->|"TRANSFER<br/>(legal, document,<br/>complaint, etc.)"| XFER["📲 Transfer to Human Agent<br/>Dial HUMAN_AGENT_NUMBER<br/>Log: Transferred"]
    
    INTENT -->|"YES_INTERESTED<br/>(haan, sure, ho, etc.)"| YES["✅ Log Interest<br/>Fetch city events<br/>Say thank you + event info"]
    
    INTENT -->|"NO_INTERESTED<br/>(nahi, nako, nope, etc.)"| NO["❌ Log Decline<br/>Say polite goodbye"]
    
    INTENT -->|"CALLBACK<br/>(call back, later, etc.)"| CB["📋 Log Callback Request<br/>Promise to call back"]
    
    INTENT -->|"FAQ Match<br/>(cost, duration,<br/>eligibility, etc.)"| FAQANS["📖 FAQ Answer<br/>From knowledge base<br/>in user's language"]
    
    INTENT -->|"UNKNOWN<br/>(no keyword match)"| LLMCALL["🤖 LLM Fallback<br/>GPT-4o-mini with<br/>conversation history"]
    
    FAQANS --> TURN{"Turn Count<br/>< 5?"}
    LLMCALL --> TURN
    
    TURN -->|Yes| SPEAK["🔊 Speak Response<br/>via Twilio TTS"]
    SPEAK --> REC2["🎙️ Record Next Input"]
    REC2 --> STT
    
    TURN -->|"No (≥5 turns)"| ENDMSG["👋 Say Goodbye<br/>Max turns reached"]
    
    XFER --> DONE(["📊 Call Complete"])
    YES --> DONE
    NO --> DONE
    CB --> DONE
    ENDMSG --> DONE
    
    DONE --> XLLOG["📝 Log to Excel<br/>(call_responses.xlsx)"]
    DONE --> DBLOG["💾 Update SQLite<br/>(status, interest, etc.)"]

    style START fill:#e94560,stroke:#fff,color:#fff
    style INTENT fill:#f39c12,stroke:#fff,color:#000
    style XFER fill:#e74c3c,stroke:#fff,color:#fff
    style YES fill:#2ecc71,stroke:#fff,color:#fff
    style NO fill:#95a5a6,stroke:#fff,color:#fff
    style CB fill:#3498db,stroke:#fff,color:#fff
    style LLMCALL fill:#9b59b6,stroke:#fff,color:#fff
    style FAQANS fill:#1abc9c,stroke:#fff,color:#fff
    style DONE fill:#e94560,stroke:#fff,color:#fff
```

---

## 3. Intent Detection & Routing Pipeline

The FAQ engine uses a **priority-ordered keyword matching** system. Higher-priority intents (like `TRANSFER`) are checked first for safety.

```mermaid
flowchart LR
    INPUT["User Speech<br/>(transcribed text)"] --> LOWER["Lowercase &<br/>Strip"]
    
    LOWER --> P1{"🔴 TRANSFER?<br/>legal, document,<br/>court, lawyer..."}
    P1 -->|Match| R1["→ Dial Human Agent"]
    P1 -->|No| P2{"🟢 YES_INTERESTED?<br/>haan, sure, ho,<br/>interested..."}
    
    P2 -->|Match| R2["→ Log Interest +<br/>Event Info"]
    P2 -->|No| P3{"⚪ NO_INTERESTED?<br/>nahi, nako,<br/>not interested..."}
    
    P3 -->|Match| R3["→ Polite Decline"]
    P3 -->|No| P4{"🔵 CALLBACK?<br/>call back, later,<br/>baad mein..."}
    
    P4 -->|Match| R4["→ Schedule Callback"]
    P4 -->|No| P5{"🟡 FAQ?<br/>cost, duration,<br/>eligibility, when,<br/>where, about..."}
    
    P5 -->|Match| R5["→ FAQ Knowledge<br/>Base Answer"]
    P5 -->|No| P6{"🟣 GREETING?<br/>hello, namaste,<br/>namaskar..."}
    
    P6 -->|Match| R6["→ Greeting Script"]
    P6 -->|No| R7["🤖 UNKNOWN<br/>→ LLM Fallback<br/>(GPT-4o-mini)"]

    style INPUT fill:#2c3e50,stroke:#fff,color:#fff
    style R7 fill:#9b59b6,stroke:#fff,color:#fff
```

### Intent Priority Order (Highest → Lowest)

| Priority | Intent | Action | Keywords (Sample) |
|:---:|---|---|---|
| 1 | `TRANSFER` | Dial human agent | legal, document, court, lawyer, कानूनी, कायदेशीर |
| 2 | `YES_INTERESTED` | Log interest, share events | yes, haan, ho, sure, हाँ, होय |
| 3 | `NO_INTERESTED` | Log decline, goodbye | no, nahi, nako, नहीं, नाही |
| 4 | `CALLBACK` | Log callback request | call back, later, बाद में, नंतर |
| 5 | `COST` | FAQ: free program | cost, fee, price, शुल्क, किंमत |
| 6 | `DURATION` | FAQ: 2-3 hours | duration, how long, किती वेळ |
| 7 | `ELIGIBILITY` | FAQ: who can attend | eligible, who can, पात्रता, कोण |
| 8 | `SCHEDULE` | FAQ: date/timing | when, date, कब, केव्हा |
| 9 | `LOCATION` | FAQ: venue/place | where, venue, कहाँ, कुठे |
| 10 | `PROGRAM_DETAILS` | FAQ: about the program | details, information, माहिती, जानकारी |
| 11 | `GREETING` | Greeting response | hello, namaste, नमस्कार |
| 12 | `UNKNOWN` | **LLM Fallback** (GPT-4o-mini) | *(no match)* |

---

## 4. Campaign / Bulk Calling Pipeline

```mermaid
flowchart TD
    DASH["🖥️ Dashboard<br/>POST /api/campaigns/start"]
    
    DASH --> CREATE["Create Campaign<br/>in SQLite"]
    CREATE --> BG["🔄 Background Task<br/>run_campaign()"]
    
    BG --> LOAD["📊 Load Contacts<br/>from call_responses.xlsx<br/>(Name, Number columns)"]
    
    LOAD --> BATCH["Split into Batches<br/>(50 calls per batch)"]
    
    BATCH --> LOOP["For Each Contact<br/>in Batch"]
    
    LOOP --> CALL["📞 Twilio API<br/>calls.create()<br/>webhook → /voice"]
    CALL --> LOG["💾 Log Call to DB<br/>(call_sid, phone, name)"]
    LOG --> WAIT2["⏳ Wait 2s<br/>(between calls)"]
    WAIT2 --> LOOP
    
    LOOP -->|Batch Done| UPDATE["Update Campaign<br/>completed_calls count"]
    UPDATE --> WAIT10{"More<br/>Batches?"}
    WAIT10 -->|Yes| DELAY["⏳ Wait 10 min<br/>(anti-spam delay)"]
    DELAY --> LOOP
    WAIT10 -->|No| COMPLETE["✅ Campaign Complete"]

    style DASH fill:#3498db,stroke:#fff,color:#fff
    style CALL fill:#e94560,stroke:#fff,color:#fff
    style COMPLETE fill:#2ecc71,stroke:#fff,color:#fff
```

> [!IMPORTANT]
> **Rate Limiting**: Batches of 50 calls with 10-minute delays between batches and 2-second delays between individual calls to avoid telecom spam flags.

---

## 5. Speech Processing Pipeline (Sarvam AI)

```mermaid
sequenceDiagram
    participant User as 👤 CA (Phone)
    participant Twilio as 📞 Twilio
    participant App as 🖥️ FastAPI
    participant Sarvam as 🧠 Sarvam AI
    participant OpenAI as 🤖 OpenAI

    User->>Twilio: Speaks into phone
    Twilio->>Twilio: <Record> captures audio
    Twilio->>App: POST /voice/process-speech<br/>(RecordingUrl)
    App->>Twilio: GET RecordingUrl.wav<br/>(with auth)
    Twilio-->>App: Audio bytes (WAV)
    App->>Sarvam: POST /speech-to-text<br/>(file: audio.wav,<br/>model: saaras:v3)
    Sarvam-->>App: { transcript, language_code }
    
    alt Known Intent (keyword match)
        App->>App: FAQ / Script response
    else Unknown Intent
        App->>OpenAI: POST chat/completions<br/>(model: gpt-4o-mini,<br/>conversation history)
        OpenAI-->>App: LLM response (≤2 sentences)
    end
    
    App->>Twilio: TwiML <Say> response<br/>(Google Wavenet / Polly)
    Twilio->>User: Speaks response
```

---

## 6. Data Persistence & Dual Logging

The system maintains **two parallel persistence layers** — SQLite for structured querying and Excel for real-time operational tracking.

```mermaid
flowchart LR
    subgraph Events["Call Events"]
        E1["Call Started"]
        E2["Language Selected"]
        E3["Interest Expressed"]
        E4["Declined"]
        E5["Transfer"]
        E6["Callback"]
        E7["Call Ended"]
    end

    subgraph SQLite["💾 SQLite (arthsakshar.db)"]
        T1[("calls<br/>call_sid, phone, language,<br/>status, duration,<br/>interested, transferred,<br/>callback_requested")]
        T2[("campaigns<br/>name, status,<br/>total/completed calls")]
        T3[("events<br/>city, date, venue,<br/>coordinator")]
    end

    subgraph Excel["📊 Excel (call_responses.xlsx)"]
        XL1["Name | Number | Status |<br/>Interest | Follow Up |<br/>Transferred | Notes | Time"]
    end

    E1 & E2 --> T1
    E3 & E4 & E5 & E6 & E7 --> T1
    E3 & E4 & E5 & E6 & E7 --> XL1

    subgraph API["REST API (Dashboard)"]
        A1["GET /api/stats"]
        A2["GET /api/calls"]
        A3["GET /api/events"]
        A4["GET /api/campaigns"]
    end

    T1 --> A1 & A2
    T2 --> A4
    T3 --> A3

    style SQLite fill:#0f3460,stroke:#e94560,color:#fff
    style Excel fill:#53354a,stroke:#e94560,color:#fff
    style API fill:#16213e,stroke:#0f3460,color:#fff
```

> [!NOTE]
> Excel writes are protected by an `asyncio.Lock` to prevent concurrent write corruption. The Excel file serves dual duty — it's both the **contact source** for campaigns and the **live tracking destination** for call outcomes.

---

## 7. Session Management (In-Memory)

Each active call maintains an in-memory session (`call_sessions` dict) keyed by Twilio's `CallSid`:

```mermaid
stateDiagram-v2
    [*] --> language_selection: Call starts
    language_selection --> introduction: Language chosen
    introduction --> conversation: Introduction delivered
    conversation --> conversation: FAQ/LLM turn (max 5)
    conversation --> completed: Interest / Decline / Max turns
    conversation --> transferred: Transfer to human
    conversation --> callback: Callback requested
    completed --> [*]: Session cleaned up
    transferred --> [*]: Session cleaned up
    callback --> [*]: Session cleaned up
```

**Session Data Structure:**
```json
{
  "language": "marathi | hindi | english",
  "state": "language_selection | introduction | conversation",
  "turn_count": 0,
  "interested": false,
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

---

## 8. LLM Fallback Pathway

When the FAQ engine returns `UNKNOWN`, the system escalates to GPT-4o-mini with **full conversation history** for contextual responses:

```mermaid
flowchart TD
    UNK["Intent: UNKNOWN<br/>(no keyword match)"]
    
    UNK --> HIST["Load conversation<br/>history from session"]
    HIST --> BUILD["Build Messages:<br/>1. System prompt (language-specific)<br/>2. Previous user/assistant turns<br/>3. Current user message"]
    BUILD --> CALL["OpenAI API<br/>model: gpt-4o-mini<br/>temp: 0.7, max_tokens: 150"]
    CALL --> RESP["Response:<br/>≤2 sentences,<br/>strictly on-topic"]
    RESP --> SAVE["Append to session<br/>messages[] history"]

    style UNK fill:#9b59b6,stroke:#fff,color:#fff
    style CALL fill:#e74c3c,stroke:#fff,color:#fff
```

> [!TIP]
> The LLM is constrained by language-specific system prompts that enforce: (1) max 2 sentences, (2) budget-literacy topics only, (3) suggest human callback for complex questions.

---

## 9. File-by-File Module Summary

| File | Role | Key Functions |
|---|---|---|
| [app.py](file:///d:/Projects/arthsakshar-ai/app.py) | Main FastAPI server | Webhooks (`/voice`, `/voice/language`, `/voice/process-speech`, `/voice/conversation`, `/voice/status`), REST API, TTS voice config |
| [config.py](file:///d:/Projects/arthsakshar-ai/config.py) | Centralized config | Loads `.env` vars (Sarvam, Twilio, OpenAI, DB, rate limits) |
| [faq_engine.py](file:///d:/Projects/arthsakshar-ai/faq_engine.py) | Intent detection + FAQ KB | `detect_intent()`, `process_user_input()`, multilingual knowledge base |
| [llm_agent.py](file:///d:/Projects/arthsakshar-ai/llm_agent.py) | LLM fallback | `generate_response()` via GPT-4o-mini with conversation history |
| [sarvam_ai.py](file:///d:/Projects/arthsakshar-ai/sarvam_ai.py) | Sarvam AI client | STT (`saaras:v3`), TTS (`bulbul:v3`), Translation (`mayura:v1`) |
| [scripts.py](file:///d:/Projects/arthsakshar-ai/scripts.py) | Multilingual scripts | Greeting, intro, FAQ, fallback in Marathi/Hindi/English |
| [call_manager.py](file:///d:/Projects/arthsakshar-ai/call_manager.py) | Bulk calling | `run_campaign()` with batch processing & rate limiting |
| [database.py](file:///d:/Projects/arthsakshar-ai/database.py) | SQLite layer | CRUD for calls, campaigns, events; dashboard stats |
| [excel_manager.py](file:///d:/Projects/arthsakshar-ai/excel_manager.py) | Excel tracking | `log_call_response()` with phone-number dedup |
| [dashboard.py](file:///d:/Projects/arthsakshar-ai/dashboard.py) | Dashboard helpers | Additional dashboard utilities |

---

## 10. Key Architectural Decisions

| Decision | Rationale |
|---|---|
| **Twilio TTS** (not Sarvam TTS) for call responses | Eliminates HTTP round-trip latency; Twilio plays directly without downloading audio |
| **Sarvam AI STT** (not Twilio STT) for transcription | Superior Indic language support (Marathi, Hindi) with `saaras:v3` model |
| **Keyword-based intent** before LLM | Faster, cheaper, deterministic for common intents; LLM only for edge cases |
| **In-memory sessions** (dict) | Low-latency for active calls; acceptable since calls are ephemeral (max 5 turns) |
| **Dual persistence** (SQLite + Excel) | SQLite for dashboards/analytics; Excel for operational teams to monitor live |
| **Record-then-transcribe** pattern | More reliable than streaming STT for telephony; Twilio `<Record>` handles audio capture |
| **Max 5 conversation turns** | Keeps calls focused and cost-effective; prevents runaway API costs |
