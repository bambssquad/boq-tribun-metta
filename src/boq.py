# -*- coding: utf-8 -*-
import math
from geom import *

def _diag(a, b):
    return math.sqrt(a*a + b*b) / 1000.0

# ---------- profil hollow: (nama, jumlah, panjang total m, kg/m, catatan) ----------
KOL_LEN = (len(PORTAL) * sum(col_top(y) for y in ROWS) + 4 * sum(col_top(y) for y in ROWS[:-1])) / 1000.0 - 4.5
SEG_LEN = sum(b - a for a, b in SEGMENTS) / 1000.0            # 15.1 m per tier
BRACE_LEN = 8 * _diag(1770, 2500)   # hanya bidang belakang; sisi ujung diikat ke kolom beton

HOLLOW_ITEMS = [
    ("Kolom tribun",      "HOLLOW 50x100x2,3", 71, KOL_LEN,        "100x50x2.3", "tinggi 500–2500 mm mengikuti tier"),
    ("Balok tepi tier",   "HOLLOW 50x100x2,3", 15, SEG_LEN * 5,    "100x50x2.3", "3 segmen x 5 tier"),
    ("Stiffener dek",     "HOLLOW 50x100x2,3", 15, SEG_LEN * 5,    "100x50x2.3", "tengah bentang tiap tier, sedalam balok"),
    ("Rangka sandaran belakang","HOLLOW 50x100x2,3", 1, 17.7,      "100x50x2.3", "rail atas & bawah + tiang, mengikuti busur dinding"),
    ("Strut anchor",      "HOLLOW 50x100x2,3", 16, 12 * 0.7 + 4 * 0.312, "100x50x2.3", "12 ke kolom beton dalam + 4 ikatan rangka ujung"),
    ("Bracing X",         "HOLLOW 40x40x2",    8, BRACE_LEN,       "40x40x2",   "4 bay bidang belakang"),
    ("Rail atas & tengah","HOLLOW 40x40x2",   10, 10 * 1.0,        "40x40x2",   "balustrade dua sisi ujung"),
    ("Baluster + pegangan","HOLLOW 40x40x2,8", 83, 83 * 1.1,       "40x40x2.8", "80 baluster @100 + 3 tiang pegangan"),
]

# ---------- pelat: (nama, tebal mm, luas m2, tambahan kg/m2 motif, catatan) ----------
# Pelat bordes lebih berat dari pelat polos karena motif kembangnya: lembar 8 mm
# 4ft x 8ft ditimbang 192 kg = 64,6 kg/m2, sedangkan polos 62,8 kg/m2 -> +1,8 kg/m2.
PLATE_ITEMS = [
    ("Plat dek bordes 8 mm",        8,  SEG_LEN * TIERS * 1.0, 1.8, "permukaan injak 5 tier, motif kembang anti-slip"),
    ("Plat riser muka tier",        2,  SEG_LEN * TIERS * 0.5, 0.0, "penutup muka tier, tinggi 500 mm — non-struktural"),
    ("Plat tekuk tangga + stringer",4,  26.9,                  1.8, "anak tangga 2 jalur + 4 stringer, bordes anti-slip"),
    ("Skirt kolong + toe-board",    2,  6.0,                   0.0, "10 skirt + 10 toe-board"),
    ("Base plate",                  8,  71 * 0.15 * 0.15,      0.0, "150x150, 71 titik — plat polos 8 mm"),
]

SAND_AREA   = 7.29          # panel kayu sandaran, menerus A-C
SAND_VOL    = SAND_AREA * 0.040
RUBBER_AREA = 71 * 0.15 * 0.15
PINUS_VOL   = SEG_LEN * TIERS * 0.4 * 0.04

FASTENERS = [
    ("Baut M12 gr.4.6 + mur + ring", 168, "bh", "2 per sambungan balok–kolom (84 titik)"),
    ("Dynabolt M10 L=80",            32,  "bh", "2 per titik anchor (16 titik) — hanya ke kolom beton"),
    ("Pelat buhul 6 mm 200x200",     16,  "bh", "titik buhul bracing belakang"),
    ("Pelat siku 6 mm 90x120",       84,  "bh", "dudukan balok tepi"),
    ("Karet dudukan 10 mm 150x150",  71,  "bh", f"total {RUBBER_AREA:.2f} m2"),
    ("Sekrup kayu 5x40 + ring",      420, "bh", "pemasangan panel kayu sandaran 40 mm ke rangka"),
]

CONSUMABLES = [
    ("Kawat las E6013 3,2 mm", "±38 kg", "las sudut a=4 mm, total ±950 m alur"),
    ("Cat dasar zinc chromate", "±34 L", "1 lapis, daya sebar 10 m2/L"),
    ("Cat finish hitam doff",   "±52 L", "2 lapis, luas permukaan baja ±340 m2"),
    ("Cat epoxy kuning kontras","±6 L",  "nosing anak tangga — dicat, bukan strip menonjol"),
    ("Finish clear kayu",       "±9 L",  "papan pinus + panel sandaran, 2 lapis"),
]

BAR_LEN   = 6.0        # lonjor hollow standar (m)
SHEET_W, SHEET_H = 1.22, 2.44
SHEET_A   = SHEET_W * SHEET_H
