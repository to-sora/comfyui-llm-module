import {state,emit} from './state.js';
import {api} from './api.js';
import {merge} from './paging.js';
let source,loading=false,again=false,buffer=[],generation=0;
const kinds=['run.queued','message.delta','message.updated','tool.started','image.progress','image.preview','image.done','image.error','message.done','run.error','chat.summary','trace.changed'];
function apply(event){if(Number(event.lastEventId)<=state.cursor)return;state.cursor=Number(event.lastEventId);const d=JSON.parse(event.data);const kind=event.type;
if(kind==='message.delta'){const row=state.messages.find(m=>m.id===d.message_id);if(row){let last=row.parts.at(-1);if(last?.type!=='text'){last={type:'text',text:''};row.parts.push(last)}last.text+=d.text;emit('message',row.id)}}
else if(kind==='image.done'){state.images[d.image.id]=d.image;emit('image',d.image.id)}
else if(kind.startsWith('image.')){const row=state.images[d.image_id];if(row){row.progress={...row.progress,...d};emit('image',row.id)}}
else if(kind==='message.updated'||kind==='message.done')refresh();
else if(kind==='run.error'){if(state.runs[d.run_id])state.runs[d.run_id].error=d.message;emit('activity',d.message);refresh()}
else if(kind==='run.queued'){if(state.runs[d.id])Object.assign(state.runs[d.id],d);emit('queue',d)}
else if(kind==='tool.started'||kind==='chat.summary')emit('activity',d.message);
else if(kind==='trace.changed')emit('trace',d.run_id);
}
export async function refresh(){if(loading){again=true;return}if(!state.chat)return;loading=true;const id=state.chat.id,gen=generation;try{const data=await api(`/api/chats/${id}/messages`);if(gen!==generation)return;Object.assign(state,merge(data));emit('thread');const queued=buffer;buffer=[];for(const event of queued)apply(event)}catch(e){emit('connection',{connected:false,message:e.message})}finally{if(gen===generation){loading=false;if(again){again=false;refresh()}}}}
export function disconnect(){generation++;source?.close();source=null;loading=again=false;buffer=[]}
window.addEventListener('pagehide',disconnect);
window.addEventListener('beforeunload',disconnect);
export function connect(){source=new EventSource(`/api/chats/${state.chat.id}/events?cursor=${state.cursor}`);for(const kind of kinds)source.addEventListener(kind,e=>loading?buffer.push(e):apply(e));source.onerror=()=>emit('connection',{connected:false,message:'Reconnecting to Studio…'});source.onopen=()=>emit('connection',{connected:!state.boot.error,message:state.boot.error})}
