import json
import urllib.request

req = urllib.request.Request('http://127.0.0.1:8000/api/command/text', data=b'{"session_id":"t1","text":"Explain photosynthesis for class 6"}', headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    print(json.dumps(json.loads(response.read()), indent=2))
