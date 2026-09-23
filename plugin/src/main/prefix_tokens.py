def common_prefix(encode):
    """Probe valid conversations because Qwen3.5 templates require a user turn."""
    first = encode("A prefix warmup probe")
    second = encode("Z different warmup probe")
    count = 0
    for left, right in zip(first, second):
        if left != right:
            break
        count += 1
    if count == 0:
        raise ValueError("Chat template produced an empty reusable prefix")
    return first[:count]
