from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent

def build(dist):
 p=dist/'tools.html';s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 b=s.new_tag('button',attrs={'type':'button','data-rab-mode':'labor','aria-pressed':'false'});b.string='RAB Upah';s.select_one('.rab-mode').append(b)
 panel=BeautifulSoup('''<div id="rab-labor-panel" hidden><section id="labor-quote"><h3>RAB Upah / METTA</h3><p>Penawaran terpisah berdasarkan PDF 09 September 2026. Nilai awal Rp50.632.900; seluruh isian dapat diedit dan tersimpan di perangkat ini.</p><div class="lq-controls"><button data-lq-view="table" aria-pressed="true">Tabel</button><button data-lq-view="preview" aria-pressed="false">Preview A4</button><button id="lq-download">Unduh PDF</button><button id="lq-add">Tambah pekerjaan</button><button id="lq-reset">Pulihkan angka PDF</button><strong id="lq-total"></strong></div><div id="lq-table"><div id="lq-fields"></div><p class="lq-hint">Jumlah = volume × upah. Kolom jumlah manual dapat diisi atau dikosongkan untuk hitungan otomatis. Dua baris kayu memakai jumlah asli PDF karena volume yang ditampilkan dibulatkan.</p><div class="lq-scroll"><table><thead><tr><th>No.</th><th>Uraian pekerjaan</th><th>Material</th><th>Volume</th><th>Satuan</th><th>Upah satuan</th><th>Jumlah manual</th><th>Jumlah</th><th>Aksi</th></tr></thead><tbody id="lq-rows"></tbody></table></div></div><div id="lq-preview" hidden></div></section></div>''','html.parser')
 s.select_one('#anggaran').append(panel)
 for name in ['labor-quote.js','labor-quote.css']:
  el=s.new_tag('script',src='assets/'+name) if name.endswith('.js') else s.new_tag('link',rel='stylesheet',href='assets/'+name)
  s.body.append(el);(dist/'assets'/name).write_bytes((ROOT/name).read_bytes())
 p.write_text(str(s),encoding='utf-8')
