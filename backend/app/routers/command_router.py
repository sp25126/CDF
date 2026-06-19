import uuid
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form

from app.schemas.command import CommandRequest
from app.schemas.response import AssistantResponse
from app.services.orchestrator import build_assistant_response, UNCLEAR_RESPONSES
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.language_router import detect_language
import base64

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/text")
async def process_text(request: CommandRequest):
    """
    Exposes text command processing endpoint returning a unified AssistantResponse payload.
    """
    response_payload = await build_assistant_response(
        session_id=request.session_id,
        text=request.text,
        mode_hint=request.mode_hint,
        source_mode=request.source_mode,
        user_api_key=request.user_api_key,
        user_provider=request.user_provider,
        user_model=request.user_model,
    )
    
    dump = response_payload.model_dump()
    dump["status"] = "success"
    dump["data"] = dump.copy()
    return dump

@router.post("/audio")
async def process_audio(
    session_id: str = Form(...),
    audio: UploadFile = File(...),
    text_hint: Optional[str] = Form(None),
    source_mode: Optional[bool] = Form(False)
):
    """
    Exposes audio command processing endpoint returning a unified AssistantResponse payload.
    """
    audio_bytes = await audio.read()
    
    # 1. Transcribe audio
    transcript = ""
    try:
        transcript = await stt_service.transcribe(audio_bytes, audio.filename)
    except Exception as e:
        logger.error(f"Live STT failed: {e}. Falling back to text hint or default.")
        if text_hint:
            transcript = text_hint
            
    # 2. Check for empty transcript
    if not transcript.strip():
        language_mode = detect_language(text_hint or "")
        lang_key = language_mode if language_mode in UNCLEAR_RESPONSES else "hinglish"
        conf = UNCLEAR_RESPONSES[lang_key]
        
        # Audio unrecognized feedback message
        if language_mode == "english":
            msg = "Voice not clearly heard. Please speak again or type below."
        elif language_mode == "hindi":
            msg = "आवाज़ साफ़ नहीं सुनाई दी। कृपया फिर से बोलें या नीचे टाइप करें।"
        else:
            msg = "Awaaz saaf nahi sunai di. Kripya fir se bolein ya niche type karein."
            
        # TTS synthesis for clarification
        audio_base64 = None
        try:
            audio_content = await tts_service.speak(msg)
            if audio_content:
                audio_b64 = base64.b64encode(audio_content).decode("utf-8")
                audio_base64 = f"data:audio/mp3;base64,{audio_b64}"
        except Exception as tts_err:
            logger.error(f"Fallback audio TTS failed: {tts_err}")

        response_payload = AssistantResponse(
            session_id=session_id,
            mode="clarify",
            language_mode=language_mode,
            transcript_text="Voice Input (Not Recognized)",
            answer_text=msg,
            requires_clarification=True,
            next_actions=conf["suggestions"],
            audio_base64=audio_base64,
            title="Clarification Requested"
        )
        dump = response_payload.model_dump()
        dump["status"] = "success"
        dump["data"] = dump.copy()
        return dump
        
    # 3. Process transcribed text via orchestrator
    response_payload = await build_assistant_response(
        session_id=session_id,
        text=transcript,
        source_mode=source_mode
    )
    
    dump = response_payload.model_dump()
    dump["status"] = "success"
    dump["data"] = dump.copy()
    return dump
