from typing import List, Optional
import uuid
import logging
import httpx
from app.schemas.visual import VisualRef

logger = logging.getLogger(__name__)

async def verify_url(url: str) -> bool:
    """Perform a fast asynchronous HEAD or GET request with a compliant User-Agent to verify a URL is loadable."""
    headers = {
        "User-Agent": "ShikshaSahayak/1.0 (contact: contact@shikshasahayak.org)"
    }
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.head(url, headers=headers)
            if resp.status_code == 200:
                return True
            # HEAD might be blocked or not supported, try GET
            resp = await client.get(url, headers=headers)
            return resp.status_code == 200
    except Exception as e:
        logger.warning(f"[VisualRetrieval] URL verification failed for {url}: {e}")
        return False

async def retrieve_visuals(topic: str, class_level: Optional[str] = None) -> List[VisualRef]:
    """
    Retrieves and validates visuals for a given topic.
    Returns 1-3 verified, loadable images or an empty list if none are reachable.
    """
    topic_lower = topic.lower()
    candidates = []
    
    if "photosynthesis" in topic_lower:
        candidates.append(
            VisualRef(
                type="diagram",
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Photosynthesis_en.svg/960px-Photosynthesis_en.svg.png",
                description="Diagram showing photosynthesis process",
                visual_id=str(uuid.uuid4())
            )
        )
    elif "gravity" in topic_lower:
        candidates.append(
            VisualRef(
                type="diagram",
                url="https://upload.wikimedia.org/wikipedia/commons/7/7d/Gravity_action-reaction.gif",
                description="Action-reaction forces of gravity",
                visual_id=str(uuid.uuid4())
            )
        )
    elif "solar system" in topic_lower or "planets" in topic_lower:
        candidates.append(
            VisualRef(
                type="image",
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Planets2013.svg/960px-Planets2013.svg.png",
                description="The Solar System",
                visual_id=str(uuid.uuid4())
            )
        )
    
    # Generic fallback only if no topic matched
    if not candidates:
        candidates.append(
            VisualRef(
                type="image",
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Book_icon_%28closed%29_-_Blue_and_gold.svg/500px-Book_icon_%28closed%29_-_Blue_and_gold.svg.png",
                description="Educational Resource",
                visual_id=str(uuid.uuid4())
            )
        )
        
    # Asynchronously validate URLs
    verified_visuals = []
    for vis in candidates:
        if await verify_url(vis.url):
            verified_visuals.append(vis)
        else:
            logger.warning(f"[VisualRetrieval] URL failed verification and was discarded: {vis.url}")
            
    return verified_visuals
