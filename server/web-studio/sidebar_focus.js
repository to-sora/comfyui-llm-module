import {$} from './dom.js';
import {openPanel,releasePanel} from './panel_focus.js';
export function closeSidebar(){document.body.classList.remove('sidebar-open');$('#menu').setAttribute('aria-expanded','false');releasePanel($('#sidebar'))}
export function toggleSidebar(){if(document.body.classList.contains('sidebar-open'))return closeSidebar();document.body.classList.add('sidebar-open');$('#menu').setAttribute('aria-expanded','true');openPanel($('#sidebar'),closeSidebar)}
window.addEventListener('resize',()=>{if(innerWidth>700)closeSidebar()});
