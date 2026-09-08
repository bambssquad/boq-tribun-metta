# METTA — arsip desain, BOQ dan penawaran

Web: https://bambssquad.github.io/boq-tribun-metta/

Halaman utama memuat Timeline, Surf, Indeks dan Proyek dalam hitam-putih tanpa musik. Menu membuka model 3D, gambar teknik interaktif, BOQ dan penawaran pada `tools.html`.

## BOQ dan jasa per kg

Buka **Menu → BOQ & biaya**, lalu aktifkan **Hitung jasa per kg**. Tarif awal Rp6.000/kg mencakup jasa fabrikasi dan pemasangan; material dihitung terpisah. Tarif dapat diubah. Menonaktifkan toggle mengeluarkan jasa dari total tanpa mengubah kuantitas atau harga material.

Dasar penagihan adalah berat pembelian: jumlah lonjor dibulatkan × panjang stok × kg/m, ditambah jumlah lembar dibulatkan × luas lembar × kg/m². Sisa potong termasuk sekali melalui jumlah stok. Saat input R02 dan allowance bawaan digunakan: 7.940,076 kg × Rp6.000 = Rp47.640.456 sebelum material, overhead dan pajak. Rincian setiap komponen dapat dibuka di panel jasa. Berat motif bordes belum terukur; sebagian item masih estimasi sebagaimana catatan BOQ.

**Buka template penawaran** menampilkan surat yang dapat diisi nama perusahaan, klien, nomor, tanggal, lingkup dan termin pembayaran. Nilai jasa mengikuti BOQ. Menu Ekspor menyediakan Excel berumus dengan lembar PENAWARAN, REKAP, INPUT, BOQ dan BERAT; sakelar Excel ada di INPUT!B14 (1 aktif, 0 nonaktif) dan tarif di INPUT!B13. PDF dibuat melalui dialog cetak browser.

Harga material yang kosong belum masuk total. Overhead dan pajak adalah input terpisah; tarif Rp6.000/kg bukan harga material. Spesifikasi dan validasi struktur tetap berada dalam lampiran teknis.

## Pengembangan

Gunakan Python 3.12+ dan Node 22+:

```sh
python -m pip install -r requirements.txt
python build_preview.py
python validate.py
node kg_pricing.test.cjs
node lookback.test.cjs
node panzoom.test.cjs
python publish_public.py
```

Commit sumber beserta hasil publikasi. GitHub Pages memakai berkas statis di root. Workflow memeriksa bahwa halaman terbit sesuai hasil build. Generator `src/` dipertahankan; `build_preview.py` menerapkan data model revisi, `kg_pricing.py` menambahkan tarif jasa, dan `lookback.py` membuat halaman arsip terpisah. `data/` mencatat kuantitas dan asal geometri. `assets/technical/` memuat 12 DXF/SVG, PDF gabungan dan ekspor sheet Revit.

Referensi visual: https://tlb.betteroff.studio/. Implementasi interaksi dan konten METTA dibuat terpisah; musik, font komersial dan kode referensi tidak disertakan.

R03: seluruh 12 gambar kini memiliki 136 dimensi CAD dan label LOD 200. Dimensi terdaftar pada assets/technical/dimensions-R03.json; python check_dimensions.py memeriksa entitas CAD, satuan, PDF dan dasar angka. Jalankan python technical.py untuk memperbarui gambar, lalu build_preview.py. URL unduhan R02 dipertahankan agar tautan lama tetap berfungsi; isi dokumennya telah direvisi R03. Geometri dan harga BOQ tetap. Revit menerima anotasi garis/teks native dan skema dimensi pendamping; belum berupa dimensi asosiatif ke model.
