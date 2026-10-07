export const S={sid:null,boot:null,data:null,selected:null,checked:new Set(),refreshers:[]};
export const $=id=>document.getElementById(id);
export function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
export function notice(text){$('notice').textContent=text;$('notice').hidden=!text;}
export async function api(path,body){const r=await fetch('/api'+path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const v=await r.json();if(!r.ok||(v.error&&path!=='/bootstrap'))throw Error(v.error||r.statusText);return v;}
export const url=(id,query='')=>`/api/session/${S.sid}/image/${id}${query}`;
export async function tool(name,args={}){return api(`/session/${S.sid}/tool`,{name,arguments:args,request_id:crypto.randomUUID()});}
export async function refresh(){S.data=await api(`/session/${S.sid}/state`);for(const fn of S.refreshers)fn();}
export async function guarded(fn,button){try{notice('');if(button)button.disabled=true;await fn();await refresh();}catch(e){notice(e.message);}finally{if(button)button.disabled=false;if(S.data)for(const render of S.refreshers)render();}}
export const selected=()=>S.data?.images.find(i=>i.id===S.selected);
export function on(id,fn){$(id).onclick=()=>guarded(fn,$(id));}
export function select(id){S.selected=id;for(const fn of S.refreshers)fn();}
export function options(node,values,current){node.replaceChildren(...values.map(v=>{const o=el('option',String(v));o.value=v;return o;}));if(current!==undefined)node.value=current;}
