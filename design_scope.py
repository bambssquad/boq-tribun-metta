"""Repack native RHS only; never subtract proposed kg from pooled purchase kg."""
import json
from collections import defaultdict
from pathlib import Path
from revision04 import pack_bars

ROOT = Path(__file__).parent

def build():
    d = json.loads((ROOT/'assets/r05/boq.json').read_text(encoding='utf-8'))
    live = json.loads((ROOT/'data/quantity-reaudit-live.json').read_text(encoding='utf-8'))
    byid = {e['id']: e for e in live['members']}
    cuts, owners = [], {}
    for r in d['rows']:
        if r['id'] not in ['X01','X02','X03','X04','X05','X06','B01']: continue
        for ident in r['revit_ids']:
            e = byid[ident]['props']
            cuts.append((str(ident), e.get('Cut Length', e.get('System Length'))*304.8))
            owners[str(ident)] = r['id']
    stocks = pack_bars(cuts)
    allocated = defaultdict(float)
    for b in stocks:
        total = sum(L for _, L in b['cuts'])
        assert sum(L+3 for _, L in b['cuts']) <= 6000.000001
        for ident, L in b['cuts']: allocated[owners[str(ident)]] += L/total
    assert len(cuts) == 245 and len(stocks) == 97
    assert abs(sum(allocated.values())-97)<1e-8
    out = dict(native=dict(stocks=stocks, stock_count=97, cut_count=245,
        length_m=sum(L for _,L in cuts)/1000, allocated_bars=dict(allocated)),
        excluded_ids=['B02','B03','B04','B05','B06'],
        limitation='Versi A menghapus penyangga dan pengaku tangga usulan beserta baut/mur/ring B04-B06. Pelat, sambungan utama, angkur, cat dan biaya pelengkap tetap estimasi/cadangan bersama; bukan seluruhnya elemen native dan bukan RAB pelaksanaan final.')
    (ROOT/'assets/r07/design-scope.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    return out

if __name__ == '__main__':
    print('PASS: native scope', build()['native']['stock_count'], 'stocks')
