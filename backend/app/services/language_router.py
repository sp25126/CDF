"""
Language detection and routing for the CDF classroom assistant.

This module provides deterministic language detection using simple heuristics.
Language modes: hinglish (default), english, hindi.
"""

from typing import Tuple


def detect_language(text: str) -> str:
    """
    Detect the requested language mode from the user's command.
    
    Rules:
    - If teacher explicitly says "in English", "English mein", "English" -> english
    - If teacher explicitly says "in Hindi", "Hindi mein", "pure Hindi" -> hindi
    - Otherwise -> hinglish
    """
    if not text:
        return "hinglish"
    
    t = text.lower()
    
    # Check for Hinglish first to avoid overlaps (though Hinglish contains 'english' substring)
    if "hinglish" in t:
        return "hinglish"
        
    # Check for English
    if "in english" in t or "english mein" in t or "english me" in t or "english" in t:
        return "english"
    
    # Check for Hindi
    if "in hindi" in t or "hindi mein" in t or "hindi me" in t or "pure hindi" in t or "hindi" in t:
        return "hindi"
    
    return "hinglish"


