from .assets import check_size
from .errors import UserError
from .generation import defaults, recipe, seed


def options(caps, settings, args, mode="text"):
    value = {**caps["defaults"], **defaults(), **args}
    value["seed"] = seed(args.get("seed"))
    if "aspect" in args and "width" not in args and "height" not in args:
        if args["aspect"] not in recipe()["aspects"]:
            raise UserError("Unknown image aspect")
        value["width"], value["height"] = recipe()["aspects"][args["aspect"]]
    value["denoise"] = 1.0 if mode == "text" else args.get("denoise", 0.5)
    if mode != "text" and "strength" in args:
        if args["strength"] not in recipe()["strengths"]:
            raise UserError("Strength must be low, medium or high")
        value["denoise"] = recipe()["strengths"][args["strength"]]
    try:
        for k in ("width", "height", "steps"):
            value[k] = int(value[k])
    except (TypeError, ValueError) as exc:
        raise UserError("Image dimensions and steps must be integers") from exc
    check_size((value["width"], value["height"]))
    if mode == "text" and any(value[k] % 8 or value[k] < 16 for k in ("width", "height")):
        raise UserError("SDXL dimensions must be multiples of 8, from 16 to 4096")
    if not 0 <= value["seed"] <= 2**64 - 1 or not 1 <= value["steps"] <= 10000:
        raise UserError("Invalid seed or steps")
    for k, maximum in (("cfg", 100), ("denoise", 1)):
        value[k] = float(value[k])
        if not 0 <= value[k] <= maximum:
            raise UserError(f"Invalid {k}")
    for k in ("sampler_name", "scheduler"):
        if value[k] not in caps["enums"][k]:
            raise UserError(f"Unknown {k}")
    if value["checkpoint"] not in caps["checkpoints"]:
        raise UserError("Select a detected compatible SDXL checkpoint")
    return {k: value[k] for k in ("prompt", "negative", "checkpoint", "width", "height",
        "seed", "steps", "cfg", "sampler_name", "scheduler", "denoise")}
