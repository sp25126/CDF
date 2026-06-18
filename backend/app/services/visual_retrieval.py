from typing import List, Optional
import uuid
from app.schemas.visual import VisualRef

def retrieve_visuals(topic: str, class_level: Optional[str] = None) -> List[VisualRef]:
    """
    Mock implementation of visual retrieval.
    Returns 1-3 deterministic mock images related to common educational topics.
    """
    topic_lower = topic.lower()
    
    if "photosynthesis" in topic_lower:
        return [
            VisualRef(
                type="diagram",
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Photosynthesis_en.svg/800px-Photosynthesis_en.svg.png",
                description="Diagram showing photosynthesis process",
                visual_id=str(uuid.uuid4())
            )
        ]
    elif "gravity" in topic_lower:
        return [
            VisualRef(
                type="diagram",
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Gravity_action-reaction.svg/640px-Gravity_action-reaction.svg.png",
                description="Action-reaction forces of gravity",
                visual_id=str(uuid.uuid4())
            )
        ]
    elif "solar system" in topic_lower or "planets" in topic_lower:
        return [
            VisualRef(
                type="image",
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Planets2013.svg/1024px-Planets2013.svg.png",
                description="The Solar System",
                visual_id=str(uuid.uuid4())
            )
        ]
    
    # Generic fallback
    return [
        VisualRef(
            type="image",
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Book_icon_%28closed%29_-_Blue_and_gold.svg/640px-Book_icon_%28closed%29_-_Blue_and_gold.svg.png",
            description="Educational Resource",
            visual_id=str(uuid.uuid4())
        )
    ]
