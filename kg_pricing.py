"""Add the authorized Rp/kg fabrication-and-installation offer to the existing calculator."""
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent

def patch(js):
 def replace(old,new,count=1):
  nonlocal js
  assert old in js,old[:100]
  js=js.replace(old,new,count)
 replace('load();','''load();
if(!S.fabrication){S.fabrication={enabled:true,rate:6000};S.price=true;}
function serviceCost(){return computePurchaseService(S.rows,S.bar,DATA.sheetA,basisH,basisP,!!S.fabrication?.enabled,S.fabrication?.rate??6000);}
function syncServiceUI(){
 const j=serviceCost();
 $('tgFabrication').checked=j.enabled;$('fabricationRate').value=j.rate;
 $('fabricationWeight').textContent=f(j.kg,2)+' kg';$('fabricationAmount').textContent=rp(j.cost);
 $('fabricationBasis').innerHTML=j.items.map(r=>`<tr><td>${esc(r.name)}</td><td class="num">${r.units} ${r.stock}</td><td class="num">${f(r.netKg,2)}</td><td class="num">${f(r.purchaseKg,2)}</td></tr>`).join('');
}
document.addEventListener('change',e=>{
 if(e.target.id==='tgFabrication'||e.target.id==='fabricationRate'){
  S.fabrication={enabled:$('tgFabrication').checked,rate:Math.max(0,Number($('fabricationRate').value)||0)};
  if(S.fabrication.enabled){S.price=true;$('tgPrice').checked=true;}save();render();
 }
});
''')
 replace('function basisH(r){',(ROOT/'kg_pricing.js').read_text(encoding='utf-8-sig')+'\nfunction basisH(r){')
 replace("$('grand').innerHTML=odo('grand',f((sumH+sumP)/1000,2)+' ton');", "const job=serviceCost();syncServiceUI();\n  $('grand').innerHTML=odo('grand',f(job.kg/1000,2)+' ton');")
 replace('const _sub=costH+costP+costO,','const _sub=costH+costP+costO+job.cost,')
 replace('TOT={costH:costH,costP:costP,costO:costO,','TOT={costJ:job.cost,serviceKg:job.kg,serviceRate:job.rate,costH:costH,costP:costP,costO:costO,')
 replace('let TOT={costH:0', 'let TOT={costJ:0,serviceKg:0,serviceRate:6000,costH:0')
 replace('total:_pre+_tax,kg:sumH+sumP','total:_pre+_tax,kg:job.kg')
 replace('const sub=costH+costP+costO;', 'const sub=costH+costP+costO+job.cost;')
 replace("let rows=[['Profil hollow',costH],['Pelat baja',costP],['Material lain',costO]];", "let rows=[['Profil hollow',costH],['Pelat baja',costP],['Material lain',costO],['Jasa fabrikasi & pemasangan (berat pembelian)',job.cost]];")
 replace("if(S.mode!=='ringkas'){","if(true){")
 replace('const kg=sumH+sumP;', 'const kg=job.kg;')
 replace("TOT.costO]];", "TOT.costO],['Jasa fabrikasi & pemasangan — '+f(TOT.serviceKg,2)+' kg × '+rp(TOT.serviceRate)+'/kg'+(S.fabrication?.enabled?'':' (nonaktif)'),TOT.costJ||0]];")
 replace("['Material lain',TOT.costO],\n   ['Subtotal'", "['Material lain',TOT.costO],['Jasa fabrikasi & pemasangan',TOT.costJ||0],['Berat pembelian jasa (kg)',TOT.serviceKg],['Tarif jasa (Rp/kg)',TOT.serviceRate],\n   ['Subtotal'")
 replace('other:S.rows.other, offer:S.offer};','other:S.rows.other, offer:S.offer, fabrication:S.fabrication};')
 replace('if(o.mode) S.mode=o.mode;',"if(o.mode) S.mode=o.mode;\n    if(o.fabrication)S.fabrication={enabled:!!o.fabrication.enabled,rate:Math.max(0,Number(o.fabrication.rate)||0)};")
 replace('rev:DATA.rev,rows:clone(BASE)};', 'rev:DATA.rev,rows:clone(BASE),fabrication:{enabled:true,rate:6000}};')
 replace("if(!S.offer) S.offer=OFFER0();", "if(!S.offer) S.offer=OFFER0();\nif(location.hash==='#penawaran')S.offer.on=true;\ndocument.querySelector('.kg-offer-link')?.addEventListener('click',()=>{OF().on=true;save();renderOffer();});")
 # Add formula-driven purchasing weights; existing material-cost formulas stay intact.
 replace("inp[11]=[{t:'Baris B3:B9 di lembar ini dipakai seluruh rumus BOQ.'}];", """inp[11]=[{t:'B3:B9: parameter BOQ. B13: tarif jasa. B14: 1 aktif / 0 nonaktif.'}];
  inp[12]=[{t:'Tarif fabrikasi & pemasangan (Rp/kg)'},{n:serviceCost().rate,s:s.inp}];
  inp[13]=[{t:'Aktifkan jasa per kg (1/0)'},{n:serviceCost().enabled?1:0,s:s.inp}];
  inp[14]=[{t:'Dasar jasa: berat pembelian, termasuk pembulatan lonjor/lembar.'}];
  inp[15]=[{t:'Harga material terpisah; tarif jasa belum termasuk overhead dan PPN rekap.'}];""")
 replace('const rows=[];\n  rows[0]=',"const weightRows=[[{t:'BERAT PEMBELIAN — DASAR JASA',s:s.title}],[],['Uraian','Stok beli','Satuan','kg/stok','Berat beli (kg)'].map(t=>({t,s:s.head}))];\n  const rows=[];\n  rows[0]=")
 replace("S.rows.hollow.forEach(x=>{\n    no++; const R=r+1;", "S.rows.hollow.forEach(x=>{\n    no++; const R=r+1, W=weightRows.length+1;\n    weightRows.push([{t:x.nm},{f:`BOQ!I${R}`,s:s.n0},{t:'lonjor'},{f:`INPUT!$B$5*${(+x.kg||0)}`,s:s.n2},{f:`B${W}*D${W}`,s:s.n2}]);")
 replace("S.rows.plate.forEach(x=>{\n    no++; const R=r+1;", "S.rows.plate.forEach(x=>{\n    no++; const R=r+1, W=weightRows.length+1;\n    weightRows.push([{t:x.nm},{f:`BOQ!I${R}`,s:s.n0},{t:'lembar'},{f:`INPUT!$B$6*(${(+x.t||0)}*INPUT!$B$7+${(+x.sur||0)})`,s:s.n2},{f:`B${W}*D${W}`,s:s.n2}]);")
 a=js.index('  // ---------- REKAP ----------');b=js.index('\n}\n\nfunction downloadXlsx',a)
 js=js[:a]+'''  const endWeight=weightRows.length;
  weightRows.push([{t:'TOTAL BERAT PEMBELIAN',s:s.bold},null,null,null,{f:`SUM(E4:E${endWeight})`,s:s.n2}]);
  const rk=[];
  rk[0]=[{t:'REKAPITULASI BIAYA — '+P,s:s.title}];
  rk[2]=[{t:'Bagian',s:s.head},{t:'Uraian',s:s.head},{t:'Jumlah',s:s.head}];
  rk[3]=[{t:'A'},{t:'Profil hollow'},{f:`BOQ!L${aSub}`,s:s.rp}];
  rk[4]=[{t:'B'},{t:'Pelat baja'},{f:`BOQ!L${bSub}`,s:s.rp}];
  rk[5]=[{t:'C'},{t:'Material lain'},{f:`BOQ!L${cSub}`,s:s.rp}];
  rk[6]=[{t:'D'},{t:'Jasa fabrikasi & pemasangan'},{f:`IF(INPUT!B14=1,BERAT!E${endWeight+1}*INPUT!B13,0)`,s:s.rp}];
  rk[7]=[null,{t:'Subtotal',s:s.bold},{f:'SUM(C4:C7)',s:s.rp}];
  rk[8]=[null,{t:'Overhead & keuntungan'},{f:'C8*INPUT!B8',s:s.rp}];
  rk[9]=[null,{t:'Jumlah sebelum pajak'},{f:'C8+C9',s:s.rp}];
  rk[10]=[null,{t:'PPN'},{f:'C10*INPUT!B9',s:s.rp}];
  rk[11]=[null,{t:'NILAI PENAWARAN',s:s.bold},{f:'C10+C11',s:s.rp}];
  rk[13]=[null,{t:'Dasar jasa: berat pembelian (kg)'},{f:`BERAT!E${endWeight+1}`,s:s.n2}];
  const offer=OF(), qr=[];
  qr[0]=[{t:'SURAT PENAWARAN HARGA',s:s.title}];
  qr[2]=[{t:'Perusahaan'},{t:offer.co.nm||''}];qr[3]=[{t:'Kepada'},{t:offer.cl.nm||''}];
  qr[4]=[{t:'Nomor'},{t:ofNo()}];qr[5]=[{t:'Lokasi'},{t:offer.cl.loc}];
  qr[7]=[{t:'Jasa fabrikasi & pemasangan'},{f:'REKAP!C7',s:s.rp}];
  qr[8]=[{t:'Material sesuai BOQ'},{f:'SUM(REKAP!C4:C6)',s:s.rp}];
  qr[9]=[{t:'Overhead & keuntungan'},{f:'REKAP!C9',s:s.rp}];
  qr[10]=[{t:'PPN'},{f:'REKAP!C11',s:s.rp}];
  qr[11]=[{t:'NILAI PENAWARAN',s:s.bold},{f:'REKAP!C12',s:s.rp}];
  qr[13]=[{t:'Dasar berat: pembelian baja termasuk sisa potong.'}];
  qr[14]=[{t:'Tarif jasa (Rp/kg)'},{f:'INPUT!B13',s:s.rp}];
  qr[16]=[{t:'Tahap pembayaran',s:s.head},{t:'Persentase (%)',s:s.head},{t:'Nominal',s:s.head}];
  offer.terms.forEach(t=>{const row=qr.length+1;qr.push([{t:t.nm},{n:+t.pct||0,s:s.inp},{f:`$B$12*B${row}/100`,s:s.rp}]);});
  qr.push([{t:'Lingkup: jasa fabrikasi dan pemasangan baja. Material dihitung terpisah.'}]);
  qr.push([{t:'Harga kosong pada BOQ belum termasuk nilai penawaran.'}]);
  return XL.book([
    {name:'PENAWARAN',rows:qr,cols:[58,32,24]},
    {name:'REKAP',rows:rk,cols:[8,60,25]},
    {name:'INPUT',rows:inp,cols:[65,24,35]},
    {name:'BOQ',rows,cols:[5,34,20,8,13,14,9,12,14,14,13,16,44]},
    {name:'BERAT',rows:weightRows,cols:[45,16,15,18,22]}
  ]);''' + js[b:]
 # Default offer wording must match the selected service scope.
 replace("scope:['Fabrikasi & pemasangan rangka tribun baja hollow sesuai gambar kerja S-01 s/d S-12',\n         'Pelat dek bordes, papan dudukan pinus, railing, tangga, dan sandaran',\n         'Pengecatan lengkap (primer + finish) dan pembersihan area kerja'],", "scope:['Jasa fabrikasi dan pemasangan komponen baja yang tercantum pada BOQ.',\n         'Dasar pengukuran jasa: berat pembelian lonjor dan lembar baja, termasuk sisa potong.',\n         'Material dihitung terpisah sesuai baris BOQ yang diberi harga.'],")
 return js

def enhance(s):
 panel=BeautifulSoup('''<section class="kg-pricing" aria-labelledby="kg-heading"><div class="kg-header"><h3 id="kg-heading">Jasa fabrikasi & pemasangan</h3><label class="kg-toggle"><input type="checkbox" role="switch" id="tgFabrication" checked> Hitung jasa per kg</label></div><div class="kg-grid"><label>Tarif jasa / kg<input id="fabricationRate" type="number" min="0" step="100" value="6000"></label><div><span>Berat pembelian baja</span><strong id="fabricationWeight">—</strong></div><div><span>Subtotal jasa</span><strong id="fabricationAmount">—</strong></div></div><p>Dasar: jumlah lonjor × panjang stok × kg/m, ditambah jumlah lembar × luas lembar × kg/m². Sisa potong sudah termasuk. Material, overhead, dan PPN dihitung terpisah di rekap.</p><details><summary>Rincian berat yang ditagihkan</summary><div class="tw"><table><thead><tr><th>Komponen</th><th>Stok beli</th><th>Berat bersih (kg)</th><th>Berat beli (kg)</th></tr></thead><tbody id="fabricationBasis"></tbody></table></div></details><a class="kg-offer-link" href="#penawaran">Buka template penawaran ↓</a></section>''','html.parser')
 s.select_one('#boq .boqbar').insert_before(panel)
 return s
