"""
Unified command endpoint — /api/command (POST)

A single, frontend-friendly wrapper over build_assistant_response.
Normalises every response into the GlobalResponse envelope so the
frontend never has to handle multiple response shapes.
"""
import logging
from fastapi import APIRouter, HTTPException
from app.api.schemas import CommandRequest, GlobalResponse
from app.services.orchestrator import build_assistant_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=GlobalResponse, summary="Submit a classroom command")
async def unified_command(request: CommandRequest):
    """
    POST /api/command

    Accepts a teacher's text command and returns a normalised assistant
    response. The response includes:
      - mode / intent (explain | quiz | unclear)
      - avatar_state for JULI-E animation
      - response_text for TTS (markdown-stripped)
      - structured bullets / questions for the smart-board display
      - media items (visuals, videos) if available
      - source citations if source_mode is active
      - a transcript_entry for the frontend history store

    Empty or invalid commands are rejected with a 400 and a helpful
    user-facing message — no raw stack traces are ever returned.
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "EMPTY_COMMAND",
                "message": "Command cannot be empty. Please type or speak a question."
            }
        )

    try:
        payload = await build_assistant_response(
            session_id=request.session_id,
            text=text,
            mode_hint=request.mode_hint,
            source_mode=request.source_mode or False,
        )
    except Exception as exc:
        logger.error(f"[UnifiedCommand] Orchestrator error for session={request.session_id}: {exc}")
        return GlobalResponse(
            status="error",
            error={
                "code": "PROCESSING_ERROR",
                "message": "The assistant ran into a problem. Please try again."
            }
        )

    data = payload.model_dump()

    # Inject a transcript_entry so the frontend can update history without
    # additional round-trips.
    data["transcript_entry"] = {
        "role": "assistant",
        "text": data.get("response_text") or data.get("answer_text") or "",
        "mode": data.get("mode"),
        "language_mode": data.get("language_mode"),
    }

    return GlobalResponse(status="success", data=data)
