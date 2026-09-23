def prepare(engine, prefix, prompt=None, images=None):
    messages = []
    if prefix:
        messages.append({"role": "system", "content": prefix})
    if prompt is not None:
        content = prompt
        if images:
            if not engine.vision:
                raise ValueError("Images require a vision model / 圖片需要視覺模型")
            content = [{"type": "image", "image": image} for image in images]
            content.append({"type": "text", "text": prompt})
        messages.append({"role": "user", "content": content})
    processor = engine.processor
    tokenizer = getattr(processor, "tokenizer", processor)
    template = getattr(processor, "chat_template", None) or tokenizer.chat_template
    if template:
        return processor.apply_chat_template(
            messages, tokenize=True, return_dict=True, return_tensors="pt",
            add_generation_prompt=prompt is not None, enable_thinking=False,
        ).to(engine.model.device)
    if images:
        raise ValueError("Vision checkpoint requires a chat template")
    return tokenizer(prefix + (prompt or ""), return_tensors="pt").to(engine.model.device)


def prefill_inputs(engine, prefix):
    first = prepare(engine, prefix, "A")
    second = prepare(engine, prefix, "B")
    a, b = first["input_ids"][0], second["input_ids"][0]
    length = 0
    for left, right in zip(a.tolist(), b.tolist()):
        if left != right:
            break
        length += 1
    return {key: value[..., :length] for key, value in first.items()
            if key in {"input_ids", "attention_mask", "token_type_ids", "mm_token_type_ids"}}
