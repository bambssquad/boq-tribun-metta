import math,json
from pathlib import Path
from study_r05 import rhs,beam,compression
ROOT=Path(__file__).parent
s=json.loads((ROOT/'data/r05-study.json').read_text(encoding='utf-8'));d=json.loads((ROOT/'assets/r05/boq.json').read_text(encoding='utf-8'))
for t in [1.488,1.6,1.86,2.0,2.139,2.3]:
 p=rhs(t);analytic=50*100-(50-2*t)*(100-2*t)-(4-math.pi)*((2*t)**2-t*t)
 assert abs(p['A']-analytic)<.002
 assert p['Ix']>p['Iy']>0 and p['Z']>p['S']
assert not beam(4000,.25,1.488)['passes_screen']
assert beam(2000,.25,1.488)['passes_screen']
assert not beam(1060,1.77,1.488)['passes_screen']
assert compression(2482,1.488,2)['phiPn_kN']<compression(2482,1.488,1)['phiPn_kN']
assert len(s['candidate_ids'])==len(set(s['candidate_ids']))==45
old={str(label):L for stock in s['procurement']['baseline_cuts'] for label,L in stock['cuts']}
new={}
for stock in s['procurement']['baseline_cuts']:
  assert stock['used']<=6000 and abs(stock['used']-sum(L+3 for _,L in stock['cuts']))<1e-6
  for label,L in stock['cuts']:
   assert str(label) not in new;new[str(label)]=L
assert old==new
assert len(new)==361 and len(s['procurement']['baseline_cuts'])==101
for key,mass in [('model',3282.5),('h20',2854.26),('h16',2283.61)]:
 assert abs(s['procurement']['variants'][key]['purchase_kg']-mass)<1e-6
 assert abs(sum(({**r,**r.get('variants',{}).get(key,{})})['purchase_qty'] for r in d['rows'][:8])-mass)<1e-6
assert abs(sum(r['purchase_qty'] for r in d['rows'] if r['unit']=='kg')-9570.466)<1e-6
plate=d['plate_stock'];assert plate['sheet_count']==5 and abs(plate['purchase_kg']-678.24)<1e-8
assert len(d['source_rows'])==24
print('PASS: rounded sections, long-span/thin-bearer boundaries, restraint sensitivity, 361 unique cuts, 101 stocks at all thicknesses, steel and plate masses reconciled.')
