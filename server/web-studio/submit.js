import {state,emit,active,uploadsPending} from './state.js';
import {$} from './dom.js';
import {api} from './api.js';
import {open} from './chats.js';
import {refresh} from './stream.js';

export async function send(text,attachments=state.attachments){
 if(!state.ready||state.routing||state.routeError||state.sending||uploadsPending())throw Error('Please wait for the current action to finish');
 if(active())throw Error('Wait for this reply or stop it first');
 if(!text.trim()&&Array.isArray(attachments)&&!attachments.length)return;
 const origin=state.route;
 let chat=state.chat?.id;
 state.sending=true;emit('sending');
 try{
  const images=typeof attachments==='function'?await attachments():attachments;
  const ids=images.map(i=>i.id);
  if(!chat){
   chat=(await api('/api/chats','POST',{})).id;
   if(state.route===origin){
    state.route++;state.path='/chats/'+chat;history.pushState({},'',state.path);
    const held=state.attachments;
    await open(chat);
    if(state.chat?.id===chat){
     state.attachments=[...new Map([...held,...state.attachments].map(i=>[i.id,i])).values()];
     emit('attachments');$('#library').hidden=true;$('#conversation').hidden=false;$('#chat-menu').hidden=false;
    }
   }
  }
  await api(`/api/chats/${chat}/messages`,'POST',{text,attachments:ids});
  if(state.chat?.id!==chat)return;
  const prompt=$('#prompt');
  if(prompt.value===text){prompt.value='';prompt.style.height='auto'}
  state.attachments=state.attachments.filter(i=>!ids.includes(i.id));emit('attachments');
  await refresh();if(state.chat?.id===chat)prompt.focus();
 }finally{state.sending=false;emit('sending')}
}
