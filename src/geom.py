# -*- coding: utf-8 -*-
"""Geometri terkunci Tribun METTA LT 4 (satuan mm, koordinat lokal tribun)."""

SPAN   = 17700          # X 0..17700
DEPTH  = 5000           # Y 0..5000 (0 = sisi lapangan, 5000 = sisi dinding)
TIERS  = 5
TIER_D = 1000           # kedalaman tiap tier
RISER  = 500            # beda tinggi tiap tier

# garis portal yang MASIH ada (x, mm)  -- 5310 & 12390 dihapus krn masuk jalur tangga
PORTAL_ALL = [n * 1770 for n in range(11)]
PORTAL_DEL = [5310, 12390]
PORTAL = [x for x in PORTAL_ALL if x not in PORTAL_DEL]

# baris kolom pada arah Y
ROWS = [0, 1000, 2000, 3000, 4000, 5000]

# jalur tangga
STAIR_AB = (4850, 6850)     # gabungan A+B, lebar 2000
STAIR_C  = (12250, 12850)   # lebar 600
AISLES   = [STAIR_AB, STAIR_C]

# segmen dek per tier
SEGMENTS = [(0, 4850), (6850, 12250), (12850, 17700)]

# kolom beton eksisting 600(X) x 500(Y), pusat y = 2938
CONC = [(-150, 2938), (5850, 2938), (11850, 2938), (17850, 2938)]
CONC_B, CONC_H = 600, 500

# tangga: 3 optrede 167 + 3 antrede 267 per tier  (Blondel 2R+T = 601)
ST_R, ST_T, ST_N = 167, 267, 3

# tinggi puncak kolom pada tiap baris Y
def col_top(y):
    if y >= 5000:
        return 2500
    return int(y / TIER_D) * RISER + RISER

def tier_front(t):   # t = 1..5
    return (t - 1) * TIER_D

def deck_z(t):
    return t * RISER

# ---------- berat profil (kg/m) ----------
HOLLOW = {
    "80x40x3.2": 5.71,
    "100x50x2.3": 5.25,
    "40x40x2":   2.39,
    "40x40x2.8": 3.27,
}
RHO_PLATE = 7.85   # kg/m2 per mm tebal
