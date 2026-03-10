"""
ArthSakshar AI – Multi-Language Scripts
Greeting, workshop explanation, and FAQ templates in Marathi, Hindi, and English.
"""

SCRIPTS = {
    "marathi": {
        "greeting": (
            "नमस्कार, मी अर्थसाक्षर AI बोलत आहे. "
        ),
        "introduction": (
            "दरवर्षीप्रमाणे यंदाही राज्याचा अर्थसंकल्प जाहीर झाला आहे. "
            "तो आपल्या राज्याच्या विकासासाठी अत्यंत महत्त्वाचा आहे, पण त्यातील संकल्पना आणि तरतुदी सामान्य लोकांसाठी समजून घेणे अनेकदा कठीण जाते. "
            "याच पार्श्वभूमीवर, आम्ही आपल्या संस्थेमार्फत ‘अर्थसंकल्प साक्षरता’ कार्यक्रम आयोजित करण्याचा प्रस्ताव मांडत आहोत. "
            "यामध्ये मुख्य दोन उपक्रम राबवले जातील: एक म्हणजे ‘बजेट सोप्या भाषेत’ कार्यशाळा, जिथे अर्थसंकल्पाचे महत्त्वाचे मुद्दे सोप्या भाषेत समजावले जातील. "
            "दुसरे म्हणजे सोशल मीडिया व ग्राफिक पोस्ट्सद्वारे जनजागृती, जेणेकरून अधिकाधिक नागरिकांपर्यंत माहिती पोहोचेल. "
            "अशा कार्यक्रमांमुळे विद्यार्थ्यांमध्ये, महिला गटांमध्ये आणि सामान्य नागरिकांमध्ये आर्थिक जाण आणि जबाबदार नागरिकत्वाची जाणीव अधिक दृढ होईल. "
        ),
        "workshop_info": (
            "आम्ही या उपक्रमासाठी आशय, ग्राफिक सामग्री आणि मार्गदर्शनासह पूर्ण विनामूल्य सहकार्य करण्यास तत्पर आहोत. "
        ),
        "ask_interest": "आपल्या संस्थेचा सहभाग आम्हाला खूप महत्त्वाचा आहे. आपण या उपक्रमात सहभागी व्हाल का? कृपया होय किंवा नाही सांगा.",
        "thank_you": "धन्यवाद! आपल्या सहभागाबद्दल आभारी आहोत. आपला दिवस शुभ असो!",
        "not_interested": "ठीक आहे, धन्यवाद. काही प्रश्न असल्यास संपर्क करा. शुभ दिवस!",
        "transfer": "आपला प्रश्न आमच्या कार्यालयीन प्रतिनिधीकडे पाठवत आहे. कृपया थांबा.",
        "event_info": "आपल्या शहरात {city} मध्ये {date} रोजी {venue} येथे कार्यशाळा आहे. संयोजक {coordinator} आहेत.",
        "faq_free": "हा उपक्रम पूर्णपणे विनामूल्य आहे. कोणतेही शुल्क नाही.",
        "faq_who": "सर्व सनदी लेखापाल, व्यावसायिक, विद्यार्थी, महिला बचत गट आणि नागरिक सहभागी होऊ शकतात.",
        "faq_duration": "कार्यशाळा साधारणपणे दोन ते तीन तासांची असते.",
        "fallback": "मला तुमचा प्रश्न पूर्णपणे समजला नाही. कृपया पुन्हा सांगा किंवा आमच्या प्रतिनिधीशी बोलायचे असल्यास 'ट्रान्सफर' म्हणा.",
    },
    "hindi": {
        "greeting": (
            "नमस्कार! मैं अर्थसाक्षर AI बोल रहा हूँ। "
            "बजट साक्षरता अभियान से आपसे संपर्क कर रहा हूँ।"
        ),
        "introduction": (
            "हर साल की तरह इस बार भी राज्य का बजट घोषित हुआ है। "
            "यह राज्य के विकास के लिए बहुत महत्वपूर्ण है, लेकिन कई नागरिकों को "
            "इसके प्रावधान समझना मुश्किल होता है। "
            "इसलिए हम 'बजट साक्षरता' कार्यक्रम आयोजित कर रहे हैं।"
        ),
        "workshop_info": (
            "इसमें 'बजट आसान भाषा में' कार्यशाला और सोशल मीडिया जागरूकता अभियान शामिल हैं। "
            "यह कार्यक्रम पूरी तरह निःशुल्क है।"
        ),
        "ask_interest": "क्या आप हमारे साथ शामिल होंगे? कृपया हाँ या ना बोलें।",
        "thank_you": "धन्यवाद! आपकी भागीदारी के लिए आभारी हैं। आपका दिन शुभ हो!",
        "not_interested": "ठीक है, धन्यवाद। कोई सवाल हो तो संपर्क करें। शुभ दिन!",
        "transfer": "आपका सवाल हमारे कार्यालय प्रतिनिधि को भेज रहे हैं। कृपया रुकें।",
        "event_info": "आपके शहर {city} में {date} को {venue} पर कार्यशाला है। संयोजक {coordinator} हैं।",
        "faq_free": "यह कार्यक्रम पूरी तरह निःशुल्क है। कोई फीस नहीं।",
        "faq_who": "सभी चार्टर्ड अकाउंटेंट, व्यवसायी, छात्र, महिला स्वयं सहायता समूह और नागरिक भाग ले सकते हैं।",
        "faq_duration": "कार्यशाला आमतौर पर दो से तीन घंटे की होती है।",
        "fallback": "मुझे आपका सवाल पूरी तरह समझ नहीं आया। कृपया दोबारा बोलें या हमारे प्रतिनिधि से बात करने के लिए 'ट्रांसफर' बोलें।",
    },
    "english": {
        "greeting": (
            "Hello! I am ArthSakshar AI. "
            "I am calling from the Budget Literacy Initiative."
        ),
        "introduction": (
            "As every year, the state budget has been announced. "
            "It is crucial for the development of the state, but many citizens "
            "find it difficult to understand the provisions. "
            "That is why we are organizing the Budget Literacy program."
        ),
        "workshop_info": (
            "This includes 'Budget in Simple Language' workshops and social media awareness campaigns. "
            "This program is completely free of cost."
        ),
        "ask_interest": "Would you like to join us? Please say yes or no.",
        "thank_you": "Thank you! We appreciate your participation. Have a great day!",
        "not_interested": "That's alright, thank you. Feel free to contact us if you have questions. Have a good day!",
        "transfer": "I am connecting you with our office representative. Please hold.",
        "event_info": "There is a workshop in {city} on {date} at {venue}. The coordinator is {coordinator}.",
        "faq_free": "This program is completely free of cost. There are no charges.",
        "faq_who": "All Chartered Accountants, business owners, students, women self-help groups, and citizens can participate.",
        "faq_duration": "The workshop typically lasts two to three hours.",
        "fallback": "I didn't fully understand your question. Please repeat or say 'transfer' to speak with our representative.",
    },
}

LANGUAGE_MAP = {
    "1": "marathi",
    "2": "hindi",
    "3": "english",
    "marathi": "marathi",
    "hindi": "hindi",
    "english": "english",
}

LANGUAGE_CODES = {
    "marathi": "mr-IN",
    "hindi": "hi-IN",
    "english": "en-IN",
}

LANGUAGE_GREETING = (
    "Namaskar! Kripya bhasha chuniye. "
    "मराठीसाठी एक दाबा. "
    "हिंदी के लिए दो दबाएं."
    "For english press three."
)


def get_script(language: str, key: str, **kwargs) -> str:
    """Get a script in the specified language with optional formatting."""
    lang = LANGUAGE_MAP.get(language, "english")
    scripts = SCRIPTS.get(lang, SCRIPTS["english"])
    text = scripts.get(key, scripts.get("fallback", ""))
    if kwargs:
        text = text.format(**kwargs)
    return text


def get_full_introduction(language: str) -> str:
    """Get the complete introduction script."""
    lang = LANGUAGE_MAP.get(language, "english")
    scripts = SCRIPTS.get(lang, SCRIPTS["english"])
    return f"{scripts['greeting']} {scripts['introduction']} {scripts['workshop_info']} {scripts['ask_interest']}"


def get_event_info(language: str, city: str, date: str, venue: str, coordinator: str) -> str:
    """Get event info formatted for the specified language."""
    return get_script(language, "event_info", city=city, date=date, venue=venue, coordinator=coordinator)
