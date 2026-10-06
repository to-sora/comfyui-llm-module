from .edit_schema import definitions


def field(kind, **extra):
    return {"type": kind, **extra}


def tool(name, description, properties=None, required=None):
    return {"type": "function", "function": {"name": name, "description": description,
        "parameters": {"type": "object", "properties": properties or {}, "required": required or []}}}


def schemas(caps, expanded=False):
    ident = field("integer", minimum=0, maximum=20000)
    props = {"prompt": field("string"), "negative": field("string"),
        "width": field("integer", maximum=4096), "height": field("integer", maximum=4096),
        "seed": field("integer"), "steps": field("integer"), "cfg": field("number"),
        "denoise": field("number", minimum=0, maximum=1)}
    if expanded:
        from .model_tools import schema
        props.update(schema(caps)["function"]["parameters"]["properties"])
    result = [tool("image_gen_sdxl_text", "Queue a text-to-image job; call sent_all_pending to generate.", props, ["prompt"]),
        tool("image_gen_sdxl_image", "Queue image-to-image using a source image/job ID.",
             {**props, "source": ident}, ["source", "prompt"]),
        tool("image_gen_sdxl_inpaint", "Queue masked edit; white mask pixels change.",
             {**props, "source": ident, "mask": ident}, ["source", "mask", "prompt"]),
        tool("sent_all_pending", "Generate ALL queued jobs in one batch, then inspect the final images."),
        tool("check_current_pending", "List pending jobs."),
        tool("list_models", "List detected LLM profiles and compatible SDXL checkpoints."),
        tool("view_images", "Attach actual image pixels for visual inspection.",
             {"ids": field("array", items=ident, minItems=1, maxItems=4)}, ["ids"])]
    for name in ("job_status", "cancel_job"):
        result.append(tool(name, name.replace("_", " "), {"id": ident}, ["id"]))
    edits = definitions()
    result.append(tool("image_edit_basic", "Queue CPU editing. params are operation settings.",
        {"source": ident, "operation": field("string", enum=list(edits)), "params": field("object")}, ["source", "operation"]))
    for op, definition in edits.items():
        if not expanded and op != "text":
            continue
        args = {"source": ident}
        for key, spec in definition.items():
            args[key] = field("string" if spec[0] == "enum" and isinstance(spec[1], str) else
                "number" if spec[0] == "enum" else spec[0], default=spec[1])
            if spec[0] == "enum":
                args[key]["enum"] = spec[2:]
        result.append(tool("image_edit_" + op, "Queue CPU " + op, args, ["source"]))
    if expanded:
        result.append(schema(caps))
        from .queue_batch import schema as batch_schema
        result.append(batch_schema())
    return result
