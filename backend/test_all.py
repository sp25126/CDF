import requests
import json
import base64

def p(res):
    d = res.json()
    if 'audio_base64' in d:
        d['audio_base64'] = '<hidden>'
    print(d)
import base64

BASE_URL = "http://127.0.0.1:8000/api"

print("--- Test 1 ---")
with open("sample.pdf", "wb") as f:
    f.write(base64.b64decode("JVBERi0xLjQKMSAwIG9iaiA8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PiBlbmRvYmogMiAwIG9iaiA8PC9UeXBlL1BhZ2VzL0NvdW50IDEvS2lkc1szIDAgUl0+PiBlbmRvYmogMyAwIG9iaiA8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDU5NSA4NDJdL1BhcmVudCAyIDAgUi9SZXNvdXJjZXM8PC9Gb250PDwvRjEgNCAwIFI+Pj4+L0NvbnRlbnRzIDUgMCBSPj4gZW5kb2JqIDQgMCBvYmogPDwvVHlwZS9Gb250L1N1YnR5cGUvVHlwZTEvQmFzZUZvbnQvSGVsdmV0aWNhPj4gZW5kb2JqIDUgMCBvYmogPDwvTGVuZ3RoIDkwPj5zdHJlYW0KQlQKL0YxIDI0IFRmCjEwMCA3MDAgVGQKKEV4cGxhaW4gcGhvdG9zeW50aGVzaXMsIGl0IGlzIHRoZSBwcm9jZXNzIG9mIG1ha2luZyBmb29kIGZyb20gc3VubGlnaHQuIFRoaXMgdG9waWMgaXMgYWJvdXQgcGxhbnRzLikgVGoKRVQKZW5kc3RyZWFtIGVuZG9iaiB4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYKMDAwMDAwMDAwOSAwMDAwMCBuCjAwMDAwMDAwNTYgMDAwMDAgbgowMDAwMDAwMTExIDAwMDAwIG4KMDAwMDAwMDIxMiAwMDAwMCBuCjAwMDAwMDAyOTkgMDAwMDAgbgp0cmFpbGVyIDw8L1NpemUgNi9Sb290IDEgMCBSPj4Kc3RhcnR4cmVmCjQ0MAolJUVPRgo="))
with open("sample.pdf", "rb") as f:
    res = requests.post(f"{BASE_URL}/sources/upload", files={"file": f})
    test1_source_id = res.json()["data"]["id"]
    p(res)

print("\n--- Test 2 ---")
res = requests.post(f"{BASE_URL}/sources/add-url", json={"url": "https://example.com/"})
p(res)

print("\n--- Test 3 ---")
res = requests.get(f"{BASE_URL}/sources/list")
sources = res.json()
print(sources)

print("\n--- Test 4 ---")
res = requests.post(f"{BASE_URL}/sources/query", json={"source_id": test1_source_id, "query": "What is this topic about?"})
p(res)

res = requests.post(f"{BASE_URL}/command/text", json={"session_id": "s2", "text": "Explain photosynthesis using the uploaded source", "source_mode": True})
print("\n--- Test 5 ---")
p(res)

print("\n--- Test 6 ---")
res = requests.post(f"{BASE_URL}/command/text", json={"session_id": "s3", "text": "According to the uploaded source, explain quantum mechanics", "source_mode": True})
p(res)

print("\n--- Test 7 ---")
res = requests.post(f"{BASE_URL}/command/text", json={"session_id": "s4", "text": "Explain photosynthesis with visuals", "source_mode": False})
p(res)

print("\n--- Test 8 ---")
res = requests.post(f"{BASE_URL}/command/text", json={"session_id": "s5", "text": "Explain the water cycle with an animated video", "source_mode": False})
p(res)

print("\n--- Test 9 ---")
res = requests.post(f"{BASE_URL}/command/text", json={"session_id": "s6", "text": "Teach fractions from the source in English with a visual and video", "source_mode": True})
p(res)
