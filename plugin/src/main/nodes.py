from .node_loader import QwenLoader
from .node_generate import QwenGenerate, QwenBatch

NODE_CLASS_MAPPINGS = {"QwenLoader": QwenLoader,
                       "QwenGenerate": QwenGenerate,
                       "QwenBatch": QwenBatch}
