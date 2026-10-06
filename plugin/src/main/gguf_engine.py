import llama_cpp as lc
from llama_cpp.llama_chat_format import MTMDChatHandler
from comfy import model_management as mm
from .images import data_url, tensor_images
from .messages import normalize
from .tool_calls import parse


def interrupt(tokens, scores):
    mm.throw_exception_if_processing_interrupted()
    return scores


class GGUFEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        if cfg["quantization"] not in {"auto", "none"}:
            raise ValueError("GGUF weight quantization is stored in the file; choose auto.")
        types = {"none": lc.GGML_TYPE_F16, "q8_0": lc.GGML_TYPE_Q8_0,
                 "q4_0": lc.GGML_TYPE_Q4_0}
        if cfg["kv_quantization"] not in types:
            raise ValueError("GGUF KV quantization: none, q8_0, q4_0")
        gpu = cfg["device"] != "cpu"
        if gpu and not lc.llama_supports_gpu_offload():
            raise RuntimeError("Install the CUDA GGUF backend with plugin/install-gguf.sh")
        self.handler = MTMDChatHandler(cfg["mmproj"], verbose=False, use_gpu=gpu) if cfg["mmproj"] else None
        self.model = lc.Llama(
            model_path=cfg["model"], n_ctx=cfg["context_tokens"],
            n_gpu_layers=-1 if gpu else 0, n_batch=512, n_ubatch=256,
            flash_attn=True, type_k=types[cfg["kv_quantization"]],
            type_v=types[cfg["kv_quantization"]], chat_handler=self.handler,
            verbose=False)
        if self.handler:
            try:
                self.handler._init_mtmd_context(self.model)
            except BaseException:
                self.model.close()
                raise

    def chat(self, request, images=None):
        messages, tools = normalize(request)
        pictures = tensor_images(images)
        if pictures:
            user = next(m for m in reversed(messages) if m["role"] == "user")
            if isinstance(user["content"], str):
                user["content"] = [{"type": "text", "text": user["content"]}]
            user["content"] += [{"type": "image_url", "image_url": {"url": data_url(p)}} for p in pictures]
        args = dict(messages=messages, tools=tools, temperature=request.get("temperature", 0),
                    max_tokens=request.get("max_completion_tokens", request.get("max_tokens", 256)),
                    logits_processor=lc.LogitsProcessorList([interrupt]))
        self.model.reset()
        if self.handler:
            result = self.handler(llama=self.model, **args, enable_thinking=request.get("enable_thinking", False))
        else:
            result = self.model.create_chat_completion(**args)
        choice = result["choices"][0]
        message = parse(choice["message"].get("content") or "", tools)
        return {"message": message, "finish_reason": "tool_calls" if message.get("tool_calls") else choice["finish_reason"],
                "usage": result["usage"]}

    def close(self):
        self.model.close()
        self.model = self.handler = None
