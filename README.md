# METTA — arsip desain, BOQ dan penawaran

R04 (9 September 2026): `r04.html` is the selected all-in budget, with material, consumables, labor, logistics, overhead, profit and configurable output tax. Its purchasing-weight basis drives the Rp6,000/kg service toggle. Net theoretical and catalog purchasing weights have separate ledgers; unmeasured backing and concrete ties remain explicit provisional sums. Connections and stair supports are design proposals, not a fabrication release.

The current 3D projection contains 165 RHS members, 80 columns, 20 diagonals (10 X sets), 176 native stair plate parts and 310 native 2-mm cover parts. R04 overlays use saved Revit IDs/cut-length readbacks and common plate geometry; R03 source snapshots are retained unchanged. Rear/bottom covers are excluded. Four concrete columns are clipped from the 2-mm panel layout with 3-mm clearance. The archive opens on six current R04 CAD/PDF sheets followed by twelve clearly labeled R03 sheets. Revit sheet previews are under `assets/r04/revit/`.

R04 nesting compares 160 deterministic guillotine heuristics with 10-mm trim and 3-mm kerf: eight 3-mm sheets and twenty-six 2-mm sheets for the fixed current part list. This is the best searched arrangement, not a global optimality proof. `check_r04.py` verifies coverage, kerf/trim, stock capacity, native plate/cover dimensions and mass; `check_r04_web.py` verifies published IDs/counts and links. `r04_controller.test.cjs` checks loading, filters, service toggle, complete printing, sheet dialogs, exports and reset. Run these along with the existing validation and interaction tests. Browser visual parity is not asserted.

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

SAP branding: nama lengkap SELARAS ADHI PERKASA tampil pada awal, lalu beralih menjadi SAP ketika scroll dan navigasi; scroll balik mengembalikan nama lengkap. Judul proyek dua baris: ARSIP DESAIN METTA dan (09/2026). Header halaman teknis memakai SAP. Pengujian meliputi wheel, touch, keyboard, menu dan navigasi.
