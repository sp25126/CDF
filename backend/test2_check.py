import json
import urllib.request

req = urllib.request.Request('http://127.0.0.1:8000/api/command/text', data=b'{"session_id":"t1","text":"Explain photosynthesis for class 6"}', headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())
    print(f"mode: {data.get('mode')}")
    print(f"language_mode: {data.get('language_mode')}")
    print(f"requires_clarification: {data.get('requires_clarification')}")
