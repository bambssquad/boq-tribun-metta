(()=>{
 'use strict';
 const $=id=>document.getElementById(id),key='metta-site-version-v1';let payload,payloads={},active,mesh='m20_25',sequence=0;
 const bar=document.createElement('section');bar.id='site-version-bar';bar.setAttribute('aria-label','Versi seluruh desain');
 bar.innerHTML='<strong>VERSI DESAIN</strong><button data-site-version="v1" aria-pressed="false">V1 · Awal</button><button data-site-version="v2" aria-pressed="false">V2 · Infill + mesh</button><label>Struktur V2 <select id="site-structure"><option value="baseline">Dasar</option><option value="a">A · Bantuan kolom beton</option><option value="c">C · Rangka mandiri</option></select></label><p id="site-version-status" role="status">Memuat pilihan model, gambar dan RAB…</p>';
 document.body.prepend(bar);
 const gallery=$('gambar'),oldGallery=document.createElement('div');oldGallery.id='v1-drawings';
 while(gallery.firstChild)oldGallery.append(gallery.firstChild);gallery.append(oldGallery);
 const v2=document.createElement('div');v2.id='v2-drawings';v2.className='site-version-hidden';
 v2.innerHTML='<div class="v2-heading"><p>03 / GAMBAR DESAIN · V2</p><h2>Infill tengah dan penutup mesh</h2><p>Dua jalur tangga tetap; bidang infill mengikuti geometri versi aktif. Klik gambar untuk membuka ukuran penuh.</p></div><div class="v2-drawings">'+[['01-denah-r08','Denah V2'],['02-infill','Rangka dan potongan infill'],['03-mesh','Penutup mesh dan penjepit']].map(([file,name])=>`<article><h3>${name}</h3><a href="assets/r08/${file}.svg" target="_blank" rel="noopener"><img src="assets/r08/${file}.svg" alt="${name}" loading="lazy"></a></article>`).join('')+'</div><p class="v2-note">Studi koordinasi. Sambungan, tumpuan lantai dan akses evakuasi belum disahkan untuk fabrikasi.</p><a href="assets/r08/index.html">Paket V2 / R08 dan daftar potong</a>';
 gallery.append(v2);
 const modelTitle=document.querySelector('#tiga-d h2'),modelNote=document.querySelector('#tiga-d .lede'),oldTitle=modelTitle.textContent,oldNote=modelNote.textContent;
 const material=$('material'),oldMaterial=document.createElement('div');while(material.firstChild)oldMaterial.append(material.firstChild);material.append(oldMaterial);
 const mat=document.createElement('div');mat.className='v2-material site-version-hidden';mat.innerHTML='<h2>04 / Material V2</h2><p>Memuat kebutuhan material dari model…</p>';material.append(mat);
 const hero=document.querySelector('.hero-drawing img'),oldHero=hero?{src:hero.getAttribute('src'),alt:hero.alt}:null;
 const captions=[...document.querySelectorAll('.hero-drawing figcaption,.hero-drawing-info')].map(el=>({el,html:el.innerHTML}));
 const options={m16_25:{wire_mm:1.6,opening_label_mm:25},m20_25:{wire_mm:2,opening_label_mm:25},m20_50:{wire_mm:2,opening_label_mm:50}};
 function thickness(){window.MettaModelVersion?.thickness({h16:'1,6',h20:'2,0',model:'2,3'}[$('br-case')?.value]||'2,3',{s16:'1,6',s17:'1,7',s20:'2,0',s23:'2,3',reference:'2,0 / 2,8 acuan'}[$('br-shs')?.value]||'2,0 / 2,8 acuan');}
 function show(version,sync=true){
  const structure=$('br-structure')?.value||'baseline';payload=payloads[version==='v2'?structure:'baseline'];if(!payload||!window.MettaModelVersion)return;
  $('site-structure').value=structure;$('site-structure').disabled=version!=='v2';document.documentElement.dataset.mettaStructure=structure;
  active=version;mesh=$('br-mesh')?.value||mesh;
  window.MettaModelVersion.apply(version,payload,options[mesh]);
  thickness();
  const newer=version==='v2';oldGallery.classList.toggle('site-version-hidden',newer);v2.classList.toggle('site-version-hidden',!newer);oldMaterial.classList.toggle('site-version-hidden',newer);mat.classList.toggle('site-version-hidden',!newer);
  modelTitle.textContent=newer?'02 / Model koordinasi 3D · V2 / '+({baseline:'Dasar',a:'A · Bantuan beton',c:'C · Mandiri'}[structure]):oldTitle+' · V1';
  modelNote.textContent=newer?`V2 / R08: infill ${payload.infill_width_mm} mm, ${payload.stair_panels} panel tangga tersisa, ${payload.new_posts} kolom tambahan (infill + opsi struktur) dan sisi mesh terbuka. Model web menunjukkan usulan termasuk penyangga tangga; Revit asli tidak diubah. Sambungan/angkur belum dimodelkan rinci.`:oldNote;
  mat.innerHTML=`<h2>04 / Material V2</h2><p>RHS ${payload.rhs_stocks} batang 6 m; SHS tangga + mesh ${payload.shs_stocks} batang dan railing 20 batang terpisah. Berat mengikuti tebal di RAB.</p><p>Dek 4 mm; tangga tekuk 3 mm; riser depan tetap pelat 2 mm. Kedua sisi luar memakai mesh, rangka SHS dan strip penjepit. Infill ${payload.infill_width_mm} mm; total ${payload.new_posts} kolom tambahan untuk infill dan opsi struktur; tambahan dudukan indikatif ${payload.extra_seats}.</p><a href="#rab-11sep">Buka RAB aktif untuk volume, ketebalan dan pilihan mesh</a>`;
  if(hero){hero.src=newer?'assets/r08/01-denah-r08.svg':oldHero.src;hero.alt=newer?'Denah versi V2 / R08':oldHero.alt;}
  captions.forEach(({el,html})=>{el.innerHTML=newer?(el.matches('figcaption')?'<span>V2 / R08 · DENAH INFILL + MESH</span>':`<span><b>${80+payload.new_posts}</b> kolom termasuk ${payload.new_posts} usulan</span><span><b>${payload.stair_panels}</b> panel tangga</span><span><b>${payload.mesh.length}</b> panel mesh</span>`):html;});
  const kicker=document.querySelector('.pitch-kicker span:last-child');if(kicker)kicker.textContent=newer?'USULAN DESAIN · V2 / R08':'USULAN DESAIN · V1 / R04';
  bar.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.siteVersion===version)));
  $('site-version-status').textContent=newer?'V2 / '+structure.toUpperCase()+' aktif — model 3D, gambar, material dan RAB R08.':'V1 aktif — model dan gambar awal; RAB versi awal.';
  document.documentElement.dataset.siteVersion=version;
  window.dispatchEvent(new CustomEvent('metta:version',{detail:{version,structure}}));
  try{localStorage.setItem(key,version);}catch{}
  if(sync&&$('br-scope')){document.querySelector('[data-rab-mode="revision"]')?.click();const target=newer?'r08':'full';if($('br-case').value==='source'){$('br-case').value='model';$('br-case').dispatchEvent(new Event('change',{bubbles:true}));}if($('br-scope').value!==target){$('br-scope').value=target;$('br-scope').dispatchEvent(new Event('change',{bubbles:true}));}}
 }
 $('site-structure').addEventListener('change',e=>{if($('br-structure')){$('br-structure').value=e.target.value;$('br-structure').dispatchEvent(new Event('change',{bubbles:true}));}});
 window.addEventListener('metta:structure',()=>show(active||'v2',false));
 bar.addEventListener('click',e=>{if(e.target.dataset.siteVersion)show(e.target.dataset.siteVersion);});
 document.addEventListener('change',e=>{if(e.target.id==='br-scope')show(e.target.value==='r08'?'v2':'v1',false);if(e.target.id==='br-mesh'&&active==='v2')show('v2',false);if(['br-case','br-shs'].includes(e.target.id))thickness();});
 // One atomic fetch, then wait for the existing BOQ controller to finish loading.
 Promise.all(['baseline','a','c'].map(async mode=>{const r=await fetch('assets/r08/viewer'+(mode==='baseline'?'':'-'+mode)+'.json');if(!r.ok){if(mode==='baseline')throw Error('Model V2 gagal dimuat.');return [mode,null];}return [mode,await r.json()];})).then(all=>{
  payloads=Object.fromEntries(all);payload=payloads.baseline;$('site-structure').querySelectorAll('option').forEach(o=>o.disabled=!payloads[o.value]);let preferred='v2';try{preferred=localStorage.getItem(key)||'v2';}catch{}
  const q=new URLSearchParams(location.search);if(q.get('design')==='r08'||q.get('version')==='v2')preferred='v2';if(q.get('version')==='v1')preferred='v1';
  const ready=()=>{if($('br-scope-info')?.textContent&&window.MettaModelVersion){show(preferred==='v1'?'v1':'v2');return;}if(++sequence<200)setTimeout(ready,50);else $('site-version-status').textContent='RAB belum siap. Muat ulang halaman untuk menyinkronkan versi.';};ready();
 }).catch(e=>{$('site-version-status').textContent=e.message;bar.querySelectorAll('button').forEach(b=>b.disabled=true);});
})();
