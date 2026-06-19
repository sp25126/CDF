"""
Language detection and routing for the CDF classroom assistant.

This module provides deterministic language detection using simple heuristics.
Language modes: hinglish (default), english, hindi.
"""

from typing import Tuple


def detect_language_details(text: str) -> Tuple[str, bool]:
    """
    Detect the requested language mode from the user's command and whether it was explicitly requested.
    Returns (language_mode, is_explicit).
    """
    if not text:
        return "hinglish", False
    
    t = text.lower()
    
    # Check for Hinglish
    if "hinglish" in t:
        return "hinglish", True
        
    # Check for English
    if "in english" in t or "english mein" in t or "english me" in t or "english" in t:
        return "english", True
    
    # Check for Hindi
    if "in hindi" in t or "hindi mein" in t or "hindi me" in t or "pure hindi" in t or "hindi" in t:
        return "hindi", True
    
    return "hinglish", False


def detect_language(text: str) -> str:
    """
    Detect the requested language mode from the user's command.
    
    Rules:
    - If teacher explicitly says "in English", "English mein", "English" -> english
    - If teacher explicitly says "in Hindi", "Hindi mein", "pure Hindi" -> hindi
    - Otherwise -> hinglish
    """
    return detect_language_details(text)[0]


