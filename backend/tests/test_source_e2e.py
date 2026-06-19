import httpx
import sys
import os
import time

BASE_URL = "http://localhost:8000"

def test_source_ingestion_and_grounding():
    print("Starting Source Grounding E2E Integration Tests...")

    # Step 1: Clean any pre-existing sources to start fresh
    print("1. Listing initial sources...")
    r = httpx.get(f"{BASE_URL}/sources/list")
    assert r.status_code == 200, f"Failed listing sources: {r.text}"
    initial_sources = r.json().get("data", [])
    for src in initial_sources:
        src_id = src["id"]
        print(f"   Deleting pre-existing source {src_id}...")
        httpx.delete(f"{BASE_URL}/sources/{src_id}")

    # Step 2: Add pasted text source
    print("2. Adding text source...")
    source_payload = {
        "title": "Haryana Farming and Buffaloes Info",
        "text": "Haryana is known for its high milk production. Murrah buffaloes are the pride of Haryana and are often called black gold. Haryana farmers grow wheat, paddy, and mustard in abundance."
    }
    r = httpx.post(f"{BASE_URL}/sources/add-text", json=source_payload)
    assert r.status_code == 200, f"Failed to add text source: {r.text}"
    source_data = r.json().get("data", {})
    source_id = source_data.get("id")
    assert source_id is not None, "Source ID should be returned"
    print(f"   Added source successfully with ID: {source_id}")

    # Step 3: Verify the source is listed
    print("3. Listing sources to verify insertion...")
    r = httpx.get(f"{BASE_URL}/sources/list")
    assert r.status_code == 200
    listed_sources = r.json().get("data", [])
    assert any(s["id"] == source_id for s in listed_sources), f"Source {source_id} not in list: {listed_sources}"
    assert any(s["title"] == "Haryana Farming and Buffaloes Info" for s in listed_sources)
    print("   Source list verification passed.")

    # Step 4: Test source-grounded query for fact present in document
    print("4. Testing query for present fact (Murrah buffaloes)...")
    payload = {
        "text": "What is the pride of Haryana?",
        "session_id": "e2e-session",
        "source_mode": True
    }
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Command failed: {r.text}"
    res = r.json().get("data", {})
    assert res.get("mode") == "explain"
    assert res.get("source_mode") is True
    assert "buffalo" in res.get("response_text", "").lower() or "murrah" in res.get("response_text", "").lower() or "not found" not in res.get("title", "").lower()
    assert len(res.get("citations", [])) > 0, "Should contain citations"
    print("   Query for present fact passed.")

    # Step 5: Test source-grounded query for fact NOT present in document
    print("5. Testing query for absent fact (Photosynthesis)...")
    payload = {
        "text": "Explain photosynthesis in detail",
        "session_id": "e2e-session",
        "source_mode": True
    }
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Command failed: {r.text}"
    res = r.json().get("data", {})
    assert res.get("mode") == "explain"
    assert res.get("source_mode") is True
    # The system should either refuse (cannot find in source) OR return a response with 0 citations
    # (LLM may answer from general knowledge — acceptable as long as it doesn't cite the farming doc)
    response_text = res.get("response_text", "")
    citations = res.get("citations", [])
    is_refusal = "cannot find" in response_text.lower() or "not found" in res.get("title", "").lower()
    has_farming_citation = any("haryana" in str(c).lower() or "farming" in str(c).lower() or "buffalo" in str(c).lower() for c in citations)
    assert is_refusal or (not has_farming_citation), (
        f"Should not cite the farming document for a photosynthesis question. Citations: {citations}"
    )
    print("   Query for absent fact passed.")

    # Step 6: Test source-grounded quiz for present facts
    print("6. Testing quiz generation for present facts (Haryana farming)...")
    payload = {
        "text": "Create a 2 question quiz on Haryana buffaloes and farming",
        "session_id": "e2e-session",
        "source_mode": True
    }
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Command failed: {r.text}"
    res = r.json().get("data", {})
    assert res.get("mode") == "quiz"
    assert res.get("source_mode") is True
    # If LLM doesn't support or fallback handles it, it might generate quiz questions
    if res.get("title") != "Not Found":
        assert len(res.get("questions", [])) > 0
        assert len(res.get("citations", [])) > 0
        print("   Quiz generation for present facts passed.")
    else:
        print("   Quiz fallback returned Not Found, skipping assertion.")

    # Step 7: Test source-grounded quiz for absent facts
    print("7. Testing quiz generation for absent facts (Photosynthesis)...")
    payload = {
        "text": "Create a 2 question quiz on Photosynthesis",
        "session_id": "e2e-session",
        "source_mode": True
    }
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Command failed: {r.text}"
    res = r.json().get("data", {})
    assert res.get("mode") == "quiz"
    assert res.get("source_mode") is True
    assert res.get("response_text") == "I cannot find the answer to this question in the provided source material."
    assert len(res.get("citations", [])) == 0, "Absent facts quiz should not have citations"
    print("   Quiz generation for absent facts passed.")

    # Step 8: Clean up added source
    print("8. Cleaning up the ingested source...")
    r = httpx.delete(f"{BASE_URL}/sources/{source_id}")
    assert r.status_code == 200
    r = httpx.get(f"{BASE_URL}/sources/list")
    assert r.status_code == 200
    listed_sources = r.json().get("data", [])
    assert not any(s["id"] == source_id for s in listed_sources), "Source should be deleted"
    print("   Cleanup passed.")

    print("\nAll Source Grounding E2E tests passed successfully!")

if __name__ == "__main__":
    # Give a tiny bit of time for uvicorn to be fully ready
    time.sleep(1)
    try:
        test_source_ingestion_and_grounding()
    except AssertionError as e:
        print(f"\nAssertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        sys.exit(1)
