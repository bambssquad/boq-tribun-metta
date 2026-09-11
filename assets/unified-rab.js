(()=>{
 const frame=document.getElementById('rab-full-frame'),full=document.getElementById('rab-full-panel'),quantity=document.getElementById('rab-quantity-panel'),status=document.getElementById('rab-frame-status');
 const select=mode=>{full.hidden=mode!=='full';quantity.hidden=mode!=='quantity';const labor=document.getElementById('rab-labor-panel');if(labor)labor.hidden=mode!=='labor';const revision=document.getElementById('rab-revision-panel');if(revision)revision.hidden=mode!=='revision';document.querySelectorAll('[data-rab-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.rabMode===mode)));if(mode==='full')frame.contentWindow?.postMessage({type:'metta-rab-measure'},location.origin);};
 document.querySelectorAll('[data-rab-mode]').forEach(b=>b.addEventListener('click',()=>select(b.dataset.rabMode)));
 const route=()=>{if(['#boq','#penawaran'].includes(location.hash)){select('quantity');if(location.hash==='#penawaran')document.getElementById('rincian-penawaran').open=true;}else if(location.hash==='#rab-11sep'){select('revision');document.getElementById('anggaran')?.scrollIntoView?.();}else if(['#anggaran','#fastener-rab','#penawaran-r04'].includes(location.hash))select('full');};
 window.addEventListener('hashchange',route);route();
 document.querySelectorAll('a[href="#anggaran"]').forEach(a=>a.addEventListener('click',()=>select('full')));
 window.addEventListener('message',e=>{if(e.origin!==location.origin||e.source!==frame.contentWindow||e.data?.type!=='metta-rab-height')return;const h=e.data.height;if(Number.isFinite(h)&&h>=100&&h<=200000){frame.style.height=Math.ceil(h+16)+'px';status.hidden=true;}});
 frame.addEventListener('load',()=>frame.contentWindow?.postMessage({type:'metta-rab-measure'},location.origin));
})();
