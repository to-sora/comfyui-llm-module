import {$} from './dom.js';
import {state,emit} from './state.js';
import * as chats from './chats.js';
import * as composer from './composer.js';
import * as viewer from './viewer.js';
import * as library from './library.js';
import * as empty from './empty.js';
import * as drafts from './drafts.js';
import {disconnect} from './stream.js';
import {closeSidebar} from './sidebar_focus.js';
export async function route(){drafts.save();const sequence=++state.route;state.routing=true;state.routeError=null;composer.controls();try{if(state.path&&state.path!==location.pathname){$('#prompt').value='';$('#prompt').style.height='auto'}state.path=location.pathname;viewer.close();closeSidebar();const path=location.pathname;const lib=path==='/library';$('#library').hidden=!lib;$('#conversation').hidden=lib;$('#chat-menu').hidden=lib;disconnect();if(lib){chats.clear();$('#chat-title').textContent='Library';await library.show();await chats.list()}else{const match=path.match(/^\/chats\/([0-9A-Z]{26})$/);await chats.open(match?.[1]);empty.render()}}catch(error){if(sequence!==state.route)return;state.routeError=error.message;throw error}finally{if(sequence===state.route){state.routing=false;drafts.restore();composer.controls()}}}
export async function navigate(value){const path=typeof value==='string'?value:value.path;history.pushState({},'',path);const sequence=state.route+1;await route();if(sequence!==state.route)return;if(value.attachments){state.attachments=value.attachments;emit('attachments');emit('compose',value.text||'')}}
