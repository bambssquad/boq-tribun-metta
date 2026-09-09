import json,math
from pathlib import Path
import ezdxf
from revision04 import build_data
from pypdf import PdfReader
ROOT=Path(__file__).parent;d=build_data()
def verify(sheets,expected):
 ids=[]
 for parts in sheets:
  for p in parts:
   ids.append(p['id']);assert p['x']>=10 and p['y']>=10 and p['x']+p['w']<=2390+.001 and p['y']+p['h']<=1190+.001
  for i,p in enumerate(parts):
   for q in parts[i+1:]:assert p['x']+p['w']+2.99<=q['x'] or q['x']+q['w']+2.99<=p['x'] or p['y']+p['h']+2.99<=q['y'] or q['y']+q['h']+2.99<=p['y'],(p,q)
 assert len(ids)==len(set(ids))==expected
verify([row['parts'] for s in d['nesting'] for row in s],56)
verify(d['enclosure']['nesting'],len(d['enclosure']['panels']))
for bins in [d['main_stock'],d['cross_stock']]:
 for b in bins:assert sum(L+3 for _,L in b['cuts'])<=6000+.001
assert abs(sum(r['profile']['area_m2'] for r in d['stairs'])-d['audited_area'])<1e-5
assert d['net_flat_area']<d['flat_area']
assert abs(sum(r['qty']*r['kg_per_unit'] for r in d['rows'])-d['steel_purchase_kg'])<1e-6
assert len({r['code'] for r in d['rows']})==len(d['rows'])
assert len(d['nesting'])<=8 and len(d['enclosure']['nesting'])<=26
cover_parts={p['code']:p for p in json.loads((ROOT/'data/r04-cover-parts.json').read_text())}
for p in d['enclosure']['panels']:
 q=cover_parts['C2-'+p['code']];x,y,z=p['x'],p['y'],p['z'];w,h=p['width'],p['height']
 bounds=[x,y,z,x+w,y+2,z+h] if p['plane']=='xz' else [x,y,z,x+2,y+w,z+h] if p['plane']=='yz' else [x,y,z,x+w,y+h,z+2]
 assert max(abs(a-b) for a,b in zip(bounds,q['bounds']))<1e-6
 assert abs(q['net_kg']-p['kg'])<1e-8
assert abs(sum(p['net_kg'] for p in cover_parts.values())-d['enclosure']['net_kg'])<1e-6
audit=json.loads((ROOT/'data/revit-r04-audit.json').read_text())
cut_ids={ident for b in d['main_stock'] for ident,L in b['cuts']}
assert not set(map(str,audit['removed_ids'])) & cut_ids
assert set(str(r['id']) for r in audit['braces'])<=cut_ids
assert len(d['stair_geometry'])==176
native_parts=json.loads((ROOT/'data/r04-plate-parts.json').read_text())
flat_area=sum((p['bounds'][3]-p['bounds'][0])*(p['bounds'][4]-p['bounds'][1])/1e6 for p in native_parts if p['kind']=='tapak')
assert abs(flat_area-d['audited_area'])<1e-5
for p in native_parts:
 if p['kind']=='tapak':assert abs(p['bounds'][5]-p['bounds'][2]-3)<1e-6
for name in ['T-01','T-02','T-03','T-04','T-05','T-06']:
 doc=ezdxf.readfile(ROOT/'assets/r04'/f'{name}.dxf');assert doc.units==4 and not doc.audit().has_errors
assert len(PdfReader(ROOT/'assets/r04/METTA-R04-tangga-detail.pdf').pages)==6
print('PASS: part coverage, kerf/trim, no nesting overlap, stock capacity, native plate thickness/area, bracing IDs, mass and 6 CAD files.')
