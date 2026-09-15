(() => {
  'use strict';
  const host=document.querySelector('#gambar');if(!host)return;
  const root=document.createElement('section');root.id='metta-detailed-drawings';
  root.innerHTML=`<h3>Gambar teknik · jelajahi detail</h3><p>LOD 100 / koordinasi konseptual. Dimensi arsip dan usulan ditandai; belum untuk fabrikasi.</p><div class="md-toolbar"><label>Lembar <select aria-label="Pilih lembar gambar"></select></label><button data-act="out" aria-label="Perkecil gambar">−</button><button data-act="in" aria-label="Perbesar gambar">+</button><button data-act="fit">Pas layar</button><button data-act="full">Layar penuh</button><a target="_blank" rel="noopener">Buka SVG</a><output aria-live="polite">100%</output></div><div class="md-stage" tabindex="0" aria-label="Gambar teknik. Seret untuk geser; tombol plus dan minus untuk zoom."><img draggable="false" alt="Lembar gambar teknik METTA"></div><p class="md-hint">Seret untuk menggeser · roda mouse untuk zoom · tombol + / − untuk zoom · 0 untuk pas layar</p>`;
  host.prepend(root);
  const select=root.querySelector('select'),stage=root.querySelector('.md-stage'),img=root.querySelector('img'),link=root.querySelector('a'),status=root.querySelector('output');
  let manifest,version='v1',zoom=1,x=0,y=0,drag=null;
  function paint(){img.style.transform=`translate(${x}px,${y}px) scale(${zoom})`;status.textContent=Math.round(zoom*100)+'%';}
  function fit(){zoom=1;x=y=0;paint();}
  function scale(f){zoom=Math.max(.5,Math.min(12,zoom*f));paint();}
  function sheet(){const item=manifest.versions[version][select.selectedIndex];img.src='assets/drawings/'+item.file;img.alt=item.title+' / '+version.toUpperCase();link.href=img.src;fit();}
  function setVersion(v){version=v==='v2'?'v2':'v1';root.dataset.version=version;if(!manifest)return;const old=select.selectedIndex;select.replaceChildren(...manifest.versions[version].map(s=>{const o=document.createElement('option');o.textContent=version.toUpperCase()+' · '+s.title;return o;}));select.selectedIndex=Math.max(0,Math.min(old,select.options.length-1));sheet();}
  select.addEventListener('change',sheet);
  root.addEventListener('click',e=>{const a=e.target.closest('[data-act]')?.dataset.act;if(a==='in')scale(1.3);if(a==='out')scale(1/1.3);if(a==='fit')fit();if(a==='full'){if(document.fullscreenElement)document.exitFullscreen();else root.requestFullscreen?.().catch(()=>{status.textContent='Layar penuh tidak tersedia';});}});
  stage.addEventListener('wheel',e=>{e.preventDefault();scale(e.deltaY<0?1.12:1/1.12);},{passive:false});
  stage.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,ox:x,oy:y};stage.setPointerCapture(e.pointerId);});
  stage.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;x=drag.ox+e.clientX-drag.x;y=drag.oy+e.clientY-drag.y;paint();});
  ['pointerup','pointercancel','lostpointercapture'].forEach(n=>stage.addEventListener(n,()=>drag=null));
  stage.addEventListener('keydown',e=>{if(['+','=','-','0'].includes(e.key)){e.preventDefault();if(e.key==='0')fit();else scale(e.key==='-'?1/1.3:1.3);}});
  window.MettaDrawings={setVersion};window.addEventListener('metta:version',e=>setVersion(e.detail.version));
  fetch('assets/drawings/manifest.json').then(r=>{if(!r.ok)throw Error('manifest');return r.json();}).then(m=>{manifest=m;setVersion(document.documentElement.dataset.mettaVersion||document.documentElement.dataset.siteVersion||version);}).catch(()=>{status.textContent='Gambar belum berhasil dimuat. Muat ulang halaman.';});
})();
