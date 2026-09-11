"""Independent limits and reconciliation checks for the preliminary study."""
import math,json,io,contextlib
from pathlib import Path
from structural_r06 import section,beam_check,guard_check,build,geometry
from r06_report import build as report
for b,h,t in [(50,100,1.488),(40,40,2.139),(60,60,2.139)]:
    # Closed-form rounded-rectangle area, independent from quadrature.
    area=2*t*(b+h)-(16-3*math.pi)*t*t
    assert math.isclose(section(b,h,t)['A'],area,rel_tol=1e-7)
short=beam_check(50,100,1.6,1000,.25);long=beam_check(50,100,1.6,2000,.25)
assert math.isclose(long['Mu_kNm']/short['Mu_kNm'],4)
assert math.isclose(long['deflection_mm']/short['deflection_mm'],16)
assert guard_check(40,40,2.3,500)['Mu_kNm']==guard_check(40,40,2.3,1000)['Mu_kNm']
assert not guard_check(40,40,2.8)['passes_member_screen']
assert guard_check(60,60,2.3)['passes_member_screen']
with contextlib.redirect_stdout(io.StringIO()):d=build();report()
assert len(d['matrix'])==18 and len(d['mixed'])==3
assert len(d['geometry']['columns'])==80
baseline=next(r for r in d['matrix'] if r['key']=='model-existing')
assert baseline['stocks']==101 and baseline['cost_low']==d['baseline_total']
assert baseline['max_gap_mm']==2040
thin=next(r for r in d['matrix'] if r['key']=='h16-existing')
assert not thin['gravity_screen'] and thin['bearer']['ratio']>1
infill=next(r for r in d['matrix'] if r['key']=='h16-1000')
assert infill['columns']==146 and infill['stocks']==129 and infill['max_gap_mm']<=1000
assert len(infill['stair_conflicts'])>0 and infill['cost_low']>d['baseline_total']
assert d['mixed'][1]['saving']<0 # Stock separation can erase nominal kg savings.
assert d['mixed'][2]['stocks']==103
assert all(r['compliance']=='BELUM DAPAT DITETAPKAN' for r in d['matrix'])
assert all(r['columns_checks'][0]['capacity_kN']>r['columns_checks'][1]['capacity_kN'] for r in d['matrix'])
assert len({(c['x'],c['y']) for c in d['geometry']['columns']})==80
print('PASS: R06 section units, beam scaling, railing point load, cost/stock reconciliation, stair conflicts and explicit compliance limits.')
