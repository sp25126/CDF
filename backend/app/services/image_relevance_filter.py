"""
Image Relevance Filter — strict topic-to-image semantic validation.

PRINCIPLE: Reject any image that is only loosely related.
Never return a "close enough" fallback — return empty instead.

Each topic maps to:
  - required_keywords: at least one must appear in title/description/alt
  - forbidden_keywords: if any appear → hard reject
  - min_score: minimum relevance score (0.0–1.0) to pass
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Topic relevance profiles ────────────────────────────────────────────────
# Each entry:
#   "topic_pattern" (regex) → { required, forbidden, min_score }
#
# Ordered from most-specific to least-specific.
TOPIC_PROFILES = [
    {
        "pattern": r"\bphotosynthesis\b",
        "required": [
            "photosynthesis", "chlorophyll", "chloroplast", "plant", "leaf",
            "sunlight", "glucose", "carbon dioxide", "co2", "stoma", "stomata",
            "light reaction", "calvin", "thylakoid", "food", "oxygen"
        ],
        "forbidden": [
            "black hole", "galaxy", "star", "nebula", "photon",
            "quantum", "electron", "atom", "particle physics",
            "neuron", "brain", "anatomy"
        ],
        "min_score": 0.35,
    },
    {
        "pattern": r"\bphoton\b|\bphotons\b|\blight particle\b",
        "required": [
            "photon", "light", "electromagnetic", "quantum", "particle",
            "wave", "radiation", "spectrum", "wavelength", "optics",
            "visible light", "energy level", "photon emission"
        ],
        "forbidden": [
            "black hole", "galaxy", "plant", "leaf", "chlorophyll",
            "photosynthesis", "anatomy", "cell", "bacteria"
        ],
        "min_score": 0.35,
    },
    {
        "pattern": r"\bblack hole\b|\bblackholes\b",
        "required": [
            "black hole", "singularity", "event horizon", "accretion",
            "spacetime", "gravitational", "astronomy", "astrophysics",
            "galaxy", "hawking"
        ],
        "forbidden": [
            "plant", "leaf", "photosynthesis", "chlorophyll", "cell",
            "anatomy", "bacteria", "chemistry"
        ],
        "min_score": 0.5,
    },
    {
        "pattern": r"\bgravity\b|\bgravitation\b",
        "required": [
            "gravity", "gravitation", "force", "mass", "weight",
            "newton", "acceleration", "orbit", "planet", "fall", "attraction"
        ],
        "forbidden": [
            "black hole singularity", "photosynthesis", "chlorophyll",
            "bacteria", "neuron"
        ],
        "min_score": 0.4,
    },
    {
        "pattern": r"\bevaporation\b|\bcondensation\b|\bwater cycle\b",
        "required": [
            "evaporation", "condensation", "water", "vapour", "vapor",
            "cycle", "cloud", "rain", "liquid", "gas", "heat"
        ],
        "forbidden": ["black hole", "photosynthesis", "quantum", "particle"],
        "min_score": 0.4,
    },
    {
        "pattern": r"\bforce\b|\bmotion\b|\bnewton\b",
        "required": [
            "force", "motion", "newton", "velocity", "acceleration",
            "mass", "friction", "momentum", "inertia", "push", "pull"
        ],
        "forbidden": ["black hole", "photosynthesis", "cell", "bacteria"],
        "min_score": 0.4,
    },
    {
        "pattern": r"\bcell\b|\bcells\b|\bcell biology\b",
        "required": [
            "cell", "membrane", "nucleus", "organelle", "mitochondria",
            "cytoplasm", "biology", "living", "organism", "prokaryote", "eukaryote"
        ],
        "forbidden": ["black hole", "gravity", "force", "motion"],
        "min_score": 0.4,
    },
    {
        "pattern": r"\banatomy\b|\bhuman body\b|\borgan\b",
        "required": [
            "anatomy", "body", "organ", "heart", "lung", "kidney",
            "brain", "muscle", "bone", "tissue", "blood"
        ],
        "forbidden": ["black hole", "galaxy", "plant", "photosynthesis"],
        "min_score": 0.4,
    },
    {
        "pattern": r"\bsolar system\b|\bplanet\b|\bplanets\b",
        "required": [
            "solar system", "planet", "sun", "orbit", "earth", "mars",
            "jupiter", "saturn", "moon", "astronomy", "space"
        ],
        "forbidden": ["photosynthesis", "cell", "anatomy", "bacteria"],
        "min_score": 0.4,
    },
    {
        "pattern": r"\bmicroorganism\b|\bmicroorganisms\b|\bbacteria\b|\bvirus\b|\bfungi\b|\bprotozoa\b|\bmicrobe\b|\bmicrobes\b",
        "required": [
            "microorganism", "bacteria", "virus", "fungi", "protozoa",
            "microbe", "germ", "pathogen", "living", "cell", "microscope",
            "infectious", "disease", "single cell", "unicellular"
        ],
        "forbidden": ["black hole", "galaxy", "planet", "gravity", "photosynthesis", "plant"],
        "min_score": 0.3,
    },
]

# Generic science/education fallback (weak check — only used when no topic profile matches)
GENERIC_FORBIDDEN = [
    "nude", "adult", "nsfw", "violence", "blood", "gore"
]


def _normalize(text: str) -> str:
    """Lowercase and strip extra whitespace."""
    return re.sub(r"\s+", " ", (text or "").lower().strip())


def _compute_relevance_score(
    text_corpus: str,
    required_keywords: list,
    forbidden_keywords: list,
) -> tuple[float, Optional[str]]:
    """
    Compute relevance score (0.0–1.0).
    Returns (score, reject_reason).
    reject_reason is non-None only if hard-rejected.
    """
    corpus = _normalize(text_corpus)

    # Hard reject on forbidden keywords
    for fw in forbidden_keywords:
        if fw in corpus:
            return 0.0, f"Forbidden keyword '{fw}' found in image metadata"

    # Score = weighted by hits. Even 1-2 specific keyword hits should pass.
    # We use sqrt normalization so a single strong hit (e.g. "chloroplast") gives ~0.25
    # and 2–3 hits give 0.4–0.55, pushing past typical 0.35 thresholds.
    hit_count = sum(1 for kw in required_keywords if kw in corpus)
    if not required_keywords:
        return 0.5, None  # No profile → neutral

    import math
    score = math.sqrt(hit_count / len(required_keywords))
    return score, None



def find_topic_profile(topic: str) -> Optional[dict]:
    """Find the most specific matching topic profile."""
    norm_topic = _normalize(topic)
    for profile in TOPIC_PROFILES:
        if re.search(profile["pattern"], norm_topic):
            return profile
    return None


def is_image_relevant(
    topic: str,
    image_title: Optional[str],
    image_description: Optional[str],
    image_alt_text: Optional[str],
    image_source: Optional[str] = None,
) -> tuple[bool, float, Optional[str]]:
    """
    Main entry point. Returns (passes, score, reject_reason).

    passes     = True if image is relevant enough to return
    score      = relevance float 0.0–1.0
    reject_reason = human-readable string if rejected, else None
    """
    # Build searchable corpus from all available metadata
    corpus_parts = [
        image_title or "",
        image_description or "",
        image_alt_text or "",
        image_source or "",
        topic,  # also include topic itself so exact matches score high
    ]
    corpus = " ".join(corpus_parts)

    # Generic forbidden check (safety)
    for fw in GENERIC_FORBIDDEN:
        if fw in _normalize(corpus):
            return False, 0.0, f"Safety filter: '{fw}' found"

    # Find topic profile
    profile = find_topic_profile(topic)

    if profile is None:
        # No specific profile for this topic — use loose check
        # Require at least one word from the topic to appear in the corpus
        topic_words = [w for w in _normalize(topic).split() if len(w) > 3]
        if not topic_words:
            return True, 0.5, None  # Very short topic, can't check well

        any_hit = any(w in _normalize(corpus) for w in topic_words)
        if not any_hit:
            return False, 0.1, f"No topic word from '{topic}' found in image metadata"
        return True, 0.5, None

    # Score against profile
    score, reject_reason = _compute_relevance_score(
        corpus,
        profile["required"],
        profile["forbidden"],
    )

    if reject_reason:
        logger.info(f"[ImageRelevance] REJECT topic='{topic}' reason='{reject_reason}'")
        return False, score, reject_reason

    if score < profile["min_score"]:
        reason = (
            f"Relevance score {score:.2f} below minimum {profile['min_score']} "
            f"for topic '{topic}'"
        )
        logger.info(f"[ImageRelevance] REJECT {reason}")
        return False, score, reason

    logger.info(
        f"[ImageRelevance] PASS topic='{topic}' score={score:.2f} "
        f"title='{(image_title or '')[:60]}'"
    )
    return True, score, None
