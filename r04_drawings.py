"""Native DXF linework/dimensions and matching SVG/PDF proposal sheets."""
import json,math,html,zipfile
import numpy as np
import ezdxf
from reportlab.pdfgen import canvas
from pathlib import Path
from technical import Drawing
from dimensioning import dimension
from revision04 import OUT,build_data

def drawings(data):
 ds=[]
 def sheet(code,title,notes):
  d=Drawing(8);d.code=code;d.title=title;d.notes=notes;ds.append(d);return d
 d=sheet('T-01','Denah modul tangga / tumpuan',[
  '56 bidang sesuai outline IFC; luas setiap bidang cocok dengan audit Revit sebelum penggantian.',
  'Tapak 600 / 800 / 2000; pengaku SHS40x40x2, jarak bersih <=75; stringer RHS50x100x2,3.',
  'Stringer pada sisi dan antara: bentang pengaku <=800. Jalur ke rangka utama perlu koordinasi node.'])
 for r in data['stairs']:
  for part in r['profile']['parts']:
   for ring in [part['outer'],*part['holes']]:
    for a,b in zip(ring,ring[1:]):d.line(a,b)
 for x in [0,17700]:d.line((x,0),(x,5000),'grid')
 dimension(d,(0,0),(17700,0),-650,130);dimension(d,(17700,0),(17700,5000),-550,100)
 d.text(2500,5600,'DEK BORDES 4 mm / 6 X BELAKANG + 2 X SISI + 2 X DEK',150)
 d=sheet('T-02','Pelat tekuk 3 mm / pengaku tapak',[
  'Ukuran contoh tapak 800x266,7. Lebar lain600/2000; landing dalam466,6, lihat jadwal JSON.',
  'Dua tekukan90 derajat; dimensi luar flange50. Ri3 dan K0,40 adalah asumsi uji kupon bengkel.',
  'Celah bersih penyangga <=75; antiselip agregat di seluruh bidang injak, nosing warna kontras.'])
 # Cross section in depth / elevation, actual thickness.
 D=266.7
 d.rect(0,0,D,3);d.rect(0,-47,3,47);d.rect(D-3,-47,3,47)
 for xx in [3,3+(D-46)/2,D-43]:d.rect(xx,-40,40,40,'balok');d.rect(xx+2,-38,36,36,'context')
 dimension(d,(0,3),(D,3),60,12,label='266,7');dimension(d,(D,-47),(D,3),-45,10,label='50 luar')
 dimension(d,(43,-40),(3+(D-46)/2,-40),-30,10,label='70,35 bersih')
 d.text(0,105,'POTONGAN TAPAK / t3 / SHS40x40x2',13)
 # Plan below: same relative structure, beam along width.
 d.rect(0,-650,800,D)
 for yy in [-647,-647+(D-46)/2,-650+D-43]:d.rect(0,yy,800,40,'balok')
 for xx in [0,750]:d.rect(xx,-647,50,D-6,'bracing')
 dimension(d,(0,-650),(800,-650),-55,14,label='800 / contoh');dimension(d,(800,-650),(800,-650+D),-50,12)
 d.text(0,-320,'DENAH / 3 PENGAKU + 2 STRINGER MODUL',15)
 d.text(430,65,'Landing466,6:5pengaku',13);d.text(430,35,'Lebar2000:4garis stringer',13)
 d=sheet('T-03','Sambungan baut / las bengkel',[
  'Usulan kupingan samping6mm 90x120:2bautM12 kelas8.8, lubang14, 2ring/baut; bukan end plate menutup RHS.',
  'Las sudut kaki3mm di bengkel; panjang efektif dan pelat penerima harus dihitung dari gaya node.',
  'Baut mengikat kupingan di luar rongga RHS; jangan kencangkan langsung menekan dinding hollow2,3mm.'])
 d.rect(0,0,90,120);d.rect(170,0,90,120,'context')
 for x in [45,215]:
  for y in [25,95]:
   for k in range(32):
    a=k*math.tau/32;b=(k+1)*math.tau/32;d.line((x+7*math.cos(a),y+7*math.sin(a)),(x+7*math.cos(b),y+7*math.sin(b)))
 dimension(d,(0,0),(90,0),-25,6);dimension(d,(90,0),(90,120),-25,6)
 dimension(d,(0,25),(0,95),22,6,label='70 pitch');dimension(d,(0,0),(0,25),22,5,label='25 tepi')
 d.rect(-100,10,120,100,'context')
 d.text(-100,180,'RHS / ujung pada x20; baut pada x45',7)
 d.text(0,150,'KUPINGAN SAMPING 6',8);d.text(170,150,'PELAT PENERIMA 6',8)
 d.text(0,-70,'2 x M12 - lubang14 / baut40 nominal',8)
 d.rect(50,-290,50,100,'balok');d.rect(52.3,-287.7,45.4,95.4,'context')
 d.rect(100,-275,6,120);d.rect(106,-275,6,120,'context');d.rect(112,-250,110,50,'balok')
 for yy in [-250,-180]:d.rect(90,yy,40,12)
 d.text(0,-340,'SKEMA PASANG / pelat sambungan di luar profil',8)
 d.text(0,-365,'Akses kunci >=30; detail penerima mengikuti node rangka',7)
 d.text(0,-390,'Dudukan gravitasi dan pengaku stabilitas diperiksa terpisah',7)
 d=sheet('T-04','Bentangan / nesting / urutan kerja',[
  'Stok1200x2400, trim10mm, kerf3mm. Pilihan terbaik dari160varian potong lurus; bukan optimum global.',
  'BD pertekuk = 2(Ri+t) - pi/2(Ri+K.t); blank = D+2x50-2BD, dibulatkan ke atas1mm.',
  'Ukur > kupon tekuk > potong dan bor > tekuk > las jig > trial fit > cat > baut lokasi > touch-up.'])
 # One verified nesting sheet with all actual placements.
 d.rect(0,0,2400,1200)
 for row in data['nesting'][0]:
  for p in row['parts']:
   d.rect(p['x'],p['y'],p['w'],p['h'])
   label=p['id']+' / '+str(p['w'])+'x'+str(p['h'])
   d.text(p['x']+10,p['y']+p['h']/2,label,min(22,(p['w']-20)/max(1,len(label))/.62))
 dimension(d,(0,0),(2400,0),-120,35);dimension(d,(2400,0),(2400,1200),-130,30)
 d.text(0,1380,f"56 BLANK / {len(data['nesting'])} LEMBAR / LUAS {data['flat_area']:.3f} m2",55)
 d.text(0,-330,'Contoh flat tapak266,7: 356 mm; landing466,6: 556 mm',35)
 d.text(0,-430,'BD = '+f"{data['bend_deduction']:.3f}"+' mm per tekukan (asumsi)',35)
 d=sheet('T-05','Penutup 2 mm / tampak dan takikan',[
  'Riser, fascia dan sisi tertutup; belakang dan bawah terbuka. Semua permukaan baja dicat.',
  'Penutup di luar muka balok. Return25mm; empat kolom beton diberi celah3mm; tidak ditutup menembus beton.',
  f"{len(data['enclosure']['panels'])} bagian native / {data['enclosure']['area']:.3f}m2 / {data['enclosure']['net_kg']:.3f}kg teoritis. Sekrup dan backing mengikuti detail pemasangan."])
 for r in data['enclosure']['panels']:
  if r['plane']=='yz' and r['x']<0:d.rect(r['y'],r['z'],r['width'],r['height'])
 dimension(d,(-27,0),(5492,0),-300,65)
 dimension(d,(5492,0),(5492,2540),-300,60,label='2540 / 2500 + fascia40')
 for y in [0,1000,2000,3000,4000,5000]:d.line((y,-80),(y,2600),'grid')
 d.text(500,2950,'SAMPING KIRI / PANEL DIPOTONG DI KOLOM BETON',100)
 for c in json.loads((OUT.parent.parent/'data/r04-concrete-context.json').read_text()):
  if c['lo'][0]<0<c['hi'][0]:
   d.rect(c['lo'][1],0,c['hi'][1]-c['lo'][1],2700,'context')
   dimension(d,(c['lo'][1]-3,2700),(c['hi'][1]+3,2700),120,40,label='506 / kolom500 + 2x3')
 # Enlarged corner, at drawing-right. Exact abutting solids, no double-volume corner.
 ox=6600;oz=1300;scale=10
 d.rect(ox,oz,20,400);d.rect(ox+20,oz+380,250,20)
 dimension(d,(ox,oz),(ox,oz+400),100,28,label='40 fascia')
 dimension(d,(ox+20,oz+400),(ox+270,oz+400),100,28,label='25 return')
 d.text(ox-100,oz-250,'DETAIL TEPI / t2 / pembesaran10x',45)
 d=sheet('T-06','Bracing X / posisi revisi native',[
  '10setX:6belakang,2sisi tetap,2mendatar di bawah dek+1500.12diagonal belakang lama telah dihapus.',
  'X belakang memakai bidangY4970/5030 agar diagonal bersilang tanpa bertabrakan. Sambungan ujung belum final.',
  'X mendatar: lapis atas1325..1375 dan bawah1265..1315; celah10mm. Ukuran profil RHS50x100x2,3.'])
 rear=json.loads((OUT.parent.parent/'data/r04-rear-braces.json').read_text())
 for r in rear:d.line((r['x0'],r['startZ']),(r['x1'],r['endZ']),'bracing')
 for x in sorted({p[k] for p in rear for k in ['x0','x1']}):d.line((x,18),(x,2500),'balok')
 dimension(d,(0,0),(17700,0),-350,100)
 for r in rear[::2]:dimension(d,(r['x0'],2350),(r['x1'],2350),350,65)
 d.text(0,3250,'TAMPAK BELAKANG / NODE +150 DAN +2350',140)
 dy=-6700
 d.rect(0,dy,17700,5000,'grid')
 for x0,x1 in [(3540,4830),(12870,14160)]:
  d.rect(x0,2000+dy,x1-x0,1000,'balok')
  d.line((x0,2000+dy),(x1,3000+dy),'bracing');d.line((x0,3000+dy),(x1,2000+dy),'bracing')
  dimension(d,(x0,2000+dy),(x1,2000+dy),-300,80,label='1290')
 dimension(d,(14160,2000+dy),(14160,3000+dy),-500,80,label='1000')
 d.text(0,dy-750,'DENAH X MENDATAR / DI BAWAH DEK +1500',140)
 return ds

def create():
 data=build_data();ds=drawings(data);pdf=canvas.Canvas(str(OUT/'METTA-R04-tangga-detail.pdf'),pagesize=(1191,842));manifest=[]
 for d in ds:
  lo,hi=d.bounds();span=np.maximum(hi-lo,[1,1]);sc=min(990/span[0],465/span[1])*.86;off=np.array([(1191-span[0]*sc)/2,210+(465-span[1]*sc)/2])-lo*sc
  xy=lambda p:(np.array(p)*sc+off).tolist()
  svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1191 842"><rect width="1191" height="842" fill="white"/>']
  doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace()
  for lay in ['detail','dim','bracing','context','balok','grid']:doc.layers.new(lay,dxfattribs={'color':7})
  dimlines={i for q in d.dimensions for i in q['vector_lines']};dimlabels={q['vector_label'] for q in d.dimensions}
  for q in d.dimensions:ms.add_aligned_dim(p1=q['a'],p2=q['b'],distance=q['offset'],text=q['label'],override={'dimtxt':q['height'],'dimasz':q['height']*.35}).render()
  for i,(a,b,g) in enumerate(d.lines):
   x,y=xy(a);X,Y=xy(b);pdf.setStrokeGray(.6 if g=='context' else .15);pdf.setLineWidth(.65);pdf.line(x,y,X,Y);svg.append(f'<path d="M{x:.2f},{842-y:.2f}L{X:.2f},{842-Y:.2f}" fill="none" stroke="#333" stroke-width=".7"/>')
   if i not in dimlines:ms.add_line(a,b,dxfattribs={'layer':g})
  texts=[]
  for i,(x,y,t,h) in enumerate(d.labels):
   X,Y=xy((x,y));texts.append((X,Y,t,max(8,min(13,h*sc))))
   if i not in dimlabels:ms.add_text(t,dxfattribs={'height':h,'insert':(x,y)})
  texts += [(40,792,'SAP / SELARAS ADHI PERKASA',18),(40,756,d.code+'  '+d.title.upper(),23),(940,793,'METTA / R04',13),(940,770,'09.09.2026',12),(40,42,'mm / NTS | LOD200 koordinasi; detail usulan terukur, belum rilis fabrikasi.',11)]
  texts += [(40,145-i*22,n,11) for i,n in enumerate(d.notes)]
  for x,y,t,s in texts:
   pdf.setFillGray(.08);pdf.setFont('Helvetica',s);pdf.drawString(x,y,t);svg.append(f'<text x="{x:.2f}" y="{842-y:.2f}" font-family="Arial" font-size="{s:.2f}" fill="#111">{html.escape(t)}</text>')
  svg.append('</svg>');(OUT/(d.code+'.svg')).write_text(''.join(svg),encoding='utf8');doc.saveas(OUT/(d.code+'.dxf'));pdf.showPage();manifest.append(dict(code=d.code,title=d.title,notes=d.notes,dimensions=len(d.dimensions)))
 pdf.save();(OUT/'drawings.json').write_text(json.dumps(manifest,ensure_ascii=False),encoding='utf8')
 with zipfile.ZipFile(OUT/'METTA-R04-DXF.zip','w',zipfile.ZIP_DEFLATED) as z:
  for d in ds:z.write(OUT/(d.code+'.dxf'),d.code+'.dxf')
 print(f'R04:{len(ds)} CAD/PDF/SVG sheets generated')
if __name__=='__main__':create()
