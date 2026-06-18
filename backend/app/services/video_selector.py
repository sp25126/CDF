import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def select_best_video(ranked_videos: List[dict]) -> Optional[Dict[str, Any]]:
    """
    Choose exactly one best video for in-app embedding and return the other candidates as alternatives.
    Returns: {"primary": VideoDict, "alternatives": [VideoDict]}
    """
    if not ranked_videos:
        return None
        
    primary = ranked_videos[0]
    alternatives = ranked_videos[1:3] # Max 2 alternatives
    
    logger.info(f"[VideoSelector] Selected primary video: {primary.get('video_title')}")
    
    return {
        "primary": primary,
        "alternatives": alternatives
    }
