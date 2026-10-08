export const state={chat:null,messages:[],runs:{},images:{},chats:[],attachments:[],boot:{},cursor:0,view:null};
const events=new EventTarget();
export function emit(type,data){events.dispatchEvent(new CustomEvent(type,{detail:data}))}
export function on(type,fn){events.addEventListener(type,e=>fn(e.detail))}
export function active(){return Object.values(state.runs).find(r=>['queued','running'].includes(r.status))}
