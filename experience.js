(()=>{
const track=document.querySelector('.drawing-track'),cards=[...document.querySelectorAll('.drawing-card')];
const dialog=document.getElementById('drawing-dialog');let active=0,opener=null;
const drawingPanZoom=createDrawingPanZoom(document.getElementById('drawing-viewport'),document.getElementById('drawing-large'),{
 plus:document.getElementById('drawing-zoom-in'),minus:document.getElementById('drawing-zoom-out'),
 reset:document.getElementById('drawing-reset'),level:document.getElementById('drawing-zoom-level')
});
function show(i){active=(i+DRAWING_DATA.length)%DRAWING_DATA.length;const d=DRAWING_DATA[active];
 document.getElementById('drawing-title').textContent=d.code+' / '+d.title;
 const img=document.getElementById('drawing-large');img.src=d.svg;img.alt=d.title;
 document.getElementById('drawing-note').textContent=d.notes.join(' ');
 document.getElementById('drawing-dxf').href=d.dxf;document.getElementById('drawing-svg').href=d.svg;
 drawingPanZoom.reset();
}
document.querySelectorAll('[data-drawing]').forEach(b=>b.addEventListener('click',()=>{opener=b;show(Number(b.dataset.drawing));dialog.showModal();}));
document.getElementById('drawing-close').onclick=()=>dialog.close();
dialog.addEventListener('close',()=>opener?.focus());
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
document.getElementById('drawing-prev').onclick=()=>show(active-1);
document.getElementById('drawing-next').onclick=()=>show(active+1);
dialog.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();show(active+1)}if(e.key==='ArrowLeft'){e.preventDefault();show(active-1)}});
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{
 const category=b.dataset.filter;
 document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
 cards.forEach(c=>c.hidden=category!=='Semua'&&c.dataset.category!==category);
 document.getElementById('gallery-count').textContent='('+cards.filter(c=>!c.hidden).length+')';track.scrollTo({left:0});
}));
function step(n){const c=cards.find(c=>!c.hidden);track.scrollBy({left:n*(c.getBoundingClientRect().width+30),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
document.getElementById('gallery-prev').onclick=()=>step(-1);document.getElementById('gallery-next').onclick=()=>step(1);
track.addEventListener('keydown',e=>{if(e.target!==track)return;if(e.key==='ArrowRight'){e.preventDefault();step(1)}if(e.key==='ArrowLeft'){e.preventDefault();step(-1)}});
document.querySelectorAll('[data-index]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();document.querySelector('[data-filter="Semua"]').click();cards[Number(a.dataset.index)].scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'nearest',inline:'center'});}));
const observer=new IntersectionObserver(entries=>{entries.forEach(e=>{document.querySelector('[data-index="'+cards.indexOf(e.target)+'"]')?.classList.toggle('current',e.isIntersecting);});},{root:track,threshold:.55});cards.forEach(c=>observer.observe(c));
let ticking=false;addEventListener('scroll',()=>{if(ticking)return;ticking=true;requestAnimationFrame(()=>{document.body.classList.toggle('scrolled',scrollY>100);ticking=false;});},{passive:true});
})();
