import{S,$,el,options}from'./state.js';
export function field(parent,name,label,type='text',value='',attrs={}){const l=el('label',label,'field');const input=el(type==='textarea'?'textarea':type==='select'?'select':'input');input.id=name;input.name=name;if(input.tagName==='INPUT')input.type=type;input.value=value;for(const[k,v]of Object.entries(attrs))input.setAttribute(k,v);l.append(input);parent.append(l);return input;}
export function init(){const box=$('settings');box.innerHTML='<h2>Create & refine <small>生成與修改</small></h2><p class="muted field">SDXL · ComfyUI workflows</p><div id="model-fields"></div><div id="prompt-fields"></div><div id="size-fields" class="grid2"></div><details id="advanced"><summary>Advanced settings</summary><div id="advanced-fields" class="grid2"></div></details><div id="generate-buttons" class="toolbar"></div>';
field($('model-fields'),'checkpoint','Image model · 圖片模型','select');
field($('model-fields'),'mode','Workflow','select');options($('mode'),['text','image','inpaint']);
field($('prompt-fields'),'prompt','Positive prompt · 提示','textarea','',{placeholder:'Describe the image you want…'});
field($('prompt-fields'),'negative','Negative prompt','textarea','',{placeholder:'Things to avoid…'});
for(const[k,label]of [['width','Width'],['height','Height']])field($('size-fields'),k,label,'number',1024,{min:16,max:4096,step:8});
const adv=$('advanced-fields');
for(const[k,label,type]of [['seed','Seed','text'],['steps','Steps','number'],['cfg','CFG','number'],['denoise','Image strength','number'],['sampler_name','Sampler','select'],['scheduler','Scheduler','select']])field(adv,k,label,type);
$('steps').min=1;$('steps').max=10000;$('cfg').step=.1;$('denoise').step=.05;$('denoise').min=0;$('denoise').max=1;
for(const[id,title,cls]of [['generate','Generate','primary'],['queue','Add to pending',''],['upload','Upload image','']]){const b=el('button',title,cls);b.id=id;$('generate-buttons').append(b);}
const input=el('input');input.type='file';input.accept='image/*';input.id='file-input';input.hidden=true;box.append(input);}
export function settings(){const data={};document.querySelectorAll('#settings [name],#llm-fields [name]').forEach(n=>{data[n.name]=n.type==='number'?Number(n.value):n.value;});return data;}
export function populate(data){for(const[k,v]of Object.entries(data)){const n=$(k);if(n)n.value=v;}}
