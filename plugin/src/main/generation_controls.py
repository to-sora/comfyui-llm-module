from comfy import model_management as mm
from transformers import StoppingCriteria


def end_tokens(model, tokenizer):
    """Honor the chat tokenizer's EOS as well as checkpoint generation stops."""
    configured = model.generation_config.eos_token_id
    values = list(configured) if isinstance(configured, (list, tuple)) else [configured]
    values.append(tokenizer.eos_token_id)
    ids = sorted({value for value in values if isinstance(value, int)})
    return {'eos_token_id': ids} if ids else {}


class StopGeneration(StoppingCriteria):
    def __init__(self, tokenizer, marker=None):
        self.end = tokenizer.encode(marker, add_special_tokens=False) if marker else []

    def __call__(self, input_ids, scores, **kwargs):
        mm.throw_exception_if_processing_interrupted()
        return bool(self.end and input_ids[0, -len(self.end):].tolist() == self.end)


def single_tool(request):
    return bool(request.get("tools") and request.get("parallel_tool_calls") is False
                and request.get("tool_choice") != "none")
