import asyncio
import json
import socket
import uuid
from pathlib import Path
import aiohttp
from .stream_client import json_call


async def main():
    root = Path(__file__).resolve().parents[3]
    config = root / "plugin/config/config.yaml"
    saved = config.read_text()
    connector = aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as client:
        url = "https://127.0.0.1:8188/v1/chat/completions"
        async with client.post(url, data="{", headers={"Content-Type": "application/json"}) as r:
            invalid = await r.json()
            assert r.status == 400 and invalid["error"]["message"], invalid
        body = {"model": "Qwen3.5-9B", "max_tokens": 32, "kv_quantization": "hqq_8",
                "messages": [{"role": "user", "content": "What is 6 times 7? Reply with only the number."}]}
        await json_call(client, "/v1/chat/completions", body)
        ident = str(uuid.uuid4())
        try:
            config.write_text(saved.replace("request_timeout: 900", "request_timeout: 1"))
            async with client.post(url, json={**body, "comfy_prompt_id": ident, "max_tokens": 2048,
                    "messages": [{"role": "user", "content": "Write a detailed 1000-word story about a lighthouse keeper."}]}) as r:
                timeout = await r.json()
                assert r.status == 500 and "exceeded 1s" in timeout["error"]["message"], timeout
        finally:
            config.write_text(saved)
        for _ in range(80):
            queue = await json_call(client, "/queue")
            history = await json_call(client, "/history/"+ident)
            if not history and not any(v[1] == ident for v in queue["queue_running"]+queue["queue_pending"]):
                break
            await asyncio.sleep(.25)
        else:
            raise AssertionError("Timeout left a ComfyUI prompt behind")
        reply = await json_call(client, "/v1/chat/completions", body)
        assert reply["choices"][0]["message"]["content"].strip() == "42"
        logs = (root / "plugin/data/service.log").read_text()
        assert "Traceback" in logs and "exceeded 1s" in logs
    result = {"status": "PASS", "invalid_json": invalid, "timeout": timeout,
              "native_prompt_removed": True, "traceback_recorded": True, "next_reply": "42"}
    (root / "fan-out/studio-engine/faults.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
