from pydantic import BaseModel
from typing import Optional

class VideoRef(BaseModel):
    """Reference to a video."""
    title: str
    youtube_id: str
    duration: Optional[int] = None
    video_id: Optional[str] = None
    url: Optional[str] = None
