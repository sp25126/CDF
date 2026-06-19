"""
Tests for source ingestion and retrieval — updated to use source_ingest_service.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.source_ingest import source_ingest_service
from app.services.retrieval import retrieve_relevant_chunks


class TestSourceRetrieval(unittest.TestCase):
    def setUp(self):
        # Reset in-memory state before each test
        source_ingest_service.sources = {}
        source_ingest_service.chunks = []

    def test_add_text_source_creates_chunks(self):
        """Adding a text source should create at least one chunk."""
        text = "Photosynthesis is how plants make food. " * 20
        source_ingest_service.add_text_source("Photosynthesis Doc", text)
        self.assertGreater(len(source_ingest_service.chunks), 0)

    def test_chunks_have_required_fields(self):
        """Each chunk must carry source_title, text, page_number, section_label."""
        source_ingest_service.add_text_source("Test Doc", "Gravity pulls objects down. " * 30)
        for chunk in source_ingest_service.chunks:
            self.assertIn("source_title", chunk)
            self.assertIn("text", chunk)
            self.assertIn("page_number", chunk)
            self.assertIn("section_label", chunk)

    def test_list_sources_returns_added_source(self):
        """list_sources() should return metadata for every added source."""
        source_ingest_service.add_text_source("My Test Source", "Some content " * 10)
        sources = source_ingest_service.list_sources()
        titles = [s["title"] for s in sources]
        self.assertIn("My Test Source", titles)

    def test_deterministic_retrieval_fractions(self):
        """Retrieval should return the fraction chunk for a fractions query."""
        source_ingest_service.add_text_source(
            "Fractions Doc",
            "Fractions represent parts of a whole. Half is 1/2, quarter is 1/4. "
            "Denominators are the bottom numbers. Numerators are the top. " * 5,
        )
        source_ingest_service.add_text_source(
            "Wrestling Doc",
            "Wrestling is a popular sport in Haryana villages. "
            "Matches are held in clay arenas called Akhadas. " * 5,
        )

        results = retrieve_relevant_chunks("What is a denominator in fractions?", limit=1)
        self.assertEqual(len(results), 1)
        self.assertIn("Fractions", results[0].source_title)

    def test_deterministic_retrieval_wrestling(self):
        """Retrieval should return the wrestling chunk for a wrestling query."""
        source_ingest_service.add_text_source(
            "Fractions Doc",
            "Fractions represent parts of a whole. " * 5,
        )
        source_ingest_service.add_text_source(
            "Wrestling Doc",
            "Wrestling is a popular sport in Haryana. Akhadas are clay arenas. " * 5,
        )

        results = retrieve_relevant_chunks("Where do Haryanvi wrestlers fight?", limit=1)
        self.assertEqual(len(results), 1)
        self.assertIn("Wrestling", results[0].source_title)

    def test_retrieve_returns_empty_when_no_sources(self):
        """Retrieval on empty DB returns empty list."""
        results = retrieve_relevant_chunks("anything", limit=3)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
