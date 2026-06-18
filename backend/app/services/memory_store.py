import os
import json
import logging
from typing import Dict, Any

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
SESSION_MEMORY_FILE = os.path.join(DATA_DIR, "session_memory.json")
USER_MEMORY_FILE = os.path.join(DATA_DIR, "user_memory.json")

logger = logging.getLogger(__name__)

class MemoryStore:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory file {self.file_path}: {e}")
                self.data = {}

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory file {self.file_path}: {e}")

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()

    def delete(self, key: str):
        if key in self.data:
            del self.data[key]
            self.save()

# Global instances for simple file-based storage
session_store = MemoryStore(SESSION_MEMORY_FILE)
user_store = MemoryStore(USER_MEMORY_FILE)
