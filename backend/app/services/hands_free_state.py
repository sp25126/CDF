import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class HandsFreeState:
    """
    Manages the state of the hands-free voice loop per session.
    States:
    - idle: Default state. Not listening.
    - listening: Mic is open, waiting for user speech.
    - command_recognized: Just recognized a command, processing it.
    - explaining: Currently giving an explanation.
    - quizzing: Currently running a quiz.
    - awaiting_followup: Waiting for user to answer a follow-up or quiz question.
    - speaking: Currently speaking TTS.
    """
    
    def __init__(self):
        # Maps session_id to state dictionary
        self._states: Dict[str, dict] = {}

    def _ensure_session(self, session_id: str):
        if session_id not in self._states:
            self._states[session_id] = {
                "hands_free_mode": False,
                "assistant_state": "idle",
                "current_quiz_index": 0,
                "follow_up_prompt": None,
                "next_voice_commands": []
            }

    def enable_hands_free(self, session_id: str):
        self._ensure_session(session_id)
        self._states[session_id]["hands_free_mode"] = True
        logger.info(f"Hands-free mode enabled for session {session_id}")

    def disable_hands_free(self, session_id: str):
        self._ensure_session(session_id)
        self._states[session_id]["hands_free_mode"] = False
        self._states[session_id]["assistant_state"] = "idle"
        logger.info(f"Hands-free mode disabled for session {session_id}")

    def is_hands_free(self, session_id: str) -> bool:
        self._ensure_session(session_id)
        return self._states[session_id]["hands_free_mode"]

    def set_state(self, session_id: str, state: str, prompt: str = None, commands: list = None):
        self._ensure_session(session_id)
        self._states[session_id]["assistant_state"] = state
        self._states[session_id]["follow_up_prompt"] = prompt
        self._states[session_id]["next_voice_commands"] = commands or []
        logger.info(f"Session {session_id} state changed to {state}")

    def get_state(self, session_id: str) -> dict:
        self._ensure_session(session_id)
        return self._states[session_id]

    def reset_quiz_index(self, session_id: str):
        self._ensure_session(session_id)
        self._states[session_id]["current_quiz_index"] = 0

    def get_quiz_index(self, session_id: str) -> int:
        self._ensure_session(session_id)
        return self._states[session_id]["current_quiz_index"]

    def increment_quiz_index(self, session_id: str):
        self._ensure_session(session_id)
        self._states[session_id]["current_quiz_index"] += 1

# Singleton instance
state_manager = HandsFreeState()
