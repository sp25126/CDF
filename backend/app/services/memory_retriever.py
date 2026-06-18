from app.services.session_memory import session_memory_service
from app.services.user_memory import user_memory_service
from app.services.memory_summarizer import memory_summarizer
from typing import Dict, Any

class MemoryRetriever:
    def retrieve_memory_context(self, session_id: str, user_id: str, query: str) -> Dict[str, Any]:
        """
        Gather session and user memory and format it for the prompt assembler.
        """
        session = session_memory_service.get_session(session_id)
        user = user_memory_service.get_user(user_id)
        
        # Summarize turns
        recent_turns_summary = memory_summarizer.summarize_recent_turns(session.recent_turns)
        
        # Format user preferences
        user_prefs = {
            "preferred_language": user.preferred_language,
            "preferred_class_level": user.preferred_class_level or "Not specified",
            "recurring_topics": user.recurring_topics[-5:], # Last 5 topics
            "correction_history": [c.get("text") for c in user.corrections[-3:]] # Last 3 corrections
        }
        
        return {
            "session_summary": recent_turns_summary,
            "user_preferences": user_prefs,
            "assistant_state": session.assistant_state,
            "current_mode": session.mode,
            "current_language_mode": session.language_mode,
            "hands_free": session.hands_free
        }

memory_retriever = MemoryRetriever()
