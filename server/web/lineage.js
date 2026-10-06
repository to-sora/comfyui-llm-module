import{S,$,el,select}from'./state.js';
export function render(image){const nodes=new Map((S.data.lineage||S.data.images).map(i=>[i.id,i]));const out=$('lineage');out.replaceChildren();const seen=new Set();
function visit(id){if(seen.has(id))return;seen.add(id);const node=nodes.get(id);if(!node){out.append(el('span',`#${id} · shared source`,'muted'));return;}for(const parent of node.parents||[])visit(parent);if(out.childNodes.length)out.append(el('span','→','muted'));const b=el('button',`#${node.id} · ${node.operation}${node.deleted?' · deleted':''}${node.final?' · final':''}`);b.disabled=!!node.deleted;b.onclick=()=>select(node.id);out.append(b);}
visit(image.id);for(const event of S.data.events||[])if(event.image===image.id)out.append(el('span',event.action,'muted'));
for(const child of S.data.images.filter(i=>i.parents?.includes(image.id))){out.append(el('span','→','muted'));const b=el('button',`#${child.id} · ${child.operation}`);b.onclick=()=>select(child.id);out.append(b);}}
