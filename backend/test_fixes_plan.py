import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_voice_gating():
    print("--- Testing Voice Gating ---")
    
    # 1. Filler speech (should be rejected/unclear in hands-free)
    # To simulate hands-free noise, we need the session to be in hands-free mode
    requests.post(f"{BASE_URL}/api/command/text", json={"session_id": "test-hf", "text": "hands_free_start"})
    
    res = requests.post(f"{BASE_URL}/api/command/text", json={"session_id": "test-hf", "text": "maafi chahta hu"})
    data = res.json()["data"]
    if data["requires_clarification"]:
        print("PASS: 'maafi chahta hu' was correctly filtered as unclear.")
    else:
        print("FAIL: 'maafi chahta hu' was not filtered.", data)

    # 2. Valid command
    res = requests.post(f"{BASE_URL}/api/command/text", json={"session_id": "test-hf", "text": "stop"})
    data = res.json()["data"]
    if data["mode"] == "stop":
        print("PASS: 'stop' command routed correctly.")
    else:
        print("FAIL: 'stop' command not routed.", data)

def test_answers_and_animation():
    print("\n--- Testing Answers and Animation ---")
    
    # Explain mode
    res = requests.post(f"{BASE_URL}/api/command/text", json={"session_id": "test-ans", "text": "Explain gravity"})
    data = res.json()["data"]
    
    if data["avatar_state"] == "speaking":
        print("PASS: Avatar state is 'speaking' during explain.")
    else:
        print("FAIL: Avatar state is not 'speaking'.")
        
    text = data.get("answer_text", "")
    if len(text) > 100 and ("*" in text or "-" in text or "\n" in text):
        print("PASS: Answer contains detailed formatting/bullets.")
    else:
        print("WARNING: Answer may not have bullets or sufficient detail.")

    # Quiz mode
    res = requests.post(f"{BASE_URL}/api/command/text", json={"session_id": "test-ans2", "text": "Start a quiz on gravity"})
    data = res.json()["data"]
    
    if data["avatar_state"] == "speaking":
        print("PASS: Avatar state is 'speaking' during quiz.")
    else:
        print("FAIL: Avatar state is not 'speaking' during quiz.")

def test_media_attachment():
    print("\n--- Testing Media Attachments ---")
    
    # Visuals
    res = requests.post(f"{BASE_URL}/api/command/text", json={"session_id": "test-media", "text": "Explain photosynthesis"})
    data = res.json()["data"]
    if data.get("visuals") and len(data["visuals"]) > 0:
        print("PASS: Visual cards attached for photosynthesis.")
    else:
        print("FAIL: No visual cards attached.")

    # Videos
    res = requests.post(f"{BASE_URL}/api/command/text", json={"session_id": "test-media2", "text": "Explain water cycle with an animated lesson"})
    data = res.json()["data"]
    if data.get("videos") and len(data["videos"]) > 0:
        print("PASS: YouTube learning video attached.")
    else:
        print("FAIL: No video attached.")

if __name__ == "__main__":
    test_voice_gating()
    test_answers_and_animation()
    test_media_attachment()
