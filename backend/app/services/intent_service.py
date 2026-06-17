from typing import Literal
import logging
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

IntentType = Literal["explain", "quiz", "clarify"]
LanguageType = Literal["default", "hinglish", "english", "hindi"]

def detect_language(text: str) -> LanguageType:
    """
    Detects the requested language mode based on keywords in the text.
    """
    if not text:
        return "default"
        
    text_lower = text.lower()
    
    # English keywords
    if any(phrase in text_lower for phrase in ["in english", "english mein", "english me"]):
        return "english"
        
    # Hindi keywords
    if any(phrase in text_lower for phrase in ["in hindi", "hindi mein", "hindi me", "pure hindi"]):
        return "hindi"
        
    # Hinglish keywords
    if any(phrase in text_lower for phrase in ["in hinglish", "hinglish mein", "hinglish me"]):
        return "hinglish"
        
    return "default"

async def detect_intent(text: str) -> IntentType:
    """
    Classifies text into explain, quiz, or clarify.
    Supports English, Hinglish, and Devanagari Hindi.
    """
    if not text:
        return "clarify"
        
    text_lower = text.lower().strip()
    
    # 1. Local Keyword Check (English, Hinglish, Devanagari)
    explain_keywords = [
        "explain", "meaning", "define", "definition", "how", "why", "what is", "what are",
        "batao", "kya hai", "samjhao", "samjha", "boliye", "bolo", "bataiye", "bataye",
        "समझाओ", "बताओ", "क्या है", "परिभाषा", "मतलब", "अर्थ", "कैसे", "क्यों", "स्पष्ट"
    ]
    if any(keyword in text_lower for keyword in explain_keywords):
        return "explain"
        
    quiz_keywords = [
        "quiz", "question", "test", "mcq", "exam", "assess", "ask",
        "sawal", "pucho", "poocho", "test lo", "mcq lo", "quiz lo",
        "क्विज़", "सवाल", "पूछो", "प्रश्न", "परीक्षा", "एमसीक्यू", "जांच"
    ]
    if any(keyword in text_lower for keyword in quiz_keywords):
        return "quiz"
        
    # 2. LLM Fallback for robust intent detection
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intent classifier for an AI Teaching Assistant.\n"
                    "Classify the user's input into one of three categories: 'explain', 'quiz', or 'clarify'.\n"
                    "- Choose 'explain' if the user wants to understand, learn, or get an explanation about a topic (e.g. 'gravity', 'explain photosynthesis', 'प्रकाश संश्लेषण क्या है', 'gravity samjhao').\n"
                    "- Choose 'quiz' if the user wants to be tested, wants questions, or a quiz (e.g. 'ask me questions about gravity', 'क्विज़ करो', 'सवाल पूछो').\n"
                    "- Choose 'clarify' if the input is gibberish, incomplete, or ambiguous (e.g. 'asdfgh', 'hello').\n\n"
                    "Your response must be a single JSON object in the following format:\n"
                    "{\"intent\": \"explain\"} or {\"intent\": \"quiz\"} or {\"intent\": \"clarify\"}"
                )
            },
            {"role": "user", "content": text}
        ]
        result = await llm_service.get_chat_completion(messages, response_format={"type": "json_object"})
        intent = result.get("intent", "clarify")
        logger.info(f"LLM detected intent '{intent}' for text: '{text}'")
        if intent in ["explain", "quiz", "clarify"]:
            return intent
    except Exception as e:
        logger.error(f"LLM intent detection failed: {e}")
        pass

    # 3. Simple fallback heuristics for short phrases
    words = text_lower.split()
    if len(words) <= 3 and len(text_lower) > 2:
        return "explain"
        
    return "clarify"
