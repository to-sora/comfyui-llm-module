def graph(seed=42):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {
            "clip": ["1", 1], "text": "A red cube beside a blue sphere on a white table, studio photograph, soft lighting"}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {
            "clip": ["1", 1], "text": "text, watermark, blurry"}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {
            "width": 1024, "height": 1024, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
            "latent_image": ["4", 0], "seed": seed, "steps": 20, "cfg": 6.0,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {
            "samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {
            "images": ["6", 0], "filename_prefix": "sdxl-api-check"}},
    }
