"""Reconcile physical cuts, six-metre stock and the user's Excel weights."""
import csv, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np
from r04_model import load_model
from revision04 import pack_bars
from study_r05 import rhs

ROOT = Path(__file__).parent
def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

def build():
    model=load_model(); base=read('assets/r04/data.json'); boq=read('assets/r05/boq.json'); source=read('data/boq-2026-09-11-source.json')
    native={str(e['id']) for e in model['rhs']} | {str(e['id']) for e in model['columns']}
    cuts=[(str(label),float(length)) for stock in base['main_stock'] for label,length in stock['cuts']]
    assert len(cuts)==len({label for label,_ in cuts})==361
    assert native=={label for label,_ in cuts if label in native}
    parts=[]
    for label,part in [('native',[(i,L) for i,L in cuts if i in native]),('stair_proposal',[(i,L) for i,L in cuts if i not in native]),('combined',cuts)]:
        stocks=pack_bars(part);length=sum(L for _,L in part)/1000
        parts.append(dict(scope=label,cut_count=len(part),cut_length_m=length,stock_count=len(stocks),stock_length_m=len(stocks)*6,
            purchase_kg=len(stocks)*32.5,net_section_kg=length*rhs(2.3)['kg_m'],net_catalogue_kg=length*32.5/6,
            kerf_m=len(part)*.003,offcut_m=len(stocks)*6-length-len(part)*.003,minimum_by_length=math.ceil((length+len(part)*.003)/6)))
    geo={e['id']:e for e in model['items']};duplicates=defaultdict(list)
    for e in model['rhs']:
        key=tuple(sorted(tuple(np.round(v,2)) for v in geo[e['id']]['vertices']))
        duplicates[key].append(e['id'])
    duplicate_groups=[ids for ids in duplicates.values() if len(ids)>1]
    joists=next(r['revit_ids'] for r in boq['rows'] if r['id']=='X03');overlaps=[]
    for n,a in enumerate(joists):
        v=np.array(geo[a]['vertices']);lo=v.min(0);hi=v.max(0)
        for b in joists[n+1:]:
            w=np.array(geo[b]['vertices']);lb=w.min(0);hb=w.max(0)
            if abs((lo[1]+hi[1]-lb[1]-hb[1])/2)<2 and abs((lo[2]+hi[2]-lb[2]-hb[2])/2)<2:
                length=min(hi[0],hb[0])-max(lo[0],lb[0])
                if length>3:overlaps.append(dict(ids=[a,b],overlap_mm=float(length)))
    assert not duplicate_groups and not overlaps
    excel_kg=sum(r['qty'] for r in source['rows'][:5])
    rows=[]
    for r in boq['rows'][:8]:
        length=r['net_qty']/rhs(2.3)['kg_m']
        origin=next((x for x in source['rows'] if x['id']==r['id']),None)
        rows.append(dict(id=r['id'],name=r['name'],cut_count=len(r['revit_ids']) if r['id']!='B02' else 116,
            length_m=length,net_section_kg=r['net_qty'],purchase_allocated_kg=r['purchase_qty'],
            source_kg=origin['qty'] if origin else None,source_material=origin['material'] if origin else 'Tidak ada baris terpisah'))
    out=dict(date='2026-09-11',profile='50x100x2.3 mm',stock_m=6,stock_kg=32.5,
        catalogue_url='https://www.smsperkasa.com/produk/besi-hollow-hitam',
        excel_hollow_50x100_kg=excel_kg,excel_equivalent_at_30kg=excel_kg/30,excel_equivalent_at_catalogue=excel_kg/32.5,
        scopes=parts,components=rows,duplicate_rhs_groups=duplicate_groups,collinear_joist_overlaps=overlaps,
        limitations=['Panjang dan ID dicocokkan dengan pembacaan Revit 11 September; geometri duplikat diperiksa pada arsip R04 yang direkonsiliasi.',
            'Jumlah batang berasal dari pola potong, bukan pembulatan berat tiap komponen.',
            '97 batang native + 7 batang usulan jika dibeli terpisah; gabungan 101 karena sisa potong dipakai bersama.',
            'Berat penampang memakai sudut membulat; berat katalog dan berat timbang produk dapat berbeda.',
            'Pola FFD adalah solusi layak, bukan bukti jumlah batang minimum global.'])
    folder=ROOT/'assets/r05';folder.mkdir(exist_ok=True)
    def rounded(value):
        if isinstance(value,float):return round(value,8)
        if isinstance(value,list):return [rounded(x) for x in value]
        if isinstance(value,dict):return {k:rounded(v) for k,v in value.items()}
        return value
    out=rounded(out)
    (folder/'audit-batang.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    with (folder/'pola-potong-101-batang.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f);writer.writerow(['Batang_stok','Panjang_stok_mm','ID_potongan','Panjang_potongan_mm','Sumber','Kg_stok_1.6_sekali_per_batang','Kg_stok_2.0_sekali_per_batang','Kg_stok_2.3_sekali_per_batang','Alokasi_kg_potongan_2.3'])
        for n,stock in enumerate(base['main_stock'],1):
            total=sum(L for _,L in stock['cuts'])
            for j,(label,length) in enumerate(stock['cuts']):writer.writerow([n,6000,label,round(length,4),'Revit' if str(label) in native else 'Usulan tangga',22.61 if j==0 else '',28.26 if j==0 else '',32.5 if j==0 else '',32.5*length/total])
    print('Stock audit:',len(cuts),'unique cuts;',round(parts[-1]['cut_length_m'],3),'m;',parts[-1]['stock_count'],'stocks;',parts[-1]['purchase_kg'],'kg; no duplicate RHS solids or collinear joist overlaps.')
    return out

if __name__=='__main__':build()
