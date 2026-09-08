import json,re,subprocess,shutil
import ezdxf
from pypdf import PdfReader
from pathlib import Path
from bs4 import BeautifulSoup
p=Path(__file__).parent
html=(p/'dist/tools.html').read_text(encoding='utf-8');s=BeautifulSoup(html,'html.parser')
ids=[x['id'] for x in s.select('[id]')];assert len(ids)==len(set(ids))
for a in s.select('a[href^="#"]'):
    target=a['href'][1:]
    assert not target or target in ids,target
script='\n'.join(x.get_text() for x in s.select('script') if not x.get('src'))
tmp=p/'check.generated.js';tmp.write_text(script,encoding='utf-8')
node=shutil.which('node') or r'C:\Users\adigh\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
subprocess.run([node,'--check',str(tmp)],check=True);tmp.unlink()
m=json.loads((p/'data/model.json').read_text())
assert len(m['rhs'])==161 and len(m['columns'])==80
assert len([i for i in m['items'] if i['group']=='bracing'])==16
assert len([i for i in m['items'] if i['group']=='baseplate'])==160
assert abs(m['deck_area_m2']-82.34504912118528)<1e-8
assert all(len(i['vertices'])==8 for i in m['items'])
basis=re.search(r'function basisH\(r\)\{(.*?)\n\}',script,re.S).group(0)
test="const assert=require('node:assert/strict'); let S={wH:5,bar:6,mode:'satuan'};"+basis+"\n"+'''const r={nm:'Rangka RHS — hasil model',n:161,L:415.19,kg:32.5/6};
assert.equal(basisH(r).bars,75);assert.equal(basisH(r).kg,2437.5);
S.wH=10;assert.equal(basisH(r).bars,77);
S.wH=5;r.L=100;assert.equal(basisH(r).bars,18);
console.log('BOQ: combined stock, mass, waste changes and edited lengths verified.');'''
subprocess.run([node,'-e',test],check=True)
assert 'IF(AND(B${R}=' in script,'Excel must preserve optimized stock condition'
for el in s.select('[src],a[href]'):
    uri=el.get('src') or el.get('href','')
    if uri.startswith('assets/'):
        assert (p/'dist'/uri).is_file(),uri
manifest=json.loads((p/'assets/technical/manifest.json').read_text(encoding='utf8'))
assert len(manifest)==12
for r in manifest:
    doc=ezdxf.readfile(p/r['dxf']);assert doc.units==4 and not doc.audit().has_errors
assert len(PdfReader(p/'assets/technical/METTA-R02-gambar-koordinasi.pdf').pages)==12
assert len(list((p/'assets/technical/revit').glob('S-*.png')))==12
fin=json.loads((p/'data/finishes-audit.json').read_text())
geo=json.loads((p/'data/finishes-geometry.json').read_text())
assert len(fin['rail'])==95 and len(geo['items'])==197
assert {r['id'] for r in fin['rail']+fin['floor']}=={r['id'] for r in geo['items']}
data=json.loads(re.search(r'const DATA = (\{.*?\});',script,re.S).group(1))
assert abs(data['sheetA']-2.88)<1e-10
assert next(r['n'] for r in data['hollow'] if r['nm']=='Tiang railing — hasil model')==85
assert abs(next(r['L'] for r in data['hollow'] if r['nm']=='Tiang railing — hasil model')-97.5)<.001
assert 'catalog-prices' in ids and 'drawing-dialog' in ids
print('PASS: 12 editable DXFs (mm), 12 PDF pages, 12 Revit exports, local assets and 197 finish geometry IDs.')
print('PASS: JavaScript syntax, internal links, model counts, deck area, BOQ and Excel formula rule.')
# Validate the archive entry and its links to the preserved working page.
home=BeautifulSoup((p/'dist/index.html').read_text(encoding='utf-8'),'html.parser')
assert len(home.select('.archive-card'))==12
assert home.select_one('.sap-wordmark').get_text(strip=True)=='SELARAS ADHI PERKASA'
assert home.select_one('.archive-project-title').get_text(strip=True)=='ARSIP DESAIN METTA'
assert home.select_one('.archive-project-date').get_text(strip=True)=='(09/2026)'
assert home.select_one('.small-brand').get_text(strip=True)=='SAP'
assert s.select_one('.look-brand').get_text(strip=True)=='SAP'
assert len(home.select('.timeline-scale button'))==12
assert not home.select('audio,video'),'Archive must have no soundtrack or media player'
assert 'AudioContext' not in (p/'lookback.js').read_text(encoding='utf-8')
for el in home.select('[src],a[href],link[href]'):
    uri=el.get('src') or el.get('href','')
    if uri.startswith(('http:','https:','data:')):continue
    path,_,fragment=uri.partition('#')
    if path:assert (p/'dist'/path).is_file(),uri
    if path=='tools.html' and fragment:assert fragment in ids,uri
for script_path in ['lookback.js','panzoom.js']:
    subprocess.run([node,'--check',str(p/'dist'/script_path)],check=True)
assert 'const METTA_DRAWINGS=[{' in str(home)
print('PASS: archive routes, 12 drawings, tool deep links, no audio, and controller syntax.')
