"""Quantity decisions based on a new read-only Revit readback and explicit stock units."""
import csv,json,math
from pathlib import Path
from revision04 import pack_bars
from study_r05 import rhs
ROOT=Path(__file__).parent
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def close(a,b,tol=1e-5):assert abs(a-b)<=tol,(a,b)

def audit(d):
    live=read('data/quantity-reaudit-live.json')['members'];byid={e['id']:e for e in live}
    old={e['id']:e for e in read('data/revit-2026-09-11-audit.json')['members']}
    rows={r['id']:r for r in d['rows']};source={r['id']:r for r in d['source_rows']}
    assert len(byid)==len(live)==545
    checks=0
    for e in live:
        if e['id'] not in old:continue
        assert e['name']==old[e['id']]['name']
        for k in ['Cut Length','System Length','Area','Volume']:
            if k in e['props'] and k in old[e['id']]['props']:
                close(e['props'][k],old[e['id']]['props'][k]);checks+=1
    batches={};native_cuts=[]
    for key in ['X01','X02','X03','X04','X05','X06','B01','X07','X08']:
        r=rows[key];members=[byid[i] for i in r['revit_ids']]
        cuts=[(str(e['id']),e['props'].get('Cut Length',e['props'].get('System Length'))*304.8) for e in members]
        L=sum(c[1] for c in cuts)/1000
        t=2 if key=='X07' else 2.8 if key=='X08' else 2.3
        close(r['net_qty'],L*rhs(t,40 if key in ['X07','X08'] else 50,40 if key in ['X07','X08'] else 100)['kg_m'])
        if key in ['X07','X08']:
            stocks=pack_bars(cuts);mass=15.07 if key=='X07' else 21.1
            assert all(s['used']<=6000 for s in stocks)
            close(r['purchase_qty'],len(stocks)*mass)
            batches[key]=dict(cuts=len(cuts),length_m=L,stocks=len(stocks),kg_per_stock=mass,stocks_plan=stocks)
        else:native_cuts+=cuts
        r['verification']='Panjang model dibaca ulang; kg bersih penampang, kg beli katalog'
    assert len(native_cuts)==len({i for i,L in native_cuts})==245
    native_stocks=pack_bars(native_cuts)
    base=read('assets/r04/data.json');allcuts=[c for s in base['main_stock'] for c in s['cuts']]
    expected_native={i:L for i,L in native_cuts}
    for i,L in allcuts:
        if str(i) in expected_native:close(L,expected_native[str(i)],.001)
    assert len(allcuts)==361 and len(base['main_stock'])==101
    for s in base['main_stock']:assert sum(L+3 for i,L in s['cuts'])<=6000
    crosscuts=[c for s in base['cross_stock'] for c in s['cuts']]
    assert len(pack_bars(crosscuts))==27
    close(sum(L for i,L in crosscuts)/1000,base['cross_length'])
    close(rows['B03']['purchase_qty'],27*15.07)
    floors=lambda name:[e for e in live if name in e['name'] and e['category']=='Floors']
    deck=floors('BORDES');wood=floors('PINUS');plates=floors('BASE PLATE');rubber=floors('KARET')
    assert [len(deck),len(wood),len(plates),len(rubber)]==[30,15,80,80]
    area=sum(e['props']['Area'] for e in deck)*.3048**2
    close(rows['X09']['net_qty'],area*.004*7850)
    close(rows['X09']['purchase_qty'],math.ceil(area*1.1/2.88)*2.88*.004*7850)
    close(rows['X22']['net_qty'],sum(e['props']['Volume'] for e in wood)*.3048**3/.016)
    close(rows['X13']['net_qty'],sum(e['props']['Area'] for e in plates)*.3048**2*.008*7850,.05)
    assert rows['X21']['purchase_qty']==len(rubber)
    # Exact 1200 x 2400 mm, replacing catalogue weights for larger 4 x 8 ft plates.
    plate_specs=[(['X10','X12'],26,2,1222),(['X11'],8,3,560),(['X13'],1,8,187),(['X14'],5,6,678.24)]
    corrections=[]
    for keys,count,t,previous in plate_specs:
        kg=count*1.2*2.4*t/1000*7850
        close(sum(rows[k]['purchase_qty'] for k in keys),kg)
        corrections.append(dict(ids=keys,sheets=count,thickness_mm=t,previous_kg=previous,corrected_kg=kg,difference_kg=kg-previous))
        for k in keys:
            note=f' Stok tepat 1200×2400 mm, t={t} mm; {count} lembar bersama = {kg:.3f} kg teoritis (7850 kg/m³). Bukan berat timbang; bukan lembar 4×8 kaki.'
            if note not in rows[k]['basis']:rows[k]['basis']+=note
    # Count checks confirm budgets, not connection adequacy or a fabrication release.
    for k,n in [('X15',660),('X17',660),('X18',1320),('B04',464),('B05',464),('B06',928)]:
        assert rows[k]['net_qty']==n
        expected=math.ceil((660 if k.startswith('X') else 464)*1.05)*(2 if k in ['X18','B06'] else 1)
        assert rows[k]['purchase_qty']==expected
    cover=read('data/r04-cover-parts.json')
    close(rows['X10']['net_qty']+rows['X12']['net_qty'],sum(p['area_m2'] for p in cover)*15.7)
    assert len(cover)==310 and len(read('data/r04-plate-parts.json'))==176
    close(rows['X11']['net_qty'],base['new_bent_3mm_kg'])
    close(rows['X23']['net_qty'],7.29/.4)
    close(rows['X24']['purchase_qty'],base['coating_area'])
    for r in d['rows']:
        if r['id'] in ['X09','X13','X21','X22']:r['verification']='Jumlah/luas/volume model dibaca ulang; stok atau allowance dihitung terpisah'
        elif r['id'] in ['X10','X11','X12']:r['verification']='Geometri dan pola potong arsip; bukan pembacaan ulang semua pelat native'
        elif 'verification' not in r:r['verification']='Usulan atau allowance; aritmetika diperiksa, kebutuhan final belum ditetapkan'
    ledger=[dict(id=r['id'],name=r['name'],unit=r['unit'],excel_qty=source.get(r['id'],{}).get('purchase_qty'),
        excel_unit=source.get(r['id'],{}).get('unit'),net_qty=r['net_qty'],purchase_qty=r['purchase_qty'],
        verification=r['verification'],basis=r['basis']) for r in d['rows']]
    steel=sum(r['purchase_qty'] for r in d['rows'] if r['unit']=='kg')
    close(steel,9570.466)
    out=dict(revision='quantity-reaudit-2026-09-11',live_elements=545,parameter_checks=checks,
        confirmed_excel_kg=1620,confirmed_excel_kg_per_bar=30,confirmed_excel_bars=54,
        native_rhs=dict(cuts=245,length_m=sum(L for i,L in native_cuts)/1000,stocks=len(native_stocks),purchase_kg=len(native_stocks)*32.5),
        full_rhs=dict(cuts=361,length_m=sum(L for i,L in allcuts)/1000,stocks=101,purchase_kg=3282.5),
        shs_batches=batches,plate_corrections=corrections,steel_purchase_kg=steel,previous_steel_purchase_kg=9640.394,
        ledger=ledger,decision='Gunakan volume model untuk lingkup model, bukan 54 batang hasil konversi Excel. Pertahankan 101 sebagai pola layak model + usulan, bukan minimum terbukti. Semua usulan tetap berlabel dan belum final.',
        limits='RHS memakai massa katalog 32,5 kg/6 m pada 2,3 mm. Angka30 kg dari Bam adalah pembagi Excel, bukan berat timbang. Pelat120×240 dihitung geometris. Profil railing masih memakai family pengganti; berat family tidak dipakai. Sambungan, backing, angkur, coating, cadangan dan pengaku usulan belum menjadi kebutuhan pelaksanaan final.')
    def clean(v):
        if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
        if isinstance(v,list):return [clean(x) for x in v]
        return round(v,8) if isinstance(v,float) else v
    out=clean(out);target=ROOT/'assets/r06'
    (target/'quantity-reaudit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    with (target/'quantity-reaudit.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows(out['ledger'])
    return out

if __name__=='__main__':
    a=audit(read('assets/r05/boq.json'));print(f"PASS: {a['live_elements']} live elements, {a['parameter_checks']} parameters, all {len(a['ledger'])} RAB rows classified; steel {a['steel_purchase_kg']} kg.")
