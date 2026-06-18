import re
from typing import List
from app.schemas.chunk import Chunk
from app.services.source_ingest import source_ingest_service

def retrieve_relevant_chunks(query: str, source_id: str = None, limit: int = 3) -> List[Chunk]:
    """
    Retrieve the most relevant chunks for a teacher question.
    Uses simple keyword retrieval token frequency ranking.
    """
    all_chunks = source_ingest_service.get_all_chunks()
    
    if source_id:
        chunks_to_search = [c for c in all_chunks if c["source_id"] == source_id]
    else:
        chunks_to_search = all_chunks

    if not query or not chunks_to_search:
        return []

    # Tokenize query
    stop_words = {"the", "a", "an", "on", "of", "in", "to", "for", "with", "is", "are", "and", "or"}
    query_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 1 and w.lower() not in stop_words]
    
    if not query_words:
        # Fallback to absolute match if query only has stop words
        query_words = [w.lower() for w in re.findall(r'\w+', query)]

    scored_chunks = []
    for chunk_data in chunks_to_search:
        chunk_text_lower = chunk_data["text"].lower()
        score = 0
        matched_unique_words = 0

        for word in query_words:
            count = chunk_text_lower.count(word)
            if count > 0:
                matched_unique_words += 1
                score += count * len(word) # weight longer word matches higher
            elif len(word) >= 4:
                # Simple prefix stem-matching heuristic
                stem = word[:4]
                stem_count = chunk_text_lower.count(stem)
                if stem_count > 0:
                    matched_unique_words += 0.5
                    score += stem_count * 2 # partial match score weight

        if score > 0:
            scored_chunks.append((score, matched_unique_words, len(chunk_data["text"]), chunk_data))

    # Rank chunks:
    # 1. Higher score (weighted word matches)
    # 2. More unique query words matched
    # 3. Shorter chunk length (for conciseness)
    scored_chunks.sort(key=lambda x: (-x[0], -x[1], x[2]))
    
    return [Chunk(**item[3]) for item in scored_chunks[:limit]]
