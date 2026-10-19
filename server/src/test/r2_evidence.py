def verify(first, result):
    before, after = result['before'], result['after']
    assert result['service']['pid'] == first['comfy_pid']
    assert result['service']['created'] == result['process_created_after']
    assert after['weight_reads'] == before['weight_reads']
    assert all(v['reads'] == 1 and v['state'] == 'resident'
               for v in after['weight_reads'].values())
    models = {m['model']:m for m in after['models']}
    assert all(m['loads'] == 1 for m in models.values())
    llm = models['Qwen3.8-27B']
    assert llm['transfers'] == 2
    retained = llm['diagnostics']['storage']['cuda']
    offloads = [e for e in after['events'] if e['model'] == llm['model'] and e['event'] == 'offloaded']
    assert len(offloads) == 2
    assert all(e['ram_bytes'] == e['freed_bytes'] == retained for e in offloads)
    assert models['Qwen3.5-9B']['diagnostics']['storage']['cpu'] > 0
    assert models['Qwen3.5-9B']['diagnostics']['storage']['cuda'] == 0
    runs = [first['run'], *[t['run'] for t in result['turns']]]
    assert len(runs) == 3 and all(r['status'] == 'done' for r in runs)
    assert sum(s['kind'] == 'assistant' for r in runs for s in r['trace']['steps']) == 5
    host = first['observation']['host'] + result['observation']['host']
    assert min(h['planned_available'] for h in host) >= 8*1024**3
    assert max(h['swap_used'] for h in host) == 0
    assert not first['console_errors'] and not result['console_errors']
