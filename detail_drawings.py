"""Zoomable vector coordination sheets, derived from archived solids and R08 proposals."""
import html,json,shutil
from pathlib import Path
from shapely.geometry import MultiPoint
import r04_model
ROOT=Path(__file__).parent
def build(dist):
 out=Path(dist)/'assets/drawings';out.mkdir(parents=True,exist_ok=True)
 g=json.loads((ROOT/'assets/r08/geometry.json').read_text()); native=r04_model.load_model()['items']
 manifest={'status':'LOD 100 / koordinasi konseptual; bukan gambar fabrikasi','units':'mm','versions':{}}
 def start(title):
  return ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950"><rect width="1400" height="950" fill="#faf9f5"/><style>text{font:17px Arial;fill:#173d45}.title{font-size:28px;font-weight:bold}.small{font-size:14px}.dim{stroke:#52747b;stroke-width:1;fill:none}</style>',f'<text x="45" y="50" class="title">{html.escape(title)}</text><text x="45" y="82">Satuan mm · arsip geometri R04 + usulan R08 · dimensi dibulatkan 1 mm</text>']
 def txt(a,x,y,t,cl=''):a.append(f'<text x="{x}" y="{y}" class="{cl}">{html.escape(str(t))}</text>')
 def line(a,x,y,X,Y):a.append(f'<path class="dim" d="M{x:.2f} {y:.2f}L{X:.2f} {Y:.2f}"/>')
 def dim(a,x,X,y,label):
  line(a,x,y,X,y);line(a,x,y-6,x,y+6);line(a,X,y-6,X,y+6);txt(a,(x+X)/2-20,y-10,label,'small')
 def end(a,name,notes):
  for i,t in enumerate(notes):txt(a,45,775+i*25,t,'small')
  line(a,45,910,1355,910);txt(a,45,935,'METTA · LOD 100 / KOORDINASI KONSEPTUAL · BELUM UNTUK FABRIKASI','small')
  a.append('</svg>');(out/name).write_text(''.join(a),encoding='utf-8')
 def projection(a,items,axes,origin,scale,filter_fn=lambda e:True):
  for e in items:
   if not filter_fn(e):continue
   pts=[(origin[0]+v[axes[0]]*scale,origin[1]-v[axes[1]]*scale) for v in e['vertices']]
   shape=MultiPoint(pts).convex_hull
   if shape.geom_type!='Polygon':continue
   coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in shape.exterior.coords)
   proposed=str(e['id']).startswith('I');fill='#dba64f' if proposed else '#b9ced0'
   a.append(f'<polygon data-member="{html.escape(str(e["id"]))}" points="{coords}" fill="{fill}" stroke="#2d5962" stroke-width=".7"><title>{html.escape(str(e["id"]))} / {html.escape(e["group"])}</title></polygon>')
 for version in ('v1','v2'):
  sheets=[]
  def add(name,title):sheets.append({'file':name,'title':title})
  src='01-denah-r07.svg' if version=='v1' else '01-denah-r08.svg'
  # Preserve measured polygon detail, but label its coordination status consistently.
  plan=(ROOT/'assets/r08'/src).read_text(encoding='utf-8').replace('STUDIO KOORDINASI','LOD 100 / KOORDINASI KONSEPTUAL')
  if version=='v1':
   plan=plan.replace('R08 mempertahankan tiga strip jalur nominal 600 mm pada dua zona. Lebar efektif belum dikurangi pegangan.', 'V1: zona tangga kiri 2000 mm dan kanan 600 mm. Lebar efektif perlu pemeriksaan pegangan.')
   plan=plan.replace('Tambahan tempat duduk indikatif: 4 (modul 500 mm; baris ke-4 terpotong kolom beton).','V1: panel tengah zona kiri tetap tangga; tidak ada tambahan dudukan infill.')
   plan=plan.replace('METTA / R08 /','METTA / V1 /')
  (out/f'{version}-01-plan.svg').write_text(plan,encoding='utf-8');add(f'{version}-01-plan.svg','01 · Denah tribun dan akses')
  structural=[e for e in native if e['group'] in ('kolom','balok','stiffener','bracing') and (version=='v1' or e['id'] in g['retained_native_ids'])]
  if version=='v2':structural+=g['frame']
  a=start(version.upper()+' / 02 · Denah rangka dan jejak kolom')
  projection(a,structural,(0,1),(90,620),.067)
  dim(a,90,90+17700*.067,190,'17700')
  for x,X in [(4850.0373,5450.0373),(5450.0373,6250.0763),(6250.0763,6850.0751),(12250.0643,12850.0631)]:dim(a,90+x*.067,90+X*.067,700,str(round(X-x)))
  end(a,f'{version}-02-frame.svg',['Biru: solid luar arsip. Emas: usulan rangka infill V2. Buka SVG lalu hover elemen untuk ID sumber.',
   'Proyeksi seluruh rangka; garis yang saling silang belum membuktikan sambungan atau transfer gaya.',
   'Tebal RHS 50×100 mengikuti toggle RAB; gambar solid luar tidak memperlihatkan tebal dinding.',
   'Penempatan tumpuan dan detail sambungan tetap harus diperiksa terhadap model analisis.'])
  add(f'{version}-02-frame.svg','02 · Denah rangka dengan ID elemen')
  a=start(version.upper()+' / 03 · Tampak rangka depan dan potongan sisi')
  projection(a,structural,(0,2),(80,360),.067);dim(a,80,80+17700*.067,405,'17700')
  # A genuine slice avoids implying every frame lies in one plane.
  section_x=3540
  projection(a,structural,(1,2),(120,730),.08,lambda e:min(v[0] for v in e['vertices'])<=section_x<=max(v[0] for v in e['vertices']))
  txt(a,670,475,'POTONGAN A–A / x = 3540 dari sisi kiri')
  txt(a,670,510,'Hanya solid yang memotong bidang A–A ditampilkan.','small')
  txt(a,670,545,'Tinggi tingkat nominal: +500 / +1000 / +1500 / +2000 / +2500','small')
  txt(a,670,580,'Kedalaman modul nominal: 1000; platform belakang: 492','small')
  txt(a,670,615,'Elevasi solid aktual dapat berbeda karena tebal dek dan dudukan.','small')
  for y in range(0,5000,1000):dim(a,120+y*.08,120+(y+1000)*.08,754,'1000')
  end(a,f'{version}-03-sections.svg',['Tampak depan adalah proyeksi rangka; komponen di belakang tetap terlihat sebagai gambar koordinasi.',
   'Potongan A–A dipilih dari geometri; railing, finishing dan fondasi tidak termasuk proyeksi rangka ini.',
   'Jangan ukur layar untuk panjang fabrikasi. Daftar potong dan dimensi sambungan harus dirilis tersendiri.'])
  add(f'{version}-03-sections.svg','03 · Tampak rangka dan potongan A–A')
  a=start(version.upper()+' / 04 · Detail simpul — skema koordinasi')
  a.append('<g fill="#bbd2d2" stroke="#285863" stroke-width="2"><rect x="210" y="245" width="120" height="310"/><rect x="150" y="555" width="240" height="13"/><rect x="130" y="185" width="470" height="60"/><rect x="120" y="170" width="490" height="15"/></g>')
  txt(a,150,630,'SKEMA TUMPUAN / tidak berskala')
  for i,t in enumerate(['Dek → pengaku → balok → kolom → pelat dasar → lantai.',
   'RHS 50×100; tebal mengikuti konfigurasi RAB.',
   'Pelat dasar lama: 150×150×8 (arsip).',
   'V2 infill: 140×150×8 + karet 3 (usulan).',
   'Las, baut, lubang, jarak tepi dan angkur: belum didesain.',
   'Jumlah angkur dalam RAB adalah allowance, bukan kapasitas.',
   'Periksa tekuk lokal, torsi, eksentrisitas dan reaksi lantai.',
   'Mesh penutup tidak dimasukkan sebagai bracing.']):txt(a,660,210+i*45,t,'small')
  end(a,f'{version}-04-joint.svg',['Gambar memperjelas urutan lapisan. Ukuran las dan angkur sengaja tidak ditetapkan tanpa perhitungan.',
   'LOD 100 = tujuan konseptual; detail visual ini tidak mengubah status menjadi gambar pelaksanaan.',
   'Agar siap fabrikasi: finalisasi mutu, sambungan, toleransi, korosi, ereksi dan verifikasi insinyur.'])
  add(f'{version}-04-joint.svg','04 · Detail simpul dan batas desain')
  if version=='v2':
   for src,title in [('02-infill.svg','05 · Infill, takikan beton dan lapisan'),('03-mesh.svg','06 · Penutup mesh dan penjepit')]:
    name=version+'-'+src;shutil.copy2(ROOT/'assets/r08'/src,out/name);add(name,title)
  columns=sorted([e for e in structural if e['group'] in ('kolom','I01')],key=lambda e:(sum(v[1] for v in e['vertices']),sum(v[0] for v in e['vertices'])))
  for page in range((len(columns)+23)//24):
   a=start(version.upper()+f' / K{page+1:02} · Jadwal koordinat kolom')
   for x,t in [(45,'ID sumber'),(340,'X pusat'),(510,'Y pusat'),(680,'Z bawah'),(850,'Z atas'),(1020,'Panjang solid'),(1210,'Dasar')]:txt(a,x,140,t,'small')
   for row,e in enumerate(columns[page*24:(page+1)*24]):
    lo=[min(v[i] for v in e['vertices']) for i in range(3)];hi=[max(v[i] for v in e['vertices']) for i in range(3)]
    vals=[str(e['id']),f'{(lo[0]+hi[0])/2:.1f}',f'{(lo[1]+hi[1])/2:.1f}',f'{lo[2]:.1f}',f'{hi[2]:.1f}',f'{hi[2]-lo[2]:.1f}','Usulan' if e['group']=='I01' else 'Arsip']
    for x,t in zip([45,340,510,680,850,1020,1210],vals):txt(a,x,170+row*24,t,'small')
    line(a,45,178+row*24,1355,178+row*24)
   name=f'{version}-K{page+1:02}-columns.svg'
   end(a,name,[f'Kolom {page*24+1}–{min(len(columns),(page+1)*24)} dari {len(columns)}; koordinat lokal dalam mm; titik nol mengikuti arsip geometri.',
    'Panjang solid adalah selisih elevasi luar. Angka ini bukan panjang potong final atau tinggi bersih pemasangan.',
    'Koordinat tidak mencakup toleransi, kemiringan lantai, lubang angkur atau keputusan sambungan.'])
   add(name,f'K{page+1:02} · Koordinat kolom {page*24+1}–{min(len(columns),(page+1)*24)}')
  manifest['versions'][version]=sheets
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 for file in ('drawing-viewer.js','drawing-viewer.css'):shutil.copy2(ROOT/file,Path(dist)/'assets'/file)
 return manifest
if __name__=='__main__':build(ROOT)
