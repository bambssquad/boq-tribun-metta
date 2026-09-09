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

 editor=BeautifulSoup('''<section class="budget-editor"><h3>Edit rincian pekerjaan</h3><div class="downloads"><label>Terapkan ke <select id="budget-target"><option value="offer">Penawaran ini saja</option><option value="main">RAB utama + penawaran</option></select></label><label>Tabel <select id="budget-category"><option>Upah</option><option>Semua</option><option>Material</option><option>Bahan habis pakai</option><option>Peralatan dan logistik</option></select></label><label>Dasar upah <select id="labor-layout"><option value="">Pilih template</option><option value="activity">Rincian aktivitas</option><option value="component">Berat per komponen</option></select></label><button id="budget-add">Tambah pekerjaan</button></div><p>Volume × harga satuan = jumlah. Isi jumlah manual untuk borongan atau nilai kontrak. Template mengganti upah gabungan saja; tekuk, cat dan kayu tetap terpisah. Seluruh kolom dapat diedit. Data kosong dihitung nol dan perlu dilengkapi.</p><datalist id="budget-units"><option>kg</option><option>m²</option><option>unit</option><option>borongan</option><option>hari</option><option>m</option></datalist><div class="table-wrap"><table><thead><tr>'''+''.join('<th>'+x+'</th>' for x in ['Kode','Uraian','Kategori','Volume','Satuan','Harga satuan','Jumlah manual','Pemasok','Spesifikasi','Catatan','Status','Kontak','Dasar harga','kg per satuan','Jumlah','Aksi'])+'''</tr></thead><tbody id="budget-editor-rows"></tbody></table></div><div class="downloads"><label><input id="offer-detail" type="checkbox" checked> Lampiran rincian pekerjaan</label><label><input id="term-detail" type="checkbox"> Termin per pekerjaan</label></div></section>''','html.parser')
 s.select_one('#offer-fields').insert_before(editor)
 for name in ['budget-editor.js','offer-pdf.js']:
  tag=s.new_tag('script',src='assets/'+name);s.body.append(tag);(dist/'assets'/name).write_bytes((ROOT/name).read_bytes())
 tag=s.new_tag('link',rel='stylesheet',href='assets/budget-editor.css');s.head.append(tag);(dist/'assets/budget-editor.css').write_bytes((ROOT/'budget-editor.css').read_bytes())
 import shutil
 shutil.copytree(ROOT/'vendor',dist/'assets/vendor',dirs_exist_ok=True)
 for el in s.select('p.small'):
  if 'dialog cetak' in el.get_text():el.string='PDF A4 diunduh langsung. Rincian mengikuti pilihan tampilan dan nilai penawaran saat ini.'
 p.write_text(str(s),encoding='utf-8')
 for ext in ['js','css']:(dist/'assets'/('client-offer.'+ext)).write_bytes((ROOT/('client-offer.'+ext)).read_bytes())
