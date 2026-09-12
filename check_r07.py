"""Check review issue quantities, references, status and document completeness."""
import csv,json,math
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=Path(__file__).parent;OUT=ROOT/'assets/r07'
d=json.loads((OUT/'paket.json').read_text(encoding='utf-8'))
b=json.loads((ROOT/'assets/r05/boq.json').read_text(encoding='utf-8'))
def rows(name):
    with (OUT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
assert d['choices']==['1A','2A','3A'] and d['fabrication_released'] is False
cuts=rows('daftar-potong-review.csv')
assert len(cuts)==len({r['id_potongan'] for r in cuts})==361
assert sum(r['asal']=='Model' for r in cuts)==245
assert all(not r['panjang_final_disetujui_mm'] for r in cuts)
assert abs(sum(float(r['panjang_model_mm']) for r in cuts)/1000-b['quantity_audit']['full_rhs']['length_m'])<1e-6
stocks={}
for r in cuts:stocks[r['stok_acuan']]=stocks.get(r['stok_acuan'],0)+float(r['panjang_model_mm'])+3
assert len(stocks)==101 and max(stocks.values())<=6000
assert all('BELUM UNTUK' in r['status'] for r in cuts)
assert len(rows('register-kolom.csv'))==80
assert len(rows('form-ukur-lapangan.csv'))==10
assert len(rows('register-sambungan.csv'))==7
assert len(rows('tahapan-dan-QC.csv'))==10
budget=rows('RAB-review.csv');assert len(budget)==40
for extras in [False,True]:
    selection=[r for r in budget if extras or r['kelompok']=='Dasar']
    expected=next(r for r in b['comparison'] if r['case']=='model' and r['basis']=='purchase' and r['extras']==extras)
    assert abs(sum(float(r['total']) for r in selection)-expected['total'])<1e-6
assert abs(sum(float(r['volume_beli']) for r in budget if r['satuan']=='kg')-9570.466)<1e-6
page=BeautifulSoup((OUT/'index.html').read_text(encoding='utf-8'),'html.parser')
for a in page.select('[href],img[src]'):
    url=a.get('href',a.get('src',''))
    if not url or url.startswith(('http','#')):continue
    assert (OUT/url.split('#')[0]).resolve().is_file(),url
assert len(page.select('[data-note]'))==10
assert 'fabrication_released:false' in page.get_text() or 'fabrication_released:false' in str(page)
pdf=PdfReader(OUT/'METTA-R07-paket-pemeriksaan.pdf');assert len(pdf.pages)==13
texts=[p.extract_text() for p in pdf.pages]
assert all('UNTUK PEMERIKSAAN INSINYUR' in t for t in texts)
assert 'https://pesta.bsn.go.id/produk/detail/12927-sni17272020' in '\n'.join(texts)
assert 'Kandidat diperiksa' in '\n'.join(texts)
assert d['sections'][-1]['rows'][0][0].startswith('SNI ')
for svg in OUT.glob('*.svg'):
    s=ET.parse(svg).getroot()
    assert 'UNTUK PEMERIKSAAN' in ''.join(s.itertext())
print('PASS: R07 review status, 13 PDF pages, 361 cuts/101 stocks, 80 column IDs, 40 cost rows, form fields and local links.')

rab=PdfReader(OUT/"METTA-R07-RAB-lengkap.pdf")
rabtext="\n".join(p.extract_text() for p in rab.pages)
assert len(rab.pages)==9
for expected in ["269.719.729","90.307.093","179.412.636","240.204.729","DRAF UNTUK PEMERIKSAAN","SUBTOTAL KG DAN BATANG PER PROFIL","SUBTOTAL KG DAN ALOKASI BATANG PER KOMPONEN","3.282,5","9.570,466"]:assert expected in rabtext,expected
print("PASS: RAB PDF 9 pages and full/base cost reconciliation.")
