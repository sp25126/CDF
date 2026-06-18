from pydantic import BaseModel
from typing import Optional

class Chunk(BaseModel):
    """A text chunk from a source document."""
    chunk_id: str
    source_id: str
    source_title: str
    text: str
    page_number: int = 1
    section_label: Optional[str] = None
