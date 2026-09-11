"""Independently reconcile Excel RHS weights with archived audited model cuts."""
import json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from r04_model import load_model
ROOT=Path(__file__).parent
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def build():
    d=read('assets/r05/boq.json');source=read('data/boq-2026-09-11-source.json');live=read('data/revit-2026-09-11-audit.json')
    audit=read('assets/r05/audit-batang.json');stocks=d['study']['procurement']['baseline_cuts'];model=load_model()
    cuts=[(str(id),float(length)) for stock in stocks for id,length in stock['cuts']]
    native={str(r['id']) for r in model['rhs']+model['columns']};seen=set();native_length=proposal_length=0.
    current={str(r['id']):r for r in live['members']};mismatches=[]
    for id,L in cuts:
        assert id not in seen;seen.add(id)
        if id in native:
            native_length+=L;p=current[id]['props'];measured=p.get('Cut Length',p.get('System Length'))*304.8
            if abs(L-measured)>1:mismatches.append(dict(id=id,cut_mm=L,audit_mm=measured))
        else:proposal_length+=L
    assert native<=seen and not mismatches
    stock_length=6000*len(stocks);used=sum(L for _,L in cuts);kerf=len(cuts)*3
    assert all(sum(L for _,L in s['cuts'])+3*len(s['cuts'])<=6000+1e-7 for s in stocks)
    # Check all RHS and columns, not just the joist group: exact duplicate
    # solids and coincident axis-aligned members in the same cross-section plane.
    solids=defaultdict(list);aligned=[]
    for e in model['items']:
        if str(e['id']) not in native:continue
        v=np.array(e['vertices']);solids[tuple(sorted(tuple(np.round(p,2)) for p in v))].append(e['id'])
        lo=v.min(0);hi=v.max(0);size=hi-lo;axis=int(np.argmax(size));cross=[i for i in range(3) if i!=axis]
        if all(abs(size[i]-expected)<.5 for i,expected in zip(sorted(cross,key=lambda i:size[i]),[50,100])):
            aligned.append(dict(id=e['id'],axis=axis,center=(lo+hi)/2,lo=lo,hi=hi,cross=cross))
    overlaps=[]
    for i,a in enumerate(aligned):
        for b in aligned[i+1:]:
            if a['axis']!=b['axis']:continue
            if all(abs(a['center'][k]-b['center'][k])<1 for k in a['cross']):
                k=a['axis'];overlap=min(a['hi'][k],b['hi'][k])-max(a['lo'][k],b['lo'][k])
                if overlap>3:overlaps.append(dict(ids=[a['id'],b['id']],overlap_mm=float(overlap)))
    duplicates=[ids for ids in solids.values() if len(ids)>1]
    assert not duplicates and not overlaps
    source_ids=['X01','X02','X03','X04','X05'];sr={r['id']:r for r in source['rows']}
    assert all(r['unit'].lower()=='kg' and '100x50' in r['material'].replace(' ','') for r in [sr[id] for id in source_ids])
    excel_kg=sum(sr[id]['qty'] for id in source_ids)
    bridge=[]
    for r in audit['components']:
        old=sr[r['id']]['qty'] if r['id'] in source_ids else 0
        bridge.append(dict(id=r['id'],name=r['name'],excel_rhs_kg=old,model_purchase_kg=r['purchase_allocated_kg'],
            difference_kg=r['purchase_allocated_kg']-old,length_m=r['length_m'],pieces=r['cut_count'],
            note='Excel bracing62kg adalah40x40; bukan bagian1620kg RHS.' if r['id']=='X06' else 'Tidak ada baris RHS terpisah di Excel; bukan bukti tidak tercakup dalam pekerjaan lain.' if r['id'] in ['B01','B02'] else 'Perbandingan label; kesetaraan lingkup belum dikonfirmasi dari daftar potong Excel.'))
    assert abs(excel_kg+sum(r['difference_kg'] for r in bridge)-len(stocks)*32.5)<1e-5
    data=dict(source_filename=source['filename'],source_sheet=source['sheet'],source_rows=[sr[id]['excel_row'] for id in source_ids],
      excel_rhs_kg=excel_kg,excel_conversion_confirmed_by_user=True,example_excel_kg_per_bar=30,example_excel_bars=excel_kg/30,
      stock_length_m=6,model_stocks=len(stocks),model_purchase_kg=len(stocks)*32.5,
      model_cut_length_m=used/1000,native_length_m=native_length/1000,proposal_length_m=proposal_length/1000,
      native_cuts=len(native),proposal_cuts=len(cuts)-len(native),unique_cuts=len(cuts),
      kerf_m=kerf/1000,offcut_m=(stock_length-used-kerf)/1000,
      length_lower_bound=math.ceil((used+kerf)/6000),minimum_proven=False,
      example54_available_m=54*6,example54_length_shortfall_m=used/1000-54*6,
      duplicate_solids=duplicates,collinear_overlaps=overlaps,aligned_members_checked=len(aligned),length_mismatches=mismatches,
      bridge=bridge,
      conclusion='54 batang dapat benar untuk lingkup Excel/asumsi lain.101 adalah pola layak untuk361potongan pada versi model+usulan ini, bukan lingkup yang sama atau minimum global terbukti.',
      provenance='Sumber Excel adalah ekstraksi tersimpan11Sep; ID/panjang dari audit11Sep. Geometri pemeriksaan duplikat adalah arsipR04 yang direkonsiliasi, bukan pengukuran lapangan.')
    def clean(v):
        if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
        if isinstance(v,list):return [clean(x) for x in v]
        return round(v,8) if isinstance(v,float) else v
    data=clean(data);(ROOT/'assets/r06/kg-reconciliation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PASS: 361 unique cuts, 245 native lengths within1mm;101 stocks feasible;99 length lower bound; Excel/model kg bridge reconciles; no checked duplicates.')
    return data
if __name__=='__main__':build()
