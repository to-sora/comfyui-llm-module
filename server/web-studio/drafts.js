import {$,toast} from './dom.js';
import {state,on,emit} from './state.js';
const key=id=>'studio.draft.'+(id||'new');
let restoring=false;
export function save(){if(restoring||!state.ready||state.routing)return;try{localStorage.setItem(key(state.chat?.id),JSON.stringify({text:$('#prompt').value,attachments:state.attachments}))}catch{toast('The browser could not save this draft')}}
export function restore(){restoring=true;try{const value=JSON.parse(localStorage.getItem(key(state.chat?.id))||'{}');$('#prompt').value=value.text||'';state.attachments=value.attachments||[];emit('attachments');$('#prompt').dispatchEvent(new Event('input'))}catch{localStorage.removeItem(key(state.chat?.id))}finally{restoring=false}}
export function clear(id){localStorage.removeItem(key(id))}
export function init(){$('#prompt').addEventListener('input',save);on('attachments',save);window.addEventListener('pagehide',save);window.addEventListener('beforeunload',save)}
