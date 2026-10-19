from .tool_calls import parse
from .gemma_tools import parse as parse_gemma
from .model_response import parse as parse_response


def opened(tokenizer, inputs):
    return tokenizer.decode(inputs['input_ids'][0,-16:],skip_special_tokens=False).rstrip().endswith('<think>')


def finish(engine, request, tokens, count, thinking_open):
    processor = engine.processor
    tokenizer = getattr(processor,'tokenizer',processor)
    raw = processor.decode(tokens,skip_special_tokens=False)
    if thinking_open:
        raw = '<think>'+raw
    reasoning = 0
    if '<think>' in raw:
        thought = raw.split('<think>',1)[1].split('</think>',1)[0]
        reasoning = len(tokenizer.encode(thought,add_special_tokens=False))
    native_gemma = engine.model.config.model_type == 'gemma4'
    message = parse_response(parse_gemma if native_gemma else parse,raw,request.get('tools'))
    limit = request.get('max_completion_tokens',request.get('max_tokens',256))
    reason = 'tool_calls' if message.get('tool_calls') else 'length' if len(tokens)>=limit else 'stop'
    engine.diagnostics['thinking'] = {'enabled':request.get('enable_thinking',False),
                                    'tokens':reasoning, 'closed':'</think>' in raw}
    return {'message':message,'finish_reason':reason,'usage':{'prompt_tokens':count,
        'completion_tokens':len(tokens),'total_tokens':count+len(tokens),
        'completion_tokens_details':{'reasoning_tokens':reasoning},
        'image_tokens':engine.diagnostics.get('token_budget',{}).get('image_tokens',[])}}
