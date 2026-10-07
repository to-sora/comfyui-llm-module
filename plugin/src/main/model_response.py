import re


def parse(parser, raw, tools):
    visible = re.sub(r"<think>.*?(?:</think>|$)", "", raw, flags=re.S)
    try:
        return parser(visible, tools)
    except (ValueError, KeyError, TypeError) as exc:
        return {"role": "assistant", "content": visible.strip() or None,
                "tool_parse_error": str(exc).strip() or "Malformed tool call", "raw_output": visible}
