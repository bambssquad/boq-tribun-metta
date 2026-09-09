"""Static Sites build; preserve existing calculator, spreadsheet and viewer controls."""
import sys,json,re,shutil,hashlib
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'src'))
import build,boq,three_d,experience,pitch,kg_pricing
import revision04,r04_model
r04=revision04.build_data()
model=r04_model.load_model()
fin=json.loads((ROOT/'data/finishes-audit.json').read_text())
fgeom=json.loads((ROOT/'data/finishes-geometry.json').read_text())
rhs=model['rhs'];cut=sum(r['props']['Cut Length']*304.8 for r in rhs)/1000
frame_stock=revision04.pack_bars([(str(r['id']),r['props']['Cut Length']*304.8) for r in rhs])
frame_bars=len(frame_stock);frame_stock_m=frame_bars*6
collen=sum(c['length_mm'] for c in model['columns'])/1000
build.HOLLOW['100x50x2.3']=32.5/6
build.SHEET_A=1.2*2.4
build.HOLLOW_ITEMS=[
 ('Rangka RHS — hasil model','RHS 50×100×2,3',len(rhs),cut,'100x50x2.3',f'165 framing termasuk20diagonal;{frame_bars}stok6m, kerf3mm, pola FFD. Kolom dipisahkan pada kalkulator ini.'),
 ('Kolom — hasil model','RHS 50×100×2,3',80,collen,'100x50x2.3','80 kolom, dasar +18 mm. Jumlah beli masih perkiraan, bukan pola potong.'),
 ('Rail atas — hasil model','HOLLOW 40x40x2',10,sum(r['length_mm'] for r in fin['rail'] if 'RAILING HITAM' in r['type'])/1000,'40x40x2','10 elemen; tipe Revit lama masih memakai keluarga W, penampang fisik harus diperiksa.'),
 ('Tiang railing — hasil model','HOLLOW 40x40x2,8',85,sum(r['length_mm'] for r in fin['rail'] if 'TIANG RAILING' in r['type'])/1000,'40x40x2.8','85 tiang dari System Length model aktif; berat profil masih estimasi katalog lama.')]
build.PLATE_ITEMS=[('Dek bordes 4 mm — hasil model',4,model['deck_area_m2'],0,'Jumlah Area 30 elemen Revit; 28 berluas positif. Berat baja dasar saja; motif belum terukur.'),
 ('Penutup riser, fascia dan sisi 2 mm — R04',2,r04['enclosure']['area'],0,'310bagian native, takikan beton dan return tepi termasuk; belakang/bawah terbuka. Pola beli aktual di RAB R04.'),
 ('Pelat tekuk tangga 3 mm — R04',3,r04['net_flat_area'],0,'56bidang; luas bersih termasuk tekukan dan takikan. Pembelian mengikuti pola nesting, lihat RAB R04.'),
 ('Base plate',8,80*.15*.15,0,'80 dudukan 150×150. Tanpa angkur ke pelat lantai.')]
build.OTHER_ITEMS=[r for r in build.OTHER_ITEMS if r['nm'].startswith(('Papan pinus','Panel kayu','Finish clear'))]
for r in build.OTHER_ITEMS:r['note']='Estimasi web lama; belum diukur ulang. '+r['note']
for r in build.OTHER_ITEMS:
 if r['nm'].startswith('Papan pinus'):
  r['q']=sum(x['volume_m3'] for x in fin['floor'] if 'PINUS' in x['type']);r['note']='Volume 15 elemen Revit aktif; jumlah papan beli dan sambungan kayu belum final.'
build.OTHER_ITEMS.append(dict(nm='Cat nosing — luas model',q=sum(x['area_m2'] for x in fin['floor'] if 'NOSING' in x['type']),un='m²',note='31 elemen representasi cat; konsumsi liter mengikuti produk dan jumlah lapis.'))
build.OTHER_ITEMS.append(dict(nm='Karet dudukan 150×150×10',q=80,un='bh',note='Jumlah dudukan model; grade bantalan belum terverifikasi.'))
build.SHEETS=[];build.RASIO=[];build.SPEK=[]
build.REV='R04-1200x2400-'+hashlib.sha1(json.dumps([model,fin,r04['flat_area']],sort_keys=True).encode()).hexdigest()[:10]
# Same renderer, now fed 80 supports and 161 frame objects from the audited model.
js=three_d.JS_3D
js=js.replace('const ST_R=167,','const ST_R=500/3,')
a=js.index('// base plate\n');b=js.index('// dek + pinus',a)
injection='const REVISED='+json.dumps(model['items'],separators=(',',':'))+';\nREVISED.forEach(e=>{ if(e.group===\'dek\'){const v=e.vertices;const lo=v[0],hi=v[6];Bcut(\'dek\',...lo,hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2]);} else G[e.group].boxes.push(e.vertices.flat()); });\n'
js=js[:a]+injection+js[b:]
js=js.replace("Bcut('dek',a,yf,z,b-a,TIER_D,8);",'')
js=js.replace("Bcut('pinus',a,yf,z+8", "Bcut('pinus',a,yf,z")
a=js.index('// strut anchor:');b=js.index('// dinding gym',a);js=js[:a]+js[b:]
js=js.replace("g.boxes.forEach(b=>{gi.push(k); bx.push([b[0],b[1],b[2]+dz,b[3],b[4],b[5]]);});", "g.boxes.forEach(b=>{gi.push(k); bx.push(b.length===24?b.map((v,i)=>v+(i%3===2?dz:0)):[b[0],b[1],b[2]+dz,b[3],b[4],b[5]]);});")
js=js.replace('WX[o]=x;   WY[o]=y;    WZ[o]=z;', 'if(b.length===24){for(let k=0;k<8;k++){WX[o+k]=b[k*3];WY[o+k]=b[k*3+1];WZ[o+k]=b[k*3+2];}BG[i]=gi[i];continue;}\n    WX[o]=x;   WY[o]=y;    WZ[o]=z;')
js=js.replace("const G={};", "GROUPS.forEach(g=>{g.note='Representasi koordinasi; profil dan sambungan disederhanakan. Bukan hasil pemeriksaan kekuatan.';if(['kolom','balok','stiffener','bracing'].includes(g.id))g.prof='RHS 50 × 100 × 2,3 mm';if(g.id==='dek')g.prof='Bordes 4 mm; tebal dasar menunggu sertifikat';if(['dinding','jendela','kusen','riser','skirt'].includes(g.id))g.off=true;});\nconst G={};")
build.JS_3D=js
pos=build.JS_3D.index("const cv=document.getElementById('cv3')")
finish_items=[e for e in fgeom['items'] if e['group']!='tangga']+r04['stair_geometry']+r04_model.cover_geometry()
finish_js="['pinus','tangga','nosing','railing','riser','skirt'].forEach(k=>G[k].boxes=[]);\nconst FINISH_GEOMETRY="+json.dumps(finish_items,separators=(',',':'))+";\nFINISH_GEOMETRY.forEach(e=>G[e.group].boxes.push(e.vertices.flat()));\nGROUPS.find(g=>g.id==='tangga').prof='Pelat tekuk3mm / 176bagian native / 56bidang';\nGROUPS.filter(g=>['riser','skirt'].includes(g.id)).forEach(g=>{g.off=false;g.mat='Pelat baja2mm / cat hitam';g.prof='Pelat penutup2mm / dicat';g.name=g.id==='riser'?'Riser, fascia dan return2mm':'Penutup kedua sisi2mm';g.note='310bagian total; belakang/bawah terbuka. Luas dan berat di RAB R04.';});\n"
build.JS_3D=build.JS_3D[:pos]+finish_js+build.JS_3D[pos:]
build.JS_3D=build.JS_3D.replace('if(j){','if(j && document.getElementById(j[0])){')
build.JS_3D=build.JS_3D.replace('type="checkbox" checked><span class="sw"', 'type="checkbox" ${g.off?\'\':\'checked\'}><span class="sw"')
build.JS_3D=build.JS_3D.replace("mat:'Baja BJ 37", "mat:'Baja — mutu belum diverifikasi")
# For the unchanged framing row, use the verified combined stock result. User edits
# deliberately revert to an estimate; column and railing quantities stay separate.
build.JS=build.JS.replace("const Lw=r.L*(1+S.wH/100), kg=Lw*(r.kg||0), bars=Math.ceil(Lw/(S.bar||6));",f"const verified=r.n===165 && r.nm==='Rangka RHS — hasil model' && Math.abs(r.L-{round(cut,2)})<.005 && S.bar===6 && S.wH===5; const Lw=verified?{frame_stock_m}:r.L*(1+S.wH/100), kg=Lw*(r.kg||0), bars=verified?{frame_bars}:Math.ceil(Lw/(S.bar||6));")
build.JS=build.JS.replace('ppn:11','ppn:0').replace("$('ppn').value=11", "$('ppn').value=0")
build.JS=build.JS.replace('load();', '''load();
document.getElementById('catalog-prices')?.addEventListener('click',()=>{
 let n=0;
 S.rows.hollow.forEach(r=>{if((r.nm==='Rangka RHS — hasil model'||r.nm==='Kolom — hasil model')&&(r.p==null||r.p==='')){r.p=434500;r.u='btg';n++;}});
 S.rows.plate.forEach(r=>{if(r.nm==='Dek bordes 4 mm — hasil model'&&(r.p==null||r.p==='')){r.p=1273000;r.u='lbr';n++;}});
 S.price=true;document.getElementById('tgPrice').checked=true;save();render();document.getElementById('catalog-price-status').textContent=n+' harga kosong diisi. Harga termasuk PPN pemasok; periksa pajak rekap agar tidak dihitung dua kali.';
});''')
old_formula='{f:`E${R}*(1+${W_H})`,s:s.n2}'
new_formula='{f:`IF(AND(B${R}="Rangka RHS — hasil model",D${R}=165,ABS(E${R}-'+str(round(cut,2))+')<0.005,${BARC}=6,${W_H}=0.05),'+str(frame_stock_m)+',E${R}*(1+${W_H}))`,s:s.n2}'
assert old_formula in build.JS
build.JS=build.JS.replace(old_formula,new_formula)
build.JS=build.JS.replace("const byT={};\n  S.rows.plate.forEach(r=>{byT[r.t]=(byT[r.t]||0)+(+r.A||0)});\n  Object.entries(byT).forEach(([t,A])=>{", "S.rows.plate.forEach(r=>{const t=r.t,A=+r.A||0;")
build.JS=build.JS.replace('`<tr><td>Pelat ${t} mm</td>', '`<tr><td>${esc(r.nm)} / ${t} mm</td>')
build.JS=kg_pricing.patch(build.JS)
raw=build.build();s=BeautifulSoup(raw,'html.parser')
for sel in ['.top','.hero','#indeks','#ixprev','#spek','.foot']:
 for el in s.select(sel):el.decompose()
main=s.select_one('main');header=BeautifulSoup('''<header class="mast"><a href="#" class="wordmark">METTA<span>®</span></a><span class="edition">TRIBUN / LT 04<br>KOORDINASI · 07.09.26</span><nav><a href="#tiga-d">Model ↗</a><a href="#boq">BOQ ↗</a><a href="#potong">Potong ↗</a></nav></header><section class="intro"><div class="intro-line"><h1>LESS STEEL.<br>MORE CLARITY.</h1><span class="edition-number">04<span>mm</span></span></div><div class="intro-bottom"><p>Tribun METTA. Model, material,<br>dan biaya dalam satu tempat.</p><p class="status"><span></span> Studi koordinasi<br>Belum untuk fabrikasi</p><a class="circle-link" href="#tiga-d" aria-label="Lihat model">↓</a></div></section><div class="facts-new"><div><b>17,70 × 5,00</b><span>meter · 5 tingkat</span></div><div><b>80</b><span>titik dudukan</span></div><div><b>8 X</b><span>16 diagonal · +150 mm</span></div><div><b>82,35 m²</b><span>Area dek Revit</span></div></div>''','html.parser')
main.insert(0,header)
s.select_one('#tiga-d h2').string='01 / Explore the structure.'
s.select_one('#tiga-d .lede').string='Putar, pisahkan lapisan, atau pilih komponen. Struktur utama mengikuti audit Revit dan revisi +150 mm. Geometri batas luar 95 elemen railing, 56 pelat tangga, 15 papan pinus dan 31 nosing dicocokkan dengan ID model aktif. Sandaran, penutup dan konteks tetap skema lama; profil dan sambungan disederhanakan.'
s.select_one('#boq h2').string='02 / Know the quantities.'
s.select_one('#boq .lede').string='Isi harga untuk menyusun estimasi. Kuantitas rangka dan dek sudah diperbarui; item berlabel estimasi lama belum diukur ulang. Sambungan, angkur, las, dan cat belum masuk total. Harga kosong bukan barang gratis.'
s.select_one('#potong h2').string='03 / Make every cut count.'
s.select_one('#potong .lede').string='Rangka 161 batang: minimum 75 stok × 6 m pada input studi, sisa + kerf 7,725%. Kolom dan railing di bawah memakai perkiraan pembelian terpisah. Perubahan panjang atau allowance membatalkan pola potong ini.'
download=BeautifulSoup('<p class="download"><a href="assets/Daftar-potong-RHS-OPTIMASI-STUDI.csv" download>↓ Unduh pola 75 batang (CSV)</a><a href="assets/Persiapan-fabrikasi-METTA.md" download>↓ Catatan revisi</a></p>','html.parser');s.select_one('#potong').insert(2,download)
s.select_one('#penawaran h2').string='04 / Put a price on it.'
s.select_one('footer') if s.select_one('footer') else None
main.append(BeautifulSoup('''<section class="review" id="spek"><p class="eyebrow">SEBELUM PRODUKSI</p><h2>Detail matters.</h2><div class="review-grid"><p><b>Dudukan lepas.</b><br>Base plate di atas karet. Tidak ada angkur ke pelat lantai. Ikatan ke kolom beton perlu diperiksa.</p><p><b>Data yang belum final.</b><br>Sertifikat baja dan tebal dasar bordes belum diterima. Sambungan dan kapasitas beton belum diverifikasi.</p><p><b>Dari 75,50 ke 82,35 m².</b><br>BOQ kini memakai jumlah Area 30 elemen dek Revit, bukan luas nominal web lama. Dua elemen memiliki luas nol dan perlu audit lanjut.</p></div><details><summary>Gambar dan perhitungan versi sebelumnya</summary><p>Arsip sumber 8 mm tersedia di <a href="https://bambssquad.github.io/boq-tribun-metta/" target="_blank" rel="noopener">web lama</a>. Jangan pakai detail lama sebagai detail final revisi 4 mm.</p></details></section><footer class="new-foot"><strong>METTA.</strong><span>MODEL / MATERIAL / COST<br>Preview pribadi · bukan gambar fabrikasi</span><a href="#">Kembali ke atas ↑</a></footer>''','html.parser'))
# Remove obsolete branding links and claims from the reused export template.
for a in s.select('a[href*="claude.ai"]'):a.decompose()
s=experience.enhance(s)
s=pitch.present(s)
s=kg_pricing.enhance(s)
html=str(s).replace('gambar kerja fabrikasi','studi koordinasi').replace('value="11"','value="0"')
css=(ROOT/'theme.css').read_text()+'\n'+(ROOT/'experience.css').read_text()+'\n'+(ROOT/'pitch.css').read_text()+'\n'+(ROOT/'glass.css').read_text(encoding='utf-8')
html='<!doctype html><html lang="id" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>METTA — Proposal Desain Tribun</title></head><body>'+html+'<style>'+css+'</style></body></html>'
dist=ROOT/'dist';dist.mkdir(exist_ok=True);(dist/'index.html').write_text(html,encoding='utf-8')
if (ROOT/'assets').exists():shutil.copytree(ROOT/'assets',dist/'assets',dirs_exist_ok=True)
import lookback
lookback.build(dist)
import r04_web
r04_web.build(dist,r04)
import rab_download
rab_download.build(dist)
print(json.dumps(dict(bytes=len(html),frame_count=len(rhs),column_count=len(model['columns']),frame_cut_m=cut,column_m=collen,deck_area_m2=model['deck_area_m2'])))
