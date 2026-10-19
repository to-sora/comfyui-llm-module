import asyncio
from pathlib import Path
from aiohttp import web
from .registry import profiles
from .settings import APP,read
from .checkpoint_cache import native
from .checkpoint_header import shapes


def checkpoints():
    accepted, excluded = [], []
    root=(APP/read('config.yaml')['comfy_directory']).resolve()/'models/checkpoints'
    for name in native().INPUT_TYPES()['required']['ckpt_name'][0]:
        try:
            shape = shapes(root/name)
            prefix = "model.diffusion_model."
            adm = shape.get(prefix + "label_emb.0.0.weight", [])
            inp = shape.get(prefix + "input_blocks.0.0.weight", [])
            keys = list(shape)
            valid = len(adm) == 2 and adm[1] == 2816 and len(inp) == 4 and inp[1] == 4
            valid &= all(any(k.startswith(p) for k in keys) for p in (
                "first_stage_model.", "conditioner.embedders.0.", "conditioner.embedders.1."))
            (accepted if valid else excluded).append(name)
        except Exception:
            excluded.append(name)
    from .ram_budget import SDXL_LIMIT
    return {"checkpoints": accepted, "excluded_count": len(excluded),
            'batch_checkpoints':[name for name in accepted if (root/name).stat().st_size<=SDXL_LIMIT//2]}


def install(routes):
    @routes.get("/llm/capabilities")
    async def capabilities(request):
        result = await asyncio.to_thread(checkpoints)
        result["profiles"] = [{"id": name, "backend": p["backend"],
            "quantization": p.get("quantization", "auto"), "kv_quantization": "none",
            "vision": True}
            for name, p in profiles().items()]
        result["scoped_cancel"] = True
        return web.json_response(result)
