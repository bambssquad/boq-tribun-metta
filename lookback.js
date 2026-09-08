(()=>{
'use strict';
const $=s=>document.querySelector(s), cards=[...document.querySelectorAll('.archive-card')];
const stage=$('.archive-carousel'), track=$('.archive-track'), reduced=matchMedia('(prefers-reduced-motion: reduce)');
const menu=$('#archive-menu'), dialog=$('#sheet-dialog'), image=$('#sheet-image');
const pan=createDrawingPanZoom($('#sheet-viewport'),image,{plus:$('#sheet-plus'),minus:$('#sheet-minus'),reset:$('#sheet-reset'),level:$('#sheet-scale')});
let view='timeline', position=0,target=0,step=330,total=0,raf=0,drag=null, suppress=false, active=0, opener=null, zoomAnimation=null;
const wrap=(x,n)=>((x%n)+n)%n;
let brandTravel=0,brandTouchY=null;
function syncBrand(){document.body.dataset.brandCompact=String(view!=='timeline'||menu.open||dialog.open||brandTravel>=100||(window.scrollY||0)>40);}
function compactBrand(){brandTravel=160;syncBrand();}
function brandDelta(delta){brandTravel=Math.max(0,Math.min(180,brandTravel+delta));syncBrand();}
addEventListener('wheel',e=>{if(menu.open||dialog.open||e.ctrlKey||e.target?.closest('input,select,textarea'))return;brandDelta(e.deltaY*(e.deltaMode===1?18:e.deltaMode===2?innerHeight:1));},{passive:true});
addEventListener('scroll',syncBrand,{passive:true});
addEventListener('touchstart',e=>{brandTouchY=!menu.open&&!dialog.open&&e.touches.length===1?e.touches[0].clientY:null;},{passive:true});
addEventListener('touchmove',e=>{if(brandTouchY===null||menu.open||dialog.open||e.touches.length!==1)return;const y=e.touches[0].clientY;brandDelta(brandTouchY-y);brandTouchY=y;},{passive:true});
addEventListener('touchend',()=>brandTouchY=null,{passive:true});
addEventListener('touchcancel',()=>brandTouchY=null,{passive:true});
function layout(){step=cards[0].getBoundingClientRect().width+(innerWidth<=800?14:22);total=step*cards.length;render();}
function render(){
 if(view==='index'||view==='proyek')return;
 let closest=Infinity,index=0;
 const drift=target-position;
 cards.forEach((card,i)=>{
  const x=wrap(i*step-position+step,total)-step;
  const center=(x+step/2-innerWidth/2)/innerWidth;
  const surf=view==='surf';
  const y=surf?Math.sin(center*2.4)*Math.min(innerHeight*.19,160):0;
  const angle=reduced.matches?0:surf?Math.max(-65,Math.min(65,-center*55)):Math.max(-18,Math.min(18,drift*.055));
  card.style.transform=`translate3d(${x}px,${y}px,0) rotateY(${angle}deg)`;
  const distance=Math.abs(x+step/2-innerWidth/2);if(distance<closest){closest=distance;index=i;}
 });
 document.querySelectorAll('[data-jump]').forEach((b,i)=>b.classList.toggle('active',i===index));
 $('#current-sheet').textContent=METTA_DRAWINGS[index].code;
 active=index;
}
function tick(){raf=0;position+=(target-position)*(reduced.matches?1:.1);if(Math.abs(target-position)<.08)position=target;render();if(Math.abs(target-position)>.08)raf=requestAnimationFrame(tick);}
function wake(){if(!raf)raf=requestAnimationFrame(tick);}
function move(delta,collapse=true){if(view==='index'||view==='proyek'||dialog.open||menu.open)return;if(collapse)compactBrand();target+=delta;wake();}
function jump(index){let desired=index*step-(innerWidth-step)/2;desired+=Math.round((target-desired)/total)*total;target=desired;wake();}
function route(){
 const hash=location.hash.slice(1)||'timeline';
 if(['tiga-d','boq','anggaran','potong','material','lampiran','pelaksanaan','spek','revit-native','penawaran'].includes(hash)){location.replace('tools.html#'+hash);return;}
 view=['timeline','surf','index','proyek'].includes(hash)?hash:hash==='gambar'?'index':'timeline';
 const old=document.body.dataset.view;document.body.dataset.view=view;
 if(view==='timeline'&&old!==view)brandTravel=0;
 syncBrand();
 $('#proyek').hidden=view!=='proyek';$('.index-filter').hidden=view!=='index';
 cards.forEach(c=>c.hidden=false);$('#category').value='Semua';
 document.querySelectorAll('[data-view-link]').forEach(a=>{if(a.dataset.viewLink===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 if(menu.open)closeMenu();
 if(old!==view&&Element.prototype.animate&&!reduced.matches){$('.archive-logo').animate([{opacity:.2,transform:'translate(-50%, -18px)'},{opacity:1,transform:'translate(-50%, 0)'}],{duration:750,easing:'cubic-bezier(.19,1,.22,1)'});track.animate([{opacity:0,transform:'translateY(55px)'},{opacity:1,transform:'translateY(0)'}],{duration:850,easing:'cubic-bezier(.19,1,.22,1)'});}
 if(view==='index'||view==='proyek')window.scrollTo(0,0);
 requestAnimationFrame(layout);
}
function loadSheet(i){zoomAnimation?.cancel();active=wrap(i,METTA_DRAWINGS.length);const d=METTA_DRAWINGS[active];$('#sheet-title').textContent=d.code+' / '+d.title;image.src=d.svg;image.alt=d.title;$('#sheet-notes').textContent=d.notes.join(' ');$('#sheet-dxf').href=d.dxf;$('#sheet-svg').href=d.svg;pan.reset();}
function flip(from,to,src,reverse=false){
 if(reduced.matches||!Element.prototype.animate||!from.width||!to.width)return;
 zoomAnimation?.cancel();
 const ghost=document.createElement('img');ghost.className='flip-ghost';ghost.src=src;ghost.alt='';
 Object.assign(ghost.style,{left:to.left+'px',top:to.top+'px',width:to.width+'px',height:to.height+'px'});(dialog.open?dialog:document.body).append(ghost);
 image.style.opacity='0';
 const begin={transform:`translate(${from.left-to.left}px,${from.top-to.top}px) scale(${from.width/to.width},${from.height/to.height})`,opacity:1};
 const end={transform:'translate(0,0) scale(1,1)',opacity:1};
 zoomAnimation=ghost.animate([begin,end],{duration:850,easing:'cubic-bezier(.19,1,.22,1)'});
 const clear=()=>{ghost.remove();image.style.opacity='';zoomAnimation=null;};zoomAnimation.onfinish=clear;zoomAnimation.oncancel=clear;
}
function openSheet(index,button){if(suppress)return;compactBrand();opener=button;const from=button.getBoundingClientRect();loadSheet(index);dialog.showModal();requestAnimationFrame(()=>flip(from,$('#sheet-viewport').getBoundingClientRect(),image.src));}
function closeSheet(){zoomAnimation?.cancel();const from=$('#sheet-viewport').getBoundingClientRect();dialog.close();if(opener?.isConnected){const to=opener.getBoundingClientRect();if(to.bottom>0&&to.top<innerHeight)flip(from,to,image.src,true);opener.focus({preventScroll:true});}}
function closeMenu(){menu.close();$('#menu-toggle').setAttribute('aria-expanded','false');syncBrand();}
$('#menu-toggle').onclick=()=>{compactBrand();menu.showModal();$('#menu-toggle').setAttribute('aria-expanded','true');};$('#menu-close').onclick=closeMenu;
menu.addEventListener('close',()=>$('#menu-toggle').setAttribute('aria-expanded','false'));
menu.addEventListener('click',e=>{if(e.target.closest('a[href^="#"]'))closeMenu();});
$('#sheet-close').onclick=closeSheet;dialog.addEventListener('cancel',e=>{e.preventDefault();closeSheet();});dialog.addEventListener('close',()=>pan.reset());
$('#sheet-next').onclick=()=>loadSheet(active+1);$('#sheet-prev').onclick=()=>loadSheet(active-1);
dialog.addEventListener('keydown',e=>{if(e.target.closest('#sheet-viewport'))return;if(e.key==='ArrowRight'){e.preventDefault();loadSheet(active+1);}if(e.key==='ArrowLeft'){e.preventDefault();loadSheet(active-1);}});
cards.forEach((c,i)=>{const b=c.querySelector('button');b.onclick=()=>openSheet(i,b);b.addEventListener('focus',()=>{if(!dialog.open&&view!=='index')jump(i);});});
document.querySelectorAll('[data-jump]').forEach(b=>b.onclick=()=>{compactBrand();jump(+b.dataset.jump);});$('#previous').onclick=()=>move(-step);$('#next').onclick=()=>move(step);
$('#category').onchange=e=>cards.forEach(c=>c.hidden=e.target.value!=='Semua'&&c.dataset.category!==e.target.value);
stage.addEventListener('wheel',e=>{if(view==='index'||view==='proyek'||e.ctrlKey)return;e.preventDefault();move((Math.abs(e.deltaX)>Math.abs(e.deltaY)?e.deltaX:e.deltaY)*(e.deltaMode===1?18:e.deltaMode===2?innerWidth:1),false);},{passive:false});
stage.addEventListener('pointerdown',e=>{if(view==='index'||view==='proyek'||e.button!==0||!e.isPrimary)return;drag={id:e.pointerId,x:e.clientX,last:e.clientX,time:performance.now(),velocity:0,moved:false};suppress=false;target=position;});
stage.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const now=performance.now(),dx=e.clientX-drag.last;drag.velocity=dx/Math.max(8,now-drag.time)*16;drag.last=e.clientX;drag.time=now;if(Math.abs(e.clientX-drag.x)>5){drag.moved=true;stage.classList.add('dragging');stage.setPointerCapture(e.pointerId);}target-=dx;wake();});
function endDrag(e){if(!drag||drag.id!==e.pointerId)return;suppress=drag.moved;if(e.type!=='pointercancel')target-=Math.max(-70,Math.min(70,drag.velocity))*9;drag=null;if(stage.hasPointerCapture(e.pointerId))stage.releasePointerCapture(e.pointerId);stage.classList.remove('dragging');wake();setTimeout(()=>suppress=false,80);}
stage.addEventListener('pointerup',endDrag);stage.addEventListener('pointercancel',endDrag);stage.addEventListener('lostpointercapture',e=>{if(drag)endDrag(e);});
stage.addEventListener('dragstart',e=>e.preventDefault());
addEventListener('keydown',e=>{if(dialog.open||menu.open||view==='index'||view==='proyek'||e.target.closest('input,select,textarea'))return;if(['ArrowDown','PageDown'].includes(e.key)){e.preventDefault();brandDelta(160);}if(['ArrowUp','PageUp','Home'].includes(e.key)){e.preventDefault();brandTravel=0;syncBrand();}if(e.key==='ArrowRight'){e.preventDefault();move(step);}if(e.key==='ArrowLeft'){e.preventDefault();move(-step);}});
addEventListener('resize',layout,{passive:true});addEventListener('hashchange',route);reduced.addEventListener('change',()=>{zoomAnimation?.cancel();position=target;render();});
document.addEventListener('click',e=>{const a=e.target.closest('a[href^="tools.html"]');if(!a||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||e.button!==0||reduced.matches)return;e.preventDefault();document.body.classList.add('page-out');setTimeout(()=>location.assign(a.href),420);});
addEventListener('pageshow',()=>document.body.classList.remove('page-out'));
setTimeout(()=>$('.entry-mask')?.remove(),1500);route();layout();jump(0);
})();
