from pathlib import Path
from bs4 import BeautifulSoup
import json,html
ROOT=Path(__file__).parent
def build(dist):
 p=dist/'tools.html';s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 old=s.select_one('#pelaksanaan')
 old.clear();old.append(BeautifulSoup('''<p class="eyebrow">JADWAL / PELAKSANAAN</p><h2>Timeline pelaksanaan.</h2><p>Jadwal awal berupa estimasi. Edit nama tahap, tanggal mulai dan durasi; perubahan tersimpan pada perangkat ini.</p><div class="plan-controls"><label>Mulai proyek <input id="plan-start" type="date"></label><label>Hari kerja <select id="plan-week"><option value="5">Senin–Jumat</option><option value="6">Senin–Sabtu</option></select></label><div role="group" aria-label="Tampilan jadwal"><button data-plan-view="both" aria-pressed="true">Keduanya</button><button data-plan-view="cards" aria-pressed="false">Kartu</button><button data-plan-view="gantt" aria-pressed="false">Gantt</button></div><button id="plan-reset">Reset estimasi</button></div><p id="plan-summary" aria-live="polite"></p><div id="plan-card-panel"><div class="plan-arrows"><span>Geser / scroll untuk menelusuri tahapan</span><button id="plan-prev" aria-label="Tahap sebelumnya">←</button><button id="plan-next" aria-label="Tahap berikutnya">→</button></div><div id="plan-cards" tabindex="0" aria-label="Kartu tahapan pelaksanaan"></div></div><div id="plan-gantt-panel"><p>Geser batang Gantt untuk mengubah tanggal mulai. Gunakan tombol panah saat batang dipilih, atau edit tanggal pada kartu. Tahap berikutnya tetap; tumpang tindih menunjukkan pekerjaan paralel.</p><div id="plan-gantt" tabindex="0" aria-label="Diagram Gantt pelaksanaan"></div></div><p class="small">Durasi dalam hari kerja; hari libur nasional dan cuti proyek belum dikurangi. Jadwal dapat diubah setelah akses lokasi dan ketersediaan material disepakati.</p>''','html.parser'))
 # Remove the obsolete duplicated heading while preserving the technical method.
 for h in s.select('#metode-perakitan h2'):
  h.clear();h.string='Metode perakitan'
 data=json.loads((dist/'assets/r04/data.json').read_text(encoding='utf-8'))
 lines=[]
 for r in data['rows']:
  if not r.get('supplier'):continue
  source=data['sources'][r['source']][1]
  lines.append('<tr><td>'+r['code']+'</td><td>'+html.escape(r['name'])+'</td><td>'+str(r['qty'])+' '+r['unit']+'</td><td>Rp '+f"{r['price']:,.0f}".replace(',','.')+'</td><td><a href="'+html.escape(source)+'" target="_blank" rel="noopener">'+html.escape(r['supplier'])+'</a></td></tr>')
 quick=BeautifulSoup('<section id="fastener-rab"><h3>Baut, mur, ring dan sekrup — RAB R04</h3><p>Harga dasar estimasi, bukan penawaran pemasok. Semua item berikut sudah masuk total RAB lengkap; tidak ditambahkan kembali ke kalkulator kuantitas di bawah.</p><div class="tw"><table><thead><tr><th>Kode</th><th>Jenis / ukuran</th><th>Jumlah beli</th><th>Harga satuan dasar</th><th>Pemasok</th></tr></thead><tbody>'+''.join(lines)+'</tbody></table></div><p><a href="r04.html#rab"><b>Edit harga dan unduh RAB lengkap beserta spesifikasi pemasok ↗</b></a></p><p>Ikatan beton tetap M17 dan hardware railing/backing tetap M22 berupa provisional sum; tidak dibuat jumlah baut fiktif sebelum detail sambungan ditetapkan.</p></section>','html.parser')
 s.select_one('#anggaran').select_one('h2').insert_after(quick)
 css=s.new_tag('link',rel='stylesheet',href='assets/execution-timeline.css');s.head.append(css)
 js=s.new_tag('script',src='assets/execution-timeline.js');s.body.append(js)
 p.write_text(str(s),encoding='utf-8')
 for ext in ['css','js']:(dist/'assets'/('execution-timeline.'+ext)).write_bytes((ROOT/('execution_timeline.'+ext)).read_bytes())
