from comfy import model_management as mm
from transformers import StoppingCriteria


class StopGeneration(StoppingCriteria):
    def __init__(self, tokenizer, marker=None):
        self.end = tokenizer.encode(marker, add_special_tokens=False) if marker else []

    def __call__(self, input_ids, scores, **kwargs):
        mm.throw_exception_if_processing_interrupted()
        return bool(self.end and input_ids[0, -len(self.end):].tolist() == self.end)


def single_tool(request):
    return bool(request.get("tools") and request.get("parallel_tool_calls") is False
                and request.get("tool_choice") != "none")


def gguf_controls(model, request):
    end = model.tokenize(b"</tool_call>", add_bos=False, special=True) if single_tool(request) else []
    def control(tokens, scores):
        mm.throw_exception_if_processing_interrupted()
        if end and tokens[-len(end):].tolist() == end:
            scores[:] = float("-inf")
            scores[model.token_eos()] = 0
        return scores
    return control
