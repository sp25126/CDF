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


def detect_intent(text: str) -> Tuple[str, float]:
    """
    Detect the user's intent from their command.
    
    Rules (in priority order):
    1. Check for stop keywords -> "stop" (confidence: 0.9)
    2. Check for quiz keywords -> "quiz" (confidence: 0.85)
    3. Check for followup keywords -> "followup" (confidence: 0.8)
    4. Check for explain keywords -> "explain" (confidence: 0.85)
    5. Short multi-word text -> "explain" (confidence: 0.5)
    6. Otherwise -> "unclear" (confidence: 0.3)
    
    Args:
        text: User's command (raw input)
        
    Returns:
        Tuple[intent, confidence] where confidence is 0.0-1.0
    """
    if not text:
        return ("unclear", 0.0)
    
    norm_text = normalize_text(text)
    tokens = norm_text.split()
    
    # Check stop first (highest priority)
    for keyword in STOP_KEYWORDS:
        if keyword in norm_text:
            return ("stop", 0.9)
    
    # Check quiz keywords
    for keyword in QUIZ_KEYWORDS:
        if keyword in norm_text:
            return ("quiz", 0.85)
    
    # Check followup keywords
    for keyword in FOLLOWUP_KEYWORDS:
        if keyword in norm_text:
            return ("followup", 0.8)
    
    # Check explain keywords
    for keyword in EXPLAIN_KEYWORDS:
        if keyword in norm_text:
            return ("explain", 0.85)
    
    # If text is reasonable length and contains alphanumeric, might be a topic
    if len(tokens) >= 2 and len(text) > 3:
        return ("explain", 0.5)  # Lower confidence, could be unclear
    
    # Otherwise unclear
    return ("unclear", 0.3)
