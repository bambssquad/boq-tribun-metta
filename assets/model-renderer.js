const DATA = {"rev": "R04-1200x2400-7b45395dbb", "other": [{"nm": "Papan pinus 400×40 (dudukan)", "q": 1.1970162520117402, "un": "m³", "note": "Volume 15 elemen Revit aktif; jumlah papan beli dan sambungan kayu belum final."}, {"nm": "Panel kayu sandaran 40 mm", "q": 0.292, "un": "m³", "note": "Estimasi web lama; belum diukur ulang. 7.29 m² menerus A–C, finish clear"}, {"nm": "Finish clear kayu", "q": 9, "un": "liter", "note": "Estimasi web lama; belum diukur ulang. papan pinus + panel sandaran, 2 lapis"}, {"nm": "Cat nosing — luas model", "q": 1.9120855900147202, "un": "m²", "note": "31 elemen representasi cat; konsumsi liter mengikuti produk dan jumlah lapis."}, {"nm": "Karet dudukan 150×150×10", "q": 80, "un": "bh", "note": "Jumlah dudukan model; grade bantalan belum terverifikasi."}], "hollow": [{"nm": "Rangka RHS — hasil model", "pr": "RHS 50×100×2,3", "n": 165, "L": 418.74, "kg": 5.416666666666667, "note": "165 framing termasuk20diagonal;75stok6m, kerf3mm, pola FFD. Kolom dipisahkan pada kalkulator ini."}, {"nm": "Kolom — hasil model", "pr": "RHS 50×100×2,3", "n": 80, "L": 133.56, "kg": 5.416666666666667, "note": "80 kolom, dasar +18 mm. Jumlah beli masih perkiraan, bukan pola potong."}, {"nm": "Rail atas — hasil model", "pr": "HOLLOW 40x40x2", "n": 10, "L": 8.43, "kg": 2.39, "note": "10 elemen; tipe Revit lama masih memakai keluarga W, penampang fisik harus diperiksa."}, {"nm": "Tiang railing — hasil model", "pr": "HOLLOW 40x40x2,8", "n": 85, "L": 97.5, "kg": 3.27, "note": "85 tiang dari System Length model aktif; berat profil masih estimasi katalog lama."}], "plate": [{"nm": "Dek bordes 4 mm — hasil model", "t": 4, "A": 82.35, "sur": 0, "note": "Jumlah Area 30 elemen Revit; 28 berluas positif. Berat baja dasar saja; motif belum terukur."}, {"nm": "Penutup riser, fascia dan sisi 2 mm — R04", "t": 2, "A": 62.98, "sur": 0, "note": "310bagian native, takikan beton dan return tepi termasuk; belakang/bawah terbuka. Pola beli aktual di RAB R04."}, {"nm": "Pelat tekuk tangga 3 mm — R04", "t": 3, "A": 15.96, "sur": 0, "note": "56bidang; luas bersih termasuk tekukan dan takikan. Pembelian mengikuti pola nesting, lihat RAB R04."}, {"nm": "Base plate", "t": 8, "A": 1.8, "sur": 0, "note": "80 dudukan 150×150. Tanpa angkur ke pelat lantai."}], "sheetA": 2.88};

// layer toggle
document.querySelectorAll('.chip input').forEach(cb=>{
  cb.addEventListener('change',()=>{
    const sec=document.getElementById(cb.dataset.sheet);
    sec.querySelectorAll('.'+cb.dataset.lay).forEach(g=>g.classList.toggle('hidden',!cb.checked));
  });
});
// pan + zoom + pinch (dua jari) + ketuk-dua-kali untuk reset
document.querySelectorAll('.frame').forEach(fr=>{
  const pan=fr.querySelector('.pan');
  let s=1,tx=0,ty=0,raf=0;
  const pts=new Map(); let p0=0,s0=1,m0=null,moved=0,lastTap=0;
  const apply=()=>{ if(raf) return; raf=requestAnimationFrame(()=>{raf=0;
    pan.style.transform=`translate3d(${tx}px,${ty}px,0) scale(${s})`;}); };
  const zoomAt=(mx,my,ns)=>{ns=Math.min(9,Math.max(.5,ns));
    tx=mx-(mx-tx)*(ns/s); ty=my-(my-ty)*(ns/s); s=ns; apply();};
  const reset=()=>{s=1;tx=0;ty=0;apply();};
  // isi layar: perbesar sampai gambar mengisi bingkai (buat baca denah panjang di HP)
  window.__fit=window.__fit||{};
  window.__fit[fr.dataset.frame]=mode=>{
    if(mode==='reset'){reset();return true;}
    const R=fr.getBoundingClientRect(), vb=pan.querySelector('svg').viewBox.baseVal;
    if(!vb.width||R.width<40||R.height<40) return false;
    const asp=vb.width/vb.height;
    const dw = (R.width/R.height>asp) ? R.height*asp : R.width;
    const dh = dw/asp;
    const ns = Math.min(4, Math.max(1, Math.max(R.width/dw, R.height/dh)));
    s=ns; tx=R.width/2-(R.width/2)*s; ty=R.height/2-(R.height/2)*s; apply(); return true;
  };
  const mid=()=>{const a=[...pts.values()];
    return {x:(a[0].x+a[1].x)/2,y:(a[0].y+a[1].y)/2,d:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)};};

  fr.addEventListener('wheel',e=>{
    e.preventDefault();
    const r=fr.getBoundingClientRect();
    zoomAt(e.clientX-r.left,e.clientY-r.top,s*(e.deltaY<0?1.14:1/1.14));
  },{passive:false});

  fr.addEventListener('pointerdown',e=>{
    pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
    fr.setPointerCapture(e.pointerId);
    if(pts.size===1){moved=0; fr.dataset.moved='0'; fr.classList.add('drag');}
    if(pts.size===2){const m=mid(); p0=m.d; s0=s; m0=m;}
  });
  fr.addEventListener('pointermove',e=>{
    const p=pts.get(e.pointerId); if(!p) return;
    const dx=e.clientX-p.x, dy=e.clientY-p.y; p.x=e.clientX; p.y=e.clientY;
    if(pts.size>=2){
      const r=fr.getBoundingClientRect(), m=mid();
      if(p0>8) zoomAt(m.x-r.left,m.y-r.top,s0*(m.d/p0));
      tx+=m.x-m0.x; ty+=m.y-m0.y; m0=m; apply(); return;
    }
    moved+=Math.abs(dx)+Math.abs(dy);
    fr.dataset.moved = moved>6?'1':'0';
    tx+=dx; ty+=dy; apply();
  });
  const up=e=>{
    const had=pts.size; pts.delete(e.pointerId);
    if(pts.size<2) p0=0;
    if(pts.size===0){
      fr.classList.remove('drag');
      if(had===1 && moved<6){
        const now=performance.now();
        if(now-lastTap<300){ reset(); lastTap=0; }
        else lastTap=now;
      }
    }
  };
  fr.addEventListener('pointerup',up); fr.addEventListener('pointercancel',up);

  const btn=document.querySelector(`[data-reset="${fr.dataset.frame}"]`);
  if(btn) btn.addEventListener('click',()=>{
    reset();
    document.getElementById(fr.dataset.frame).querySelectorAll('.chip input').forEach(cb=>{
      cb.checked=true;
      document.getElementById(cb.dataset.sheet).querySelectorAll('.'+cb.dataset.lay)
        .forEach(g=>g.classList.remove('hidden'));
    });
  });
});

// ---------------- penulis XLSX (tanpa library) ----------------
const XL=(function(){
  const T=(()=>{const t=new Uint32Array(256);
    for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0;}
    return t;})();
  const crc32=b=>{let c=0xFFFFFFFF;for(let i=0;i<b.length;i++)c=T[(c^b[i])&0xFF]^(c>>>8);
    return (c^0xFFFFFFFF)>>>0;};
  const enc=s=>new TextEncoder().encode(s);
  const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');

  function zip(files){
    const parts=[], central=[]; let off=0;
    files.forEach(f=>{
      const nm=enc(f.name), data=typeof f.data==='string'?enc(f.data):f.data;
      const c=crc32(data), n=data.length;
      const lh=new Uint8Array(30+nm.length), dv=new DataView(lh.buffer);
      dv.setUint32(0,0x04034b50,true); dv.setUint16(4,20,true); dv.setUint16(6,0,true);
      dv.setUint16(8,0,true); dv.setUint16(10,0,true); dv.setUint16(12,0x2100,true);
      dv.setUint32(14,c,true); dv.setUint32(18,n,true); dv.setUint32(22,n,true);
      dv.setUint16(26,nm.length,true); dv.setUint16(28,0,true);
      lh.set(nm,30);
      parts.push(lh,data);
      const ch=new Uint8Array(46+nm.length), cv=new DataView(ch.buffer);
      cv.setUint32(0,0x02014b50,true); cv.setUint16(4,20,true); cv.setUint16(6,20,true);
      cv.setUint16(8,0,true); cv.setUint16(10,0,true); cv.setUint16(12,0,true);
      cv.setUint16(14,0x2100,true);
      cv.setUint32(16,c,true); cv.setUint32(20,n,true); cv.setUint32(24,n,true);
      cv.setUint16(28,nm.length,true); cv.setUint32(42,off,true);
      ch.set(nm,46);
      central.push(ch);
      off+=lh.length+n;
    });
    let csize=0; central.forEach(c=>csize+=c.length);
    const end=new Uint8Array(22), ev=new DataView(end.buffer);
    ev.setUint32(0,0x06054b50,true); ev.setUint16(8,central.length,true);
    ev.setUint16(10,central.length,true); ev.setUint32(12,csize,true); ev.setUint32(16,off,true);
    let total=off+csize+22, out=new Uint8Array(total), p=0;
    parts.forEach(a=>{out.set(a,p);p+=a.length;});
    central.forEach(a=>{out.set(a,p);p+=a.length;});
    out.set(end,p);
    return out;
  }

  // ---- sel ----
  const col=i=>{let s='';i++;while(i>0){const m=(i-1)%26;s=String.fromCharCode(65+m)+s;i=(i-m-1)/26;}return s;};
  const S={def:0,bold:1,n2:2,n0:3,rp:4,head:5,inp:6,title:7,sec:8};
  const cell=(r,c,v)=>{
    const ref=col(c)+r;
    if(v==null||v==='') return '';
    if(typeof v!=='object')
      return `<c r="${ref}" t="inlineStr"><is><t xml:space="preserve">${esc(v)}</t></is></c>`;
    const s=v.s!=null ? ` s="${v.s}"` : '';
    if(v.f!=null && v.f!=='') return `<c r="${ref}"${s}><f>${esc(v.f)}</f></c>`;
    if(v.n!=null && v.n!=='' && isFinite(v.n)) return `<c r="${ref}"${s}><v>${v.n}</v></c>`;
    if(v.t!=null && v.t!=='')
      return `<c r="${ref}"${s} t="inlineStr"><is><t xml:space="preserve">${esc(v.t)}</t></is></c>`;
    return `<c r="${ref}"${s}/>`;   // sel kosong bergaya (mis. kolom harga yang belum diisi)
  };
  const sheet=(rows,cols)=>{
    let x='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      +'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
    if(cols) x+='<cols>'+cols.map((w,i)=>`<col min="${i+1}" max="${i+1}" width="${w}" customWidth="1"/>`).join('')+'</cols>';
    x+='<sheetData>';
    rows.forEach((row,ri)=>{
      if(!row) return;
      x+=`<row r="${ri+1}">`+row.map((v,ci)=>v==null?'':cell(ri+1,ci,v)).join('')+'</row>';
    });
    return x+'</sheetData></worksheet>';
  };

  const STYLES='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    +'<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    +'<numFmts count="3">'
    +'<numFmt numFmtId="164" formatCode="&quot;Rp&quot;#,##0"/>'
    +'<numFmt numFmtId="165" formatCode="#,##0.00"/>'
    +'<numFmt numFmtId="166" formatCode="#,##0"/></numFmts>'
    +'<fonts count="4">'
    +'<font><sz val="11"/><name val="Calibri"/></font>'
    +'<font><b/><sz val="11"/><name val="Calibri"/></font>'
    +'<font><b/><sz val="16"/><name val="Calibri"/></font>'
    +'<font><b/><sz val="11"/><color rgb="FF9A6A05"/><name val="Calibri"/></font></fonts>'
    +'<fills count="4"><fill><patternFill patternType="none"/></fill>'
    +'<fill><patternFill patternType="gray125"/></fill>'
    +'<fill><patternFill patternType="solid"><fgColor rgb="FFFFF3C4"/><bgColor indexed="64"/></patternFill></fill>'
    +'<fill><patternFill patternType="solid"><fgColor rgb="FFE8E4DA"/><bgColor indexed="64"/></patternFill></fill></fills>'
    +'<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    +'<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    +'<cellXfs count="9">'
    +'<xf xfId="0" numFmtId="0" fontId="0" fillId="0" borderId="0"/>'
    +'<xf xfId="0" numFmtId="0" fontId="1" fillId="0" borderId="0" applyFont="1"/>'
    +'<xf xfId="0" numFmtId="165" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/>'
    +'<xf xfId="0" numFmtId="166" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/>'
    +'<xf xfId="0" numFmtId="164" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/>'
    +'<xf xfId="0" numFmtId="0" fontId="1" fillId="3" borderId="0" applyFont="1" applyFill="1"/>'
    +'<xf xfId="0" numFmtId="164" fontId="1" fillId="2" borderId="0" applyNumberFormat="1" applyFont="1" applyFill="1"/>'
    +'<xf xfId="0" numFmtId="0" fontId="2" fillId="0" borderId="0" applyFont="1"/>'
    +'<xf xfId="0" numFmtId="0" fontId="3" fillId="0" borderId="0" applyFont="1"/>'
    +'</cellXfs></styleSheet>';

  function book(sheets){
    const names=sheets.map(s=>s.name);
    const files=[
      {name:'[Content_Types].xml', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        +'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        +'<Default Extension="xml" ContentType="application/xml"/>'
        +'<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        + names.map((n,i)=>`<Override PartName="/xl/worksheets/sheet${i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')
        +'<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        +'</Types>'},
      {name:'_rels/.rels', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        +'</Relationships>'},
      {name:'xl/workbook.xml', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        +'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
        + names.map((n,i)=>`<sheet name="${esc(n)}" sheetId="${i+1}" r:id="rId${i+1}"/>`).join('')
        +'</sheets><calcPr calcId="0" fullCalcOnLoad="1"/></workbook>'},
      {name:'xl/_rels/workbook.xml.rels', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + names.map((n,i)=>`<Relationship Id="rId${i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i+1}.xml"/>`).join('')
        + `<Relationship Id="rId${names.length+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>`
        +'</Relationships>'},
      {name:'xl/styles.xml', data:STYLES},
    ];
    sheets.forEach((s,i)=>files.push({name:`xl/worksheets/sheet${i+1}.xml`, data:sheet(s.rows,s.cols)}));
    return zip(files);
  }
  return {book, S};
})();

// ---------------- BOQ: hitung, harga, dan edit ----------------
const $=id=>document.getElementById(id);
const f=(n,d=1)=>Number(n||0).toLocaleString('id-ID',{minimumFractionDigits:d,maximumFractionDigits:d});
const rp=n=>'Rp ' + Math.round(n||0).toLocaleString('id-ID');
const pn=s=>{
  s=String(s==null?'':s).trim().replace(/[^\d.,-]/g,'');
  if(s.indexOf(',')>=0) s=s.replace(/\./g,'').replace(',','.');
  else if(!/\.\d{1,2}$/.test(s)) s=s.replace(/\./g,'');
  const v=parseFloat(s); return isFinite(v)?v:0;
};
const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

if($('tH')){
const KEY='boq-metta-v2';
const BASE={hollow:DATA.hollow, plate:DATA.plate, other:DATA.other||[]};
const clone=o=>JSON.parse(JSON.stringify(o));
const OFFER0=()=>({
  on:false, edit:false,
  co:{nm:'', addr:'', tel:'', email:'', logo:''},
  cl:{nm:'', loc:'Gedung METTA \u2014 Lantai 4 (+16.00)', no:'', rev:'0'},
  dt:{issue:'', valid:14, start:'', end:''},
  terms:[],
  sched:[{nm:'Fabrikasi di bengkel', w0:1, dur:3},
         {nm:'Pengiriman ke site', w0:4, dur:1},
         {nm:'Erection & sambungan', w0:4, dur:2},
         {nm:'Finishing cat & railing', w0:6, dur:1},
         {nm:'Serah terima', w0:7, dur:1}],
  scope:['Jasa fabrikasi dan pemasangan komponen baja yang tercantum pada BOQ.',
         'Dasar pengukuran jasa: berat pembelian lonjor dan lembar baja, termasuk sisa potong.',
         'Material dihitung terpisah sesuai baris BOQ yang diberi harga.'],
  excl:['Listrik kerja & air kerja di lokasi', 'Akses alat angkat / lift barang gedung',
        'Izin kerja gedung dan biaya administrasi pengelola', 'Pekerjaan sipil & perbaikan lantai eksisting'],
  tnc:['Harga berlaku selama masa berlaku penawaran di atas.',
       'Harga sudah termasuk PPN sesuai rekap.',
       'Perubahan lingkup dihitung sebagai pekerjaan tambah/kurang.'],
  sign:{nm:'', role:''}
});
let S={price:false, mode:'satuan', unitAll:'auto', edit:false, wH:5, wP:10, bar:6, ohp:10, ppn:0,
       rev:DATA.rev, rows:clone(BASE)};
let migrated=0;

function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
function load(){
  try{
    const raw=localStorage.getItem(KEY); if(!raw) return;
    const o=JSON.parse(raw);
    if(!o || !o.rows || !o.rows.hollow) return;
    if(o.rev === DATA.rev){ S=Object.assign(S,o); return; }
    // Model sudah direvisi sejak terakhir dibuka. Kuantitas WAJIB ikut model baru,
    // tapi harga yang sudah susah payah diisi dipindahkan berdasarkan nama item.
    const harga={};
    ['hollow','plate','other'].forEach(k=>(o.rows[k]||[]).forEach(r=>{
      if(r && r.p!=null && r.p!=='') harga[k+'|'+r.nm]=r.p; }));
    S=Object.assign(S,o,{rows:clone(BASE), rev:DATA.rev});
    let pindah=0;
    ['hollow','plate','other'].forEach(k=>S.rows[k].forEach(r=>{
      const p=harga[k+'|'+r.nm];
      if(p!=null){ r.p=p; pindah++; }
    }));
    migrated=pindah+1;   // >0 menandakan terjadi migrasi, walau tak ada harga yang pindah
    save();
  }catch(e){}
}
load();
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

document.getElementById('catalog-prices')?.addEventListener('click',()=>{
 let n=0;
 S.rows.hollow.forEach(r=>{if((r.nm==='Rangka RHS — hasil model'||r.nm==='Kolom — hasil model')&&(r.p==null||r.p==='')){r.p=434500;r.u='btg';n++;}});
 S.rows.plate.forEach(r=>{if(r.nm==='Dek bordes 4 mm — hasil model'&&(r.p==null||r.p==='')){r.p=1273000;r.u='lbr';n++;}});
 S.price=true;document.getElementById('tgPrice').checked=true;save();render();document.getElementById('catalog-price-status').textContent=n+' harga kosong diisi. Harga termasuk PPN pemasok; periksa pajak rekap agar tidak dihitung dua kali.';
});
document.addEventListener('change',e=>{
  const t=e.target;
  if(t.id==='unitAll'){ S.unitAll=t.value; save(); render(); return; }
  if(t.classList && t.classList.contains('usel')){
    const tb=t.dataset.t==='H'?S.rows.hollow:S.rows.plate;
    const row=tb[+t.dataset.i]; if(row){ row.u=t.value; save(); render(); }
  }
});

// ---- satuan harga per mode ----
// Shared purchasing-weight calculation. Waste enters stock counts, never twice.
function computePurchaseService(rows, barLength, sheetArea, hollowBasis, plateBasis, enabled, rate) {
  const positive=x=>Number.isFinite(+x)&&+x>0?+x:0;
  const bar=positive(barLength)||6, sheet=positive(sheetArea)||2.88;
  const items=[
    ...rows.hollow.map(r=>{const b=hollowBasis(r),units=Math.ceil(positive(b.bars));return {name:r.nm,stock:'lonjor',units,netKg:positive(r.L)*positive(r.kg),purchaseKg:units*bar*positive(r.kg)};}),
    ...rows.plate.map(r=>{const b=plateBasis(r),units=Math.ceil(positive(b.sh)),density=positive(r.t)*7.85+positive(r.sur);return {name:r.nm,stock:'lembar',units,netKg:positive(r.A)*density,purchaseKg:units*sheet*density};})
  ];
  const kg=items.reduce((sum,r)=>sum+r.purchaseKg,0);
  const netKg=items.reduce((sum,r)=>sum+r.netKg,0);
  const unitRate=positive(rate);
  return {items,kg,netKg,extraKg:kg-netKg,rate:unitRate,cost:enabled?kg*unitRate:0,enabled:!!enabled};
}
if(typeof module!=='undefined')module.exports={computePurchaseService};

function basisH(r){
  const verified=r.n===165 && r.nm==='Rangka RHS — hasil model' && Math.abs(r.L-418.74)<.005 && S.bar===6 && S.wH===5; const Lw=verified?450:r.L*(1+S.wH/100), kg=Lw*(r.kg||0), bars=verified?75:Math.ceil(Lw/(S.bar||6));
  if(S.mode==='ringkas') return {q:Lw, un:'m', kg, bars, Lw};
  return {q:kg, un:'kg', kg, bars, Lw};
}
function basisP(r){
  const Aw=r.A*(1+S.wP/100), kg=Aw*((r.t||0)*7.85+(r.sur||0)), sh=Math.ceil(Aw/DATA.sheetA);
  if(S.mode==='ringkas') return {q:Aw, un:'m²', kg, sh, Aw};
  if(S.mode==='perkg')   return {q:kg,  un:'kg', kg, sh, Aw};
  return {q:sh, un:'lembar', kg, sh, Aw};
}
const basisO=r=>({q:+r.q||0, un:r.un||'bh'});

// ---- satuan harga: pilihan global + override per baris ----
const UNITS={H:[['kg','kg'],['m','m\u02b9'],['btg','lonjor'],['bh','buah']],
             P:[['kg','kg'],['m2','m\u00b2'],['m3','m\u00b3'],['lbr','lembar'],['bh','buah']]};
const ULAB={kg:'kg',m:'m\u02b9',btg:'lonjor',bh:'buah',m2:'m\u00b2',m3:'m\u00b3',lbr:'lembar'};
const GMAP={H:{kg:'kg',m:'m',m2:null,m3:null,btg:'btg',bh:'bh'},
            P:{kg:'kg',m:null,m2:'m2',m3:'m3',btg:'lbr',bh:'bh'}};
function unitOf(t,r){
  if(r.u && (UNITS[t]||[]).some(x=>x[0]===r.u)) return r.u;
  if(S.unitAll && S.unitAll!=='auto'){const m=GMAP[t][S.unitAll]; if(m) return m;}
  if(t==='H') return S.mode==='ringkas'?'m':'kg';
  return S.mode==='ringkas'?'m2':(S.mode==='perkg'?'kg':'lbr');
}
function qtyU(t,r,B,u){
  if(t==='H') return u==='m'?B.Lw : u==='btg'?B.bars : u==='bh'?(+r.n||0) : B.kg;
  return u==='m2'?B.Aw : u==='m3'?B.Aw*((+r.t||0)/1000) : (u==='lbr'||u==='bh')?B.sh : B.kg;
}
const usel=(t,i,u)=>'<td class="usel-cell"><select class="usel" data-t="'+t+'" data-i="'+i+'">'
  + UNITS[t].map(([v,l])=>`<option value="${v}"${v===u?' selected':''}>${l}</option>`).join('')
  + '</select></td>';

// ---- odometer + bar volume (transform saja, tidak memicu layout) ----
const REDUCE = matchMedia('(prefers-reduced-motion:reduce)').matches;
const ODO={};
const odo=(k,txt)=>`<span class="odo" data-k="${k}">${esc(txt)}</span>`;
function paintOdo(){
  // Currency remains one text node: digit animations obscure totals during edits.
  document.querySelectorAll('.odo').forEach(el=>{ODO[el.dataset.k]=el.textContent;});
}

const vbar=(v,g)=>`<span class="vb" data-v="${v}" data-g="${g}"></span>`;
function paintBars(){
  ['H','P'].forEach(g=>{
    const els=[...document.querySelectorAll('.vb[data-g="'+g+'"]')];
    if(!els.length) return;
    const mx=Math.max(...els.map(e=>+e.dataset.v||0))||1;
    els.forEach(e=>{
      const s2=Math.max(0.02,(+e.dataset.v||0)/mx);
      if(REDUCE){ e.style.transform='scaleX('+s2+')'; return; }
      e.style.transform='scaleX(0)';
      requestAnimationFrame(()=>{e.style.transform='scaleX('+s2+')';});
    });
  });
}

const ed=(t,i,fld,val,cls)=>S.edit
  ? `<td class="${cls||''} cel" contenteditable="plaintext-only" data-t="${t}" data-i="${i}" data-f="${fld}">${esc(val)}</td>`
  : `<td class="${cls||''}">${esc(val)}</td>`;
const price=(t,i,r)=>S.price
  ? `<td class="num"><input class="pin" type="number" min="0" step="1000" data-t="${t}" data-i="${i}" value="${r.p==null?'':r.p}"></td>`
  : '';
const jml=v=>S.price?`<td class="num">${rp(v)}</td>`:'';
const del=(t,i)=>S.edit?`<td class="num"><button type="button" class="delrow" data-t="${t}" data-i="${i}" title="Hapus baris">×</button></td>`:'';

function head(cols){
  return '<tr>'+cols.map(c=>`<th class="${c[1]||''}">${c[0]}</th>`).join('')+'</tr>';
}

function render(){
  const wH=1+S.wH/100, wP=1+S.wP/100, BAR=S.bar||6;
  let sumH=0,sumBar=0,costH=0;

  // ---- profil hollow ----
  let cols=[['Elemen'],['Profil'],['Btg','num'],['Panjang (m)','num'],['+waste','num'],
            ['kg/m','num'],['Berat (kg)','num'],['Lonjor','num']];
  if(S.price) cols=cols.concat([['Satuan harga'],['Harga satuan','num'],['Jumlah','num']]);
  cols.push(['Catatan']); if(S.edit) cols.push(['','num']);
  $('tH').tHead.innerHTML=head(cols);
  let tb='';
  S.rows.hollow.forEach((r,i)=>{
    const B=basisH(r); sumH+=B.kg; sumBar+=B.bars;
    const u=unitOf('H',r), qu=qtyU('H',r,B,u);
    const j=(+r.p||0)*qu; costH+=j;
    tb+='<tr>'+ed('H',i,'nm',r.nm)+ed('H',i,'pr',r.pr)+ed('H',i,'n',r.n,'num')
      + ed('H',i,'L',f(r.L,2),'num')
      + `<td class="num">${f(B.Lw,2)}</td>`+ed('H',i,'kg',f(r.kg,2),'num')
      + `<td class="num">${vbar(B.kg,'H')}${f(B.kg,0)}</td><td class="num">${B.bars}</td>`
      + (S.price?usel('H',i,u):'')+price('H',i,r)+jml(j)+ed('H',i,'note',r.note)+del('H',i)+'</tr>';
  });
  $('tH').tBodies[0].innerHTML=tb;
  $('tH').tFoot.innerHTML='<tr><td colspan="6">Subtotal profil hollow</td>'
    + `<td class="num">${odo('sH',f(sumH,0)+' kg')}</td><td class="num">${sumBar}</td>`
    + (S.price?`<td></td><td></td><td class="num">${odo('cH',rp(costH))}</td>`:'')
    + '<td></td>'+(S.edit?'<td></td>':'')+'</tr>';

  // ---- pelat ----
  let sumP=0,sumSh=0,costP=0;
  cols=[['Elemen'],['Tebal (mm)','num'],['Luas (m²)','num'],['+waste','num'],
        ['Berat (kg)','num'],['Lembar 1220×2440','num']];
  if(S.price) cols=cols.concat([['Satuan harga'],['Harga satuan','num'],['Jumlah','num']]);
  cols.push(['Catatan']); if(S.edit) cols.push(['','num']);
  $('tP').tHead.innerHTML=head(cols);
  tb='';
  S.rows.plate.forEach((r,i)=>{
    const B=basisP(r); sumP+=B.kg; sumSh+=B.sh;
    const u=unitOf('P',r), qu=qtyU('P',r,B,u);
    const j=(+r.p||0)*qu; costP+=j;
    tb+='<tr>'+ed('P',i,'nm',r.nm)+ed('P',i,'t',r.t,'num')+ed('P',i,'A',f(r.A,2),'num')
      + `<td class="num">${f(B.Aw,2)}</td><td class="num">${vbar(B.kg,'P')}${f(B.kg,0)}</td>`
      + `<td class="num">${B.sh}</td>`
      + (S.price?usel('P',i,u):'')+price('P',i,r)+jml(j)+ed('P',i,'note',r.note)+del('P',i)+'</tr>';
  });
  $('tP').tBodies[0].innerHTML=tb;
  $('tP').tFoot.innerHTML='<tr><td colspan="4">Subtotal pelat</td>'
    + `<td class="num">${odo('sP',f(sumP,0)+' kg')}</td><td class="num">${sumSh}</td>`
    + (S.price?`<td></td><td></td><td class="num">${odo('cP',rp(costP))}</td>`:'')
    + '<td></td>'+(S.edit?'<td></td>':'')+'</tr>';

  // ---- material lain ----
  let costO=0;
  cols=[['Item'],['Jumlah','num'],['Satuan']];
  if(S.price) cols=cols.concat([['Harga satuan','num'],['Jumlah','num']]);
  cols.push(['Catatan']); if(S.edit) cols.push(['','num']);
  $('tO').tHead.innerHTML=head(cols);
  tb='';
  S.rows.other.forEach((r,i)=>{
    const B=basisO(r); const j=(+r.p||0)*B.q; costO+=j;
    tb+='<tr>'+ed('O',i,'nm',r.nm)+ed('O',i,'q',f(r.q,(r.q%1)?3:0),'num')+ed('O',i,'un',r.un)
      + price('O',i,r)+jml(j)+ed('O',i,'note',r.note)+del('O',i)+'</tr>';
  });
  $('tO').tBodies[0].innerHTML=tb;
  $('tO').tFoot.innerHTML = S.price
    ? `<tr><td colspan="${3+(S.price?1:0)}">Subtotal material lain</td>`
      + `<td class="num">${odo('cO',rp(costO))}</td><td></td>${S.edit?'<td></td>':''}</tr>`
    : '';

  const job=serviceCost();syncServiceUI();
  $('grand').innerHTML=odo('grand',f(job.kg/1000,2)+' ton');
  const _sub=costH+costP+costO+job.cost, _oh=_sub*S.ohp/100, _pre=_sub+_oh, _tax=_pre*S.ppn/100;
  TOT={costJ:job.cost,serviceKg:job.kg,serviceRate:job.rate,costH:costH,costP:costP,costO:costO,sub:_sub,oh:_oh,pre:_pre,tax:_tax,
       total:_pre+_tax,kg:job.kg};

  // ---- rekap harga ----
  const rk=$('rekap');
  if(S.price){
    const sub=costH+costP+costO+job.cost;
    let rows=[['Profil hollow',costH],['Pelat baja',costP],['Material lain',costO],['Jasa fabrikasi & pemasangan (berat pembelian)',job.cost]];
    let html='<h3 class="sub">Rekapitulasi biaya</h3><div class="tw"><table><tbody>';
    rows.forEach((r,ri)=>html+=`<tr><td>${r[0]}</td><td class="num">${odo('rk'+ri,rp(r[1]))}</td></tr>`);
    html+=`<tr><td><b>Subtotal</b></td><td class="num"><b>${odo('rksub',rp(sub))}</b></td></tr>`;
    let total=sub;
    if(true){
      const oh=sub*S.ohp/100, pre=sub+oh, tax=pre*S.ppn/100; total=pre+tax;
      html+=`<tr><td>Overhead &amp; keuntungan ${S.ohp}%</td><td class="num">${rp(oh)}</td></tr>`
          + `<tr><td>Jumlah sebelum pajak</td><td class="num">${rp(pre)}</td></tr>`
          + `<tr><td>PPN ${S.ppn}%</td><td class="num">${rp(tax)}</td></tr>`;
    }
    html+=`</tbody><tfoot><tr><td>TOTAL</td><td class="num">${odo('rktot',rp(total))}</td></tr>`;
    const kg=job.kg;
    html+=`<tr><td>Biaya per kg baja</td><td class="num">${kg?rp(total/kg):'—'}</td></tr>`;
    html+='</tfoot></table></div>';
    rk.innerHTML=html; rk.hidden=false;
  } else { rk.innerHTML=''; rk.hidden=true; }

  const rn=$('revNote');
  if(rn){
    if(migrated){
      rn.innerHTML='Kuantitas di tabel ini baru saja disesuaikan dengan <b>revisi terakhir model</b>. '
        + (migrated>1 ? 'Harga satuan yang sudah kamu isi tetap dipertahankan untuk item yang namanya sama. '
                      : '')
        + 'Kalau kamu sengaja mengedit tabel sebelumnya, editan itu diganti — tekan Reset untuk memastikan.';
      rn.hidden=false;
    } else rn.hidden=true;
  }
  document.querySelectorAll('.ponly').forEach(e=>e.hidden=!S.price);
  $('segMode').hidden=!S.price;
  const ua=$('unitAll'); if(ua) ua.value=S.unitAll||'auto';
  paintOdo(); paintBars(); if(window.__ofCalc) __ofCalc();
  document.querySelectorAll('.addrow').forEach(e=>e.hidden=!S.edit);
  document.querySelectorAll('#segMode button').forEach(bm=>
    bm.classList.toggle('on', bm.dataset.mode===S.mode));
  cutlist();
}

function cutlist(){
  const tc=$('tCut'); if(!tc) return;
  const tb=tc.tBodies[0]; tb.innerHTML='';
  S.rows.hollow.forEach(r=>{
    const B=basisH(r), buy=B.bars*(S.bar||6);
    tb.insertAdjacentHTML('beforeend',
      `<tr><td>${esc(r.nm)} — ${esc(r.pr)}</td><td class="num">${f(r.L,1)} m</td>
       <td class="num">${B.bars} lonjor (${f(buy,1)} m)</td>
       <td class="num">${f(buy-r.L,1)} m</td><td>lonjor ${S.bar} m</td></tr>`);
  });
  S.rows.plate.forEach(r=>{const t=r.t,A=+r.A||0;
    const Aw=A*(1+S.wP/100), sh=Math.ceil(Aw/DATA.sheetA), buy=sh*DATA.sheetA;
    tb.insertAdjacentHTML('beforeend',
      `<tr><td>${esc(r.nm)} / ${t} mm</td><td class="num">${f(A,2)} m²</td>
       <td class="num">${sh} lembar (${f(buy,2)} m²)</td>
       <td class="num">${f(buy-A,2)} m²</td><td>lembar 1220 × 2440</td></tr>`);
  });
}

// ---- interaksi ----
const arr=t=>t==='H'?S.rows.hollow:t==='P'?S.rows.plate:S.rows.other;
const NUMF={n:1,L:1,kg:1,t:1,A:1,q:1};

document.addEventListener('input',e=>{
  const el=e.target;
  if(el.classList && el.classList.contains('pin')){
    const r=arr(el.dataset.t)[+el.dataset.i];
    if(r){ r.p=el.value===''?null:+el.value; save();
      // Keep the focused input and caret intact until the edit is committed.
    }
    return;
  }
  if(['wH','wP','bar','ohp','ppn'].indexOf(el.id)>=0){
    S[el.id]=+el.value||0; save();
  }
});
document.addEventListener('change',e=>{const el=e.target;if(el.classList?.contains('pin')||['wH','wP','bar','ohp','ppn'].includes(el.id))render();});
document.addEventListener('blur',e=>{
  const el=e.target;
  if(!el.classList || !el.classList.contains('cel')) return;
  const r=arr(el.dataset.t)[+el.dataset.i]; if(!r) return;
  const fld=el.dataset.f;
  r[fld]= NUMF[fld] ? pn(el.textContent) : el.textContent.trim();
  save(); render();
}, true);

document.addEventListener('click',e=>{
  const b=e.target.closest ? e.target.closest('button') : null; if(!b) return;
  if(b.dataset.mode){ S.mode=b.dataset.mode; save(); render(); return; }
  if(b.dataset.add){
    const t=b.dataset.add;
    if(t==='H') S.rows.hollow.push({nm:'Item baru',pr:'',n:1,L:0,kg:0,note:''});
    if(t==='P') S.rows.plate.push({nm:'Item baru',t:0,A:0,note:''});
    if(t==='O') S.rows.other.push({nm:'Item baru',q:0,un:'bh',note:''});
    save(); render(); return;
  }
  if(b.classList.contains('delrow')){
    arr(b.dataset.t).splice(+b.dataset.i,1); save(); render(); return;
  }
  if(b.id==='exXls'){ copyTSV(b); return; }
  if(b.id==='exPdf'){ toPrint(b); return; }
  if(b.id==='exJson'){ copyJSON(b); return; }
  if(b.id==='exXlsx'){ downloadXlsx(b); return; }
  if(b.id==='exLoad'){ const bx=$('exLoadBox'); bx.hidden=!bx.hidden;
    if(!bx.hidden) $('exCode').focus(); return; }
  if(b.id==='exApply'){ applyCode(); return; }
  if(b.id==='boqReset'){
    if(b.dataset.armed){ 
      S={price:S.price,mode:S.mode,unitAll:S.unitAll,edit:S.edit,wH:5,wP:10,bar:6,ohp:10,ppn:0,
         rev:DATA.rev,rows:clone(BASE),fabrication:{enabled:true,rate:6000}};
      migrated=0;
      try{ localStorage.removeItem(KEY); }catch(e2){}
      $('wH').value=5; $('wP').value=10; $('bar').value=6; $('ohp').value=10; $('ppn').value=0;
      b.textContent='Reset ke default'; delete b.dataset.armed; render();
    } else {
      b.dataset.armed='1'; b.textContent='Yakin? klik lagi';
      setTimeout(()=>{ if(b.dataset.armed){ b.textContent='Reset ke default'; delete b.dataset.armed; } },4000);
    }
  }
});

['tgPrice','tgEdit','tgExport'].forEach(id=>{
  const el=$(id); if(!el) return;
  el.addEventListener('change',()=>{
    if(id==='tgPrice') S.price=el.checked;
    else if(id==='tgEdit') S.edit=el.checked;
    else { S.exp=el.checked; $('exportbox').hidden=!el.checked; }
    save(); render();
  });
});


// ---- unduhan berkas nyata hanya jalan di luar sandbox artifact ----
const CAN_DL = !/(^|\.)claude\.ai$/i.test(location.hostname);
function projName(){
  const v=($('exProj')&&$('exProj').value||'').trim();
  return v || 'BOQ';
}
function slug(s){ return s.replace(/[^\wÀ-ɏ -]/g,'').replace(/\s+/g,'-').slice(0,60) || 'BOQ'; }

function workbook(){
  const s=XL.S, P=projName();
  // ---------- INPUT ----------
  const inp=[];
  inp[0]=[{t:'PARAMETER — ubah di sini, seluruh BOQ ikut berubah',s:s.title}];
  inp[1]=[{t:P}];
  const par=[['Waste profil hollow',S.wH/100],['Waste pelat baja',S.wP/100],
             ['Panjang lonjor hollow (m)',S.bar],['Luas lembar pelat (m²)',DATA.sheetA],
             ['Berat jenis pelat (kg/m²/mm)',7.85],['Overhead & keuntungan',S.ohp/100],
             ['PPN',S.ppn/100]];
  par.forEach((p,i)=>{ inp[i+2]=[{t:p[0]}, {n:p[1], s:s.n2}]; });
  inp[10]=[{t:'Isi kolom Harga Satuan (kuning) di lembar BOQ. Kolom lain rumus.'}];
  inp[11]=[{t:'B3:B9: parameter BOQ. B13: tarif jasa. B14: 1 aktif / 0 nonaktif.'}];
  inp[12]=[{t:'Tarif fabrikasi & pemasangan (Rp/kg)'},{n:serviceCost().rate,s:s.inp}];
  inp[13]=[{t:'Aktifkan jasa per kg (1/0)'},{n:serviceCost().enabled?1:0,s:s.inp}];
  inp[14]=[{t:'Dasar jasa: berat pembelian, termasuk pembulatan lonjor/lembar.'}];
  inp[15]=[{t:'Harga material terpisah; tarif jasa belum termasuk overhead dan PPN rekap.'}];

  // ---------- BOQ ----------
  const W_H='INPUT!$B$3', W_P='INPUT!$B$4', BARC='INPUT!$B$5',
        SHA='INPUT!$B$6', RHO='INPUT!$B$7';
  const weightRows=[[{t:'BERAT PEMBELIAN — DASAR JASA',s:s.title}],[],['Uraian','Stok beli','Satuan','kg/stok','Berat beli (kg)'].map(t=>({t,s:s.head}))];
  const rows=[];
  rows[0]=[{t:'BILL OF QUANTITY — '+P, s:s.title}];
  rows[1]=[{t:'Kuantitas dari model METTA.rvt · mode harga: '+S.mode
            +' · satuan: '+(S.unitAll==='auto'?'bawaan tiap baris':ULAB[S.unitAll]||S.unitAll)}];
  const H=['No','Uraian pekerjaan','Spesifikasi','Btg/Bh','Volume model','Volume + waste',
           'Satuan','Berat (kg)','Beli (lonjor/lembar)','Harga satuan','Satuan harga','Jumlah','Catatan'];
  rows[3]=H.map(t=>({t:t,s:s.head}));
  let r=4, no=0;
  const ring = S.mode==='ringkas', perkg = S.mode==='perkg';

  rows[r]=[{t:'A.  PROFIL HOLLOW', s:s.sec}]; r++;
  const aStart=r+1;
  S.rows.hollow.forEach(x=>{
    no++; const R=r+1, W=weightRows.length+1;
    weightRows.push([{t:x.nm},{f:`BOQ!I${R}`,s:s.n0},{t:'lonjor'},{f:`INPUT!$B$5*${(+x.kg||0)}`,s:s.n2},{f:`B${W}*D${W}`,s:s.n2}]);
    rows[r]=[{n:no},{t:x.nm},{t:x.pr},{n:+x.n||0},{n:+x.L||0,s:s.n2},
             {f:`IF(AND(B${R}="Rangka RHS — hasil model",D${R}=165,ABS(E${R}-418.74)<0.005,${BARC}=6,${W_H}=0.05),450,E${R}*(1+${W_H}))`,s:s.n2},{t:'m'},
             {f:`F${R}*${(+x.kg||0)}`,s:s.n0},{f:`ROUNDUP(F${R}/${BARC},0)`,s:s.n0},
             {n:(x.p==null?null:+x.p),s:s.inp},{t:'Rp / '+ULAB[unitOf('H',x)]},
             {f:(uu=>uu==='m'?`F${R}*J${R}`:uu==='btg'?`I${R}*J${R}`:uu==='bh'?`D${R}*J${R}`
                 :`H${R}*J${R}`)(unitOf('H',x)),s:s.rp},{t:x.note}];
    r++;
  });
  const aEnd=r, aSub=r+1;
  rows[r]=[null,{t:'Subtotal A — profil hollow',s:s.bold},null,null,null,null,null,
           {f:`SUM(H${aStart}:H${aEnd})`,s:s.n0},{f:`SUM(I${aStart}:I${aEnd})`,s:s.n0},
           null,null,{f:`SUM(L${aStart}:L${aEnd})`,s:s.rp}];
  r+=2;

  rows[r]=[{t:'B.  PELAT BAJA', s:s.sec}]; r++;
  const bStart=r+1;
  S.rows.plate.forEach(x=>{
    no++; const R=r+1, W=weightRows.length+1;
    weightRows.push([{t:x.nm},{f:`BOQ!I${R}`,s:s.n0},{t:'lembar'},{f:`INPUT!$B$6*(${(+x.t||0)}*INPUT!$B$7+${(+x.sur||0)})`,s:s.n2},{f:`B${W}*D${W}`,s:s.n2}]);
    rows[r]=[{n:no},{t:x.nm},{t:'tebal '+(x.t)+' mm'},null,{n:+x.A||0,s:s.n2},
             {f:`E${R}*(1+${W_P})`,s:s.n2},{t:'m²'},
             {f:`F${R}*(${(+x.t||0)}*${RHO}+${(+x.sur||0)})`,s:s.n0},{f:`ROUNDUP(F${R}/${SHA},0)`,s:s.n0},
             {n:(x.p==null?null:+x.p),s:s.inp},
             {t:'Rp / '+ULAB[unitOf('P',x)]},
             {f:(uu=>uu==='m2'?`F${R}*J${R}`:uu==='m3'?`F${R}*${(+x.t||0)}/1000*J${R}`
                 :(uu==='lbr'||uu==='bh')?`I${R}*J${R}`:`H${R}*J${R}`)(unitOf('P',x)),s:s.rp},{t:x.note}];
    r++;
  });
  const bEnd=r, bSub=r+1;
  rows[r]=[null,{t:'Subtotal B — pelat baja',s:s.bold},null,null,null,null,null,
           {f:`SUM(H${bStart}:H${bEnd})`,s:s.n0},{f:`SUM(I${bStart}:I${bEnd})`,s:s.n0},
           null,null,{f:`SUM(L${bStart}:L${bEnd})`,s:s.rp}];
  r+=2;

  rows[r]=[{t:'C.  MATERIAL LAIN', s:s.sec}]; r++;
  const cStart=r+1;
  S.rows.other.forEach(x=>{
    no++; const R=r+1;
    rows[r]=[{n:no},{t:x.nm},null,null,{n:+x.q||0,s:s.n2},{f:`E${R}`,s:s.n2},{t:x.un},
             null,null,{n:(x.p==null?null:+x.p),s:s.inp},{t:'Rp / '+(x.un||'bh')},
             {f:`F${R}*J${R}`,s:s.rp},{t:x.note}];
    r++;
  });
  const cEnd=r, cSub=r+1;
  rows[r]=[null,{t:'Subtotal C — material lain',s:s.bold},null,null,null,null,null,null,null,
           null,null,{f:`SUM(L${cStart}:L${cEnd})`,s:s.rp}];

  const endWeight=weightRows.length;
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
  ]);
}

function downloadXlsx(btn){
  try{
    const bytes=workbook();
    const blob=new Blob([bytes],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
    const url=URL.createObjectURL(blob), a=document.createElement('a');
    a.href=url; a.download=slug(projName())+'.xlsx';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),4000);
    const lab=btn.querySelector('b'), o=lab.textContent;
    lab.textContent='Berkas dibuat'; setTimeout(()=>lab.textContent=o,2200);
  }catch(e){
    btn.querySelector('span').textContent='Gagal membuat berkas: '+e.message;
  }
}

function applyCode(){
  const msg=$('exMsg'), raw=($('exCode').value||'').trim();
  const i=raw.indexOf('{');
  try{
    if(i<0) throw new Error('kode tidak dikenali');
    const o=JSON.parse(raw.slice(i));
    if(!o || !o.hollow || !o.plate) throw new Error('isi kode tidak lengkap');
    S.rows={hollow:o.hollow, plate:o.plate, other:o.other||[]};
    ['wH','wP','bar','ohp','ppn'].forEach(k=>{ if(typeof o[k]==='number') S[k]=o[k]; });
    if(o.mode) S.mode=o.mode;
    if(o.fabrication)S.fabrication={enabled:!!o.fabrication.enabled,rate:Math.max(0,Number(o.fabrication.rate)||0)};
  if(o.offer) S.offer=Object.assign(OFFER0(), o.offer);
    $('wH').value=S.wH; $('wP').value=S.wP; $('bar').value=S.bar;
    $('ohp').value=S.ohp; $('ppn').value=S.ppn;
    save(); render();
    msg.textContent='Kode diterapkan.'; msg.className='exmsg ok';
  }catch(e){
    msg.textContent='Gagal: '+e.message; msg.className='exmsg bad';
  }
  setTimeout(()=>{ msg.textContent=''; },4000);
}

function exportUI(){
  const note=$('exNote'); if(!note) return;
  document.querySelectorAll('.dlonly').forEach(e=>e.hidden=!CAN_DL);
  note.innerHTML = CAN_DL
    ? 'Berkas Excel dibuat langsung di browsermu — tidak ada data yang dikirim ke mana pun. '
      + 'Rumusnya hidup: ubah waste, harga, atau PPN di lembar <b>INPUT</b>, seluruh total ikut berubah.'
    : 'Catatan jujur: di halaman claude.ai ini unduhan berkas diblokir sandbox. PDF lewat dialog '
      + 'cetak browser, Excel lewat tempel, dan berkas .xlsx berumus dibuat dari <b>kode BOQ</b>. '
      + 'Kalau halaman ini dipasang di alamatmu sendiri, tombol unduh langsung akan muncul.';
}

// ---- cetak: sembunyikan sementara mode edit supaya sel tidak berbingkai ----
function toPrint(btn){
  const wasEdit=S.edit;
  if(wasEdit){ S.edit=false; render(); }
  document.body.classList.add('printing');
  const back=()=>{
    document.body.classList.remove('printing');
    if(wasEdit){ S.edit=true; render(); }
  };
  const mq=window.matchMedia('print');
  const off=()=>{ back(); mq.removeEventListener && mq.removeEventListener('change',onch); };
  const onch=e=>{ if(!e.matches) off(); };
  if(mq.addEventListener) mq.addEventListener('change',onch);
  addEventListener('afterprint', back, {once:true});
  setTimeout(()=>{
    try{ window.print(); }
    catch(e){ back(); btn.querySelector('span').textContent =
      'Dialog cetak diblokir di tampilan ini — buka halaman di tab browser sendiri, lalu Ctrl+P.'; }
    setTimeout(back, 1500);
  }, 60);
}

function copyJSON(btn){
  const payload={v:2, proyek:'Tribun METTA LT 4', mode:S.mode,
    wH:S.wH, wP:S.wP, bar:S.bar, ohp:S.ohp, ppn:S.ppn,
    hollow:S.rows.hollow, plate:S.rows.plate, other:S.rows.other, offer:S.offer, fabrication:S.fabrication};
  const txt='BOQ-METTA '+JSON.stringify(payload);
  const done=()=>{ const o=btn.querySelector('b').textContent;
    btn.querySelector('b').textContent='Kode tersalin';
    setTimeout(()=>btn.querySelector('b').textContent=o,2200); };
  if(navigator.clipboard && navigator.clipboard.writeText)
    navigator.clipboard.writeText(txt).then(done,()=>fallback(txt,done));
  else fallback(txt,done);
}

function copyTSV(btn){
  const out=[];
  const tbl=(id,title)=>{
    const t=$(id); if(!t) return;
    out.push(title);
    [...t.querySelectorAll('tr')].forEach(tr=>{
      out.push([...tr.children].map(td=>{
        const inp=td.querySelector('input');
        return (inp?inp.value:td.textContent).replace(/\s+/g,' ').trim();
      }).join('\t'));
    });
    out.push('');
  };
  tbl('tH','PROFIL HOLLOW'); tbl('tP','PELAT BAJA'); tbl('tO','MATERIAL LAIN');
  if(S.price){ out.push('REKAPITULASI');
    $('rekap').querySelectorAll('tr').forEach(tr=>
      out.push([...tr.children].map(td=>td.textContent.trim()).join('\t'))); }
  const txt=out.join('\n');
  const lab=btn.querySelector('b')||btn;
  const done=()=>{ const o=lab.textContent; lab.textContent='Tersalin — tempel di Excel';
    setTimeout(()=>lab.textContent=o,2200); };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).then(done,()=>fallback(txt,done));
  } else fallback(txt,done);
}
function fallback(txt,done){
  const ta=document.createElement('textarea');
  ta.value=txt; ta.style.position='fixed'; ta.style.opacity='0';
  document.body.appendChild(ta); ta.select();
  try{ document.execCommand('copy'); done(); }catch(e){}
  ta.remove();
}


// ================= PENAWARAN =================
let TOT={costJ:0,serviceKg:0,serviceRate:6000,costH:0,costP:0,costO:0,sub:0,oh:0,pre:0,tax:0,total:0,kg:0};
const OF=()=>S.offer||(S.offer=OFFER0());
const dstr=v=>{ if(!v) return '—';
  const d=new Date(v+'T00:00:00'); if(isNaN(d)) return '—';
  const B=['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
  return d.getDate()+' '+B[d.getMonth()]+' '+d.getFullYear(); };
function addDays(v,n){ const d=new Date(v+'T00:00:00'); if(isNaN(d)) return '';
  d.setDate(d.getDate()+n); return d.toISOString().slice(0,10); }
function workdays(a,b){ if(!a||!b) return 0;
  let d=new Date(a+'T00:00:00'), e=new Date(b+'T00:00:00'), n=0;
  if(isNaN(d)||isNaN(e)||e<d) return 0;
  while(d<=e){ const w=d.getDay(); if(w!==0&&w!==6) n++; d.setDate(d.getDate()+1); }
  return n; }
const ofNo=()=>{ const o=OF(); if(o.cl.no) return o.cl.no;
  const y=(o.dt.issue||new Date().toISOString().slice(0,10)).slice(0,4);
  return 'PN/'+y+'/001'; };
const ip=(path,val,type,ph)=>`<input class="ofin" data-of="${path}" type="${type||'text'}" `
  + `value="${String(val==null?'':val).replace(/"/g,'&quot;')}" placeholder="${ph||''}">`;

function ofWeeks(){ const o=OF();
  let n=0; o.sched.forEach(r=>n=Math.max(n,(+r.w0||1)+(+r.dur||1)-1));
  return Math.max(4, Math.min(26, n)); }

function renderOffer(){
  const box=$('ofbox'); if(!box) return;
  const o=OF(); box.hidden=!o.on;
  const tg=$('tgOffer'); if(tg) tg.checked=!!o.on;
  const te=$('tgOfEdit'); if(te) te.checked=!!o.edit;
  if(!o.on){ return; }
  const ed=o.edit;
  const t=(v,ph)=>ed?'':(v||`<span class="ofph">${ph||'—'}</span>`);
  const H=[];
  H.push('<article class="ofpage">');
  // kop
  H.push('<header class="ofhead"><div class="ofco">');
  H.push(ed?ip('co.nm',o.co.nm,'text','Nama perusahaan'):`<div class="ofconm">${esc(o.co.nm)||'<span class="ofph">Nama perusahaan</span>'}</div>`);
  H.push(ed?ip('co.addr',o.co.addr,'text','Alamat'):`<div class="ofcosm">${esc(o.co.addr)}</div>`);
  H.push(ed?ip('co.tel',o.co.tel,'text','Telepon'):`<div class="ofcosm">${esc(o.co.tel)}</div>`);
  H.push(ed?ip('co.email',o.co.email,'text','Email'):`<div class="ofcosm">${esc(o.co.email)}</div>`);
  H.push('</div><div class="oflogo">');
  H.push(o.co.logo?`<img src="${o.co.logo}" alt="logo">`:'<span class="ofph">logo</span>');
  if(ed) H.push('<label class="oflogobtn">Unggah logo<input type="file" id="ofLogo" accept="image/*" hidden></label>');
  H.push('</div></header>');
  H.push('<h3 class="oftitle">Surat Penawaran Harga</h3>');
  // meta
  const rows=[['No. penawaran', ed?ip('cl.no',o.cl.no,'text',ofNo()):esc(ofNo())],
              ['Revisi', ed?ip('cl.rev',o.cl.rev):esc(o.cl.rev)],
              ['Kepada', ed?ip('cl.nm',o.cl.nm,'text','Nama klien'):(esc(o.cl.nm)||t('','Nama klien'))],
              ['Lokasi', ed?ip('cl.loc',o.cl.loc):esc(o.cl.loc)],
              ['Tanggal', ed?ip('dt.issue',o.dt.issue,'date'):dstr(o.dt.issue)],
              ['Berlaku', ed?(ip('dt.valid',o.dt.valid,'number')+' hari'):
                 (o.dt.valid?`${o.dt.valid} hari — s/d ${dstr(addDays(o.dt.issue,+o.dt.valid))}`:'—')],
              ['Rencana mulai', ed?ip('dt.start',o.dt.start,'date'):dstr(o.dt.start)],
              ['Rencana selesai', ed?ip('dt.end',o.dt.end,'date'):dstr(o.dt.end)],
              ['Durasi', `<span id="ofDur">—</span>`]];
  H.push('<div class="ofmeta">');
  rows.forEach(r=>H.push(`<div class="ofmr"><span>${r[0]}</span><span>${r[1]}</span></div>`));
  H.push('</div>');
  // rekap
  H.push('<h4 class="ofh4">A. Rekapitulasi biaya</h4>');
  H.push('<table class="oftab" id="ofRekap"><tbody></tbody></table>');
  // termin
  H.push('<h4 class="ofh4">B. Termin pembayaran'
    + (ed?' <button type="button" class="addrow" data-ofadd="terms">+ termin</button>':'')
    + '</h4>');
  H.push('<table class="oftab" id="ofTerm"><thead><tr><th style="width:34px">#</th><th>Tahap / syarat</th>'
    + '<th class="num" style="width:78px">%</th><th class="num" style="width:150px">Nominal</th>'
    + (ed?'<th style="width:36px"></th>':'') + '</tr></thead><tbody></tbody><tfoot></tfoot></table>');
  H.push('<p class="ofnote" id="ofTermNote"></p>');
  // jadwal
  H.push('<h4 class="ofh4">C. Jadwal pelaksanaan'
    + (ed?' <button type="button" class="addrow" data-ofadd="sched">+ tahap</button>':'')
    + '</h4>');
  H.push('<div class="ofgantt" id="ofGantt"></div>');
  // lingkup
  H.push('<div class="ofcols">');
  H.push('<div><h4 class="ofh4">D. Lingkup pekerjaan'
    + (ed?' <button type="button" class="addrow" data-ofadd="scope">+</button>':'') + '</h4>'
    + '<ul class="oflist" id="ofScope"></ul></div>');
  H.push('<div><h4 class="ofh4">E. Tidak termasuk'
    + (ed?' <button type="button" class="addrow" data-ofadd="excl">+</button>':'') + '</h4>'
    + '<ul class="oflist" id="ofExcl"></ul></div>');
  H.push('</div>');
  // syarat + ttd
  H.push('<h4 class="ofh4">F. Syarat &amp; ketentuan'
    + (ed?' <button type="button" class="addrow" data-ofadd="tnc">+</button>':'') + '</h4>'
    + '<ol class="oflist ofnum" id="ofTnc"></ol>');
  H.push('<div class="ofsign"><div class="ofsigbox">'
    + '<div class="ofsigd">Hormat kami,</div><div class="ofsigsp"></div>'
    + (ed?ip('sign.nm',o.sign.nm,'text','Nama penanda tangan'):`<div class="ofsignm">${esc(o.sign.nm)||'<span class="ofph">Nama</span>'}</div>`)
    + (ed?ip('sign.role',o.sign.role,'text','Jabatan'):`<div class="ofsigrl">${esc(o.sign.role)}</div>`)
    + '</div></div>');
  H.push('</article>');
  $('ofdoc').innerHTML=H.join('');
  ofCalc();
}

function ofCalc(){
  const o=OF(); if(!o.on) return;
  const d=$('ofDur'); if(d){ const n=workdays(o.dt.start,o.dt.end);
    d.textContent = n? (n+' hari kerja') : '—'; }
  // rekap
  const rk=$('ofRekap'); if(rk){
    const R=[['Profil hollow',TOT.costH],['Pelat baja',TOT.costP],['Material lain',TOT.costO],['Jasa fabrikasi & pemasangan — '+f(TOT.serviceKg,2)+' kg × '+rp(TOT.serviceRate)+'/kg'+(S.fabrication?.enabled?'':' (nonaktif)'),TOT.costJ||0]];
    let h='';
    R.forEach(r=>h+=`<tr><td>${r[0]}</td><td class="num">${rp(r[1])}</td></tr>`);
    h+=`<tr><td>Subtotal</td><td class="num">${rp(TOT.sub)}</td></tr>`;
    h+=`<tr><td>Overhead &amp; keuntungan ${S.ohp}%</td><td class="num">${rp(TOT.oh)}</td></tr>`;
    h+=`<tr><td>PPN ${S.ppn}%</td><td class="num">${rp(TOT.tax)}</td></tr>`;
    h+=`<tr class="ofsum"><td>NILAI PENAWARAN</td><td class="num">${odo('ofTot',rp(TOT.total))}</td></tr>`;
    rk.tBodies[0].innerHTML=h;
  }
  // termin
  const tt=$('ofTerm');
  if(tt){
    const ed=o.edit; let h='', sum=0;
    o.terms.forEach((r,i)=>{
      const pct=+r.pct||0; sum+=pct;
      h+=`<tr><td class="num">${i+1}</td>`
       + `<td>${ed?ip('terms.'+i+'.nm',r.nm,'text','mis. DP saat SPK'):esc(r.nm||'')}</td>`
       + `<td class="num">${ed?ip('terms.'+i+'.pct',r.pct,'number'):(pct+'%')}</td>`
       + `<td class="num">${rp(TOT.total*pct/100)}</td>`
       + (ed?`<td class="num"><button type="button" class="delrow" data-ofdel="terms" data-i="${i}">×</button></td>`:'')
       + '</tr>';
    });
    if(!o.terms.length) h='<tr><td colspan="'+(o.edit?5:4)+'" class="ofph">Belum ada termin — nyalakan <b>Edit isi</b> lalu tekan <b>+ termin</b>.</td></tr>';
    tt.tBodies[0].innerHTML=h;
    tt.tFoot.innerHTML = o.terms.length
      ? `<tr><td></td><td>Jumlah</td><td class="num">${f(sum,sum%1?1:0)}%</td>`
        + `<td class="num">${rp(TOT.total*sum/100)}</td>${o.edit?'<td></td>':''}</tr>` : '';
    const nt=$('ofTermNote');
    if(nt) nt.innerHTML = !o.terms.length ? ''
      : (Math.abs(sum-100)<0.01 ? '<span class="okmsg">Total termin 100% — sudah pas.</span>'
         : `<span class="warnmsg">Total termin ${f(sum,1)}% — kurang/lebih ${f(100-sum,1)}% dari nilai penawaran.</span>`);
  }
  // gantt
  const g=$('ofGantt');
  if(g){
    const W=ofWeeks(), ed=o.edit;
    let h='<div class="gwrap"><div class="grow ghead"><div class="gnm">Tahap</div><div class="gbars">';
    for(let w=1;w<=W;w++) h+=`<span class="gw">M${w}</span>`;
    h+='</div>'+(ed?'<div class="gact"></div>':'')+'</div>';
    o.sched.forEach((r,i)=>{
      const w0=Math.max(1,+r.w0||1), du=Math.max(1,+r.dur||1);
      h+='<div class="grow"><div class="gnm">'
       + (ed?ip('sched.'+i+'.nm',r.nm,'text','Nama tahap')
             +ip('sched.'+i+'.w0',w0,'number')+ip('sched.'+i+'.dur',du,'number')
           :esc(r.nm||''))
       + '</div><div class="gbars">';
      for(let w=1;w<=W;w++){
        const on = w>=w0 && w<w0+du;
        h+=`<span class="gc${on?' on':''}"></span>`;
      }
      h+='</div>'+(ed?`<div class="gact"><button type="button" class="delrow" data-ofdel="sched" data-i="${i}">×</button></div>`:'')+'</div>';
    });
    h+='</div>';
    if(o.dt.start) h+=`<p class="ofnote">Minggu 1 dihitung dari ${dstr(o.dt.start)}.</p>`;
    g.innerHTML=h;
  }
  // daftar teks
  const lst=(id,key)=>{ const el=$(id); if(!el) return;
    const ed=o.edit; let h='';
    (o[key]||[]).forEach((v,i)=>{
      h+='<li>'+(ed?ip(key+'.'+i,v,'text','…')
        +`<button type="button" class="delrow" data-ofdel="${key}" data-i="${i}">×</button>`:esc(v))+'</li>';
    });
    if(!h) h='<li class="ofph">—</li>';
    el.innerHTML=h; };
  lst('ofScope','scope'); lst('ofExcl','excl'); lst('ofTnc','tnc');
  paintOdo();
}
window.__ofCalc=ofCalc;

function ofSet(path,val){
  const o=OF(), parts=path.split('.');
  let t=o;
  for(let i=0;i<parts.length-1;i++){
    const k=parts[i]; t = Array.isArray(t)? t[+k] : t[k];
    if(!t) return;
  }
  const last=parts[parts.length-1];
  if(Array.isArray(t)) t[+last]=val; else t[last]=val;
  save();
}

document.addEventListener('input', e=>{
  const el=e.target;
  if(el.classList && el.classList.contains('ofin')){
    ofSet(el.dataset.of, el.type==='number' ? (+el.value||0) : el.value);
    ofCalc();
  }
});
document.addEventListener('change', e=>{
  const el=e.target;
  if(el.id==='tgOffer'){ OF().on=el.checked; save(); renderOffer(); return; }
  if(el.id==='tgOfEdit'){ OF().edit=el.checked; save(); renderOffer(); return; }
  if(el.id==='ofLogo' && el.files && el.files[0]){
    const fr=new FileReader();
    fr.onload=()=>{ if((fr.result||'').length>400000){ alert('Logo terlalu besar — pakai gambar di bawah 300 KB.'); return; }
      OF().co.logo=fr.result; save(); renderOffer(); };
    fr.readAsDataURL(el.files[0]);
  }
});
document.addEventListener('click', e=>{
  const b=e.target.closest('[data-ofadd],[data-ofdel],#ofReset,#ofPdf,#ofXls');
  if(!b) return;
  const o=OF();
  if(b.dataset.ofadd){
    const k=b.dataset.ofadd;
    if(k==='terms') o.terms.push({nm:'',pct:0});
    else if(k==='sched') o.sched.push({nm:'',w0:1,dur:1});
    else o[k].push('');
    save(); renderOffer(); return;
  }
  if(b.dataset.ofdel){ const k=b.dataset.ofdel; o[k].splice(+b.dataset.i,1); save(); renderOffer(); return; }
  if(b.id==='ofReset'){ const on=o.on, ed=o.edit; S.offer=OFFER0(); S.offer.on=on; S.offer.edit=ed;
    save(); renderOffer(); return; }
  if(b.id==='ofPdf'){ printOffer(b); return; }
  if(b.id==='ofXls'){ copyOfferTSV(b); return; }
});

function printOffer(btn){
  let st=document.getElementById('ofPageCSS');
  if(!st){ st=document.createElement('style'); st.id='ofPageCSS';
    st.textContent='@page{size:A4 portrait;margin:14mm}'; document.head.appendChild(st); }
  document.body.classList.add('printing','printing-of');
  const back=()=>{ document.body.classList.remove('printing','printing-of');
    const e=document.getElementById('ofPageCSS'); if(e) e.remove(); };
  addEventListener('afterprint', back, {once:true});
  setTimeout(()=>{ try{ window.print(); }catch(e){ back(); }
    setTimeout(back,1500); }, 60);
}

function copyOfferTSV(btn){
  const o=OF(), out=[];
  out.push('SURAT PENAWARAN HARGA');
  out.push(['Perusahaan',o.co.nm].join('\t'));
  out.push(['Alamat',o.co.addr].join('\t'));
  out.push(['Kontak',[o.co.tel,o.co.email].filter(Boolean).join(' / ')].join('\t'));
  out.push(['No. penawaran',ofNo()].join('\t'));
  out.push(['Revisi',o.cl.rev].join('\t'));
  out.push(['Kepada',o.cl.nm].join('\t'));
  out.push(['Lokasi',o.cl.loc].join('\t'));
  out.push(['Tanggal',dstr(o.dt.issue)].join('\t'));
  out.push(['Berlaku',o.dt.valid+' hari'].join('\t'));
  out.push(['Mulai',dstr(o.dt.start)].join('\t'));
  out.push(['Selesai',dstr(o.dt.end)].join('\t'));
  out.push(['Durasi',workdays(o.dt.start,o.dt.end)+' hari kerja'].join('\t'));
  out.push('');
  out.push('REKAPITULASI BIAYA');
  [['Profil hollow',TOT.costH],['Pelat baja',TOT.costP],['Material lain',TOT.costO],['Jasa fabrikasi & pemasangan',TOT.costJ||0],['Berat pembelian jasa (kg)',TOT.serviceKg],['Tarif jasa (Rp/kg)',TOT.serviceRate],
   ['Subtotal',TOT.sub],['Overhead & keuntungan',TOT.oh],['PPN',TOT.tax],['NILAI PENAWARAN',TOT.total]]
   .forEach(r=>out.push([r[0],Math.round(r[1])].join('\t')));
  out.push('');
  out.push('TERMIN PEMBAYARAN'); out.push(['No','Tahap','%','Nominal'].join('\t'));
  o.terms.forEach((r,i)=>out.push([i+1,r.nm,(+r.pct||0),Math.round(TOT.total*(+r.pct||0)/100)].join('\t')));
  out.push('');
  out.push('JADWAL PELAKSANAAN'); out.push(['Tahap','Mulai minggu','Durasi (minggu)'].join('\t'));
  o.sched.forEach(r=>out.push([r.nm,r.w0,r.dur].join('\t')));
  out.push('');
  out.push('LINGKUP PEKERJAAN'); o.scope.forEach(v=>out.push(v));
  out.push(''); out.push('TIDAK TERMASUK'); o.excl.forEach(v=>out.push(v));
  out.push(''); out.push('SYARAT & KETENTUAN'); o.tnc.forEach(v=>out.push(v));
  out.push(''); out.push(['Hormat kami',o.sign.nm,o.sign.role].join('\t'));
  const txt=out.join('\n'), lab=btn.querySelector('b')||btn;
  const done=()=>{ const x=lab.textContent; lab.textContent='Tersalin — tempel di Excel';
    setTimeout(()=>lab.textContent=x,2200); };
  if(navigator.clipboard && navigator.clipboard.writeText)
    navigator.clipboard.writeText(txt).then(done,()=>fallback(txt,done));
  else fallback(txt,done);
}

if(!S.offer) S.offer=OFFER0();
if(location.hash==='#penawaran')S.offer.on=true;
document.querySelector('.kg-offer-link')?.addEventListener('click',()=>{OF().on=true;save();renderOffer();});
renderOffer();

$('tgPrice').checked=S.price; $('tgEdit').checked=S.edit;
$('tgExport').checked=!!S.exp; $('exportbox').hidden=!S.exp;
exportUI();
$('wH').value=S.wH; $('wP').value=S.wP; $('bar').value=S.bar;
$('ohp').value=S.ohp; $('ppn').value=S.ppn;
render();
}


// pratinjau indeks mengikuti kursor — kloning SVG lembar aslinya, nol byte tambahan
(function(){
  const prev=document.getElementById('ixprev');
  if(!prev||!matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  const cache={}; let raf=0, tx=0, ty=0;
  const move=e=>{tx=e.clientX; ty=e.clientY;
    if(!raf) raf=requestAnimationFrame(()=>{raf=0;
      prev.style.top=ty+'px'; prev.style.left=Math.min(tx+230,innerWidth-24)+'px';});};
  document.querySelectorAll('.ix').forEach(a=>{
    a.addEventListener('pointerenter',()=>{
      const id=a.dataset.prev;
      if(!cache[id]){
        const src=document.querySelector('#'+id+' .pan svg');
        if(!src) return;
        const c=src.cloneNode(true); c.removeAttribute('style'); cache[id]=c;
      }
      if(prev.firstChild!==cache[id]){prev.textContent=''; prev.appendChild(cache[id]);}
      prev.classList.add('on');
    });
    a.addEventListener('pointerleave',()=>prev.classList.remove('on'));
    a.addEventListener('pointermove',move);
  });
})();

// ---------- mode layar penuh ----------
const SHEETIDS=[...document.querySelectorAll('.sheet')].map(s=>s.id);
function setFull(id,on){
  const sec=document.getElementById(id);
  sec.classList.toggle('full',on);
  document.body.classList.toggle('locked',on);
  const btn=sec.querySelector('.expand');
  btn.textContent=on?'Keluar':'Layar penuh';
  btn.setAttribute('aria-pressed',on?'true':'false');
  sec.querySelectorAll('[data-nav]').forEach(n=>{
    const i=SHEETIDS.indexOf(id);
    n.disabled = n.dataset.nav==='prev' ? i===0 : i===SHEETIDS.length-1;
  });
  if(!on) sec.scrollIntoView({block:'start'});
  window.dispatchEvent(new Event('resize'));
  const fit=window.__fit&&window.__fit[id];
  if(fit) requestAnimationFrame(()=>fit(on&&innerWidth<=860?'fill':'reset'));
}
document.querySelectorAll('[data-full]').forEach(b=>b.addEventListener('click',()=>{
  const id=b.dataset.full;
  setFull(id, !document.getElementById(id).classList.contains('full'));
}));
document.querySelectorAll('[data-nav]').forEach(b=>b.addEventListener('click',()=>{
  const i=SHEETIDS.indexOf(b.dataset.s);
  const j=b.dataset.nav==='prev'?i-1:i+1;
  if(j<0||j>=SHEETIDS.length) return;
  setFull(b.dataset.s,false); setFull(SHEETIDS[j],true);
}));
addEventListener('keydown',e=>{
  const cur=document.querySelector('.sheet.full'); if(!cur) return;
  if(e.key==='Escape') setFull(cur.id,false);
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
    const i=SHEETIDS.indexOf(cur.id), j=e.key==='ArrowLeft'?i-1:i+1;
    if(j>=0&&j<SHEETIDS.length){setFull(cur.id,false); setFull(SHEETIDS[j],true);}
  }
});

// ---------- alat ukur: klik dua titik, jarak dalam mm sebenarnya ----------
const NS='http://www.w3.org/2000/svg';
document.querySelectorAll('[data-meas]').forEach(btn=>{
  const id=btn.dataset.meas;
  const sec=document.getElementById(id);
  const fr=sec.querySelector('.frame'), svg=sec.querySelector('.pan svg');
  let on=false, a=null, g=null;
  const clear=()=>{ if(g) g.remove(); g=null; a=null; };
  const toModel=e=>{
    const p=svg.createSVGPoint(); p.x=e.clientX; p.y=e.clientY;
    return p.matrixTransform(svg.getScreenCTM().inverse());
  };
  const mk=(t,at)=>{const el=document.createElementNS(NS,t);
    for(const k in at) el.setAttribute(k,at[k]); return el;};
  btn.addEventListener('click',()=>{
    on=!on; btn.setAttribute('aria-pressed',on?'true':'false');
    fr.classList.toggle('measuring',on); btn.textContent=on?'Selesai':'Ukur';
    if(!on) clear();
  });
  fr.addEventListener('pointerup',e=>{
    if(!on||e.pointerType==='mouse'&&e.button!==0) return;
    if(fr.dataset.moved==='1') return;
    const q=toModel(e);
    if(!a){ clear(); a=q;
      g=mk('g',{class:'measg'}); svg.appendChild(g);
      g.appendChild(mk('circle',{cx:a.x,cy:a.y,r:22,fill:'var(--accent)'}));
      return;
    }
    const d=Math.hypot(q.x-a.x,q.y-a.y);
    g.appendChild(mk('line',{x1:a.x,y1:a.y,x2:q.x,y2:q.y,
      stroke:'var(--accent)','stroke-width':8}));
    g.appendChild(mk('circle',{cx:q.x,cy:q.y,r:22,fill:'var(--accent)'}));
    const t=mk('text',{x:(a.x+q.x)/2,y:(a.y+q.y)/2-40,fill:'var(--accent)',
      'text-anchor':'middle','font-family':'"JetBrains Mono",monospace','font-size':150});
    t.textContent=Math.round(d).toLocaleString('id-ID')+' mm';
    g.appendChild(t); a=null;
  });
});

// ---------- angka BOQ berhitung naik sekali saat blok masuk layar ----------
(function(){
  const boq=document.getElementById('boq'); if(!boq) return;
  const ids=['sumH','sumBar','sumP','sumSheet','grand'];
  const run=()=>{
    if(matchMedia('(prefers-reduced-motion:reduce)').matches) return;
    ids.forEach(id=>{
      const el=document.getElementById(id); if(!el) return;
      const txt=el.textContent, m=txt.match(/[\d.,]+/); if(!m) return;
      const target=parseFloat(m[0].replace(/\./g,'').replace(',','.'));
      if(!isFinite(target)) return;
      const dec=(m[0].split(',')[1]||'').length;
      const t0=performance.now(), D=900;
      const step=now=>{
        const k=Math.min(1,(now-t0)/D), e=1-Math.pow(1-k,3);
        el.textContent=txt.replace(m[0],(target*e).toLocaleString('id-ID',
          {minimumFractionDigits:dec,maximumFractionDigits:dec}));
        if(k<1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  };
  if(!('IntersectionObserver' in window)) return;
  const io=new IntersectionObserver((e,o)=>{if(e[0].isIntersecting){run();o.disconnect();}},
    {threshold:0.15});
  io.observe(boq);
})();

// petunjuk menyesuaikan perangkat
if(matchMedia('(pointer:coarse)').matches)
  document.querySelectorAll('[data-h]').forEach(h=>h.textContent='cubit untuk zoom · ketuk 2\u00d7 reset');

// reveal saat masuk layar — transform + opacity saja, stagger 60 ms
(function(){
  const els=[...document.querySelectorAll('.rv')];
  if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion:reduce)').matches){
    els.forEach(e=>e.classList.add('in')); return;
  }
  const io=new IntersectionObserver((ents,o)=>{
    ents.filter(e=>e.isIntersecting).forEach((e,i)=>{
      setTimeout(()=>e.target.classList.add('in'), i*60);
      o.unobserve(e.target);
    });
  },{rootMargin:'0px 0px -8% 0px',threshold:0.04});
  els.forEach(e=>io.observe(e));
})();

'use strict';
const ExplodedCatalog=(()=>{
 function layout(count,width,height){const cols=Math.max(1,Math.ceil(Math.sqrt(count*width/Math.max(1,height)))),rows=Math.max(1,Math.ceil(count/cols));return {cols,rows,cell:Math.min(width/cols,height/rows)*.88};}
 function target(index,bounds,layout,width,height,zoom=1,ox=0,oy=0){const {cols,rows,cell}=layout;const size=Math.max(bounds[2]-bounds[0],bounds[3]-bounds[1],1);return {x:width/2+ox+((index%cols)-(cols-1)/2)*cell*zoom,y:height/2+oy+(Math.floor(index/cols)-(rows-1)/2)*cell*zoom,s:cell*.72*zoom/size,cx:(bounds[0]+bounds[2])/2,cy:(bounds[1]+bounds[3])/2};}
 function dimensions(b){const v=b.length===24?b:Array.from({length:8},(_,i)=>[b[0]+([1,2,5,6].includes(i)?b[3]:0),b[1]+([2,3,6,7].includes(i)?b[4]:0),b[2]+(i>=4?b[5]:0)]).flat();const distance=(a,c)=>Math.hypot(...[0,1,2].map(k=>v[a*3+k]-v[c*3+k]));return [distance(0,1),distance(1,2),distance(0,4)];}
 return {layout,target,dimensions};
})();
if(typeof module!=='undefined')module.exports=ExplodedCatalog;


(function(){
const SPAN=17700, DEPTH=5000, TIERS=5, TIER_D=1000, RISER=500;
const PORTAL=[0,1770,3540,7080,8850,10620,14160,15930,17700];
const ROWS=[0,1000,2000,3000,4000,5000];
const AB=[4850,6850], SC=[12250,12850];
const SEG=[[0,4850],[6850,12250],[12850,17700]];
const ST_R=500/3, ST_T=267, ST_N=3;
const colTop=y=> y>=5000?2500:Math.floor(y/TIER_D)*RISER+RISER;

const GROUPS=[
 {id:'baseplate',lay:-1,name:'Base plate + karet',
  mat:'Pelat baja 8 mm + karet 10 mm',prof:'150 × 150 × 8 + karet 10 mm',
  note:'Tumpuan sendi, duduk lepas tanpa angkur ke lantai',key:'bp'},
 {id:'kolom',lay:0,name:'Kolom tribun',
  mat:'Baja — mutu belum diverifikasi — hollow hitam',prof:'50 × 100 × 2,3 mm · lonjor 6 m',
  note:'5,25 kg/m · gaya 12,8 kN · rasio 0,23 (tekuk λ=118)',key:'col'},
 {id:'balok',lay:0,name:'Balok tepi tier',
  mat:'Baja — mutu belum diverifikasi — hollow hitam',prof:'50 × 100 × 2,3 mm · lonjor 6 m',
  note:'Bentang 1.770 mm · σ 87 MPa · lendutan L/962 · rasio 0,54',key:'beam'},
 {id:'stiffener',lay:0,name:'Stiffener dek',
  mat:'Baja — mutu belum diverifikasi — hollow hitam',prof:'50 × 100 × 2,3 mm — sama dengan balok',
  note:'Bentang plat dek 1.000 → 500 mm · σ 96 MPa · rasio 0,60 · dudukan rata tanpa ganjal',key:'stf'},
 {id:'bracing',lay:0,name:'Bracing X',
  mat:'Baja — mutu belum diverifikasi — hollow',prof:'40 × 40 × 2 mm',note:'4 bay belakang + 2 panel tiap sisi ujung',key:'brc'},
 {id:'dek',lay:1,tex:1,name:'Plat dek',
  mat:'Pelat bordes anti-slip',prof:'tebal 8 mm · lembar 4ft × 8ft, 192 kg',
  note:'64,6 kg/m² · bentang 500 mm · σ 25 MPa · lendutan L/926',key:'dek'},
 {id:'pinus',lay:2,name:'Papan dudukan',
  mat:'Kayu pinus',prof:'400 × 40 mm',note:'Satu papan di muka tiap tier',key:'pin'},
 {id:'tangga',lay:3,tex:1,name:'Anak tangga',
  mat:'Pelat tekuk bordes anti-slip',prof:'tebal 4 mm',
  note:'3 optrede 167 + 3 antrede 267 per tier · panel 267×700 σ maks 111 MPa, lendutan 1,65 mm',key:'stp'},
 {id:'nosing',lay:3,name:'Nosing kontras',
  mat:'Cat epoxy kuning kontras',prof:'lebar 50 mm — rata, tidak menonjol',
  note:'Dicat di atas motif bordes; sengaja bukan strip agar tidak jadi titik sandung',key:'nos'},
 {id:'beton',lay:0,fixed:true,alpha:0.5,name:'Kolom beton eksisting',
  mat:'Beton bertulang gedung',prof:'600 × 500 mm',
  note:'4 kolom menembus tribun — dikelilingi void 50 mm, tidak boleh dipotong',key:'cnc'},
 {id:'void',lay:1,name:'Kerah void 50 mm',
  mat:'Pelat penutup celah 8 mm',prof:'lebar 50 mm keliling',
  note:'Menutup celah 50 mm antara dek dan kolom beton di permukaan injak',key:'vd'},
 {id:'anchor',lay:0,name:'Strut anchor ke kolom beton',
  mat:'Baja — mutu belum diverifikasi — hollow hitam',prof:'50 × 100 × 2,3 mm — sama profil rangka',
  note:'16 titik · pelat 6 mm + 2× dynabolt M10 · gaya 2,1 kN/titik · rasio 0,13',key:'anc'},
 {id:'dinding',lay:0,fixed:true,alpha:0.72,name:'Dinding gym (konteks)',
  mat:'Beton plester, cat eksisting',prof:'melengkung R 165 m · tebal 200 mm',
  note:'Tribun berdiri lepas, jarak bersih minimal 200 mm ke dinding',key:'wl'},
 {id:'jendela',lay:0,fixed:true,alpha:0.45,name:'Kaca jendela gym',
  mat:'Kaca bening pada kusen aluminium',prof:'pias 1.475 × 1.150 mm',
  note:'Konteks — tidak boleh tertutup sandaran tribun',key:'wn'},
 {id:'sandaran',lay:4,name:'Rangka sandaran',
  mat:'Baja — mutu belum diverifikasi — hollow, cat hitam doff',prof:'tiang & rail 60 × 60 mm',
  note:'Tiang @1.475 mm, rail atas +3.600 dan rail bawah +2.500',key:'snd'},
 {id:'sandkayu',lay:4,name:'Panel kayu sandaran',
  mat:'Papan kayu pinus — type SANDARAN PINEWOOD 40mm',prof:'tebal 40 mm · tinggi 1.000 mm',
  note:'Menerus A–C mengikuti busur dinding, offset 200 mm dari tembok',key:'sndk'},
 {id:'kusen',lay:0,fixed:true,name:'Kusen jendela gym',
  mat:'Aluminium eksisting',prof:'kusen 60 mm + mullion',
  note:'Konteks — pembagi pias jendela dinding gym',key:'ksn'},
 {id:'riser',lay:1,name:'Penutup muka tier & samping',
  mat:'Pelat polos 2 mm, tekuk tepi 20 mm',prof:'tinggi 500 mm per tier · panel ujung mengikuti profil tier',
  note:'Non-struktural — menutup muka tier dan sisi ujung kiri-kanan',key:'ris'},
 {id:'skirt',lay:1,name:'Penutup kolong & toe-board',
  mat:'Pelat polos 2 mm, tekuk tepi 20 mm',prof:'skirt tinggi 500 mm · toe-board 100 mm',
  note:'Skirt menutup kolong tribun; toe-board menahan barang jatuh di tepi dek & jalur tangga',key:'skt'},
 {id:'railing',lay:4,name:'Balustrade & railing',
  mat:'Baja — mutu belum diverifikasi — hollow',prof:'baluster 40×40×2,8 · rail 40×40×2',
  note:'Celah bersih ≤100 mm, anti-panjat',key:'rail'},
];
GROUPS.forEach(g=>{g.note='Representasi koordinasi; profil dan sambungan disederhanakan. Bukan hasil pemeriksaan kekuatan.';if(['kolom','balok','stiffener','bracing'].includes(g.id))g.prof='RHS 50 × 100 × 2,3 mm';if(g.id==='dek')g.prof='Bordes 4 mm; tebal dasar menunggu sertifikat';if(['dinding','jendela','kusen','riser','skirt'].includes(g.id))g.off=true;});
const G={}; GROUPS.forEach(g=>{g.boxes=[];G[g.id]=g;});
const B=(g,x,y,z,dx,dy,dz)=>G[g].boxes.push([x,y,z,dx,dy,dz]);

// kolom beton eksisting + lubang (void 50 mm keliling) yang harus dihindari pelat & balok
const CONC=[[-150,2938],[5850,2938],[11850,2938],[17850,2938]];
const VOID=50;
const CUT=CONC.map(([cx,cy])=>[cx-300-VOID, cy-250-VOID, cx+300+VOID, cy+250+VOID]);
function Bcut(g,x,y,z,dx,dy,dz){
  let parts=[[x,y,dx,dy]];
  CUT.forEach(([x0,y0,x1,y1])=>{
    const out=[];
    parts.forEach(([px,py,pdx,pdy])=>{
      const ax=px, ay=py, bx=px+pdx, by=py+pdy;
      if(x1<=ax||x0>=bx||y1<=ay||y0>=by){ out.push([px,py,pdx,pdy]); return; }
      if(y0>ay) out.push([ax,ay,pdx,y0-ay]);
      if(y1<by) out.push([ax,y1,pdx,by-y1]);
      const m0=Math.max(ay,y0), m1=Math.min(by,y1);
      if(x0>ax) out.push([ax,m0,x0-ax,m1-m0]);
      if(x1<bx) out.push([x1,m0,bx-x1,m1-m0]);
    });
    parts=out;
  });
  parts.forEach(q=>{ if(q[2]>1&&q[3]>1) B(g,q[0],q[1],z,q[2],q[3],dz); });
}


REVISED.forEach(e=>{ if(e.group==='dek'){const v=e.vertices;const lo=v[0],hi=v[6];Bcut('dek',...lo,hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]);} else G[e.group].boxes.push(e.vertices.flat()); });
// dek + pinus
for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D,z=t*RISER;
  SEG.forEach(([a,b])=>{
                        Bcut('pinus',a,yf,z,b-a,400,40);});}
// tangga + nosing
[AB,SC].forEach(([a,b])=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z0=t*RISER-RISER;
    for(let k=0;k<ST_N;k++){const y0=yf+k*ST_T, w=(k<ST_N-1)?ST_T:TIER_D-2*ST_T;
      B('tangga',a,y0,z0+(k+1)*ST_R,b-a,w,4);
      B('tangga',a,y0-4,z0+k*ST_R,b-a,4,ST_R);
      B('nosing',a,y0,z0+(k+1)*ST_R+4,b-a,50,1);}}});
// kolom beton eksisting (600 x 500) + kerah void + strut anchor
CONC.forEach(([cx,cy])=>B('beton',cx-300,cy-250,-200,600,500,3800));
// kerah void 50 mm di dek yang ditembus kolom beton
CONC.forEach(([cx,cy])=>{
  [1500,2000].forEach(z=>{
    const x0=Math.max(0,cx-350),x1=Math.min(SPAN,cx+350),y0=cy-300,y1=cy+300;
    if(x1-x0<80) return;
    if(cx>AB[0]&&cx<AB[1]) return;
    B('void',x0,y0,z,x1-x0,50,6);
    B('void',x0,y1-50,z,x1-x0,50,6);
    if(cx-350>=0) B('void',x0,y0+50,z,50,y1-y0-100,6);
    if(cx+350<=SPAN) B('void',x1-50,y0+50,z,50,y1-y0-100,6);
  });
});
// dinding gym melengkung (busur R 165 m -> sagitta 237 mm) + jendela + sandaran
const R=165000, SAG=237;
const wallY=x=>{const u=(x-SPAN/2)/ (SPAN/2); return DEPTH+520+SAG*(1-u*u);};
const NSEG=24;
for(let i=0;i<NSEG;i++){
  const x0=SPAN*i/NSEG, x1=SPAN*(i+1)/NSEG, w=x1-x0;
  const yy=wallY((x0+x1)/2);
  B('dinding',x0,yy,0,w,200,4600);
  // pias jendela: 2 baris, tiap segmen satu daun, dengan kusen + mullion tengah
  [1500,3000].forEach(z=>{
    const gx=x0+60, gw=w-120, gy=yy-34, gd=68;
    B('kusen',gx-60,gy,z-60,gw+120,gd,60);            // ambang bawah
    B('kusen',gx-60,gy,z+1150,gw+120,gd,60);          // ambang atas
    B('kusen',gx-60,gy,z,60,gd,1150);                 // tiang kusen kiri
    B('kusen',gx+gw,gy,z,60,gd,1150);                 // tiang kusen kanan
    B('kusen',gx+gw/2-25,gy,z,50,gd,1150);            // mullion tengah
    B('jendela',gx,yy-30,z,gw/2-25,60,1150);
    B('jendela',gx+gw/2+25,yy-30,z,gw/2-25,60,1150);
  });
}
// sandaran belakang menerus, offset 200 mm dari muka dinding
for(let i=0;i<NSEG;i++){
  const x0=SPAN*i/NSEG, x1=SPAN*(i+1)/NSEG, w=x1-x0;
  const yy=wallY((x0+x1)/2)-200-60;
  B('sandkayu',x0,yy+10,2560,w,40,1000);              // panel papan kayu 40 mm
  B('sandaran',x0,yy,3560,w,60,40);                    // rail penutup atas
  B('sandaran',x0,yy,2500,w,60,60);                    // rail bawah
  if(i%2===0) B('sandaran',x0,yy,2500,60,60,1100);     // tiang @1475 mm
}
// railing
[0,SPAN].forEach(x=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D,z=t*RISER;
    for(let i=0;i<=10;i++){const yy=yf+i*100; if(yy>yf+TIER_D)break;
      B('railing',x-20,yy-20,z,40,40,1100);}
    B('railing',x-20,yf,z+1060,40,TIER_D,40);
    B('railing',x-20,yf,z+510,40,TIER_D,40);}});

// penutup muka tier (plat riser 2 mm) + panel samping ujung
for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z0=(t-1)*RISER;
  SEG.forEach(([a,b])=>Bcut('riser',a,yf-2,z0,b-a,2,RISER));}
[0,SPAN].forEach((x,i)=>{const xo = i===0 ? -2 : 0;
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D;
    Bcut('riser',x+xo,yf,0,2,TIER_D,t*RISER);}});
// skirt kolong: menutup rongga di bawah dek pada sisi jalur tangga
[AB,SC].forEach(([a,b])=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z=t*RISER;
    B('skirt',a-2,yf,z-RISER,2,TIER_D,RISER);
    B('skirt',b,yf,z-RISER,2,TIER_D,RISER);}});
// skirt kolong sisi belakang (di bawah tier 5 sampai dinding)
SEG.forEach(([a,b])=>B('skirt',a,DEPTH-2,0,b-a,2,2500));
// toe-board 100 mm di tepi dek: ujung kiri-kanan + kedua sisi tiap jalur tangga
[[0,-2],[SPAN,0],[AB[0],-2],[AB[1],0],[SC[0],-2],[SC[1],0]].forEach(([x,d])=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z=t*RISER;
    B('skirt',x+d,yf,z+8,2,TIER_D,100);}});

['pinus','tangga','nosing','railing','riser','skirt'].forEach(k=>G[k].boxes=[]);

FINISH_GEOMETRY.forEach(e=>G[e.group].boxes.push(e.vertices.flat()));
GROUPS.find(g=>g.id==='tangga').prof='Pelat tekuk3mm / 176bagian native / 56bidang';
GROUPS.filter(g=>['riser','skirt'].includes(g.id)).forEach(g=>{g.off=false;g.mat='Pelat baja2mm / cat hitam';g.prof='Pelat penutup2mm / dicat';g.name=g.id==='riser'?'Riser, fascia dan return2mm':'Penutup kedua sisi2mm';g.note='310bagian total; belakang/bawah terbuka. Luas dan berat di RAB R04.';});
const cv=document.getElementById('cv3'), ctx=cv.getContext('2d');
let az=0.62, el=0.60, zoom=1, ox=0, oy=0, ex=0;
const CX=SPAN/2, CY=DEPTH/2, CZ=1100;
const LAYZ=[0,2600,5200,7800,10400]; // offset ledak per lapis (dikali ex)
const LAYBP=-2600;

function palette(){
  const cs=getComputedStyle(document.documentElement);
  const g=n=>cs.getPropertyValue(n).trim();
  return {steel:g('--steel'),ink:g('--ink'),accent:g('--accent'),dim:g('--dim'),
          line:g('--line'),paper:g('--paper'),muted:g('--muted')};
}
let P=palette();
// warna konteks dipatok, bukan diambil dari palet baja, supaya material terbaca
const MAT={dinding:'#8C8478', jendela:'#4E7FA6', kusen:'#9AA1A6', sandkayu:'#B07C42',
           pinus:'#C08A45'};
const BASE=()=>({baseplate:P.accent,kolom:P.steel,balok:P.steel,stiffener:P.steel,
  bracing:P.accent,dek:P.steel,pinus:MAT.pinus,tangga:P.dim,nosing:P.accent,railing:P.steel,
  beton:P.muted,void:P.dim,anchor:P.dim,dinding:MAT.dinding,jendela:MAT.jendela,
  kusen:MAT.kusen,sandkayu:MAT.sandkayu,sandaran:P.steel,riser:P.steel,skirt:P.steel});
const TINT={baseplate:0.95,kolom:1.0,balok:0.72,stiffener:1.25,bracing:1.0,
  dek:1.55,pinus:1.0,tangga:1.0,nosing:1.35,railing:1.3,
  beton:1.35,void:1.35,anchor:0.85,dinding:1.0,jendela:1.15,kusen:1.0,
  sandkayu:1.0,sandaran:0.85,riser:0.62,skirt:0.5};
const COLOR=()=>{const b=BASE(),o={};for(const k in b) o[k]=shade(b[k],TINT[k]);return o;};

const _sc=document.createElement('canvas').getContext('2d');
function shade(hex,f){
  const c=_sc; c.fillStyle=hex;
  const h=c.fillStyle; let r,g,b;
  if(h.startsWith('#')){const v=h.length===4?h.replace(/#(.)(.)(.)/,'#$1$1$2$2$3$3'):h;
    r=parseInt(v.substr(1,2),16);g=parseInt(v.substr(3,2),16);b=parseInt(v.substr(5,2),16);}
  else{const m=h.match(/[\d.]+/g);r=+m[0];g=+m[1];b=+m[2];}
  const mix=(x)=>Math.max(0,Math.min(255,Math.round(x*f)));
  return `rgb(${mix(r)},${mix(g)},${mix(b)})`;
}
function project(x,y,z,W,H,S){
  const ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el);
  const X=(x-CX), Y=(y-CY), Z=(z-CZ);
  const x1=X*ca-Y*sa, y1=X*sa+Y*ca;
  return [W/2+ox+x1*S, H/2+oy-(y1*se+Z*ce)*S, y1*ce-Z*se];
}
const FACES=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[3,2,6,7],[0,3,7,4],[1,2,6,5]];
const LUM=[0.52,1.0,0.88,0.70,0.80,0.64];
let sel=null,isolated=null;let pieceRefs=[];let exMode='axo',playing=false,anim=0,animTime=0;
const COARSE = matchMedia('(pointer:coarse)').matches;
let texOn = !COARSE;

// LUT warna: 16 grup x 6 muka, dihitung sekali per perubahan palet — bukan per muka per frame
let FILL=[], FILLSEL=[];
function makeLUT(){
  const C=COLOR(); FILL=[]; FILLSEL=[];
  GROUPS.forEach(g=>{
    const base=C[g.id];
    FILL.push(LUM.map(l=>shade(base,l)));
    FILLSEL.push(LUM.map(l=>shade(base,Math.min(1.4,l*1.55))));
  });
}
makeLUT();

// Geometri dunia disimpan datar; hanya dibangun ulang saat ledak / lapis berubah.
let WX,WY,WZ,PX,PY,DEP,ORD,BG,NB=0,dirty=true;
function rebuild(){
  const gi=[],bx=[];pieceRefs=[];
  GROUPS.forEach((g,k)=>{
    if(g.off) return;
    const dz=g.fixed||exMode==='catalog'?0:(g.lay<0?LAYBP:LAYZ[g.lay])*(ex/100);
    g.boxes.forEach((b,bi)=>{if(isolated&&(isolated.g!==k||isolated.bi!==bi))return;pieceRefs.push({g:k,bi,box:b});gi.push(k); bx.push(b.length===24?b.map((v,i)=>v+(i%3===2?dz:0)):[b[0],b[1],b[2]+dz,b[3],b[4],b[5]]);});
  });
  NB=gi.length;
  WX=new Float32Array(NB*8); WY=new Float32Array(NB*8); WZ=new Float32Array(NB*8);
  PX=new Float32Array(NB*8); PY=new Float32Array(NB*8);
  DEP=new Float32Array(NB); ORD=new Int32Array(NB); BG=new Int16Array(NB);
  for(let i=0;i<NB;i++){
    const b=bx[i], o=i*8, x=b[0],y=b[1],z=b[2],dx=b[3],dy=b[4],dh=b[5];
    if(b.length===24){for(let k=0;k<8;k++){WX[o+k]=b[k*3];WY[o+k]=b[k*3+1];WZ[o+k]=b[k*3+2];}BG[i]=gi[i];continue;}
    WX[o]=x;   WY[o]=y;    WZ[o]=z;
    WX[o+1]=x+dx;WY[o+1]=y; WZ[o+1]=z;
    WX[o+2]=x+dx;WY[o+2]=y+dy;WZ[o+2]=z;
    WX[o+3]=x;   WY[o+3]=y+dy;WZ[o+3]=z;
    for(let k=0;k<4;k++){WX[o+4+k]=WX[o+k];WY[o+4+k]=WY[o+k];WZ[o+4+k]=z+dh;}
    BG[i]=gi[i];
  }
  dirty=false;
}

function draw(){
  if(dirty) rebuild();
  const W=cv.width,H=cv.height;
  const ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el);
  const spread=exMode==='catalog'?0:(10400+2600)*(ex/100);
  const vert=DEPTH*Math.sin(el)+(2500+spread+1100)*Math.cos(el);
  const horiz=(SPAN+DEPTH)*0.72;
  const S=Math.min(W/(horiz*1.12), H/(vert*1.22))*zoom;
  const cx=W/2+ox, cy=H/2+oy;
  for(let i=0;i<NB;i++){
    const o=i*8; let d=0;
    for(let k=0;k<8;k++){
      const X=WX[o+k]-CX, Y=WY[o+k]-CY, Z=WZ[o+k]-CZ;
      const x1=X*ca-Y*sa, y1=X*sa+Y*ca;
      PX[o+k]=cx+x1*S; PY[o+k]=cy-(y1*se+Z*ce)*S; d+=y1*ce-Z*se;
    }
    DEP[i]=d*0.125; ORD[i]=i;
  }
  if(exMode==='catalog'&&ex>0){
    const t=ex/100,grid=ExplodedCatalog.layout(NB,W*.90,H*.86);
    for(let i=0;i<NB;i++){const o=i*8;let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity;
      for(let k=0;k<8;k++){left=Math.min(left,PX[o+k]);right=Math.max(right,PX[o+k]);top=Math.min(top,PY[o+k]);bottom=Math.max(bottom,PY[o+k]);}
      const cell=ExplodedCatalog.target(i,[left,top,right,bottom],grid,W,H,zoom,ox,oy);
      for(let k=0;k<8;k++){PX[o+k]=(1-t)*PX[o+k]+t*(cell.x+(PX[o+k]-cell.cx)*cell.s);PY[o+k]=(1-t)*PY[o+k]+t*(cell.y+(PY[o+k]-cell.cy)*cell.s);}
    }
  }
  if(isolated&&NB===1){const xs=Array.from(PX),ys=Array.from(PY),l=Math.min(...xs),r=Math.max(...xs),t=Math.min(...ys),b=Math.max(...ys),scale=Math.min(W*.7/Math.max(1,r-l),H*.7/Math.max(1,b-t))*zoom;for(let k=0;k<8;k++){PX[k]=W/2+ox+(xs[k]-(l+r)/2)*scale;PY[k]=H/2+oy+(ys[k]-(t+b)/2)*scale;}}
  ORD.sort((a,b)=>DEP[b]-DEP[a]);

  ctx.clearRect(0,0,W,H);
  const edges = !lowQ && zoom>0.85;
  let alpha=1; ctx.globalAlpha=1;
  for(let n=0;n<NB;n++){
    const i=ORD[n], o=i*8, g=GROUPS[BG[i]];
    const a=(g.alpha!==undefined)?g.alpha:1;
    if(a!==alpha){ctx.globalAlpha=a; alpha=a;}
    const isSel = sel===i, lut = isSel?FILLSEL[BG[i]]:FILL[BG[i]];
    for(let fi=0;fi<6;fi++){
      const f=FACES[fi];
      const x0=PX[o+f[0]],y0=PY[o+f[0]],x1=PX[o+f[1]],y1=PY[o+f[1]],
            x2=PX[o+f[2]],y2=PY[o+f[2]],x3=PX[o+f[3]],y3=PY[o+f[3]];
      if(x0*y1-x1*y0 + x1*y2-x2*y1 + x2*y3-x3*y2 + x3*y0-x0*y3 >= 0) continue;
      ctx.beginPath(); ctx.moveTo(x0,y0); ctx.lineTo(x1,y1); ctx.lineTo(x2,y2); ctx.lineTo(x3,y3);
      ctx.closePath();
      ctx.fillStyle=lut[fi]; ctx.fill();
      if(texOn && g.tex && fi===1 && !lowQ){
        // motif kembang digambar di ruang muka: dua vektor tepi, satu jalur, satu stroke
        const ux=(x1-x0), uy=(y1-y0), vx=(x3-x0), vy=(y3-y0);
        const lu=Math.hypot(ux,uy), lv=Math.hypot(vx,vy);
        if(lu>26 && lv>10){
          const nu=Math.min(40,Math.max(2,Math.round(lu/14))), nv=Math.min(14,Math.max(1,Math.round(lv/14)));
          ctx.beginPath();
          for(let a=0;a<nu;a++)for(let b2=0;b2<nv;b2++){
            const su=(a+0.5)/nu, sv=(b2+0.5)/nv, sk=((a+b2)%2)?0.18:-0.18;
            const px=x0+ux*su+vx*sv, py=y0+uy*su+vy*sv;
            const dx2=(ux/nu)*0.34+(vx/nv)*sk, dy2=(uy/nu)*0.34+(vy/nv)*sk;
            ctx.moveTo(px-dx2,py-dy2); ctx.lineTo(px+dx2,py+dy2);
          }
          ctx.strokeStyle='rgba(0,0,0,.30)'; ctx.lineWidth=0.9; ctx.stroke();
        }
      }
      if(edges||isSel){ctx.strokeStyle=isSel?P.accent:'rgba(255,255,255,.13)';
        ctx.lineWidth=isSel?1.6:0.5; ctx.stroke();}
    }
  }
  ctx.globalAlpha=1;
  hud.textContent = NB+' bagian · '+(exMode==='catalog'?'katalog ':'axo ')+Math.round(ex)+'% · zoom '+zoom.toFixed(2)+'×';
}
const hud=document.getElementById('hudCount');

// satu gambar per frame layar, bukan per event pointer.
// rAF bisa tidak pernah dijalankan kalau halaman dimuat di latar atau di-prerender,
// jadi selalu disiapkan jaring pengaman berbasis timer.
let pend=0, guard=0;
function render(){
  if(pend) return;
  pend=requestAnimationFrame(()=>{pend=0; clearTimeout(guard); guard=0; draw();});
  if(!guard) guard=setTimeout(()=>{
    guard=0;
    if(pend){ cancelAnimationFrame(pend); pend=0; draw(); }
  }, 400);
}
function reflow(){ dirty=true; render(); }

let lowQ=false, qTimer=0;
function resize(){
  const r=cv.parentElement.getBoundingClientRect();
  const full=Math.min(2,window.devicePixelRatio||1);
  const dpr=lowQ?Math.min(1,full):full;
  const w=Math.round(r.width*dpr), h=Math.round(r.height*dpr);
  if(cv.width!==w||cv.height!==h){cv.width=w; cv.height=h;}
  cv.style.width=r.width+'px'; cv.style.height=r.height+'px';
  if(booted) draw(); else render();
}
// saat diputar/di-pinch, turunkan resolusi piksel — di HP ini bedanya 4-9x jumlah piksel
function quality(low){
  clearTimeout(qTimer);
  if(low){ if(!lowQ){lowQ=true; resize();} }
  else qTimer=setTimeout(()=>{lowQ=false; resize();},170);
}
let rTimer=0;
window.addEventListener('resize',()=>{clearTimeout(rTimer);rTimer=setTimeout(resize,120);});

// interaksi — rotasi 1 jari, pinch 2 jari, geser dengan Shift / dua jari
const stage=cv.parentElement;
const pts=new Map();
let moved=0, pinch0=0, zoom0=1, mid0=null;
function mid(){ const a=[...pts.values()];
  return {x:(a[0].x+a[1].x)/2, y:(a[0].y+a[1].y)/2,
          d:Math.hypot(a[0].x-a[1].x, a[0].y-a[1].y)}; }

stage.addEventListener('pointerdown',e=>{
  pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
  stage.setPointerCapture(e.pointerId);
  if(pts.size===1){moved=0; stage.classList.add('drag'); quality(true);}
  if(pts.size===2){const m=mid(); pinch0=m.d; zoom0=zoom; mid0={x:m.x,y:m.y};}
});
stage.addEventListener('pointermove',e=>{
  const p=pts.get(e.pointerId); if(!p) return;
  const dx=e.clientX-p.x, dy=e.clientY-p.y;
  p.x=e.clientX; p.y=e.clientY;
  if(pts.size>=2){
    const m=mid();
    if(pinch0>8){ zoom=Math.max(0.35,Math.min(12, zoom0*(m.d/pinch0))); }
    ox+=(m.x-mid0.x); oy+=(m.y-mid0.y); mid0={x:m.x,y:m.y};
    quality(true); render(); return;
  }
  moved+=Math.abs(dx)+Math.abs(dy);
  if(e.shiftKey||(exMode==='catalog'&&ex>0)){const dpr=cv.width/cv.getBoundingClientRect().width;ox+=dx*dpr;oy+=dy*dpr;}
  else {az+=dx*0.006; el=Math.max(0.05,Math.min(1.45,el+dy*0.005));}
  quality(true); render();
});
function up(e){
  const had=pts.size;
  pts.delete(e.pointerId);
  if(pts.size<2) pinch0=0;
  if(pts.size===0){
    stage.classList.remove('drag'); quality(false);
    if(had===1 && moved<5) pick(e);
  }
}
stage.addEventListener('pointerup',up);
stage.addEventListener('pointercancel',e=>{moved=10;up(e);});
stage.addEventListener('wheel',e=>{e.preventDefault();
  zoom=Math.max(0.35,Math.min(12,zoom*(e.deltaY<0?1.12:1/1.12)));
  quality(true); quality(false); render();},{passive:false});

function pick(e){
  const r=cv.getBoundingClientRect();
  const dpr=cv.width/r.width;
  const mx=(e.clientX-r.left)*dpr, my=(e.clientY-r.top)*dpr;
  for(let n=NB-1;n>=0;n--){
    const i=ORD[n], o=i*8;
    for(let fi=0;fi<6;fi++){
      const f=FACES[fi];
      const q=[[PX[o+f[0]],PY[o+f[0]]],[PX[o+f[1]],PY[o+f[1]]],
               [PX[o+f[2]],PY[o+f[2]]],[PX[o+f[3]],PY[o+f[3]]]];
      let a=0; for(let k=0;k<4;k++){const j=(k+1)%4; a+=q[k][0]*q[j][1]-q[j][0]*q[k][1];}
      if(a>=0) continue;
      if(inside(mx,my,q)){ stopExplosion();sel=i; showPick(GROUPS[BG[i]]); render(); return; }
    }
  }
  sel=null; showPick(null); render();
}
function inside(x,y,q){
  let s=false;
  for(let i=0,j=3;i<4;j=i++){
    const xi=q[i][0],yi=q[i][1],xj=q[j][0],yj=q[j][1];
    if(((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi)) s=!s;
  }
  return s;
}
const JUMP={baseplate:['S-10','Detail Base Plate'],kolom:['S-03','Rencana Rangka'],
  balok:['S-03','Rencana Rangka'],stiffener:['S-06','Potongan A\u2013A'],
  bracing:['S-03','Rencana Rangka'],dek:['S-01','Denah Tribun'],pinus:['S-06','Potongan A\u2013A'],
  tangga:['S-08','Detail Tangga'],nosing:['S-08','Detail Tangga'],
  railing:['S-09','Detail Railing'],anchor:['S-11','Detail Sambungan'],
  sandaran:['S-05','Tampak Samping'],sandkayu:['S-05','Tampak Samping'],
  kusen:['S-05','Tampak Samping'],beton:['S-02','Rencana Tumpuan'],
  void:['S-01','Denah Tribun'],dinding:['S-05','Tampak Samping'],jendela:['S-05','Tampak Samping']};
function showPick(g){
  const card=document.getElementById('pick');
  const nm=card.querySelector('.pk-name'), dl=card.querySelector('.pk-dl');
  const old=card.querySelector('.pk-jump'); if(old) old.remove();
  if(!g){document.getElementById('ex-isolate').disabled=true;nm.textContent='Belum ada yang dipilih';dl.innerHTML='';return;}
  nm.textContent=g.name;
  dl.innerHTML=`<dt>Material</dt><dd>${g.mat}</dd>
    <dt>Ukuran</dt><dd>${g.prof}</dd>
    <dt>Jumlah</dt><dd>${g.boxes.length} bagian</dd>
    <dt>Catatan</dt><dd style="font-family:inherit">${g.note}</dd>`;
    const piece=pieceRefs[sel];
  if(piece){const dims=ExplodedCatalog.dimensions(piece.box);let source=null;const flat=piece.box.length===24?piece.box:null;
    if(flat)source=[...REVISED,...FINISH_GEOMETRY].find(x=>x.group===g.id&&x.vertices.flat().every((v,i)=>Math.abs(v-flat[i])<.001));
    if(!source&&window.MettaModelVersion)source=window.MettaModelVersion.source(piece.box);
    const add=(label,value)=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;dl.append(dt,dd);};
    add('Dimensi geometri',dims.map(x=>x.toLocaleString('id-ID',{maximumFractionDigits:1})).join(' × ')+' mm');
    add('ID sumber',source?.id!=null?String(source.id):'Tidak tersedia untuk bagian ini');
    if(source?.mark)add('Mark',source.mark);
    add('Bagian web',g.id+' / '+(piece.bi+1));
  }
  document.getElementById('ex-isolate').disabled=!piece;
  const j=JUMP[g.id];
  if(j && document.getElementById(j[0])){
    const btn=document.createElement('button');
    btn.className='pk-jump'; btn.textContent='Lihat '+j[0]+' \u00b7 '+j[1];
    btn.addEventListener('click',()=>{
      const sec=document.getElementById(j[0]);
      sec.classList.add('in');
      sec.scrollIntoView({behavior:'smooth',block:'start'});
    });
    card.appendChild(btn);
  }
}

// legend
const leg=document.getElementById('legend');
const _LC=COLOR();
GROUPS.forEach(g=>{
  const C=_LC;
  const el2=document.createElement('label'); el2.className='lg';
  el2.innerHTML=`<input type="checkbox" ${g.off?'':'checked'}><span class="sw" style="background:${C[g.id]}"></span><span>${g.name}</span>`;
  el2.querySelector('input').addEventListener('change',ev=>{g.off=!ev.target.checked;sel=null;showPick(null);reflow();});
  leg.appendChild(el2);
});
function setCtx(on){sel=null;showPick(null);
  ['dinding','jendela','kusen','beton'].forEach(id=>{G[id].off=!on;});
  dirty=true;
  document.querySelectorAll('.lg').forEach(l=>{
    const nm=l.textContent.trim();
    if(nm.indexOf('Dinding')===0||nm.indexOf('Kaca jendela')===0||nm.indexOf('Kusen')===0||nm.indexOf('Kolom beton')===0){
      l.querySelector('input').checked=on;}
  });
  render();
}
document.getElementById('ctxOn').addEventListener('click',()=>setCtx(true));
document.getElementById('ctxOff').addEventListener('click',()=>setCtx(false));
function setExplode(value){ex=Math.max(0,Math.min(100,value));document.getElementById('ex').value=ex;document.getElementById('ex-percent').textContent=Math.round(ex)+'%';reflow();}
function stopExplosion(){playing=false;cancelAnimationFrame(anim);anim=0;document.getElementById('ex-play').textContent='Putar';document.getElementById('ex-play').setAttribute('aria-pressed','false');quality(false);}
function playFrame(time){if(!playing)return;const dt=Math.min(80,time-animTime);animTime=time;setExplode(ex+dt/60);if(ex>=100){stopExplosion();return;}anim=requestAnimationFrame(playFrame);}
document.getElementById('ex').addEventListener('input',e=>{stopExplosion();setExplode(+e.target.value);});
document.getElementById('ex-play').addEventListener('click',()=>{if(playing){stopExplosion();return;}if(ex>=100)setExplode(0);playing=true;animTime=performance.now();document.getElementById('ex-play').textContent='Jeda';document.getElementById('ex-play').setAttribute('aria-pressed','true');quality(true);anim=requestAnimationFrame(playFrame);});
document.getElementById('ex-reset').addEventListener('click',()=>{stopExplosion();isolated=null;sel=null;az=.62;el=.60;zoom=1;ox=oy=0;showPick(null);setExplode(0);});
document.getElementById('ex-isolate').addEventListener('click',()=>{if(pieceRefs[sel]){stopExplosion();isolated={g:pieceRefs[sel].g,bi:pieceRefs[sel].bi};sel=0;zoom=1;ox=oy=0;reflow();}});
document.getElementById('ex-show-all').addEventListener('click',()=>{isolated=null;sel=null;showPick(null);reflow();});
document.querySelectorAll('[data-ex-mode]').forEach(b=>b.addEventListener('click',()=>{stopExplosion();exMode=b.dataset.exMode;sel=null;showPick(null);zoom=1;ox=oy=0;document.querySelectorAll('[data-ex-mode]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.getElementById('ex-hint').textContent=exMode==='catalog'?'Komponen disusun sebagai katalog. Ukuran tampilan disesuaikan per bagian; klik untuk dimensi. Seret untuk geser, scroll/pinch untuk zoom.':'Geser untuk memisahkan lapisan struktur. Seret untuk memutar.';reflow();}));
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopExplosion();});

(function(){const cb=document.getElementById('texCb'); if(!cb) return;
  cb.checked=texOn;
  cb.addEventListener('change',()=>{texOn=cb.checked; render();});})();
document.querySelectorAll('[data-ex]').forEach(b=>b.addEventListener('click',()=>{
  stopExplosion();setExplode(+b.dataset.ex);}));
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{
  const v=b.dataset.view;
  if(v==='iso'){az=0.62;el=0.60;}
  if(v==='depan'){az=0;el=0.08;}
  if(v==='samping'){az=-Math.PI/2;el=0.08;}
  if(v==='atas'){az=0;el=1.45;}
  ox=0;oy=0;render();}));
const mq=window.matchMedia('(prefers-color-scheme: dark)');
mq.addEventListener('change',()=>{P=palette(); makeLUT();
  document.querySelectorAll('.lg .sw').forEach((s,i)=>s.style.background=COLOR()[GROUPS[i].id]);
  render();});

// bottom sheet (mobile)
const tgl=document.getElementById('sheetTgl'), side=document.getElementById('v3side');
if(tgl) tgl.addEventListener('click',()=>{
  const on=side.classList.toggle('open');
  tgl.setAttribute('aria-expanded',on?'true':'false');
  document.getElementById('sheetTglTxt').textContent=on?'Tutup panel':'Kontrol & material';
});

// render pertama ditunda sampai panggung mendekati layar → halaman ringan saat dibuka
let booted=false;
const boot=()=>{ if(booted) return; booted=true; resize(); draw(); };
// Runs inside the existing 3D renderer closure: camera and picking stay shared.
const versionBaseline=GROUPS.map(g=>({boxes:g.boxes.slice(),name:g.name,mat:g.mat,prof:g.prof,note:g.note}));
const sameBox=(b,v)=>b.length===24&&b.every((x,i)=>Math.abs(x-v[i])<.001);
let versionSources=new Map();
window.MettaModelVersion={
 source(box){return versionSources.get(box);},
 thickness(rhs,shs){
  for(const id of ['kolom','balok','stiffener','bracing'])G[id].prof=`RHS 50 × 100 × ${rhs} mm`+(id==='stiffener'?' / pengaku tangga SHS 40 × 40 × '+shs+' mm':'');
  G.railing.prof='SHS 40 × 40 × '+shs+' mm';
  if(sel!==null)showPick(GROUPS[pieceRefs[sel]?.g]);
 },
 apply(version,data,mesh={wire_mm:2,opening_label_mm:25}){
  versionSources=new Map();
  stopExplosion();isolated=null;sel=null;showPick(null);
  GROUPS.forEach((g,i)=>Object.assign(g,versionBaseline[i],{boxes:versionBaseline[i].boxes.slice()}));
  if(version==='v2'){
   const removed=new Set(data.remove_ids),removeBoxes=[...REVISED,...FINISH_GEOMETRY].filter(e=>removed.has(e.id)).map(e=>({group:e.group,v:e.vertices.flat()}));
   for(const g of GROUPS){if(data.clear_groups.includes(g.id))g.boxes=[];else g.boxes=g.boxes.filter(b=>!removeBoxes.some(e=>e.group===g.id&&sameBox(b,e.v)));}
   // Rebuild retained deck using the original concrete-void clipping function.
   REVISED.filter(e=>e.group==='dek'&&!removed.has(e.id)).forEach(e=>{const a=e.vertices[0],b=e.vertices[6];Bcut('dek',...a,b[0]-a[0],b[1]-a[1],b[2]-a[2]);});
   for(const e of data.items){G[e.group].boxes.push(e.box);versionSources.set(e.box,{id:e.id,mark:'R08 / usulan koordinasi'});}
   // True open mesh: individual wire solids, not a filled opaque side plate.
   const wire=mesh.wire_mm,pitch=mesh.opening_label_mm+wire;
   for(const p of data.mesh){
    const [a,y,z,A,Y,Z]=p.bounds,x=(a+A)/2,W=Y-y,H=Z-z,left=x<1000,face=x+(left?-22:22);
    const put=(b)=>G.skirt.boxes.push(b);
    put([x-20,y,z,40,W,40]);put([x-20,y,Z-40,40,W,40]);
    put([x-20,y,z+40,40,40,H-80]);put([x-20,Y-40,z+40,40,40,H-80]);
    for(let yy=y+20;yy<=Y-20+.001;yy+=pitch)put([face-wire/2,yy-wire/2,z+20,wire,wire,H-40]);
    for(let zz=z+20;zz<=Z-20+.001;zz+=pitch)put([face-wire/2,y+20,zz-wire/2,wire,W-40,wire]);
    const clampX=face+(left?-3:0);
    put([clampX,y+20,z+20,3,W-40,30]);put([clampX,y+20,Z-50,3,W-40,30]);
    put([clampX,y+20,z+20,3,30,H-40]);put([clampX,Y-50,z+20,3,30,H-40]);
   }
   Object.assign(G.skirt,{name:'Mesh sisi + rangka panel',mat:'Kawat loket galvanis; rangka SHS dan strip penjepit',prof:`Lubang ${mesh.opening_label_mm} / kawat ${wire} mm`,note:'R08: penutup sisi, bukan pengganti railing atau bracing.'});
   G.tangga.prof=`R08 / ${data.stair_panels} panel tekuk 3 mm`;G.baseplate.note=`V2: 80 dudukan lama + ${data.new_posts} base dan angkur infill usulan. Kapasitas lantai belum disahkan.`;
   for(const k of ['kolom','balok','stiffener'])G[k].note='V2 / geometri arsip + rangka R08 usulan. Penyangga tangga termasuk; profil tiap komponen mengikuti RAB.';
  }
  GROUPS.forEach((g,i)=>{const label=leg.children[i];if(label)label.lastElementChild.textContent=g.name;});
  cv.dataset.siteVersion=version;cv.dataset.stairPanels=String(version==='v2'?data.stair_panels:data.old_stair_panels);cv.dataset.infillColumns=String(version==='v2'?data.new_posts:0);
  dirty=true;if(booted){resize();draw();}
 }
};

window.__boot3d=boot; window.__resize3d=()=>{ if(booted){ resize(); draw(); } };

const stageEl=document.querySelector('.v3-stage');
function near(){
  if(!stageEl) return false;
  const r=stageEl.getBoundingClientRect();
  return r.height>0 && r.top < innerHeight+280 && r.bottom > -280;
}
function maybeBoot(){
  if(booted){ cleanupBoot(); return; }
  if(near()){ boot(); cleanupBoot(); }
}
function cleanupBoot(){
  cleanupPoll();
  removeEventListener('scroll', maybeBoot);
  removeEventListener('resize', maybeBoot);
  removeEventListener('load', maybeBoot);
  document.removeEventListener('visibilitychange', maybeBoot);
  if(io) io.disconnect();
}
let io=null;
if('IntersectionObserver' in window){
  io=new IntersectionObserver(es=>{ if(es.some(e=>e.isIntersecting)) maybeBoot(); }, {rootMargin:'280px'});
  if(stageEl) io.observe(stageEl);
}
// Cadangan berlapis. Observer dan event scroll ternyata tidak selalu memicu
// (halaman dimuat di latar, lompat anchor, gulir terprogram), jadi patokan
// terakhirnya adalah pemeriksaan berkala yang berhenti sendiri begitu menyala.
addEventListener('scroll', maybeBoot, {passive:true});
addEventListener('resize', maybeBoot);
addEventListener('load', maybeBoot);
document.addEventListener('visibilitychange', maybeBoot);
let poll=setInterval(maybeBoot, 350);
function cleanupPoll(){ if(poll){ clearInterval(poll); poll=0; } }
setTimeout(maybeBoot, 200);

// Patokan terakhir. Di sebagian lingkungan (tab yang dikendalikan otomasi, timer
// yang di-throttle, halaman di-prerender) tidak ada satu pun pemicu di atas yang
// jalan, dan penonton cuma melihat kanvas kosong. Lebih baik gambar sekali setelah
// halaman selesai dimuat daripada berisiko tidak muncul sama sekali; konten utama
// sudah tampil duluan, jadi halaman tetap terasa ringan saat dibuka.
function forceBoot(){ setTimeout(()=>{ if(!booted){ boot(); cleanupBoot(); } }, 1200); }
if(document.readyState==='complete') forceBoot();
else addEventListener('load', forceBoot);
})();
