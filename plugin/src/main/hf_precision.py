from contextlib import contextmanager
import torch


def selected(name, path):
    if name in ('fp32_projection', 'fp32_default_attention', 'prefill_fp32', 'prefill_fp16'):
        return True
    if name == 'mlp_down_fp32':
        return path.endswith('.mlp.down_proj')
    if name == 'mlp_gateup_fp32':
        return path.endswith(('.mlp.gate_proj', '.mlp.up_proj'))
    return ((name == 'attention_fp32' and any(p in path for p in ('.linear_attn.', '.self_attn.')))
            or (name == 'mlp_fp32' and '.mlp.' in path))


@contextmanager
def precision(model, name):
    saved, hooks = [], []
    head = model.get_output_embeddings()
    owned, original = 'forward' in head.__dict__, head.forward
    try:
        for path, module in model.named_modules():
            if type(module).__name__ != 'Linear4bit' or not selected(name, path):
                continue
            dtype = module.compute_dtype
            saved.append((module, dtype, module.compute_type_is_set,
                          module.bias.dtype if module.bias is not None else None))
            module.compute_type_is_set = True
            if name not in ('fp32_projection', 'fp32_default_attention'):
                def choose(layer, args, original=dtype):
                    value = args[0]
                    target = torch.float16 if name == 'prefill_fp16' else torch.float32
                    layer.compute_dtype = target if value.numel() > value.shape[-1] else original
                hooks.append(module.register_forward_pre_hook(choose))
            else:
                module.compute_dtype = torch.float32
        if name == 'head_fp32':
            def project(value):
                if value.device.type == 'cuda' and value.dtype in (torch.float16, torch.bfloat16):
                    output = torch.mm(value.reshape(-1, value.shape[-1]), head.weight.t(),
                                      out_dtype=torch.float32)
                    if head.bias is not None:
                        output += head.bias.float()
                    return output.reshape(*value.shape[:-1], head.out_features)
                return original(value)
            head.forward = project
        yield
    finally:
        if name == 'head_fp32':
            if owned:
                head.forward = original
            else:
                del head.forward
        for hook in hooks:
            hook.remove()
        for module, dtype, configured, bias_dtype in saved:
            module.compute_dtype, module.compute_type_is_set = dtype, configured
            if bias_dtype is not None:
                module.bias.data = module.bias.data.to(bias_dtype)
