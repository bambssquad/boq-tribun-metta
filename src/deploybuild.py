# -*- coding: utf-8 -*-
"""Paket siap unggah ke GitHub Pages — satu berkas index.html, tanpa jejak claude.ai."""
import os, re, shutil, zipfile
import build

OUT = os.environ.get("DEPLOY_OUT", "/tmp/tribun/deploy")
TITLE = "BOQ & RAB Tribun Baja Hollow — Gedung METTA"
DESC = ("Gambar kerja, model 3D, bill of quantity, dan RAB tribun baja hollow. "
        "Isi harga langsung di halaman, unduh Excel berumus, atau simpan PDF.")

FAVICON = ("data:image/svg+xml,"
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' fill='%230A0B0D'/%3E"
           "%3Cpath d='M5 24h22M8 24V9M14 24V13M20 24V17M26 24V20' stroke='%23E0A62A'"
           " stroke-width='2.4' fill='none'/%3E%3C/svg%3E")


def make():
    body = build.build()

    # ---- versi terpasang sendiri: unduhan selalu tersedia ----
    body = body.replace(
        "const CAN_DL = !/(^|\\.)claude\\.ai$/i.test(location.hostname);",
        "const CAN_DL = true;")
    # cabang pesan untuk sandbox tidak terpakai di sini — buang teksnya
    body = re.sub(r": 'Catatan jujur: di halaman claude\.ai.*?';",
                  ": '';", body, flags=re.S)

    # ---- buang tautan ke artifact claude.ai ----
    body = re.sub(r'<a href="https://claude\.ai[^"]*"[^>]*>.*?</a>', '', body)
    body = body.replace(' · </div>', '</div>')

    head = (
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>{TITLE}</title>\n'
        f'<meta name="description" content="{DESC}">\n'
        '<meta name="color-scheme" content="dark">\n'
        f'<meta property="og:title" content="{TITLE}">\n'
        f'<meta property="og:description" content="{DESC}">\n'
        '<meta property="og:type" content="website">\n'
        f'<link rel="icon" href="{FAVICON}">\n'
    )
    # judul ganda: buang <title> bawaan dari build()
    body = re.sub(r'<title>.*?</title>\s*', '', body, count=1)
    body = re.sub(r'<meta name="viewport"[^>]*>\s*', '', body, count=1)

    html = ('<!doctype html>\n<html lang="id">\n<head>\n' + head + '</head>\n<body>\n'
            + body + '\n</body>\n</html>\n')

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    open(f"{OUT}/index.html", "w", encoding="utf-8").write(html)
    open(f"{OUT}/.nojekyll", "w").write("")
    open(f"{OUT}/README.md", "w", encoding="utf-8").write(README)

    zp = os.environ.get("DEPLOY_ZIP", "/tmp/tribun/deploy-boq-tribun-metta.zip")
    if zp and zp != "-":
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for f in ("index.html", ".nojekyll", "README.md"):
                z.write(f"{OUT}/{f}", f)

    left = html.lower().count("claude")
    return len(html), left, zp


README = """# BOQ & RAB Tribun Baja Hollow — Gedung METTA

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
"""


if __name__ == "__main__":
    n, left, zp = make()
    print("index.html:", n, "byte · sisa kata 'claude':", left)
    if zp and zp != "-" and os.path.exists(zp):
        print("zip:", zp, os.path.getsize(zp), "byte")
