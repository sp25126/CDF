import httpx, asyncio, json
async def test():
    r = await httpx.AsyncClient(timeout=120.0).post('http://127.0.0.1:8000/command/text', json={'text':'explain photon','session_id':'test-session'})
    print('Status:', r.status_code)
    print(json.dumps(r.json(), indent=2))
asyncio.run(test())
