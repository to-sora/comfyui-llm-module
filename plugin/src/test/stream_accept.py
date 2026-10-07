import asyncio
import json
import socket
import uuid
from pathlib import Path
import aiohttp
from .stream_client import collect, json_call
from .model_cases import TOOL


async def main():
    client = aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=socket.AF_INET, ssl=False),
                                  timeout=aiohttp.ClientTimeout(total=180))
    body = {"model": "Qwen3.5-9B", "kv_quantization": "hqq_8", "max_tokens": 128,
        "messages": [{"role": "user", "content": "Explain how clouds form in four sentences."}]}
    async with client:
        stream = await collect(client, body)
        plain = await json_call(client, "/v1/chat/completions", body)
        assert stream["content"] == plain["choices"][0]["message"]["content"], stream
        assert stream["chunks"] > 3 and stream["seconds"]-stream["first_content"] > .05, stream
        assert "<think>" not in stream["content"]
        tools = await collect(client, {**body, "tools": [TOOL], "tool_choice": "required",
            "messages": [{"role": "system", "content": "Use the available weather tool."},
                         {"role": "user", "content": "What is the weather in Hong Kong?"}]})
        assert len(tools["tool_calls"]) == 1, tools
        call = tools["tool_calls"][0]["function"]
        assert call["name"] == "get_weather" and json.loads(call["arguments"])["city"] == "Hong Kong", call
        ident = str(uuid.uuid4())
        await collect(client, {**body, "comfy_prompt_id": ident, "max_tokens": 2048,
            "messages": [{"role": "user", "content": "Write a detailed 1000-word story about a lighthouse keeper."}]}, disconnect=True)
        for _ in range(80):
            q = await json_call(client, "/queue")
            history = await json_call(client, "/history/" + ident)
            if not history and not any(row[1] == ident for row in q["queue_running"]+q["queue_pending"]):
                break
            await asyncio.sleep(.25)
        else:
            raise AssertionError("Disconnected stream left an orphaned prompt")
        recovered = await collect(client, {**body, "messages": [{"role": "user", "content": "What is 6 times 7? Reply with only the number."}]})
        assert recovered["content"].strip() == "42", recovered
    result = {"status": "PASS", "text": stream, "tool": call, "disconnect_cancelled": True,
              "queue_recovered": True}
    path = Path(__file__).resolve().parents[3] / "fan-out/studio-engine/stream.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
