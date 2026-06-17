import unittest
import sys
import os

# Adjust path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.source_service import source_service

class TestSourceRetrieval(unittest.TestCase):
    def setUp(self):
        # Reset source database for testing
        source_service.sources = {}
        source_service.chunks = []

    def test_chunking_and_overlap(self):
        text = "This is a long piece of text that we want to chunk. " * 30
        chunks = source_service.chunk_text(text, "test-source-id", "test-title")
        
        self.assertTrue(len(chunks) > 1, "Should split text into multiple chunks")
        for c in chunks:
            self.assertEqual(c["source_id"], "test-source-id")
            self.assertEqual(c["source_title"], "test-title")
            self.assertTrue(len(c["text"]) >= 50, "Chunks should be reasonably sized")
            self.assertTrue(len(c["text"]) <= 850, "Chunks should satisfy max size limit")

    def test_section_label_matching(self):
        text = ("Chapter 1: Intro to variables. " + "x" * 600 + "\n") + \
               ("Section 3: Functions and loops. " + "y" * 600 + "\n") + \
               ("Section 4: Arrays. " + "z" * 600)
        
        chunks = source_service.chunk_text(text, "sec-id", "sec-title")
        found_section_3 = False
        for c in chunks:
            if "Section 3" in (c["section_label"] or ""):
                found_section_3 = True
                
        # The regex match for 'Section 3' inside chunks should find it
        self.assertTrue(found_section_3, "Should extract Section 3 label from text chunks")

    def test_deterministic_retrieval(self):
        # Ingest a document with 5 different sections
        sec1 = "Section 1: Photosynthesis is how plants cook food. They use sunlight, water, and chlorophyll. Leaves act as the kitchen."
        sec2 = "Section 2: Gravity is the invisible pull of the Earth. Newton saw an apple fall and discovered gravity."
        sec3 = "Section 3: Fractions represent parts of a whole. Half is 1/2, quarter is 1/4. Denominators are the bottom numbers."
        sec4 = "Section 4: Food chains represent energy transfer. Plants are producers, grasshoppers are primary consumers."
        sec5 = "Section 5: Wrestling is a popular sport in Haryana villages. Matches are held in clay arenas called Akhadas."

        source_service.add_text_source("Section 1 Docs", sec1)
        source_service.add_text_source("Section 2 Docs", sec2)
        source_service.add_text_source("Section 3 Docs", sec3)
        source_service.add_text_source("Section 4 Docs", sec4)
        source_service.add_text_source("Section 5 Docs", sec5)

        # Retrieve for fractions question (should hit Section 3)
        results = source_service.retrieve_chunks("What is a denominator in fractions?", limit=1)
        self.assertEqual(len(results), 1)
        self.assertIn("Fractions", results[0]["text"])
        self.assertIn("Section 3 Docs", results[0]["source_title"])

        # Retrieve for wrestling question (should hit Section 5)
        results_wrestling = source_service.retrieve_chunks("Where do Haryanvi wrestlers fight?", limit=1)
        self.assertEqual(len(results_wrestling), 1)
        self.assertIn("Wrestling", results_wrestling[0]["text"])
        self.assertIn("Akhadas", results_wrestling[0]["text"])

if __name__ == "__main__":
    unittest.main()
