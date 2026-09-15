# Perbandingan A/C - dua tangga penuh

Koreksi sumbu native menghilangkan putus sambungan numerik yang menghasilkan angka lama sekitar 24 mm. A/C bukan klaim bahwa penambahan material itu yang menghilangkan 24 mm.

A memakai rangka utama, 40 penghubung riser las, 10 cleat pendek dan dua header ke kolom beton pada landing tengah. C memakai 40 penghubung riser serta lima kotak penopang per tangga (40 kolom, 40 balok, 40 diagonal). Sebanyak 60 girder sisi B02 tetap berasal dari RAB dasar; tidak dihitung dua kali. Seluruh 30 tapak masuk beban A/C, sebesar 5.999915 m². Ini menggantikan percobaan kasar menumpuk seluruh beban flight hanya pada satu landing.

`options-spec.json` merupakan geometri usulan dan input RAB. `analysis.json` berisi tiga tebal RHS, tegangan gross, reaksi angkur (demand saja), pemeriksaan benturan, pemeriksaan SHS lokal serta beban horizontal fiktif 0.2%. Beban horizontal tersebut hanya uji kekakuan elastis orde pertama; bukan analisis langsung AISC, gempa, angin atau P-delta.

## Batas keputusan

- RHS1.6 mendekati Fy235 pada screening tegangan gross gabungan. Nilai di bawah Fy tidak membuktikan kapasitas setelah tekuk lokal/global, reduksi tebal, las dan sambungan.
- Semua kaki (80 kolom utama, infill dan kaki C) mengandalkan kapasitas lantai/angkur yang belum diketahui. Budget angkur tidak membuktikan tumpuan jepit. Pad karet10mm perlu verifikasi tekan dan slip.
- Railing SHS40x40 kantilever1100mm belum memenuhi target lendutan11mm untuk keempat tebal. Kandidat berikutnya A=SHS60x60x2.3; C=pengaku atau distribusi beban pegangan yang dihitung. Kandidat ini belum mengganti gambar/RAB pagar.
- SHS B03 diperiksa lokal sebagai balok550mm dengan tributari115mm dan kasus beban titik1.334kN. Pelat3mm, lipatan, luas kontak beban titik dan sambungan masih membutuhkan pemeriksaan pelat terpisah.
- Las pada riser lap166.7mm dan cleat45mm harus dibuktikan mampu meneruskan momen. Hardware/konsumsi las dalam RAB hanya allowance.
- Analisis stabilitas orde kedua, beban lokasi, gempa/angin, getaran kerumunan dan kapasitas beton belum lengkap. Tidak ada status siap fabrikasi atau aman terverifikasi.

## Reproduksi

```
python geometry_axes.py
python structural-study.py
python fem_model.py
python structural-study.py --analyse
python check_fem.py
node check_fem_viewer.cjs
```

Sumber primer metode dan pemeriksaan tersedia di analysis.json dan assets/fem/README.md. Semua asumsi harus ditinjau sebelum keputusan pelaksanaan.
