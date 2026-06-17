import os
import io
import re
import uuid
import json
import logging
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
SOURCES_FILE = os.path.join(DATA_DIR, "sources.json")
CHUNKS_FILE = os.path.join(DATA_DIR, "chunks.json")

class SourceService:
    def __init__(self):
        self.sources: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(SOURCES_FILE):
            try:
                with open(SOURCES_FILE, "r", encoding="utf-8") as f:
                    self.sources = json.load(f)
            except Exception as e:
                logger.error(f"Error loading sources.json: {e}")
                self.sources = {}
        else:
            self.sources = {}

        if os.path.exists(CHUNKS_FILE):
            try:
                with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception as e:
                logger.error(f"Error loading chunks.json: {e}")
                self.chunks = []
        else:
            self.chunks = []

    def _save_db(self):
        try:
            with open(SOURCES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.sources, f, ensure_ascii=False, indent=2)
            with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving source DB to disk: {e}")

    def add_text_source(self, title: str, text: str) -> Dict[str, Any]:
        """
        Add a plain text source, chunk it, and save to index.
        """
        source_id = str(uuid.uuid4())
        metadata = {
            "id": source_id,
            "title": title,
            "type": "text",
            "page_count": 1,
            "origin_url": None,
            "language": self.detect_text_language(text),
            "created_at": self._get_timestamp()
        }
        self.sources[source_id] = metadata
        
        # Chunk text
        chunks = self.chunk_text(text, source_id, title)
        self.chunks.extend(chunks)
        self._save_db()
        return metadata

    async def add_url_source(self, url: str) -> Dict[str, Any]:
        """
        Scrape a URL, extract text, chunk it, and save.
        """
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=15.0)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        
        # Clean up script, style, header, footer elements
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.extract()

        title = soup.title.string.strip() if soup.title else url
        title = title or url

        # Extract main text content
        raw_text = soup.get_text(separator="\n")
        lines = (line.strip() for line in raw_text.splitlines())
        phrases = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(p for p in phrases if p)

        source_id = str(uuid.uuid4())
        metadata = {
            "id": source_id,
            "title": title,
            "type": "url",
            "page_count": 1,
            "origin_url": url,
            "language": self.detect_text_language(text),
            "created_at": self._get_timestamp()
        }
        self.sources[source_id] = metadata

        chunks = self.chunk_text(text, source_id, title)
        self.chunks.extend(chunks)
        self._save_db()
        return metadata

    def add_pdf_source(self, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """
        Parse a PDF, chunk page-by-page, and save.
        """
        reader = PdfReader(io.BytesIO(file_bytes))
        page_chunks = []
        source_id = str(uuid.uuid4())
        full_text = ""

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            page_text = page.extract_text() or ""
            full_text += page_text + "\n"
            
            # Chunk the page text specifically to preserve page numbers
            page_blocks = self.chunk_text(page_text, source_id, filename, page_number=page_num)
            page_chunks.extend(page_blocks)

        metadata = {
            "id": source_id,
            "title": filename,
            "type": "pdf",
            "page_count": len(reader.pages),
            "origin_url": None,
            "language": self.detect_text_language(full_text),
            "created_at": self._get_timestamp()
        }
        self.sources[source_id] = metadata
        self.chunks.extend(page_chunks)
        self._save_db()
        return metadata

    def chunk_text(self, text: str, source_id: str, source_title: str, page_number: int = 1) -> List[Dict[str, Any]]:
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

            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "source_id": source_id,
                "source_title": source_title,
                "text": chunk_content.strip(),
                "page_number": page_number,
                "section_label": section_label
            })
            
            start = end - overlap
            if start >= len(text) or chunk_size > len(text) - end:
                break
                
        # If there's remaining text
        if start < len(text) and len(text) - start > 50:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "source_id": source_id,
                "source_title": source_title,
                "text": text[start:].strip(),
                "page_number": page_number,
                "section_label": section_label
            })

        return chunks

    def retrieve_chunks(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Perform case-insensitive keyword token frequency ranking on chunks.
        """
        if not query or not self.chunks:
            return []

        # Tokenize query
        stop_words = {"the", "a", "an", "on", "of", "in", "to", "for", "with", "is", "are", "and", "or"}
        query_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 1 and w.lower() not in stop_words]
        
        if not query_words:
            # Fallback to absolute match if query only has stop words
            query_words = [w.lower() for w in re.findall(r'\w+', query)]

        scored_chunks = []
        for chunk in self.chunks:
            chunk_text_lower = chunk["text"].lower()
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
                scored_chunks.append((score, matched_unique_words, len(chunk["text"]), chunk))

        # Rank chunks:
        # 1. Higher score (weighted word matches)
        # 2. More unique query words matched
        # 3. Shorter chunk length (for conciseness)
        scored_chunks.sort(key=lambda x: (-x[0], -x[1], x[2]))
        
        return [item[3] for item in scored_chunks[:limit]]

    def delete_source(self, source_id: str) -> bool:
        """
        Delete a source and all associated chunks.
        """
        if source_id in self.sources:
            del self.sources[source_id]
            self.chunks = [c for c in self.chunks if c["source_id"] != source_id]
            self._save_db()
            return True
        return False

    def list_sources(self) -> List[Dict[str, Any]]:
        """
        List all source metadata.
        """
        return list(self.sources.values())

    def detect_text_language(self, text: str) -> str:
        """
        Detect if text is mostly Devanagari (Hindi) or Latin (English/Hinglish).
        """
        if not text:
            return "English"
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(re.findall(r'\w', text))
        if total_chars > 0 and (hindi_chars / total_chars) > 0.1:
            return "Hindi"
        return "English"

    def _get_timestamp(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

# Instantiate global service
source_service = SourceService()
