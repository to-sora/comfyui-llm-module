from .errors import UserError
import time
import uuid


def response(model, result):
    return {"id": "chatcmpl-" + uuid.uuid4().hex, "object": "chat.completion",
            "created": int(time.time()), "model": model,
            "choices": [{"index": 0, "message": result["message"],
                         "finish_reason": result["finish_reason"]}],
            "usage": result["usage"]}


def validate(body):
    if not isinstance(body, dict):
        raise UserError("Request must be a JSON object.")
    if not isinstance(body.get("model"), str):
        raise UserError("model must be a string.")
    if not isinstance(body.get("messages"), list) or not body["messages"]:
        raise UserError("messages must be a nonempty array.")
    for message in body["messages"]:
        if not isinstance(message, dict) or message.get("role") not in {
                "system", "developer", "user", "assistant", "tool"}:
            raise UserError("Each message needs a valid role.")
    if not isinstance(body.get("tools", []), list):
        raise UserError("tools must be an array.")
    for tool in body.get("tools", []):
        function = tool.get("function") if isinstance(tool, dict) else None
        if not isinstance(function, dict) or tool.get("type") != "function" or not isinstance(
                function.get("name"), str):
            raise UserError("Each tool needs a function name.")
    for field in ("stream", "parallel_tool_calls", "prefix_cache"):
        if field in body and not isinstance(body[field], bool):
            raise UserError(f"{field} must be a boolean.")
    if 'diagnostic_prefix' in body and body['diagnostic_prefix'] not in (
            'default', 'full_accumulation', 'math_attention', 'fixed_reduction',
            'fp32_projection', 'fp32_default_attention', 'prefix_fp32', 'prefill_fp32', 'dense_prefill',
            'attention_fp32', 'mlp_fp32', 'head_fp32', 'mlp_down_fp32', 'mlp_gateup_fp32',
            'prefill_fp16', 'mlp_math_fp32'):
        raise UserError('Unknown prefix diagnostic mode.')
    temperature = body.get("temperature", 0)
    if body.get('diagnostic_kernels','reference') not in ('reference','local','conv','delta'):
        raise UserError('Unknown hybrid kernel mode.')
    if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 2:
        raise UserError("temperature must be between 0 and 2.")
    if body.get("n", 1) != 1:
        raise UserError("Only n=1 is supported; submit separate queued requests.")
    limit = body.get("max_completion_tokens", body.get("max_tokens", 256))
    if type(limit) is not int or limit <= 0:
        raise UserError("max_tokens must be a positive integer.")
    from .request_options import validate as validate_options
    validate_options(body)
    return body
