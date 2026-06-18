import logging
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.command import CommandRequest
from app.schemas.response import AssistantResponse
from app.services.orchestrator import build_assistant_response
from app.services.hands_free_state import state_manager

router = APIRouter()
logger = logging.getLogger(__name__)

class HandsFreeRequest(BaseModel):
    session_id: str

@router.post("/hands-free/start")
async def start_hands_free(request: HandsFreeRequest):
    """Starts the hands-free loop for the session."""
    state_manager.enable_hands_free(request.session_id)
    state_manager.set_state(request.session_id, "listening")
    
    response_payload = AssistantResponse(
        session_id=request.session_id,
        mode="hands_free_start",
        hands_free_mode=True,
        assistant_state="listening",
        avatar_state="listening",
        answer_text="Hands-free mode started. Listening...",
        title="Hands-Free Mode Started"
    )
    
    dump = response_payload.model_dump()
    dump["status"] = "success"
    dump["data"] = dump.copy()
    return dump

@router.post("/hands-free/stop")
async def stop_hands_free(request: HandsFreeRequest):
    """Stops the hands-free loop for the session."""
    state_manager.disable_hands_free(request.session_id)
    
    response_payload = AssistantResponse(
        session_id=request.session_id,
        mode="hands_free_stop",
        hands_free_mode=False,
        assistant_state="idle",
        avatar_state="idle",
        answer_text="Hands-free mode stopped.",
        title="Hands-Free Mode Stopped"
    )
    
    dump = response_payload.model_dump()
    dump["status"] = "success"
    dump["data"] = dump.copy()
    return dump

@router.post("/command")
async def process_voice_command(request: CommandRequest):
    """Processes a voice command in the hands-free loop."""
    response_payload = await build_assistant_response(
        session_id=request.session_id,
        text=request.text,
        mode_hint=request.mode_hint,
        source_mode=request.source_mode
    )
    
    dump = response_payload.model_dump()
    dump["status"] = "success"
    dump["data"] = dump.copy()
    return dump
