"""
Memory service tests — uses unique session/user IDs to avoid cross-test state bleed.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.session_memory import session_memory_service
from app.services.user_memory import user_memory_service
from app.services.memory_retriever import memory_retriever
from app.services.memory_writer import memory_writer


def test_session_persistence():
    print("Testing Session Persistence...")
    # Use a unique session ID so previous test runs don't pollute state
    session_id = "test-mem-fresh-001"
    # Clear any pre-existing state using the service's public API
    session_memory_service.clear_session(session_id)

    session_memory_service.add_turn(session_id, "user", "Hello assistant")
    session_memory_service.add_turn(session_id, "assistant", "Hello student")

    mem = session_memory_service.get_session(session_id)
    assert len(mem.recent_turns) == 2, f"Expected 2 turns, got {len(mem.recent_turns)}"
    assert mem.recent_turns[0]["content"] == "Hello assistant"
    print("Pass: Session persistence works")


def test_preference_learning():
    print("\nTesting Preference Learning...")
    user_id = "test-mem-user-001"
    text = "always use english"
    memory_writer.process_turn_for_long_term_memory(user_id, text)

    user = user_memory_service.get_user(user_id)
    assert user.preferred_language == "english"
    print("Pass: Language preference learned")


def test_correction_recording():
    print("\nTesting Correction Recording...")
    user_id = "test-mem-user-002"
    text = "That is wrong, photosynthesis uses water not oil."
    memory_writer.process_turn_for_long_term_memory(user_id, text)

    user = user_memory_service.get_user(user_id)
    assert len(user.corrections) > 0
    assert "wrong" in user.corrections[-1]["text"]
    print("Pass: Correction recorded")


def test_retrieval_relevance():
    print("\nTesting Retrieval Context...")
    session_id = "test-mem-fresh-002"
    user_id = "test-mem-user-001"  # same user as preference test above
    ctx = memory_retriever.retrieve_memory_context(session_id, user_id, "query")

    assert "session_summary" in ctx
    assert "user_preferences" in ctx
    assert ctx["user_preferences"]["preferred_language"] == "english"
    print("Pass: Memory retrieval context correct")


if __name__ == "__main__":
    try:
        test_session_persistence()
        test_preference_learning()
        test_correction_recording()
        test_retrieval_relevance()
        print("\nALL MEMORY TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        import sys as _sys
        _sys.exit(1)
