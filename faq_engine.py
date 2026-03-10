"""
ArthSakshar AI – FAQ Engine & Intent Detection
Knowledge base with categorized Q&A and intent classification.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


# ─── Intent Types ───────────────────────────────────────────────
class Intent:
    PROGRAM_DETAILS = "program_details"
    COST = "cost"
    DURATION = "duration"
    ELIGIBILITY = "eligibility"
    SCHEDULE = "schedule"
    LOCATION = "location"
    YES_INTERESTED = "yes_interested"
    NO_INTERESTED = "no_interested"
    CALLBACK = "callback"
    TRANSFER = "transfer"
    GREETING = "greeting"
    UNKNOWN = "unknown"


# ─── Keyword Patterns for Intent Detection ──────────────────────
INTENT_PATTERNS = {
    Intent.TRANSFER: {
        "keywords": [
            "office", "legal", "document", "political", "address", "registration",
            "certificate", "complaint", "advocate", "lawyer", "court",
            "कार्यालय", "कानूनी", "दस्तावेज", "राजनीतिक", "पता", "पंजीकरण",
            "कायदेशीर", "कागदपत्र", "राजकीय", "नोंदणी", "प्रमाणपत्र",
            "transfer", "ट्रान्सफर", "ट्रांसफर", "representative", "agent",
        ],
    },
    Intent.YES_INTERESTED: {
        "keywords": [
            "yes", "haan", "ha", "ho", "sure", "okay", "ok", "interested",
            "join", "participate", "हाँ", "हाँ जी", "हो", "होय", "जरूर",
            "ठीक", "शामिल", "सहभागी",
        ],
    },
    Intent.NO_INTERESTED: {
        "keywords": [
            "no", "nahi", "nahi", "not interested", "busy", "later",
            "नहीं", "नको", "नाही", "व्यस्त", "बाद में", "नंतर",
            "na", "naa", "nahin", "nhi", "nope",
        ],
    },
    Intent.COST: {
        "keywords": [
            "cost", "fee", "charge", "price", "free", "payment", "pay",
            "शुल्क", "फीस", "कीमत", "मुफ्त", "निःशुल्क", "किंमत", "विनामूल्य",
            "kitna", "paisa", "paise", "rupees",
        ],
    },
    Intent.DURATION: {
        "keywords": [
            "duration", "how long", "time", "hours", "minutes",
            "कितना समय", "कितने घंटे", "किती वेळ", "किती तास",
            "kitna time", "kitni der",
        ],
    },
    Intent.ELIGIBILITY: {
        "keywords": [
            "who can", "eligible", "qualification", "criteria", "attend",
            "कौन", "पात्रता", "योग्यता", "कोण", "पात्र",
            "kaun", "kon", "kiske liye",
        ],
    },
    Intent.SCHEDULE: {
        "keywords": [
            "when", "date", "schedule", "timing", "kab",
            "कब", "तारीख", "समय", "केव्हा", "तारीख",
        ],
    },
    Intent.LOCATION: {
        "keywords": [
            "where", "venue", "place", "location", "kahan",
            "कहाँ", "स्थान", "जगह", "कुठे", "ठिकाण",
        ],
    },
    Intent.PROGRAM_DETAILS: {
        "keywords": [
            "what", "about", "details", "information", "tell me",
            "explain", "क्या", "बताइए", "जानकारी", "विवरण",
            "काय", "सांगा", "माहिती", "kya hai", "batao",
        ],
    },
    Intent.CALLBACK: {
        "keywords": [
            "callback", "call back", "call later", "later",
            "बाद में", "नंतर", "फोन करो", "कॉल बॅक",
        ],
    },
    Intent.GREETING: {
        "keywords": [
            "hello", "hi", "namaste", "namaskar",
            "नमस्ते", "नमस्कार",
        ],
    },
}


# ─── FAQ Knowledge Base ─────────────────────────────────────────
FAQ_KNOWLEDGE = {
    Intent.PROGRAM_DETAILS: {
        "en": (
            "The Budget Literacy Initiative is a program to help citizens understand "
            "the state budget in simple language. We conduct workshops, social media campaigns, "
            "and outreach programs across Maharashtra to make financial governance accessible to all."
        ),
        "hi": (
            "बजट साक्षरता अभियान एक कार्यक्रम है जो नागरिकों को राज्य का बजट "
            "आसान भाषा में समझाने के लिए बनाया गया है। हम महाराष्ट्र भर में कार्यशालाएं, "
            "सोशल मीडिया अभियान और जागरूकता कार्यक्रम आयोजित करते हैं।"
        ),
        "mr": (
            "अर्थसंकल्प साक्षरता उपक्रम हा नागरिकांना राज्याचा अर्थसंकल्प सोप्या भाषेत "
            "समजावून सांगण्यासाठी तयार केलेला कार्यक्रम आहे. आम्ही महाराष्ट्रभर कार्यशाळा, "
            "सोशल मीडिया मोहीम आणि जनजागृती कार्यक्रम आयोजित करतो."
        ),
    },
    Intent.COST: {
        "en": "This program is completely free of cost. There are no charges or fees to participate.",
        "hi": "यह कार्यक्रम पूरी तरह निःशुल्क है। भाग लेने के लिए कोई शुल्क नहीं है।",
        "mr": "हा उपक्रम पूर्णपणे विनामूल्य आहे. सहभागी होण्यासाठी कोणतेही शुल्क नाही.",
    },
    Intent.DURATION: {
        "en": "Each workshop typically lasts 2 to 3 hours, including an interactive Q&A session.",
        "hi": "प्रत्येक कार्यशाला आमतौर पर 2 से 3 घंटे तक चलती है, जिसमें प्रश्नोत्तर सत्र भी शामिल है।",
        "mr": "प्रत्येक कार्यशाळा साधारणपणे 2 ते 3 तास चालते, ज्यामध्ये प्रश्नोत्तर सत्र समाविष्ट आहे.",
    },
    Intent.ELIGIBILITY: {
        "en": (
            "All Chartered Accountants, business owners, students, women self-help groups, "
            "and citizens can participate. Everyone is welcome!"
        ),
        "hi": (
            "सभी चार्टर्ड अकाउंटेंट, व्यवसायी, छात्र, महिला स्वयं सहायता समूह "
            "और नागरिक भाग ले सकते हैं। सभी का स्वागत है!"
        ),
        "mr": (
            "सर्व सनदी लेखापाल, व्यावसायिक, विद्यार्थी, महिला बचत गट "
            "आणि नागरिक सहभागी होऊ शकतात. सर्वांचे स्वागत आहे!"
        ),
    },
}

# Language abbreviation map
LANG_ABBREV = {
    "marathi": "mr",
    "hindi": "hi",
    "english": "en",
}


def detect_intent(text: str) -> str:
    """
    Detect user intent from their speech/text input.
    Uses keyword matching with priority ordering (transfer > callback > yes/no > faq).
    """
    text_lower = text.lower().strip()

    # Priority order: transfer first (safety), then specific intents
    priority_order = [
        Intent.TRANSFER,
        Intent.YES_INTERESTED,
        Intent.NO_INTERESTED,
        Intent.CALLBACK,
        Intent.COST,
        Intent.DURATION,
        Intent.ELIGIBILITY,
        Intent.SCHEDULE,
        Intent.LOCATION,
        Intent.PROGRAM_DETAILS,
        Intent.GREETING,
    ]

    for intent in priority_order:
        patterns = INTENT_PATTERNS.get(intent, {})
        keywords = patterns.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in text_lower:
                logger.info(f"Intent detected: {intent} (keyword: '{keyword}' in '{text_lower[:50]}')")
                return intent

    logger.info(f"Intent: UNKNOWN for text: '{text_lower[:50]}'")
    return Intent.UNKNOWN


def get_faq_answer(intent: str, language: str = "english") -> str | None:
    """
    Get a FAQ answer for the detected intent in the specified language.
    Returns None if no FAQ answer is available.
    """
    lang_key = LANG_ABBREV.get(language, "en")
    faq = FAQ_KNOWLEDGE.get(intent)
    if faq:
        return faq.get(lang_key, faq.get("en", ""))
    return None


def process_user_input(text: str, language: str = "english") -> Tuple[str, str]:
    """
    Process user input and return (intent, response_text).
    Returns the intent and the appropriate response text.
    """
    intent = detect_intent(text)

    if intent == Intent.TRANSFER:
        from scripts import get_script
        return intent, get_script(language, "transfer")

    if intent == Intent.YES_INTERESTED:
        from scripts import get_script
        return intent, get_script(language, "thank_you")

    if intent == Intent.NO_INTERESTED:
        from scripts import get_script
        return intent, get_script(language, "not_interested")

    if intent == Intent.CALLBACK:
        responses = {
            "english": "Sure, we will call you back at a convenient time. Thank you!",
            "hindi": "ज़रूर, हम आपको सुविधाजनक समय पर वापस कॉल करेंगे। धन्यवाद!",
            "marathi": "नक्की, आम्ही आपल्याला सोयीस्कर वेळी परत कॉल करू. धन्यवाद!",
        }
        return intent, responses.get(language, responses["english"])

    # FAQ-based answers
    faq_answer = get_faq_answer(intent, language)
    if faq_answer:
        return intent, faq_answer

    if intent == Intent.GREETING:
        from scripts import get_script
        return intent, get_script(language, "greeting")

    # Unknown → fallback
    from scripts import get_script
    return intent, get_script(language, "fallback")
