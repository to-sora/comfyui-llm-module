import {state,emit,on} from './state.js';
import {$,el,button,dialog,safe} from './dom.js';
import {api} from './api.js';
import {disconnect,connect,refresh} from './stream.js';
let opening=0,listing=0;
export async function list(){const request=++listing,data=await api('/api/chats');if(request!==listing)return;state.chats=data.chats;const current=state.chats.find(c=>c.id===state.chat?.id);if(current){state.chat.title=current.title;$('#chat-title').textContent=current.title}const box=$('#chat-list');box.replaceChildren();let group='';for(const c of state.chats){const label=new Date(c.updated*1000).toLocaleDateString();if(label!==group){box.append(el('div',{class:'date-label'},label));group=label}box.append(el('a',{href:'/chats/'+c.id,class:'chat-link'+(state.chat?.id===c.id?' active':''),'data-route':''},el('span',{class:'grow'},c.title),c.running?el('small',{},'working'):null))}}
export async function create(){const c=await api('/api/chats','POST',{});emit('navigate','/chats/'+c.id);return c}
function reset(chat){Object.assign(state,{chat,messages:[],runs:{},images:{},attachments:[],cursor:0});$('#chat-title').textContent=chat?.title||'New chat';emit('attachments');emit('thread')}
export function clear(){opening++;disconnect();reset(null)}
export async function open(id){const request=++opening;disconnect();const chat=id?await api('/api/chats/'+id):null;if(request!==opening)return;reset(chat);if(id){await refresh();if(request!==opening)return;connect()}await list()}
export function options(){if(!state.chat)return;const chat=state.chat;const input=el('input',{value:chat.title,'aria-label':'Chat title',maxLength:100});const box=el('div',{},el('label',{},'Chat title',input),button('Save title',safe(async()=>{await api('/api/chats/'+chat.id,'PATCH',{title:input.value});$('#dialog').close();await list()}),{class:'primary'}),el('p',{class:'muted'},'Deleting a chat keeps its images in Library.'),button('Delete chat',()=>{box.replaceChildren(el('p',{},'Delete this conversation? This cannot be undone.'),button('Delete',safe(async()=>{await api('/api/chats/'+chat.id,'DELETE');$('#dialog').close();emit('navigate','/')}),{class:'danger'}))},{class:'danger'}));dialog('Chat options',box)}
on('chats',safe(list));
