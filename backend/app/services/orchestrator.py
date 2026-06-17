import uuid
import base64
import logging
from typing import Optional

from app.schemas.response import AssistantResponse, QuizPayload, QuizQuestion, SourceRef
from app.services.language_router import detect_language
from app.services.intent_router import detect_intent, normalize_text
from app.services.explain_service import generate_explanation
from app.services.quiz_service import generate_quiz
from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)

# Basic fallbacks for unclear commands
UNCLEAR_RESPONSES = {
    "english": {
        "message": "I did not understand that. Please repeat in simpler words or ask to explain a topic.",
        "suggestions": ["Explain Photosynthesis", "Quiz on Gravity"],
        "response_text": "I'm sorry, I did not understand that. Please repeat in simpler words."
    },
    "hindi": {
        "message": "मुझे समझ नहीं आया। कृपया आसान शब्दों में दोहराएं या समझाने के लिए कहें।",
        "suggestions": ["Explain Photosynthesis", "Quiz on Gravity"],
        "response_text": "माफ़ कीजिये, मुझे समझ नहीं आया। कृपया आसान शब्दों में फिर से समझाएं।"
    },
    "hinglish": {
        "message": "Mafi chahta hu, samajh nahi aaya. Kripya thode aasan shabdon mein bataiye.",
        "suggestions": ["Explain Photosynthesis", "Quiz on Gravity"],
        "response_text": "Mafi chahta hu, samajh nahi aaya. Kripya thode aasan shabdon mein bataiye."
    }
}

async def build_assistant_response(
    session_id: str,
    text: str,
    mode_hint: Optional[str] = None,
    source_mode: bool = False
) -> AssistantResponse:
    """
    Main orchestrator service that coordinates intent, language, explanation/quiz logic,
    and returns a unified AssistantResponse schema.
    """
    normalized = normalize_text(text)
    
    # 1. Determine intent and language mode
    if mode_hint:
        intent = mode_hint
        confidence = 1.0  # Manual hint has highest confidence
    else:
        intent, confidence = detect_intent(normalized)
    
    language_mode_str, lang_confidence = detect_language(text)
    language_mode = language_mode_str  # Use string directly
    
    logger.info(f"Orchestrator: raw_text='{text}', normalized='{normalized}', intent='{intent}' (conf={confidence:.2f}), lang='{language_mode}' (conf={lang_confidence:.2f})")
    
    # Defaults
    requires_clarification = False
    answer_text = None
    quiz_payload = None
    next_actions = []
    avatar_state = "idle"
    source_refs = []
    
    # Compatibility attributes
    title = None
    grade_level = None
    bullets = []
    example = None
    recap = None
    questions_compat = []
    
    # 2. Route based on intent
    if intent == "explain":
        avatar_state = "speaking"
        res = await generate_explanation(session_id, normalized, language_mode, source_mode)
        
        title = res.get("title")
        grade_level = res.get("grade_level")
        bullets = res.get("bullets", [])
        example = res.get("example")
        recap = res.get("recap")
        answer_text = res.get("answer_text")
        
        # Citations mapping
        if "citations" in res:
            source_refs = [
                SourceRef(
                    title=c["source_title"],
                    snippet=c["snippet"],
                    page_number=c.get("page_number"),
                    section_label=c.get("section_label")
                )
                for c in res["citations"]
            ]
            
        next_actions = ["Explain Photosynthesis", "Start a Quiz"]
        
    elif intent == "quiz":
        avatar_state = "speaking"
        res = await generate_quiz(session_id, normalized, language_mode, source_mode)
        
        title = res.get("title")
        answer_text = res.get("response_text")
        
        raw_qs = res.get("questions", [])
        questions = [
            QuizQuestion(
                question=q["question"],
                options=q["options"],
                correct_index=q["correct_index"],
                explanation=q["explanation"]
            )
            for q in raw_qs
        ]
        
        if questions:
            quiz_payload = QuizPayload(
                title=res.get("title", "Quiz"),
                topic=normalized,
                questions=questions,
                total_questions=len(questions)
            )
            questions_compat = questions
            
        # Citations mapping
        if "citations" in res:
            source_refs = [
                SourceRef(
                    title=c["source_title"],
                    snippet=c["snippet"],
                    page_number=c.get("page_number"),
                    section_label=c.get("section_label")
                )
                for c in res["citations"]
            ]
            
        next_actions = ["Explain topic", "Ask next question"]
        
    elif intent == "stop":
        avatar_state = "idle"
        if language_mode == "english":
            answer_text = "Stopping lesson. Let me know when you are ready to continue."
        elif language_mode == "hindi":
            answer_text = "पढ़ाई रोक दी गई है। जब आप तैयार हों तो बताइएगा।"
        else:
            answer_text = "Class pause kar di gayi hai. Jab aap ready ho bataiye."
        next_actions = ["Resume teaching"]
        
    elif intent == "followup":
        # Followup handles repeat logic, routing back to last explanation if possible
        # Default to a generic Hinglish/Hindi/English repeat message
        avatar_state = "speaking"
        if language_mode == "english":
            answer_text = "Alright, let's explain this topic once more."
        elif language_mode == "hindi":
            answer_text = "ठीक है, चलिए इस विषय को एक बार फिर से समझते हैं।"
        else:
            answer_text = "Theek hai, chaliye is topic ko ek baar fir se samajhte hain."
        next_actions = ["Explain Photosynthesis", "Quiz on Gravity"]
        
    else:
        # Unclear/clarify intent
        requires_clarification = True
        lang_key = language_mode if language_mode in UNCLEAR_RESPONSES else "hinglish"
        conf = UNCLEAR_RESPONSES[lang_key]
        
        title = "Clarification Requested"
        answer_text = conf["response_text"]
        next_actions = conf["suggestions"]
    
    # 3. Generate TTS audio base64 payload
    audio_base64 = None
    if answer_text:
        try:
            audio_content = await tts_service.speak(answer_text)
            if audio_content:
                audio_b64 = base64.b64encode(audio_content).decode("utf-8")
                audio_base64 = f"data:audio/mp3;base64,{audio_b64}"
        except Exception as e:
            logger.error(f"Orchestrator TTS failed: {e}")
            
    return AssistantResponse(
        session_id=session_id,
        mode=intent,
        language_mode=language_mode,
        transcript_text=text,
        answer_text=answer_text,
        quiz=quiz_payload,
        next_actions=next_actions,
        confidence=confidence,
        requires_clarification=requires_clarification,
        avatar_state=avatar_state,
        source_refs=source_refs,
        audio_base64=audio_base64,
        
        # Explain card attributes
        title=title,
        grade_level=grade_level,
        bullets=bullets,
        example=example,
        recap=recap,
        
        # Quiz card compatibility
        questions=questions_compat
    )
