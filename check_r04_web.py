import json,re,subprocess,shutil
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent
home=BeautifulSoup((ROOT/'dist/index.html').read_text(encoding='utf8'),'html.parser')
page=BeautifulSoup((ROOT/'dist/r04.html').read_text(encoding='utf8'),'html.parser')
tools=(ROOT/'dist/tools.html').read_text(encoding='utf8')
d=json.loads((ROOT/'dist/assets/r04/data.json').read_text())
assert len(home.select('.archive-card'))==18
gallery=json.loads(re.search(r'const METTA_DRAWINGS=(\[.*?\]);',str(home),re.S).group(1))
assert [r['revision'] for r in gallery[:6]]==['R04']*6
assert all(r['revision']=='R03' and 'Arsip R03' in r['title'] for r in gallery[6:])
assert len(page.select('[data-sheet]'))==6
revised=json.loads(re.search(r'const REVISED=(\[.*?\]);',tools,re.S).group(1))
finishes=json.loads(re.search(r'const FINISH_GEOMETRY=(\[.*?\]);',tools,re.S).group(1))
ids={r['id'] for r in revised};audit=json.loads((ROOT/'data/revit-r04-audit.json').read_text())
assert not ids & set(audit['removed_ids'])
assert {r['id'] for r in audit['braces']}<=ids
assert len([r for r in revised if r['group']=='bracing'])==20
assert len([r for r in finishes if r['group']=='tangga'])==176
assert len([r for r in finishes if r['group'] in ['riser','skirt']])==310
for r in revised+finishes:assert len(r['vertices'])==8 and all(len(v)==3 for v in r['vertices'])
assert d['native_counts']==dict(rhs=165,columns=80,diagonals=20,x_sets=10,stair_fields=56,stair_parts=176,cover_parts=310)
assert len(d['mass_ledger'])==8
assert abs(sum(r['purchase_kg'] for r in d['mass_ledger'])-d['steel_purchase_kg'])<1e-6
for r in [home,page]:
 ids={el['id'] for el in r.select('[id]')}
 for el in r.select('[href],[src]'):
  url=el.get('href',el.get('src',''))
  if url.startswith(('http:','https:','data:')):continue
  path,_,fragment=url.partition('#')
  assert not path or (ROOT/'dist'/path).is_file(),url
  if not path:assert not fragment or fragment in ids or (r is home and fragment in ['timeline','surf','index']),url
for g in gallery:
 for key in ['svg','dxf','pdf']:assert (ROOT/'dist'/g[key]).is_file()
node=shutil.which('node') or r'C:\Users\adigh\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
subprocess.run([node,'--check',str(ROOT/'dist/assets/r04/app.js')],check=True)
print('PASS: published-model IDs/counts, native plate/cover geometry, 18 revision-aware gallery items, 6 new sheets, purchasing mass and all local links.')
