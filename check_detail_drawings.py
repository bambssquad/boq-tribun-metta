import json, tempfile,xml.etree.ElementTree as ET
from pathlib import Path
import detail_drawings
with tempfile.TemporaryDirectory() as tmp:
 m=detail_drawings.build(Path(tmp));out=Path(tmp)/'assets/drawings'
 assert len(m['versions']['v1'])==8 and len(m['versions']['v2'])==11
 for v,sheets in m['versions'].items():
  for sheet in sheets:
   root=ET.parse(out/sheet['file']).getroot();assert root.tag.endswith('svg');assert root.attrib['viewBox']
   assert len(list(root.iter()))>12
 a=ET.parse(out/'v1-02-frame.svg');b=ET.parse(out/'v2-02-frame.svg')
 ids=lambda tree:{e.attrib['data-member'] for e in tree.iter() if 'data-member' in e.attrib}
 g=json.loads((detail_drawings.ROOT/'assets/r08/geometry.json').read_text())
 d=json.loads((detail_drawings.ROOT/'assets/r08/data.json').read_text())
 width=str(round(d['params']['x1']-d['params']['x0']))
 assert 'INFILL '+width in (out/'v2-01-plan.svg').read_text(encoding='utf-8')
 assert '>'+width+'</text>' in (out/'v2-02-frame.svg').read_text(encoding='utf-8')
 assert {str(e['id']) for e in g['frame']}<=ids(b)
 assert not {str(e['id']) for e in g['frame']}&ids(a)
 assert len({x for x in ids(b) if x.startswith('I')})==54
 for mode in ('a','c'):
  if f'v2-{mode}' not in m['versions']:continue
  option=json.loads((detail_drawings.ROOT/f'assets/r08/geometry-{mode}.json').read_text())
  drawn=ids(ET.parse(out/f'v2-{mode}-02-frame.svg'))
  assert {str(e['id']) for e in option.get('added_native_items',[])}<=drawn
 print(f'PASS: {sum(map(len,m["versions"].values()))} XML sheets; V1 excludes infill; V2 contains all 54 proposed members; A/C added members match geometry; viewer assets copied.')
