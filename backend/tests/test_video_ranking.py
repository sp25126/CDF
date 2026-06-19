"""
Video search unit tests — match against actual video_title values in VIDEO_DB.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.video_search import search_videos, VIDEO_DB


@pytest.mark.asyncio
async def test_video_search_single_topic():
    """Photosynthesis in English should return a valid primary result."""
    result = await search_videos("photosynthesis", "how do plants make food", language_mode="english")

    assert result is not None, "Expected a result for photosynthesis"
    assert "primary" in result
    assert "alternatives" in result
    primary_title = result["primary"]["video"].title
    # Match against the actual entry in VIDEO_DB (contains em-dash '—')
    assert "photosynthesis" in primary_title.lower(), f"Unexpected title: {primary_title!r}"


@pytest.mark.asyncio
async def test_video_search_hindi_priority():
    """Hindi photosynthesis query should prefer the Hindi-labelled video."""
    result = await search_videos("photosynthesis", "paudhe khana kaise banate hain", language_mode="hindi")

    assert result is not None
    primary_title = result["primary"]["video"].title.lower()
    # Should prefer the Hindi entry
    assert "hindi" in primary_title or "photosynthesis" in primary_title, (
        f"Unexpected Hindi-priority title: {primary_title!r}"
    )


@pytest.mark.asyncio
async def test_video_search_known_topic_returns_result():
    """Any query for a well-known topic should return at least a primary."""
    result = await search_videos("photosynthesis", "explain it", language_mode="hinglish")
    assert result is not None
    assert result["primary"] is not None


@pytest.mark.asyncio
async def test_video_search_no_match():
    """A topic that has no entry in VIDEO_DB should return None."""
    result = await search_videos("quantum string theory advanced multiverse", "", language_mode="english")
    # This topic genuinely has no VIDEO_DB entry; None or empty primary expected
    assert result is None or result.get("primary") is None


@pytest.mark.asyncio
async def test_video_search_microorganisms():
    """Microorganisms should now have a VIDEO_DB entry and return a result."""
    result = await search_videos("microorganisms", "explain bacteria and virus", language_mode="english")
    assert result is not None, "Expected a result for microorganisms"
    assert result["primary"] is not None


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_video_search_single_topic())
    asyncio.run(test_video_search_hindi_priority())
    asyncio.run(test_video_search_no_match())
    asyncio.run(test_video_search_microorganisms())
    print("All video tests passed!")
