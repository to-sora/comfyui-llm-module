def node(kind, **inputs):
    return {"class_type": kind, "inputs": inputs}


def graph(p, source=None, mask=None):
    g = {"1": node("CheckpointLoaderSimple", ckpt_name=p["checkpoint"]),
         "2": node("CLIPTextEncode", clip=["1", 1], text=p["prompt"]),
         "3": node("CLIPTextEncode", clip=["1", 1], text=p["negative"]),
         "4": node("EmptyLatentImage", width=p["width"], height=p["height"], batch_size=1),
         "5": node("KSampler", model=["1", 0], positive=["2", 0], negative=["3", 0],
                   latent_image=["4", 0], **{k: p[k] for k in
                   ("seed", "steps", "cfg", "sampler_name", "scheduler", "denoise")}),
         "6": node("VAEDecode", samples=["5", 0], vae=["1", 2]),
         "7": node("SaveImage", images=["6", 0], filename_prefix="workbench/" + p["output_key"])}
    if source:
        g["8"] = node("LoadImage", image=source)
        g["4"] = node("VAEEncode", pixels=["8", 0], vae=["1", 2])
    if mask:
        g["9"] = node("LoadImageMask", image=mask, channel="red")
        g["10"] = g["4"]
        g["4"] = node("SetLatentNoiseMask", samples=["10", 0], mask=["9", 0])
    return g
