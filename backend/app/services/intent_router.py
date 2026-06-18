"""
Intent detection and routing for the CDF classroom assistant.

This module provides deterministic intent classification using simple heuristics.
Intent types: explain, quiz, followup, stop, unclear.
"""

import re
from typing import Tuple


# Intent patterns (lowercase)
EXPLAIN_KEYWORDS = {
    "explain", "teach", "what is", "how does", "describe", "tell",
    "define", "meaning", "concept", "why", "how", "what's",
    "what does", "how to", "समझाओ", "बताओ", "क्या है"
}

QUIZ_KEYWORDS = {
    "quiz", "test", "question", "mcq", "ask me", "question me",
    "query", "exam", "पूछो", "सवाल", "प्रश्न", "टेस्ट"
}

FOLLOWUP_KEYWORDS = {
    "repeat", "again", "slower", "simpler", "once more",
    "फिर से", "दोबारा", "आसान", "धीमा", "फिर"
}

STOP_KEYWORDS = {
    "stop", "cancel", "pause", "quit", "exit", "end",
    "done", "enough", "बंद करो", "रुको", "समाप्त"
}


def normalize_text(text: str) -> str:
    """
    Normalize user input for robust matching.
    
    - Lowercase
    - Remove extra whitespace
    - Remove punctuation but preserve meaning
    
    Args:
        text: Raw user input
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    text = text.lower().strip()
    # Remove common punctuation but keep alphanumeric and spaces
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text


def detect_intent(text: str) -> str:
    """
    Detect the user's intent from their command.
    
    Intent rules:
    - "explain", "teach", "what is", "how does" -> explain
    - "quiz", "test", "question", "mcq" -> quiz
    - "repeat", "slower", "again" -> followup
    - "stop", "cancel", "pause" -> stop
    - otherwise -> unclear
    """
    if not text:
        return "unclear"
        
    t = text.lower()
    
    # Check explain keywords
    if any(k in t for k in ["explain", "teach", "what is", "how does"]):
        return "explain"
        
    # Check quiz keywords
    if any(k in t for k in ["quiz", "test", "question", "mcq"]):
        return "quiz"
        
    # Check followup keywords
    if any(k in t for k in ["repeat", "slower", "again"]):
        return "followup"
        
    # Check stop keywords
    if any(k in t for k in ["stop", "cancel", "pause"]):
        return "stop"
        
    return "unclear"

