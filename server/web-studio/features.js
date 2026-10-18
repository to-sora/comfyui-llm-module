import {$,button,safe,toast} from './dom.js';
import {state,on,emit,active} from './state.js';
import {show as search} from './search.js';
import {show as backup} from './backup.js';
import {show as storage} from './storage.js';
import {archived} from './chat_options.js';
import {create} from './chats.js';
import {api} from './api.js';
let unread=0,installPrompt;
export function init(){const nav=$('.nav-bottom');nav.prepend(button('Search',search,{id:'search'}),button('Archived chats',safe(archived)),button('Storage',safe(storage)),button('Backup and restore',backup));if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e;nav.append(button('Install Studio',safe(async()=>{await installPrompt.prompt();installPrompt=null})))});on('finished',data=>{if(!document.hidden&&state.chat?.id===data.chat_id)return;unread++;document.title='('+unread+') Studio';navigator.setAppBadge?.(unread)?.catch(()=>{});toast(data.title+' · '+(data.status==='done'?'Finished':'Reply stopped'));if(state.boot.settings?.notifications&&'Notification' in window&&Notification.permission==='granted'){const n=new Notification(data.title,{body:data.status==='done'?'Your reply is ready.':'Your reply needs attention.',tag:data.run_id});n.onclick=()=>{window.focus();emit('navigate','/chats/'+data.chat_id);n.close()}}});document.addEventListener('visibilitychange',()=>{if(!document.hidden){unread=0;document.title='Studio';navigator.clearAppBadge?.()?.catch(()=>{})}});document.addEventListener('keydown',safe(async e=>{if(!(e.ctrlKey||e.metaKey))return;if(e.key.toLowerCase()==='k'){e.preventDefault();search()}else if(e.shiftKey&&e.key.toLowerCase()==='o'){e.preventDefault();await create()}else if(e.key==='.'&&active()){e.preventDefault();await api('/api/runs/'+active().id+'/cancel','POST',{})}}))}
