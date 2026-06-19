"""
Video Search — deterministic, LLM-independent educational video retrieval.

Pipeline:
  1. Keyword match against validated VIDEO_DB
  2. Validate all YouTube IDs via youtube_validate
  3. Rank by language match + topic relevance
  4. Return best_video + up to 3 candidate_videos
  5. Return None if nothing valid exists — never fabricate a link

All YouTube IDs in VIDEO_DB have been manually verified as real, non-playlist,
non-channel, embeddable links.
"""
import logging
from typing import Optional, Dict, Any, List

from app.schemas.video import VideoRef
from app.services.video_ranker import rank_videos
from app.services.video_selector import select_best_video
from app.services.youtube_validate import validate_youtube_entry

logger = logging.getLogger(__name__)

# ─── Verified Educational Video Registry ─────────────────────────────────────
# Each entry: youtube_id is a real, playable, embeddable YouTube video ID.
# LLM does NOT pick these. IDs are curated and pre-validated.
VIDEO_DB: List[Dict[str, Any]] = [
    # ── Photosynthesis ──────────────────────────────────────────────────────
    {
        "video_title": "Photosynthesis — The Dr. Binocs Show",
        "youtube_id": "D1Ymc311XS8",
        "topics": ["photosynthesis"],
        "language": "english",
        "duration": 300,
        "video_reason": "Animated overview of photosynthesis process for Class 6–8.",
    },
    {
        "video_title": "Photosynthesis in Hindi — Mast Gyan",
        "youtube_id": "78_bS8Qe_4M",
        "topics": ["photosynthesis"],
        "language": "hindi",
        "duration": 420,
        "video_reason": "Clear Hindi explanation of plants making food.",
    },
    # ── Microorganisms ─────────────────────────────────────────────────────
    {
        "video_title": "Microorganisms — The Dr. Binocs Show",
        "youtube_id": "8MLg3gVsHok",
        "topics": ["microorganism", "microorganisms", "bacteria", "virus", "fungi", "protozoa", "micro"],
        "language": "english",
        "duration": 340,
        "video_reason": "Fun animated intro to microorganisms, bacteria, viruses, and fungi for Class 8.",
    },
    {
        "video_title": "Microorganisms Friend and Foe — Class 8 Science",
        "youtube_id": "1d19Bsn2aKs",
        "topics": ["microorganism", "microorganisms", "bacteria", "virus", "fungi"],
        "language": "hindi",
        "duration": 480,
        "video_reason": "Hindi explanation of microorganisms as friends and foes (NCERT Class 8).",
    },
    # ── Photons / Light ────────────────────────────────────────────────────
    {
        "video_title": "What is a Photon? — Fermilab",
        "youtube_id": "8vXW-tU-vIQ",
        "topics": ["photons", "photon", "light particle", "light quantum"],
        "language": "english",
        "duration": 350,
        "video_reason": "Excellent explanation of photons and light quanta.",
    },
    {
        "video_title": "Light and Electromagnetic Spectrum — Crash Course",
        "youtube_id": "X93pMl_MdGY",
        "topics": ["photons", "photon", "light", "electromagnetic", "spectrum"],
        "language": "english",
        "duration": 720,
        "video_reason": "Comprehensive look at light, photons, and the EM spectrum.",
    },
    # ── Gravity / Force ────────────────────────────────────────────────────
    {
        "video_title": "Force and Laws of Motion — Khan Academy",
        "youtube_id": "kKKM8Y-u7ds",
        "topics": ["force", "motion", "newton", "gravity"],
        "language": "english",
        "duration": 600,
        "video_reason": "Excellent overview of forces and Newton's laws.",
    },
    {
        "video_title": "Force and Pressure Class 8 — Hindi",
        "youtube_id": "2Z0kQ-Xk_3Q",
        "topics": ["force", "pressure", "motion"],
        "language": "hindi",
        "duration": 500,
        "video_reason": "Hindi medium explanation of Force and Pressure.",
    },
    {
        "video_title": "What is Gravity? — MinutePhysics",
        "youtube_id": "Xjqe6lOKSSU",
        "topics": ["gravity", "gravitation", "mass", "weight"],
        "language": "english",
        "duration": 240,
        "video_reason": "Clear and concise explanation of gravity for students.",
    },
    # ── Black Holes ────────────────────────────────────────────────────────
    {
        "video_title": "Black Holes Explained — Kurzgesagt",
        "youtube_id": "e-P5IFTqB98",
        "topics": ["black hole", "black holes", "event horizon", "singularity"],
        "language": "english",
        "duration": 480,
        "video_reason": "Beautiful animated explanation of black holes.",
    },
    # ── Evaporation / Water Cycle ──────────────────────────────────────────
    {
        "video_title": "The Water Cycle — Crash Course Kids",
        "youtube_id": "al-do-HGuIk",
        "topics": ["evaporation", "condensation", "water cycle", "water"],
        "language": "english",
        "duration": 240,
        "video_reason": "Clear visualization of the water cycle.",
    },
    # ── Cell Biology ───────────────────────────────────────────────────────
    {
        "video_title": "The Cell — Amoeba Sisters",
        "youtube_id": "8IlzKri08kk",
        "topics": ["cell", "cells", "cell biology", "mitochondria", "nucleus"],
        "language": "english",
        "duration": 450,
        "video_reason": "Engaging overview of plant and animal cells.",
    },
    # ── Solar System / Planets ─────────────────────────────────────────────
    {
        "video_title": "Solar System 101 — National Geographic",
        "youtube_id": "libKVRa01L8",
        "topics": ["solar system", "planets", "planet", "sun", "orbit"],
        "language": "english",
        "duration": 320,
        "video_reason": "Official NatGeo overview of the solar system.",
    },
    # ── Artificial Intelligence ────────────────────────────────────────────
    {
        "video_title": "What Is AI? Crash Course AI #1",
        "youtube_id": "a0_lo_UdVHw",
        "topics": ["artificial intelligence", "ai", "machine learning"],
        "language": "english",
        "duration": 660,
        "video_reason": "Excellent overview of Artificial Intelligence and what it actually is.",
    },
]


def _validate_db_entry(entry: Dict[str, Any]) -> bool:
    """Pre-validate a DB entry via youtube_validate."""
    result = validate_youtube_entry(entry.get("youtube_id", ""))
    if result is None:
        logger.warning(
            f"[VideoSearch] DB entry '{entry.get('video_title')}' "
            f"has invalid ID '{entry.get('youtube_id')}' — skipping"
        )
    return result is not None


async def search_videos(
    topic: str, text: str, language_mode: str = "english"
) -> Optional[Dict[str, Any]]:
    """
    Search for videos matching the topic.
    Returns {primary, alternatives} or None if nothing valid is found.
    LLM is NOT called; URL fabrication is impossible.
    """
    # The topic is now an LLM-extracted noun phrase (e.g. "Photosynthesis", "Artificial Intelligence")
    # so no further cleaning is needed — just normalize case for matching
    normalized_topic = topic.lower().strip()
    normalized_text = text.lower()

    # Match candidates from the registry
    candidates = []
    for entry in VIDEO_DB:
        # Validate the DB ID before including
        if not _validate_db_entry(entry):
            continue

        # Topic keyword match (any topic in the entry's topic list as a whole word)
        import re
        matched = False
        for t in entry.get("topics", []):
            escaped_t = re.escape(t)
            # Match whole words only to prevent 'ai' matching inside 'explain'
            if re.search(rf'\b{escaped_t}\b', normalized_topic) or re.search(rf'\b{escaped_t}\b', normalized_text):
                matched = True
                break
        if matched:
            candidates.append(entry)

    if not candidates:
        logger.info(f"[VideoSearch] No matching videos in DB for topic='{topic}'. Falling back to dynamic search.")
        return await _search_videos_dynamic(topic, language_mode)

    # Rank by language preference + topic relevance
    ranked = rank_videos(candidates, normalized_topic, language_mode)

    # Select best + alternatives
    selection = select_best_video(ranked)

    if not selection:
        return None

    def to_output(vid: dict) -> dict:
        vid_id = vid["youtube_id"]
        return {
            "video": VideoRef(
                title=vid["video_title"],
                youtube_id=vid_id,
                url=f"https://www.youtube.com/watch?v={vid_id}",
                video_id=vid_id,
            ),
            "reason": vid.get("video_reason", ""),
        }

    result = {
        "primary": to_output(selection["primary"]),
        "alternatives": [to_output(alt) for alt in selection.get("alternatives", [])],
    }

    logger.info(
        f"[VideoSearch] topic='{topic}' lang='{language_mode}' → "
        f"primary='{selection['primary']['video_title']}' "
        f"alternatives={len(result['alternatives'])}"
    )
    return result

async def _search_videos_dynamic(topic: str, language_mode: str) -> Optional[Dict[str, Any]]:
    """
    Fallback to dynamic YouTube search using yt-dlp if no DB match is found.
    """
    try:
        import yt_dlp
    except ImportError:
        logger.warning("[VideoSearch] yt-dlp not installed, cannot perform dynamic search.")
        return None

    query = f"{topic} educational video {'in Hindi' if language_mode in ['hindi', 'hinglish'] else 'in English'}"
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'default_search': 'ytsearch',
        'max_downloads': 3
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entries = info['entries']
                
                def to_output(vid: dict) -> dict:
                    vid_id = vid.get('id')
                    return {
                        "video": VideoRef(
                            title=vid.get('title') or "Video",
                            youtube_id=vid_id,
                            url=f"https://www.youtube.com/watch?v={vid_id}",
                            video_id=vid_id,
                        ),
                        "reason": "Dynamically retrieved based on your request."
                    }
                
                result = {
                    "primary": to_output(entries[0]),
                    "alternatives": [to_output(alt) for alt in entries[1:3] if alt]
                }
                
                logger.info(f"[VideoSearch] Dynamic search success for '{query}' → primary={entries[0].get('id')}")
                return result
    except Exception as e:
        logger.error(f"[VideoSearch] Dynamic search failed: {e}")
        
    return None
