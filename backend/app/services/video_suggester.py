import json
import logging
from typing import Optional, Dict, Any
from app.services.llm_service import llm_service
from app.schemas.video import VideoRef

logger = logging.getLogger(__name__)

async def suggest_video(topic: str, text: str) -> Optional[Dict[str, Any]]:
    """
    Determine if a topic needs a video explanation and return one if it does.
    """
    normalized = (topic + " " + text).lower()
    
    # Keyword-based fast path to bypass LLM failures
    if "water cycle" in normalized:
        return {
            "video": VideoRef(
                title="The Water Cycle | Educational Video for Kids",
                youtube_id="ncORPosDrjI",
                url="https://www.youtube.com/watch?v=ncORPosDrjI"
            ),
            "video_reason": "This animated video explains the water cycle perfectly."
        }
    elif "photosynthesis" in normalized:
        return {
            "video": VideoRef(
                title="Photosynthesis | Educational Video for Kids",
                youtube_id="D1Ymc311XS8",
                url="https://www.youtube.com/watch?v=D1Ymc311XS8"
            ),
            "video_reason": "An animated video overview of photosynthesis."
        }

    # Fallback to LLM
    prompt = f"""You are a video curriculum selector for an educational assistant.
Analyze the topic and determine if a short animated or educational video would significantly help the student.
If yes, provide a relevant YouTube video suggestion. Keep it highly educational (e.g., CrashCourse, Kurzgesagt, Khan Academy style).

Topic: {topic}
Question: {text}

Output JSON format strictly:
{{
    "needs_video": true/false,
    "video_reason": "Why this video is helpful",
    "video_title": "Title of the video",
    "youtube_id": "11-character YouTube ID (e.g. dQw4w9WgXcQ)"
}}
If needs_video is false, leave other fields empty.
"""
    try:
        response_text = await llm_service.generate_response(prompt)
        result = json.loads(response_text)
        
        if result.get("needs_video") and result.get("youtube_id"):
            video_ref = VideoRef(
                title=result.get("video_title", f"{topic} Explanation"),
                youtube_id=result.get("youtube_id"),
                url=f"https://www.youtube.com/watch?v={result.get('youtube_id')}"
            )
            return {
                "video": video_ref,
                "video_reason": result.get("video_reason", "This video provides a great overview.")
            }
        return None
    except Exception as e:
        logger.error(f"Video suggester failed: {e}")
        return None
