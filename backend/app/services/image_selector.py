"""
Image Selector — selects the best image from a relevance-filtered list.
Ranks by relevance score embedded in the 'reason' field, then by description richness.
"""
import logging
import re
from typing import List, Optional

from app.schemas.visual import VisualRef

logger = logging.getLogger(__name__)


def _extract_score(vis: VisualRef) -> float:
    """Extract the relevance score from the reason string, e.g. 'Relevance score 0.75 ...'"""
    if vis.reason:
        match = re.search(r"score\s+([\d.]+)", vis.reason)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    # Fall back to description length as a weak proxy
    return len(vis.description or "") / 1000.0


def select_best_image(images: List[VisualRef]) -> Optional[VisualRef]:
    """
    Select the single best image from the already-filtered list.
    Ranks by relevance score first, then description richness.
    """
    if not images:
        return None

    ranked = sorted(images, key=_extract_score, reverse=True)
    best = ranked[0]
    logger.info(
        f"[ImageSelector] Selected: '{best.title}' "
        f"score={_extract_score(best):.2f} url={best.url}"
    )
    return best
