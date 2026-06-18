import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.prompt_assembler import prompt_assembler
from app.schemas.chunk import Chunk

def test_prompt_construction():
    print("Testing Prompt Assembly...")
    memory_context = {
        "session_summary": "Student: Explain gravity\nAssistant: Gravity pulls objects down.",
        "user_preferences": {
            "preferred_language": "hinglish",
            "preferred_class_level": "Grade 6",
            "recurring_topics": ["physics"],
            "correction_history": ["You spoke too fast earlier."]
        },
        "assistant_state": "idle",
        "current_mode": "explain",
        "current_language_mode": "hinglish",
        "hands_free": False
    }

    chunks = [
        Chunk(chunk_id="1", source_id="src1", source_title="Doc1", text="Gravity is a fundamental interaction...", page_number=1, section_label=None)
    ]

    prompt = prompt_assembler.assemble_prompt(
        query="What is gravity?",
        memory_context=memory_context,
        source_chunks=chunks,
        source_mode=True
    )

    # Basic assertions
    assert "MEMORY CONTEXT" in prompt
    assert "SOURCE MATERIAL" in prompt
    assert "Gravity is a fundamental interaction" in prompt
    assert "Student Question: What is gravity?" in prompt
    
    # Assert brevity (approx check)
    assert len(prompt) < 3000

    print("Pass: Prompt assembled correctly with memory and sources.")
    # print(prompt) # Uncomment to see full prompt

if __name__ == "__main__":
    try:
        test_prompt_construction()
        print("\nALL PROMPT ASSEMBLY TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
