import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_hands_free_flow():
    print("Test 1: Start Hands Free Mode")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "test-hf-1",
        "text": "hands_free_start",
        "context": {}
    })
    data = res.json().get("data", {})
    assert data.get("hands_free_mode") is True
    print("Pass: Hands free started\n")
    
    print("Test 2: Ask explanation in Hands Free Mode")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "test-hf-1",
        "text": "Explain gravity",
        "context": {}
    })
    data = res.json().get("data", {})
    # Should get a follow-up prompt
    assert data.get("follow_up_prompt") is not None
    assert data.get("assistant_state") == "awaiting_followup"
    print("Pass: Follow-up generated\n")
    
    print("Test 3: Interactive Voice Command Router (Next Question/Quiz)")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "test-hf-1",
        "text": "ask one question",
        "context": {}
    })
    data = res.json().get("data", {})
    assert data.get("assistant_state") == "quizzing"
    print("Pass: Voice command router properly mapped to quiz\n")

    print("Test 4: Stop Hands Free Mode")
    res = requests.post(f"{BASE_URL}/api/command/text", json={
        "session_id": "test-hf-1",
        "text": "stop hands free",
        "context": {}
    })
    data = res.json().get("data", {})
    assert data.get("hands_free_mode") is False
    print("Pass: Hands free stopped\n")
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    try:
        test_hands_free_flow()
    except AssertionError as e:
        print("TEST FAILED:", e)
    except Exception as e:
        print("ERROR:", e)
