"""
ArthSakshar AI – Configuration
Loads all environment variables and provides centralized settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Sarvam AI
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_TTS_URL: str = "https://api.sarvam.ai/text-to-speech"
    SARVAM_STT_URL: str = "https://api.sarvam.ai/speech-to-text"
    SARVAM_TRANSLATE_URL: str = "https://api.sarvam.ai/translate"

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")

    # Human agent for call transfer
    HUMAN_AGENT_NUMBER: str = os.getenv("HUMAN_AGENT_NUMBER", "+919999999999")

    # Server
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///arthsakshar.db")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "arthsakshar.db")

    # Calling config
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "50"))
    BATCH_DELAY_SECONDS: int = int(os.getenv("BATCH_DELAY_SECONDS", "600"))
    MAX_CALLS_PER_HOUR: int = int(os.getenv("MAX_CALLS_PER_HOUR", "250"))


settings = Settings()
