from app.schemas.memory import SessionMemory
from app.services.memory_store import session_store
from typing import Optional

class SessionMemoryService:
    def get_session(self, session_id: str) -> SessionMemory:
        data = session_store.get(session_id)
        if data:
            return SessionMemory(**data)
        return SessionMemory(session_id=session_id)

    def update_session(self, memory: SessionMemory):
        session_store.set(memory.session_id, memory.model_dump())

    def add_turn(self, session_id: str, role: str, content: str):
        memory = self.get_session(session_id)
        memory.recent_turns.append({"role": role, "content": content})
        # Keep only the last 10 turns to avoid bloat
        if len(memory.recent_turns) > 10:
            memory.recent_turns = memory.recent_turns[-10:]
        self.update_session(memory)

    def clear_session(self, session_id: str):
        session_store.delete(session_id)

session_memory_service = SessionMemoryService()
