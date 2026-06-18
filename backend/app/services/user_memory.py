from app.schemas.memory import UserMemory
from app.services.memory_store import user_store
from typing import Optional

class UserMemoryService:
    def get_user(self, user_id: str) -> UserMemory:
        data = user_store.get(user_id)
        if data:
            return UserMemory(**data)
        return UserMemory(user_id=user_id)

    def update_user(self, memory: UserMemory):
        user_store.set(memory.user_id, memory.model_dump())

    def record_correction(self, user_id: str, correction: dict):
        memory = self.get_user(user_id)
        memory.corrections.append(correction)
        self.update_user(memory)

    def update_preferences(self, user_id: str, **kwargs):
        memory = self.get_user(user_id)
        for key, value in kwargs.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        self.update_user(memory)

user_memory_service = UserMemoryService()
