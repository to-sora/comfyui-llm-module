import {$,safe,toast} from './dom.js';
import {api} from './api.js';
import {state,emit,on} from './state.js';
import * as chats from './chats.js';
import * as composer from './composer.js';
import * as uploads from './uploads.js';
import * as debug from './debug.js';
import * as settings from './settings.js';
import * as locale from './locale.js';
import {route,navigate} from './navigation.js';
import * as drafts from './drafts.js';
import {init as initFeatures} from './features.js';
import {connectGlobal} from './global_stream.js';
import './thread.js';
import './connection.js';
import './mask.js';
import {closeSidebar,toggleSidebar} from './sidebar_focus.js';
async function start(){await locale.init();state.boot=await api('/api/bootstrap');locale.apply(state.boot.settings);$('#debug').hidden=!state.boot.settings?.technical;composer.init();uploads.init();drafts.init();initFeatures();$('#new-chat').onclick=safe(chats.create);$('#menu').onclick=toggleSidebar;$('#close-sidebar').onclick=closeSidebar;$('#chat-menu').onclick=chats.options;$('#debug').onclick=safe(()=>debug.show());$('#settings').onclick=settings.show;document.addEventListener('click',e=>{const a=e.target.closest('a[data-route],a.brand');if(!a||e.ctrlKey||e.metaKey||e.shiftKey)return;e.preventDefault();safe(navigate)(a.getAttribute('href'))});on('navigate',safe(navigate));window.onpopstate=safe(route);connectGlobal();emit('connection',{connected:state.boot.connected,message:state.boot.error});await route();state.ready=true;composer.controls();$('#composer').removeAttribute('aria-busy')}
start().catch(e=>{toast(e.message);$('#connection').textContent=e.message});
