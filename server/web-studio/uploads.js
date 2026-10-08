import {state,emit,on} from './state.js';
import {$,el,button,safe,toast} from './dom.js';
import {api} from './api.js';
export function attach(image){if(state.attachments.some(i=>i.id===image.id))return;if(state.attachments.length>=8)throw Error('Attach up to eight images');state.attachments.push(image);emit('attachments')}
export async function upload(files,kind='upload'){
 if(!files.length)return;
 if(!state.ready||state.routing||state.routeError||state.sending)throw Error('Please wait for the current action to finish');
 const route=state.route,pending=state.uploads[route]||0;
 if(state.attachments.length+pending+files.length>8)throw Error('Attach up to eight images');
 state.uploads[route]=pending+files.length;emit('uploads');
 let last;
 try{
  for(const file of files){
   const form=new FormData();form.append('file',file,file.name||'image.png');
   last=await api('/api/uploads?kind='+kind,'POST',form);
   if(state.route===route)attach(last);
  }
  if(state.route!==route)toast('Uploaded images are saved in Library');
  return last;
 }finally{state.uploads[route]-=files.length;if(!state.uploads[route])delete state.uploads[route];emit('uploads')}
}
export function render(){const box=$('#attachments');box.replaceChildren(...state.attachments.map(image=>el('span',{class:'attachment'},el('img',{src:'/api/images/'+image.id+'/thumb',alt:''}),image.kind==='mask'?'Edit area':image.recipe?.name||'Image',button('×',()=>{state.attachments=state.attachments.filter(i=>i.id!==image.id);emit('attachments')},{'aria-label':'Remove attachment'}))))}
export function init(){const files=$('#files');$('#attach').onclick=()=>files.click();files.onchange=safe(async()=>{try{await upload([...files.files])}finally{files.value=''}});const composer=$('#composer');composer.addEventListener('dragover',e=>{e.preventDefault();composer.classList.add('drag')});composer.addEventListener('dragleave',()=>composer.classList.remove('drag'));document.addEventListener('drop',safe(async e=>{e.preventDefault();composer.classList.remove('drag');await upload([...e.dataTransfer.files])}));document.addEventListener('dragover',e=>e.preventDefault());$('#prompt').addEventListener('paste',safe(async e=>{const files=[...e.clipboardData.items].filter(i=>i.kind==='file').map(i=>i.getAsFile());if(files.length){e.preventDefault();await upload(files)}}));on('attachments',render)}
