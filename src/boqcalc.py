# -*- coding: utf-8 -*-
"""Hitungan BOQ di Python — rumus persis sama dengan yang dipakai halaman web."""
import math
from boq import *

WH, WP, BAR = 0.05, 0.10, 6.0     # waste hollow, waste pelat, panjang lonjor (m)


def hollow_rows(wh=WH, bar=BAR):
    rows, sum_kg, sum_bar = [], 0.0, 0
    for nm, pr, n, L, prof, note in HOLLOW_ITEMS:
        Lw = L * (1 + wh)
        kg_m = HOLLOW[prof]
        kg = Lw * kg_m
        bars = math.ceil(Lw / bar)
        rows.append(dict(nm=nm, pr=pr, n=n, L=L, kgm=kg_m, Lw=Lw, kg=kg, bars=bars, note=note))
        sum_kg += kg
        sum_bar += bars
    return rows, sum_kg, sum_bar


def plate_rows(wp=WP):
    rows, sum_kg, sum_sheet = [], 0.0, 0
    for nm, t, A, sur, note in PLATE_ITEMS:
        Aw = A * (1 + wp)
        kg = Aw * (t * 7.85 + sur)  # 7,85 kg/m2 per mm + tambahan motif bordes
        sh = math.ceil(Aw / SHEET_A)
        rows.append(dict(nm=nm, t=t, A=A, sur=sur, Aw=Aw, kg=kg, sh=sh, note=note))
        sum_kg += kg
        sum_sheet += sh
    return rows, sum_kg, sum_sheet


def totals():
    _, hk, hb = hollow_rows()
    _, pk, ps = plate_rows()
    return dict(hollow_kg=hk, hollow_bar=hb, plate_kg=pk, plate_sheet=ps, steel_kg=hk + pk)
