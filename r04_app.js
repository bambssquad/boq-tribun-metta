'use strict';
function r04Totals(rows,settings){
 const safe=x=>Number.isFinite(+x)?Math.max(0,+x):0;
 const groups={};let kg=0;
 rows.forEach(r=>{kg+=safe(r.qty)*safe(r.kg_per_unit);});
 const items=rows.map(r=>({...r,qty:r.code==='U01'?kg:safe(r.qty),price:r.code==='U01'?(settings.service?safe(settings.rate):0):safe(r.price)}));
 items.forEach(r=>{r.amount=Math.round(r.qty*r.price);groups[r.category]=(groups[r.category]||0)+r.amount;});
 const direct=Object.values(groups).reduce((a,b)=>a+b,0),oh=Math.round(direct*safe(settings.overhead)/100),profit=Math.round((direct+oh)*safe(settings.profit)/100),pretax=direct+oh+profit,tax=Math.round(pretax*safe(settings.tax)/100);
 return {items,groups,kg,direct,oh,profit,pretax,tax,total:pretax+tax};
}
if(typeof module!=='undefined')module.exports={r04Totals};
if(typeof document!=='undefined'){
 const $=x=>document.getElementById(x),num=(n,d=0)=>new Intl.NumberFormat('id-ID',{maximumFractionDigits:d,minimumFractionDigits:d}).format(n),rp=n=>'Rp '+num(n),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let data,rows,settings,filter='Semua',totals;
 const key='metta-r04-allin-v1';
 function save(){try{localStorage.setItem(key,JSON.stringify({prices:Object.fromEntries(rows.map(r=>[r.code,r.price])),settings}));}catch{}}
 function summary(){
  totals=r04Totals(rows,settings);
  $('totals').innerHTML=[...Object.entries(totals.groups),['Biaya langsung',totals.direct],['Overhead '+settings.overhead+'%',totals.oh],['Laba '+settings.profit+'%',totals.profit],['Sebelum pajak',totals.pretax],['Pajak keluaran '+settings.tax+'%',totals.tax],['TOTAL ANGGARAN',totals.total]].map(([k,v],i,a)=>`<div class="${i===a.length-1?'grand':''}"><dt>${esc(k)}</dt><dd>${rp(v)}</dd></div>`).join('');
  $('offer-note').textContent='Basis jasa: '+num(totals.kg,3)+' kg pembelian stok × '+rp(settings.rate)+'/kg'+(settings.service?'':' (upah per kg nonaktif)')+'. Fastener dihitung per buah/set dan belum memiliki berat sertifikat; massanya tidak ditambahkan secara fiktif ke dasar jasa.';
  $('load-status').textContent=rows.length+' item · harga dan asumsi tersimpan pada perangkat ini.';
 }
 function render(){
  summary();
  $('rows').innerHTML=totals.items.filter(r=>filter==='Semua'||filter===r.category).map(r=>`<tr><td><b>${r.code}</b><br>${esc(r.name)}<span class="status">${esc(r.status)}</span></td><td class="num">${num(r.qty,3)}</td><td>${esc(r.unit)}</td><td>${r.code==='U01'?rp(r.price):`<input aria-label="Harga ${esc(r.name)}" data-price="${r.code}" type="number" min="0" step="any" value="${r.price}">`}</td><td class="num" data-amount="${r.code}">${num(r.amount)}</td><td>${esc(r.basis)}${data.sources[r.source]?`<br><a href="${data.sources[r.source][1]}" target="_blank" rel="noopener">Sumber / pemasok ↗</a>`:''}</td></tr>`).join('');
 }
 function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 fetch('assets/r04/data.json').then(r=>{if(!r.ok)throw Error('load');return r.json();}).then(d=>{
  data=d;rows=structuredClone(d.rows);settings={...d.defaults,rate:6000};
  try{const s=JSON.parse(localStorage.getItem(key));if(s){rows.forEach(r=>{if(Number.isFinite(+s.prices?.[r.code])&&+s.prices[r.code]>=0)r.price=+s.prices[r.code];});for(const k of ['rate','overhead','profit','tax'])if(Number.isFinite(+s.settings?.[k]))settings[k]=Math.max(0,+s.settings[k]);if(typeof s.settings?.service==='boolean')settings.service=s.settings.service;}}catch{}
  for(const k of ['rate','overhead','profit','tax'])$(k).value=settings[k];$('service').checked=settings.service;
  for(const k of ['service','rate','overhead','profit','tax'])$(k).addEventListener('change',()=>{settings[k]=k==='service'?$(k).checked:Math.max(0,Number($(k).value)||0);save();render();});
  $('rows').addEventListener('change',e=>{const code=e.target.dataset.price;if(!code)return;rows.find(r=>r.code===code).price=Math.max(0,Number(e.target.value)||0);save();render();});
  document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));render();}));
  const waste=100*(1-d.flat_area/(d.nesting.length*2.88));
  $('analysis-results').innerHTML=[[num(d.new_bent_3mm_kg,2)+' kg','Pelat tangga bersih, termasuk tekukan'],[d.nesting.length+' lembar','Stok pelat3mm / 1200×2400'],[num(waste,2)+'%','Sisa geometris + kerf pelat'],[d.main_stock.length+' batang','RHS gabungan rangka, kolom dan stringer']].map(([a,b])=>`<div><strong>${a}</strong><span>${b}</span></div>`).join('');
  const a=d.analysis;
  $('calculation').innerHTML=`<p>${esc(a.assumption)}</p><p>E=${num(a.E_MPa)}MPa; Fy=${a.Fy_MPa}MPa asumsi. Pelat3mm, strip100mm, celah75mm: tegangan${num(a.plate_stress_MPa,2)}MPa, lendutan${num(a.plate_deflection_mm,3)}mm. SHS40×40×2, bentang800mm: tegangan${num(a.beam_stress_MPa,2)}MPa, lendutan${num(a.beam_deflection_mm,3)}mm. Pembanding lentur0,9Fy=${a.limit_MPa}MPa; lendutanSHS L/360=2,222mm.</p><p>Rumus strip: M=qL²/8; Z=bt²/6; I=bt³/12; δ=5qL⁴/(384EI). Pengaku: M=PL/4 dan δ=PL³/(48EI). Faktor1,6 pada beban titik untuk tegangan. Distribusi tapak100×100 adalah asumsi skenario, bukan hasil uji. ${esc(a.scope)}</p><p>Luas proyeksi audit${num(d.audited_area,6)}m²; bounding box${num(d.bounds_area,6)}m²; bentangan tekuk${num(d.flat_area,6)}m². Tiga besaran ini berbeda. Massa RAB dihitung dari stok nominal; massa pengiriman harus memakai surat timbang/sertifikat.</p><p>Luas cat${num(d.coating_area,3)}m². Cat2-in-1 dua lapis menggantikan paket primer dan topcoat terpisah. Antiselip bidang injak dihitung sebagai sistem tersendiri.</p>`;
  $('csv').addEventListener('click',()=>{const q=s=>'"'+String(s??'').replace(/"/g,'""')+'"';const lines=[['Kode','Kategori','Item','Volume','Satuan','Harga','Jumlah','Basis','Status'],...totals.items.map(r=>[r.code,r.category,r.name,r.qty,r.unit,r.price,r.amount,r.basis,r.status]),[],['Biaya langsung',totals.direct],['Overhead',totals.oh],['Laba',totals.profit],['Pajak',totals.tax],['Total',totals.total]];download('METTA-R04-RAB.csv','\uFEFF'+lines.map(x=>x.map(q).join(',')).join('\r\n'),'text/csv;charset=utf-8');});
  $('json').addEventListener('click',()=>download('METTA-R04-penawaran.json',JSON.stringify({revision:'R04',generated:new Date().toISOString(),settings,...totals},null,2),'application/json'));
  const beforePrint=()=>{filter='Semua';document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.filter==='Semua')));render();};
  window.addEventListener('beforeprint',beforePrint);
  $('print').addEventListener('click',()=>{beforePrint();window.print();});$('reset').addEventListener('click',()=>{rows=structuredClone(data.rows);settings={...data.defaults,rate:6000};for(const k of ['rate','overhead','profit','tax'])$(k).value=settings[k];$('service').checked=settings.service;save();render();});render();
  let format='xlsx';
  document.querySelectorAll('[data-rab-format]').forEach(b=>b.addEventListener('click',()=>{format=b.dataset.rabFormat;document.querySelectorAll('[data-rab-format]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));$('rab-download-action').textContent=format==='xlsx'?'Unduh Excel':'Simpan PDF';$('rab-download-hint').textContent=format==='xlsx'?'Menggunakan harga dan pengaturan saat ini.':'Pada dialog cetak, pilih Simpan sebagai PDF.';}));
  $('rab-download-action').addEventListener('click',()=>{
   if(format==='pdf'){beforePrint();window.print();return;}
   summary();
   const cell=v=>typeof v==='number'?{n:v}:{t:String(v??'')},table=rs=>rs.map(r=>r.map(cell));
   const rab=[['SAP / SELARAS ADHI PERKASA — METTA R04'],['RAB sesuai harga saat ekspor; nilai merupakan snapshot.'],['Kode','Kategori','Uraian','Volume','Satuan','Harga satuan','Jumlah','Dasar kuantitas','Status'],...totals.items.map(r=>[r.code,r.category,r.name,r.qty,r.unit,r.price,r.amount,r.basis,r.status])];
   const rekap=[['METTA R04 — REKAP RAB'],...Object.entries(totals.groups),['Biaya langsung',totals.direct],['Overhead',totals.oh],['Laba',totals.profit],['Sebelum pajak',totals.pretax],['Pajak',totals.tax],['TOTAL ANGGARAN',totals.total]];
   const config=[['Pengaturan','Nilai'],['Tarif jasa Rp/kg',settings.rate],['Jasa aktif',settings.service?1:0],['Berat pembelian jasa kg',totals.kg],['Overhead %',settings.overhead],['Laba %',settings.profit],['Pajak %',settings.tax],['Waktu ekspor',new Date().toISOString()]];
   const bytes=XL.book([{name:'REKAP',rows:table(rekap),cols:[58,26]},{name:'RAB',rows:table(rab),cols:[14,26,60,18,15,22,24,90,40]},{name:'PENGATURAN',rows:table(config),cols:[38,34]}]);
   download('METTA-R04-RAB.xlsx',bytes,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  });
 }).catch(()=>{$('load-status').textContent='Rincian belum berhasil dimuat. Muat ulang halaman; salinan CSV tersedia di tautan unduhan.';});
 const viewer=createDrawingPanZoom($('viewport'),$('sheet-image'),{plus:$('plus'),minus:$('minus'),reset:$('fit'),level:$('scale')});
 document.querySelectorAll('[data-sheet]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.sheet;$('sheet-title').textContent=b.innerText;$('sheet-image').src='assets/r04/'+id+'.svg';$('sheet-image').alt=b.innerText;$('dxf').href='assets/r04/'+id+'.dxf';$('drawing-dialog').showModal();viewer.reset();}));$('close').addEventListener('click',()=>$('drawing-dialog').close());
}
