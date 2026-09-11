# METTA — verifikasi batang, kilogram dan RAB 11 September 2026

Status: perbandingan anggaran dan penyaringan awal struktur. Belum menjadi desain pelaksanaan yang telah memenuhi seluruh pemeriksaan standar.

## Keputusan yang digunakan

- Toggle 1,6 / 2,0 / 2,3 mm berlaku pada seluruh hollow 50×100: kolom, balok, pengaku, bracing dan usulan penyangga tangga. Dimensi luar, posisi, panjang potong dan jumlah tempat duduk tetap.
- Model Revit masih 2,3 mm. Versi 1,6 dan 2,0 mm adalah skenario perbandingan, belum diterapkan ke model native.
- Ukuran stok pelat sambungan 6 mm adalah 120×240 cm. Potongan kupingan 90×120 mm dan buhul 200×200 mm tetap.

## Mengapa 54 batang di Excel berbeda dari 101 di web

Lima baris hollow 50×100 pada Excel berjumlah 1.620 kg. Dibagi asumsi 30 kg/batang menghasilkan 54 batang. Dengan massa katalog 32,5 kg/batang, nilainya 49,85 batang ekuivalen. Keduanya belum membuktikan jumlah batang yang dapat dipotong menjadi seluruh anggota model.

| Lingkup | Potongan | Panjang bersih | Stok 6 m bila dipotong terpisah | Berat pembelian 2,3 mm |
|---|---:|---:|---:|---:|
| Rangka dan kolom Revit | 245 | 552,301 m | 97 | 3.152,50 kg |
| Penyangga tangga usulan | 116 | 37,837 m | 7 | 227,50 kg |
| Seluruhnya, sisa potong dipakai bersama | 361 | 590,138 m | 101 | 3.282,50 kg |

97 + 7 menjadi 101 saat dipotong bersama; sisa batang dari kelompok pertama digunakan untuk potongan kelompok lain. Angka 101 adalah solusi pola potong yang layak, bukan bukti optimum global. Sebanyak 361 ID potongan unik telah diperiksa. Tidak ada geometri RHS duplikat persis atau pengaku memanjang segaris yang menumpuk pada arsip geometri yang direkonsiliasi.

| Komponen | Potongan | Panjang model | Kg bersih penampang 2,3 mm | Kg pembelian teralokasi | Kg Excel |
|---|---:|---:|---:|---:|---:|
| Kolom tribun | 80 | 133,560 m | 686,96 | 738,95 | 637 |
| Balok tepi tier | 15 | 73,710 m | 379,12 | 409,49 | 416 |
| Pengaku longitudinal dek | 45 | 226,069 m | 1.162,78 | 1.243,32 | 416 |
| Rangka belakang | 4 | 17,396 m | 89,48 | 95,11 | 98 |
| Strut ke kolom beton | 16 | 2,172 m | 11,17 | 11,85 | 53 |
| Bracing X | 20 | 42,388 m | 218,02 | 235,70 | 62 (40×40×2) |
| Balok silang penumpu dek | 65 | 57,006 m | 293,21 | 314,04 | Tidak terpisah |
| Penyangga tangga / usulan | 116 | 37,837 m | 194,61 | 234,03 | Tidak terpisah |

Perbedaan utama adalah pengaku longitudinal: Excel 416 kg, sedangkan 45 anggota model memiliki panjang 226,069 m dan massa penampang bersih sekitar 1.162,78 kg. Sebanyak 65 balok silang dihitung terpisah. Bracing Excel memakai 40×40×2 mm, sedangkan bracing model aktif memakai 50×100×2,3 mm. Penyangga tangga 116 potongan masih usulan tambahan dan diberi label tersebut.

Berat bersih penampang memakai dimensi luar dan sudut membulat; berat pembelian memakai massa katalog stok. Nilai ini tidak boleh dicampur saat mengonversi kg menjadi jumlah batang. Berat timbang, sertifikat dan tebal aktual produk belum tersedia.

## Perbandingan tebal seluruh hollow 50×100

| Tebal | Jumlah stok | Kg/batang 6 m | Total kg pembelian | Harga/batang untuk anggaran | Dasar |
|---|---:|---:|---:|---:|---|
| 1,6 mm | 101 | 22,61 | 2.283,61 | Rp 302.278 | Estimasi: massa interpolasi katalog 1,5/1,8 mm dan harga/kg Excel 2,3 mm; bukan penawaran 1,6 mm. |
| 2,0 mm | 101 | 28,26 | 2.854,26 | Rp 373.900 | Katalog SMS Perkasa, harga tayang 27 Agustus; dibaca 11 September 2026. |
| 2,3 mm | 101 | 32,50 | 3.282,50 | Rp 434.500 | Katalog SMS Perkasa; sama dengan tarif Excel. |

Untuk 1,6 mm, massa 22,61 kg merupakan interpolasi katalog 1,5 dan 1,8 mm. Harga/kg memakai tarif 2,3 mm dalam Excel. Harga tersebut belum menjadi harga pemasok 1,6 mm. Untuk 2,0 dan 2,3 mm, massa dan harga berasal dari katalog SMS Perkasa yang menampilkan tanggal harga 27 Agustus 2026, dibaca 11 September 2026.

| Versi | Upah/jasa | Material | Total tanpa pelengkap | Total dengan pelengkap |
|---|---:|---:|---:|---:|
| 1,6 mm / studi | Rp 62.493.320 | Rp 159.639.227 | Rp 222.132.547 | Rp 251.647.547 |
| 2,0 mm / studi | Rp 65.917.221 | Rp 166.873.018 | Rp 232.790.239 | Rp 262.305.239 |
| 2,3 mm / model | Rp 68.486.661 | Rp 172.993.619 | Rp 241.480.280 | Rp 270.995.280 |

Semua total sebelum overhead, laba dan pajak tambahan. Pelengkap proyek Rp 29.515.000 mencakup backing/hardware, antiselip, clear coat, tekuk, transportasi, alat angkat, perancah, pengukuran, proteksi dan cadangan pemeriksaan desain/tumpuan. Alat kerja dan kawat las mengikuti pembagian biaya sumber; listrik disediakan METTA. Perubahan desain sambungan atau penguatan dapat mengubah biaya tersebut.

## Pelat sambungan: lembar 120×240 cm

- Stok: 5 lembar × 1,2 m × 2,4 m × 0,006 m × 7.850 kg/m³ = 678,24 kg teoritis.
- Potongan tetap: 464 kupingan tangga + 548 kupingan rangka berukuran 90×120 mm, serta 40 buhul 200×200 mm; total 1.052 bagian.
- Luas potongan 12,5296 m²; berat bersih 590,144 kg sebelum lubang. Berat beli mencakup seluruh sisa lembar sekali.
- Lima lembar dibuktikan dengan pola penempatan. Batas tepi 10 mm, celah potong 3 mm, semua bagian berada dalam lembar dan tidak bertumpuk.
- Nilai lama 700 kg menggunakan 5 × 140 kg katalog. Untuk stok tepat 1200×2400 mm, massa dihitung ulang menjadi 678,24 kg; tarif/kg tetap dari Excel. Ukuran buhul tidak diganti menjadi ukuran lembar.
- Berkas pola pelat dan pola batang tersedia sebagai CSV; berat batang dicantumkan hanya sekali per stok agar penjumlahan tidak berulang.

## Audit sumber model

- Revit 2027: 385 elemen dibaca, termasuk 175 framing, 165 kolom/tiang railing, 30 dek dan 15 papan pinus. Seluruh 165 ID RHS dan panjang potongnya cocok dengan R04.
- SHA256 model tersimpan sama dengan checkpoint R04. Ekspor IFC baru gagal transaksi; geometri arsip yang direkonsiliasi dan registri native tetap disebut sebagai sumber.
- Luas dek 82,345049121 m². Dua elemen 1686791 dan 1686827 mengembalikan luas nol; tidak diberikan luas fiktif.
- Pelat tangga 176 bagian dan penutup 310 bagian memakai registri native R04. Sebagian penyangga dan detail sambungan masih usulan anggaran.
- Family 10 rail horizontal masih bernama M_W Shapes dan menyimpan properti profil lama. Beberapa properti A/W kolom juga lama; biaya memakai panjang, penampang dan massa katalog yang dijelaskan, bukan berat family tersebut.

## Batas penyaringan struktur

Asumsi: E 200.000 MPa, Fy 235 MPa, massa jenis 7.850 kg/m³, radius luar 2t dan radius dalam t. Beban mati 1,5 kN/m², hidup 5 kN/m², titik 1,334 kN. Beban merata dan titik diperiksa sebagai alternatif bersama beban mati. Kombinasi gravitasi 1,2D+1,6L; batas lendutan L/360. Tebal 93% nominal hanya sensitivitas, bukan toleransi produk yang telah dibuktikan.

| Tebal nominal | Rasio lentur pengaku, 2 m | Rasio lentur balok silang | Kesimpulan terbatas |
|---|---:|---:|---|
| 1,6 mm | 0,533 | 1,004 | Balok silang melewati batas kasus |
| 2,0 mm | 0,435 | 0,820 | Lolos kasus batang ini; belum membuktikan rangka |
| 2,3 mm | 0,384 | 0,724 | Lolos kasus batang ini; belum membuktikan rangka |

Pengaku memakai lebar tributari 250 mm dan bentang minimal 2 m. Balok silang diuji bentang 1.060 mm dengan lebar tributari 1,77 m. Tumpuan dan pengekangan lateral disimpulkan dari geometri untuk studi; keduanya harus dibuktikan pada detail. Kapasitas kolom hanya dihitung untuk sensitivitas tekan murni K=1 dan K=2, tanpa rasio kelulusan karena gaya rangka belum ditentukan.

Versi 1,6/2,0/2,3 mm adalah perbandingan biaya untuk susunan yang sama. Versi seluruh rangka 1,6 mm tidak lolos kasus penyaringan balok silang pada tebal asumsi 1,488 mm. Tidak satu pun versi dinyatakan memenuhi seluruh pemeriksaan struktur.

Belum selesai: analisis rangka tiga dimensi, stabilitas/goyang, gempa, getaran akibat aktivitas serempak, diafragma, pelat/tapak lokal, dinding hollow pada reaksi, las/baut, angkur, transfer gaya melalui base plate/karet, dan kapasitas beton LT4. Data sertifikat baja, tebal aktual, mutu beton serta tulangan dibutuhkan untuk menutup pemeriksaan tersebut.

## Koreksi terhadap Excel sumber

- Subtotal upah I32 dan material J32 berhenti di baris 30, sehingga cat pada baris 31 terlewat. Rekap sumber lengkap: upah Rp 62.143.000, material Rp 156.653.686, total Rp 218.796.686.
- Label paket baut + mur + ring dipecah supaya tidak ditafsirkan ganda. Tangga memakai 488 baut, 488 mur dan 976 ring; rangka 693 baut, 693 mur dan 1.386 ring masih berdasarkan usulan sambungan.
- Karet mengikuti 80 titik dudukan. Pinus mengikuti volume 1,197016252 m³, menjadi 74,813516 m bersih dan 82,294867 m pembelian dengan sisa 10%.
- Cat mengikuti luas estimasi 626,0562 m². Nilai paket Excel Rp 28.885.500 dinormalisasi menjadi tarif/m²; penipisan dinding hollow tidak menurunkan luas permukaan cat.
- Angkur 32 buah M10 pada Excel diganti cadangan biaya ikatan beton karena jumlah dan kapasitasnya belum ditetapkan.

## Sumber primer

SNI 1727:2020 menjadi acuan beban; SNI 1729:2020 mengadopsi AISC 360-16 untuk baja struktural. SNI 7971:2013 digunakan bila produk/sistem berada dalam ruang lingkup baja canai dingin. Jalur standar harus mengikuti spesifikasi produk, bukan tebal saja. Gempa dan beton juga memerlukan SNI 1726:2019 serta SNI 2847:2019. Studi ini tidak menyatakan seluruh persyaratan tersebut telah dipenuhi.

- [SNI 1727:2020](https://pesta.bsn.go.id/produk/detail/12927-sni17272020)
- [SNI 1729:2020, adopsi AISC360-16](https://pesta.bsn.go.id/produk/detail/12882-sni17292020)
- [SNI 7971:2013; bila standar produk canai dingin berlaku](https://pesta.bsn.go.id/produk/detail/9714-sni79712013)
- [AISC360-16 B4, E3/E7, F7, G5](https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_june-2019_linked.pdf)
- [ICC300-2017 303; pembanding beban tribun](https://codes.iccsafe.org/content/ICC3002017/chapter-3-construction?site_type=public)
- [Katalog hollow50x100x1,6; tanpa harga/sertifikat](https://jualbesi.com/produk/besi-hollow-hitam-50x100x1-6/)
- [Harga dan massa stok pembanding1,5/1,8/2,3mm, 11 September2026](https://www.smsperkasa.com/produk/besi-hollow-hitam)

Tidak ada pemasok yang dihubungi dan tidak ada pembelian yang dilakukan.
