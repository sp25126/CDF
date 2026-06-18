import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_source_grounded():
    print("Testing Source-grounded Explain...")
    payload = {
        "session_id": "p5",
        "text": "Explain this topic from the uploaded source",
        "source_mode": True
    }
    res = requests.post(f"{BASE_URL}/api/command/text", json=payload)
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    test_source_grounded()
