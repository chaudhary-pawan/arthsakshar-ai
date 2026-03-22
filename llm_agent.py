"""
ArthSakshar AI - LLM Agent
Fallback pathway for complex queries.
"""
import logging
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)

# Initialize client only if key exists
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

SYSTEM_PROMPT = {
    "english": (
        "You are ArthSakshar AI, a polite and helpful assistant for the Maharashtra Budget Literacy Initiative. "
        "Keep your answers strictly under 2 sentences. "
        "Do not answer questions unrelated to the initiative. "
        "If the user asks a complex question, advise them that a human agent can call them back."
    ),
    "hindi": (
        "आप अर्थसाक्षर AI हैं, जो महाराष्ट्र बजट साक्षरता अभियान के लिए एक विनम्र और सहायक सहायक हैं। "
        "अपने उत्तरों को 2 वाक्यों से कम रखें। "
        "अभियान से असंबंधित प्रश्नों के उत्तर न दें। "
        "यदि उपयोगकर्ता एक जटिल विषय पूछता है, तो उन्हें बताएं कि एक मानव एजेंट वापस कॉल कर सकता है।"
    ),
    "marathi": (
        "तुम्ही अर्थसाक्षर AI आहात, महाराष्ट्र अर्थसंकल्प साक्षरता अभियानासाठी एक नम्र आणि उपयुक्त सहाय्यक. "
        "तुमची उत्तरे 2 वाक्यांपेक्षा कमी ठेवा. "
        "अभियानाशी संबंधित नसलेल्या प्रश्नांची उत्तरे देऊ नका. "
        "जर वापरकर्त्याने जटिल प्रश्न विचारला, तर त्यांना सांगा की आमचा प्रतिनिधी त्यांना परत कॉल करेल."
    )
}

async def generate_response(transcript: str, language: str = "english", previous_messages: list = None) -> str:
    """
    Generate an LLM response using OpenAI API.
    """
    if not client:
        return "Sorry, the AI engine is currently unavailable."
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.get(language, SYSTEM_PROMPT["english"])}
    ]
    
    if previous_messages:
        # previous_messages should be a list of dicts like [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        messages.extend(previous_messages)
        
    messages.append({"role": "user", "content": transcript})
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        from scripts import get_script
        return get_script(language, "fallback")
