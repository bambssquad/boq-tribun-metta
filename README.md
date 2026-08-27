# BOQ & RAB Tribun Baja Hollow — Gedung METTA

Satu berkas `index.html` yang berdiri sendiri: gambar kerja, model 3D, spesifikasi,
bill of quantity, RAB, dan daftar potong. Tidak butuh server, database, atau proses build.

## Cara memasang di GitHub Pages

1. Buat repository baru di GitHub, misalnya `boq-tribun-metta`. Boleh **Public**
   (kalau isinya mau bisa dibuka siapa saja) atau **Private** — Pages tetap jalan
   di akun berbayar; untuk akun gratis, repo harus Public.
2. Klik **Add file → Upload files**, lalu seret **`index.html`**, **`.nojekyll`**,
   dan **`README.md`** dari folder ini. Klik **Commit changes**.
3. Masuk ke **Settings → Pages**.
4. Bagian *Build and deployment*: **Source** pilih **Deploy from a branch**,
   **Branch** pilih **main** dan folder **/ (root)**. Klik **Save**.
5. Tunggu 1–2 menit. Alamatnya muncul di halaman yang sama:
   `https://<namauser>.github.io/boq-tribun-metta/`

Berkas `.nojekyll` penting supaya GitHub tidak memproses ulang isi folder.

## Memakai domain sendiri

1. Di **Settings → Pages → Custom domain**, isi misalnya `rab.namadomainmu.com`,
   lalu **Save**.
2. Di panel DNS penyedia domainmu, tambahkan record **CNAME**:
   `rab` → `<namauser>.github.io`
3. Kembali ke Settings → Pages, centang **Enforce HTTPS** setelah sertifikatnya terbit
   (biasanya di bawah 15 menit).

Setelah domain terpasang, alamat `github.io` tidak lagi terlihat oleh pengunjung.

## Memperbarui isinya

Unggah ulang `index.html` yang baru ke repo yang sama (Add file → Upload files →
pilih *Replace*). Pages akan menerbitkan ulang otomatis dalam satu-dua menit.

## Yang perlu diketahui pemakai

- **Isi harga** menampilkan kolom harga satuan, rekap, overhead, PPN, dan total.
- **Edit tabel** membuat seluruh sel bisa diubah, termasuk menambah atau menghapus baris.
- **Ekspor** berisi **Unduh Excel (.xlsx)** — berkas Excel asli dengan rumus hidup —
  dan **Simpan PDF** lewat dialog cetak browser.
- Semua ketikan tersimpan di browser masing-masing pemakai (localStorage). Tidak ada
  data yang dikirim ke server mana pun; berkas Excel dibuat di dalam browser.
- Tombol **Reset ke default** mengembalikan seluruh angka ke kuantitas model.

## Catatan teknis

- Satu-satunya sumber luar adalah Google Fonts. Kalau ingin benar-benar tanpa panggilan
  keluar, hapus baris `<link ... fonts.googleapis.com ...>` di dalam `index.html`;
  halaman tetap jalan dengan huruf bawaan sistem.
- Semua kuantitas berasal dari model Revit `METTA.rvt`. Kalau modelnya berubah,
  angka di halaman ini harus dibangun ulang.
