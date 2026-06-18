import pytest
import asyncio
from app.services.video_search import search_videos

@pytest.mark.asyncio
async def test_video_search_single_topic():
    """Test searching for a single known topic returns best_video and alternatives."""
    result = await search_videos("photosynthesis", "how do plants make food", language_mode="english")
    
    assert result is not None
    assert "primary" in result
    assert "alternatives" in result
    assert result["primary"]["video"].title == "Photosynthesis - The Dr. Binocs Show"
    
@pytest.mark.asyncio
async def test_video_search_hindi_priority():
    """Test searching with language_mode=hindi priorities hindi videos."""
    result = await search_videos("photosynthesis", "paudhe khana kaise banate hain", language_mode="hindi")
    
    assert result is not None
    assert result["primary"]["video"].title == "Photosynthesis in Hindi"
    
@pytest.mark.asyncio
async def test_video_search_no_match():
    """Test searching for an unknown topic returns None."""
    result = await search_videos("quantum string theory", "explain strings", language_mode="english")
    assert result is None
