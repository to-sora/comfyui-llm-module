import{S,$,el,on,api,tool,selected,select,guarded}from'./state.js';
import{settings,populate}from'./forms.js';
import{blob}from'./mask.js';
export async function saveSettings(){return api(`/session/${S.sid}/settings`,settings());}
export async function upload(file,mask=false){const form=new FormData();form.append('image',file,file.name||'mask.png');const r=await fetch(`/api/session/${S.sid}/upload${mask?'?mask=1':''}`,{method:'POST',body:form});const v=await r.json();if(!r.ok)throw Error(v.error);return v;}
async function generate(send){await saveSettings();const p=settings(),mode=$('mode').value;const args={...p};delete args.mode;if(mode!=='text'){const i=selected();if(!i)throw Error('Select or upload a source image.');args.source=i.id;if(mode==='inpaint'){args.width=i.width;args.height=i.height;args.mask=(await upload(await blob(),true)).id;}}
await tool('image_gen_sdxl_'+mode,args);if(send)await tool('sent_all_pending');}
export function init(){on('generate',()=>generate(true));on('queue',()=>generate(false));on('send-pending',()=>tool('sent_all_pending'));$('upload').onclick=()=>$('file-input').click();$('file-input').onchange=()=>guarded(async()=>{const file=$('file-input').files[0];if(file){const i=await upload(file);S.selected=i.id;$('file-input').value='';}});
const box=$('image-actions');for(const[id,label]of [['edit-selected','Edit'],['download','Download'],['reuse','Reuse settings'],['check-result','Check result'],['revise','Revise from feedback']]){const b=el('button',label);b.id=id;box.append(b);}
$('edit-selected').onclick=()=>{$('edit-panel').open=true;$('edit-panel').scrollIntoView({behavior:'smooth',block:'center'});};
on('reuse',async()=>{const i=selected();if(!i)throw Error('Select an image.');populate(i.settings||i.source_settings||{});});
on('download',async()=>{if(!selected())throw Error('Select an image.');const a=el('a');a.href=`/api/session/${S.sid}/image/${S.selected}?download=1`;a.download=`image-${S.selected}.png`;a.click();});
on('check-result',()=>inspect(false));on('revise',()=>inspect(true));}
async function inspect(revise){if(!selected())throw Error('Select an image.');await saveSettings();$('chat-panel').open=true;const requirement=$('chat-input').value.trim()||$('prompt').value.trim()||'Describe visible matches, problems, colors and objects.';const text=revise?`Revise image #${S.selected} from this feedback: ${$('inspection').textContent||requirement}. Queue an edit, send it, then inspect the actual result.`:`Check image #${S.selected} against: ${requirement}. Inspect actual visible pixels. Do not generate or edit.`;await api(`/session/${S.sid}/chat`,{text,images:[S.selected]});}
