from .plugin.src.main.bootstrap import initialize

initialize()
from .plugin.src.main.nodes import NODE_CLASS_MAPPINGS

NODE_DISPLAY_NAME_MAPPINGS = {
    name: name.replace("Qwen", "Qwen ") for name in NODE_CLASS_MAPPINGS
}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
