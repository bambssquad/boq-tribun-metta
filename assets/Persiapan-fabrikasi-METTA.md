# METTA — persiapan fabrikasi, belum terbit untuk produksi

## Revisi model 3D

Enam belas diagonal diberi Mark X01-A sampai X08-B. Titik bawah diubah dari +18 menjadi +150 mm terhadap LT4; titik atas tetap +2350 mm. Tujuannya memberi ruang dari zona dudukan. Potongan C-C telah diperiksa secara visual. Ini koreksi koordinasi, bukan ukuran sambungan yang sudah dihitung. Delapan pasangan dikelompokkan sebagai assembly koordinasi; jangan mengelas kedua diagonal pada persilangan hanya karena berada dalam satu assembly.

Daftar potong optimal diperbarui dari parameter model sesudah perubahan: 161 framing memerlukan minimum 75 batang stok 6 m untuk input studi ini. Panjang potongan 415.239 mm, kerf 483 mm, sisa 34.278 mm. Sisa termasuk kerf 7,725%. Hasil sebelumnya 7,389% sudah digantikan. Kolom, railing, plat, trimming stok dan allowance sambungan belum termasuk.

## Ketentuan dari web Bam

Sumber: https://bambssquad.github.io/boq-tribun-metta/ , salinan proyek dengan DATA.rev 9056af5e6b. Pembacaan daring ulang gagal; ketentuan di bawah dibaca dari salinan yang sudah tersimpan.

| Detail web | Isi sumber | Perlakuan pada revisi |
|---|---|---|
| Tumpuan | Base 150×150×8, karet 10; duduk lepas, tanpa angkur pelat lantai | Pertahankan prinsip tanpa pengeboran lantai; verifikasi reaksi dan geser/angkat melalui jalur ikatan kolom |
| D1 balok-kolom | 2 M12 grade 4.6 + pelat siku 6, atau las a=4 dua kali 80 | Pilihan detail harus sesuai gaya dan dinding RHS; belum instruksi produksi |
| D2 bracing-kolom | Buhul 6 mm 200×200; las a=4 dua sisi 40 | Web semula untuk bracing 40×40×2, kini model 50×100×2,3; tidak bisa langsung dianggap detail lolos |
| D3 strut-beton | Pelat 6, 2 dynabolt M10, kedalaman 80 | Hanya ke kolom beton. Produk, tulangan, tepi, kapasitas dan beban masih harus diverifikasi |
| D4 railing-dek | Las a=4 keliling | Dek berkurang 8 menjadi 4 mm; periksa transfer momen railing ke rangka, bukan plat saja |

Istilah las a=4 pada web perlu dipastikan: tebal tenggorokan atau panjang kaki las. Jangan menerjemahkannya diam-diam ke spesifikasi lain. Tidak ada gusset, lubang angkur atau simbol las final yang ditambahkan atas dasar angka web saja.

## Data yang ditunggu

Bam menyatakan spesifikasi material sudah dikonfirmasi dan akan memberikan sertifikat. Dokumen belum diterima pada saat pembaruan ini. Perlu tebal dasar bordes tanpa motif, standar/grade hollow, tebal aktual dan sertifikat yang terkait material yang dibeli. Untuk ikatan kolom beton diperlukan data struktur eksisting dan verifikasi insinyur struktur. Gambar arsitektur dan BOQ tidak menyediakan kapasitas tersebut.

Model dan daftar potong boleh dipakai untuk koordinasi dan estimasi. Jangan mulai pemotongan, pengelasan atau pengeboran dari paket ini sebelum detail serta perhitungan diselesaikan.
