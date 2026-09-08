"""Auditable coordination drawings. DXF model space is in millimetres.
No member or connection capacity is certified by these projections.
"""
import json, math, html, csv, zipfile
from pathlib import Path
import numpy as np
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).parent
OUT=ROOT/'assets'/'technical'; OUT.mkdir(parents=True,exist_ok=True)
MODEL=json.loads((ROOT/'data/model.json').read_text())
COLORS={'dek':'#657f45','kolom':'#1c292c','balok':'#31596b','stiffener':'#698491','bracing':'#b64a45','baseplate':'#746052','dim':'#526e80','detail':'#303330','context':'#90948d'}
EDGES=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
TITLES=['Denah tribun','Rencana tumpuan','Rencana rangka & X','Tampak depan','Tampak samping','Potongan portal','Potongan tangga','Detail anak tangga','Railing & balustrade','Base plate & karet','Sambungan D1-D4','Urutan pemasangan']
NOTES=[
 ['Dek bordes 4 mm. Proyeksi batas luar model; bukaan di sekitar beton harus disurvei.', 'Area BOQ 82,345 m2 dari parameter Revit; bukan luas proyeksi persegi gambar ini.'],
 ['80 kolom, 80 base plate 150x150x8, 80 karet 150x150x10.', 'Dasar kolom +18 mm. Dudukan lepas tidak otomatis menjadi sendi yang menahan geser/angkat.'],
 ['161 RHS 50x100x2,3 termasuk 16 diagonal / 8 X. Node bawah +150 mm.', '45 joist longitudinal dan 65 balok silang mengikuti revisi model; celah sambungan belum final.'],
 ['Proyeksi rangka dari lapangan. Semua tingkat terlihat transparan; garis belakang tidak dihapus.', 'Finishing, railing dan tangga perlu dicocokkan dengan model arsitektur.'],
 ['Potongan sisi x=0, toleransi seleksi 100 mm; tinggi tier nominal 500/1000/1500/2000/2500.', 'X melintang tetap studi. Penyaluran gaya horizontal ke beton belum terverifikasi.'],
 ['Potongan portal x=1770, toleransi seleksi 100 mm. Dek 4 mm; tumpuan utama mengikuti model.', 'Jarak penyangga 250 mm adalah target studi dek, bukan bukti beban titik dan getaran lulus.'],
 ['Geometri tangga dari web arsitektur; 5 tier, kenaikan per tier 500 mm.', 'Jalur 2000 mm terpotong kolom beton; jalur 600 mm belum dibuktikan memenuhi evakuasi.'],
 ['Satu modul usulan: 3 kenaikan 166,67 mm; tapak 267 mm, sisa landing 199 mm.', 'Bordes 4 mm. Radius tekuk, bentangan potong dan rangka tangga belum ditetapkan.'],
 ['Skema koordinasi: tinggi 1100 mm, bukaan bersih baluster <=100 mm sebagai target studi.', 'Beban pagar, pemanjatan, sambungan dan lebar jalur harus diperiksa; ukuran bukan persetujuan.'],
 ['Dudukan sesuai model: karet 10, base plate 8, kolom mulai +18 mm.', 'Tanpa angkur ke pelat LT4 mengikuti konsep sumber. Las dan tahan geser/angkat belum dirancang.'],
 ['D1 balok-kolom; D2 X-kolom; D3 ikatan ke beton; D4 railing-rangka.', 'Skema jalur gaya saja. Diameter baut, las, gusset dan angkur lama tidak berlaku otomatis.'],
 ['Urutan: survei beton / marking > karet & dudukan > kolom > balok & X > dek > tangga & railing.', 'Gunakan penyangga sementara; lepas setelah stabilitas dan semua sambungan diperiksa.']]

class Drawing:
 def __init__(self,idx): self.idx=idx;self.code=f'S-{idx:02}';self.title=TITLES[idx-1];self.lines=[];self.labels=[]
 def line(self,a,b,g='detail'):
  a=tuple(map(float,a));b=tuple(map(float,b))
  if math.dist(a,b)>.001:self.lines.append((a,b,g))
 def rect(self,x,y,w,h,g='detail'):
  p=[(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]
  for a,b in zip(p,p[1:]):self.line(a,b,g)
 def text(self,x,y,t,h=90):self.labels.append((x,y,str(t),h))
 def dim(self,a,b,y,label):
  self.line((a,y),(b,y),'dim')
  tick=min(60,(b-a)*.02);h=min(80,max(8,(b-a)*.02))
  for x in [a,b]:self.line((x,y-tick),(x,y+tick),'dim')
  self.text((a+b)/2-len(label)*h*.25,y+tick*1.6,label,h)
 def project(self,groups,plane='xy',slice_x=None):
  seen=set()
  for e in MODEL['items']:
   if e['group'] not in groups:continue
   v=np.array(e['vertices'])
   if slice_x is not None and not(v[:,0].min()-100<=slice_x<=v[:,0].max()+100):continue
   if plane=='xy':p=v[:,[0,1]]
   elif plane=='xz':p=v[:,[0,2]]
   elif plane=='yz':p=v[:,[1,2]]
   else:p=np.column_stack((.866*(v[:,0]-v[:,1]),v[:,2]-.5*(v[:,0]+v[:,1])))
   for i,j in EDGES:
    key=tuple(sorted([tuple(np.round(p[i],1)),tuple(np.round(p[j],1))]))
    if key in seen:continue
    seen.add(key);self.line(p[i],p[j],e['group'])
 def bounds(self):
  pts=[p for a,b,g in self.lines for p in [a,b]]+[(x,y) for x,y,t,h in self.labels]
  ar=np.array(pts);lo=ar.min(0);hi=ar.max(0)
  return lo,hi

def make_drawings():
 ds=[Drawing(i) for i in range(1,13)]
 ds[0].project(['dek','kolom']);ds[1].project(['baseplate','kolom']);ds[2].project(['kolom','balok','stiffener','bracing'])
 for d in ds[:3]:d.dim(0,17700,-450,'17700');d.text(6000,5450,'BELAKANG / Y +5000',110)
 ds[3].project(['kolom','balok','stiffener','dek','baseplate'],'xz');ds[3].dim(0,17700,-350,'17700')
 for d,x in [(ds[4],0),(ds[5],1770)]:
  d.project(['kolom','balok','stiffener','dek','bracing','baseplate'],'yz',x)
  d.dim(0,5000,-300,'5000')
  for i in range(1,6):d.text(i*1000-700,i*500+150,f'+{i*500}',75)
 for d,count in [(ds[6],5),(ds[7],1)]:
  for tier in range(count):
   for k in range(3):
    y=tier*500+(k+1)*500/3;x=tier*1000+k*267
    d.line((x,y-500/3),(x,y),'dek');d.line((x,y),(x+267,y),'dek')
   d.line((tier*1000+801,(tier+1)*500),(tier*1000+1000,(tier+1)*500),'dek')
  d.dim(0,count*1000,-150,str(count*1000));d.text(0,count*500+120,'BORDES 4 mm / USULAN KOORDINASI',35 if count==1 else 85)
 d=ds[8];d.rect(0,0,2000,40,'balok');d.rect(0,1100,2000,40,'detail')
 for x in [0,1000,2000]:d.rect(x,40,40,1060,'kolom')
 for x in range(140,2000,140):d.rect(x,140,40,960,'detail')
 d.rect(0,40,2000,100,'dek');d.dim(0,2000,-160,'2000 modul ilustrasi');d.text(2150,1050,'1100',55)
 d=ds[9];d.rect(-75,0,150,10,'baseplate');d.rect(-75,10,150,8,'detail');d.rect(-25,18,50,180,'kolom');d.rect(-22.7,18,45.4,180,'context');d.line((-110,0),(110,0),'context')
 d.text(110,7,'karet 10',8);d.text(110,21,'plat 8',8);d.text(65,100,'RHS 50x100x2,3',8);d.dim(-75,75,-80,'150')
 d=ds[10]
 for i,t in enumerate(['D1 / BALOK-KOLOM','D2 / X-KOLOM','D3 / IKATAN BETON','D4 / RAILING-RANGKA']):
  x=(i%2)*1100;y=(i//2)*950
  d.text(x,y+650,t,42);d.rect(x,y,100,500,'kolom')
  if i==1:d.line((x+100,y+80),(x+530,y+500),'bracing');d.line((x+130,y+80),(x+560,y+500),'bracing')
  else:d.rect(x+100,y+300,480,100,'balok')
  d.rect(x+40,y+240,150,180,'context');d.text(x,y-120,'UKURAN SAMBUNGAN: HOLD',32)
 ds[11].project(['baseplate','kolom','balok','stiffener','bracing','dek'],'iso')
 return ds

def write_outputs(ds):
 pdf=canvas.Canvas(str(OUT/'METTA-R02-gambar-koordinasi.pdf'),pagesize=(1190.55,841.89));manifest=[]
 native=[]
 for d in ds:
  lo,hi=d.bounds();span=np.maximum(hi-lo,[1,1]);scale=min(990/span[0],500/span[1])*.88;off=np.array([(1100-span[0]*scale)/2,180+(530-span[1]*scale)/2])-lo*scale
  def xy(p):return (np.array(p)*scale+off).tolist()
  parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1191 842" role="img" aria-label="'+html.escape(d.title)+'"><rect width="1191" height="842" fill="#f5f3ed"/>']
  pdf.setFillColor(HexColor('#f5f3ed'));pdf.rect(0,0,1191,842,stroke=0,fill=1)
  doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace()
  for layer,color in COLORS.items():doc.layers.new(layer,dxfattribs={'color':7,'true_color':int(color[1:],16)})
  for a,b,g in d.lines:
   x,y=xy(a);X,Y=xy(b);col=COLORS[g]
   pdf.setStrokeColor(HexColor(col));pdf.setLineWidth(.7);pdf.line(x,y,X,Y)
   parts.append(f'<path d="M{x:.2f},{842-y:.2f}L{X:.2f},{842-Y:.2f}" stroke="{col}" fill="none" stroke-width=".8"/>')
   ms.add_line(a,b,dxfattribs={'layer':g})
  for x,y,t,h in d.labels:
   X,Y=xy((x,y));size=max(8,min(14,h*scale));pdf.setFillColor(HexColor('#26302b'));pdf.setFont('Helvetica',size);pdf.drawString(X,Y,t)
   parts.append(f'<text x="{X:.2f}" y="{842-Y:.2f}" font-family="Arial" font-size="{size:.2f}" fill="#26302b">{html.escape(t)}</text>')
   ms.add_text(t,dxfattribs={'height':h,'insert':(x,y),'layer':'dim'})
  for x,y,t,size in [(38,792,'METTA / LT 04',20),(38,752,d.code+'   '+d.title.upper(),24),(905,796,'R02 / 07.09.2026',12),(905,775,'KOORDINASI',12),(38,36,'SATUAN DXF: mm | PDF: FIT / NTS | DIMENSI TERTULIS YANG BERLAKU | BUKAN UNTUK FABRIKASI',10)]:
   pdf.setFillColor(HexColor('#1c292c'));pdf.setFont('Helvetica',size);pdf.drawString(x,y,t)
   parts.append(f'<text x="{x}" y="{842-y}" font-family="Arial" font-size="{size}" fill="#1c292c">{html.escape(t)}</text>')
  for n,t in enumerate(NOTES[d.idx-1]):
   y=115-n*22;pdf.setFont('Helvetica',11);pdf.drawString(38,y,t)
   parts.append(f'<text x="38" y="{842-y}" font-family="Arial" font-size="11">{html.escape(t)}</text>')
  parts.append('</svg>');(OUT/(d.code+'.svg')).write_text(''.join(parts),encoding='utf8')
  doc.saveas(OUT/(d.code+'.dxf'));pdf.showPage()
  manifest.append(dict(code=d.code,title=d.title,notes=NOTES[d.idx-1],svg='assets/technical/'+d.code+'.svg',dxf='assets/technical/'+d.code+'.dxf',category='Denah' if d.idx<=3 else 'Potongan' if d.idx<=7 else 'Detail'))
  # Paper-coordinate line and text data for native Revit sheet drafting, if needed.
  if d.idx in [1,2,3,8,9,10,11]:native.append(dict(code=d.code,title=d.title,lines=[(xy(a),xy(b)) for a,b,g in d.lines],labels=[(*xy((x,y)),t) for x,y,t,h in d.labels]))
 pdf.save();(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf8')
 (ROOT/'data/native-details.json').write_text(json.dumps(native),encoding='utf8')
 with zipfile.ZipFile(OUT/'METTA-R02-DXF.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in OUT.glob('S-*.dxf'):z.write(p,p.name)
 return manifest

def calculations():
 E=200000;fy=240;D=1.2;L=4.79;qs=D+L;qu=1.2*D+1.6*L;rows=[]
 for span in [250,1000/3,500]:
  t=4;I=1000*t**3/12;S=1000*t*t/6;stress=qu*span**2/(8*S);defl=5*qs*span**4/(384*E*I)
  rows.append(dict(span_mm=round(span,2),stress_MPa=round(stress,2),yield_ratio=round(stress/(.9*fy),3),deflection_mm=round(defl,3),L360_mm=round(span/360,3),pass_screen=stress<=.9*fy and defl<=span/360))
 result=dict(status='Penyaringan satu arah; bukan verifikasi SNI lengkap',assumptions=dict(E_MPa=E,Fy_MPa=fy,D_kPa=D,L_kPa=L,live_load_status='Input pembanding, kategori dan pasal SNI belum dikunci',service_kPa=qs,ultimate_kPa=qu),deck=rows,deck_base_mass_kg=MODEL['deck_area_m2']*31.4,deck_mass_reduction_kg=MODEL['deck_area_m2']*31.4,stock_frame_cost=75*434500,stock_frame_bars=75,deck_area_lower_bound_sheets=math.ceil(MODEL['deck_area_m2']/2.88),plate_catalog_price=1273000,plate_stock_status='Batas bawah luas; bukan hasil nesting, belum boleh dipakai sebagai jumlah pesanan',unverified=['beban titik dan distribusi dua arah','getaran dan kenyamanan','tekuk lokal RHS, torsi dan gaya gabungan','las/gusset/baut/angkur','geser dan angkat dudukan','kapasitas beton LT4 dan tulangan','gempa, angin, beban pagar dan evakuasi'])
 (OUT/'perhitungan-studi.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 return result

if __name__=='__main__':
 ds=make_drawings();write_outputs(ds);c=calculations()
 print(json.dumps(dict(drawings=len(ds),deck=c['deck'],deck_area=MODEL['deck_area_m2'])))
