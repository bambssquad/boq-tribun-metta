# -*- coding: utf-8 -*-
import json, io, sys, re, hashlib
from geom import *
from boq import *
import sheets
import draw
from three_d import HTML_3D, CSS_3D, JS_3D
import xlsxjs
import style

SHEETS = [
    ("S-01", "Denah Tribun", "1 : 100", sheets.s01,
     ["dek", "tangga", "kolom", "beton", "railing", "dim", "notasi"],
     "Denah lantai tribun di elevasi +16.00 (LT 4). Papan pinus 400 mm ada di muka tiap tier; "
     "void 50 mm mengelilingi keempat kolom beton eksisting."),
    ("S-02", "Rencana Tumpuan & Base Plate", "1 : 100", sheets.s02,
     ["outline", "bp", "beton", "dim", "notasi"],
     "Posisi 71 titik tumpuan. Tumpuan sendi: kolom duduk lepas di atas karet, tidak ada angkur "
     "yang menembus pelat lantai gedung."),
    ("S-03", "Rencana Rangka", "1 : 100", sheets.s03,
     ["balok", "brace", "anchor", "kolom", "dim", "notasi"],
     "Balok tepi di muka tiap tier, stiffener sedalam balok di tengah bentang, bracing X di belakang, "
     "dan rangka ujung diikat langsung ke kolom beton ujung yang bertumpang 150 mm."),
    ("S-04", "Tampak Depan", "1 : 100", sheets.s04,
     ["muka", "kolom", "tangga", "railing", "sandaran", "dim", "notasi"],
     "Dilihat dari sisi lapangan. Kolong tribun tertutup skirt pelat 2 mm sampai batas tier 1."),
    ("S-05", "Tampak Samping", "1 : 50", sheets.s05,
     ["dek", "kolom", "balok", "railing", "brace", "bp", "dim", "notasi"],
     "Sisi ujung tribun — profil tangga tier terlihat penuh bersama balustrade dan bracing sisi."),
    ("S-06", "Potongan A–A · Portal Tipikal", "1 : 50", sheets.s06,
     ["dek", "kolom", "balok", "bp", "dim", "notasi"],
     "Potongan pada garis portal tipikal. Tiap tier: balok tepi hollow 50x100x2,3, stiffener "
     "sama profil di tengah bentang, plat dek bordes 8 mm, papan pinus 400x40."),
    ("S-07", "Potongan B–B · Tangga A+B", "1 : 50", sheets.s07,
     ["tangga", "beton", "dek", "dim", "notasi"],
     "Potongan memanjang jalur tangga gabungan. Kolom beton berdiri di tengah bukaan 2000 mm "
     "dan membagi jalur jadi dua lintasan bersih 700 mm."),
    ("S-08", "Detail Tangga", "1 : 20", sheets.s08,
     ["tangga", "notasi"],
     "Satu tier tangga: 3 optrede 167 mm + 3 antrede 267 mm, naik total 500 mm."),
    ("S-09", "Detail Railing & Balustrade", "1 : 20", sheets.s09,
     ["railing", "dim", "notasi"],
     "Balustrade anti-panjat untuk pengguna anak: baluster vertikal rapat, tanpa elemen "
     "horizontal yang bisa dipijak, toe-board 100 mm menutup celah bawah."),
    ("S-10", "Detail Base Plate & Tumpuan", "1 : 10", sheets.s10,
     ["bp", "notasi"],
     "Tumpuan kolom: pelat 150x150x8 di atas karet 10 mm, las sudut a=4 mm keliling profil."),
    ("S-11", "Detail Sambungan D1–D4", "1 : 10", sheets.s11,
     ["detail"],
     "Empat tipe sambungan yang dipakai berulang di seluruh rangka."),
    ("S-12", "Exploded Axonometric", "—", sheets.s12,
     ["notasi"],
     "Urutan pasang dari bawah ke atas: base plate → rangka kolom & balok → plat dek → papan "
     "pinus → plat tangga → railing."),
]

MAT = {
    "H1": ("Hollow 50\u00d7100\u00d72,3 mm", "kolom, balok tepi, stiffener, strut anchor \u2014 BJ 37"),
    "H2": ("Hollow 40\u00d740\u00d72,0 mm", "bracing X belakang & rail pegangan"),
    "H3": ("Hollow 40\u00d740\u00d72,8 mm", "tiang baluster @100 mm"),
    "P8": ("Pelat bordes 8 mm", "dek injak, motif kembang anti-slip"),
    "P4": ("Pelat tekuk bordes 4 mm", "anak tangga + stringer"),
    "P2": ("Pelat polos 2 mm (tekuk tepi 20 mm)", "riser muka tier, skirt kolong, toe-board"),
    "B8": ("Base plate pelat 8 mm 150\u00d7150", "71 titik tumpuan"),
    "K1": ("Karet alas 10 mm 150\u00d7150", "di bawah tiap base plate, duduk lepas"),
    "W1": ("Papan pinus 400\u00d740 mm", "dudukan di muka tiap tier, finish clear"),
    "W2": ("Panel sandaran pinus 40 mm", "sandaran belakang menerus"),
    "C1": ("Kolom beton eksisting 600\u00d7500", "titik ikat satu-satunya \u2014 bukan pelat lantai"),
    "F1": ("Cat epoxy kuning 50 mm", "penanda nosing, rata permukaan (tidak menonjol)"),
}

LAYER_LABEL = {
    "dek": "Dek & pinus", "tangga": "Tangga", "kolom": "Kolom", "beton": "Kolom beton",
    "railing": "Railing", "dim": "Dimensi", "notasi": "Notasi", "outline": "Batas",
    "bp": "Base plate", "balok": "Balok", "brace": "Bracing", "anchor": "Anchor",
    "muka": "Muka tier", "detail": "Detail", "sandaran": "Sandaran",
}

SPEK = [
    ("Baja profil", [
        ("Mutu", "BJ 37 — fy 240 MPa, fu 370 MPa"),
        ("Rangka utama", "Hollow 50 × 100 × 2,3 mm — kolom, balok tepi, stiffener, strut anchor"),
        ("Nama di toko", "Besi Hollow 50 x 100 x 2,3mm x 6M (hitam)"),
        ("Bracing & rail", "Hollow 40 × 40 × 2,0 mm"),
        ("Baluster & tiang pegangan", "Hollow 40 × 40 × 2,8 mm"),
        ("Panjang batang", "6 m — panjang lonjor standar pasaran"),
    ]),
    ("Pelat", [
        ("Dek injak", "Pelat bordes 8 mm — motif kembang, anti-slip"),
        ("Lembar dek", "4ft × 8ft (1.219 × 2.438), 192 kg/lembar — 64,6 kg/m²"),
        ("Anak tangga & stringer", "Pelat tekuk bordes 4 mm — panel 267 × 700 antar lipatan"),
        ("Riser muka tier", "Pelat polos 2 mm — penutup, non-struktural"),
        ("Skirt & toe-board", "Pelat polos 2 mm dengan tekuk tepi 20 mm \u2014 lipatan itu yang bikin kaku, bukan tebalnya"),
        ("Base plate", "Pelat polos 8 mm, 150 × 150 — gauge sama dengan dek"),
        ("Nosing", "Dicat, tidak menonjol — lihat Finishing"),
    ]),
    ("Kayu & karet", [
        ("Papan dudukan", "Pinus 400 × 40 mm, satu papan di muka tiap tier"),
        ("Panel sandaran", "Papan kayu pinus 40 mm (type SANDARAN PINEWOOD 40mm)"),
        ("Alas tumpuan", "Karet 10 mm, 150 × 150 di bawah tiap base plate"),
    ]),
    ("Geometri", [
        ("Bentang total", "17.700 mm (muka-dalam ke muka-dalam kolom ujung)"),
        ("Kedalaman", "5.000 mm — 5 tier @ 1.000 mm"),
        ("Beda tinggi tier", "500 mm, dek +500 sampai +2.500"),
        ("Jarak portal", "1.770 mm"),
        ("Bentang pelat dek", "500 mm — stiffener di tengah tiap tier"),
        ("Tangga", "3 optrede 167 + 3 antrede 267 per tier — 2R+T = 601 mm, pelat tekuk 4 mm"),
        ("Lebar jalur", "Tangga A+B 2 × 700 mm bersih mengapit kolom; tangga C 600 mm"),
    ]),
    ("Sambungan", [
        ("Kolom → base plate", "Las sudut a = 4 mm keliling profil"),
        ("Balok tepi → kolom", "2 × baut M12 gr.4.6 pada pelat siku 6 mm, atau las a = 4 mm 2 × 80 mm"),
        ("Stiffener → balok", "Sedalam balok (100 mm) — dudukan rata, tanpa ganjal"),
        ("Bracing → kolom", "Pelat buhul 6 mm, las a = 4 mm dua sisi 40 mm"),
        ("Strut anchor → kolom beton", "Pelat 6 mm + 2 × dynabolt M10 kedalaman 80 mm"),
        ("Larangan", "Tidak boleh ada angkur ke pelat lantai gedung — hanya ke kolom beton"),
    ]),
    ("Finishing", [
        ("Persiapan", "Bebas kerak & minyak, sikat mekanis St 2"),
        ("Primer", "Zinc chromate 1 lapis"),
        ("Finish", "Cat hitam doff 2 lapis"),
        ("Nosing", "Cat epoxy kuning kontras selebar 50 mm di tepi anak tangga — "
                   "TIDAK memakai strip menonjol agar tidak jadi titik sandung"),
        ("Kayu", "Finish clear 2 lapis"),
    ]),
    ("Beban rencana", [
        ("Beban hidup", "4,79 kPa — SNI 1727:2020, tribun tempat duduk tidak tetap"),
        ("Beban mati", "0,86 kPa — dek 8 mm 0,63 + papan pinus 0,08 + rangka & riser 0,15"),
        ("Kombinasi", "1,2 D + 1,6 L = 8,70 kPa"),
        ("Lateral", "5% beban vertikal — bracing X belakang + 16 titik ikatan ke kolom beton"),
        ("Pengguna", "Anak usia SD bersama orang tua — beban berkerumun & berdiri diperhitungkan"),
    ]),
    ("Sumber material (Surabaya / Jakarta)", [
        ("Plat bordes 8 & 3 mm", "smsperkasa.com/produk/plat-bordes"),
        ("Hollow 50×100×2,3×6M", "smsperkasa.com — SKU BHHM-501002C3-6STDNB"),
        ("Katalog hollow hitam", "smsperkasa.com/produk/besi-hollow-hitam"),
        ("Plat polos 8 mm Surabaya", "duaputrapetir.co.id — 1200×2400 t8, 187 kg"),
        ("Hollow 50×100 Surabaya", "sahabatbesibaja.com — Sahabat Ana Grup"),
        ("Distributor bordes Surabaya", "suksesindoperkasa.com/distributor-plat-bordes-surabaya"),
        ("Catatan", "Ukuran & berat di atas dikutip dari katalog penjual, bukan asumsi. "
                    "Konfirmasi stok saat pemesanan — tebal hollow 50×100 umum di 2,0 / 2,3 / 2,8 mm."),
    ]),
]

RASIO = [
    ("Kolom hollow 50×100×2,3", "12,8 kN", "56,8 kN (tekuk, λ=118)", 0.23),
    ("Balok tepi 50×100×2,3", "σ 87 MPa", "160 MPa izin · δ L/962", 0.54),
    ("Stiffener dek 50×100×2,3", "σ 96 MPa", "160 MPa izin · δ L/863", 0.60),
    ("Pelat dek bordes 8 mm (bentang 500)", "σ 25 MPa", "160 MPa izin · δ L/926", 0.16),
    ("Anak tangga bordes 4 mm (beban titik 1,33 kN)", "σ 111 MPa", "160 MPa izin · δ 1,65 mm", 0.69),
    ("Bracing X 40×40×2 (belakang)", "10,6 kN", "15,5 kN", 0.68),
    ("Ikatan rangka ujung ke kolom beton", "6,2 kN", "16 kN (2×M10)", 0.39),
    ("Base plate 150×150×8", "0,57 MPa", "karet 3–5 MPa", 0.19),
    ("Strut anchor ke kolom beton", "2,1 kN", "16 kN (2×M10)", 0.13),
]



U0 = 17.1  # basis lama: lembar 1:100 dengan viewBox 20500 mm

def _sw(v):        # tebal garis -> piksel layar
    return min(max(float(v) / U0, 0.45), 1.6)

def _fs(v):        # ukuran huruf -> piksel layar
    return min(max(float(v) / U0 * 1.45, 11.0), 17.0)

def dwg_style(u, key):
    """DWG_CSS untuk satu lembar: angka dikali u, dan tiap selector dikunci ke lembar itu
    (style di dalam SVG tetap global di HTML, jadi harus diberi lingkup sendiri)."""
    css = re.sub(r"/\*.*?\*/", "", DWG_CSS, flags=re.S)
    css = re.sub(r"stroke-width:([\d.]+)", lambda m: f"stroke-width:{_sw(m.group(1))*u:.1f}", css)
    css = re.sub(r"font-size:([\d.]+)px", lambda m: f"font-size:{_fs(m.group(1))*u:.1f}px", css)
    def dash(m):
        vals = [max(float(x)/U0, 1.0)*u for x in m.group(1).split()]
        return "stroke-dasharray:" + " ".join(f"{v:.1f}" for v in vals)
    css = re.sub(r"stroke-dasharray:([\d. ]+)", dash, css)

    out = []
    for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", css):
        parts = []
        for one in sel.split(","):
            one = one.strip()
            if not one:
                continue
            parts.append(f"svg.{key}{one}" if one.startswith(".dwg") else f"svg.{key} {one}")
        if parts:
            out.append(",".join(parts) + "{" + body.strip() + "}")
    return "<style>" + "".join(out) + "</style>"


def sheet_u(svg, fw=1200.0, fh=540.0):
    """Satuan gambar per piksel saat lembar dipaskan ke bingkai fw x fh."""
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    return max(vb[2] / fw, vb[3] / fh)


OTHER_ITEMS = (
    [{"nm": nm, "q": q, "un": un, "note": note} for nm, q, un, note in FASTENERS]
    + [{"nm": "Papan pinus 400×40 (dudukan)", "q": round(PINUS_VOL, 3), "un": "m³",
        "note": f"15 batang, total panjang {SEG_LEN*TIERS:.1f} m"},
       {"nm": "Panel kayu sandaran 40 mm", "q": round(SAND_VOL, 3), "un": "m³",
        "note": f"{SAND_AREA:.2f} m² menerus A–C, finish clear"},
       {"nm": "Kawat las E6013 3,2 mm", "q": 38, "un": "kg",
        "note": "las sudut a=4 mm, total ±950 m alur"},
       {"nm": "Cat dasar zinc chromate", "q": 34, "un": "liter",
        "note": "1 lapis, daya sebar 10 m²/L"},
       {"nm": "Cat finish hitam doff", "q": 52, "un": "liter",
        "note": "2 lapis, luas permukaan baja ±340 m²"},
       {"nm": "Finish clear kayu", "q": 9, "un": "liter",
        "note": "papan pinus + panel sandaran, 2 lapis"}]
)


def boq_rev():
    """Stempel isi BOQ. Kalau kuantitas model berubah, stempel ikut berubah,
    dan halaman tahu bahwa data tersimpan di browser sudah basi."""
    src = repr(HOLLOW_ITEMS) + repr(PLATE_ITEMS) + repr(OTHER_ITEMS)
    return hashlib.sha1(src.encode("utf-8")).hexdigest()[:10]


REV = boq_rev()


def offer_inner():
    return (
      '<div class="boqbar">'
      '<label class="sw"><input type="checkbox" id="tgOffer"><span>Susun penawaran</span></label>'
      '<label class="sw"><input type="checkbox" id="tgOfEdit"><span>Edit isi</span></label>'
      '<span class="bgrow"></span>'
      '<button type="button" class="reset" id="ofReset">Reset penawaran</button>'
      '</div>'
      '<div id="ofbox" hidden>'
      '<p class="lede ofhint">Angka rupiah ditarik langsung dari BOQ di atas — nyalakan '
      '<b>Isi harga</b> di sana dulu supaya nominal termin terisi. Semua ketikan di halaman ini '
      'tersimpan di browser ini saja.</p>'
      '<div class="ofdoc" id="ofdoc"></div>'
      '<div class="exrow ofex">'
      '<button type="button" class="exbtn" id="ofPdf"><b>Simpan PDF A4</b>'
      '<span>Mencetak hanya lembar penawaran ini dengan tata letak A4 potret.</span></button>'
      '<button type="button" class="exbtn" id="ofXls"><b>Salin ke Excel</b>'
      '<span>Menyalin kop, rekap, termin, dan jadwal — tempel (Ctrl+V) di Excel.</span></button>'
      '</div>'
      '</div>'
    )

def boq_inner():
    """Isi blok BOQ — dipakai halaman dokumen dan halaman meja gambar."""
    return (
      '<div class="boqbar">'
      '<label class="sw"><input type="checkbox" id="tgPrice"><span>Isi harga</span></label>'
      '<div class="seg" id="segMode" hidden>'
      '<button type="button" data-mode="satuan" class="on">Satuan bawaan</button>'
      '<button type="button" data-mode="ringkas">Ringkas</button>'
      '<button type="button" data-mode="perkg">Semua baja per kg</button></div>'
      '<label class="usel-all ponly" hidden>Satuan harga '
      '<select id="unitAll">'
      '<option value="auto">Bawaan tiap baris</option>'
      '<option value="kg">kg</option>'
      '<option value="m">meter lari (m\u02b9)</option>'
      '<option value="m2">m\u00b2</option>'
      '<option value="m3">m\u00b3</option>'
      '<option value="btg">batang / lonjor / lembar</option>'
      '<option value="bh">buah</option>'
      '</select></label>'
      '<label class="sw"><input type="checkbox" id="tgEdit"><span>Edit tabel</span></label>'
      '<label class="sw"><input type="checkbox" id="tgExport"><span>Ekspor</span></label>'
      '<span class="bgrow"></span>'
      '<button type="button" class="reset" id="boqReset">Reset ke default</button>'
      '</div>'
      '<div class="exportbox" id="exportbox" hidden>'
      '<div class="exrow">'
      '<button type="button" class="exbtn" id="exPdf"><b>Simpan PDF</b>'
      '<span>Buka dialog cetak &rarr; pilih <i>Save as PDF</i>. Tata letak cetak A3 sudah disiapkan.</span></button>'
      '<button type="button" class="exbtn" id="exXls"><b>Salin ke Excel</b>'
      '<span>Menyalin seluruh tabel + rekap. Tempel (Ctrl+V) di Excel — kolom langsung terpisah.</span></button>'
      '<button type="button" class="exbtn dlonly" id="exXlsx" hidden><b>Unduh Excel (.xlsx)</b>'
      '<span>Berkas Excel asli berisi lembar INPUT, BOQ, dan REKAP dengan <i>rumus hidup</i> \u2014 '
      'ubah waste atau harga di Excel, totalnya ikut berubah.</span></button>'
      '<button type="button" class="exbtn" id="exJson"><b>Salin kode BOQ</b>'
      '<span>Kode ringkas berisi seluruh editanmu \u2014 simpan sebagai cadangan, atau kirim '
      'ke rekanmu supaya dia membuka BOQ yang sama persis.</span></button>'
      '<button type="button" class="exbtn" id="exLoad"><b>Muat kode BOQ</b>'
      '<span>Tempel kode dari orang lain (atau cadanganmu) untuk mengembalikan seluruh isian.</span></button>'
      '</div>'
      '<div class="exload" id="exLoadBox" hidden>'
      '<textarea id="exCode" rows="3" placeholder="Tempel kode BOQ di sini\u2026"></textarea>'
      '<button type="button" class="reset" id="exApply">Terapkan kode</button>'
      '<span class="exmsg" id="exMsg"></span></div>'
      '<div class="exname"><label>Nama proyek <input type="text" id="exProj" '
      'value="Tribun METTA LT 4" maxlength="60"></label></div>'
      '<p class="exnote" id="exNote"></p>'
      '</div>'
      '<p class="exnote revnote" id="revNote" hidden></p>'
      '<div class="wastebar">'
      '<label>Waste profil hollow <input type="number" id="wH" value="5" min="0" max="30" step="1"><span>%</span></label>'
      '<label>Waste pelat <input type="number" id="wP" value="10" min="0" max="30" step="1"><span>%</span></label>'
      '<label>Panjang lonjor <input type="number" id="bar" value="6" min="4" max="12" step="1"><span>m</span></label>'
      '<label class="ponly" hidden>Overhead &amp; untung <input type="number" id="ohp" value="10" min="0" max="50" step="1"><span>%</span></label>'
      '<label class="ponly" hidden>PPN <input type="number" id="ppn" value="11" min="0" max="20" step="1"><span>%</span></label>'
      '</div>'
      '<h3 class="sub">Profil hollow <button type="button" class="addrow" data-add="H" hidden>+ baris</button></h3>'
      '<div class="tw"><table id="tH"><thead></thead><tbody></tbody><tfoot></tfoot></table></div>'
      '<h3 class="sub">Pelat baja <button type="button" class="addrow" data-add="P" hidden>+ baris</button></h3>'
      '<div class="tw"><table id="tP"><thead></thead><tbody></tbody><tfoot></tfoot></table></div>'
      '<h3 class="sub">Material lain <button type="button" class="addrow" data-add="O" hidden>+ baris</button></h3>'
      '<div class="tw"><table id="tO"><thead></thead><tbody></tbody><tfoot></tfoot></table></div>'
      '<p class="tot">Total berat baja <b id="grand">—</b> — profil hollow + pelat, sudah termasuk waste.</p>'
      '<div id="rekap" hidden></div>'
    )


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build():
    out = io.StringIO()
    w = out.write

    w('<meta name="viewport" content="width=device-width,initial-scale=1">\n')
    w('<title>Tribun METTA LT 4</title>\n')
    w(style.FONTS + "\n")
    w(f"<style>{style.CSS}.hidden{{display:none}}{CSS_3D}</style>\n")

    # ---- header ----
    w('<header class="top">')
    w('<div class="top-in">')
    w('<div class="brand"><span class="mark"></span><div>')
    w('<div class="bname">Tribun Baja Hollow — Gedung METTA</div>')
    w('<div class="bsub">Lantai 4 (+16.00) · gambar kerja fabrikasi · 12 lembar</div>')
    w('</div></div>')
    w('<nav class="pills">')
    for num, name, *_ in SHEETS:
        w(f'<a class="pill" href="#{num}">{num}</a>')
    w('<a class="pill" href="#tiga-d">3D</a>'
      '<a class="pill" href="#spek">SPEK</a><a class="pill" href="#boq">BOQ</a>'
      '<a class="pill" href="#penawaran">PENAWARAN</a>'
      '<a class="pill" href="#potong">POTONG</a>')
    w('</nav></div></header>')

    w('<main class="wrap">')

    # ---- ringkas ----
    w('<section class="hero">')
    w('<p class="eyebrow">METTA · LT 4 (+16.00) · 12 lembar</p>')
    w('<h1><span class="ln"><i>Set gambar</i></span>'
      '<span class="ln"><i>kerja</i></span>'
      '<span class="ln"><i>tribun</i></span></h1>')
    w('<p class="lede">Semua gambar di halaman ini dibangun dari geometri model Revit yang sudah '
      'terkunci — bentang 17.700, kedalaman 5.000, 5 tier @500. Angka pada garis ukur adalah '
      'milimeter sebenarnya, bukan skala gambar.</p>')
    w('<div class="facts">')
    for k, v in [("Bentang", "17.700 mm"), ("Kedalaman", "5.000 mm"), ("Tier", "5 @ 500 mm"),
                 ("Jalur tangga", "700+700 & 600 mm"), ("Titik tumpuan", "71"),
                 ("Berat baja", "±9,23 ton")]:
        w(f'<div class="fact"><span class="fk">{k}</span><span class="fv">{v}</span></div>')
    w('</div></section>')

    # ---- indeks lembar ----
    w('<section class="ixwrap rv" id="indeks">')
    w('<h3 class="sub">Indeks lembar</h3>')
    w('<div class="ixlist">')
    for num, name, scale, fn, layers, desc in SHEETS:
        w(f'<a class="ix" href="#{num}" data-prev="{num}">'
          f'<span class="ix-n">{num}</span>'
          f'<span class="ix-name">{esc(name)}</span>'
          f'<span class="ix-s">1 : {scale.split(":")[-1].strip()}</span></a>')
    w('</div></section>')
    w('<div id="ixprev" aria-hidden="true"></div>')

    # ---- sheets ----
    for num, name, scale, fn, layers, desc in SHEETS:
        draw.set_u(17.0)
        u = sheet_u(fn())
        draw.set_u(u)
        key = "sh" + num.replace("-", "")
        svg = fn().replace('class="dwg"', f'class="dwg {key}"', 1)
        svg = svg.replace(">", ">" + dwg_style(u, key), 1)
        w(f'<section class="sheet rv" id="{num}">')
        w('<div class="shead">')
        w(f'<div class="snum">{num}</div>')
        w(f'<div class="sname">{esc(name)}</div>')
        w(f'<div class="sscale">Skala {scale}</div>')
        w(f'<div class="navf"><button data-nav="prev" data-s="{num}" aria-label="Lembar sebelumnya">&larr;</button>'
          f'<button data-nav="next" data-s="{num}" aria-label="Lembar berikutnya">&rarr;</button></div>')
        w('</div>')
        w(f'<p class="sdesc">{esc(desc)}</p>')
        w('<div class="ctrls">')
        for lay in layers:
            lid = f"{num}-{lay}"
            w(f'<label class="chip"><input type="checkbox" checked data-sheet="{num}" '
              f'data-lay="lay-{lay}"><span>{LAYER_LABEL.get(lay, lay)}</span></label>')
        w(f'<button class="meas-btn" data-meas="{num}" aria-pressed="false">Ukur</button>')
        w(f'<button class="expand" data-full="{num}" aria-pressed="false">Layar penuh</button>')
        w(f'<button class="reset" data-reset="{num}">Reset tampilan</button>')
        w('</div>')
        w(f'<div class="frame" data-frame="{num}"><div class="pan">{svg}</div>'
          '<div class="hint" data-h>seret · scroll zoom · ketuk 2× reset</div></div>')
        codes = []
        for c in re.findall(r'data-mat="([^"]+)"', svg):
            if c not in codes:
                codes.append(c)
        if codes:
            w('<div class="matleg"><span class="mlh">Material pada lembar ini</span><dl>')
            for c in codes:
                nm, note = MAT[c]
                w(f'<dt>{c}</dt><dd><b>{esc(nm)}</b> — {esc(note)}</dd>')
            w('</dl></div>')
        w('</section>')

    # ---- 3D ----
    w(HTML_3D)

    # ---- spek ----
    w('<section class="block rv" id="spek"><h2>Spesifikasi teknis</h2>')
    w('<div class="spek">')
    for group, rows in SPEK:
        w(f'<div class="skgroup"><h3>{esc(group)}</h3><dl>')
        for k, v in rows:
            w(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>')
        w('</dl></div>')
    w('</div>')

    w('<h3 class="sub">Rasio kapasitas</h3>')
    w('<div class="tw"><table class="rasio"><thead><tr><th>Elemen</th><th>Gaya / tegangan</th>'
      '<th>Kapasitas</th><th>Rasio</th></tr></thead><tbody>')
    for el, gy, kap, r in RASIO:
        lvl = "ok" if r < 0.7 else ("warn" if r < 0.9 else "crit")
        w(f'<tr><td>{esc(el)}</td><td class="num">{esc(gy)}</td><td class="num">{esc(kap)}</td>'
          f'<td class="num"><span class="bar {lvl}"><i style="width:{r*100:.0f}%"></i></span>'
          f'<b>{r:.2f}</b></td></tr>')
    w('</tbody></table></div>')
    w('</section>')

    # ---- BOQ ----
    w('<section class="block rv" id="boq"><h2>Bill of quantity &amp; kebutuhan material</h2>')
    w('<p class="lede">Kuantitas dihitung dari geometri model. Nyalakan <b>Isi harga</b> untuk '
      'menghitung biaya, atau <b>Edit tabel</b> untuk mengubah isinya — semua ketikanmu tersimpan '
      'di browser ini dan bisa dikembalikan lewat tombol reset.</p>')
    w(boq_inner())
    w('</section>')

    # ---- penawaran ----
    w('<section class="block rv" id="penawaran"><h2>Penawaran &amp; termin pembayaran</h2>')
    w('<p class="lede">Template surat penawaran: kop, rekap biaya, termin pembayaran dengan '
      'nominal otomatis, jadwal pelaksanaan, dan lingkup pekerjaan. Bisa dicetak PDF A4 atau '
      'disalin ke Excel.</p>')
    w(offer_inner())
    w('</section>')

    # ---- cutting list ----
    w('<section class="block rv" id="potong"><h2>Daftar potong</h2>')
    w('<p class="lede">Perkiraan jumlah batang dan lembar yang perlu dibeli, memakai faktor waste '
      'di atas. Sisa potongan adalah selisih antara panjang terpakai dan panjang yang dibeli.</p>')
    w('<div class="tw"><table id="tCut"><thead><tr><th>Profil / pelat</th>'
      '<th class="num">Terpakai</th><th class="num">Dibeli</th><th class="num">Sisa</th>'
      '<th>Bentuk beli</th></tr></thead><tbody></tbody></table></div>')
    w('</section>')

    w('<footer class="foot"><div>Tribun Baja Hollow · Gedung METTA · LT 4 (+16.00) · '
      '<a href="https://claude.ai/code/artifact/4af32bcd-4d75-439f-bedc-bd2f8632b618" '
      'style="color:var(--accent)">buka versi meja gambar &rarr;</a></div>'
      '<div>Dibangun dari model <code>METTA.rvt</code> — geometri terkunci, bukan sketsa.</div>'
      '</footer>')
    w('</main>')

    data = {
        "rev": REV,
        "other": OTHER_ITEMS,
        "hollow": [{"nm": a, "pr": b, "n": c, "L": round(d, 2), "kg": HOLLOW[e], "note": f}
                   for a, b, c, d, e, f in HOLLOW_ITEMS],
        "plate": [{"nm": a, "t": b, "A": round(c, 2), "sur": d, "note": e}
                  for a, b, c, d, e in PLATE_ITEMS],
        "sheetA": SHEET_A,
    }
    js_all = JS.replace("__XLSXJS__", xlsxjs.JS)
    w(f'<script>const DATA = {json.dumps(data, ensure_ascii=False)};\n{js_all}\n{JS_3D}</script>')
    return out.getvalue()


DWG_CSS = r"""
/* --- gaya garis gambar --- */
.dwg{stroke-linecap:square}
.deck{fill:color-mix(in srgb,var(--steel) 10%,transparent);stroke:var(--steel);stroke-width:8}
.pinus{fill:color-mix(in srgb,var(--accent) 26%,transparent);stroke:var(--accent);stroke-width:6}
.tread{fill:color-mix(in srgb,var(--steel) 5%,transparent);stroke:var(--steel);stroke-width:5}
.stringer{stroke:var(--ink);stroke-width:14;fill:none}
.col,.colE{fill:var(--steel);stroke:none}
.conc{fill:color-mix(in srgb,var(--ink) 28%,transparent);stroke:var(--ink);stroke-width:8}
.void{fill:none;stroke:var(--dim);stroke-width:6;stroke-dasharray:40 26}
.rail{stroke:var(--ink);stroke-width:12;fill:none}
.outline{fill:none;stroke:var(--ink);stroke-width:12}
.bp{fill:none;stroke:var(--steel);stroke-width:8}
.beam{stroke:var(--ink);stroke-width:20;fill:none}
.stiff{stroke:var(--steel);stroke-width:9;fill:none;stroke-dasharray:90 50}
.brace{stroke:var(--accent);stroke-width:12;fill:none}
.anchor{stroke:var(--dim);stroke-width:14;fill:none}
.skirt{fill:color-mix(in srgb,var(--steel) 14%,transparent);stroke:var(--steel);stroke-width:8}
.edge{stroke:var(--steel);stroke-width:7;fill:none}
.aisleE{fill:color-mix(in srgb,var(--paper) 80%,transparent);stroke:var(--accent);stroke-width:7}
.sandE{fill:color-mix(in srgb,var(--accent) 18%,transparent);stroke:var(--accent);stroke-width:7}
.gridline{stroke:var(--faint);stroke-width:4;stroke-dasharray:120 40 12 40}
.gridline.off{stroke-dasharray:16 34;opacity:.5}
.bub circle{fill:var(--surface);stroke:var(--faint);stroke-width:6}
.bubtxt{font-family:"JetBrains Mono",monospace;font-size:150px;fill:var(--muted)}
.dim{stroke:var(--dim);stroke-width:5;fill:none}
.dimtxt{font-family:"JetBrains Mono",monospace;font-size:130px;fill:var(--dim)}
.lbl,.note{font-family:Archivo,sans-serif;font-size:140px;fill:var(--muted)}
.dtitle{font-family:Archivo,sans-serif;font-size:120px;font-weight:700;fill:var(--ink)}
.axlbl{font-family:Archivo,sans-serif;font-size:680px;font-weight:600;fill:var(--muted)}
.leader{stroke:var(--faint);stroke-width:5;fill:none}
.mtag .leader{stroke:var(--accent);stroke-width:5}
.mdot{fill:var(--accent);stroke:none}
.mtxt{font-family:"JetBrains Mono","IBM Plex Mono",monospace;font-size:132px;font-weight:600;fill:var(--accent)}
.slab{stroke:var(--ink);stroke-width:16;fill:none}
/* potongan */
.deckS{fill:var(--steel);stroke:none}
.pinusS{fill:color-mix(in srgb,var(--accent) 40%,transparent);stroke:var(--accent);stroke-width:4}
.riserS{fill:var(--steel);stroke:var(--steel);stroke-width:5}
.colS{fill:color-mix(in srgb,var(--steel) 55%,transparent);stroke:var(--ink);stroke-width:5}
.beamS{fill:color-mix(in srgb,var(--ink) 35%,transparent);stroke:var(--ink);stroke-width:5}
.stiffS{fill:none;stroke:var(--steel);stroke-width:5}
.treadS{fill:var(--steel);stroke:var(--steel);stroke-width:5}
.nosingS{fill:var(--accent);stroke:none}
.none{display:none}
.concS{fill:color-mix(in srgb,var(--ink) 22%,transparent);stroke:var(--ink);stroke-width:6}
.railS{fill:color-mix(in srgb,var(--ink) 45%,transparent);stroke:var(--ink);stroke-width:4}
.balS{fill:color-mix(in srgb,var(--ink) 45%,transparent);stroke:var(--ink);stroke-width:4}
.toeS{fill:color-mix(in srgb,var(--steel) 30%,transparent);stroke:var(--steel);stroke-width:4}
.braceS{stroke:var(--accent);stroke-width:9;fill:none}
.bpS{fill:var(--ink);stroke:none}
.karetS{fill:color-mix(in srgb,var(--ink) 45%,transparent);stroke:none}
.stringerS{stroke:var(--ink);stroke-width:9;fill:none}
.ghost{stroke:var(--faint);stroke-width:5;stroke-dasharray:70 40;fill:none}
.weld{fill:var(--accent);stroke:none}
.bolt{fill:none;stroke:var(--ink);stroke-width:5}
.gusset{fill:color-mix(in srgb,var(--accent) 30%,transparent);stroke:var(--accent);stroke-width:5}
.anchorS{stroke:var(--dim);stroke-width:10;fill:none}
/* aksonometri */
.ax-top{stroke:var(--ink);stroke-width:4}
.ax-l{stroke:var(--ink);stroke-width:4}
.ax-r{stroke:var(--ink);stroke-width:4}
.c-col.ax-top{fill:color-mix(in srgb,var(--steel) 62%,transparent)}
.c-col.ax-l{fill:color-mix(in srgb,var(--steel) 40%,transparent)}
.c-col.ax-r{fill:color-mix(in srgb,var(--steel) 24%,transparent)}
.c-beam.ax-top{fill:color-mix(in srgb,var(--ink) 40%,transparent)}
.c-beam.ax-l{fill:color-mix(in srgb,var(--ink) 26%,transparent)}
.c-beam.ax-r{fill:color-mix(in srgb,var(--ink) 16%,transparent)}
.c-deck.ax-top{fill:color-mix(in srgb,var(--steel) 34%,transparent)}
.c-deck.ax-l,.c-deck.ax-r{fill:color-mix(in srgb,var(--steel) 20%,transparent)}
.c-pin.ax-top{fill:color-mix(in srgb,var(--accent) 55%,transparent)}
.c-pin.ax-l,.c-pin.ax-r{fill:color-mix(in srgb,var(--accent) 32%,transparent)}
.c-stair.ax-top{fill:color-mix(in srgb,var(--dim) 40%,transparent)}
.c-stair.ax-l,.c-stair.ax-r{fill:color-mix(in srgb,var(--dim) 24%,transparent)}
.c-rail.ax-top{fill:color-mix(in srgb,var(--ink) 34%,transparent)}
.c-rail.ax-l,.c-rail.ax-r{fill:color-mix(in srgb,var(--ink) 20%,transparent)}
.c-bp.ax-top{fill:color-mix(in srgb,var(--accent) 46%,transparent)}
.c-bp.ax-l,.c-bp.ax-r{fill:color-mix(in srgb,var(--accent) 26%,transparent)}
.hidden{display:none}
"""

CSS = r"""
*,*::before,*::after{box-sizing:border-box}
:root{
  --ground:#EDECE9; --surface:#FFFFFF; --paper:#FBFBF9;
  --ink:#15181D; --muted:#5B6472; --faint:#8C95A3;
  --line:#C7CBD2; --hair:#DDE0E5;
  --steel:#39414E; --accent:#C8901A; --dim:#2C6B8C;
  --ok:#3F7A4E; --warn:#B5761B; --crit:#A8402F;
  --shadow:0 1px 2px rgba(18,22,28,.06),0 8px 24px rgba(18,22,28,.06);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#0E1116; --surface:#161A20; --paper:#12161C;
    --ink:#E7EAEF; --muted:#98A2B1; --faint:#6C7686;
    --line:#333B47; --hair:#242B34;
    --steel:#A9B4C3; --accent:#EBBA45; --dim:#69AECE;
    --ok:#6FB183; --warn:#D9A24E; --crit:#D97A66;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 28px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  --ground:#0E1116; --surface:#161A20; --paper:#12161C;
  --ink:#E7EAEF; --muted:#98A2B1; --faint:#6C7686;
  --line:#333B47; --hair:#242B34;
  --steel:#A9B4C3; --accent:#EBBA45; --dim:#69AECE;
  --ok:#6FB183; --warn:#D9A24E; --crit:#D97A66;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 28px rgba(0,0,0,.35);
}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"IBM Plex Sans","Segoe UI",system-ui,sans-serif;
  font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased;
}
h1,h2,h3,.snum,.sname,.pill,.bname{font-family:"IBM Plex Sans Condensed","IBM Plex Sans",sans-serif}
.num,code,.fv,.bsub{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}

.top{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--ground) 88%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--hair)}
.top-in{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;gap:20px;align-items:center;
  justify-content:space-between;flex-wrap:wrap}
.brand{display:flex;gap:12px;align-items:center}
.mark{width:26px;height:26px;flex:0 0 auto;border:2px solid var(--ink);
  background:repeating-linear-gradient(135deg,var(--ink) 0 2px,transparent 2px 6px)}
.bname{font-weight:700;font-size:17px;letter-spacing:-.01em;line-height:1.2}
.bsub{font-size:11.5px;color:var(--muted);letter-spacing:.02em}
.pills{display:flex;gap:5px;flex-wrap:wrap}
.pill{font-size:11.5px;font-weight:600;letter-spacing:.04em;text-decoration:none;color:var(--muted);
  border:1px solid var(--hair);padding:4px 9px;border-radius:2px;background:var(--surface)}
.pill:hover{color:var(--ink);border-color:var(--steel)}
.pill:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.wrap{max-width:1180px;margin:0 auto;padding:0 22px 90px}
.hero{padding:52px 0 34px;border-bottom:1px solid var(--hair)}
h1{font-size:clamp(30px,4.4vw,46px);line-height:1.06;letter-spacing:-.02em;margin:0 0 14px;
  text-wrap:balance;font-weight:600}
.lede{max-width:64ch;color:var(--muted);margin:0 0 22px}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
  background:var(--hair);border:1px solid var(--hair)}
.fact{background:var(--surface);padding:12px 14px;display:flex;flex-direction:column;gap:2px}
.fk{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--faint)}
.fv{font-size:16px;font-weight:600}

.sheet{margin:44px 0;background:var(--surface);border:1px solid var(--hair);box-shadow:var(--shadow)}
.shead{display:flex;align-items:baseline;gap:14px;padding:14px 18px;border-bottom:1px solid var(--hair);
  flex-wrap:wrap}
.snum{font-family:"IBM Plex Mono",monospace;font-weight:600;font-size:13px;letter-spacing:.06em;
  color:var(--surface);background:var(--steel);padding:3px 8px}
.sname{font-size:19px;font-weight:600;letter-spacing:-.01em;flex:1}
.sscale{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--muted)}
.sdesc{margin:0;padding:12px 18px 0;color:var(--muted);max-width:76ch;font-size:14px}
.ctrls{display:flex;gap:6px;flex-wrap:wrap;padding:14px 18px 12px;align-items:center}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;border:1px solid var(--hair);
  padding:3px 9px;cursor:pointer;user-select:none;background:var(--paper)}
.chip input{margin:0;accent-color:var(--steel);width:12px;height:12px}
.chip:has(input:not(:checked)){opacity:.42}
.chip:focus-within{outline:2px solid var(--accent);outline-offset:1px}
.reset{margin-left:auto;font:inherit;font-size:11.5px;background:none;border:1px solid var(--hair);
  padding:4px 10px;cursor:pointer;color:var(--muted)}
.reset:hover{color:var(--ink);border-color:var(--steel)}

.frame{position:relative;overflow:hidden;background:var(--paper);border-top:1px solid var(--hair);
  height:min(66vh,560px);touch-action:none;cursor:grab}
.frame.drag{cursor:grabbing}
.pan{width:100%;height:100%;transform-origin:0 0}
.hint{position:absolute;right:10px;bottom:8px;font-size:10.5px;color:var(--faint);
  font-family:"IBM Plex Mono",monospace;pointer-events:none}
svg.dwg{width:100%;height:100%;display:block}

/* --- gaya garis gambar --- */
.dwg{stroke-linecap:square}
.deck{fill:color-mix(in srgb,var(--steel) 10%,transparent);stroke:var(--steel);stroke-width:8}
.pinus{fill:color-mix(in srgb,var(--accent) 26%,transparent);stroke:var(--accent);stroke-width:6}
.tread{fill:color-mix(in srgb,var(--steel) 5%,transparent);stroke:var(--steel);stroke-width:5}
.stringer{stroke:var(--ink);stroke-width:14;fill:none}
.col,.colE{fill:var(--steel);stroke:none}
.conc{fill:color-mix(in srgb,var(--ink) 28%,transparent);stroke:var(--ink);stroke-width:8}
.void{fill:none;stroke:var(--dim);stroke-width:6;stroke-dasharray:40 26}
.rail{stroke:var(--ink);stroke-width:12;fill:none}
.outline{fill:none;stroke:var(--ink);stroke-width:12}
.bp{fill:none;stroke:var(--steel);stroke-width:8}
.beam{stroke:var(--ink);stroke-width:20;fill:none}
.stiff{stroke:var(--steel);stroke-width:9;fill:none;stroke-dasharray:90 50}
.brace{stroke:var(--accent);stroke-width:12;fill:none}
.anchor{stroke:var(--dim);stroke-width:14;fill:none}
.skirt{fill:color-mix(in srgb,var(--steel) 14%,transparent);stroke:var(--steel);stroke-width:8}
.edge{stroke:var(--steel);stroke-width:7;fill:none}
.aisleE{fill:color-mix(in srgb,var(--paper) 80%,transparent);stroke:var(--accent);stroke-width:7}
.sandE{fill:color-mix(in srgb,var(--accent) 18%,transparent);stroke:var(--accent);stroke-width:7}
.gridline{stroke:var(--faint);stroke-width:4;stroke-dasharray:120 40 12 40}
.gridline.off{stroke-dasharray:16 34;opacity:.5}
.bub circle{fill:var(--surface);stroke:var(--faint);stroke-width:6}
.bubtxt{font-family:"IBM Plex Mono",monospace;font-size:150px;fill:var(--muted)}
.dim{stroke:var(--dim);stroke-width:5;fill:none}
.dimtxt{font-family:"IBM Plex Mono",monospace;font-size:130px;fill:var(--dim)}
.lbl,.note{font-family:"IBM Plex Sans Condensed",sans-serif;font-size:140px;fill:var(--muted)}
.dtitle{font-family:"IBM Plex Sans Condensed",sans-serif;font-size:120px;font-weight:700;fill:var(--ink)}
.axlbl{font-family:"IBM Plex Sans Condensed",sans-serif;font-size:680px;font-weight:600;fill:var(--muted)}
.leader{stroke:var(--faint);stroke-width:5;fill:none}
.mtag .leader{stroke:var(--accent);stroke-width:5}
.mdot{fill:var(--accent);stroke:none}
.mtxt{font-family:"JetBrains Mono","IBM Plex Mono",monospace;font-size:132px;font-weight:600;fill:var(--accent)}
.slab{stroke:var(--ink);stroke-width:16;fill:none}
/* potongan */
.deckS{fill:var(--steel);stroke:none}
.pinusS{fill:color-mix(in srgb,var(--accent) 40%,transparent);stroke:var(--accent);stroke-width:4}
.riserS{fill:var(--steel);stroke:var(--steel);stroke-width:5}
.colS{fill:color-mix(in srgb,var(--steel) 55%,transparent);stroke:var(--ink);stroke-width:5}
.beamS{fill:color-mix(in srgb,var(--ink) 35%,transparent);stroke:var(--ink);stroke-width:5}
.stiffS{fill:none;stroke:var(--steel);stroke-width:5}
.treadS{fill:var(--steel);stroke:var(--steel);stroke-width:5}
.nosingS{fill:var(--accent);stroke:none}
.none{display:none}
.concS{fill:color-mix(in srgb,var(--ink) 22%,transparent);stroke:var(--ink);stroke-width:6}
.railS{fill:color-mix(in srgb,var(--ink) 45%,transparent);stroke:var(--ink);stroke-width:4}
.balS{fill:color-mix(in srgb,var(--ink) 45%,transparent);stroke:var(--ink);stroke-width:4}
.toeS{fill:color-mix(in srgb,var(--steel) 30%,transparent);stroke:var(--steel);stroke-width:4}
.braceS{stroke:var(--accent);stroke-width:9;fill:none}
.bpS{fill:var(--ink);stroke:none}
.karetS{fill:color-mix(in srgb,var(--ink) 45%,transparent);stroke:none}
.stringerS{stroke:var(--ink);stroke-width:9;fill:none}
.ghost{stroke:var(--faint);stroke-width:5;stroke-dasharray:70 40;fill:none}
.weld{fill:var(--accent);stroke:none}
.bolt{fill:none;stroke:var(--ink);stroke-width:5}
.gusset{fill:color-mix(in srgb,var(--accent) 30%,transparent);stroke:var(--accent);stroke-width:5}
.anchorS{stroke:var(--dim);stroke-width:10;fill:none}
/* aksonometri */
.ax-top{stroke:var(--ink);stroke-width:4}
.ax-l{stroke:var(--ink);stroke-width:4}
.ax-r{stroke:var(--ink);stroke-width:4}
.c-col.ax-top{fill:color-mix(in srgb,var(--steel) 62%,transparent)}
.c-col.ax-l{fill:color-mix(in srgb,var(--steel) 40%,transparent)}
.c-col.ax-r{fill:color-mix(in srgb,var(--steel) 24%,transparent)}
.c-beam.ax-top{fill:color-mix(in srgb,var(--ink) 40%,transparent)}
.c-beam.ax-l{fill:color-mix(in srgb,var(--ink) 26%,transparent)}
.c-beam.ax-r{fill:color-mix(in srgb,var(--ink) 16%,transparent)}
.c-deck.ax-top{fill:color-mix(in srgb,var(--steel) 34%,transparent)}
.c-deck.ax-l,.c-deck.ax-r{fill:color-mix(in srgb,var(--steel) 20%,transparent)}
.c-pin.ax-top{fill:color-mix(in srgb,var(--accent) 55%,transparent)}
.c-pin.ax-l,.c-pin.ax-r{fill:color-mix(in srgb,var(--accent) 32%,transparent)}
.c-stair.ax-top{fill:color-mix(in srgb,var(--dim) 40%,transparent)}
.c-stair.ax-l,.c-stair.ax-r{fill:color-mix(in srgb,var(--dim) 24%,transparent)}
.c-rail.ax-top{fill:color-mix(in srgb,var(--ink) 34%,transparent)}
.c-rail.ax-l,.c-rail.ax-r{fill:color-mix(in srgb,var(--ink) 20%,transparent)}
.c-bp.ax-top{fill:color-mix(in srgb,var(--accent) 46%,transparent)}
.c-bp.ax-l,.c-bp.ax-r{fill:color-mix(in srgb,var(--accent) 26%,transparent)}
.hidden{display:none}

.block{margin:56px 0 0;padding-top:34px;border-top:1px solid var(--hair)}
h2{font-size:clamp(23px,3vw,31px);margin:0 0 10px;letter-spacing:-.015em;font-weight:600}
h3.sub{font-size:14px;letter-spacing:.09em;text-transform:uppercase;color:var(--faint);
  margin:34px 0 12px;font-weight:600}
.spek{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:1px;
  background:var(--hair);border:1px solid var(--hair);margin-top:20px}
.skgroup{background:var(--surface);padding:18px}
.skgroup h3{margin:0 0 12px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--accent);font-weight:700}
.skgroup dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:7px 16px}
.skgroup dt{color:var(--muted);font-size:13.5px}
.skgroup dd{margin:0;font-size:13.5px}

.tw{overflow-x:auto;border:1px solid var(--hair);background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:640px}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--hair);vertical-align:top}
th{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);
  font-weight:600;white-space:nowrap;background:var(--paper)}
td.num,th.num{text-align:right;font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
tfoot td{font-weight:600;border-bottom:none;background:var(--paper)}
tbody tr:hover{background:color-mix(in srgb,var(--accent) 7%,transparent)}
.bar{display:inline-block;width:64px;height:6px;background:var(--hair);margin-right:8px;
  vertical-align:middle}
.bar i{display:block;height:100%}
.bar.ok i{background:var(--ok)} .bar.warn i{background:var(--warn)} .bar.crit i{background:var(--crit)}

.wastebar{display:flex;gap:22px;flex-wrap:wrap;margin:18px 0 6px;padding:14px 16px;
  background:var(--surface);border:1px solid var(--hair)}
.wastebar label{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted)}
.wastebar input{width:66px;font:inherit;font-family:"IBM Plex Mono",monospace;padding:4px 7px;
  border:1px solid var(--line);background:var(--paper);color:var(--ink);text-align:right}
.wastebar input:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.tot{margin:20px 0 0;font-size:15px}
.tot b{font-family:"IBM Plex Mono",monospace;font-size:19px}
.callout{margin-top:22px;padding:14px 16px;border-left:3px solid var(--accent);
  background:var(--surface);font-size:13.5px;color:var(--muted)}
.callout b{color:var(--ink)}
.foot{margin-top:64px;padding-top:20px;border-top:1px solid var(--hair);display:flex;
  justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--faint)}
"""+CSS_3D+r"""
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media (max-width:640px){.frame{height:52vh}.wrap{padding:0 14px 60px}}
"""

JS = r"""
// layer toggle
document.querySelectorAll('.chip input').forEach(cb=>{
  cb.addEventListener('change',()=>{
    const sec=document.getElementById(cb.dataset.sheet);
    sec.querySelectorAll('.'+cb.dataset.lay).forEach(g=>g.classList.toggle('hidden',!cb.checked));
  });
});
// pan + zoom + pinch (dua jari) + ketuk-dua-kali untuk reset
document.querySelectorAll('.frame').forEach(fr=>{
  const pan=fr.querySelector('.pan');
  let s=1,tx=0,ty=0,raf=0;
  const pts=new Map(); let p0=0,s0=1,m0=null,moved=0,lastTap=0;
  const apply=()=>{ if(raf) return; raf=requestAnimationFrame(()=>{raf=0;
    pan.style.transform=`translate3d(${tx}px,${ty}px,0) scale(${s})`;}); };
  const zoomAt=(mx,my,ns)=>{ns=Math.min(9,Math.max(.5,ns));
    tx=mx-(mx-tx)*(ns/s); ty=my-(my-ty)*(ns/s); s=ns; apply();};
  const reset=()=>{s=1;tx=0;ty=0;apply();};
  // isi layar: perbesar sampai gambar mengisi bingkai (buat baca denah panjang di HP)
  window.__fit=window.__fit||{};
  window.__fit[fr.dataset.frame]=mode=>{
    if(mode==='reset'){reset();return true;}
    const R=fr.getBoundingClientRect(), vb=pan.querySelector('svg').viewBox.baseVal;
    if(!vb.width||R.width<40||R.height<40) return false;
    const asp=vb.width/vb.height;
    const dw = (R.width/R.height>asp) ? R.height*asp : R.width;
    const dh = dw/asp;
    const ns = Math.min(4, Math.max(1, Math.max(R.width/dw, R.height/dh)));
    s=ns; tx=R.width/2-(R.width/2)*s; ty=R.height/2-(R.height/2)*s; apply(); return true;
  };
  const mid=()=>{const a=[...pts.values()];
    return {x:(a[0].x+a[1].x)/2,y:(a[0].y+a[1].y)/2,d:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)};};

  fr.addEventListener('wheel',e=>{
    e.preventDefault();
    const r=fr.getBoundingClientRect();
    zoomAt(e.clientX-r.left,e.clientY-r.top,s*(e.deltaY<0?1.14:1/1.14));
  },{passive:false});

  fr.addEventListener('pointerdown',e=>{
    pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
    fr.setPointerCapture(e.pointerId);
    if(pts.size===1){moved=0; fr.dataset.moved='0'; fr.classList.add('drag');}
    if(pts.size===2){const m=mid(); p0=m.d; s0=s; m0=m;}
  });
  fr.addEventListener('pointermove',e=>{
    const p=pts.get(e.pointerId); if(!p) return;
    const dx=e.clientX-p.x, dy=e.clientY-p.y; p.x=e.clientX; p.y=e.clientY;
    if(pts.size>=2){
      const r=fr.getBoundingClientRect(), m=mid();
      if(p0>8) zoomAt(m.x-r.left,m.y-r.top,s0*(m.d/p0));
      tx+=m.x-m0.x; ty+=m.y-m0.y; m0=m; apply(); return;
    }
    moved+=Math.abs(dx)+Math.abs(dy);
    fr.dataset.moved = moved>6?'1':'0';
    tx+=dx; ty+=dy; apply();
  });
  const up=e=>{
    const had=pts.size; pts.delete(e.pointerId);
    if(pts.size<2) p0=0;
    if(pts.size===0){
      fr.classList.remove('drag');
      if(had===1 && moved<6){
        const now=performance.now();
        if(now-lastTap<300){ reset(); lastTap=0; }
        else lastTap=now;
      }
    }
  };
  fr.addEventListener('pointerup',up); fr.addEventListener('pointercancel',up);

  const btn=document.querySelector(`[data-reset="${fr.dataset.frame}"]`);
  if(btn) btn.addEventListener('click',()=>{
    reset();
    document.getElementById(fr.dataset.frame).querySelectorAll('.chip input').forEach(cb=>{
      cb.checked=true;
      document.getElementById(cb.dataset.sheet).querySelectorAll('.'+cb.dataset.lay)
        .forEach(g=>g.classList.remove('hidden'));
    });
  });
});
__XLSXJS__
// ---------------- BOQ: hitung, harga, dan edit ----------------
const $=id=>document.getElementById(id);
const f=(n,d=1)=>Number(n||0).toLocaleString('id-ID',{minimumFractionDigits:d,maximumFractionDigits:d});
const rp=n=>'Rp ' + Math.round(n||0).toLocaleString('id-ID');
const pn=s=>{
  s=String(s==null?'':s).trim().replace(/[^\d.,-]/g,'');
  if(s.indexOf(',')>=0) s=s.replace(/\./g,'').replace(',','.');
  else if(!/\.\d{1,2}$/.test(s)) s=s.replace(/\./g,'');
  const v=parseFloat(s); return isFinite(v)?v:0;
};
const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

if($('tH')){
const KEY='boq-metta-v2';
const BASE={hollow:DATA.hollow, plate:DATA.plate, other:DATA.other||[]};
const clone=o=>JSON.parse(JSON.stringify(o));
const OFFER0=()=>({
  on:false, edit:false,
  co:{nm:'', addr:'', tel:'', email:'', logo:''},
  cl:{nm:'', loc:'Gedung METTA \u2014 Lantai 4 (+16.00)', no:'', rev:'0'},
  dt:{issue:'', valid:14, start:'', end:''},
  terms:[],
  sched:[{nm:'Fabrikasi di bengkel', w0:1, dur:3},
         {nm:'Pengiriman ke site', w0:4, dur:1},
         {nm:'Erection & sambungan', w0:4, dur:2},
         {nm:'Finishing cat & railing', w0:6, dur:1},
         {nm:'Serah terima', w0:7, dur:1}],
  scope:['Fabrikasi & pemasangan rangka tribun baja hollow sesuai gambar kerja S-01 s/d S-12',
         'Pelat dek bordes, papan dudukan pinus, railing, tangga, dan sandaran',
         'Pengecatan lengkap (primer + finish) dan pembersihan area kerja'],
  excl:['Listrik kerja & air kerja di lokasi', 'Akses alat angkat / lift barang gedung',
        'Izin kerja gedung dan biaya administrasi pengelola', 'Pekerjaan sipil & perbaikan lantai eksisting'],
  tnc:['Harga berlaku selama masa berlaku penawaran di atas.',
       'Harga sudah termasuk PPN sesuai rekap.',
       'Perubahan lingkup dihitung sebagai pekerjaan tambah/kurang.'],
  sign:{nm:'', role:''}
});
let S={price:false, mode:'satuan', unitAll:'auto', edit:false, wH:5, wP:10, bar:6, ohp:10, ppn:11,
       rev:DATA.rev, rows:clone(BASE)};
let migrated=0;

function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
function load(){
  try{
    const raw=localStorage.getItem(KEY); if(!raw) return;
    const o=JSON.parse(raw);
    if(!o || !o.rows || !o.rows.hollow) return;
    if(o.rev === DATA.rev){ S=Object.assign(S,o); return; }
    // Model sudah direvisi sejak terakhir dibuka. Kuantitas WAJIB ikut model baru,
    // tapi harga yang sudah susah payah diisi dipindahkan berdasarkan nama item.
    const harga={};
    ['hollow','plate','other'].forEach(k=>(o.rows[k]||[]).forEach(r=>{
      if(r && r.p!=null && r.p!=='') harga[k+'|'+r.nm]=r.p; }));
    S=Object.assign(S,o,{rows:clone(BASE), rev:DATA.rev});
    let pindah=0;
    ['hollow','plate','other'].forEach(k=>S.rows[k].forEach(r=>{
      const p=harga[k+'|'+r.nm];
      if(p!=null){ r.p=p; pindah++; }
    }));
    migrated=pindah+1;   // >0 menandakan terjadi migrasi, walau tak ada harga yang pindah
    save();
  }catch(e){}
}
load();
document.addEventListener('change',e=>{
  const t=e.target;
  if(t.id==='unitAll'){ S.unitAll=t.value; save(); render(); return; }
  if(t.classList && t.classList.contains('usel')){
    const tb=t.dataset.t==='H'?S.rows.hollow:S.rows.plate;
    const row=tb[+t.dataset.i]; if(row){ row.u=t.value; save(); render(); }
  }
});

// ---- satuan harga per mode ----
function basisH(r){
  const Lw=r.L*(1+S.wH/100), kg=Lw*(r.kg||0), bars=Math.ceil(Lw/(S.bar||6));
  if(S.mode==='ringkas') return {q:Lw, un:'m', kg, bars, Lw};
  return {q:kg, un:'kg', kg, bars, Lw};
}
function basisP(r){
  const Aw=r.A*(1+S.wP/100), kg=Aw*((r.t||0)*7.85+(r.sur||0)), sh=Math.ceil(Aw/DATA.sheetA);
  if(S.mode==='ringkas') return {q:Aw, un:'m²', kg, sh, Aw};
  if(S.mode==='perkg')   return {q:kg,  un:'kg', kg, sh, Aw};
  return {q:sh, un:'lembar', kg, sh, Aw};
}
const basisO=r=>({q:+r.q||0, un:r.un||'bh'});

// ---- satuan harga: pilihan global + override per baris ----
const UNITS={H:[['kg','kg'],['m','m\u02b9'],['btg','lonjor'],['bh','buah']],
             P:[['kg','kg'],['m2','m\u00b2'],['m3','m\u00b3'],['lbr','lembar'],['bh','buah']]};
const ULAB={kg:'kg',m:'m\u02b9',btg:'lonjor',bh:'buah',m2:'m\u00b2',m3:'m\u00b3',lbr:'lembar'};
const GMAP={H:{kg:'kg',m:'m',m2:null,m3:null,btg:'btg',bh:'bh'},
            P:{kg:'kg',m:null,m2:'m2',m3:'m3',btg:'lbr',bh:'bh'}};
function unitOf(t,r){
  if(r.u && (UNITS[t]||[]).some(x=>x[0]===r.u)) return r.u;
  if(S.unitAll && S.unitAll!=='auto'){const m=GMAP[t][S.unitAll]; if(m) return m;}
  if(t==='H') return S.mode==='ringkas'?'m':'kg';
  return S.mode==='ringkas'?'m2':(S.mode==='perkg'?'kg':'lbr');
}
function qtyU(t,r,B,u){
  if(t==='H') return u==='m'?B.Lw : u==='btg'?B.bars : u==='bh'?(+r.n||0) : B.kg;
  return u==='m2'?B.Aw : u==='m3'?B.Aw*((+r.t||0)/1000) : (u==='lbr'||u==='bh')?B.sh : B.kg;
}
const usel=(t,i,u)=>'<td class="usel-cell"><select class="usel" data-t="'+t+'" data-i="'+i+'">'
  + UNITS[t].map(([v,l])=>`<option value="${v}"${v===u?' selected':''}>${l}</option>`).join('')
  + '</select></td>';

// ---- odometer + bar volume (transform saja, tidak memicu layout) ----
const REDUCE = matchMedia('(prefers-reduced-motion:reduce)').matches;
const ODO={};
const odo=(k,txt)=>`<span class="odo" data-k="${k}">${esc(txt)}</span>`;
function paintOdo(){
  const els=[...document.querySelectorAll('.odo')];
  els.forEach((el,n)=>{
    const k=el.dataset.k, txt=el.textContent, prev=ODO[k];
    ODO[k]=txt;
    if(REDUCE || prev===undefined || prev===txt || n>24) return;
    const pad=prev.length<txt.length ? prev.padStart(txt.length,' ') : prev.slice(-txt.length);
    let h='';
    for(let i=0;i<txt.length;i++){
      const a=pad[i]||' ', b=txt[i];
      h += (a===b) ? `<span class="oc">${esc(b)}</span>`
                   : `<span class="oc roll"><b><i>${esc(a)}</i><i>${esc(b)}</i></b></span>`;
    }
    el.innerHTML=h;
    const rolls=el.querySelectorAll('.roll');
    requestAnimationFrame(()=>rolls.forEach((r,i)=>{
      r.style.transitionDelay=(i*26)+'ms'; r.classList.add('go');}));
  });
}
const vbar=(v,g)=>`<span class="vb" data-v="${v}" data-g="${g}"></span>`;
function paintBars(){
  ['H','P'].forEach(g=>{
    const els=[...document.querySelectorAll('.vb[data-g="'+g+'"]')];
    if(!els.length) return;
    const mx=Math.max(...els.map(e=>+e.dataset.v||0))||1;
    els.forEach(e=>{
      const s2=Math.max(0.02,(+e.dataset.v||0)/mx);
      if(REDUCE){ e.style.transform='scaleX('+s2+')'; return; }
      e.style.transform='scaleX(0)';
      requestAnimationFrame(()=>{e.style.transform='scaleX('+s2+')';});
    });
  });
}

const ed=(t,i,fld,val,cls)=>S.edit
  ? `<td class="${cls||''} cel" contenteditable="plaintext-only" data-t="${t}" data-i="${i}" data-f="${fld}">${esc(val)}</td>`
  : `<td class="${cls||''}">${esc(val)}</td>`;
const price=(t,i,r)=>S.price
  ? `<td class="num"><input class="pin" type="number" min="0" step="1000" data-t="${t}" data-i="${i}" value="${r.p==null?'':r.p}"></td>`
  : '';
const jml=v=>S.price?`<td class="num">${rp(v)}</td>`:'';
const del=(t,i)=>S.edit?`<td class="num"><button type="button" class="delrow" data-t="${t}" data-i="${i}" title="Hapus baris">×</button></td>`:'';

function head(cols){
  return '<tr>'+cols.map(c=>`<th class="${c[1]||''}">${c[0]}</th>`).join('')+'</tr>';
}

function render(){
  const wH=1+S.wH/100, wP=1+S.wP/100, BAR=S.bar||6;
  let sumH=0,sumBar=0,costH=0;

  // ---- profil hollow ----
  let cols=[['Elemen'],['Profil'],['Btg','num'],['Panjang (m)','num'],['+waste','num'],
            ['kg/m','num'],['Berat (kg)','num'],['Lonjor','num']];
  if(S.price) cols=cols.concat([['Satuan harga'],['Harga satuan','num'],['Jumlah','num']]);
  cols.push(['Catatan']); if(S.edit) cols.push(['','num']);
  $('tH').tHead.innerHTML=head(cols);
  let tb='';
  S.rows.hollow.forEach((r,i)=>{
    const B=basisH(r); sumH+=B.kg; sumBar+=B.bars;
    const u=unitOf('H',r), qu=qtyU('H',r,B,u);
    const j=(+r.p||0)*qu; costH+=j;
    tb+='<tr>'+ed('H',i,'nm',r.nm)+ed('H',i,'pr',r.pr)+ed('H',i,'n',r.n,'num')
      + ed('H',i,'L',f(r.L,2),'num')
      + `<td class="num">${f(B.Lw,2)}</td>`+ed('H',i,'kg',f(r.kg,2),'num')
      + `<td class="num">${vbar(B.kg,'H')}${f(B.kg,0)}</td><td class="num">${B.bars}</td>`
      + (S.price?usel('H',i,u):'')+price('H',i,r)+jml(j)+ed('H',i,'note',r.note)+del('H',i)+'</tr>';
  });
  $('tH').tBodies[0].innerHTML=tb;
  $('tH').tFoot.innerHTML='<tr><td colspan="6">Subtotal profil hollow</td>'
    + `<td class="num">${odo('sH',f(sumH,0)+' kg')}</td><td class="num">${sumBar}</td>`
    + (S.price?`<td></td><td></td><td class="num">${odo('cH',rp(costH))}</td>`:'')
    + '<td></td>'+(S.edit?'<td></td>':'')+'</tr>';

  // ---- pelat ----
  let sumP=0,sumSh=0,costP=0;
  cols=[['Elemen'],['Tebal (mm)','num'],['Luas (m²)','num'],['+waste','num'],
        ['Berat (kg)','num'],['Lembar 1220×2440','num']];
  if(S.price) cols=cols.concat([['Satuan harga'],['Harga satuan','num'],['Jumlah','num']]);
  cols.push(['Catatan']); if(S.edit) cols.push(['','num']);
  $('tP').tHead.innerHTML=head(cols);
  tb='';
  S.rows.plate.forEach((r,i)=>{
    const B=basisP(r); sumP+=B.kg; sumSh+=B.sh;
    const u=unitOf('P',r), qu=qtyU('P',r,B,u);
    const j=(+r.p||0)*qu; costP+=j;
    tb+='<tr>'+ed('P',i,'nm',r.nm)+ed('P',i,'t',r.t,'num')+ed('P',i,'A',f(r.A,2),'num')
      + `<td class="num">${f(B.Aw,2)}</td><td class="num">${vbar(B.kg,'P')}${f(B.kg,0)}</td>`
      + `<td class="num">${B.sh}</td>`
      + (S.price?usel('P',i,u):'')+price('P',i,r)+jml(j)+ed('P',i,'note',r.note)+del('P',i)+'</tr>';
  });
  $('tP').tBodies[0].innerHTML=tb;
  $('tP').tFoot.innerHTML='<tr><td colspan="4">Subtotal pelat</td>'
    + `<td class="num">${odo('sP',f(sumP,0)+' kg')}</td><td class="num">${sumSh}</td>`
    + (S.price?`<td></td><td></td><td class="num">${odo('cP',rp(costP))}</td>`:'')
    + '<td></td>'+(S.edit?'<td></td>':'')+'</tr>';

  // ---- material lain ----
  let costO=0;
  cols=[['Item'],['Jumlah','num'],['Satuan']];
  if(S.price) cols=cols.concat([['Harga satuan','num'],['Jumlah','num']]);
  cols.push(['Catatan']); if(S.edit) cols.push(['','num']);
  $('tO').tHead.innerHTML=head(cols);
  tb='';
  S.rows.other.forEach((r,i)=>{
    const B=basisO(r); const j=(+r.p||0)*B.q; costO+=j;
    tb+='<tr>'+ed('O',i,'nm',r.nm)+ed('O',i,'q',f(r.q,(r.q%1)?3:0),'num')+ed('O',i,'un',r.un)
      + price('O',i,r)+jml(j)+ed('O',i,'note',r.note)+del('O',i)+'</tr>';
  });
  $('tO').tBodies[0].innerHTML=tb;
  $('tO').tFoot.innerHTML = S.price
    ? `<tr><td colspan="${3+(S.price?1:0)}">Subtotal material lain</td>`
      + `<td class="num">${odo('cO',rp(costO))}</td><td></td>${S.edit?'<td></td>':''}</tr>`
    : '';

  $('grand').innerHTML=odo('grand',f((sumH+sumP)/1000,2)+' ton');
  const _sub=costH+costP+costO, _oh=_sub*S.ohp/100, _pre=_sub+_oh, _tax=_pre*S.ppn/100;
  TOT={costH:costH,costP:costP,costO:costO,sub:_sub,oh:_oh,pre:_pre,tax:_tax,
       total:_pre+_tax,kg:sumH+sumP};

  // ---- rekap harga ----
  const rk=$('rekap');
  if(S.price){
    const sub=costH+costP+costO;
    let rows=[['Profil hollow',costH],['Pelat baja',costP],['Material lain',costO]];
    let html='<h3 class="sub">Rekapitulasi biaya</h3><div class="tw"><table><tbody>';
    rows.forEach((r,ri)=>html+=`<tr><td>${r[0]}</td><td class="num">${odo('rk'+ri,rp(r[1]))}</td></tr>`);
    html+=`<tr><td><b>Subtotal</b></td><td class="num"><b>${odo('rksub',rp(sub))}</b></td></tr>`;
    let total=sub;
    if(S.mode!=='ringkas'){
      const oh=sub*S.ohp/100, pre=sub+oh, tax=pre*S.ppn/100; total=pre+tax;
      html+=`<tr><td>Overhead &amp; keuntungan ${S.ohp}%</td><td class="num">${rp(oh)}</td></tr>`
          + `<tr><td>Jumlah sebelum pajak</td><td class="num">${rp(pre)}</td></tr>`
          + `<tr><td>PPN ${S.ppn}%</td><td class="num">${rp(tax)}</td></tr>`;
    }
    html+=`</tbody><tfoot><tr><td>TOTAL</td><td class="num">${odo('rktot',rp(total))}</td></tr>`;
    const kg=sumH+sumP;
    html+=`<tr><td>Biaya per kg baja</td><td class="num">${kg?rp(total/kg):'—'}</td></tr>`;
    html+='</tfoot></table></div>';
    rk.innerHTML=html; rk.hidden=false;
  } else { rk.innerHTML=''; rk.hidden=true; }

  const rn=$('revNote');
  if(rn){
    if(migrated){
      rn.innerHTML='Kuantitas di tabel ini baru saja disesuaikan dengan <b>revisi terakhir model</b>. '
        + (migrated>1 ? 'Harga satuan yang sudah kamu isi tetap dipertahankan untuk item yang namanya sama. '
                      : '')
        + 'Kalau kamu sengaja mengedit tabel sebelumnya, editan itu diganti — tekan Reset untuk memastikan.';
      rn.hidden=false;
    } else rn.hidden=true;
  }
  document.querySelectorAll('.ponly').forEach(e=>e.hidden=!S.price);
  $('segMode').hidden=!S.price;
  const ua=$('unitAll'); if(ua) ua.value=S.unitAll||'auto';
  paintOdo(); paintBars(); if(window.__ofCalc) __ofCalc();
  document.querySelectorAll('.addrow').forEach(e=>e.hidden=!S.edit);
  document.querySelectorAll('#segMode button').forEach(bm=>
    bm.classList.toggle('on', bm.dataset.mode===S.mode));
  cutlist();
}

function cutlist(){
  const tc=$('tCut'); if(!tc) return;
  const tb=tc.tBodies[0]; tb.innerHTML='';
  S.rows.hollow.forEach(r=>{
    const B=basisH(r), buy=B.bars*(S.bar||6);
    tb.insertAdjacentHTML('beforeend',
      `<tr><td>${esc(r.nm)} — ${esc(r.pr)}</td><td class="num">${f(r.L,1)} m</td>
       <td class="num">${B.bars} lonjor (${f(buy,1)} m)</td>
       <td class="num">${f(buy-r.L,1)} m</td><td>lonjor ${S.bar} m</td></tr>`);
  });
  const byT={};
  S.rows.plate.forEach(r=>{byT[r.t]=(byT[r.t]||0)+(+r.A||0)});
  Object.entries(byT).forEach(([t,A])=>{
    const Aw=A*(1+S.wP/100), sh=Math.ceil(Aw/DATA.sheetA), buy=sh*DATA.sheetA;
    tb.insertAdjacentHTML('beforeend',
      `<tr><td>Pelat ${t} mm</td><td class="num">${f(A,2)} m²</td>
       <td class="num">${sh} lembar (${f(buy,2)} m²)</td>
       <td class="num">${f(buy-A,2)} m²</td><td>lembar 1220 × 2440</td></tr>`);
  });
}

// ---- interaksi ----
const arr=t=>t==='H'?S.rows.hollow:t==='P'?S.rows.plate:S.rows.other;
const NUMF={n:1,L:1,kg:1,t:1,A:1,q:1};

document.addEventListener('input',e=>{
  const el=e.target;
  if(el.classList && el.classList.contains('pin')){
    const r=arr(el.dataset.t)[+el.dataset.i];
    if(r){ r.p=el.value===''?null:+el.value; save();
      const keep=document.activeElement; render();
      const again=document.querySelector(`.pin[data-t="${el.dataset.t}"][data-i="${el.dataset.i}"]`);
      if(again && keep===el) again.focus();
    }
    return;
  }
  if(['wH','wP','bar','ohp','ppn'].indexOf(el.id)>=0){
    S[el.id]=+el.value||0; save(); render();
  }
});
document.addEventListener('blur',e=>{
  const el=e.target;
  if(!el.classList || !el.classList.contains('cel')) return;
  const r=arr(el.dataset.t)[+el.dataset.i]; if(!r) return;
  const fld=el.dataset.f;
  r[fld]= NUMF[fld] ? pn(el.textContent) : el.textContent.trim();
  save(); render();
}, true);

document.addEventListener('click',e=>{
  const b=e.target.closest ? e.target.closest('button') : null; if(!b) return;
  if(b.dataset.mode){ S.mode=b.dataset.mode; save(); render(); return; }
  if(b.dataset.add){
    const t=b.dataset.add;
    if(t==='H') S.rows.hollow.push({nm:'Item baru',pr:'',n:1,L:0,kg:0,note:''});
    if(t==='P') S.rows.plate.push({nm:'Item baru',t:0,A:0,note:''});
    if(t==='O') S.rows.other.push({nm:'Item baru',q:0,un:'bh',note:''});
    save(); render(); return;
  }
  if(b.classList.contains('delrow')){
    arr(b.dataset.t).splice(+b.dataset.i,1); save(); render(); return;
  }
  if(b.id==='exXls'){ copyTSV(b); return; }
  if(b.id==='exPdf'){ toPrint(b); return; }
  if(b.id==='exJson'){ copyJSON(b); return; }
  if(b.id==='exXlsx'){ downloadXlsx(b); return; }
  if(b.id==='exLoad'){ const bx=$('exLoadBox'); bx.hidden=!bx.hidden;
    if(!bx.hidden) $('exCode').focus(); return; }
  if(b.id==='exApply'){ applyCode(); return; }
  if(b.id==='boqReset'){
    if(b.dataset.armed){ 
      S={price:S.price,mode:S.mode,unitAll:S.unitAll,edit:S.edit,wH:5,wP:10,bar:6,ohp:10,ppn:11,
         rev:DATA.rev,rows:clone(BASE)};
      migrated=0;
      try{ localStorage.removeItem(KEY); }catch(e2){}
      $('wH').value=5; $('wP').value=10; $('bar').value=6; $('ohp').value=10; $('ppn').value=11;
      b.textContent='Reset ke default'; delete b.dataset.armed; render();
    } else {
      b.dataset.armed='1'; b.textContent='Yakin? klik lagi';
      setTimeout(()=>{ if(b.dataset.armed){ b.textContent='Reset ke default'; delete b.dataset.armed; } },4000);
    }
  }
});

['tgPrice','tgEdit','tgExport'].forEach(id=>{
  const el=$(id); if(!el) return;
  el.addEventListener('change',()=>{
    if(id==='tgPrice') S.price=el.checked;
    else if(id==='tgEdit') S.edit=el.checked;
    else { S.exp=el.checked; $('exportbox').hidden=!el.checked; }
    save(); render();
  });
});


// ---- unduhan berkas nyata hanya jalan di luar sandbox artifact ----
const CAN_DL = !/(^|\.)claude\.ai$/i.test(location.hostname);
function projName(){
  const v=($('exProj')&&$('exProj').value||'').trim();
  return v || 'BOQ';
}
function slug(s){ return s.replace(/[^\wÀ-ɏ -]/g,'').replace(/\s+/g,'-').slice(0,60) || 'BOQ'; }

function workbook(){
  const s=XL.S, P=projName();
  // ---------- INPUT ----------
  const inp=[];
  inp[0]=[{t:'PARAMETER — ubah di sini, seluruh BOQ ikut berubah',s:s.title}];
  inp[1]=[{t:P}];
  const par=[['Waste profil hollow',S.wH/100],['Waste pelat baja',S.wP/100],
             ['Panjang lonjor hollow (m)',S.bar],['Luas lembar pelat (m²)',DATA.sheetA],
             ['Berat jenis pelat (kg/m²/mm)',7.85],['Overhead & keuntungan',S.ohp/100],
             ['PPN',S.ppn/100]];
  par.forEach((p,i)=>{ inp[i+2]=[{t:p[0]}, {n:p[1], s:s.n2}]; });
  inp[10]=[{t:'Isi kolom Harga Satuan (kuning) di lembar BOQ. Kolom lain rumus.'}];
  inp[11]=[{t:'Baris B3:B9 di lembar ini dipakai seluruh rumus BOQ.'}];

  // ---------- BOQ ----------
  const W_H='INPUT!$B$3', W_P='INPUT!$B$4', BARC='INPUT!$B$5',
        SHA='INPUT!$B$6', RHO='INPUT!$B$7';
  const rows=[];
  rows[0]=[{t:'BILL OF QUANTITY — '+P, s:s.title}];
  rows[1]=[{t:'Kuantitas dari model METTA.rvt · mode harga: '+S.mode
            +' · satuan: '+(S.unitAll==='auto'?'bawaan tiap baris':ULAB[S.unitAll]||S.unitAll)}];
  const H=['No','Uraian pekerjaan','Spesifikasi','Btg/Bh','Volume model','Volume + waste',
           'Satuan','Berat (kg)','Beli (lonjor/lembar)','Harga satuan','Satuan harga','Jumlah','Catatan'];
  rows[3]=H.map(t=>({t:t,s:s.head}));
  let r=4, no=0;
  const ring = S.mode==='ringkas', perkg = S.mode==='perkg';

  rows[r]=[{t:'A.  PROFIL HOLLOW', s:s.sec}]; r++;
  const aStart=r+1;
  S.rows.hollow.forEach(x=>{
    no++; const R=r+1;
    rows[r]=[{n:no},{t:x.nm},{t:x.pr},{n:+x.n||0},{n:+x.L||0,s:s.n2},
             {f:`E${R}*(1+${W_H})`,s:s.n2},{t:'m'},
             {f:`F${R}*${(+x.kg||0)}`,s:s.n0},{f:`ROUNDUP(F${R}/${BARC},0)`,s:s.n0},
             {n:(x.p==null?null:+x.p),s:s.inp},{t:'Rp / '+ULAB[unitOf('H',x)]},
             {f:(uu=>uu==='m'?`F${R}*J${R}`:uu==='btg'?`I${R}*J${R}`:uu==='bh'?`D${R}*J${R}`
                 :`H${R}*J${R}`)(unitOf('H',x)),s:s.rp},{t:x.note}];
    r++;
  });
  const aEnd=r, aSub=r+1;
  rows[r]=[null,{t:'Subtotal A — profil hollow',s:s.bold},null,null,null,null,null,
           {f:`SUM(H${aStart}:H${aEnd})`,s:s.n0},{f:`SUM(I${aStart}:I${aEnd})`,s:s.n0},
           null,null,{f:`SUM(L${aStart}:L${aEnd})`,s:s.rp}];
  r+=2;

  rows[r]=[{t:'B.  PELAT BAJA', s:s.sec}]; r++;
  const bStart=r+1;
  S.rows.plate.forEach(x=>{
    no++; const R=r+1;
    rows[r]=[{n:no},{t:x.nm},{t:'tebal '+(x.t)+' mm'},null,{n:+x.A||0,s:s.n2},
             {f:`E${R}*(1+${W_P})`,s:s.n2},{t:'m²'},
             {f:`F${R}*(${(+x.t||0)}*${RHO}+${(+x.sur||0)})`,s:s.n0},{f:`ROUNDUP(F${R}/${SHA},0)`,s:s.n0},
             {n:(x.p==null?null:+x.p),s:s.inp},
             {t:'Rp / '+ULAB[unitOf('P',x)]},
             {f:(uu=>uu==='m2'?`F${R}*J${R}`:uu==='m3'?`F${R}*${(+x.t||0)}/1000*J${R}`
                 :(uu==='lbr'||uu==='bh')?`I${R}*J${R}`:`H${R}*J${R}`)(unitOf('P',x)),s:s.rp},{t:x.note}];
    r++;
  });
  const bEnd=r, bSub=r+1;
  rows[r]=[null,{t:'Subtotal B — pelat baja',s:s.bold},null,null,null,null,null,
           {f:`SUM(H${bStart}:H${bEnd})`,s:s.n0},{f:`SUM(I${bStart}:I${bEnd})`,s:s.n0},
           null,null,{f:`SUM(L${bStart}:L${bEnd})`,s:s.rp}];
  r+=2;

  rows[r]=[{t:'C.  MATERIAL LAIN', s:s.sec}]; r++;
  const cStart=r+1;
  S.rows.other.forEach(x=>{
    no++; const R=r+1;
    rows[r]=[{n:no},{t:x.nm},null,null,{n:+x.q||0,s:s.n2},{f:`E${R}`,s:s.n2},{t:x.un},
             null,null,{n:(x.p==null?null:+x.p),s:s.inp},{t:'Rp / '+(x.un||'bh')},
             {f:`F${R}*J${R}`,s:s.rp},{t:x.note}];
    r++;
  });
  const cEnd=r, cSub=r+1;
  rows[r]=[null,{t:'Subtotal C — material lain',s:s.bold},null,null,null,null,null,null,null,
           null,null,{f:`SUM(L${cStart}:L${cEnd})`,s:s.rp}];

  // ---------- REKAP ----------
  const rk=[];
  rk[0]=[{t:'REKAPITULASI BIAYA — '+P, s:s.title}];
  rk[2]=[{t:'Bagian',s:s.head},{t:'Uraian',s:s.head},{t:'Jumlah',s:s.head}];
  rk[3]=[{t:'A'},{t:'Profil hollow'},{f:`BOQ!L${aSub}`,s:s.rp}];
  rk[4]=[{t:'B'},{t:'Pelat baja'},{f:`BOQ!L${bSub}`,s:s.rp}];
  rk[5]=[{t:'C'},{t:'Material lain'},{f:`BOQ!L${cSub}`,s:s.rp}];
  rk[6]=[null,{t:'Subtotal',s:s.bold},{f:'SUM(C4:C6)',s:s.rp}];
  if(ring){
    rk[7]=[null,{t:'TOTAL',s:s.bold},{f:'C7',s:s.rp}];
    rk[9]=[null,{t:'Berat baja total (kg)'},{f:`BOQ!H${aSub}+BOQ!H${bSub}`,s:s.n0}];
    rk[10]=[null,{t:'Biaya per kg baja'},{f:'IF(C10=0,0,C8/C10)',s:s.rp}];
  } else {
    rk[7]=[null,{t:'Overhead & keuntungan'},{f:'C7*INPUT!$B$8',s:s.rp}];
    rk[8]=[null,{t:'Jumlah sebelum pajak',s:s.bold},{f:'C7+C8',s:s.rp}];
    rk[9]=[null,{t:'PPN'},{f:'C9*INPUT!$B$9',s:s.rp}];
    rk[10]=[null,{t:'TOTAL',s:s.bold},{f:'C9+C10',s:s.rp}];
    rk[12]=[null,{t:'Berat baja total (kg)'},{f:`BOQ!H${aSub}+BOQ!H${bSub}`,s:s.n0}];
    rk[13]=[null,{t:'Biaya per kg baja'},{f:'IF(C13=0,0,C11/C13)',s:s.rp}];
  }

  return XL.book([
    {name:'INPUT', rows:inp, cols:[34,16,40]},
    {name:'BOQ',   rows:rows, cols:[5,34,20,8,13,14,9,12,14,14,13,16,44]},
    {name:'REKAP', rows:rk,  cols:[8,34,20]},
  ]);
}

function downloadXlsx(btn){
  try{
    const bytes=workbook();
    const blob=new Blob([bytes],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
    const url=URL.createObjectURL(blob), a=document.createElement('a');
    a.href=url; a.download=slug(projName())+'.xlsx';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),4000);
    const lab=btn.querySelector('b'), o=lab.textContent;
    lab.textContent='Berkas dibuat'; setTimeout(()=>lab.textContent=o,2200);
  }catch(e){
    btn.querySelector('span').textContent='Gagal membuat berkas: '+e.message;
  }
}

function applyCode(){
  const msg=$('exMsg'), raw=($('exCode').value||'').trim();
  const i=raw.indexOf('{');
  try{
    if(i<0) throw new Error('kode tidak dikenali');
    const o=JSON.parse(raw.slice(i));
    if(!o || !o.hollow || !o.plate) throw new Error('isi kode tidak lengkap');
    S.rows={hollow:o.hollow, plate:o.plate, other:o.other||[]};
    ['wH','wP','bar','ohp','ppn'].forEach(k=>{ if(typeof o[k]==='number') S[k]=o[k]; });
    if(o.mode) S.mode=o.mode;
  if(o.offer) S.offer=Object.assign(OFFER0(), o.offer);
    $('wH').value=S.wH; $('wP').value=S.wP; $('bar').value=S.bar;
    $('ohp').value=S.ohp; $('ppn').value=S.ppn;
    save(); render();
    msg.textContent='Kode diterapkan.'; msg.className='exmsg ok';
  }catch(e){
    msg.textContent='Gagal: '+e.message; msg.className='exmsg bad';
  }
  setTimeout(()=>{ msg.textContent=''; },4000);
}

function exportUI(){
  const note=$('exNote'); if(!note) return;
  document.querySelectorAll('.dlonly').forEach(e=>e.hidden=!CAN_DL);
  note.innerHTML = CAN_DL
    ? 'Berkas Excel dibuat langsung di browsermu — tidak ada data yang dikirim ke mana pun. '
      + 'Rumusnya hidup: ubah waste, harga, atau PPN di lembar <b>INPUT</b>, seluruh total ikut berubah.'
    : 'Catatan jujur: di halaman claude.ai ini unduhan berkas diblokir sandbox. PDF lewat dialog '
      + 'cetak browser, Excel lewat tempel, dan berkas .xlsx berumus dibuat dari <b>kode BOQ</b>. '
      + 'Kalau halaman ini dipasang di alamatmu sendiri, tombol unduh langsung akan muncul.';
}

// ---- cetak: sembunyikan sementara mode edit supaya sel tidak berbingkai ----
function toPrint(btn){
  const wasEdit=S.edit;
  if(wasEdit){ S.edit=false; render(); }
  document.body.classList.add('printing');
  const back=()=>{
    document.body.classList.remove('printing');
    if(wasEdit){ S.edit=true; render(); }
  };
  const mq=window.matchMedia('print');
  const off=()=>{ back(); mq.removeEventListener && mq.removeEventListener('change',onch); };
  const onch=e=>{ if(!e.matches) off(); };
  if(mq.addEventListener) mq.addEventListener('change',onch);
  addEventListener('afterprint', back, {once:true});
  setTimeout(()=>{
    try{ window.print(); }
    catch(e){ back(); btn.querySelector('span').textContent =
      'Dialog cetak diblokir di tampilan ini — buka halaman di tab browser sendiri, lalu Ctrl+P.'; }
    setTimeout(back, 1500);
  }, 60);
}

function copyJSON(btn){
  const payload={v:2, proyek:'Tribun METTA LT 4', mode:S.mode,
    wH:S.wH, wP:S.wP, bar:S.bar, ohp:S.ohp, ppn:S.ppn,
    hollow:S.rows.hollow, plate:S.rows.plate, other:S.rows.other, offer:S.offer};
  const txt='BOQ-METTA '+JSON.stringify(payload);
  const done=()=>{ const o=btn.querySelector('b').textContent;
    btn.querySelector('b').textContent='Kode tersalin';
    setTimeout(()=>btn.querySelector('b').textContent=o,2200); };
  if(navigator.clipboard && navigator.clipboard.writeText)
    navigator.clipboard.writeText(txt).then(done,()=>fallback(txt,done));
  else fallback(txt,done);
}

function copyTSV(btn){
  const out=[];
  const tbl=(id,title)=>{
    const t=$(id); if(!t) return;
    out.push(title);
    [...t.querySelectorAll('tr')].forEach(tr=>{
      out.push([...tr.children].map(td=>{
        const inp=td.querySelector('input');
        return (inp?inp.value:td.textContent).replace(/\s+/g,' ').trim();
      }).join('\t'));
    });
    out.push('');
  };
  tbl('tH','PROFIL HOLLOW'); tbl('tP','PELAT BAJA'); tbl('tO','MATERIAL LAIN');
  if(S.price){ out.push('REKAPITULASI');
    $('rekap').querySelectorAll('tr').forEach(tr=>
      out.push([...tr.children].map(td=>td.textContent.trim()).join('\t'))); }
  const txt=out.join('\n');
  const lab=btn.querySelector('b')||btn;
  const done=()=>{ const o=lab.textContent; lab.textContent='Tersalin — tempel di Excel';
    setTimeout(()=>lab.textContent=o,2200); };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).then(done,()=>fallback(txt,done));
  } else fallback(txt,done);
}
function fallback(txt,done){
  const ta=document.createElement('textarea');
  ta.value=txt; ta.style.position='fixed'; ta.style.opacity='0';
  document.body.appendChild(ta); ta.select();
  try{ document.execCommand('copy'); done(); }catch(e){}
  ta.remove();
}


// ================= PENAWARAN =================
let TOT={costH:0,costP:0,costO:0,sub:0,oh:0,pre:0,tax:0,total:0,kg:0};
const OF=()=>S.offer||(S.offer=OFFER0());
const dstr=v=>{ if(!v) return '—';
  const d=new Date(v+'T00:00:00'); if(isNaN(d)) return '—';
  const B=['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
  return d.getDate()+' '+B[d.getMonth()]+' '+d.getFullYear(); };
function addDays(v,n){ const d=new Date(v+'T00:00:00'); if(isNaN(d)) return '';
  d.setDate(d.getDate()+n); return d.toISOString().slice(0,10); }
function workdays(a,b){ if(!a||!b) return 0;
  let d=new Date(a+'T00:00:00'), e=new Date(b+'T00:00:00'), n=0;
  if(isNaN(d)||isNaN(e)||e<d) return 0;
  while(d<=e){ const w=d.getDay(); if(w!==0&&w!==6) n++; d.setDate(d.getDate()+1); }
  return n; }
const ofNo=()=>{ const o=OF(); if(o.cl.no) return o.cl.no;
  const y=(o.dt.issue||new Date().toISOString().slice(0,10)).slice(0,4);
  return 'PN/'+y+'/001'; };
const ip=(path,val,type,ph)=>`<input class="ofin" data-of="${path}" type="${type||'text'}" `
  + `value="${String(val==null?'':val).replace(/"/g,'&quot;')}" placeholder="${ph||''}">`;

function ofWeeks(){ const o=OF();
  let n=0; o.sched.forEach(r=>n=Math.max(n,(+r.w0||1)+(+r.dur||1)-1));
  return Math.max(4, Math.min(26, n)); }

function renderOffer(){
  const box=$('ofbox'); if(!box) return;
  const o=OF(); box.hidden=!o.on;
  const tg=$('tgOffer'); if(tg) tg.checked=!!o.on;
  const te=$('tgOfEdit'); if(te) te.checked=!!o.edit;
  if(!o.on){ return; }
  const ed=o.edit;
  const t=(v,ph)=>ed?'':(v||`<span class="ofph">${ph||'—'}</span>`);
  const H=[];
  H.push('<article class="ofpage">');
  // kop
  H.push('<header class="ofhead"><div class="ofco">');
  H.push(ed?ip('co.nm',o.co.nm,'text','Nama perusahaan'):`<div class="ofconm">${esc(o.co.nm)||'<span class="ofph">Nama perusahaan</span>'}</div>`);
  H.push(ed?ip('co.addr',o.co.addr,'text','Alamat'):`<div class="ofcosm">${esc(o.co.addr)}</div>`);
  H.push(ed?ip('co.tel',o.co.tel,'text','Telepon'):`<div class="ofcosm">${esc(o.co.tel)}</div>`);
  H.push(ed?ip('co.email',o.co.email,'text','Email'):`<div class="ofcosm">${esc(o.co.email)}</div>`);
  H.push('</div><div class="oflogo">');
  H.push(o.co.logo?`<img src="${o.co.logo}" alt="logo">`:'<span class="ofph">logo</span>');
  if(ed) H.push('<label class="oflogobtn">Unggah logo<input type="file" id="ofLogo" accept="image/*" hidden></label>');
  H.push('</div></header>');
  H.push('<h3 class="oftitle">Surat Penawaran Harga</h3>');
  // meta
  const rows=[['No. penawaran', ed?ip('cl.no',o.cl.no,'text',ofNo()):esc(ofNo())],
              ['Revisi', ed?ip('cl.rev',o.cl.rev):esc(o.cl.rev)],
              ['Kepada', ed?ip('cl.nm',o.cl.nm,'text','Nama klien'):(esc(o.cl.nm)||t('','Nama klien'))],
              ['Lokasi', ed?ip('cl.loc',o.cl.loc):esc(o.cl.loc)],
              ['Tanggal', ed?ip('dt.issue',o.dt.issue,'date'):dstr(o.dt.issue)],
              ['Berlaku', ed?(ip('dt.valid',o.dt.valid,'number')+' hari'):
                 (o.dt.valid?`${o.dt.valid} hari — s/d ${dstr(addDays(o.dt.issue,+o.dt.valid))}`:'—')],
              ['Rencana mulai', ed?ip('dt.start',o.dt.start,'date'):dstr(o.dt.start)],
              ['Rencana selesai', ed?ip('dt.end',o.dt.end,'date'):dstr(o.dt.end)],
              ['Durasi', `<span id="ofDur">—</span>`]];
  H.push('<div class="ofmeta">');
  rows.forEach(r=>H.push(`<div class="ofmr"><span>${r[0]}</span><span>${r[1]}</span></div>`));
  H.push('</div>');
  // rekap
  H.push('<h4 class="ofh4">A. Rekapitulasi biaya</h4>');
  H.push('<table class="oftab" id="ofRekap"><tbody></tbody></table>');
  // termin
  H.push('<h4 class="ofh4">B. Termin pembayaran'
    + (ed?' <button type="button" class="addrow" data-ofadd="terms">+ termin</button>':'')
    + '</h4>');
  H.push('<table class="oftab" id="ofTerm"><thead><tr><th style="width:34px">#</th><th>Tahap / syarat</th>'
    + '<th class="num" style="width:78px">%</th><th class="num" style="width:150px">Nominal</th>'
    + (ed?'<th style="width:36px"></th>':'') + '</tr></thead><tbody></tbody><tfoot></tfoot></table>');
  H.push('<p class="ofnote" id="ofTermNote"></p>');
  // jadwal
  H.push('<h4 class="ofh4">C. Jadwal pelaksanaan'
    + (ed?' <button type="button" class="addrow" data-ofadd="sched">+ tahap</button>':'')
    + '</h4>');
  H.push('<div class="ofgantt" id="ofGantt"></div>');
  // lingkup
  H.push('<div class="ofcols">');
  H.push('<div><h4 class="ofh4">D. Lingkup pekerjaan'
    + (ed?' <button type="button" class="addrow" data-ofadd="scope">+</button>':'') + '</h4>'
    + '<ul class="oflist" id="ofScope"></ul></div>');
  H.push('<div><h4 class="ofh4">E. Tidak termasuk'
    + (ed?' <button type="button" class="addrow" data-ofadd="excl">+</button>':'') + '</h4>'
    + '<ul class="oflist" id="ofExcl"></ul></div>');
  H.push('</div>');
  // syarat + ttd
  H.push('<h4 class="ofh4">F. Syarat &amp; ketentuan'
    + (ed?' <button type="button" class="addrow" data-ofadd="tnc">+</button>':'') + '</h4>'
    + '<ol class="oflist ofnum" id="ofTnc"></ol>');
  H.push('<div class="ofsign"><div class="ofsigbox">'
    + '<div class="ofsigd">Hormat kami,</div><div class="ofsigsp"></div>'
    + (ed?ip('sign.nm',o.sign.nm,'text','Nama penanda tangan'):`<div class="ofsignm">${esc(o.sign.nm)||'<span class="ofph">Nama</span>'}</div>`)
    + (ed?ip('sign.role',o.sign.role,'text','Jabatan'):`<div class="ofsigrl">${esc(o.sign.role)}</div>`)
    + '</div></div>');
  H.push('</article>');
  $('ofdoc').innerHTML=H.join('');
  ofCalc();
}

function ofCalc(){
  const o=OF(); if(!o.on) return;
  const d=$('ofDur'); if(d){ const n=workdays(o.dt.start,o.dt.end);
    d.textContent = n? (n+' hari kerja') : '—'; }
  // rekap
  const rk=$('ofRekap'); if(rk){
    const R=[['Profil hollow',TOT.costH],['Pelat baja',TOT.costP],['Material lain',TOT.costO]];
    let h='';
    R.forEach(r=>h+=`<tr><td>${r[0]}</td><td class="num">${rp(r[1])}</td></tr>`);
    h+=`<tr><td>Subtotal</td><td class="num">${rp(TOT.sub)}</td></tr>`;
    h+=`<tr><td>Overhead &amp; keuntungan ${S.ohp}%</td><td class="num">${rp(TOT.oh)}</td></tr>`;
    h+=`<tr><td>PPN ${S.ppn}%</td><td class="num">${rp(TOT.tax)}</td></tr>`;
    h+=`<tr class="ofsum"><td>NILAI PENAWARAN</td><td class="num">${odo('ofTot',rp(TOT.total))}</td></tr>`;
    rk.tBodies[0].innerHTML=h;
  }
  // termin
  const tt=$('ofTerm');
  if(tt){
    const ed=o.edit; let h='', sum=0;
    o.terms.forEach((r,i)=>{
      const pct=+r.pct||0; sum+=pct;
      h+=`<tr><td class="num">${i+1}</td>`
       + `<td>${ed?ip('terms.'+i+'.nm',r.nm,'text','mis. DP saat SPK'):esc(r.nm||'')}</td>`
       + `<td class="num">${ed?ip('terms.'+i+'.pct',r.pct,'number'):(pct+'%')}</td>`
       + `<td class="num">${rp(TOT.total*pct/100)}</td>`
       + (ed?`<td class="num"><button type="button" class="delrow" data-ofdel="terms" data-i="${i}">×</button></td>`:'')
       + '</tr>';
    });
    if(!o.terms.length) h='<tr><td colspan="'+(o.edit?5:4)+'" class="ofph">Belum ada termin — nyalakan <b>Edit isi</b> lalu tekan <b>+ termin</b>.</td></tr>';
    tt.tBodies[0].innerHTML=h;
    tt.tFoot.innerHTML = o.terms.length
      ? `<tr><td></td><td>Jumlah</td><td class="num">${f(sum,sum%1?1:0)}%</td>`
        + `<td class="num">${rp(TOT.total*sum/100)}</td>${o.edit?'<td></td>':''}</tr>` : '';
    const nt=$('ofTermNote');
    if(nt) nt.innerHTML = !o.terms.length ? ''
      : (Math.abs(sum-100)<0.01 ? '<span class="okmsg">Total termin 100% — sudah pas.</span>'
         : `<span class="warnmsg">Total termin ${f(sum,1)}% — kurang/lebih ${f(100-sum,1)}% dari nilai penawaran.</span>`);
  }
  // gantt
  const g=$('ofGantt');
  if(g){
    const W=ofWeeks(), ed=o.edit;
    let h='<div class="gwrap"><div class="grow ghead"><div class="gnm">Tahap</div><div class="gbars">';
    for(let w=1;w<=W;w++) h+=`<span class="gw">M${w}</span>`;
    h+='</div>'+(ed?'<div class="gact"></div>':'')+'</div>';
    o.sched.forEach((r,i)=>{
      const w0=Math.max(1,+r.w0||1), du=Math.max(1,+r.dur||1);
      h+='<div class="grow"><div class="gnm">'
       + (ed?ip('sched.'+i+'.nm',r.nm,'text','Nama tahap')
             +ip('sched.'+i+'.w0',w0,'number')+ip('sched.'+i+'.dur',du,'number')
           :esc(r.nm||''))
       + '</div><div class="gbars">';
      for(let w=1;w<=W;w++){
        const on = w>=w0 && w<w0+du;
        h+=`<span class="gc${on?' on':''}"></span>`;
      }
      h+='</div>'+(ed?`<div class="gact"><button type="button" class="delrow" data-ofdel="sched" data-i="${i}">×</button></div>`:'')+'</div>';
    });
    h+='</div>';
    if(o.dt.start) h+=`<p class="ofnote">Minggu 1 dihitung dari ${dstr(o.dt.start)}.</p>`;
    g.innerHTML=h;
  }
  // daftar teks
  const lst=(id,key)=>{ const el=$(id); if(!el) return;
    const ed=o.edit; let h='';
    (o[key]||[]).forEach((v,i)=>{
      h+='<li>'+(ed?ip(key+'.'+i,v,'text','…')
        +`<button type="button" class="delrow" data-ofdel="${key}" data-i="${i}">×</button>`:esc(v))+'</li>';
    });
    if(!h) h='<li class="ofph">—</li>';
    el.innerHTML=h; };
  lst('ofScope','scope'); lst('ofExcl','excl'); lst('ofTnc','tnc');
  paintOdo();
}
window.__ofCalc=ofCalc;

function ofSet(path,val){
  const o=OF(), parts=path.split('.');
  let t=o;
  for(let i=0;i<parts.length-1;i++){
    const k=parts[i]; t = Array.isArray(t)? t[+k] : t[k];
    if(!t) return;
  }
  const last=parts[parts.length-1];
  if(Array.isArray(t)) t[+last]=val; else t[last]=val;
  save();
}

document.addEventListener('input', e=>{
  const el=e.target;
  if(el.classList && el.classList.contains('ofin')){
    ofSet(el.dataset.of, el.type==='number' ? (+el.value||0) : el.value);
    ofCalc();
  }
});
document.addEventListener('change', e=>{
  const el=e.target;
  if(el.id==='tgOffer'){ OF().on=el.checked; save(); renderOffer(); return; }
  if(el.id==='tgOfEdit'){ OF().edit=el.checked; save(); renderOffer(); return; }
  if(el.id==='ofLogo' && el.files && el.files[0]){
    const fr=new FileReader();
    fr.onload=()=>{ if((fr.result||'').length>400000){ alert('Logo terlalu besar — pakai gambar di bawah 300 KB.'); return; }
      OF().co.logo=fr.result; save(); renderOffer(); };
    fr.readAsDataURL(el.files[0]);
  }
});
document.addEventListener('click', e=>{
  const b=e.target.closest('[data-ofadd],[data-ofdel],#ofReset,#ofPdf,#ofXls');
  if(!b) return;
  const o=OF();
  if(b.dataset.ofadd){
    const k=b.dataset.ofadd;
    if(k==='terms') o.terms.push({nm:'',pct:0});
    else if(k==='sched') o.sched.push({nm:'',w0:1,dur:1});
    else o[k].push('');
    save(); renderOffer(); return;
  }
  if(b.dataset.ofdel){ const k=b.dataset.ofdel; o[k].splice(+b.dataset.i,1); save(); renderOffer(); return; }
  if(b.id==='ofReset'){ const on=o.on, ed=o.edit; S.offer=OFFER0(); S.offer.on=on; S.offer.edit=ed;
    save(); renderOffer(); return; }
  if(b.id==='ofPdf'){ printOffer(b); return; }
  if(b.id==='ofXls'){ copyOfferTSV(b); return; }
});

function printOffer(btn){
  let st=document.getElementById('ofPageCSS');
  if(!st){ st=document.createElement('style'); st.id='ofPageCSS';
    st.textContent='@page{size:A4 portrait;margin:14mm}'; document.head.appendChild(st); }
  document.body.classList.add('printing','printing-of');
  const back=()=>{ document.body.classList.remove('printing','printing-of');
    const e=document.getElementById('ofPageCSS'); if(e) e.remove(); };
  addEventListener('afterprint', back, {once:true});
  setTimeout(()=>{ try{ window.print(); }catch(e){ back(); }
    setTimeout(back,1500); }, 60);
}

function copyOfferTSV(btn){
  const o=OF(), out=[];
  out.push('SURAT PENAWARAN HARGA');
  out.push(['Perusahaan',o.co.nm].join('\t'));
  out.push(['Alamat',o.co.addr].join('\t'));
  out.push(['Kontak',[o.co.tel,o.co.email].filter(Boolean).join(' / ')].join('\t'));
  out.push(['No. penawaran',ofNo()].join('\t'));
  out.push(['Revisi',o.cl.rev].join('\t'));
  out.push(['Kepada',o.cl.nm].join('\t'));
  out.push(['Lokasi',o.cl.loc].join('\t'));
  out.push(['Tanggal',dstr(o.dt.issue)].join('\t'));
  out.push(['Berlaku',o.dt.valid+' hari'].join('\t'));
  out.push(['Mulai',dstr(o.dt.start)].join('\t'));
  out.push(['Selesai',dstr(o.dt.end)].join('\t'));
  out.push(['Durasi',workdays(o.dt.start,o.dt.end)+' hari kerja'].join('\t'));
  out.push('');
  out.push('REKAPITULASI BIAYA');
  [['Profil hollow',TOT.costH],['Pelat baja',TOT.costP],['Material lain',TOT.costO],
   ['Subtotal',TOT.sub],['Overhead & keuntungan',TOT.oh],['PPN',TOT.tax],['NILAI PENAWARAN',TOT.total]]
   .forEach(r=>out.push([r[0],Math.round(r[1])].join('\t')));
  out.push('');
  out.push('TERMIN PEMBAYARAN'); out.push(['No','Tahap','%','Nominal'].join('\t'));
  o.terms.forEach((r,i)=>out.push([i+1,r.nm,(+r.pct||0),Math.round(TOT.total*(+r.pct||0)/100)].join('\t')));
  out.push('');
  out.push('JADWAL PELAKSANAAN'); out.push(['Tahap','Mulai minggu','Durasi (minggu)'].join('\t'));
  o.sched.forEach(r=>out.push([r.nm,r.w0,r.dur].join('\t')));
  out.push('');
  out.push('LINGKUP PEKERJAAN'); o.scope.forEach(v=>out.push(v));
  out.push(''); out.push('TIDAK TERMASUK'); o.excl.forEach(v=>out.push(v));
  out.push(''); out.push('SYARAT & KETENTUAN'); o.tnc.forEach(v=>out.push(v));
  out.push(''); out.push(['Hormat kami',o.sign.nm,o.sign.role].join('\t'));
  const txt=out.join('\n'), lab=btn.querySelector('b')||btn;
  const done=()=>{ const x=lab.textContent; lab.textContent='Tersalin — tempel di Excel';
    setTimeout(()=>lab.textContent=x,2200); };
  if(navigator.clipboard && navigator.clipboard.writeText)
    navigator.clipboard.writeText(txt).then(done,()=>fallback(txt,done));
  else fallback(txt,done);
}

if(!S.offer) S.offer=OFFER0();
renderOffer();

$('tgPrice').checked=S.price; $('tgEdit').checked=S.edit;
$('tgExport').checked=!!S.exp; $('exportbox').hidden=!S.exp;
exportUI();
$('wH').value=S.wH; $('wP').value=S.wP; $('bar').value=S.bar;
$('ohp').value=S.ohp; $('ppn').value=S.ppn;
render();
}


// pratinjau indeks mengikuti kursor — kloning SVG lembar aslinya, nol byte tambahan
(function(){
  const prev=document.getElementById('ixprev');
  if(!prev||!matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  const cache={}; let raf=0, tx=0, ty=0;
  const move=e=>{tx=e.clientX; ty=e.clientY;
    if(!raf) raf=requestAnimationFrame(()=>{raf=0;
      prev.style.top=ty+'px'; prev.style.left=Math.min(tx+230,innerWidth-24)+'px';});};
  document.querySelectorAll('.ix').forEach(a=>{
    a.addEventListener('pointerenter',()=>{
      const id=a.dataset.prev;
      if(!cache[id]){
        const src=document.querySelector('#'+id+' .pan svg');
        if(!src) return;
        const c=src.cloneNode(true); c.removeAttribute('style'); cache[id]=c;
      }
      if(prev.firstChild!==cache[id]){prev.textContent=''; prev.appendChild(cache[id]);}
      prev.classList.add('on');
    });
    a.addEventListener('pointerleave',()=>prev.classList.remove('on'));
    a.addEventListener('pointermove',move);
  });
})();

// ---------- mode layar penuh ----------
const SHEETIDS=[...document.querySelectorAll('.sheet')].map(s=>s.id);
function setFull(id,on){
  const sec=document.getElementById(id);
  sec.classList.toggle('full',on);
  document.body.classList.toggle('locked',on);
  const btn=sec.querySelector('.expand');
  btn.textContent=on?'Keluar':'Layar penuh';
  btn.setAttribute('aria-pressed',on?'true':'false');
  sec.querySelectorAll('[data-nav]').forEach(n=>{
    const i=SHEETIDS.indexOf(id);
    n.disabled = n.dataset.nav==='prev' ? i===0 : i===SHEETIDS.length-1;
  });
  if(!on) sec.scrollIntoView({block:'start'});
  window.dispatchEvent(new Event('resize'));
  const fit=window.__fit&&window.__fit[id];
  if(fit) requestAnimationFrame(()=>fit(on&&innerWidth<=860?'fill':'reset'));
}
document.querySelectorAll('[data-full]').forEach(b=>b.addEventListener('click',()=>{
  const id=b.dataset.full;
  setFull(id, !document.getElementById(id).classList.contains('full'));
}));
document.querySelectorAll('[data-nav]').forEach(b=>b.addEventListener('click',()=>{
  const i=SHEETIDS.indexOf(b.dataset.s);
  const j=b.dataset.nav==='prev'?i-1:i+1;
  if(j<0||j>=SHEETIDS.length) return;
  setFull(b.dataset.s,false); setFull(SHEETIDS[j],true);
}));
addEventListener('keydown',e=>{
  const cur=document.querySelector('.sheet.full'); if(!cur) return;
  if(e.key==='Escape') setFull(cur.id,false);
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
    const i=SHEETIDS.indexOf(cur.id), j=e.key==='ArrowLeft'?i-1:i+1;
    if(j>=0&&j<SHEETIDS.length){setFull(cur.id,false); setFull(SHEETIDS[j],true);}
  }
});

// ---------- alat ukur: klik dua titik, jarak dalam mm sebenarnya ----------
const NS='http://www.w3.org/2000/svg';
document.querySelectorAll('[data-meas]').forEach(btn=>{
  const id=btn.dataset.meas;
  const sec=document.getElementById(id);
  const fr=sec.querySelector('.frame'), svg=sec.querySelector('.pan svg');
  let on=false, a=null, g=null;
  const clear=()=>{ if(g) g.remove(); g=null; a=null; };
  const toModel=e=>{
    const p=svg.createSVGPoint(); p.x=e.clientX; p.y=e.clientY;
    return p.matrixTransform(svg.getScreenCTM().inverse());
  };
  const mk=(t,at)=>{const el=document.createElementNS(NS,t);
    for(const k in at) el.setAttribute(k,at[k]); return el;};
  btn.addEventListener('click',()=>{
    on=!on; btn.setAttribute('aria-pressed',on?'true':'false');
    fr.classList.toggle('measuring',on); btn.textContent=on?'Selesai':'Ukur';
    if(!on) clear();
  });
  fr.addEventListener('pointerup',e=>{
    if(!on||e.pointerType==='mouse'&&e.button!==0) return;
    if(fr.dataset.moved==='1') return;
    const q=toModel(e);
    if(!a){ clear(); a=q;
      g=mk('g',{class:'measg'}); svg.appendChild(g);
      g.appendChild(mk('circle',{cx:a.x,cy:a.y,r:22,fill:'var(--accent)'}));
      return;
    }
    const d=Math.hypot(q.x-a.x,q.y-a.y);
    g.appendChild(mk('line',{x1:a.x,y1:a.y,x2:q.x,y2:q.y,
      stroke:'var(--accent)','stroke-width':8}));
    g.appendChild(mk('circle',{cx:q.x,cy:q.y,r:22,fill:'var(--accent)'}));
    const t=mk('text',{x:(a.x+q.x)/2,y:(a.y+q.y)/2-40,fill:'var(--accent)',
      'text-anchor':'middle','font-family':'"JetBrains Mono",monospace','font-size':150});
    t.textContent=Math.round(d).toLocaleString('id-ID')+' mm';
    g.appendChild(t); a=null;
  });
});

// ---------- angka BOQ berhitung naik sekali saat blok masuk layar ----------
(function(){
  const boq=document.getElementById('boq'); if(!boq) return;
  const ids=['sumH','sumBar','sumP','sumSheet','grand'];
  const run=()=>{
    if(matchMedia('(prefers-reduced-motion:reduce)').matches) return;
    ids.forEach(id=>{
      const el=document.getElementById(id); if(!el) return;
      const txt=el.textContent, m=txt.match(/[\d.,]+/); if(!m) return;
      const target=parseFloat(m[0].replace(/\./g,'').replace(',','.'));
      if(!isFinite(target)) return;
      const dec=(m[0].split(',')[1]||'').length;
      const t0=performance.now(), D=900;
      const step=now=>{
        const k=Math.min(1,(now-t0)/D), e=1-Math.pow(1-k,3);
        el.textContent=txt.replace(m[0],(target*e).toLocaleString('id-ID',
          {minimumFractionDigits:dec,maximumFractionDigits:dec}));
        if(k<1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  };
  if(!('IntersectionObserver' in window)) return;
  const io=new IntersectionObserver((e,o)=>{if(e[0].isIntersecting){run();o.disconnect();}},
    {threshold:0.15});
  io.observe(boq);
})();

// petunjuk menyesuaikan perangkat
if(matchMedia('(pointer:coarse)').matches)
  document.querySelectorAll('[data-h]').forEach(h=>h.textContent='cubit untuk zoom · ketuk 2\u00d7 reset');

// reveal saat masuk layar — transform + opacity saja, stagger 60 ms
(function(){
  const els=[...document.querySelectorAll('.rv')];
  if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion:reduce)').matches){
    els.forEach(e=>e.classList.add('in')); return;
  }
  const io=new IntersectionObserver((ents,o)=>{
    ents.filter(e=>e.isIntersecting).forEach((e,i)=>{
      setTimeout(()=>e.target.classList.add('in'), i*60);
      o.unobserve(e.target);
    });
  },{rootMargin:'0px 0px -8% 0px',threshold:0.04});
  els.forEach(e=>io.observe(e));
})();
"""

if __name__ == "__main__":
    html = build()
    with open("/tmp/tribun/tribun.html", "w", encoding="utf-8") as fh:
        fh.write(html)
    print("bytes:", len(html))
