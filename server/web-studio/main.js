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
async function route(){const sequence=++state.route;state.routing=true;state.routeError=null;composer.controls();try{if(state.path&&state.path!==location.pathname){$('#prompt').value='';$('#prompt').style.height='auto'}state.path=location.pathname;viewer.close();closeSidebar();const path=location.pathname;const lib=path==='/library';$('#library').hidden=!lib;$('#conversation').hidden=lib;$('#chat-menu').hidden=lib;disconnect();if(lib){chats.clear();$('#chat-title').textContent='Library';await library.show();await chats.list()}else{const match=path.match(/^\/chats\/([0-9A-Z]{26})$/);await chats.open(match?.[1]);empty.render()}}catch(error){if(sequence!==state.route)return;state.routeError=error.message;throw error}finally{if(sequence===state.route){state.routing=false;composer.controls()}}}
async function navigate(value){const path=typeof value==='string'?value:value.path;history.pushState({},'',path);const sequence=state.route+1;await route();if(sequence!==state.route)return;if(value.attachments){state.attachments=value.attachments;emit('attachments');emit('compose',value.text||'')}}
async function start(){await locale.init();state.boot=await api('/api/bootstrap');locale.apply(state.boot.settings);$('#debug').hidden=!state.boot.settings?.technical;composer.init();uploads.init();$('#new-chat').onclick=safe(chats.create);$('#menu').onclick=toggleSidebar;$('#close-sidebar').onclick=closeSidebar;$('#chat-menu').onclick=chats.options;$('#debug').onclick=safe(()=>debug.show());$('#settings').onclick=settings.show;document.addEventListener('click',e=>{const a=e.target.closest('a[data-route],a.brand');if(!a||e.ctrlKey||e.metaKey||e.shiftKey)return;e.preventDefault();safe(navigate)(a.getAttribute('href'))});on('navigate',safe(navigate));window.onpopstate=safe(route);connectGlobal();emit('connection',{connected:state.boot.connected,message:state.boot.error});await route();state.ready=true;composer.controls();$('#composer').removeAttribute('aria-busy')}
start().catch(e=>{toast(e.message);$('#connection').textContent=e.message});
