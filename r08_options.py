"""A/C coordination BOQs from explicit structural member and anchorage schedules.

The structural specification is a study, not a released connection design.
All RHS pieces are re-packed together; reference and thickness variants share cuts.
"""
import copy, csv, json, math
from pathlib import Path
from r08 import measure_stock
from r04_nesting import pack
from r04_model import box

ROOT=Path(__file__).parent
OUT=ROOT/'assets/r08'
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def write(path,data): (OUT/path).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

def build():
    specification=read('assets/structural-study/options-spec.json')
    baseline=read('assets/r08/data.json'); audit0=read('assets/r08/audit.json'); geometry0=read('assets/r08/geometry.json')
    original=read('assets/r05/boq.json'); variants=original['study']['procurement']['variants']
    source=next(r for r in original['rows'] if r['id']=='X01')
    options={}
    for key in ['a','c']:
        spec=specification[key];d=copy.deepcopy(baseline);audit=copy.deepcopy(audit0);g=copy.deepcopy(geometry0)
        d['structure']=key;d['structure_label']=spec['label'];d['structural_assumptions']=spec.get('notes',[])
        removed={str(i) for i in spec.get('remove_ids',[])}
        cuts=[c for c in audit['cuts']['rhs'] if str(c['id']) not in removed]
        members=spec.get('added_members',[])
        owner={'kolom':'I01','balok':'I02','stiffener':'I03','bracing':'X06'}
        for m in members:
            cuts.append(dict(id=m['id'],owner=owner[m['group']],length_mm=m['length_mm'],origin=f'R08 {key.upper()} structural proposal'))
        rhs=measure_stock(cuts);d['rhs']=rhs;audit['cuts']['rhs']=cuts
        rows={r['id']:r for r in d['rows']}
        for ident in set(baseline['rhs']['lengths_m'])|set(rhs['lengths_m']):
            L=rhs['lengths_m'].get(ident,0.)
            r=rows[ident]
            r['revit_ids']=[i for i in r.get('revit_ids',[]) if str(i) not in removed]
            for case in ['model','h20','h16']:
                stockkg=variants[case]['stock_kg'];kg_m=(source['net_qty'] if case=='model' else source['variants'][case]['net_qty'])/133.5598
                dest=r if case=='model' else r['variants'][case]
                dest.update(net_qty=L*kg_m,purchase_qty=rhs['allocated_bars'].get(ident,0.)*stockkg,basis=f'R08 {key.upper()}: {L:.6f} m; alokasi dari {rhs["stock_count"]} stok bersama × {stockkg} kg/batang. Minimum belum terbukti.')
        if any(m['group']=='kolom' for m in members): rows['I01']['name']='Kolom tambahan infill dan penguatan'
        def qty(ident,net,buy,basis): rows[ident].update(net_qty=net,purchase_qty=buy,basis=f'R08 {key.upper()}: '+basis)
        # Remove the unmeasured RC lump sum; use the explicit proposal schedule.
        qty('X16',0,0,'Cadangan ikatan RC lama diganti daftar usulan A/C di bawah; kapasitas belum disahkan.')
        def add(ident,name,material,unit,net,buy,labor,rate,basis):
            r=dict(id=ident,name=name,material=material,unit=unit,net_qty=net,purchase_qty=buy,labor_rate=labor,material_rate=rate,basis=f'R08 {key.upper()}: '+basis,status='Allowance studi; bukan desain fabrikasi',extra=False)
            d['rows'].append(r);rows[ident]=r
        anchors=int(spec.get('anchor_count',0))
        if anchors:
            add('S01','Angkur tambahan struktur / tangga','M12 / allowance; produk dan kapasitas belum ditetapkan','set',anchors,math.ceil(anchors*1.05),15000,35000,'Jumlah dari jadwal titik usulan; cadangan 5%. Tarif material Rp35.000 + upah Rp15.000/set. Beton, jarak tepi, kedalaman dan produk harus diperiksa.')
        posts=[m for m in members if m['group']=='kolom']
        if posts:
            rows['I04']['name']='Base plate kolom tambahan infill dan tangga'
            rows['I05']['name']='Angkur lantai kolom tambahan infill dan tangga'
            rows['I06']['name']='Karet dudukan kolom tambahan infill dan tangga'
        baseplates=[(f'BASE{i}',150,150) for i in range(80)]+[(f'IB{i}',140,150) for i in range(20+len(posts))]
        base_sheets=pack(baseplates);audit['nesting']['infill_base8']=base_sheets
        area_old=80*.15*.15;area_new=(20+len(posts))*.14*.15;buy=len(base_sheets)*180.864
        qty('X13',area_old*62.8,buy*area_old/(area_old+area_new),'Base lama dan tambahan dinesting bersama; alokasi kg pembelian menurut luas.')
        qty('I04',area_new*62.8,buy*area_new/(area_old+area_new),f'{20+len(posts)} base usulan 140×150×8 mm; dimensi/kapasitas belum disahkan.')
        qty('I05',4*(20+len(posts)),math.ceil(4*(20+len(posts))*1.05),'4 angkur lantai per base usulan + cadangan 5%; tumpuan lantai belum diverifikasi.')
        qty('I06',20+len(posts),20+len(posts),'Karet 140×150×3 mm per base baru.')
        welded=[m for m in members if m.get('connection')=='welded' or (m['group']!='kolom' and m['length_mm']<200)]
        welded_ids={m['id'] for m in welded}
        extra_ends=2*sum(m['group']!='kolom' and m['id'] not in welded_ids for m in members)
        removed_ends=2*len(removed)
        welded_stair_ends=int(spec.get('welded_existing_stair_ends',0))
        anchor_plates=int(spec.get('anchor_plate_count',0))
        # Recover the existing coupon register, then remove obsolete tie coupons.
        old_coupons=[(p['id'],p['w'],p['h']) for sheet in audit0['nesting']['plate6'] for p in sheet]
        joints=[p for p in old_coupons if p[0].startswith('J')]
        gussets=[p for p in old_coupons if not p[0].startswith('J')]
        count=max(0,len(joints)-2*removed_ends-2*welded_stair_ends)+2*extra_ends+anchor_plates
        coupons=[(f'J{i}',90,120) for i in range(count)]+gussets
        sheets=pack(coupons);audit['nesting']['plate6']=sheets
        qty('X14',count*.09*.12*47.1+sum(w*h for _,w,h in gussets)/1e6*47.1,len(sheets)*135.648,'Pelat ujung 90×120×6 mm dan buhul dinesting ulang. Ukuran allowance; tebal/las/baut dan penyaluran gaya belum disahkan.')
        bolts=max(0,rows['X15']['net_qty']+2*extra_ends-2*removed_ends)
        for ident,factor in [('X15',1),('X17',1),('X18',2)]:qty(ident,bolts*factor,math.ceil(bolts*1.05)*factor,'2 baut per ujung tambahan; ujung batang yang dihapus dikurangi; 5% cadangan, 2 ring per baut beli.')
        stair_bolts=max(0,rows['B04']['net_qty']-2*welded_stair_ends)
        for ident,factor in [('B04',1),('B05',1),('B06',2)]:qty(ident,stair_bolts*factor,math.ceil(stair_bolts*1.05)*factor,'Ujung penyangga yang diganti sambungan las dikurangi dari baut; 5% cadangan, dua ring per baut beli.')
        if welded:
            weld_length=.6*len(welded)
            add('S02','Bahan habis pakai sambungan las tambahan','Allowance bahan las; detail prosedur dan ukuran las belum disahkan','m',weld_length,weld_length,0,10000,f'{len(welded)} penghubung pendek × dua keliling profil 0,30 m. Cadangan material Rp10.000/m; upah telah termasuk tarif RHS per kg. Ini panjang jalur nominal untuk biaya, bukan ukuran atau kapasitas las.')
        delta_length=rhs['length_m']-baseline['rhs']['length_m']
        delta_plate=(rows['X14']['net_qty']-next(r for r in baseline['rows'] if r['id']=='X14')['net_qty'])/47.1
        coat_delta=1.1*(delta_length*.3+2*(delta_plate+len(posts)*.14*.15))
        qty('X24',rows['X24']['net_qty']+coat_delta,rows['X24']['purchase_qty']+coat_delta,'Luas cat disesuaikan potongan RHS dan pelat baru/dihapus; kedua muka pelat +10%.')
        g['retained_native_ids']=[i for i in g['retained_native_ids'] if str(i) not in removed]
        g['added_native_items']=[dict(id=m['id'],group=m['group'],vertices=m['vertices']) for m in members]
        for post in posts:
            v=post['vertices'];x=sum(p[0] for p in v)/8;y=sum(p[1] for p in v)/8
            g['added_native_items'].append(dict(id=post['id']+'-BP',group='baseplate',vertices=box([x-70,y-75,3,x+70,y+75,11])))
            g['added_native_items'].append(dict(id=post['id']+'-PAD',group='baseplate',vertices=box([x-70,y-75,0,x+70,y+75,3])))
        g['structural_anchors']=spec.get('anchor_groups',[]);g['structure']=key
        d['changes']['removed_native_rhs_ids']+=list(spec.get('remove_ids',[]))
        d['changes']['infill_new_posts']=20;d['changes']['structural_posts']=len(posts);d['changes']['new_posts']=20+len(posts)
        d['changes']['structural_added_members']=len(members)
        d['notes']=[f'Opsi {spec["label"]}.']+spec.get('notes',[])+d['notes']
        write(f'geometry-{key}.json',g);write(f'audit-{key}.json',audit)
        with (OUT/f'daftar-potong-{key}.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f);w.writerow(['profil','stok','id','komponen','panjang_mm','status'])
            for label,summary,cs in [('RHS50x100',rhs,cuts),('SHS40x40-tangga-mesh',{**d['shs'],'stocks':audit['shs_stocks']},audit['cuts']['shs']),('strip30x3',{**d['clamps'],'stocks':audit['clamp_stocks']},audit['cuts']['clamps'])]:
                lookup={str(c['id']):c for c in cs}
                for i,b in enumerate(summary['stocks']):
                    for ident,L in b['cuts']:w.writerow([label,i+1,ident,lookup[str(ident)]['owner'],round(L,4),'studi - belum fabrikasi'])
        options[key]=d
    write('options.json',options)
    return options

if __name__=='__main__':
    for k,d in build().items():print(k,d['rhs']['stock_count'],'RHS',d['changes']['new_posts'],'new posts')
