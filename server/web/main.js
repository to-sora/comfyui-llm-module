import{S,$,api,refresh,notice,on,options}from'./state.js';
import*as forms from'./forms.js';import*as models from'./models.js';import*as actions from'./actions.js';import*as viewer from'./viewer.js';import*as edits from'./edits.js';import*as history from'./history.js';import*as chat from'./chat.js';import*as jobs from'./jobs.js';
async function boot(){S.boot=await api('/bootstrap');S.sid=S.boot.active;await refresh();forms.init();models.init();models.load();actions.init();viewer.init();edits.init();history.init();chat.init();jobs.init();
const sessions=$('sessions');sessions.replaceChildren(...S.boot.sessions.map(s=>{const o=document.createElement('option');o.value=s.id;o.textContent=s.name;return o;}));sessions.value=S.sid;sessions.onchange=async()=>{try{await api('/sessions',{id:sessions.value});location.reload();}catch(e){notice(e.message);sessions.value=S.sid;}};
on('new-session',async()=>{await api('/sessions',{name:$('session-name').value.trim()||'Untitled'});location.reload();});
$('connection').textContent=S.boot.error?'Gateway unavailable':`${S.boot.capabilities?.profiles.length} LLMs · ${S.boot.capabilities?.checkpoints.length} SDXL models`;
if(S.boot.error)notice(S.boot.error);await refresh();poll();}
async function poll(){try{await refresh();}catch(e){notice('Connection: '+e.message);}setTimeout(poll,800);}
boot().catch(e=>notice(e.message));
