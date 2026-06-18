import re
from typing import Optional, Dict

class MemoryEventDetector:
    def detect_preference_change(self, text: str) -> Optional[Dict[str, str]]:
        """
        Detect if the user is explicitly asking for a preference change.
        """
        text = text.lower()
        
        # Language preference
        if "always use english" in text or "english mein baat karo" in text:
            return {"preferred_language": "english"}
        if "always use hindi" in text or "hindi mein baat karo" in text:
            return {"preferred_language": "hindi"}
        if "always use hinglish" in text:
            return {"preferred_language": "hinglish"}
            
        # Class level
        match = re.search(r"always for class (\d+)", text)
        if match:
            return {"preferred_class_level": f"Class {match.group(1)}"}
            
        return None

    def detect_correction(self, text: str) -> Optional[str]:
        """
        Detect if the user is correcting the assistant.
        """
        text = text.lower()
        if "wrong" in text or "galat" in text or "not correct" in text:
            return text
        return None

memory_event_detector = MemoryEventDetector()
