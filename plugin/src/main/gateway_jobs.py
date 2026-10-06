import asyncio
import json
import socket
import time
import aiohttp
from .gateway_graph import graph
from .network import hosts, port_config
from .settings import read


async def execute(body):
    config = port_config()
    host = "127.0.0.1" if config["policy"] == "public" else hosts(config).split(",")[0]
    base = f"https://{host}:{config['port']}"
    timeout = read("config.yaml")["request_timeout"]
    connector = aiohttp.TCPConnector(family=socket.AF_INET, ssl=False)
    async with aiohttp.ClientSession(connector=connector,
                                     timeout=aiohttp.ClientTimeout(total=timeout)) as client:
        payload = {"prompt": graph(body)}
        if body.get("comfy_prompt_id"):
            payload["prompt_id"] = body["comfy_prompt_id"]
        async with client.post(base + "/prompt", json=payload) as reply:
            submitted = await reply.json()
            if reply.status != 200:
                raise ValueError(json.dumps(submitted))
        prompt_id = submitted["prompt_id"]
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            async with client.get(base + "/history/" + prompt_id) as reply:
                history = await reply.json()
            if prompt_id in history:
                result = history[prompt_id]
                if result["status"]["status_str"] != "success":
                    errors = [m[1].get("exception_message", m[0])
                              for m in result["status"]["messages"] if m[0] == "execution_error"]
                    raise RuntimeError("; ".join(errors) or "ComfyUI execution failed.")
                return json.loads(result["outputs"]["2"]["text"][0])
            await asyncio.sleep(0.1)
    raise TimeoutError(f"ComfyUI request is still unfinished: {prompt_id}")
