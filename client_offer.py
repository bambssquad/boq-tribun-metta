from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent
def build(dist):
 p=dist/'r04.html';s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 s.select_one('#penawaran-r04 h2').string='METTA — rekap anggaran.'
 box=BeautifulSoup('''<section id="client-offer"><p class="eyebrow">DOKUMEN KOMERSIAL</p><h2>Penawaran & termin pembayaran.</h2><p>Isi identitas, ketentuan dan termin. Nilai penawaran mengikuti total RAB lengkap dan tersimpan pada perangkat ini.</p><div id="offer-fields"></div><h3>Termin pembayaran</h3><div class="table-wrap"><table class="offer-term-table"><thead><tr><th>Tahap / syarat pembayaran</th><th>Persentase</th><th>Nominal</th><th></th></tr></thead><tbody id="offer-terms"></tbody></table></div><div class="downloads"><button id="offer-add-term">Tambah termin</button><button id="offer-default-terms">Termin 30 / 40 / 30</button></div><p id="offer-term-total" aria-live="polite"></p><div class="downloads"><button id="offer-pdf">Unduh penawaran + lampiran PDF</button></div><p class="small">A4 potret. Pada dialog cetak, pilih Simpan sebagai PDF; nonaktifkan header/footer bawaan browser untuk hasil bersih.</p></section>''','html.parser')
 s.select_one('#penawaran-r04').insert_after(box)
 output=s.new_tag('div',id='offer-print',attrs={'aria-hidden':'true'});s.body.append(output)
 css=s.new_tag('link',rel='stylesheet',href='assets/client-offer.css');s.head.append(css)
 js=s.new_tag('script',src='assets/client-offer.js');s.select_one('script[src="assets/r04/app.js"]').insert_before(js)
 s.select_one('#print').string='Penawaran + lampiran / PDF'
 p.write_text(str(s),encoding='utf-8')
 for ext in ['js','css']:(dist/'assets'/('client-offer.'+ext)).write_bytes((ROOT/('client-offer.'+ext)).read_bytes())
