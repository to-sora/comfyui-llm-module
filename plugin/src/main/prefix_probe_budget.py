def extra(text_config, tokens, mode):
    """Diagnostic hidden states and temporary projection/attention workspace."""
    tokens = min(tokens, 2112)
    hidden = text_config['hidden_size']
    width = max(text_config.get('intermediate_size', hidden*4), hidden*3)
    saved = tokens*hidden*(text_config['num_hidden_layers']+1)*2
    scratch = 4*width*(hidden+tokens)
    if mode in ('math_attention','fixed_reduction','fp32_projection'):
        scratch += 8*text_config['num_attention_heads']*tokens*tokens
    return saved+scratch
