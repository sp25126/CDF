import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_source_grounded_success():
    print("Uploading text source...")
    payload = {
        "title": "Photosynthesis Lesson",
        "text": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water. In plants, photosynthesis generally involves the green pigment chlorophyll and generates oxygen as a byproduct."
    }
    res = requests.post(f"{BASE_URL}/api/sources/add-text", json=payload)
    source_id = res.json().get("source_id")
    print(f"Uploaded source_id: {source_id}")

    print("Asking grounded question...")
    payload = {
        "session_id": "p-success",
        "text": "What is photosynthesis according to the source?",
        "source_mode": True
    }
    res = requests.post(f"{BASE_URL}/api/command/text", json=payload)
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    test_source_grounded_success()
