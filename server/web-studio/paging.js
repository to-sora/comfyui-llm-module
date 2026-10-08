import {state,emit} from './state.js';
import {api} from './api.js';
import {$} from './dom.js';
export function merge(data){const older=state.messages.filter(m=>data.messages[0]&&m.id<data.messages[0].id);return {...data,messages:[...older,...data.messages],runs:{...state.runs,...data.runs},images:{...state.images,...data.images},before:older.length?state.before:data.before}}
export async function earlier(){if(!state.before)return;const chat=state.chat.id;const before=state.before;const data=await api(`/api/chats/${chat}/messages?before=${before}`);if(state.chat?.id!==chat)return;const pane=$('#thread'),height=pane.scrollHeight;const ids=new Set(state.messages.map(m=>m.id));state.messages=[...data.messages.filter(m=>!ids.has(m.id)),...state.messages];Object.assign(state.runs,data.runs);Object.assign(state.images,data.images);state.before=data.before;emit('thread');pane.scrollTop=pane.scrollHeight-height}
