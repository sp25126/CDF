"""
Language detection and routing for the CDF classroom assistant.

This module provides deterministic language detection using simple heuristics.
Language modes: hinglish (default), english, hindi.
"""

from typing import Tuple


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect the requested language mode from the user's command.
    
    Rules:
    - If explicitly "in English" / "English mein" / "English me" -> english (confidence: 0.95)
    - If explicitly "in Hindi" / "Hindi mein" / "Hindi me" / "pure Hindi" -> hindi (confidence: 0.95)
    - If explicitly "in Hinglish" / "Hinglish mein" -> hinglish (confidence: 0.95)
    - Otherwise -> hinglish (default, confidence: 0.8)
    
    Args:
        text: User's command
        
    Returns:
        Tuple[language_mode, confidence] where language_mode is 'hinglish', 'english', or 'hindi'
    """
    if not text:
        return ("hinglish", 0.8)
    
    t = text.lower()
    
    # Check for explicit English request
    english_patterns = {
        "in english", "english mein", "english me", "english में",
        "english hi", "english only", "pure english"
    }
    if any(pattern in t for pattern in english_patterns):
        return ("english", 0.95)
    
    # Check for explicit Hindi request
    hindi_patterns = {
        "in hindi", "hindi mein", "hindi me", "hindi में",
        "hindi hi", "hindi only", "pure hindi", "शुद्ध हिंदी"
    }
    if any(pattern in t for pattern in hindi_patterns):
        return ("hindi", 0.95)
    
    # Check for explicit Hinglish request
    hinglish_patterns = {
        "in hinglish", "hinglish mein", "hinglish me", "hinglish में"
    }
    if any(pattern in t for pattern in hinglish_patterns):
        return ("hinglish", 0.95)
    
    # Default to hinglish (Hindi + English mix)
    return ("hinglish", 0.8)

