"""
Topic Splitter — smart compound query detection for independent media retrieval.

Improvements over the basic decompose_query:
  1. Detects both educational topics in a compound query (not just a grammatical split)
  2. Uses the image_relevance_filter topic profiles to confirm both halves are real topics
  3. Handles "A and B", "A vs B", "A with B", "A ke saath B" patterns
  4. Limits to max 2 sub-topics to keep response manageable
"""
import re
import logging
from typing import List

from app.services.question_decomposer import decompose_query

logger = logging.getLogger(__name__)

# Known educational topic keywords for validation
# Used to confirm each split part is actually a meaningful topic
KNOWN_TOPIC_KEYWORDS = {
    "photosynthesis", "photon", "photons", "black hole", "black holes",
    "gravity", "gravitation", "force", "motion", "newton",
    "evaporation", "condensation", "water cycle",
    "cell", "cells", "anatomy", "human body",
    "solar system", "planets", "planet",
    "electricity", "magnetism", "wave", "sound",
    "chemical", "chemistry", "reaction",
    "atom", "molecule", "element",
    "light", "optics", "reflection", "refraction",
    "heat", "temperature", "energy",
    "ecosystem", "food chain", "biodiversity",
    "mitosis", "meiosis", "dna", "genetics",
    "acid", "base", "ph",
    "friction", "pressure", "work", "power",
    "nucleus", "electron", "proton", "neutron",
    "microorganism", "microorganisms", "bacteria", "virus", "fungi",
    "protozoa", "microbe", "microbes", "pathogen",
    "digestion", "respiration", "nutrition", "reproduction",
}

# Conjunction patterns for splitting
SPLIT_PATTERN = re.compile(
    r"\b(and|also|plus|aur|bhi|vs|versus|with|ke saath|aur bhi)\b",
    re.IGNORECASE,
)


def _is_educational_topic(text: str) -> bool:
    """Check if a text fragment contains at least one known educational topic keyword."""
    normalized = text.lower()
    return any(kw in normalized for kw in KNOWN_TOPIC_KEYWORDS)


def split_into_topics(query: str) -> List[str]:
    """
    Split a compound educational query into independent sub-topics.
    Returns [query] (unchanged) if:
      - No conjunction found
      - Split results in non-educational fragments
      - Either half is too short

    Returns [topic_a, topic_b] if both halves are valid educational topics.
    """
    if not query:
        return []

    # Use the existing decomposer for grammatical splitting
    parts = decompose_query(query)

    if len(parts) <= 1:
        logger.info(f"[TopicSplitter] Single topic: '{query}'")
        return [query]

    # Validate that each part is an actual educational topic (not just a grammatical fragment)
    validated = []
    for part in parts[:2]:  # max 2
        stripped = part.strip()
        if len(stripped) < 4:
            continue
        if _is_educational_topic(stripped):
            validated.append(stripped)
        else:
            # Not recognized as educational — treat as context for the original query
            logger.info(
                f"[TopicSplitter] Part '{stripped}' not recognized as educational topic — "
                f"treating query as single topic"
            )
            return [query]

    if len(validated) >= 2:
        logger.info(f"[TopicSplitter] Compound split: {validated}")
        return validated

    logger.info(f"[TopicSplitter] No valid compound split — single topic: '{query}'")
    return [query]
