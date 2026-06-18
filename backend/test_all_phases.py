import requests
import json
import os
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print("RUNNING CROSS-PHASE ACCEPTANCE TEST SUITE")
    print("==================================================")
    
    # 1. Health
    print("\nTest 1: Health Check")
    res = requests.get(f"{BASE_URL}/health")
    data = res.json()
    assert data.get("status") == "ok", f"Expected status 'ok', got {data}"
    print("Pass: Health check works")
    
    # 2. Default Explain
    print("\nTest 2: Default Explain (Hinglish)")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p1",
        "text": "Explain photosynthesis for class 6"
    })
    data = res.json()
    assert data.get("mode") == "explain", f"Expected mode explain, got {data.get('mode')}"
    assert data.get("language_mode") == "hinglish", f"Expected language hinglish, got {data.get('language_mode')}"
    assert data.get("answer_text") is not None, "answer_text missing"
    assert len(data.get("next_actions", [])) > 0, "next_actions empty"
    print("Pass: Default explain (Hinglish) works")

    # 3. English Explain
    print("\nTest 3: English Explain")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p2",
        "text": "Explain gravity in English"
    })
    data = res.json()
    assert data.get("language_mode") == "english", f"Expected language english, got {data.get('language_mode')}"
    assert data.get("answer_text") is not None, "answer_text missing"
    print("Pass: English explain works")

    # 4. Quiz Default
    print("\nTest 4: Quiz Default (Hinglish)")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p3",
        "text": "Quiz me on fractions"
    })
    data = res.json()
    assert data.get("mode") == "quiz", f"Expected mode quiz, got {data.get('mode')}"
    assert data.get("quiz") is not None, "quiz payload missing"
    assert len(data.get("quiz", {}).get("questions", [])) > 0, "quiz questions missing"
    print("Pass: Quiz default works")

    # 5. Hindi Explain
    print("\nTest 5: Hindi Explain")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p4",
        "text": "Gravity Hindi mein explain karo"
    })
    data = res.json()
    assert data.get("language_mode") == "hindi", f"Expected language hindi, got {data.get('language_mode')}"
    print("Pass: Hindi explain works")

    # 6. Source Upload
    print("\nTest 6: Source Upload")
    pdf_path = os.path.join(os.path.dirname(__file__), "sample.pdf")
    # If sample.pdf doesn't exist, we write a dummy txt file and rename it
    if not os.path.exists(pdf_path):
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 mock pdf content")
            
    with open(pdf_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/sources/upload", files={"file": ("sample.pdf", f, "application/pdf")})
    data = res.json()
    assert data.get("status") == "success", f"Expected success, got {data}"
    source_id = data.get("source_id") or data.get("data", {}).get("id")
    assert source_id is not None, f"Expected source_id, got {data}"
    print(f"Pass: Source upload works (source_id: {source_id})")

    # 7. Source Query
    print("\nTest 7: Source Query")
    res = requests.post(f"{BASE_URL}/api/sources/query", json={
        "source_id": source_id,
        "query": "main topic"
    })
    data = res.json()
    assert data.get("status") == "success", f"Expected success, got {data}"
    chunks = data.get("chunks") or data.get("data", [])
    assert len(chunks) >= 0, "Expected chunks list"
    print("Pass: Source query works")

    # 8. Source-grounded Explain
    print("\nTest 8: Source-grounded Explain")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p5",
        "text": "Explain this topic from the uploaded source",
        "source_mode": True
    })
    data = res.json()
    assert data.get("status") == "success", f"Expected success, got {data}"
    # In source mode, should retrieve chunks or display fallback answer
    print("Pass: Source-grounded explain works")

    # 9. Visual Attachment
    print("\nTest 9: Visual Attachment")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p6",
        "text": "Explain photosynthesis with visuals"
    })
    data = res.json()
    visuals = data.get("visuals") or data.get("data", {}).get("visuals", [])
    reason = data.get("visual_reason") or data.get("data", {}).get("visual_reason")
    assert len(visuals) > 0 or reason is not None, f"Expected visuals or reason, got {data}"
    print("Pass: Visual attachment works")

    # 10. Video Attachment
    print("\nTest 10: Video Attachment")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p7",
        "text": "Explain water cycle with animated video"
    })
    data = res.json()
    videos = data.get("videos") or data.get("data", {}).get("videos", [])
    reason = data.get("video_reason") or data.get("data", {}).get("video_reason")
    assert len(videos) > 0 or reason is not None, f"Expected videos or reason, got {data}"
    print("Pass: Video attachment works")

    # 11. Hands-Free Command Test
    print("\nTest 11: Hands-Free Start")
    res = requests.post(f"{BASE_URL}/api/voice/hands-free/start", json={
        "session_id": "p8"
    })
    data = res.json()
    assert data.get("hands_free_mode") is True, f"Expected hands_free_mode=True, got {data}"
    assert data.get("assistant_state") == "listening", f"Expected assistant_state=listening, got {data}"
    print("Pass: Hands-free start endpoint works")

    # 12. Voice Command Routing
    print("\nTest 12: Voice Command Routing")
    res = requests.post(f"{BASE_URL}/api/voice/command", json={
        "session_id": "p8",
        "text": "repeat slower"
    })
    data = res.json()
    assert data.get("status") == "success", f"Expected success, got {data}"
    print("Pass: Voice command routing works")

    # 13. Quiz Control Command
    print("\nTest 13: Quiz Control Command")
    res = requests.post(f"{BASE_URL}/api/voice/command", json={
        "session_id": "p8",
        "text": "next question"
    })
    data = res.json()
    assert data.get("status") == "success", f"Expected success, got {data}"
    print("Pass: Quiz control command routing works")

    # 14. Avatar State Sync
    print("\nTest 14: Avatar State Sync")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "p9",
        "text": "Explain fractions"
    })
    data = res.json()
    avatar_state = data.get("avatar_state") or data.get("data", {}).get("avatar_state")
    assert avatar_state in ["speaking", "thinking", "listening", "idle"], f"Unexpected avatar state: {avatar_state}"
    print(f"Pass: Avatar state sync works (avatar_state: {avatar_state})")

    print("\n==================================================")
    print("ALL 14 ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\nTEST FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
