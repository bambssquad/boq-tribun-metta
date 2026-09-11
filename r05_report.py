import json
from pathlib import Path
ROOT=Path(__file__).parent
def build():
 d=json.loads((ROOT/'assets/r05/boq.json').read_text(encoding='utf-8'));study=d['study'];audit=d['stock_audit'];p=study['procurement'];plate=d['plate_stock']
 def num(v,n=2):return f"{v:,.{n}f}".replace(',','_').replace('.',',').replace('_','.')
 def rp(v):return 'Rp '+num(v,0)
 names={'model':'2,3 mm / model','h20':'2,0 mm / studi','h16':'1,6 mm / studi'}
 lines=['# METTA — verifikasi batang, kilogram dan RAB 11 September 2026','',
 'Status: perbandingan anggaran dan penyaringan awal struktur. Belum menjadi desain pelaksanaan yang telah memenuhi seluruh pemeriksaan standar.','',
 '## Keputusan yang digunakan','',
 '- Toggle 1,6 / 2,0 / 2,3 mm berlaku pada seluruh hollow 50×100: kolom, balok, pengaku, bracing dan usulan penyangga tangga. Dimensi luar, posisi, panjang potong dan jumlah tempat duduk tetap.',
 '- Model Revit masih 2,3 mm. Versi 1,6 dan 2,0 mm adalah skenario perbandingan, belum diterapkan ke model native.',
 '- Ukuran stok pelat sambungan 6 mm adalah 120×240 cm. Potongan kupingan 90×120 mm dan buhul 200×200 mm tetap.','',
 '## Mengapa 54 batang di Excel berbeda dari 101 di web','',
 'Lima baris hollow 50×100 pada Excel berjumlah 1.620 kg. Dibagi asumsi 30 kg/batang menghasilkan 54 batang. Dengan massa katalog 32,5 kg/batang, nilainya 49,85 batang ekuivalen. Keduanya belum membuktikan jumlah batang yang dapat dipotong menjadi seluruh anggota model.',
 '', '| Lingkup | Potongan | Panjang bersih | Stok 6 m bila dipotong terpisah | Berat pembelian 2,3 mm |','|---|---:|---:|---:|---:|']
 for row in audit['scopes']:
  title={'native':'Rangka dan kolom Revit','stair_proposal':'Penyangga tangga usulan','combined':'Seluruhnya, sisa potong dipakai bersama'}[row['scope']]
  lines.append(f"| {title} | {row['cut_count']} | {num(row['cut_length_m'],3)} m | {row['stock_count']} | {num(row['purchase_kg'])} kg |")
 lines+=['','97 + 7 menjadi 101 saat dipotong bersama; sisa batang dari kelompok pertama digunakan untuk potongan kelompok lain. Angka 101 adalah solusi pola potong yang layak, bukan bukti optimum global. Sebanyak 361 ID potongan unik telah diperiksa. Tidak ada geometri RHS duplikat persis atau pengaku memanjang segaris yang menumpuk pada arsip geometri yang direkonsiliasi.',
 '', '| Komponen | Potongan | Panjang model | Kg bersih penampang 2,3 mm | Kg pembelian teralokasi | Kg Excel |','|---|---:|---:|---:|---:|---:|']
 for r in audit['components']:
  excel='Tidak terpisah' if r['source_kg'] is None else num(r['source_kg'],0)+(' (40×40×2)' if r['id']=='X06' else '')
  lines.append(f"| {r['name']} | {r['cut_count']} | {num(r['length_m'],3)} m | {num(r['net_section_kg'])} | {num(r['purchase_allocated_kg'])} | {excel} |")
 lines+=['','Perbedaan utama adalah pengaku longitudinal: Excel 416 kg, sedangkan 45 anggota model memiliki panjang 226,069 m dan massa penampang bersih sekitar 1.162,78 kg. Sebanyak 65 balok silang dihitung terpisah. Bracing Excel memakai 40×40×2 mm, sedangkan bracing model aktif memakai 50×100×2,3 mm. Penyangga tangga 116 potongan masih usulan tambahan dan diberi label tersebut.',
 '','Berat bersih penampang memakai dimensi luar dan sudut membulat; berat pembelian memakai massa katalog stok. Nilai ini tidak boleh dicampur saat mengonversi kg menjadi jumlah batang. Berat timbang, sertifikat dan tebal aktual produk belum tersedia.','',
 '## Perbandingan tebal seluruh hollow 50×100','',
 '| Tebal | Jumlah stok | Kg/batang 6 m | Total kg pembelian | Harga/batang untuk anggaran | Dasar |','|---|---:|---:|---:|---:|---|']
 for key in ['h16','h20','model']:
  v=p['variants'][key];lines.append(f"| {num(v['thickness_mm'],1)} mm | {v['stock_count']} | {num(v['stock_kg'])} | {num(v['purchase_kg'])} | {rp(v['stock_price'])} | {v['price_basis']} |")
 lines+=['','Untuk 1,6 mm, massa 22,61 kg merupakan interpolasi katalog 1,5 dan 1,8 mm. Harga/kg memakai tarif 2,3 mm dalam Excel. Harga tersebut belum menjadi harga pemasok 1,6 mm. Untuk 2,0 dan 2,3 mm, massa dan harga berasal dari katalog SMS Perkasa yang menampilkan tanggal harga 27 Agustus 2026, dibaca 11 September 2026.','',
 '| Versi | Upah/jasa | Material | Total tanpa pelengkap | Total dengan pelengkap |','|---|---:|---:|---:|---:|']
 for key in ['h16','h20','model']:
  r=next(x for x in d['comparison'] if x['case']==key and x['basis']=='purchase' and not x['extras']);full=next(x for x in d['comparison'] if x['case']==key and x['basis']=='purchase' and x['extras'])
  lines.append(f"| {names[key]} | {rp(r['labor'])} | {rp(r['material'])} | {rp(r['total'])} | {rp(full['total'])} |")
 lines+=['','Semua total sebelum overhead, laba dan pajak tambahan. Pelengkap proyek Rp 29.515.000 mencakup backing/hardware, antiselip, clear coat, tekuk, transportasi, alat angkat, perancah, pengukuran, proteksi dan cadangan pemeriksaan desain/tumpuan. Alat kerja dan kawat las mengikuti pembagian biaya sumber; listrik disediakan METTA. Perubahan desain sambungan atau penguatan dapat mengubah biaya tersebut.','',
 '## Pelat sambungan: lembar 120×240 cm','',
 '- Stok: 5 lembar × 1,2 m × 2,4 m × 0,006 m × 7.850 kg/m³ = 678,24 kg teoritis.',
 '- Potongan tetap: 464 kupingan tangga + 548 kupingan rangka berukuran 90×120 mm, serta 40 buhul 200×200 mm; total 1.052 bagian.',
 f"- Luas potongan {num(plate['net_area_m2'],4)} m²; berat bersih {num(plate['net_kg'],3)} kg sebelum lubang. Berat beli mencakup seluruh sisa lembar sekali.",
 '- Lima lembar dibuktikan dengan pola penempatan. Batas tepi 10 mm, celah potong 3 mm, semua bagian berada dalam lembar dan tidak bertumpuk.',
 '- Nilai lama 700 kg menggunakan 5 × 140 kg katalog. Untuk stok tepat 1200×2400 mm, massa dihitung ulang menjadi 678,24 kg; tarif/kg tetap dari Excel. Ukuran buhul tidak diganti menjadi ukuran lembar.',
 '- Berkas pola pelat dan pola batang tersedia sebagai CSV; berat batang dicantumkan hanya sekali per stok agar penjumlahan tidak berulang.','',
 '## Audit sumber model','',
 '- Revit 2027: 385 elemen dibaca, termasuk 175 framing, 165 kolom/tiang railing, 30 dek dan 15 papan pinus. Seluruh 165 ID RHS dan panjang potongnya cocok dengan R04.',
 '- SHA256 model tersimpan sama dengan checkpoint R04. Ekspor IFC baru gagal transaksi; geometri arsip yang direkonsiliasi dan registri native tetap disebut sebagai sumber.',
 '- Luas dek 82,345049121 m². Dua elemen 1686791 dan 1686827 mengembalikan luas nol; tidak diberikan luas fiktif.',
 '- Pelat tangga 176 bagian dan penutup 310 bagian memakai registri native R04. Sebagian penyangga dan detail sambungan masih usulan anggaran.',
 '- Family 10 rail horizontal masih bernama M_W Shapes dan menyimpan properti profil lama. Beberapa properti A/W kolom juga lama; biaya memakai panjang, penampang dan massa katalog yang dijelaskan, bukan berat family tersebut.','',
 '## Batas penyaringan struktur','',
 'Asumsi: E 200.000 MPa, Fy 235 MPa, massa jenis 7.850 kg/m³, radius luar 2t dan radius dalam t. Beban mati 1,5 kN/m², hidup 5 kN/m², titik 1,334 kN. Beban merata dan titik diperiksa sebagai alternatif bersama beban mati. Kombinasi gravitasi 1,2D+1,6L; batas lendutan L/360. Tebal 93% nominal hanya sensitivitas, bukan toleransi produk yang telah dibuktikan.',
 '','| Tebal nominal | Rasio lentur pengaku, 2 m | Rasio lentur balok silang | Kesimpulan terbatas |','|---|---:|---:|---|']
 for key in ['h16','h20','model']:
  v=p['variants'][key];j=v['joist_checks'][1];b=v['bearer_checks'][1];conclusion='Balok silang melewati batas kasus' if not b['passes_screen'] else 'Lolos kasus batang ini; belum membuktikan rangka'
  lines.append(f"| {num(v['thickness_mm'],1)} mm | {num(j['bending_ratio'],3)} | {num(b['bending_ratio'],3)} | {conclusion} |")
 lines+=['','Pengaku memakai lebar tributari 250 mm dan bentang minimal 2 m. Balok silang diuji bentang 1.060 mm dengan lebar tributari 1,77 m. Tumpuan dan pengekangan lateral disimpulkan dari geometri untuk studi; keduanya harus dibuktikan pada detail. Kapasitas kolom hanya dihitung untuk sensitivitas tekan murni K=1 dan K=2, tanpa rasio kelulusan karena gaya rangka belum ditentukan.',
 '',study['conclusion'],'',
 'Belum selesai: analisis rangka tiga dimensi, stabilitas/goyang, gempa, getaran akibat aktivitas serempak, diafragma, pelat/tapak lokal, dinding hollow pada reaksi, las/baut, angkur, transfer gaya melalui base plate/karet, dan kapasitas beton LT4. Data sertifikat baja, tebal aktual, mutu beton serta tulangan dibutuhkan untuk menutup pemeriksaan tersebut.','',
 '## Koreksi terhadap Excel sumber','',
 '- Subtotal upah I32 dan material J32 berhenti di baris 30, sehingga cat pada baris 31 terlewat. Rekap sumber lengkap: upah Rp 62.143.000, material Rp 156.653.686, total Rp 218.796.686.',
 '- Label paket baut + mur + ring dipecah supaya tidak ditafsirkan ganda. Tangga memakai 488 baut, 488 mur dan 976 ring; rangka 693 baut, 693 mur dan 1.386 ring masih berdasarkan usulan sambungan.',
 '- Karet mengikuti 80 titik dudukan. Pinus mengikuti volume 1,197016252 m³, menjadi 74,813516 m bersih dan 82,294867 m pembelian dengan sisa 10%.',
 '- Cat mengikuti luas estimasi 626,0562 m². Nilai paket Excel Rp 28.885.500 dinormalisasi menjadi tarif/m²; penipisan dinding hollow tidak menurunkan luas permukaan cat.',
 '- Angkur 32 buah M10 pada Excel diganti cadangan biaya ikatan beton karena jumlah dan kapasitasnya belum ditetapkan.','',
 '## Sumber primer','',
 'SNI 1727:2020 menjadi acuan beban; SNI 1729:2020 mengadopsi AISC 360-16 untuk baja struktural. SNI 7971:2013 digunakan bila produk/sistem berada dalam ruang lingkup baja canai dingin. Jalur standar harus mengikuti spesifikasi produk, bukan tebal saja. Gempa dan beton juga memerlukan SNI 1726:2019 serta SNI 2847:2019. Studi ini tidak menyatakan seluruh persyaratan tersebut telah dipenuhi.','']
 lines += [f"- [{x['name']}]({x['url']})" for x in study['sources']]
 lines += ['','Tidak ada pemasok yang dihubungi dan tidak ada pembelian yang dilakukan.']
 (ROOT/'assets/r05/analisis-R05.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
if __name__=='__main__':build()
