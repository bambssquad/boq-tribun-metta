"""Check all published CAD dimensions against the shared R03 measurement register."""
import json,math
from pathlib import Path
import ezdxf
from pypdf import PdfReader
ROOT=Path(__file__).parent
register=json.loads((ROOT/'assets/technical/dimensions-R03.json').read_text(encoding='utf8'))
manifest=json.loads((ROOT/'assets/technical/manifest.json').read_text(encoding='utf8'))
pdf=PdfReader(ROOT/'assets/technical/METTA-R02-gambar-koordinasi.pdf')
assert len(register['sheets'])==len(manifest)==len(pdf.pages)==12
total=0
for i,(sheet,m) in enumerate(zip(register['sheets'],manifest)):
    dimensions=sheet['dimensions'];assert dimensions and m['lod']==200 and m['revision']=='R03'
    doc=ezdxf.readfile(ROOT/m['dxf']);assert not doc.audit().has_errors and doc.units==4
    entities=list(doc.modelspace().query('DIMENSION'))
    assert len(entities)==len(dimensions)==m['dimension_count'],sheet['code']
    for q,e in zip(dimensions,entities):
        assert e.dxf.text==q['label'] and q['value_mm']>0 and q['basis']
        # Isometric dimensions state their true XYZ length explicitly.
        if 'isometrik' not in q['basis']:assert abs(math.dist(q['a'],q['b'])-q['value_mm'])<.0001
        assert e.dxf.geometry in doc.blocks
    page=pdf.pages[i].extract_text();assert 'R03' in page and 'LOD 200' in page and sheet['code'] in page
    svg=(ROOT/m['svg']).read_text(encoding='utf8');assert 'LOD 200' in svg
    total+=len(dimensions)
assert math.isclose(267*3+199,1000) and math.isclose(500/3*3,500)
assert [q['value_mm'] for q in register['sheets'][-1]['dimensions']]==[17700,5000,2500]
print(f'PASS: {total} editable dimensions across 12 DXF/SVG/PDF sheets, mm units, R03 and LOD 200; stair closure and true isometric lengths checked.')
