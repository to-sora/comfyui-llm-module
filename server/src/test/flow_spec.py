PROFILES = ['Qwen3.5-9B','Qwen3.5-9B-gguf','Qwen3.8-27B-OBLITERATED','Qwen3.8-27B']
SETTINGS = {'quantization':'bnb_nf4','precision':'bfloat16','kv_quantization':'hqq_8',
            'context_tokens':35000,'max_tokens':12000,'max_image_tokens':16000,
            'enable_thinking':True,'image_checkpoint':'','parallel_tool_calls':False}
