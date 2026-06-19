"""
Session endpoints — /api/session/{session_id}

Wired to the real session_memory_service so the frontend gets live state
instead of mock hardcoded quiz data.
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from app.api.schemas import GlobalResponse, SessionState, SessionUpdateRequest, ResetResponse
from app.services.session_memory import session_memory_service
from app.services.source_ingest import source_ingest_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{session_id}", response_model=GlobalResponse, summary="Get live session state")
async def get_session(session_id: str):
    """
    GET /api/session/{session_id}

    Returns the current live state for a session.
    If the session has never been used, returns a safe idle state — never crashes.
    The frontend uses this on page load to restore the last known state.
    """
    mem = session_memory_service.get_session(session_id)
    turns = mem.recent_turns or []

    # Extract the last topic from the most recent assistant turn
    last_topic: str | None = None
    for turn in reversed(turns):
        if turn.get("role") == "assistant":
            content = turn.get("content", "")
            if content:
                last_topic = content[:60].split(".")[0]  # first sentence fragment
            break

    state = SessionState(
        session_id=session_id,
        mode=mem.mode or "idle",
        language_mode=mem.language_mode or "hinglish",
        assistant_state=mem.assistant_state or "idle",
        hands_free=mem.hands_free or False,
        recent_turns_count=len(turns),
        last_topic=last_topic,
        last_updated=datetime.now(timezone.utc).isoformat(),
    )
    return GlobalResponse(status="success", data=state.model_dump())


@router.post("/{session_id}", response_model=GlobalResponse, summary="Update session preferences")
async def update_session(session_id: str, body: SessionUpdateRequest):
    """
    POST /api/session/{session_id}

    Lets the frontend persist lightweight session preferences (language mode,
    hands-free toggle, source mode). Does not store sensitive data.
    """
    mem = session_memory_service.get_session(session_id)
    if body.language_mode is not None:
        mem.language_mode = body.language_mode
    if body.hands_free is not None:
        mem.hands_free = body.hands_free
    if body.source_mode is not None:
        mem.source_mode = body.source_mode
    session_memory_service.update_session(mem)
    return GlobalResponse(status="success", data={"session_id": session_id, "updated": True})


@router.post("/{session_id}/clear", response_model=GlobalResponse, summary="Clear session state")
async def clear_session(session_id: str):
    """
    POST /api/session/{session_id}/clear

    Resets a session to idle — safe for teacher handoffs and new lessons.
    """
    session_memory_service.clear_session(session_id)
    logger.info(f"[Session] Cleared session {session_id}")
    return GlobalResponse(
        status="success",
        data=ResetResponse(session_id=session_id, cleared=True, message="Session cleared").model_dump()
    )


@router.get("/{session_id}/last", response_model=GlobalResponse, summary="Get last interaction")
async def get_last_interaction(session_id: str):
    """
    GET /api/session/{session_id}/last

    Returns the last assistant response stored in session memory so the
    frontend can restore the canvas on page refresh.
    Returns an empty-safe payload if no prior interaction exists.
    """
    mem = session_memory_service.get_session(session_id)
    turns = mem.recent_turns or []

    last_assistant = None
    for turn in reversed(turns):
        if turn.get("role") == "assistant":
            last_assistant = turn
            break

    return GlobalResponse(
        status="success",
        data={
            "session_id": session_id,
            "has_history": len(turns) > 0,
            "last_assistant_turn": last_assistant,
            "language_mode": mem.language_mode or "hinglish",
            "mode": mem.mode or "idle",
            "assistant_state": mem.assistant_state or "idle",
        }
    )
