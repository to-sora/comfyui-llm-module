from .plugin.src.main.nodes import NODE_CLASS_MAPPINGS
from .plugin.src.main.bootstrap import initialize

initialize()
WEB_DIRECTORY = "./plugin/web"
__all__ = ["NODE_CLASS_MAPPINGS", "WEB_DIRECTORY"]
