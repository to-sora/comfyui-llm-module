from .assets import check_size


def options(caps, settings, args):
    value = {**caps["defaults"], **settings, **args}
    for k in ("width", "height", "seed", "steps"):
        value[k] = int(value[k])
    check_size((value["width"], value["height"]))
    if any(value[k] % 8 or value[k] < 16 for k in ("width", "height")):
        raise ValueError("SDXL dimensions must be multiples of 8, from 16 to 4096")
    if not 0 <= value["seed"] <= 2**64 - 1 or not 1 <= value["steps"] <= 10000:
        raise ValueError("Invalid seed or steps")
    for k, maximum in (("cfg", 100), ("denoise", 1)):
        value[k] = float(value[k])
        if not 0 <= value[k] <= maximum:
            raise ValueError(f"Invalid {k}")
    for k in ("sampler_name", "scheduler"):
        if value[k] not in caps["enums"][k]:
            raise ValueError(f"Unknown {k}")
    if value["checkpoint"] not in caps["checkpoints"]:
        raise ValueError("Select a detected compatible SDXL checkpoint")
    return {k: value[k] for k in ("prompt", "negative", "checkpoint", "width", "height",
        "seed", "steps", "cfg", "sampler_name", "scheduler", "denoise")}
