import {state,emit} from './state.js';
import {$,el,button,safe,dialog} from './dom.js';
import {api,download} from './api.js';
import {card} from './cards.js';
let selected=new Set(),filter='',cursor,revision=0;
function remove(){
 const content=el('div',{},el('p',{},'The selected files will be removed. This cannot be undone.'));
 const d=dialog('Delete selected images?',content);
 content.append(button('Delete images',safe(async()=>{
  await api('/api/images/actions','POST',{action:'delete',images:[...selected]});
  d.close();await show();
 }),{class:'danger'}));
}
function selection(){
 const bar=$('#selection-bar');bar.hidden=!selected.size;
 bar.replaceChildren(el('span',{class:'grow'},selected.size+' selected'),
  button('Download ZIP',safe(()=>download([...selected]))),
  button('Use in new chat',()=>emit('navigate',{path:'/',attachments:[...selected].map(i=>state.images[i])})),
  button('Delete',remove),button('Clear',()=>{selected.clear();
   document.querySelectorAll('.library-card input').forEach(n=>n.checked=false);selection();}));
}
async function load(){const request=revision,route=state.route;$('#load-more').disabled=true;try{const data=await api('/api/images?filter='+filter+(cursor?'&cursor='+cursor:''));if(request!==revision||route!==state.route)return;cursor=data.cursor;const grid=$('#library-grid');for(const image of data.images){state.images[image.id]=image;const check=el('input',{type:'checkbox','aria-label':'Select image',checked:selected.has(image.id),onchange:e=>{if(e.target.checked)selected.add(image.id);else selected.delete(image.id);selection()}});grid.append(el('div',{class:'library-card'},el('label',{class:'library-check'},check),card(image.id)))}$('#load-more').hidden=!cursor}finally{if(request===revision&&route===state.route)$('#load-more').disabled=false}}
export async function show(){revision++;state.images={};selected.clear();cursor=null;const box=$('#library');box.replaceChildren(el('div',{class:'row'},el('div',{class:'grow'},el('h2',{},'Your image library'),el('p',{class:'muted'},'Every image, across all your chats.')),el('select',{'aria-label':'Filter images',value:filter,onchange:safe(async e=>{revision++;filter=e.target.value;cursor=null;$('#library-grid').replaceChildren();await load()})},el('option',{value:''},'All images'),el('option',{value:'favorites'},'Favorites'))),el('div',{id:'library-grid',class:'library-grid'}),button('Load more',safe(load),{id:'load-more',hidden:true}),el('div',{id:'selection-bar',class:'selection-bar',hidden:true}));await load()}
