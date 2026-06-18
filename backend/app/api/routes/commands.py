import uuid
import base64
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.api.schemas import CommandRequest, GlobalResponse
from app.services.stt_service import stt_service
from app.services.orchestrator import build_assistant_response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/text", response_model=GlobalResponse)
async def process_text(request: CommandRequest):
    response = await build_assistant_response(
        session_id=request.session_id,
        text=request.text,
        mode_hint=None,
        source_mode=request.source_mode
    )
    
    return {
        "status": "success",
        "data": response.model_dump()
    }

@router.post("/audio", response_model=GlobalResponse)
async def process_audio(
    session_id: str = Form(...),
    audio: UploadFile = File(...),
    text_hint: Optional[str] = Form(None),
    source_mode: Optional[bool] = Form(False)
):
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
            transcript = ""
            
    if not transcript.strip():
        # Empty transcript fallback, pass empty string to orchestrator to let it clarify
        transcript = "unclear voice input"
        
    response = await build_assistant_response(
        session_id=session_id,
        text=transcript,
        mode_hint=None,
        source_mode=source_mode
    )
        
    return {
        "status": "success",
        "data": response.model_dump()
    }

