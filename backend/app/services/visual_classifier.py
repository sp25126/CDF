import json
import logging
import re
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

async def detect_visual_need(topic: str, text: str) -> dict:
    """
    Determine if a topic needs visual clarification.
    """
    normalized = (topic + " " + text).lower()
    
    # Keyword-based fast path to bypass LLM failures
    visual_triggers = ["photosynthesis", "gravity", "solar system", "planets", "water cycle", "anatomy", "heart", "diagram"]
    if any(trigger in normalized for trigger in visual_triggers):
        return {
            "needs_visual": True,
            "visual_reason": "Visual diagrams help explain this concept clearly.",
            "visual_confidence": 0.9
        }

    # Fallback to LLM for unknown topics
    prompt = f"""You are a visual learning classifier for an educational assistant.
Analyze the topic and student's question to determine if a picture, diagram, or chart would significantly help understanding.

Topic: {topic}
Question: {text}

Output JSON format strictly:
{{
    "needs_visual": true/false,
    "visual_reason": "Brief reason why a visual helps or is unnecessary",
    "visual_confidence": 0.0 to 1.0
}}
"""
    try:
        response_text = await llm_service.generate_response(prompt)
        result = json.loads(response_text)
        return {
            "needs_visual": bool(result.get("needs_visual", False)),
            "visual_reason": result.get("visual_reason", ""),
            "visual_confidence": float(result.get("visual_confidence", 0.0))
        }
    except Exception as e:
        logger.error(f"Visual classifier failed: {e}")
        return {
            "needs_visual": False,
            "visual_reason": "",
            "visual_confidence": 0.0
        }
