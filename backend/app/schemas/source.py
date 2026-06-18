from pydantic import BaseModel
from typing import Optional

class SourceMetadata(BaseModel):
    """Metadata for an ingested source."""
    id: str
    title: str
    type: str  # "pdf", "text", "url"
    origin_url: Optional[str] = None
    language: str
    created_at: str
    page_count: int = 1
