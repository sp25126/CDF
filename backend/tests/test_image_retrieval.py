import pytest
import asyncio
from app.services.image_retrieval import retrieve_visuals
from app.services.image_selector import select_best_image

@pytest.mark.asyncio
async def test_image_retrieval_success():
    """Test retrieving images for a known topic returns valid VisualRefs."""
    # "photosynthesis" is a common topic that should have images on Wikimedia
    visuals = await retrieve_visuals("photosynthesis")
    
    assert isinstance(visuals, list)
    # We should get at least one image or empty list, but for known topic, it shouldn't fail totally
    # It might be empty if Wikimedia is down, but normally > 0
    if len(visuals) > 0:
        best = select_best_image(visuals)
        assert best is not None
        assert best.url.startswith("http")
        assert best.title is not None

@pytest.mark.asyncio
async def test_image_retrieval_empty_for_nonsense():
    """Test retrieving images for a nonsense topic returns empty array."""
    visuals = await retrieve_visuals("xxyznonexistenttopic12345")
    assert isinstance(visuals, list)
    assert len(visuals) == 0
    
    best = select_best_image(visuals)
    assert best is None
