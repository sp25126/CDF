import uuid
import base64
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.api.schemas import CommandRequest, GlobalResponse
from app.services.intent_service import detect_intent, detect_language
from app.services.lesson_service import generate_explanation
from app.services.quiz_service import generate_quiz
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.prompts import CLARIFY_RESPONSES

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/text", response_model=GlobalResponse)
async def process_text(request: CommandRequest):
    request_id = str(uuid.uuid4())
    language_mode = detect_language(request.text)
    intent = await detect_intent(request.text)
    
    if intent == "explain":
        data = await generate_explanation(request.session_id, request.text, language_mode, source_mode=request.source_mode)
    elif intent == "quiz":
        data = await generate_quiz(request.session_id, request.text, language_mode, source_mode=request.source_mode)
    else:
        # Clarify response respecting the language mode
        data = CLARIFY_RESPONSES.get(language_mode, CLARIFY_RESPONSES["hinglish"]).copy()
    
    # Add metadata and transcript
    data["request_id"] = request_id
    data["transcript"] = request.text
    data["intent"] = intent
    data["language_mode"] = language_mode
    data["source_mode"] = request.source_mode
    
    # Generate spoken audio using TTS
    try:
        audio_content = await tts_service.speak(data.get("response_text", ""))
        if audio_content:
            audio_b64 = base64.b64encode(audio_content).decode("utf-8")
            data["audio_base64"] = f"data:audio/mp3;base64,{audio_b64}"
        else:
            data["audio_base64"] = ""
    except Exception as tts_err:
        logger.error(f"TTS generation failed for text route: {tts_err}")
        data["audio_base64"] = ""
        
    return {
        "status": "success",
        "data": data
    }

@router.post("/audio", response_model=GlobalResponse)
async def process_audio(
    session_id: str = Form(...),
    audio: UploadFile = File(...),
    text_hint: Optional[str] = Form(None),
    source_mode: Optional[bool] = Form(False)
):
    request_id = str(uuid.uuid4())
    audio_bytes = await audio.read()
    
    # Try live STT
    transcript = ""
    try:
        transcript = await stt_service.transcribe(audio_bytes, audio.filename)
    except Exception as e:
        logger.error(f"Live STT failed: {e}. Falling back to text hint or default.")
        if text_hint:
            transcript = text_hint
        else:
            transcript = "" # No fallback default topic, let it clarify gracefully
            
    language_mode = detect_language(transcript)

    # Handle empty transcript (meaning no voice detected and no fallback text hint)
    if not transcript.strip():
        data = CLARIFY_RESPONSES.get(language_mode, CLARIFY_RESPONSES["hinglish"]).copy()
        # Custom message for audio unrecognized
        if language_mode == "english":
            data["message"] = "Voice not clearly heard. Please speak again or type below."
            data["response_text"] = "Voice not clearly heard. Please speak again or type below."
        elif language_mode == "hindi":
            data["message"] = "आवाज़ साफ़ नहीं सुनाई दी। कृपया फिर से बोलें या नीचे टाइप करें।"
            data["response_text"] = "आवाज़ साफ़ नहीं सुनाई दी। कृपया फिर से बोलें या नीचे टाइप करें।"
        else:
            data["message"] = "Awaaz saaf nahi sunai di. Kripya fir se bolein ya niche type karein."
            data["response_text"] = "Awaaz saaf nahi sunai di. Kripya fir se bolein ya niche type karein."

        data["request_id"] = request_id
        data["transcript"] = "Voice Input (Not Recognized)"
        data["intent"] = "clarify"
        data["language_mode"] = language_mode
        data["source_mode"] = source_mode
        
        try:
            audio_content = await tts_service.speak(data["response_text"])
            if audio_content:
                audio_b64 = base64.b64encode(audio_content).decode("utf-8")
                data["audio_base64"] = f"data:audio/mp3;base64,{audio_b64}"
            else:
                data["audio_base64"] = ""
        except Exception as tts_err:
            logger.error(f"TTS generation failed for fallback: {tts_err}")
            data["audio_base64"] = ""
            
        return {
            "status": "success",
            "data": data
        }

    # Route through existing intent / explanation / quiz logic
    intent = await detect_intent(transcript)
    if intent == "explain":
        data = await generate_explanation(session_id, transcript, language_mode, source_mode=source_mode)
    elif intent == "quiz":
        data = await generate_quiz(session_id, transcript, language_mode, source_mode=source_mode)
    else:
        data = CLARIFY_RESPONSES.get(language_mode, CLARIFY_RESPONSES["hinglish"]).copy()
        
    # Add metadata and transcript
    data["request_id"] = request_id
    data["transcript"] = transcript
    data["intent"] = intent
    data["language_mode"] = language_mode
    data["source_mode"] = source_mode
    
    # Generate spoken audio using TTS
    try:
        audio_content = await tts_service.speak(data.get("response_text", ""))
        if audio_content:
            audio_b64 = base64.b64encode(audio_content).decode("utf-8")
            data["audio_base64"] = f"data:audio/mp3;base64,{audio_b64}"
        else:
            data["audio_base64"] = ""
    except Exception as tts_err:
        logger.error(f"TTS generation failed for audio route: {tts_err}")
        data["audio_base64"] = ""
        
    return {
        "status": "success",
        "data": data
    }

