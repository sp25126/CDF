import os
import io
import uuid
import json
import logging
from typing import List, Dict, Any
from pypdf import PdfReader
from bs4 import BeautifulSoup
import httpx
import re
from datetime import datetime, timezone

from app.schemas.source import SourceMetadata
from app.services.chunking import chunk_source_text
from app.schemas.chunk import Chunk

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
SOURCES_FILE = os.path.join(DATA_DIR, "sources.json")
CHUNKS_FILE = os.path.join(DATA_DIR, "chunks.json")

class SourceIngestService:
    def __init__(self):
        self.sources: Dict[str, dict] = {}
        self.chunks: List[dict] = []
        self._init_db()

    def _init_db(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(SOURCES_FILE):
            try:
                with open(SOURCES_FILE, "r", encoding="utf-8") as f:
                    self.sources = json.load(f)
            except Exception as e:
                logger.error(f"Error loading sources.json: {e}")
        
        if os.path.exists(CHUNKS_FILE):
            try:
                with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception as e:
                logger.error(f"Error loading chunks.json: {e}")

    def _save_db(self):
        try:
            with open(SOURCES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.sources, f, ensure_ascii=False, indent=2)
            with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving DB: {e}")

    def add_text_source(self, title: str, text: str) -> dict:
        source_id = str(uuid.uuid4())
        metadata = SourceMetadata(
            id=source_id,
            title=title,
            type="text",
            origin_url=None,
            language=self.detect_text_language(text),
            created_at=self._get_timestamp(),
            page_count=1
        ).model_dump()
        
        self.sources[source_id] = metadata
        chunks = chunk_source_text(text, source_id, title)
        self.chunks.extend([c.model_dump() for c in chunks])
        self._save_db()
        return metadata

    async def add_url_source(self, url: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=15.0)
            r.raise_for_status()
            html = r.text

        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.extract()

        title = soup.title.string.strip() if soup.title else url
        title = title or url

        raw_text = soup.get_text(separator="\n")
        lines = (line.strip() for line in raw_text.splitlines())
        phrases = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(p for p in phrases if p)

        source_id = str(uuid.uuid4())
        metadata = SourceMetadata(
            id=source_id,
            title=title,
            type="url",
            origin_url=url,
            language=self.detect_text_language(text),
            created_at=self._get_timestamp(),
            page_count=1
        ).model_dump()

        self.sources[source_id] = metadata
        chunks = chunk_source_text(text, source_id, title)
        self.chunks.extend([c.model_dump() for c in chunks])
        self._save_db()
        return metadata

    def add_pdf_source(self, filename: str, file_bytes: bytes) -> dict:
        reader = PdfReader(io.BytesIO(file_bytes))
        page_chunks = []
        source_id = str(uuid.uuid4())
        full_text = ""

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            page_text = page.extract_text() or ""
            full_text += page_text + "\n"
            
            chunks = chunk_source_text(page_text, source_id, filename, page_number=page_num)
            page_chunks.extend([c.model_dump() for c in chunks])

        metadata = SourceMetadata(
            id=source_id,
            title=filename,
            type="pdf",
            origin_url=None,
            language=self.detect_text_language(full_text),
            created_at=self._get_timestamp(),
            page_count=len(reader.pages)
        ).model_dump()

        self.sources[source_id] = metadata
        self.chunks.extend(page_chunks)
        self._save_db()
        return metadata

    def delete_source(self, source_id: str) -> bool:
        if source_id in self.sources:
            del self.sources[source_id]
            self.chunks = [c for c in self.chunks if c["source_id"] != source_id]
            self._save_db()
            return True
        return False

    def list_sources(self) -> List[dict]:
        return list(self.sources.values())

    def get_all_chunks(self) -> List[dict]:
        return self.chunks

    def detect_text_language(self, text: str) -> str:
        if not text:
            return "English"
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(re.findall(r'\w', text))
        if total_chars > 0 and (hindi_chars / total_chars) > 0.1:
            return "Hindi"
        return "English"

    def _get_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

# Global instance
source_ingest_service = SourceIngestService()
