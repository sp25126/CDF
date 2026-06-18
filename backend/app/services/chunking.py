import uuid
import re
from typing import List
from app.schemas.chunk import Chunk

def chunk_source_text(text: str, source_id: str, source_title: str, page_number: int = 1) -> List[Chunk]:
    """
    Split text into overlapping chunks of 500-800 characters.
    """
    if not text.strip():
        return []

    chunks = []
    chunk_size = 600
    overlap = 120
    start = 0

    # Basic parsing of section labels if any
    section_label = None
    
    while start < len(text):
        end = start + chunk_size
        chunk_content = text[start:end]
        
        # Adjust chunk boundaries to end at a word or sentence if possible
        if end < len(text):
            last_space = chunk_content.rfind(' ')
            last_newline = chunk_content.rfind('\n')
            boundary = max(last_space, last_newline)
            if boundary > chunk_size // 2:
                chunk_content = chunk_content[:boundary]
                end = start + boundary

        # Detect a potential section label (e.g. "Section 1", "Chapter 2")
        match = re.search(r'\b(section|chapter|part)\s+\d+', chunk_content.lower())
        if match:
            section_label = match.group(0).title()

        chunks.append(Chunk(
            chunk_id=str(uuid.uuid4()),
            source_id=source_id,
            source_title=source_title,
            text=chunk_content.strip(),
            page_number=page_number,
            section_label=section_label
        ))
        
        start = end - overlap
        if start >= len(text) or chunk_size > len(text) - end:
            break
            
    # If there's remaining text
    if start < len(text) and len(text) - start > 50:
        chunks.append(Chunk(
            chunk_id=str(uuid.uuid4()),
            source_id=source_id,
            source_title=source_title,
            text=text[start:].strip(),
            page_number=page_number,
            section_label=section_label
        ))

    return chunks
