import gzip
import json
import shutil
from pathlib import Path
from .studio_helpers import OUT,record
from .flow_spec import PROFILES


def run():
    state=json.loads((OUT/'flow-api-progress.json').read_text())
    rows=[];pics=[];summary={};total=0
    for profile in PROFILES:
        p=state['profiles'].get(profile,{'completed':0})
        total+=p['completed'];records=[]
        for i in range(1,p['completed']+1):
            file=OUT/f'flow-api-{profile}-{i:02}.json.gz'
            records.append(json.loads(gzip.decompress(file.read_bytes())))
        calls=sum(len(r['llm_requests']) for r in records)
        summary[profile]={'rounds':p['completed'],'llm_calls':calls,
                            'repairs':calls-3*p['completed'],'images':5*p['completed']}
        rss=p.get('peak_rss',0)/1e9;free=p.get('min_planned_available',0)/1e9
        loads=next((m['loads'] for m in records[-1]['after']['models'] if m['model']==profile),0) if records else 0
        rows.append(f'<tr><td>{profile}</td><td>{p["completed"]}/25</td><td>{calls}</td>'
                    f'<td>{5*p["completed"]}</td><td>{loads}</td><td>{rss:.2f}</td><td>{free:.2f}</td></tr>')
        if records:
            image=records[0]['steps'][-1]['images'][0]['job']['outputs']['11']['images'][0]
            source=Path('plugin/data/output')/image['subfolder']/image['filename']
            name='flow-sample-'+profile+'.png'
            if not (OUT/name).exists():shutil.copyfile(source,OUT/name)
            pics.append(f'<a href="{name}"><img width="220" src="{name}" alt="{profile}: yellow mug"></a>')
    title=('PASS' if total==100 else 'IN PROGRESS')+f' · {total}/100 rounds'
    page='''<!doctype html><meta charset="utf-8"><title>LLM flow evidence</title>
<style>body{font:16px system-ui;max-width:1050px;margin:32px auto;padding:16px}td,th{border:1px solid #aaa;padding:8px}table{border-collapse:collapse}img{margin:6px}</style>'''
    page+=f'<h1>{title}</h1><p>PID {state["pid"]}. Real inference; NF4/BF16/HQQ8. '
    page+='35000 context / 12000 maximum output / 16000 per-image maximum. Basic images: 512², 28 steps.</p>'
    page+='<table><tr><th>Model</th><th>Rounds</th><th>LLM calls</th><th>Images</th><th>Reads</th><th>Peak RSS GB</th><th>Min free GB*</th></tr>'+''.join(rows)+'</table>'
    page+='<p>*80 GB plan. LLM picks pairs; images2/1/2. Sharing probes excluded; repairs add calls.</p>'
    page+='<p>單一 LLM；只有換 LLM 才釋放。SDXL 當輪保留並供其他請求共用。每輪檢查 LLM 讀取一次、實際圖片 token 及 RAM；未填滿 token 上限，未保證所有圖片語意完全正確。</p>'
    page+=''.join(pics)+'<p><a href="flow-api-progress.json">Progress / 進度</a> · <a href="flow-settings-ui.json">Firefox settings / 設定驗收</a></p>'
    assert len(page.encode())<=3000
    (OUT/'flow-api-261019.html').write_text(page)
    record('flow-api-summary',{'pid':state['pid'],'rounds':total,'profiles':summary})


if __name__=='__main__':run()
