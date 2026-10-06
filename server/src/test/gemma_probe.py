import json
import sys
import urllib.request
from client import call, CTX, save

sys.path.insert(0, str(__import__('client').ROOT))
from server.src.main.tool_schema import schemas

caps = call("/bootstrap")["capabilities"]
full = schemas(caps)
compact = [t for t in full if t["function"]["name"] in ("image_gen_sdxl_text", "sent_all_pending", "view_images")]
for label, tools, choice in (("required", full, "required"), ("compact", compact, "auto")):
    body = {"model": "gemma-4-E2B", "kv_quantization": "hqq_8", "context_tokens": 4096,
        "max_tokens": 700, "tools": tools, "tool_choice": choice, "parallel_tool_calls": False,
        "messages": [{"role": "system", "content": "Queue the requested images using image_gen_sdxl_text. Once all are pending, use sent_all_pending. Return one tool call at a time. Never invent results."},
                     {"role": "user", "content": "Generate two images: a yellow teapot and a green chair. Queue both before submitting the batch."}]}
    req = urllib.request.Request("https://127.0.0.1:8188/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=300) as r:
            result = json.load(r)
    except Exception as exc:
        result = {"error": exc.read().decode() if hasattr(exc, "read") else str(exc)}
    print(label, result, flush=True)
    save("gemma-probe-" + label, result)
