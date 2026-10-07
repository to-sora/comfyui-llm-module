def staging(config):
    text = getattr(config, "text_config", config)
    # CPU-dispatched embeddings/output heads are temporarily staged on the GPU.
    return int(text.vocab_size * text.hidden_size * 2 * 1.25)


def weight_budget(config, available):
    budget = int(available - staging(config))
    if budget < 256 * 1024**2:
        raise MemoryError("Not enough GPU memory to stage an offloaded model layer")
    return budget
