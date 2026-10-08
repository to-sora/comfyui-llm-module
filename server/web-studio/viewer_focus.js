import {$} from './dom.js';
import {openPanel,releasePanel} from './panel_focus.js';
let closer;
export function sync(close=closer){closer=close;const panel=$('#viewer');if(!panel||!$('#debug-panel').hidden)return;const modal=!panel.hidden&&(innerWidth<=1000||document.body.classList.contains('viewer-full'));if(modal)openPanel(panel,close);else releasePanel(panel)}
window.addEventListener('resize',()=>sync());
