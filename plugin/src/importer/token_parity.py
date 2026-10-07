import json
import sys
from pathlib import Path
from transformers import AutoTokenizer
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Jinja2ChatFormatter
from ..main.settings import APP

TEXTS = ['Hello world!', '香港的天空是藍色。', 'def square(x):\n    return x * x',
         '  two spaces\n\tand a tab', '<|im_start|>user\nHi<|im_end|>']
DIALOGS = [
    [{'role': 'user', 'content': 'Hello!'}],
    [{'role': 'system', 'content': 'Use Traditional Chinese.'}, {'role': 'user', 'content': 'What is a mountain?'}],
    [{'role': 'user', 'content': 'Make a photo of a red cup.'},
     {'role': 'assistant', 'content': None, 'tool_calls': [{'type': 'function', 'function':
         {'name': 'generate_images', 'arguments': {'images': [{'prompt': 'a red cup'}]}}}]},
     {'role': 'tool', 'content': '{"image":3}'}]]


def main():
    target = APP / 'data/imported' / sys.argv[1]
    info = json.loads((target / 'import.json').read_text())
    tokenizer = AutoTokenizer.from_pretrained(target, local_files_only=True)
    llama = Llama(model_path=info['source'], vocab_only=True, n_gpu_layers=0, verbose=False)
    try:
        tokens = []
        for text in TEXTS:
            actual = tokenizer.encode(text, add_special_tokens=False)
            expected = llama.tokenize(text.encode(), add_bos=False, special=True)
            assert actual == expected, (text, actual, expected)
            tokens.append(len(actual))
        formatter = Jinja2ChatFormatter(llama.metadata['tokenizer.chat_template'],
            eos_token=tokenizer.eos_token, bos_token=tokenizer.bos_token or '')
        for dialog in DIALOGS:
            ref = formatter(messages=dialog, enable_thinking=False).prompt
            got = tokenizer.apply_chat_template(dialog, tokenize=False, add_generation_prompt=True, enable_thinking=False)
            assert ref == got, (ref, got)
        result = {'profile': info['profile'], 'tokenizer': 'PASS', 'texts': TEXTS,
                  'token_counts': tokens, 'template': 'PASS', 'dialogs': len(DIALOGS)}
        (target / 'token-parity.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False))
    finally:
        llama.close()


if __name__ == '__main__':
    main()
