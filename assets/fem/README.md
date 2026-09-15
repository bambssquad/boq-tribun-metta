# METTA - FEM rangka primer tersambung

Ini studi elastis linier 3D dengan enam derajat kebebasan per simpul. Implementasi Python memakai matriks balok Euler-Bernoulli 12 x 12, kekakuan aksial EA/L, torsi Saint-Venant GJ/L, dan dua sumbu lentur. Solver sparse langsung memakai penskalaan diagonal. Tidak ada weak spring atau penambahan tumpuan otomatis saat matriks singular.

## Lingkup dan batas

V1 berasal dari 245 batang RHS native R04. V2 Dasar mengambil native yang dipertahankan dan 54 batang infill R08 selebar 1.400 mm. A/C menambahkan jalur semua 30 tapak melalui 60 girder B02 yang sudah dihitung dalam RAB, 40 riser lap dan dukungan per tier. SHS B03 ditransfer sebagai balok sederhana tanpa kekakuan global. Luas A/C mencakup tambahan 5.999915 m² tapak; Dasar tidak memasukkan beban tangga sehingga bukan perbandingan luas identik. Matriks seluruh geometri singular: 14 batang V1 dan 6 batang V2 tidak memiliki jalur sambungan geometris ke kolom. `excludedSourceIds` mencatat setiap batang tersebut. Submodel yang dihitung hanya jaringan terhubung ke kolom. `grossDeckAreaM2`, `areaM2`, dan `excludedTributaryAreaM2` membedakan seluruh dek, area yang membebani submodel, dan area yang terlewat.

Sambungan dalam jarak sumbu 110 mm diidealkan kaku penuh, termasuk eksentrisitas. Transformasi offset eksak memakai u_slave = u_master + theta cross r. Node pada sumbu yang berjarak kurang dari 5 mm disatukan untuk menghindari elemen numerik sangat pendek; kedua ujung sumber tetap. Semua kontak ini tercantum di `rigidOffsets`. Kedekatan dua solid bukan bukti las atau sambungan: detail sambungan tetap perlu diperiksa insinyur. Kaki kolom dianggap jepit penuh untuk skenario utama, yaitu perkiraan kekakuan atas. Ini bukan bukti lantai atau angkur dapat memberi penjepitan. Sensitivitas `boundarySensitivity` membebaskan rotasi kaki namun tetap menahan semua translasi; skenario ini juga memerlukan angkur, bukan kaki bebas geser/angkat.

Penampang sudut tajam RHS 50x100 memakai tebal nominal 1.6, 2.0, 2.3 mm, E=200000 MPa dan nu=0.3. Orientasi batang horizontal tinggi 100 mm vertikal; kolom lebar 50 mm global X, tinggi penampang 100 mm global Y. Tebal efektif, radius sudut, variasi mutu, tekuk lokal, sambungan dan korosi tidak dihitung. V1/V2 Dasar mengecualikan tangga. A/C memasukkan B02 dan semua tapak, tetapi anggota sekunder SHS, pagar dan mesh tidak memberi kekakuan global; perubahan SHS tidak boleh diklaim mengubah hasil global ini.

Beban D=1.5 kPa dan L=5 kPa adalah skenario yang dipertahankan dari studi R06. D merupakan allowance total termasuk berat sendiri, sehingga berat rangka tidak ditambah lagi. Empat kasus D, L, D+L, 1.2D+1.6L tersedia untuk tiap versi dan tebal. Nilai 1.2D+1.6L hanya satu kombinasi gravitasi, bukan seluruh kombinasi desain. Permukaan dek disatukan per elevasi agar area tumpang tindih tidak dihitung dua kali, kemudian dikurangi footprint beton dengan celah 3 mm. Luas geometris ini tidak menggantikan kuantitas RAB. Permukaan dek dipotong pada batas tributari tengah antar batang yang menyentuh dek (sumbu sekitar 54 mm di bawah permukaan), dengan ukuran sel sepanjang batang maksimum 100 mm pada keluaran utama. Pelat penutup kecil tanpa batang kontak menggunakan sumbu terdekat. Gaya dan kopel dari centroid sel diteruskan ke simpul rangka agar gaya total dan momen global tekanan tetap persis. Transfer ini mengasumsikan pelat dapat memindahkan beban dan kopel tersebut; kekuatan/kekakuan pelat tidak diperiksa. Sensitivitas sel 400, 200 dan 100 mm tersedia di manifest. Konvergensi numerik tidak membuktikan jalur beban atau sambungan aktual; jangan pakai hasil ini untuk fabrikasi.

Tidak termasuk P-delta, nonlinearitas, tekuk global/lokal, kekuatan penampang, sambungan/angkur, gempa, angin, getaran, pondasi atau kapasitas beton. Tidak ada status aman atau lulus SNI. Hasil adalah studi kondisional, bukan analisis SAP2000/Tekla, dan bukan sertifikasi struktur.

## Koreksi sumbu dan diskretisasi

Empat balok diagonal dekat beton dahulu diambil dari bounding box sebagai batang lurus. Hal itu memutus hubungan numerik dan menghasilkan angka sekitar 24 mm. Sumbu sekarang direkonstruksi dari panjang potong, panjang sistem dan grid kolom; empat pengaku lama juga memakai offset ujung native. Bukti tersimpan dalam `data/member-axis-corrections.json`. Perbaikan model hitung ini bukan bukti bangunan pernah mengalami deformasi tersebut. Bounding box empat balok cocok dalam 0.022 mm; empat pengaku memakai panjang/offset audit dengan selisih terhadap kotak visual lama maksimum 2.72 mm.

RHS 2.3 mm, D+L=6.5 kPa, asumsi tumpuan seperti dijelaskan:

| Model | Sel 100 mm (tampilan) | Sel 50 mm (pembanding) | Perubahan |
|---|---:|---:|---:|
| V1 primer | 2.0802 mm | 2.0793 mm | 0.0403% |
| V2 Dasar primer | 1.2665 mm | 1.2696 mm | 0.2417% |
| V2 A termasuk dua tangga | 1.2674 mm | 1.2705 mm | 0.2401% |
| V2 C termasuk dua tangga | 1.2656 mm | 1.2687 mm | 0.2479% |

Semua 48 kasus memakai sel 100 mm. Ini sensitivitas numerik terhadap pembagian beban, bukan pembuktian kapasitas. Riser lap berada di luar sisi tapak supaya tidak menembus pelat; sambungan las sisi, cope antar batang dan kapasitas dinding RHS tetap perlu detail.

## Konvensi keluaran

Panjang mm, gaya N, momen Nmm, rotasi rad. Sumbu lokal x dari a ke b; z mengikuti global Z sejauh mungkin (kolom menggunakan global Y); y=z cross x. `i` dan `j` adalah gaya nodal lokal [N,Vy,Vz,T,My,Mz] di kedua ujung, sesuai matriks elemen. Scalar tiap komponen memilih nilai ujung dominan dengan tanda gaya ujung asli. Ini envelope gaya ujung, bukan diagram internal sepanjang batang kontinu. Deformasi display dapat dibesarkan tetapi data tetap mm aktual. Animasi perubahan faktor skala bukan analisis dinamik.

Model geometri tersedia dalam `model.json.gz`. Dua belas file `solution-v*-h*.json.gz` dikompresi gzip deterministik (mtime=0) dan berisi hasil untuk tekanan 1 kPa. Manifest `results.json` memuat 48 kasus, `solutionId` dan `resultScale`. Hasil perpindahan, gaya dan reaksi dikalikan faktor ini; summary kasus sudah diskalakan. Ini superposisi elastis linier eksak, bukan interpolasi hasil ketebalan.

## Reproduksi

Manifest menyimpan hash sumber solver dan geometri. `check_fem.py` menolak hasil lama bila sumber berubah; jalankan generator kembali setelah revisi geometri.

Dependensi: Python, numpy, scipy, shapely; sumber r04_model.py dan data R04/R08 di repositori.

```
python fem_model.py
python check_fem.py
```

Uji mencakup enam rigid-body modes, simetri, kantilever aksial/torsi/lentur dua arah, balok sendi-rol beban titik tengah, transformasi offset kaku, penolakan mekanisme bebas, keseimbangan gaya dan momen seluruh 48 kasus, area-tekanan, tren tebal dan perbedaan geometri V1/V2. Uji analitik membuktikan formulasi solver; tidak membuktikan asumsi sambungan dan beban bangunan.

## Referensi primer metode

- TU Delft, Euler-Bernoulli beam elements: https://interactivetextbooks.citg.tudelft.nl/computational-modelling/structural_linear/euler_bernouilli.html
- numgeo, beam formulation and local/global transformation: https://j-machacek.github.io/numgeo/theory/elements/beam.html
- TU Delft, 3D Euler beam stiffness research: https://pure.tudelft.nl/ws/portalfiles/portal/55207149/6.2019_3272.pdf

Referensi metode diperiksa pada 15 September 2026. Numgeo menjelaskan pula deformasi geser Timoshenko; implementasi ini memakai batas Euler-Bernoulli tanpa deformasi geser.
