def actual(e,run):
    wanted=run['settings']['quantization']
    if wanted in ('default','auto'):
        wanted=next(p['quantization'] for p in e.caps['profiles'] if p['id']==run['settings']['model'])
    steps=e.db.get('runs',run['id'])['trace'].get('steps',[])
    for step in reversed(steps):
        if step['kind']!='assistant':
            continue
        for model in step.get('memory',{}).get('models',[]):
            if (model['model']==run['settings']['model'] and model['loaded']
                    and model['kv_quantization']==run['settings']['kv_quantization']
                    and model['quantization']==wanted and model['precision']==run['settings']['precision']):
                return {**{k:model[k] for k in ('model','backend','quantization','kv_quantization','precision')},
                    'context_tokens':run['settings']['context_tokens'],
                    'weight_source':model.get('diagnostics',{}).get('weight_source')}
    return {'requested':run['settings'],'actual':'No runtime snapshot available'}
