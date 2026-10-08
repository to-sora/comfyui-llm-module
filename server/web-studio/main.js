import {$,safe,toast} from './dom.js';
import {api} from './api.js';
import {state,emit,on} from './state.js';
import * as chats from './chats.js';
import * as composer from './composer.js';
import * as uploads from './uploads.js';
import * as viewer from './viewer.js';
import * as library from './library.js';
import * as debug from './debug.js';
import * as settings from './settings.js';
import * as empty from './empty.js';
import * as locale from './locale.js';
import {disconnect} from './stream.js';
import {connectGlobal} from './global_stream.js';
import './thread.js';
import './connection.js';
import './mask.js';
import {closeSidebar,toggleSidebar} from './sidebar_focus.js';
async function route(){viewer.close();closeSidebar();const path=location.pathname;const lib=path==='/library';$('#library').hidden=!lib;$('#conversation').hidden=lib;$('#chat-menu').hidden=lib;disconnect();if(lib){state.chat=null;$('#chat-title').textContent='Library';await library.show();await chats.list()}else{const match=path.match(/^\/chats\/([0-9A-Z]{26})$/);await chats.open(match?.[1]);empty.render()}}
async function navigate(value){const path=typeof value==='string'?value:value.path;history.pushState({},'',path);await route();if(value.attachments){state.attachments=value.attachments;emit('attachments');emit('compose',value.text||'')}}
async function start(){await locale.init();state.boot=await api('/api/bootstrap');locale.apply(state.boot.settings);$('#debug').hidden=!state.boot.settings?.technical;composer.init();uploads.init();$('#new-chat').onclick=safe(chats.create);$('#menu').onclick=toggleSidebar;$('#close-sidebar').onclick=closeSidebar;$('#chat-menu').onclick=chats.options;$('#debug').onclick=safe(()=>debug.show());$('#settings').onclick=settings.show;document.addEventListener('click',e=>{const a=e.target.closest('a[data-route],a.brand');if(!a||e.ctrlKey||e.metaKey||e.shiftKey)return;e.preventDefault();safe(navigate)(a.getAttribute('href'))});on('navigate',safe(navigate));window.onpopstate=safe(route);connectGlobal();emit('connection',{connected:state.boot.connected,message:state.boot.error});await route();$('#send').disabled=false;$('#composer').removeAttribute('aria-busy')}
start().catch(e=>{toast(e.message);$('#connection').textContent=e.message});
