"""
Visual Classifier — determines if a topic needs image/diagram support.

Uses a keyword fast-path first to avoid unnecessary LLM calls.
Falls back to LLM only for topics not covered by the keyword list.
On LLM error: defaults to True (show visuals) to avoid silent failures.
"""
import json
import logging
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

# Topics that strongly benefit from visual diagrams
VISUAL_TRIGGER_KEYWORDS = [
    # Biology
    "photosynthesis", "cell", "cells", "mitosis", "meiosis",
    "anatomy", "heart", "lung", "kidney", "organ", "dna", "genetics",
    "ecosystem", "food chain", "bacteria", "virus", "fungi",
    "microorganism", "microorganisms", "microbe", "microbes", "protozoa",
    "digestion", "respiration", "nutrition", "reproduction",
    # Physics
    "gravity", "gravitation", "solar system", "planet", "planets",
    "black hole", "wave", "optics", "reflection", "refraction",
    "circuit", "electricity", "magnetism", "light", "spectrum",
    "photon", "photons", "quantum",
    # Chemistry
    "atom", "molecule", "periodic table", "reaction", "acid", "base",
    "bond", "crystal", "structure",
    # Earth / Water
    "water cycle", "evaporation", "condensation", "erosion", "volcano",
    "earthquake", "weather",
    # Math / Geometry
    "diagram", "graph", "chart", "triangle", "circle", "polygon",
    "geometry", "coordinate",
    # Generic
    "cycle", "process", "structure", "layer", "cross section", "model",
]


async def detect_visual_need(topic: str, text: str) -> dict:
    """
    Determine if a topic needs visual/diagram support.
    Returns {needs_visual, visual_reason, visual_confidence}
    """
    normalized = (topic + " " + text).lower()

    # Fast-path keyword check
    for trigger in VISUAL_TRIGGER_KEYWORDS:
        if trigger in normalized:
            logger.info(f"[VisualClassifier] Fast-path match: '{trigger}' → needs_visual=True")
            return {
                "needs_visual": True,
                "visual_reason": f"'{trigger}' is a visual concept that benefits from diagrams.",
                "visual_confidence": 0.9,
            }

    # LLM fallback for unknown topics
    prompt = (
        "You are a visual learning classifier for an educational assistant.\n"
        "Analyze the topic and student's question to determine if a picture, diagram, "
        "or chart would significantly help understanding.\n\n"
        f"Topic: {topic}\nQuestion: {text}\n\n"
        "Output JSON format strictly:\n"
        "{{\n"
        '    "needs_visual": true/false,\n'
        '    "visual_reason": "Brief reason",\n'
        '    "visual_confidence": 0.0 to 1.0\n'
        "}}"
    )

    try:
        response_text = await llm_service.generate_response(prompt, task_type="classify")
        result = json.loads(response_text)
        return {
            "needs_visual": bool(result.get("needs_visual", True)),
            "visual_reason": result.get("visual_reason", ""),
            "visual_confidence": float(result.get("visual_confidence", 0.5)),
        }
    except Exception as e:
        logger.warning(f"[VisualClassifier] LLM fallback failed: {e} — defaulting to needs_visual=True")
        return {
            "needs_visual": True,
            "visual_reason": "Defaulting to visual search (classifier unavailable).",
            "visual_confidence": 0.5,
        }
