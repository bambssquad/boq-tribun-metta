"""R04 stair proposal and cost basis. Archived Revit inputs remain immutable."""
import json, math, csv, html, zipfile
from r04_nesting import pack
from r04_enclosure import panels
from pathlib import Path
ROOT=Path(__file__).parent
OUT=ROOT/'assets'/'r04'
DATE='09.09.2026'
SOURCES={
 'steel':('SMS Perkasa / harga loco Surabaya 07.09.2026','https://www.smsperkasa.com/produk/besi-hollow-hitam'),
 'plate':('SMS Perkasa / pelat hitam 07.09.2026','https://www.smsperkasa.com/produk/plat-besi-hitam'),
 'deck':('Duta Merpati / bordes 4 mm; harga acuan audit 07.09.2026','https://dutamerpati.com/distributor/plat-bordes-40mm-1200x-2400-di-babat'),
 'bolts':('Sentral Mur Baut Surabaya / mutu 8.8 tersedia, harga allowance','https://www.sentralmurbaut.com/product-detail?name=hexagonal-bolts-nuts'),
 'screws':('PT Jaya Metal Surabaya / produsen SDS dan drilling wood; harga estimasi','https://www.ptjayametal.com/'),
 'paint':('Nippon Paint / Bodelac 2-in-1, 2 lapis, 10-13 m2/L/lapis','https://www.nipponpaint-indonesia.com/products/kayu-besi/decorative/bodelac-2-in-1-anti-karat'),
 'paintshop':('Artha Kencana Jaya Surabaya / produk tersedia; harga CALL tidak dipakai','https://www.tokocatsurabaya.com/'),
 'load':('BSN / SNI 1727:2020 / beban','https://pesta.bsn.go.id/produk/detail/12927-sni17272020'),
 'sni':('BSN / SNI 1729:2020 / baja struktural','https://pesta.bsn.go.id/produk/detail/12882-sni17292020'),
 'cold':('BSN / SNI 7971:2013 / baja canai dingin','https://pesta.bsn.go.id/produk/detail/9714-sni79712013')}

def pack_bars(cuts,stock=6000,kerf=3):
 bins=[]
 for label,L in sorted(cuts,key=lambda x:-x[1]):
  assert 0<L<=stock
  for b in bins:
   if b['used']+L+kerf<=stock:
    b['cuts'].append([label,L]);b['used']+=L+kerf;break
  else: bins.append(dict(cuts=[[label,L]],used=L+kerf))
 return bins

def build_data():
 m=json.loads((ROOT/'data/model.json').read_text());f=json.loads((ROOT/'data/finishes-audit.json').read_text());g=json.loads((ROOT/'data/finishes-geometry.json').read_text())
 profiles={r['id']:r for r in json.loads((ROOT/'data/stair-profiles-r04.json').read_text())['items']}
 stairs=[];extra=[];cross=[];stringers=[];flats=[];t=3;ri=3;K=.4
 # Outside dimensions: two 90-degree bends; BD=2(R+t)-pi/2(R+Kt).
 bd=2*(ri+t)-math.pi/2*(ri+K*t)
 def box(id,group,x,y,z,w,d,h):return dict(id=id,group=group,vertices=[[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z],[x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]])
 for item in g['items']:
  if item['group']!='tangga':continue
  v=item['vertices'];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
  w=round(hi[0]-lo[0],1);d=round(hi[1]-lo[1],1);z=hi[2]
  n=math.ceil((d-40)/115)+1;bays=math.ceil(w/800)
  flat=math.ceil(d+100-2*bd) # conservative whole-mm cutting width; coupon controls actual production.
  profile=profiles[item['id']]
  fold_length=0
  for part in profile['parts']:
   for a,b in zip(part['outer'],part['outer'][1:]):
    if abs(a[1]-b[1])<.01 and (abs(a[1]-lo[1])<.1 or abs(a[1]-hi[1])<.1):fold_length+=abs(a[0]-b[0])
  net_area=profile['area_m2']+fold_length*(50-bd)/1e6
  row=dict(id=item['id'],width=w,depth=d,flange=50,flat=flat,rails=n,bays=bays,z=z,x=lo[0],y=lo[1],profile=profile,fold_length_mm=fold_length,net_flat_area=net_area);stairs.append(row);flats.append((str(item['id']),w,flat))
  extra.append(box(item['id'],'tangga',lo[0],lo[1],z-3,w,d,3))
  for yy in [lo[1],lo[1]+d-3]:extra.append(box(str(item['id'])+'F'+str(yy),'tangga',lo[0],yy,z-50,w,3,47))
  for k in range(n):
   yy=lo[1]+3+k*(d-46)/(n-1)
   cross.append((str(item['id'])+'C'+str(k),w))
   extra.append(box(str(item['id'])+'C'+str(k),'tangga',lo[0],yy,z-43,w,40,40))
  for k in range(bays+1):
   xx=lo[0]+k*(w-50)/bays
   stringers.append((str(item['id'])+'S'+str(k),d-6))
   extra.append(box(str(item['id'])+'S'+str(k),'tangga',xx,lo[1]+3,z-143,50,d-6,100))
 # Only saved native plate parts enter the live-model representation. The support
 # proposal remains a separate cost scenario until its load path is resolved.
 extra=[]
 for p in json.loads((ROOT/'data/r04-plate-parts.json').read_text()):
  x,y,z,X,Y,Z=p['bounds'];extra.append(box(p['code'],'tangga',x,y,z,X-x,Y-y,Z-z))
 revit=json.loads((ROOT/'data/revit-r04-audit.json').read_text())
 live_rhs=[r for r in m['rhs'] if r['id'] not in revit['removed_ids']]+revit['braces']
 assert len(live_rhs)==165
 sheets=[[dict(parts=s)] for s in pack(flats)]
 enclosure=panels(m,stairs)
 enclosure['nesting']=pack([(r['code'],r['width'],r['height']) for r in enclosure['panels']])
 maincuts=[(str(r.get('id',i)),r['props']['Cut Length']*304.8) for i,r in enumerate(live_rhs)]+[(str(c.get('id',i)),c['length_mm']) for i,c in enumerate(m['columns'])]+stringers
 mainbins=pack_bars(maincuts);crossbins=pack_bars(cross)
 flatA=sum(w*h for _,w,h in flats)/1e6;boundA=sum(r['width']*r['depth'] for r in stairs)/1e6
 oldA=sum(r['area_m2'] for r in f['floor'] if 'TEKUK' in r['type'])
 mainL=sum(x[1] for x in maincuts)/1000;crossL=sum(x[1] for x in cross)/1000
 nends=len(stringers)*2 # module-to-primary ends: 2 M12 per end, 6mm end + receiving plate.
 main_joint_ends=(len(live_rhs)-20)*2-16 # 16 concrete ties are covered by M17.
 gussets=20*2
 plate6A=(nends+main_joint_ends)*2*.09*.12 + gussets*.2*.2
 plate8A=80*.15*.15
 riserA=enclosure['area'];skirtA=0
 # Paint external surfaces only; both faces of steel plates. Extra 10% for edges/welds.
 coatingA=1.1*(mainL*.3+(crossL+8.4254+97.498388)*.16+2*(82.345049121+flatA+riserA+skirtA+plate6A+plate8A))
 paintL=math.ceil(coatingA*2/10*1.25/2.5)*2.5
 weldM=(len(live_rhs)*2*.15+80*.3+len(cross)*2*.08+nends*.18+82.345049121/0.25*.1+sum(r['width'] for r in stairs)/1000*.8)*1.1
 # 3-mm LEG fillet, triangular area 4.5mm2, 7.85e-6 kg/mm3; 65% deposition +15% starts.
 electrodeKg=math.ceil(weldM*1000*(3**2/2)*7.85e-6/.65*1.15/5)*5
 rows=[]
 def add(code,cat,name,qty,unit,price,basis,source='',status='Allowance anggaran',kg=0):
  rows.append(dict(code=code,category=cat,name=name,qty=round(qty,4),unit=unit,price=price,basis=basis,source=source,status=status,kg_per_unit=kg))
 add('M01','Material','RHS 50x100x2,3 / 6 m',len(mainbins),'btg',434500,'Rangka native165 termasuk20diagonal + kolom80 + usulan stringer tangga; pola potong gabungan FFD.','steel','Katalog / penyangga tangga usulan',32.5)
 add('M02','Material','SHS 40x40x2 / 6 m',len(crossbins)+2,'btg',194800,f'{len(crossbins)} stok pengaku tapak + 2 stok rail atas 8,425 m.','steel','Katalog',15.07)
 add('M03','Material','SHS 40x40x2,8 / 6 m',18,'btg',277000,'85 tiang railing 97,498 m + pembulatan dan sisa.','steel','Katalog',21.1)
 add('M04','Material','Bordes dek 4 mm / 1200x2400',math.ceil(82.345049121*1.1/2.88),'lbr',1273000,'82,345 m2 + allowance nesting 10%; motif belum ditimbang.','deck','Harga acuan 07.09; nesting allowance',2.88*31.4)
 add('M05','Material','Pelat tekuk tangga 3 mm / 1200x2400',len(sheets),'lbr',860000,f'56 blank; {flatA:.3f} m2; 2 tekukan 50 mm. Pola nesting tersedia.','plate','Katalog 4x8; pesan usable >=1200x2400',70)
 add('M06','Material','Pelat penutup seluruh riser dan sisi 2 mm',len(enclosure['nesting']),'lbr',578000,f"{len(enclosure['panels'])}panel; {riserA:.6f}m2; nesting kerf3mm, trim10mm; belakang/bawah terbuka.",'plate','Katalog / dimensi usulan',47)
 add('M07','Material','Pelat sambungan 6 mm',math.ceil(plate6A*1.1/2.88),'lbr',1756000,f'{nends}pasangan kupingan tangga +{main_joint_ends}pasangan rangka90x120 +{gussets}buhul200x200; cadangan10%.16ikatan beton tercakup M17.','plate','Katalog / sambungan usulan',140)
 add('M08','Material','Base plate 8 mm / stok',1,'lbr',2187000,'80 x150x150; sisa stok untuk detail seketebalan.','plate','Katalog',187)
 add('M09','Material','Papan pinus 40 mm + sandaran',round((1.197016+7.29*.04)*1.1,3),'m3',6500000,'Volume pinus Revit + panel sandaran arsip;10% sisa. Harga budget.');add('M10','Material','Karet dudukan 150x150x10',80,'bh',18000,'80 dudukan, tanpa angkur ke pelat LT4.')
 bolts=math.ceil(nends*2*1.05)
 add('M11','Material','Baut M12 kelas8.8 panjang40 / tangga',bolts,'bh',4500,f'{nends} titik x2 baut +5% cadangan; grip2pelat6mm, verifikasi panjang.','bolts')
 add('M12','Material','Mur M12 kelas8 / tangga',bolts,'bh',1500,'Satu mur per baut; sudah terpisah dari harga batang baut.','bolts');add('M13','Material','Ring datar keras M12 / tangga',bolts*2,'bh',750,'Dua ring per baut.','bolts')
 frame_bolts=math.ceil(len(live_rhs)*2*2*1.05)
 add('M14B','Material','Baut hex M12 x40 kelas 8.8 / rangka dan X',frame_bolts,'bh',4500,'165framing termasuk20diagonal;2ujung x2baut +5%cadangan. Menggantikan komponen baut paket M14; bagian yang dilas dikurangi setelah joint ditetapkan.','bolts')
 add('M14N','Material','Mur hex M12 kelas 8 / rangka dan X',frame_bolts,'bh',1500,'Satu mur per baut M14B; bukan tambahan terhadap paket M14 lama.','bolts')
 add('M14W','Material','Ring datar keras M12 / rangka dan X',frame_bolts*2,'bh',750,'Dua ring per baut M14B; paket M14 lama dihapus agar tidak dihitung ganda.','bolts')
 add('M15','Material','Sekrup drilling wood ke baja #12 x65 + ring / usulan',500,'set',1500,'Papan40mm ke RHS2,3mm;500set allowance. Tipe wood-to-steel, kapasitas bor dan panjang ulir harus sesuai katalog produsen; ukuran65mm adalah usulan pengadaan, bukan stok terkonfirmasi.','screws')
 screw_panels=[p for p in enclosure['panels'] if p['plane']!='xy' and min(p['width'],p['height'])>=30]
 screws_net=sum(2*(math.ceil(max(0,p['width']-30)/300)+math.ceil(max(0,p['height']-30)/300)) for p in screw_panels)
 add('M16','Material','Sekrup SDS hex #12 x32 + ring EPDM / usulan',math.ceil(screws_net*1.05),'set',800,f'{len(screw_panels)}panel vertikal, kisi perimeter<=300mm, inset15mm: {screws_net}titik +5%cadangan. Return dan potongan kecil dilas. Panel2mm + RHS2,3mm: minta kapasitas bor minimal4,3mm dan data pull-out. Ukuran32mm usulan, stok belum dikonfirmasi.','screws')
 add('M17','Material','Ikatan ke kolom beton / provisional sum',1,'ls',5000000,'Cadangan desain, pelat, angkur dan pemasangan16titik; jumlah/diameter/kapasitas belum dipilih. Tidak ke pelat lantai.')
 add('M18','Material','Cat alkyd 2-in-1 hitam / 2 lapis',paintL,'L',130000,f'{coatingA:.2f} m2 x2lapis /10m2/L x1,25loss, bulat2,5L. Menggantikan primer+finish terpisah.','paint','Konsumsi produsen / harga allowance')
 add('M19','Material','Thinner kompatibel + pembersih',math.ceil(paintL*.1),'L',35000,'Allowance10%volume cat; pengenceran akhir mengikuti TDS produk.','paintshop')
 add('M20','Material','Sistem antiselip permukaan tangga',math.ceil(boundA*1.1),'m2',125000,'Sistem agregat antiselip di atas pelat polos; material dan pemasangan spesialis termasuk, pola nosing kontras.')
 add('M21','Material','Clear coat kayu',math.ceil(2*((1.197016/.04)+7.29)*2/10*1.25),'L',100000,'Dua sisi bidang utama,2lapis,10m2/L,25%loss; belum mengurangi bidang tertutup.')
 add('M22','Material','Backing penutup dan hardware railing / provisional sum',1,'ls',3500000,'Cadangan material backing/tab penutup, kupingan railing dan penyambung rel yang belum terukur. Di luar SDS M16 dan sekrup kayu M15. Berat belum masuk dasar jasa; sesuaikan saat detail dirilis.')
 add('C01','Bahan habis pakai','Elektroda / kawat las kompatibel',electrodeKg,'kg',35000,f'Panjang las budget{weldM:.1f}m; kaki3mm, efisiensi0,65, starts15%, bulat5kg. WPS memilih proses.');add('C02','Bahan habis pakai','Cakram potong',math.ceil((len(maincuts)+len(cross))/15),'bh',18000,'Produktivitas budget15potong/cakram.');add('C03','Bahan habis pakai','Flap disc + sikat kawat',math.ceil(coatingA/12),'set',28000,'Satu set/12m2 permukaan, allowance persiapan.');add('C04','Bahan habis pakai','Mata bor + pelumas',math.ceil(nends*4/150),'set',150000,'150lubang/set budget, 4lubang/titik pada2pelat.');add('C05','Bahan habis pakai','Kuas, roller, masking dan kain',1,'ls',850000,'Satu paket pekerjaan coating.');add('C06','Bahan habis pakai','Listrik bengkel',500,'kWh',2000,'Allowance500kWh; termasuk las, gerinda, bor. Tarifbudget.');add('C07','Bahan habis pakai','Gas / bahan bantu pemotongan pelat',1,'ls',750000,'Biaya mesin/laser diletakkan pada upah proses, gas allowance terpisah.')
 steelKg=sum(r['qty']*r['kg_per_unit'] for r in rows)
 add('U01','Upah','Fabrikasi + pemasangan baja',steelKg,'kg',6000,'Kesepakatan Bam: berat pembelian stok termasuk sisa; upah potong, las, bor dan ereksi. Consumables terpisah.')
 add('U02','Upah','Jasa press brake',len(stairs)*2,'tekuk',20000,'112tekukan; mesin bengkel vendor, di luar tarif las/ereksi.');add('U03','Upah','Persiapan permukaan + aplikasi cat baja',coatingA,'m2',25000,'Upah coating terpisah dari tarif fabrikasi.');add('U04','Upah','Pemasangan + finishing kayu',1,'ls',3500000,'Anggaran tukang kayu; bahan clear coat sudah M21.')
 add('L01','Peralatan dan logistik','Angkut bengkel-lokasi + bongkar',2,'rit',1500000,'Bukan ongkir toko-bengkel; ukuran truk/jam akses diverifikasi.');add('L02','Peralatan dan logistik','Hoist dan alat angkat LT4',7,'hari',500000,'Allowance 7hari, kapasitas/jalur angkat ditentukan metode kerja.');add('L03','Peralatan dan logistik','Perancah dan penyangga sementara',1,'ls',2500000,'Sewa, pengiriman dan pembongkaran.');add('L04','Peralatan dan logistik','Pengukuran + kontrol mutu las/cat',1,'ls',2000000,'Allowance ukur, inspeksi visual, DFT dan dokumentasi. Tidak termasuk uji beton laboratorium.');add('L05','Peralatan dan logistik','Pembersihan, APD dan proteksi',1,'ls',1500000,'Area LT4, alat keselamatan kerja dan serah terima.');add('L06','Peralatan dan logistik','Verifikasi desain + investigasi tumpuan',1,'ls',7500000,'Provisional sum pemeriksaan insinyur dan pengumpulan data beton; lingkup lab mengikuti temuan.')
 # Explicit load scenario, not an assertion about a code-mandated point patch.
 E=200000;fy=240;P=2000;patch=100;gap=75;I=100*3**3/12;Z=100*3**2/6
 q=P/patch;stress=1.6*q*gap**2/8/Z;defl=5*q*gap**4/(384*E*I)
 beamI=(40**4-36**4)/12;beamZ=beamI/20
 analysis=dict(E_MPa=E,Fy_MPa=fy,uniform_kPa=5,point_N=P,patch_mm=patch,plate_gap_mm=gap,plate_stress_MPa=stress,plate_deflection_mm=defl,beam_span_mm=800,beam_stress_MPa=1.6*P*800/4/beamZ,beam_deflection_mm=P*800**3/(48*E*beamI),limit_MPa=.9*fy,assumption='Skenario penyaringan: beban titik2kN pada100x100mm atau merata5kPa, bukan klaim kategori/pasalSNI telah dipenuhi.',scope='Lentur elastis lokal saja. Tekuk lokal, torsi, sambungan, stabilitas global, getaran dan beton belum selesai diperiksa.')
 net_flat=sum(r['net_flat_area'] for r in stairs)
 data=dict(revision='R04',date=DATE,stairs=stairs,stair_geometry=extra,enclosure=enclosure,flat_area=flatA,net_flat_area=net_flat,bounds_area=boundA,audited_area=oldA,old_flat_4mm_kg=oldA*31.4,new_bent_3mm_kg=net_flat*23.55,bend_deduction=bd,nesting=sheets,main_stock=mainbins,cross_stock=crossbins,main_length=mainL,cross_length=crossL,coating_area=coatingA,steel_purchase_kg=steelKg,rows=rows,analysis=analysis,sources=SOURCES,defaults=dict(overhead=7,profit=8,tax=0,service=True),notes=['Harga katalog merupakan harga tayang, bukan penawaran pemasok. Semua harga lain berlabel allowance dan dapat diedit.','Basis pajak: harga beli mengikuti tayangan pemasok (bruto bila termasuk PPN); pajak keluaran penawaran default0 sampai status kontrak ditetapkan.','Nesting memakai bounding blank; berat bersih memakai polygon takikan arsipIFC dan allowance tekukan. Cocokkan dengan model aktif sebelum produksi.','Revit R04: pelat3mm tersimpan,165RHS termasuk20diagonal terverifikasi. Penyangga tangga dan sambungan masih usulan, belum dihitung sebagai geometri native. Berat katalog pelat4x8 dipisahkan dari luas potong1200x2400; berat aktual mengikuti timbang pemasok.'])
 net_mass={'M01':mainL*32.5/6,'M02':(crossL+8.4254)*15.07/6,'M03':97.498388*21.1/6,'M04':82.345049121*31.4,'M05':net_flat*23.55,'M06':enclosure['net_kg'],'M07':plate6A*47.1,'M08':plate8A*62.8}
 data['mass_ledger']=[dict(code=r['code'],name=r['name'],net_kg=net_mass[r['code']],purchase_kg=r['qty']*r['kg_per_unit'],stock_qty=r['qty'],unit=r['unit'],basis='Berat bersih teoritis; pembelian katalog/nominal. Motif bordes belum termasuk.' if r['code']=='M04' else 'Berat bersih dari dimensi; pembelian dari massa katalog stok. Penyangga/sambungan usulan termasuk sesuai basis item.') for r in rows if r['code'] in net_mass]
 data['fastener_basis']=dict(cover_vertical_panels=len(screw_panels),cover_screws_net=screws_net,cover_screws_purchase=math.ceil(screws_net*1.05),frame_members=len(live_rhs),frame_bolts_net=len(live_rhs)*4,stair_joint_points=nends,stair_bolts_net=nends*2)
 for r in rows:
  if r['source'] in ['bolts','screws']:
   r['supplier']='Sentral Mur Baut Surabaya' if r['source']=='bolts' else 'PT Jaya Metal Surabaya'
   r['supplier_contact']='031 3535022' if r['source']=='bolts' else '0812-3033-1188 / Jl. Margomulyo 66F Kav.2 Surabaya'
   r['price_basis']='Estimasi anggaran per '+r['unit']+'; bukan harga penawaran pemasok. Ditinjau 09.09.2026.'
   r['specification']='Baja karbon; lapis seng untuk pengadaan indoor. Baut kelas8.8, mur kelas8 dan ring keras kompatibel; panjang/grip, sertifikat dan detail joint harus dicocokkan.' if r['source']=='bolts' else 'Baja karbon dikeraskan, lapis antikarat; mutu dan kapasitas mengikuti datasheet SDS produsen. Bukan pengganti baut struktural. Jenis produk pemasok tersedia; ukuran dan kapasitas pilihan belum terverifikasi.'
   r['status']='Usulan spesifikasi / harga estimasi'
 data['native_counts']=dict(rhs=165,columns=80,diagonals=20,x_sets=10,stair_fields=56,stair_parts=176,cover_parts=len(enclosure['panels']))
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 with (OUT/'berat-R04.csv').open('w',newline='',encoding='utf-8-sig') as out:
  wr=csv.writer(out);wr.writerow(['Kode','Material','Berat_bersih_teoritis_kg','Berat_pembelian_katalog_kg','Stok','Satuan','Basis'])
  for r in data['mass_ledger']:wr.writerow([r['code'],r['name'],round(r['net_kg'],6),round(r['purchase_kg'],6),r['stock_qty'],r['unit'],r['basis']])
 with (OUT/'rab-R04.csv').open('w',newline='',encoding='utf-8-sig') as out:
  wr=csv.writer(out);wr.writerow(['Kode','Kategori','Uraian','Volume','Satuan','Harga','Jumlah','Basis','Status','Sumber','Pemasok','Spesifikasi','Dasar harga'])
  for r in rows:wr.writerow([r['code'],r['category'],r['name'],r['qty'],r['unit'],r['price'],round(r['qty']*r['price']),r['basis'],r['status'],SOURCES.get(r['source'],['',''])[1],r.get('supplier',''),r.get('specification',''),r.get('price_basis','')])
 with (OUT/'potong-R04.csv').open('w',newline='',encoding='utf-8-sig') as out:
  wr=csv.writer(out);wr.writerow(['Profil','Stok','ID','Panjang_mm','Kerf_mm'])
  for profile,bins in [('RHS50x100',mainbins),('SHS40x40',crossbins)]:
   for i,b in enumerate(bins):
    for label,L in b['cuts']:wr.writerow([profile,i+1,label,round(L,3),3])
 return data

if __name__=='__main__':
 d=build_data();print(json.dumps({k:d[k] for k in ['flat_area','bounds_area','audited_area','old_flat_4mm_kg','new_bent_3mm_kg','steel_purchase_kg','coating_area','analysis']}))
