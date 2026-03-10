# 🇮🇳 ArthSakshar AI – Maharashtra's AI Civic Calling Network

An AI-powered, multilingual voice outreach system for Maharashtra's Budget Literacy Initiative. Automatically calls 65,000+ Chartered Accountants, explains budget workshops in Marathi/Hindi/English, answers FAQs, and transfers complex queries to human agents.

---

## 🏗️ Architecture

```
CA Database (CSV)
      ↓
Campaign Manager (Batch Calling)
      ↓
Twilio Voice API ←→ FastAPI Server (Webhooks)
      ↓                    ↓
Phone Call           Sarvam AI (TTS/STT/Translate)
      ↓                    ↓
User Speaks  →  FAQ Engine + Intent Detection
      ↓
If complex → Call Transfer to Human Agent
If FAQ     → AI answers in user's language
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Voice Calling | Twilio Voice API |
| AI Brain | Sarvam AI (TTS/STT/Translate) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Dashboard | Vanilla HTML/CSS/JS |
| Languages | Marathi, Hindi, English |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd arthsakshar-ai
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` and fill in your credentials:

```env
SARVAM_API_KEY=your_sarvam_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+19257226809
HUMAN_AGENT_NUMBER=+91XXXXXXXXXX
BASE_URL=https://your-ngrok-url.ngrok.io
```

### 3. Run the Server

```bash
python app.py
```

Server starts at `http://localhost:8000`

### 4. Expose via ngrok (for Twilio webhooks)

```bash
ngrok http 8000
```

Copy the ngrok URL and:
1. Update `BASE_URL` in `.env`
2. Set the Twilio phone number webhook to `https://your-url.ngrok.io/voice`

### 5. Open Dashboard

Visit `http://localhost:8000` to see the campaign management dashboard.

## 📞 Call Flow

1. **Greeting** → Language selection (1=Marathi, 2=Hindi, 3=English)
2. **Introduction** → Budget Literacy initiative explained
3. **Conversation** → AI answers FAQs, detects intent
4. **Transfer** → Complex queries → human agent
5. **Logging** → All calls tracked with analytics

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/voice` | POST | Twilio voice webhook (entry) |
| `/voice/language` | POST | Language selection handler |
| `/voice/conversation` | POST | Multi-turn AI conversation |
| `/voice/status` | POST | Call status callback |
| `/api/stats` | GET | Dashboard statistics |
| `/api/calls` | GET | Recent call logs |
| `/api/events` | GET | Maharashtra events |
| `/api/campaigns` | GET | Campaign list |
| `/api/campaigns/start` | POST | Launch bulk campaign |
| `/api/test-tts` | GET | Test Sarvam AI TTS |
| `/api/health` | GET | Health check |

## ⚠️ Important Notes

- **Twilio Trial**: Trial accounts can only call verified numbers. Upgrade for production.
- **Rate Limiting**: Bulk caller batches 50 calls with 10-min delays to avoid spam flags.
- **ngrok Required**: Twilio webhooks need a public URL. Use ngrok for local development.

## 📁 Project Structure

```
arthsakshar-ai/
├── app.py              # Main FastAPI server
├── config.py           # Environment config
├── sarvam_ai.py        # Sarvam AI client
├── faq_engine.py       # FAQ + intent detection
├── call_manager.py     # Bulk calling system
├── database.py         # SQLite database
├── scripts.py          # Multi-language scripts
├── requirements.txt    # Dependencies
├── .env                # API keys (git-ignored)
├── sample_data/
│   └── ca_data.csv     # Sample 20 CA records
└── static/
    ├── index.html      # Dashboard UI
    ├── style.css       # Premium dark theme
    └── dashboard.js    # Dashboard logic
```
