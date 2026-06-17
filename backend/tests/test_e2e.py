import httpx
import sys
import os

BASE_URL = "http://localhost:8000"

def test_explain_default():
    print("Testing Explain (Default: Written English, Spoken Hinglish)...")
    payload = {"text": "Explain gravity", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "explain"
    assert data["language_mode"] == "default"
    assert "bullets" in data
    assert "example" in data
    assert "response_text" in data
    
    # Spoken audio (response_text) should be Hinglish
    resp_text = data["response_text"].lower()
    assert any(word in resp_text for word in ["bachon", "aaj", "baare", "samajhne", "taqat", "dangal", "pehalwan", "zameen", "girega", "gurutva", "khinchti", "gravity", "ek", "hai", "ko"])
    
    # Title and example should be English (no Devanagari characters)
    assert len(data["example"]) > 3
    assert not any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in data["example"])
    print("=> Explain (Default) Passed!")

def test_explain_hinglish():
    print("Testing Explain (Explicit Hinglish)...")
    payload = {"text": "Explain gravity in Hinglish", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "explain"
    assert data["language_mode"] == "hinglish"
    print("=> Explain (Explicit Hinglish) Passed!")

def test_explain_hindi():
    print("Testing Explain (Hindi)...")
    payload = {"text": "Explain gravity in Hindi", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "explain"
    assert data["language_mode"] == "hindi"
    print("=> Explain (Hindi) Passed!")

def test_explain_english():
    print("Testing Explain (English)...")
    payload = {"text": "Explain gravity in English", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "explain"
    assert data["language_mode"] == "english"
    print("=> Explain (English) Passed!")

def test_quiz_default():
    print("Testing Quiz (Default: Written English, Spoken Hinglish)...")
    payload = {"text": "Create a 3 question quiz on fractions", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "quiz"
    assert data["language_mode"] == "default"
    assert "questions" in data
    assert len(data["questions"]) == 3
    print("=> Quiz (Default) Passed!")

def test_quiz_hinglish():
    print("Testing Quiz (Explicit Hinglish)...")
    payload = {"text": "Create a 3 question quiz on fractions in Hinglish", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "quiz"
    assert data["language_mode"] == "hinglish"
    print("=> Quiz (Explicit Hinglish) Passed!")

def test_quiz_hindi():
    print("Testing Quiz (Hindi)...")
    payload = {"text": "Create a 3 question quiz on fractions in Hindi", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "quiz"
    assert data["language_mode"] == "hindi"
    print("=> Quiz (Hindi) Passed!")

def test_quiz_english():
    print("Testing Quiz (English)...")
    payload = {"text": "Create a 3 question quiz on fractions in English", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "quiz"
    assert data["language_mode"] == "english"
    print("=> Quiz (English) Passed!")

def test_clarify():
    print("Testing Clarify...")
    payload = {"text": "asdfgh", "session_id": "test-session"}
    r = httpx.post(f"{BASE_URL}/command/text", json=payload, timeout=20.0)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res = r.json()
    assert res["status"] == "success"
    data = res["data"]
    assert data["mode"] == "clarify"
    assert data["language_mode"] == "default"
    assert "message" in data
    assert "suggestions" in data
    print("=> Clarify Passed!")

if __name__ == "__main__":
    try:
        test_explain_default()
        test_explain_hinglish()
        test_explain_hindi()
        test_explain_english()
        test_quiz_default()
        test_quiz_hinglish()
        test_quiz_hindi()
        test_quiz_english()
        test_clarify()
        print("\nAll integration tests passed successfully!")
    except AssertionError as e:
        import traceback
        traceback.print_exc()
        print(f"\nAssertion error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
