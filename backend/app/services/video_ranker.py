"""
Video Ranker — multi-factor ranking of candidate educational videos.

Scoring factors (higher = better):
  1. Language match (primary factor)
  2. Topic overlap (number of matching topic keywords)
  3. Duration preference (shorter preferred for classroom)
  4. Title quality (longer = more descriptive)
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


def rank_videos(videos: List[dict], target_topic: str, language: str) -> List[dict]:
    """
    Rank candidate videos using topic relevance, language match, and duration.
    Returns the same list sorted by score descending.
    """
    if not videos:
        return []

    target_words = set(target_topic.lower().split())

    def score_video(video: dict) -> float:
        score = 0.0
        v_lang = video.get("language", "english")

        # ── Language match ──────────────────────────────────────────────
        if language == v_lang:
            score += 10.0
        elif language == "hinglish" and v_lang in ("hindi", "english"):
            score += 7.0
        elif language == "hindi" and v_lang == "hinglish":
            score += 6.0

        # ── Topic keyword overlap ───────────────────────────────────────
        entry_topics = [t.lower() for t in video.get("topics", [])]
        topic_hits = sum(
            1 for t in entry_topics
            if t in target_topic or any(word in t for word in target_words if len(word) > 3)
        )
        score += topic_hits * 3.0

        # ── Duration preference (<10 min = better for classroom) ────────
        duration = video.get("duration", 9999)
        if duration < 300:
            score += 4.0
        elif duration < 600:
            score += 3.0
        elif duration < 900:
            score += 1.0

        # ── Title quality (more descriptive = slight bonus) ─────────────
        title_len = len(video.get("video_title", ""))
        if title_len > 30:
            score += 1.0

        return score

    ranked = sorted(videos, key=score_video, reverse=True)
    scores = [score_video(v) for v in ranked]
    logger.info(
        f"[VideoRanker] Ranked {len(ranked)} videos for '{target_topic}' lang='{language}'. "
        f"Top scores: {scores[:3]}"
    )
    return ranked
