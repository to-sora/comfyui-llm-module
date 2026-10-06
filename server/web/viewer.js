import{S,$,selected,url,el,select}from'./state.js';
import*as mask from'./mask.js';
import{render as lineage}from'./lineage.js';
let shown=null,zoom=1,x=0,y=0,drag=null;
function transform(){$('stage').style.transform=`translate(-50%,-50%) translate(${x}px,${y}px) scale(${zoom})`;}
function fit(){const i=selected();if(!i)return;zoom=Math.min(($('viewport').clientWidth-20)/i.width,($('viewport').clientHeight-20)/i.height);x=y=0;transform();}
function compare(){const enabled=$('compare').checked;$('before-image').style.display=enabled?'block':'none';$('main-image').style.clipPath=enabled?`inset(0 0 0 ${$('compare-range').value}%)`:'';}
export function init(){mask.init();$('fit').onclick=fit;$('zoom-in').onclick=()=>{zoom*=1.25;transform();};$('zoom-out').onclick=()=>{zoom/=1.25;transform();};$('compare').onchange=compare;$('compare-range').oninput=compare;
const v=$('viewport');v.onpointerdown=e=>{if(!selected()||mask.enabled())return;drag=[e.clientX-x,e.clientY-y];v.setPointerCapture(e.pointerId);};v.onpointermove=e=>{if(drag){x=e.clientX-drag[0];y=e.clientY-drag[1];transform();}};v.onpointerup=()=>drag=null;v.onwheel=e=>{if(!selected())return;e.preventDefault();zoom*=e.deltaY>0?.9:1.1;transform();};window.addEventListener('resize',fit);S.refreshers.push(render);}
function render(){const i=selected();if(!i){$('stage').hidden=true;$('empty').hidden=false;shown=null;return;}$('empty').hidden=true;$('stage').hidden=false;$('image-title').textContent=`Image #${i.id} · ${i.operation}${i.final?' · Final':''}`;$('image-size').textContent=`${i.width} × ${i.height}${i.readonly?' · Shared, read-only':''}`;
const key=S.sid+':'+i.id;if(key!==shown){shown=key;$('stage').style.width=i.width+'px';$('stage').style.height=i.height+'px';$('main-image').src=url(i.id);mask.reset(i.width,i.height);fit();}
const parent=S.data.images.find(p=>i.parents?.includes(p.id));$('compare').disabled=!parent;if(parent)$('before-image').src=url(parent.id);else $('compare').checked=false;compare();$('mask-tools').hidden=false;
$('metadata').textContent=JSON.stringify(i,null,2);lineage(i);
const review=S.data.chats.filter(c=>c.images?.includes(i.id)&&c.response).at(-1);$('inspection').hidden=!review;if(review)$('inspection').textContent=review.response;}
