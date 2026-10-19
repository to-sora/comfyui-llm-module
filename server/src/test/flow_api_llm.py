"""One transparent repair, matching Studio's malformed-tool recovery."""
from . import flow_api_prompt as prompt,flow_api_checks as check
from .flow_api_io import chat


def invoke(profile,messages,caps,pair,stage,observer,result):
    for attempt in range(2):
        reply=chat(prompt.body(profile,messages,caps,pair,stage),observer)
        result.setdefault('llm_requests',[]).append(reply)
        try:
            message,args,names=check.call(reply,stage,pair,caps)
            return reply,message,args,names
        except (AssertionError,KeyError,ValueError) as exc:
            if attempt:raise
            message=reply['choices'][0]['message']
            messages.append({'role':'assistant','content':message.get('raw_output') or str(message)})
            messages.append({'role':'user','content':
                'That call did not execute. Correct it once: '+str(exc)[:1200]+
                '\nUse the exact enum checkpoint names and requested image count; one generate_images call.'})
