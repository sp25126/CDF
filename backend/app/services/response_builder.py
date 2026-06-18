from typing import List, Optional, Dict, Any
from app.schemas.response import AssistantResponse, QuizPayload, SourceRef
from app.schemas.visual import VisualRef
from app.schemas.video import VideoRef
import base64

def build_final_response(
    session_id: str,
    intent: str,
    language_mode: str,
    text: str,
    answer_text: Optional[str] = None,
    quiz_payload: Optional[QuizPayload] = None,
    next_actions: List[str] = None,
    confidence: float = 1.0,
    requires_clarification: bool = False,
    avatar_state: str = "idle",
    source_refs: List[SourceRef] = None,
    visuals: List[VisualRef] = None,
    videos: List[VideoRef] = None,
    visual_reason: Optional[str] = None,
    video_reason: Optional[str] = None,
    audio_content: Optional[bytes] = None,
    title: Optional[str] = None,
    grade_level: Optional[int] = None,
    bullets: List[str] = None,
    example: Optional[str] = None,
    recap: Optional[str] = None,
    questions_compat: List[Any] = None,
    source_mode: bool = False,
    hands_free_mode: bool = False,
    voice_command_mode: bool = False,
    assistant_state: str = "idle",
    follow_up_prompt: Optional[str] = None,
    next_voice_commands: List[str] = None
) -> AssistantResponse:
    
    audio_base64 = None
    if audio_content:
        audio_b64 = base64.b64encode(audio_content).decode("utf-8")
        audio_base64 = f"data:audio/mp3;base64,{audio_b64}"

    return AssistantResponse(
        session_id=session_id,
        mode=intent,
        language_mode=language_mode,
        transcript_text=text,
        answer_text=answer_text,
        message=answer_text if intent == "unclear" else None,
        quiz=quiz_payload,
        next_actions=next_actions or [],
        suggestions=next_actions or [],
        confidence=confidence,
        requires_clarification=requires_clarification,
        avatar_state=avatar_state,
        source_refs=source_refs or [],
        citations=source_refs or [],
        visuals=visuals or [],
        videos=videos or [],
        visual_reason=visual_reason,
        video_reason=video_reason,
        source_mode=source_mode,
        audio_base64=audio_base64,
        
        hands_free_mode=hands_free_mode,
        voice_command_mode=voice_command_mode,
        assistant_state=assistant_state,
        follow_up_prompt=follow_up_prompt,
        next_voice_commands=next_voice_commands or [],
        
        # Explain card attributes
        title=title,
        grade_level=grade_level,
        bullets=bullets or [],
        example=example,
        recap=recap,
        response_text=answer_text,
        
        # Quiz card compatibility
        questions=questions_compat or []
    )
