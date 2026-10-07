import json
import time

BASE = "https://127.0.0.1:8188"


async def collect(client, body, disconnect=False):
    start = time.monotonic()
    parts, calls, stamps = [], [], []
    finish = None
    async with client.post(BASE + "/v1/chat/completions", json={**body, "stream": True}) as response:
        assert response.status == 200, await response.text()
        assert response.headers["Content-Type"].startswith("text/event-stream")
        async for line in response.content:
            if not line.startswith(b"data: "):
                continue
            raw = line[6:].strip()
            if raw == b"[DONE]":
                break
            item = json.loads(raw)
            assert "error" not in item, item
            for choice in item["choices"]:
                delta = choice["delta"]
                if delta.get("content"):
                    parts.append(delta["content"])
                    stamps.append(time.monotonic() - start)
                    if disconnect:
                        response.close()
                        return {"first_content": stamps[0]}
                calls.extend(delta.get("tool_calls", []))
                if choice.get("finish_reason"):
                    finish = choice["finish_reason"]
        return {"content": "".join(parts), "chunks": len(parts), "tool_calls": calls,
                "first_content": stamps[0] if stamps else None, "seconds": time.monotonic()-start,
                "finish_reason": finish}


async def json_call(client, path, body=None):
    async with client.request("POST" if body else "GET", BASE + path, json=body) as response:
        assert response.status == 200, await response.text()
        return await response.json()
