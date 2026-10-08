export const $=(q,root=document)=>root.querySelector(q);
export function el(tag,attrs={},...children){const node=document.createElement(tag);for(const [k,v]of Object.entries(attrs)){if(v==null)continue;if(k.startsWith('on'))node.addEventListener(k.slice(2),v);else if(k==='class')node.className=v;else if(k in node)node[k]=v;else node.setAttribute(k,v)}for(const c of children.flat())if(c!=null)node.append(c instanceof Node?c:document.createTextNode(String(c)));return node}
export const button=(text,fn,attrs={})=>el('button',{type:'button',onclick:fn,...attrs},text);
export function toast(text){const n=$('#toast');n.textContent=text;n.hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>n.hidden=true,6500)}
export async function copy(text){try{await navigator.clipboard.writeText(text);toast('Copied')}catch{toast('Copy was unavailable in this browser')}}
export function dialog(title,content){const d=$('#dialog');d.replaceChildren(el('h2',{},title),content,button('Close',()=>d.close()));d.showModal();return d}
export function safe(fn){return async(...args)=>{try{return await fn(...args)}catch(e){toast(e.message||'Something went wrong')}}}
