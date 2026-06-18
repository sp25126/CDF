from pydantic import BaseModel, Field
from typing import Optional

class VisualRef(BaseModel):
    """Reference to a visual asset."""
    type: str = Field(..., description="image, diagram, chart, etc.")
    url: str
    description: Optional[str] = None
    visual_id: Optional[str] = None
