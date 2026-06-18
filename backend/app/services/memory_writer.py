from app.services.user_memory import user_memory_service
from app.services.memory_events import memory_event_detector
from datetime import datetime, timezone

class MemoryWriter:
    def process_turn_for_long_term_memory(self, user_id: str, text: str):
        """
        Analyze a turn and update long-term user memory if needed.
        """
        # 1. Check for explicit preference changes
        prefs = memory_event_detector.detect_preference_change(text)
        if prefs:
            user_memory_service.update_preferences(user_id, **prefs)
            
        # 2. Check for corrections
        correction_text = memory_event_detector.detect_correction(text)
        if correction_text:
            user_memory_service.record_correction(user_id, {
                "text": correction_text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        # 3. Add to recurring topics (simple logic: if text is short and noun-like)
        if 3 < len(text.split()) < 6:
            user = user_memory_service.get_user(user_id)
            if text not in user.recurring_topics:
                user.recurring_topics.append(text)
                if len(user.recurring_topics) > 10:
                    user.recurring_topics.pop(0)
                user_memory_service.update_user(user)

memory_writer = MemoryWriter()
