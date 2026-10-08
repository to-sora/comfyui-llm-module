import {state,emit} from './state.js';
import {api} from './api.js';
let source;
export function connectGlobal(){
 source?.close();source=new EventSource(`/api/events?cursor=${state.boot.cursor||0}`);
 for(const kind of ['system.status','queue.changed','chats.changed'])source.addEventListener(kind,async event=>{
  const data=JSON.parse(event.data);
  if(kind==='system.status'){
   if(data.connected)try{state.boot=await api('/api/bootstrap')}catch{}
   state.boot.error=data.connected?null:data.message;emit('connection',data);
  }else emit(kind==='queue.changed'?'queue':'chats',data);
 });
 source.onerror=()=>emit('connection',{connected:false,message:'Reconnecting to Studio…'});
 source.onopen=()=>emit('connection',{connected:!state.boot.error,message:state.boot.error});
}
window.addEventListener('pagehide',()=>source?.close());
window.addEventListener('beforeunload',()=>source?.close());
