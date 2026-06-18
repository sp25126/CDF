import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceCommandRouter:
    """
    Detects short, standard voice commands and routes them quickly without
    needing full LLM inference in many cases. Now includes strict filtering
    for hands-free noise.
    """
    
    def __init__(self):
        # Maps simple phrases to standard intents
        self.commands = {
            "stop": "stop",
            "cancel": "stop",
            "quit": "stop",
            "exit": "stop",
            "stop hands free": "stop",
            "stop hands-free": "stop",
            "pause": "stop",
            
            "next": "next",
            "next question": "next",
            "move on": "next",
            "skip": "next",
            "go on": "next",
            
            "repeat": "repeat",
            "say that again": "repeat",
            "what did you say": "repeat",
            "pardon": "repeat",
            
            "slower": "slower",
            "speak slower": "slower",
            "too fast": "slower",
            
            "simpler": "simpler",
            "more simply": "simpler",
            "make it simpler": "simpler",
            "i don't understand": "simpler",
            
            "example": "example",
            "give an example": "example",
            "give example": "example",
            "show me an example": "example",
            
            "ask a question": "ask_question",
            "ask one question": "ask_question",
            "start quiz": "ask_question",
            
            "show answer": "show_answer",
            "what is the answer": "show_answer",
            "tell me the answer": "show_answer",
            
            "end quiz": "end_quiz",
            "stop quiz": "end_quiz"
        }
        
        # Filler and noise patterns to ignore entirely
        self.filler_words = ["maafi", "apology", "sorry", "um", "uh", "hmm", "maybe", "thank you", "chahta", "samajh nahi"]

    def is_noise(self, text: str) -> bool:
        """
        Check if the text is likely just background noise or a filler response from the STT.
        """
        normalized = text.lower()
        # If it contains any filler/apology words strongly, reject
        for filler in self.filler_words:
            if filler in normalized:
                return True
        return False

    def route_command(self, text: str, is_hands_free: bool = False) -> Optional[str]:
        """
        Returns a mapped command string if recognized.
        If is_hands_free is True, strictly gate the response to prevent false triggers.
        Returns 'unclear' if it's considered noise during hands_free.
        Returns None if no standard command is matched, so LLM can process it.
        """
        if is_hands_free and self.is_noise(text):
            logger.info(f"VoiceCommandRouter rejected noise/filler: '{text}'")
            return "unclear"
            
        normalized = text.lower().strip()
        # Remove punctuation
        for p in [".", ",", "?", "!"]:
            normalized = normalized.replace(p, "")
            
        if normalized in self.commands:
            logger.info(f"VoiceCommandRouter matched: '{text}' -> {self.commands[normalized]}")
            return self.commands[normalized]
            
        # Also do a simple "contains" check for very short matches if it's less than 5 words
        words = normalized.split()
        if len(words) <= 5:
            for phrase, intent in self.commands.items():
                if phrase in normalized:
                    logger.info(f"VoiceCommandRouter fuzzy matched: '{text}' -> {intent}")
                    return intent
                    
        # In hands_free mode, if it's super short but didn't match a command, it might be junk.
        if is_hands_free and len(words) < 2 and not self.commands.get(normalized):
            return "unclear"

        return None

voice_command_router = VoiceCommandRouter()
