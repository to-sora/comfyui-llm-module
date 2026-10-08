from .hf_load import load, processor
from .hf_inputs import prepare
from .hf_move import move
from .images import tensor_images
from .residency import sizes


class HFEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.processor, self.vision = processor(cfg)
        self.model = None
        self.diagnostics = {}
        self.prefixes = []

    def load(self, device, budget):
        if self.model is None:
            self.model = load({**self.cfg, "device": device}, self.processor, self.vision, budget)
            self.diagnostics["weight_modules"] = sum(type(m).__name__ in {"Linear4bit", "Linear8bitLt"}
                                                      for m in self.model.modules())
            self.diagnostics["weight_source"] = self.model._llm_weight_source
        else:
            move(self.model, device, budget)
        self.diagnostics["storage"] = sizes(self.model)

    def prepare(self, request, images):
        return prepare(self.processor, self.vision, request, tensor_images(images))

    def cache_tensors(self):
        from .prefix_state import tensors
        return [t for entry in self.prefixes for t in tensors(entry['state'])]

    def chat(self, request, inputs, required):
        from .hf_generate import generate
        from .working_memory import measured
        from .kernel_policy import selected
        with selected(self, request), measured(self, required):
            return generate(self, request, inputs)

    def offload(self):
        if self.model is not None:
            move(self.model, "cpu", 0)
            self.diagnostics["storage"] = sizes(self.model)
