from pathlib import Path
from bs4 import BeautifulSoup
import re
ROOT=Path(__file__).parent
def build(dist):
 p=dist/'r04.html';s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 s.select_one('#penawaran-r04 h2').string='METTA — rekap anggaran.'
 box=BeautifulSoup('''<section id="client-offer"><p class="eyebrow">DOKUMEN KOMERSIAL</p><h2>Penawaran & termin pembayaran.</h2><p>Isi identitas, ketentuan dan termin. Nilai penawaran mengikuti lingkup terpilih. Persentase biaya dan termin tersimpan pada perangkat ini.</p><div id="offer-fields"></div><h3>Termin pembayaran</h3><div class="table-wrap"><table class="offer-term-table"><thead><tr><th>Tahap / syarat pembayaran</th><th>Persentase</th><th>Nominal</th><th></th></tr></thead><tbody id="offer-terms"></tbody></table></div><div class="downloads"><button id="offer-add-term">Tambah termin</button><button id="offer-default-terms">Termin 30 / 40 / 30</button></div><p id="offer-term-total" aria-live="polite"></p><div class="downloads"><button id="offer-pdf">Unduh penawaran + lampiran PDF</button></div><p class="small">A4 potret. Pada dialog cetak, pilih Simpan sebagai PDF; nonaktifkan header/footer bawaan browser untuk hasil bersih.</p></section>''','html.parser')
 s.select_one('#penawaran-r04').insert_after(box)
 controls=BeautifulSoup('''<div class="offer-scope-controls"><label>Lingkup penawaran <select id="offer-scope"><option value="all">Semua pekerjaan</option><option value="material">Material</option><option value="labor">Upah jasa</option><option value="custom">Pilih kategori sendiri</option></select></label><div id="offer-scope-categories" hidden></div><div class="offer-scope-rates"><label>Overhead (%) <input id="offer-scope-overhead" type="number" min="0" step="0.01"></label><label>Laba (%) <input id="offer-scope-profit" type="number" min="0" step="0.01"></label><label>Pajak (%) <input id="offer-scope-tax" type="number" min="0" step="0.01"></label></div><p id="offer-scope-summary" aria-live="polite"></p><p class="small">Upah jasa mencakup fabrikasi, pemasangan, tekuk, cat dan kayu. Material tidak mencakup bahan habis pakai atau logistik; gunakan kategori pilihan untuk menggabungkannya. Persentase biaya dan termin disimpan per lingkup.</p></div>''','html.parser')
 s.select_one('#offer-fields').insert_before(controls)
 btn=s.new_tag('button',id='offer-excel');btn.string='Unduh Excel penawaran';s.select_one('#offer-pdf').insert_before(btn)
 scope_script=s.new_tag('script',src='assets/offer-scope.js');s.select_one('script[src="assets/r04/app.js"]').insert_before(scope_script)
 (dist/'assets/offer-scope.js').write_bytes((ROOT/'offer-scope.js').read_bytes())
 preview=BeautifulSoup('<details id="offer-preview-panel" open><summary>Preview layout penawaran & lampiran</summary><p class="small">Preview mengikuti isi form dan termin di atas. Geser untuk melihat seluruh lembar. Pemisahan halaman akhir mengikuti dialog cetak.</p><div class="offer-preview-scroll" tabindex="0" aria-label="Preview dokumen, geser untuk melihat lembar"><div id="offer-preview"></div></div></details>','html.parser')
 s.select_one('#client-offer').append(preview)
 output=s.new_tag('div',id='offer-print',attrs={'aria-hidden':'true'});s.body.append(output)
 css=s.new_tag('link',rel='stylesheet',href='assets/client-offer.css');s.head.append(css)
 # Reuse the document rules for preview; exclude print-only page visibility.
 source=(ROOT/'client-offer.css').read_text(encoding='utf-8')
 rules=source[source.index(' .quote-head'):].rsplit('}',1)[0]
 def scope(m):
  selectors=','.join(x.strip().replace('#offer-print','#offer-preview') if '#offer-print' in x else '#offer-preview '+x.strip() for x in m[1].split(','))
  return selectors+'{'+m[2]+'}'
 preview_style=s.new_tag('style');preview_style.string=re.sub(r'([^{}]+)\{([^{}]*)\}',scope,rules).strip()+'\n#offer-preview-panel{margin-top:28px}#offer-preview-panel summary{font-size:20px;font-weight:600;padding:16px 0;cursor:pointer}.offer-preview-scroll{overflow:auto;max-height:80vh;background:#e8e8e8;padding:20px;border:1px solid #bbb;border-radius:16px}#offer-preview{display:block;width:210mm;padding:14mm;background:#fff;color:#111;font:9pt/1.35 Arial,sans-serif;box-sizing:border-box;box-shadow:0 4px 20px #0002}#offer-preview *{box-sizing:border-box}#offer-preview .quote-cover{min-height:269mm}#offer-preview .quote-appendix{margin-top:14mm;padding-top:14mm;border-top:1px dashed #aaa}@media print{#offer-preview-panel{display:none!important}}';s.head.append(preview_style)
 js=s.new_tag('script',src='assets/client-offer.js');s.select_one('script[src="assets/r04/app.js"]').insert_before(js)
 s.select_one('#print').string='Penawaran + lampiran / PDF'
 s.select_one('#json').string='Simpan data RAB (JSON)'
 p.write_text(str(s),encoding='utf-8')
 for ext in ['js','css']:(dist/'assets'/('client-offer.'+ext)).write_bytes((ROOT/('client-offer.'+ext)).read_bytes())
