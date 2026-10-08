import {$,el,button,safe} from './dom.js';
import {on,state} from './state.js';
import {api} from './api.js';
export function render(data){if(!navigator.onLine)data={connected:false,message:'You are offline. Updates resume when you reconnect.'};const offline=$('#offline');offline.hidden=data.connected;const message=data.connected?'Ready':data.message||'Reconnecting to Studio…';$('#connection').textContent=message;$('#connection').dataset.connected=String(!!data.connected);if(!data.connected)offline.replaceChildren(el('span',{},message),button('Reconnect',safe(async()=>{const result=await api('/api/reconnect','POST',{});state.boot=await api('/api/bootstrap');render({connected:result.connected,message:result.error})})))}
on('connection',render);on('queue',value=>{if(value.active?.length)$('#connection').textContent='Working · '+(value.waiting?.length||0)+' waiting';else if(!state.boot.error)$('#connection').textContent='Ready'});

window.addEventListener('offline',()=>render({connected:false}));
window.addEventListener('online',()=>render({connected:!state.boot.error,message:state.boot.error}));
