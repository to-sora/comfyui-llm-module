import{S,$,options}from'./state.js';
import{field,populate}from'./forms.js';
export function init(){const box=$('model-fields');field(box,'model','Assistant / VLM · 語言模型','text','',{list:'model-list'});const list=document.createElement('datalist');list.id='model-list';box.append(list);
const d=document.createElement('details');d.innerHTML='<summary>LLM settings · 模型設定</summary><div id="llm-fields" class="grid2"></div>';box.append(d);
const f=$('llm-fields');field(f,'context_tokens','Context tokens','number',4096,{min:128,max:262144});field(f,'max_tokens','Reply tokens','number',512,{min:1,max:8192});field(f,'quantization','Weight quantization','select');field(f,'kv_quantization','KV quantization','select');field(f,'backend','Backend','select');options($('backend'),['auto','transformers','gguf']);field(f,'mmproj','GGUF vision projector path');
$('model').onchange=()=>quant();$('backend').onchange=()=>quant();}
export function quant(){const caps=S.boot.capabilities;if(!caps)return;const p=caps.profiles.find(p=>p.id===$('model').value);const backend=$('backend').value==='auto'?(p?.backend||($('model').value.endsWith('.gguf')?'gguf':'transformers')):$('backend').value;
const weight=backend==='gguf'?['default','auto','none']:caps.enums.quantization;
const kv=backend==='gguf'?['none','q8_0','q4_0']:['none','hqq_8','hqq_4'];
for(const[id,values]of [['quantization',weight],['kv_quantization',kv]]){const v=$(id).value;options($(id),values,values.includes(v)?v:values[0]);}}
export function load(){const caps=S.boot.capabilities;if(!caps)return;options($('checkpoint'),caps.checkpoints);options($('model-list'),caps.profiles.map(p=>p.id));for(const k of ['sampler_name','scheduler'])options($(k),caps.enums[k]);populate({...caps.defaults,...S.data.session.settings});quant();populate(S.data.session.settings);}
