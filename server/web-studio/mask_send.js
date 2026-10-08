import {el} from './dom.js';
import {api} from './api.js';
import {send} from './submit.js';

export function sendEdit(image,canvas,instruction){
 return send('Edit the painted area of this image: '+instruction,async()=>{
  const output=el('canvas',{width:image.width,height:image.height});
  const context=output.getContext('2d');
  context.fillStyle='black';context.fillRect(0,0,output.width,output.height);
  context.drawImage(canvas,0,0);
  const blob=await new Promise(resolve=>output.toBlob(resolve));
  const form=new FormData();form.append('file',blob,'edit-area.png');
  const mask=await api('/api/uploads?kind=mask&source='+image.id,'POST',form);
  return [image,mask];
 });
}
