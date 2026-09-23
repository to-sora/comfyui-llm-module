from pathlib import Path
import torch
import transformers as tf
from plugin.src.main.settings import DATA
from plugin.src.main.spec import normalize
from plugin.src.main.tensor_backend import TensorBackend
from plugin.src.main.tensor_prefix import TensorPrefix


def build():
    folder = DATA / 'hf/hub/models--Qwen--Qwen3.5-0.8B/snapshots'
    paths = list(folder.glob('*/config.json'))
    if not paths:
        return None
    path = paths[0].parent
    config = tf.AutoConfig.from_pretrained(path, local_files_only=True)
    for k, v in dict(hidden_size=32, intermediate_size=64,
        num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
        head_dim=8, linear_num_key_heads=2, linear_num_value_heads=4,
        linear_key_head_dim=8, linear_value_head_dim=8,
        layer_types=['linear_attention', 'full_attention']).items():
        setattr(config.text_config, k, v)
    config.text_config.rope_parameters.update(partial_rotary_factor=1.0,
                                             mrope_section=[1, 1, 2])
    for k, v in dict(hidden_size=32, intermediate_size=64, out_hidden_size=32,
                     depth=1, num_heads=4).items():
        setattr(config.vision_config, k, v)
    torch.manual_seed(2)
    backend = TensorBackend(normalize(str(path), device='cpu', dtype='float32'))
    backend.processor = tf.AutoProcessor.from_pretrained(path, local_files_only=True)
    backend.model = tf.AutoModelForMultimodalLM.from_config(config).eval()
    backend.vision = True
    backend.cache = TensorPrefix(backend)
    backend.cache.warm()
    return backend
