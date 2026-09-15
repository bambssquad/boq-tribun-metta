"""Independent reconciliation of generated R08 and immutable archive inputs."""
import json, math
from pathlib import Path
from shapely.geometry import shape, box
from shapely.ops import unary_union

ROOT=Path(__file__).parent
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
d=read('assets/r08/data.json');g=read('assets/r08/geometry.json');old=read('assets/r04/data.json')
audit=read('assets/r08/audit.json');d['cuts']=audit['cuts'];d['nesting']=audit['nesting'];d['shs']['stocks']=audit['shs_stocks'];d['clamps']['stocks']=audit['clamp_stocks']
for opt in d['mesh_options']:opt['nesting']=audit['mesh_nesting'][opt['id']]
strip=box(d['params']['x0'],-10,d['params']['x1'],5000)
rc=unary_union([box(c['lo'][0]-3,c['lo'][1]-3,c['hi'][0]+3,c['hi'][1]+3) for c in g['concrete']])
assert len(g['stairs'])==45
assert len(set(s['id'] for s in g['stairs']))==45
old_area=sum(s['profile']['area_m2'] for s in old['stairs'])
removed=sum(s['before_m2']-s['after_m2'] for s in d['changes']['stair_delta'])
assert abs(old_area-removed-sum(s['area_m2'] for s in g['stairs']))<1e-5
for s in g['stairs']:assert shape(s['polygon']).intersection(strip).area<.01
for p in g['infill']+g['wood']:
    polygon=shape(p['polygon']);assert polygon.intersection(rc).area<.01
    assert abs(polygon.area/1e6-p['area_m2'])<1e-9
assert sum(w['seats'] for w in g['wood'])==4
assert d['changes']['clear_passages_mm']==[600,600,600]
assert len(d['changes']['removed_native_rhs_ids'])==8
assert len(d['changes']['removed_deck_ids'])==6
for e in g['frame']:
    v=e['vertices'];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
    assert box(lo[0],lo[1],hi[0],hi[1]).intersection(rc).area<.01,(e['id'],'RC clash')
    if e['group']=='I01':
        # Actual base plate 140x150 lies inside chosen strip and outside RC.
        x=(lo[0]+hi[0])/2;y=(lo[1]+hi[1])/2;base=box(x-70,y-75,x+70,y+75)
        assert base.intersection(rc).area<.01
        assert base.difference(strip).area<.01
    if e['group']=='I03':
        # Joist top is directly below deck, not underneath the longitudinal girder.
        top=round((hi[2]+4)/500)*500;assert abs(hi[2]-(top-4))<.01
        assert abs(hi[2]-lo[2]-100)<.01
for kind in ['rhs','shs','clamps']:
    summary=d[kind];cs=d['cuts'][kind];byid={c['id']:c for c in cs}
    packed=[p for b in summary['stocks'] for p in b['cuts']]
    assert len(packed)==len(byid)==len(cs)
    assert {p[0] for p in packed}==set(byid)
    for b in summary['stocks']:
        assert sum(L+3 for _,L in b['cuts'])<=6000+1e-6
        for ident,L in b['cuts']:assert abs(L-byid[ident]['length_mm'])<1e-9
    assert abs(sum(summary['allocated_bars'].values())-summary['stock_count'])<1e-8
    assert abs(sum(L for _,L in packed)/1000-summary['length_m'])<1e-8
assert d['rhs']['stock_count']==109
assert d['rhs']['cut_count']==245-8+90+54
native={str(e['id']):e['props'] for e in read('data/quantity-reaudit-live.json')['members']}
for c in d['cuts']['rhs']:
    if c['origin']=='native archive':
        p=native[c['id']];assert abs(c['length_mm']-p.get('Cut Length',p.get('System Length'))*304.8)<.001
def nesting(sheets,W,H):
    allids=[]
    for s in sheets:
        polys=[]
        for p in s:
            assert p['x']>=10 and p['y']>=10 and p['x']+p['w']<=W-10+1e-6 and p['y']+p['h']<=H-10+1e-6
            q=box(p['x'],p['y'],p['x']+p['w'],p['y']+p['h'])
            assert all(q.intersection(other).area<.01 for other in polys)
            polys.append(q);allids.append(p['id'])
    assert len(allids)==len(set(allids))
    return allids
for name,ss in d['nesting'].items():nesting(ss,2400,1200)
assert set(nesting(d['nesting']['plate2'],2400,1200))=={p['id'] for p in g['plate2']}
assert set(nesting(d['nesting']['plate3'],2400,1200))=={p['id'] for p in g['stairs']}
assert len(nesting(d['nesting']['infill_base8'],2400,1200))==100
for opt in d['mesh_options']:
    assert opt['price_per_roll'] is None
    assert opt['purchase_kg']==opt['rolls']*opt['catalogue_roll_kg']
    assert set(nesting(opt['nesting'],opt['roll_length_m']*1000,opt['roll_width_m']*1000))=={p['id'] for p in g['mesh']}
rows={r['id']:r for r in d['rows']}
assert abs(rows['X13']['purchase_qty']+rows['I04']['purchase_qty']-len(d['nesting']['infill_base8'])*180.864)<1e-8
assert 'X12' not in rows and all(k in rows for k in ['M01','M02','M03','M04','M05','I01','I02','I03','I04','I05','I06'])
assert abs(rows['X10']['net_qty']-sum(p['area_m2'] for p in g['plate2'])*15.7)<1e-8
assert abs(rows['X11']['net_qty']-sum(p['net_flat_area'] for p in g['stairs'])*23.55)<1e-8
assert rows['X18']['purchase_qty']==2*rows['X15']['purchase_qty']
assert rows['B06']['purchase_qty']==2*rows['B04']['purchase_qty']
from pypdf import PdfReader
pdf=PdfReader(ROOT/'assets/r08/METTA-R08-RAB-portrait.pdf')
assert all(float(p.mediabox.height)>float(p.mediabox.width) for p in pdf.pages)
text=' '.join(p.extract_text() for p in pdf.pages)
table_text=' '.join(p.extract_text() for p in pdf.pages[:2])
def fmt(x,dec=0):
    s=f'{x:,.{dec}f}'
    if dec:s=s.rstrip('0').rstrip('.')
    return s.translate(str.maketrans({',':'.','.':','}))
total=0;mass=0
for r in d['rows']:
    v=r.get('mesh_variants',{}).get('m20_25',r);q=v['purchase_qty']
    labor=math.floor(q*r['labor_rate']+.5);material=math.floor(q*r['material_rate']+.5)
    total+=labor+material
    if r['unit']=='kg':mass+=q
    assert fmt(q,4) in table_text,(r['id'],'PDF qty')
    assert fmt(labor+material) in table_text,(r['id'],'PDF row total')
assert fmt(total) in text and fmt(mass,3) in text
assert '109' in text and '3.542,5' in text and 'Rp30.000/kg' in text
print('PASS: R08 geometry, RC/base clearance, 45 stairs, 4 indicative seats, native deltas, 109 RHS, all cuts/nesting and row mass reconciliation.')
