import json
import logging
from typing import Optional, Dict, Any, List
from app.services.llm_service import llm_service
from app.schemas.video import VideoRef

logger = logging.getLogger(__name__)

async def search_videos(topic: str, text: str) -> Optional[Dict[str, Any]]:
    """
    Determine if a topic needs a video explanation and return ranked video candidates.
    Returns primary video and alternatives.
    """
    normalized = (topic + " " + text).lower()

    # Fallback to LLM to generate 2-3 highly relevant educational videos
    prompt = f"""You are a video curriculum selector for an educational assistant.
Analyze the topic and determine if a short animated or educational video would significantly help the student.
If yes, provide 2-3 relevant YouTube video suggestions. Keep it highly educational (e.g., CrashCourse, Kurzgesagt, Khan Academy style).
Consider relevance, language match, and educational quality to rank them. The first one is the best for primary playback.

Topic: {topic}
Question: {text}

Output JSON format strictly:
{{
    "needs_video": true/false,
    "candidates": [
        {{
            "video_reason": "Why this video is helpful",
            "video_title": "Title of the video",
            "youtube_id": "11-character YouTube ID (e.g. dQw4w9WgXcQ)"
        }},
        ...
    ]
}}
If needs_video is false, leave candidates empty.
"""
    try:
        response_text = await llm_service.generate_response(prompt, task_type="classify")
        result = json.loads(response_text)
        
        if result.get("needs_video") and result.get("candidates"):
            candidates_data = result.get("candidates", [])
            if not candidates_data:
                return None
                
            videos = []
            for item in candidates_data:
                video_ref = VideoRef(
                    title=item.get("video_title", f"{topic} Explanation"),
                    youtube_id=item.get("youtube_id", ""),
                    url=f"https://www.youtube.com/watch?v={item.get('youtube_id', '')}"
                )
                videos.append({
                    "video": video_ref,
                    "reason": item.get("video_reason", "This video provides a great overview.")
                })
                
            if videos:
                return {
                    "primary": videos[0],
                    "alternatives": videos[1:]
                }
        return None
    except Exception as e:
        logger.error(f"Video search failed: {e}")
        return None
