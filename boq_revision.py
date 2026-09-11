"""Model-derived quantities mapped to Bam's 11 September price schedule."""
import json, math, hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from r04_model import load_model
from study_r05 import rhs

ROOT=Path(__file__).parent
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))

def build_data():
    m=load_model();live=read('data/revit-2026-09-11-audit.json');old=read('assets/r04/data.json')
    study=read('data/r05-study.json');source=read('data/boq-2026-09-11-source.json');plate=read('assets/r05/pola-pelat6mm.json')
    byid={e['id']:e for e in live['members']};shape={e['id']:e for e in m['items']}
    s={r['id']:r for r in source['rows']};ro={r['code']:r for r in old['rows']}
    classify={};lengths=defaultdict(float);ids=defaultdict(list)
    for e in live['members']:
        ident=e['id'];name=e['name'];p=e['props']
        if 'KOLOM' in name:key='X01'
        elif 'BALOK SILANG' in name:key='B01'
        elif 'BRACING X' in name:key='X06'
        elif 'RHS' in name:
            g=shape[ident];center=np.mean(g['vertices'],axis=0)
            if g['group']=='stiffener':key='X03'
            elif center[1]>4900:key='X04'
            elif p['Cut Length']*.3048<.5:key='X05'
            else:key='X02'
        elif 'TIANG RAILING' in name:key='X08'
        elif 'RAILING' in name:key='X07'
        else:continue
        L=p.get('Cut Length',p.get('System Length',0))*.3048
        classify[str(ident)]=key;lengths[key]+=L;ids[key].append(ident)
    # Reconcile every native RHS and column ID, not just category counts.
    expected={e['id'] for e in m['rhs']}|{e['id'] for e in m['columns']}
    assert expected=={int(i) for i,k in classify.items() if k not in ['X07','X08']}
    for label,L in [c for b in old['main_stock'] for c in b['cuts']]:
        if str(label) not in classify:classify[str(label)]='B02';lengths['B02']+=L/1000
    def allocation(stocks,kg):
        out=defaultdict(float)
        for b in stocks:
            total=sum(L for label,L in b['cuts'])
            for label,L in b['cuts']:out[classify[str(label)]]+=kg*L/total
        assert abs(sum(out.values())-len(stocks)*kg)<1e-7
        return out
    baseline=allocation(old['main_stock'],32.5)
    variants=study['procurement']['variants']
    variant_allocations={key:allocation(old['main_stock'],v['stock_kg']) for key,v in variants.items()}
    cover=read('data/r04-cover-parts.json')
    # Split the shared sheet purchasing weight by net area, never buy the same sheet twice.
    side=sum(x['area_m2'] for x in cover if x['code'].startswith('C2-S') and not x['code'].startswith('C2-ST'))
    cover_total=sum(x['area_m2'] for x in cover);front=cover_total-side
    floor_rows=[e for e in live['members'] if e['category']=='Floors']
    wood_volume=sum(e['props']['Volume'] for e in floor_rows if 'PINUS' in e['name'])*.3048**3
    deck_area=sum(e['props']['Area'] for e in floor_rows if 'BORDES' in e['name'])*.3048**2
    rows=[]
    def add(key,name,mat,net,buy,unit,lr,mr,basis,status='Model + pembelian',extra=False,rev=None):
        origin=s.get(key)
        r=dict(id=key,name=name,material=mat,unit=unit,net_qty=float(net),purchase_qty=float(buy),
          labor_rate=float(lr),material_rate=float(mr),basis=basis,status=status,extra=extra,
          revit_ids=ids.get(key,[]),source_row=origin['excel_row'] if origin else None)
        if rev:r['revised']=rev
        rows.append(r)
    for key,name in [('X01','Kolom tribun'),('X02','Balok tepi tier'),('X03','Pengaku longitudinal dek'),
                     ('X04','Rangka belakang'),('X05','Strut ke kolom beton'),('X06','Bracing X'),
                     ('B01','Balok silang penumpu dek'),('B02','Penyangga tangga / usulan')]:
        src=s.get(key,s['X03']);net=lengths[key]*rhs(2.3)['kg_m']
        basis=f"{len(ids[key]) if key!='B02' else 116} elemen; panjang {lengths[key]:.6f} m. Berat pembelian dialokasikan dari stok bersama menurut panjang potongan pada setiap batang."
        if key=='B02':basis+=' Penyangga belum menjadi elemen native dan jalur tumpuannya belum final.'
        if key=='X05':basis+=' Angkur dan pelat ikatan beton dihitung pada item tersendiri.'
        add(key,name,'Hollow 50×100×2,3 mm',net,baseline[key],'kg',src['labor_rate'],s['X01']['material_rate'],basis,
            'Usulan belum dimodelkan' if key=='B02' else 'Panjang Revit; berat dari penampang/katalog')
        rows[-1]['variants']={case:dict(purchase_qty=variant_allocations[case][key],net_qty=lengths[key]*rhs(v['thickness_mm'])['kg_m'],
            material=f"Hollow 50×100×{str(v['thickness_mm']).replace('.',',')} mm / studi seluruh 50×100",material_rate=v['price_kg'],
            basis=basis+' '+v['price_basis']) for case,v in variants.items() if case!='model'}
    add('X07','Rail atas / elemen horizontal','SHS 40×40×2 mm',lengths['X07']*rhs(2,40,40)['kg_m'],2*15.07,'kg',6000,s['X07']['material_rate'],
        f"10 elemen; {lengths['X07']:.6f} m; 2 stok ×6m. Family aktif masih M_W Shapes; volume family tidak dipakai sebagai berat hollow.")
    add('X08','Tiang railing dan pegangan','SHS 40×40×2,8 mm',lengths['X08']*rhs(2.8,40,40)['kg_m'],18*21.1,'kg',6000,277000/21.1,
        f"85 elemen; {lengths['X08']:.6f} m; 18 stok. Harga 2,8mm mengikuti katalog R04 karena spesifikasi Excel 2mm berbeda.")
    add('X09','Pelat dek','Bordes 4 mm',deck_area*31.4,32*2.88*31.4,'kg',s['X09']['labor_rate'],s['X09']['material_rate'],
        f"Area30floor={deck_area:.9f}m²; pembelian32lembar1200×2400, allowance10%. Berat motif bordes belum terukur.")
    add('X10','Riser, fascia dan return','Pelat polos 2 mm',front*15.7,1222*front/cover_total,'kg',6000,s['X10']['material_rate'],
        f"Luas{front:.6f}m². Alokasi proporsional dari26lembar bersama penutup sisi; bukan tambahan terhadap26lembar.")
    add('X11','Pelat tekuk tangga','Pelat polos 3 mm',old['new_bent_3mm_kg'],560,'kg',6000,s['X11']['material_rate'],
        '56bidang/176bagian native;8lembar. Penyangga RHS dan pengaku SHS dipisah agar tidak terhitung dua kali.')
    add('B03','Pengaku tapak tangga / usulan','SHS 40×40×2 mm',old['cross_length']*rhs(2,40,40)['kg_m'],27*15.07,'kg',6000,s['X07']['material_rate'],
        f"{old['cross_length']:.6f}m dari usulan pengaku tapak;27stok. Belum menjadi rangka native.",'Usulan belum dimodelkan')
    # Same cutting allowances as the reference: 2 + 18 + 27 stocks. No
    # additional saving is claimed from pooling the three fabrication batches.
    shs_specs={'s16':(1.6,12.053333333333333,153433.33333333334),
               's17':(1.7,12.806666666666667,163366.66666666666),
               's20':(2.,15.07,194800), 's23':(2.3,17.33,229100)}
    for r in rows:
        if r['id'] not in ['X07','X08','B03']:continue
        key=r['id'];L=old['cross_length'] if key=='B03' else lengths[key]
        count={'X07':2,'X08':18,'B03':27}[key]
        r['shs_variants']={}
        for case,(thickness,mass,price) in shs_specs.items():
            price_basis=('Berat dan harga interpolasi katalog 1,5–1,8 mm; estimasi, bukan penawaran.'
                         if case in ['s16','s17'] else 'Berat dan harga katalog SMS Perkasa.')
            r['shs_variants'][case]=dict(material=f"SHS 40×40×{thickness:.1f} mm / studi".replace('.',','),
                net_qty=L*rhs(thickness,40,40)['kg_m'],purchase_qty=count*mass,
                material_rate=price/mass,stock_kg=mass,
                basis=f"{L:.6f} m; {count} stok ×6m. "+price_basis+
                    ' Katalog 27 Agustus 2026, diperiksa 11 September 2026: https://www.smsperkasa.com/produk/besi-hollow-hitam. '
                    'Total tiga kelompok 47 stok; sisa antar kelompok belum dioptimalkan. Berat bersih penampang membulat R=2t/r=t. '+
                    ('Usulan belum menjadi elemen native.' if key=='B03' else 'Panjang dari audit Revit.'),
                status='Studi SHS seluruh 40×40; belum untuk fabrikasi')
    add('X12','Penutup kedua sisi','Pelat polos 2 mm',side*15.7,1222*side/cover_total,'kg',6000,s['X12']['material_rate'],
        f"Luas{side:.6f}m²; bagian dari total26lembar penutup. Belakang dan bawah terbuka.")
    add('X13','Base plate','Pelat 150×150×8 mm',80*.15*.15*.008*7850,187,'kg',6000,s['X13']['material_rate'],
        '80dudukan; satu stok pelat8mm. Berat pembelian187kg; sisa stok termasuk sekali.')
    add('X14','Pelat sambungan rangka, tangga dan buhul','Pelat 6 mm; lembar 120×240 cm',plate['net_kg'],plate['purchase_kg'],'kg',5000,s['X14']['material_rate'],
        '5 lembar 1200×2400×6 mm = 678,24 kg teoritis. Potongan tetap: 232 pasangan kupingan tangga + 274 pasangan rangka 90×120 mm + 40 buhul 200×200 mm. Pola potong 1052 bagian, tepi 10 mm dan celah potong 3 mm sudah diperiksa. Tarif/kg dari Excel.','Usulan sambungan / pola stok diperiksa')
    # Existing three rows describe frame hardware only. Stair hardware has its own rows.
    for key,code,net,name in [('X15','M14B',660,'Baut rangka dan X'),('X17','M14N',660,'Mur rangka dan X'),('X18','M14W',1320,'Ring rangka dan X'),
                              ('B04','M11',464,'Baut tangga'),('B05','M12',464,'Mur tangga'),('B06','M13',928,'Ring tangga')]:
        r=ro[code];price_source=s.get(key,s[{'B04':'X15','B05':'X17','B06':'X18'}.get(key,key)])
        spec='M12×40 kelas8.8' if code in ['M14B','M11'] else 'M12 kelas8' if code in ['M14N','M12'] else 'Ring datar keras M12'
        add(key,name,spec,net,r['qty'],'bh',price_source['labor_rate'],price_source['material_rate'],r['basis']+' Baut, mur dan ring adalah komponen terpisah.','Usulan sambungan')
    add('X16','Ikatan ke kolom beton / cadangan','Angkur dan pelat: belum ditetapkan',1,1,'ls',0,5000000,
        'Mengganti hitungan32dynaboltM10 yang belum terverifikasi. Anggaran R04 untuk16titik termasuk desain, pelat, angkur dan pemasangan; bukan jumlah angkur final.','Cadangan biaya')
    add('X19','Sekrup kayu ke baja + ring','#12×65 / usulan',500,500,'set',300,1500,ro['M15']['basis'],'Allowance jumlah')
    add('X20','Sekrup penutup + ring EPDM','#12×32 / usulan',2332,2449,'set',300,800,ro['M16']['basis'],'Usulan pola sekrup')
    add('X21','Karet dudukan','150×150×10 mm',80,80,'bh',500,25000,'80dudukan aktif; satu karet per base plate.')
    add('X22','Papan pinus dudukan','Lebar400mm; tebal40mm',wood_volume/.016,wood_volume/.016*1.1,'m',25000,90000,
        f"Volume15floor={wood_volume:.9f}m³ ÷(0,4×0,04); pembelian+10%. Bukan200m tanpa dasar geometri.")
    add('X23','Panel kayu sandaran','Lebar400mm; tebal40mm',7.29/.4,7.29/.4*1.1,'m',25000,90000,
        'Luas7,29m² dari geometri arsip, bukan hasil ukur Revit baru. Pembelian+10%. Koreksi label400×40cm menjadi lebar400mm/tebal40mm.','Geometri arsip / allowance')
    coat=old['coating_area'];src=s['X24']
    add('X24','Cat dan coating baja','Persiapan + cat; luas permukaan',coat,coat,'m²',src['qty']*src['labor_rate']/coat,src['qty']*src['material_rate']/coat,
        f"Estimasi permukaan{coat:.4f}m²; nilai paket cat Excel Rp{src['qty']*(src['labor_rate']+src['material_rate']):,.0f} dibagi luas. Penipisan hollow tidak mengurangi luas cat. Tarif ini normalisasi paket Excel, bukan harga/m² pemasok.",'Estimasi luas / tarif paket')
    extras=[('E01','Backing penutup dan hardware railing','M22'),('E02','Sistem antiselip tangga','M20'),('E03','Clear coat kayu','M21'),('E04','Jasa tekuk pelat','U02')]
    for key,name,code in extras:
        r=ro[code];add(key,name,r['name'],r['qty'],r['qty'],r['unit'],r['price'] if code.startswith('U') else 0,r['price'] if not code.startswith('U') else 0,r['basis'],r['status'],extra=True)
    for code in ['L01','L02','L03','L04','L05','L06']:
        r=ro[code];add('E'+code,r['name'],'Biaya pelengkap proyek',r['qty'],r['qty'],r['unit'],r['price'],0,r['basis'],r['status'],extra=True)
    # Each profile's stock is allocated exactly once; steel mass before plate rows reconciles.
    stock_mass=sum(r['purchase_qty'] for r in rows if r['unit']=='kg')
    expected_mass=old['steel_purchase_kg']-700+plate['purchase_kg']
    assert abs(stock_mass-expected_mass)<1e-6,(stock_mass,expected_mass)
    comparison=[]
    for case in ['model','h20','h16']:
        for mode in ['net','purchase']:
            for extra in [False,True]:
                totals=dict(material=0.,labor=0.)
                for r in rows:
                    if r['extra'] and not extra:continue
                    rr={**r,**r.get('variants',{}).get(case,{})};q=rr[mode+'_qty']
                    totals['material']+=round(q*rr['material_rate']);totals['labor']+=round(q*rr['labor_rate'])
                totals['total']=totals['material']+totals['labor'];comparison.append(dict(case=case,basis=mode,extras=extra,**totals))
    source_rows=[dict(id=r['id'],name=r['name'],material=r['material'],net_qty=r['qty'],purchase_qty=r['qty'],unit=r['unit'],labor_rate=r['labor_rate'],material_rate=r['material_rate'],basis=f"Excel sumber Sheet1 baris{r['excel_row']}; volume asli. Total dihitung ulang mencakup24baris.",status='Excel sumber',extra=False,source_row=r['excel_row'],revit_ids=[]) for r in source['rows']]
    import re
    for r in rows:
        r['basis']=re.sub(r'(?<=\d)(?=[A-Za-z])|(?<=[a-z])(?=\d)',' ',r['basis'])
    result=dict(date='2026-09-11',default_case='model',default_basis='purchase',rows=rows,source_rows=source_rows,
        study=study,comparison=comparison,source_totals=source['computed_totals'],stock_audit=read('assets/r05/audit-batang.json'),plate_stock={k:v for k,v in plate.items() if k!='sheets'},
        facts=dict(rhs=165,columns=80,rail=95,deck_area_m2=deck_area,wood_m3=wood_volume,steel_purchase_kg=stock_mass),
        notes=['Tarif upah dan material mengikuti Excel11September kecuali spesifikasi berubah atau item tidak tersedia; pengecualian tertulis pada dasar hitungan.',
               'Pembelian termasuk sisa potong; terpasang adalah berat bersih estimasi. Angka volume dan tarif bisa diedit per versi.',
               'Cadangan sambungan, pengaku tangga dan backing belum menjadi seluruhnya elemen Revit. Biaya pelengkap dapat diaktifkan terpisah.',
               'Alat kerja dan kawat las dari P.Asmadi; listrik lokasi dari METTA mengikuti catatan sumber. Tidak ditagihkan lagi pada baris pelengkap.',
               'Nilai sebelum overhead, laba dan pajak tambahan. Harga/kg dari Excel tidak membuktikan harga pemasok terkini.',
               'Versi1,6/2,0mm mengganti seluruh hollow50×100 pada perbandingan biaya; susunan dan panjang potong tetap. Revit masih2,3mm.',
               'Versi1,6mm seluruh rangka tidak lolos kasus penyaringan balok silang pada tebal asumsi1,488mm. Semua versi belum menjadi desain pelaksanaan; perlu sertifikat baja, analisis rangka, sambungan dan betonLT4.',
               'Pelat sambungan6mm dibeli5lembar120×240cm; berat678,24kg dihitung dari dimensi. Buhul200×200mm adalah ukuran potongan, bukan ukuran lembar.'])
    out=ROOT/'assets/r05';out.mkdir(exist_ok=True)
    def spaced(value):
        return re.sub(r'(?<=\d)(?=[A-Za-z])|(?<=[a-z])(?=\d)', ' ', value)
    for r in rows+source_rows:
        for k in ['material','basis','status']:
            r[k]=spaced(r[k])
    result['notes']=[spaced(n) for n in result['notes']]
    (out/'boq.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(rows=len(rows),comparison=comparison),indent=2));return result

if __name__=='__main__':build_data()
