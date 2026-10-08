export const state={chat:null,messages:[],runs:{},images:{},chats:[],attachments:[],boot:{},cursor:0,view:null,ready:false,routing:false,routeError:null,sending:false,uploads:{},route:0};
const events=new EventTarget();
export function emit(type,data){events.dispatchEvent(new CustomEvent(type,{detail:data}))}
export function on(type,fn){events.addEventListener(type,e=>fn(e.detail))}
export function active(){return Object.values(state.runs).find(r=>['queued','running'].includes(r.status))}
export function uploadsPending(){return state.uploads[state.route]||0}
