'use strict';
const MettaPlan=(()=>{
 const date=s=>new Date(s+'T12:00:00Z'),iso=d=>d.toISOString().slice(0,10);
 const valid=s=>/^\d{4}-\d{2}-\d{2}$/.test(s)&&Number.isFinite(+date(s))&&iso(date(s))===s&&+s.slice(0,4)>=2000&&+s.slice(0,4)<=2100;
 const work=(d,w)=>d.getUTCDay()!==0&&(w===6||d.getUTCDay()!==6);
 function day(s,n,w=5){let d=date(s);while(!work(d,w))d.setUTCDate(d.getUTCDate()+1);for(let i=0;i<n;){d.setUTCDate(d.getUTCDate()+1);if(work(d,w))i++;}return iso(d);}
 function offset(s,t,w){t=day(t,0,w);let i=0,d=date(day(s,0,w));while(i<3650&&iso(d)<t){d.setUTCDate(d.getUTCDate()+1);if(work(d,w))i++;}return i;}
 const defaults=()=>({start:new Date().toLocaleDateString('sv-SE'),week:5,tasks:[['Survei & pengukuran',2],['Shop drawing & persetujuan',4],['Pengadaan material',5],['Pemotongan & pengeboran',4],['Tekuk pelat & fabrikasi modul',5],['Persiapan permukaan & cat',4],['Pengiriman & persiapan lokasi',2],['Ereksi, baut & pemasangan panel',5],['Finishing & serah terima',2]].reduce((a,[name,duration])=>{a.push({name,duration,offset:a.reduce((n,t)=>n+t.duration,0)});return a;},[])});
 return {day,offset,valid,defaults};
})();
if(typeof module!=='undefined')module.exports=MettaPlan;
if(typeof document!=='undefined')(()=>{
 const $=id=>document.getElementById(id),key='metta-execution-v1',esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));let state=MettaPlan.defaults(),view='both';
 try{const v=JSON.parse(localStorage.getItem(key));if(v&&MettaPlan.valid(v.start)&&[5,6].includes(v.week)&&Array.isArray(v.tasks)&&v.tasks.length===9&&v.tasks.every(t=>typeof t.name==='string'&&t.name.length<=100&&Number.isInteger(t.duration)&&t.duration>=1&&t.duration<=365&&Number.isInteger(t.offset)&&t.offset>=0&&t.offset<=3650))state=v;}catch{}
 const save=()=>{try{localStorage.setItem(key,JSON.stringify(state));}catch{}},when=n=>MettaPlan.day(state.start,n,state.week);
 function render(){
  const scroll=$('plan-cards').scrollLeft;$('plan-start').value=state.start;$('plan-week').value=state.week;
  const total=Math.max(...state.tasks.map(t=>t.offset+t.duration));$('plan-summary').textContent=total+' hari kerja · '+when(0)+' sampai '+when(total-1)+' · estimasi dapat diedit';
  $('plan-cards').innerHTML=state.tasks.map((t,i)=>`<article class="plan-card"><span class="plan-number">${String(i+1).padStart(2,'0')}</span><label>Tahap<input data-task="${i}" data-field="name" maxlength="100" value="${esc(t.name)}"></label><label>Mulai<input type="date" data-task="${i}" data-field="date" min="${when(0)}" value="${when(t.offset)}"></label><label>Durasi hari kerja<input type="number" min="1" max="365" data-task="${i}" data-field="duration" value="${t.duration}"></label><p>Selesai <b>${when(t.offset+t.duration-1)}</b></p></article>`).join('');$('plan-cards').scrollLeft=scroll;
  const width=Math.max(840,total*30),scale=width/total;let ticks='';for(let i=0;i<total;i+=Math.max(1,Math.ceil(total/18)))ticks+=`<span style="left:${i*scale}px">${when(i).slice(5)}</span>`;
  $('plan-gantt').innerHTML=`<div class="gantt-inner" style="width:${width+220}px"><div class="gantt-axis" style="margin-left:220px;width:${width}px">${ticks}</div>${state.tasks.map((t,i)=>`<div class="gantt-row"><strong>${esc(t.name)}</strong><div class="gantt-track" style="width:${width}px"><button class="gantt-bar" data-bar="${i}" style="left:${t.offset*scale}px;width:${Math.max(28,t.duration*scale)}px" aria-label="${esc(t.name)}, ${when(t.offset)}, ${t.duration} hari kerja. Panah kiri kanan menggeser satu hari kerja.">${t.duration} hari</button></div></div>`).join('')}</div>`;
  $('plan-gantt').dataset.scale=scale;
 }
 document.querySelectorAll('[data-plan-view]').forEach(b=>b.addEventListener('click',()=>{view=b.dataset.planView;document.querySelectorAll('[data-plan-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));$('plan-card-panel').hidden=view==='gantt';$('plan-gantt-panel').hidden=view==='cards';}));
 $('plan-start').addEventListener('change',e=>{if(MettaPlan.valid(e.target.value)){state.start=e.target.value;save();}render();});$('plan-week').addEventListener('change',e=>{state.week=+e.target.value;save();render();});
 $('plan-cards').addEventListener('change',e=>{if(!e.target.dataset.field)return;const t=state.tasks[+e.target.dataset.task],f=e.target.dataset.field,v=e.target.value;if(f==='name')t.name=v.trim().slice(0,100)||t.name;if(f==='duration')t.duration=Math.min(365,Math.max(1,Math.round(+v)||1));if(f==='date'&&MettaPlan.valid(v))t.offset=MettaPlan.offset(state.start,v,state.week);save();render();});
 const shift=(i,n)=>{state.tasks[i].offset=Math.min(3650,Math.max(0,n));save();render();};
 $('plan-gantt').addEventListener('keydown',e=>{const b=e.target.closest('[data-bar]');if(!b||!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();const i=+b.dataset.bar;shift(i,state.tasks[i].offset+(e.key==='ArrowRight'?1:-1));$('plan-gantt').querySelector(`[data-bar="${i}"]`).focus();});
 let drag;
 $('plan-gantt').addEventListener('pointerdown',e=>{const b=e.target.closest('[data-bar]');if(!b)return;drag={id:e.pointerId,x:e.clientX,offset:state.tasks[+b.dataset.bar].offset,i:+b.dataset.bar,b};b.setPointerCapture(e.pointerId);});
 $('plan-gantt').addEventListener('pointermove',e=>{if(drag&&e.pointerId===drag.id)drag.b.style.transform=`translateX(${e.clientX-drag.x}px)`;});
 $('plan-gantt').addEventListener('pointerup',e=>{if(!drag||e.pointerId!==drag.id)return;const d=drag;drag=null;shift(d.i,d.offset+Math.round((e.clientX-d.x)/+$('plan-gantt').dataset.scale));});$('plan-gantt').addEventListener('pointercancel',()=>{drag=null;render();});
 const cards=$('plan-cards');$('plan-prev').onclick=()=>cards.scrollBy({left:-cards.clientWidth*.8,behavior:'smooth'});$('plan-next').onclick=()=>cards.scrollBy({left:cards.clientWidth*.8,behavior:'smooth'});
 cards.addEventListener('wheel',e=>{if(e.target.closest('input,select')||Math.abs(e.deltaX)>Math.abs(e.deltaY))return;const can=e.deltaY>0?cards.scrollLeft<cards.scrollWidth-cards.clientWidth-1:cards.scrollLeft>0;if(can){e.preventDefault();cards.scrollLeft+=e.deltaY;}},{passive:false});
 let pan;cards.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'||e.target.closest('input,button,select'))return;pan={x:e.clientX,left:cards.scrollLeft};cards.setPointerCapture(e.pointerId);});cards.addEventListener('pointermove',e=>{if(pan)cards.scrollLeft=pan.left+pan.x-e.clientX;});cards.addEventListener('pointerup',()=>pan=null);cards.addEventListener('pointercancel',()=>pan=null);
 $('plan-reset').onclick=()=>{state=MettaPlan.defaults();save();render();};render();
})();
