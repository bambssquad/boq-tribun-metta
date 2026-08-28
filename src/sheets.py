# -*- coding: utf-8 -*-
from geom import *
from draw import *
import draw

PAD = 1400  # margin gambar (mm)

# ============ S-01 DENAH TRIBUN ============
def s01():
    s = SVG(0, 0, (-PAD, -PAD*1.1, SPAN + 3.6*PAD, DEPTH + 2.4*PAD))
    o = []
    # dek per tier per segmen
    for t in range(1, TIERS+1):
        yf = tier_front(t)
        for (a, b) in SEGMENTS:
            o.append(rect(a, yf, b-a, TIER_D, "deck"))
            # papan pinus 400 di depan tiap tier
            o.append(rect(a, yf, b-a, 400, "pinus"))
    s.g("lay-dek", "".join(o)); o = []
    # jalur tangga (anak tangga)
    for (a, b) in AISLES:
        for t in range(1, TIERS+1):
            yf = tier_front(t)
            for k in range(ST_N):
                y0 = yf + k*ST_T
                h = ST_T if k < ST_N-1 else TIER_D - 2*ST_T
                o.append(rect(a, y0, b-a, h, "tread"))
            o.append(line(a, yf, a, yf+TIER_D, "stringer"))
            o.append(line(b, yf, b, yf+TIER_D, "stringer"))
    s.g("lay-tangga", "".join(o)); o = []
    # kolom hollow
    for x in PORTAL:
        for y in ROWS:
            o.append(rect(x-25, y-50, 50, 100, "col"))
    for x in (STAIR_AB[0], STAIR_AB[1], STAIR_C[0], STAIR_C[1]):
        for y in ROWS[:-1]:
            o.append(rect(x-25, y-50, 50, 100, "col"))
    s.g("lay-kolom", "".join(o)); o = []
    # kolom beton + void 50 mm
    for (cx, cy) in CONC:
        o.append(rect(cx-CONC_B/2-50, cy-CONC_H/2-50, CONC_B+100, CONC_H+100, "void"))
        o.append(rect(cx-CONC_B/2, cy-CONC_H/2, CONC_B, CONC_H, "conc"))
    s.g("lay-beton", "".join(o)); o = []
    # railing sisi
    for x in (0, SPAN):
        o.append(line(x, 0, x, DEPTH, "rail"))
    s.g("lay-railing", "".join(o)); o = []
    # dimensi
    yd = DEPTH + 520
    o.append(dim_h(0, SEGMENTS[0][1], yd, "4850"))
    o.append(dim_h(STAIR_AB[0], STAIR_AB[1], yd, "2000"))
    o.append(dim_h(STAIR_AB[1], STAIR_C[0], yd, "5400"))
    o.append(dim_h(STAIR_C[0], STAIR_C[1], yd, "600"))
    o.append(dim_h(STAIR_C[1], SPAN, yd, "4850"))
    o.append(dim_h(0, SPAN, yd + 620, "17700  (bentang total tribun)"))
    xd = -560
    for t in range(1, TIERS+1):
        o.append(dim_v(tier_front(t), tier_front(t)+TIER_D, xd, "1000"))
    o.append(dim_v(0, DEPTH, xd - 620, "5000"))
    # grid portal
    for i, x in enumerate(PORTAL_ALL):
        cls = "gridline" if x not in PORTAL_DEL else "gridline off"
        o.append(f'<line x1="{x}" y1="-340" x2="{x}" y2="{DEPTH+200}" class="{cls}"/>')
        o.append(grid_bubble(x, -620, f"P{i+1}"))
    o.append(dim_h(0, 1770, -1000, "1770 tipikal"))
    # ukuran elemen (tipikal)
    o.append(dim_v(tier_front(1), tier_front(1)+400, 3400, "400"))
    o.append(dim_h(CONC[1][0]-CONC_B/2, CONC[1][0]+CONC_B/2, CONC[1][1]-CONC_H/2-360, "600"))
    o.append(dim_v(CONC[1][1]-CONC_H/2, CONC[1][1]+CONC_H/2, CONC[1][0]+CONC_B/2+420, "500"))
    o.append(dim_h(CONC[1][0]+CONC_B/2, CONC[1][0]+CONC_B/2+50, CONC[1][1]+CONC_H/2+360, "50 void"))
    o.append(dim_h(PORTAL[6]-25, PORTAL[6]+25, tier_front(2)+560, "50"))
    o.append(dim_v(ROWS[2]-50, ROWS[2]+50, PORTAL[6]+420, "100"))
    o.append(dim_v(tier_front(2), tier_front(2)+ST_T, STAIR_AB[0]-300, "267"))
    o.append(dim_h(STAIR_AB[0], 5550, DEPTH+170, "700"))
    o.append(dim_h(6150, STAIR_AB[1], DEPTH+170, "700"))
    s.g("lay-dim", "".join(o)); o = []
    # notasi
    o.append(mtag(2600, tier_front(3)+700, 1500, tier_front(3)+1180, "P8", None, "end"))
    o.append(mtag(8200, tier_front(2)+200, 7400, tier_front(2)-320, "W1", None, "end"))
    o.append(mtag(PORTAL[6], ROWS[3], PORTAL[6]+600, ROWS[3]-380, "H1"))
    o.append(mtag(CONC[2][0]-CONC_B/2, CONC[2][1], CONC[2][0]-1100, CONC[2][1]-420, "C1", None, "end"))
    o.append(mtag(STAIR_C[0]+300, tier_front(2)+400, STAIR_C[1]+700, tier_front(2)+120, "P4"))
    o.append(mtag(SPAN, DEPTH-700, SPAN+560, DEPTH-1000, "H3"))
    o.append(txt(SEGMENTS[1][0] + 2700, 300, "PAPAN PINUS 400x40 (tiap tier)", "note"))
    o.append(txt((STAIR_AB[0]+STAIR_AB[1])/2, DEPTH-300, "TANGGA A+B  2000", "note"))
    o.append(txt((STAIR_C[0]+STAIR_C[1])/2, DEPTH-300, "TANGGA C 600", "note"))
    s.g("lay-notasi", "".join(o))
    return s.render()

# ============ S-02 RENCANA TUMPUAN & BASE PLATE ============
def s02():
    s = SVG(0, 0, (-PAD, -PAD, SPAN + 3.6*PAD, DEPTH + 2.6*PAD))
    o = []
    o.append(rect(0, 0, SPAN, DEPTH, "outline"))
    s.g("lay-outline", "".join(o)); o = []
    pts = [(x, y) for x in PORTAL for y in ROWS]
    pts += [(x, y) for x in (STAIR_AB[0], STAIR_AB[1], STAIR_C[0], STAIR_C[1]) for y in ROWS[:-1]]
    for (x, y) in pts:
        o.append(rect(x-75, y-75, 150, 150, "bp"))
        o.append(rect(x-25, y-50, 50, 100, "col"))
    s.g("lay-bp", "".join(o)); o = []
    for (cx, cy) in CONC:
        o.append(rect(cx-CONC_B/2, cy-CONC_H/2, CONC_B, CONC_H, "conc"))
    s.g("lay-beton", "".join(o)); o = []
    for i, x in enumerate(PORTAL_ALL):
        cls = "gridline" if x not in PORTAL_DEL else "gridline off"
        o.append(f'<line x1="{x}" y1="-340" x2="{x}" y2="{DEPTH+240}" class="{cls}"/>')
        o.append(grid_bubble(x, -620, f"P{i+1}"))
    for y in ROWS:
        o.append(f'<line x1="-340" y1="{y}" x2="{SPAN+240}" y2="{y}" class="gridline"/>')
        o.append(grid_bubble(-620, y, f"A{ROWS.index(y)+1}"))
    o.append(dim_h(0, 1770, -1010, "1770 tipikal"))
    o.append(dim_h(0, SPAN, DEPTH + 620, "17700"))
    for i in range(len(ROWS)-1):
        o.append(dim_v(ROWS[i], ROWS[i+1], -1010, "1000"))
    o.append(dim_v(0, DEPTH, -1290, "5000"))
    o.append(dim_h(PORTAL[2]-75, PORTAL[2]+75, ROWS[1]-300, "150"))
    o.append(dim_v(ROWS[1]-75, ROWS[1]+75, PORTAL[2]+420, "150"))
    o.append(dim_h(PORTAL[4]-25, PORTAL[4]+25, ROWS[4]+420, "50"))
    o.append(dim_v(ROWS[4]-50, ROWS[4]+50, PORTAL[4]+480, "100"))
    s.g("lay-dim", "".join(o)); o = []
    o.append(mtag(PORTAL[7]+75, ROWS[1]-75, PORTAL[7]+560, ROWS[1]-420, "B8"))
    o.append(mtag(PORTAL[7]+75, ROWS[2]+75, PORTAL[7]+560, ROWS[2]+520, "K1"))
    o.append(mtag(PORTAL[5], ROWS[3], PORTAL[5]+560, ROWS[3]-380, "H1"))
    o.append(mtag(CONC[1][0]-CONC_B/2, CONC[1][1], CONC[1][0]-1100, CONC[1][1]-420, "C1", None, "end"))
    o.append(txt(SPAN/2, DEPTH + 900,
        "BASE PLATE 150x150x8 + KARET 10 mm — DUDUK LEPAS, TANPA ANGKUR KE PELAT LANTAI", "note"))
    o.append(txt(SPAN/2, DEPTH + 1180,
        "LAS SUDUT a=4 mm KELILING PROFIL KOLOM", "note"))
    s.g("lay-notasi", "".join(o))
    return s.render()

# ============ S-03 RENCANA RANGKA ============
def s03():
    s = SVG(0, 0, (-PAD, -PAD, SPAN + 3.6*PAD, DEPTH + 2.6*PAD))
    o = []
    for t in range(1, TIERS+1):
        yf = tier_front(t)
        for (a, b) in SEGMENTS:
            o.append(line(a, yf, b, yf, "beam"))
            o.append(line(a, yf+TIER_D/2, b, yf+TIER_D/2, "stiff"))
    o.append(line(SEGMENTS[0][0], DEPTH, SEGMENTS[-1][1], DEPTH, "beam"))
    s.g("lay-balok", "".join(o)); o = []
    # bracing belakang (4 bay ber-X)
    for (a, b) in [(0,1770), (3540,5310), (8850,10620), (15930,17700)]:
        o.append(line(a, DEPTH, b, DEPTH-160, "brace"))
        o.append(line(b, DEPTH, a, DEPTH-160, "brace"))
    # ikatan rangka ujung ke kolom beton ujung (pengganti bracing sisi)
    for x in (0, SPAN):
        o.append(line(x, 2938, x, 2626, "anchor"))
    s.g("lay-brace", "".join(o)); o = []
    for (cx, cy) in CONC:
        for dz in (-1, 1):
            o.append(line(cx + dz*(CONC_B/2), cy, cx + dz*(CONC_B/2+700), cy, "anchor"))
        o.append(rect(cx-CONC_B/2, cy-CONC_H/2, CONC_B, CONC_H, "conc"))
    s.g("lay-anchor", "".join(o)); o = []
    for x in PORTAL:
        for y in ROWS:
            o.append(rect(x-25, y-50, 50, 100, "col"))
    for x in (STAIR_AB[0], STAIR_AB[1], STAIR_C[0], STAIR_C[1]):
        for y in ROWS[:-1]:
            o.append(rect(x-25, y-50, 50, 100, "col"))
    s.g("lay-kolom", "".join(o)); o = []
    o.append(dim_h(0, 1770, -700, "1770 tipikal"))
    o.append(dim_h(0, SPAN, DEPTH + 620, "17700"))
    o.append(dim_v(tier_front(3), tier_front(3)+TIER_D/2, 9600, "500"))
    o.append(dim_v(tier_front(3)+TIER_D/2, tier_front(3)+TIER_D, 9600, "500"))
    o.append(dim_v(0, DEPTH, -1290, "5000"))
    o.append(dim_h(CONC[2][0]+CONC_B/2, CONC[2][0]+CONC_B/2+700, CONC[2][1]+420, "700"))
    o.append(dim_h(3540, 5310, DEPTH + 300, "1770 bay bracing"))
    for i, x in enumerate(PORTAL_ALL):
        cls = "gridline" if x not in PORTAL_DEL else "gridline off"
        o.append(f'<line x1="{x}" y1="-340" x2="{x}" y2="{DEPTH+240}" class="{cls}"/>')
        o.append(grid_bubble(x, -620, f"P{i+1}"))
    s.g("lay-dim", "".join(o)); o = []
    o.append(mtag(9000, tier_front(3), 9700, tier_front(3)-360, "H1"))
    o.append(mtag(9800, tier_front(4)+TIER_D/2, 10600, tier_front(4)+TIER_D/2-220, "H1"))
    o.append(mtag(4400, DEPTH-80, 3600, DEPTH-460, "H2", None, "end"))
    o.append(mtag(CONC[2][0]+CONC_B/2+400, CONC[2][1], CONC[2][0]+1400, CONC[2][1]-420, "H1"))
    o.append(txt(SPAN/2, DEPTH+900, "BALOK TEPI & STIFFENER HOLLOW 50x100x2,3 — SATU PROFIL UNTUK SELURUH RANGKA", "note"))
    o.append(txt(SPAN/2, DEPTH+1180, "BRACING X HOLLOW 40x40x2 — 4 BAY BIDANG BELAKANG  •  RANGKA UJUNG DIIKAT LANGSUNG KE KOLOM BETON", "note"))
    s.g("lay-notasi", "".join(o))
    return s.render()

# ============ S-04 TAMPAK DEPAN ============
def s04():
    """Tampak depan dari sisi lapangan: muka tier bertingkat, kolom tersembunyi,
    bukaan tangga, balustrade ujung, sandaran belakang, dan rantai dimensi."""
    H = 4400
    s = SVG(0, 0, (-PAD*2.4, -H - PAD*0.6, SPAN + 4.0*PAD, H + 2.1*PAD))
    o = []

    # ---- muka tier: 5 pita riser, dipotong di bukaan tangga ----
    for t in range(1, TIERS+1):
        z0, z1 = (t-1)*RISER, t*RISER
        for (a, b) in SEGMENTS:
            o.append(rect(a, -z1, b-a, RISER, "skirt" if t == 1 else "deck"))
            o.append(rect(a, -z1-40, b-a, 40, "pinus"))       # tepi papan pinus
    o.append(line(0, 0, SPAN, 0, "slab"))
    s.g("lay-muka", "".join(o)); o = []

    # ---- kolom: tersembunyi di balik muka (garis putus), penuh di bukaan ----
    for x in PORTAL:
        inside = any(a < x < b for (a, b) in AISLES)
        if inside:
            o.append(rect(x-50, -col_top(0), 100, col_top(0), "colE"))
        else:
            o.append(line(x, 0, x, -col_top(DEPTH), "ghost"))
    s.g("lay-kolom", "".join(o)); o = []

    # ---- bukaan tangga: anak tangga terlihat menerus 0 -> +2500 ----
    for (a, b) in AISLES:
        o.append(rect(a, -2500, b-a, 2500, "aisleE"))
        for k in range(1, TIERS*ST_N + 1):
            zk = k * ST_R
            if zk > 2500:
                break
            o.append(line(a, -zk, b, -zk, "edge"))
        o.append(txt((a+b)/2, 300, f"TANGGA {b-a:.0f}", "lbl"))
    s.g("lay-tangga", "".join(o)); o = []

    # ---- balustrade ujung: satu tiang terlihat per tier di kedua ujung ----
    for x in (0, SPAN):
        for t in range(1, TIERS+1):
            z = t*RISER
            o.append(line(x, -z, x, -z-1100, "rail"))
            o.append(line(x-110, -z-1100, x+110, -z-1100, "rail"))
            o.append(line(x-110, -z-550, x+110, -z-550, "rail"))
    s.g("lay-railing", "".join(o)); o = []

    # ---- sandaran belakang terlihat di atas tier 5 ----
    o.append(rect(0, -3600, SPAN, 1000, "sandE"))
    o.append(line(0, -3600, SPAN, -3600, "edge"))
    o.append(line(0, -2600, SPAN, -2600, "edge"))
    s.g("lay-sandaran", "".join(o)); o = []

    # ---- dimensi ----
    chain = [(0, 4850), (4850, 6850), (6850, 12250), (12250, 12850), (12850, SPAN)]
    for (a, b) in chain:
        o.append(dim_h(a, b, 620, f"{b-a:.0f}"))
    o.append(dim_h(0, SPAN, 1180, "17700 (bentang total)"))
    o.append(dim_h(0, 1770, -3980, "1770 tipikal"))
    for t in range(1, TIERS+1):
        o.append(dim_v(-(t-1)*RISER, -t*RISER, -560, "500"))
    o.append(dim_v(0, -2500, -1560, "2500"))
    o.append(dim_v(-2500, -3600, -1560, "1100"))
    o.append(dim_v(-2600, -3600, -2160, "1000"))
    o.append(dim_v(0, -3600, -2760, "3600"))
    s.g("lay-dim", "".join(o)); o = []

    # ---- elevasi tiap tier + notasi ----
    for t in range(0, TIERS+1):
        z = t*RISER
        o.append(line(SPAN, -z, SPAN + 340, -z, "leader"))
        o.append(txt(SPAN + 400, -z - 6*draw.U, f"+{z/1000:.2f}", "dimtxt", "start"))
    o.append(line(SPAN, -3600, SPAN + 340, -3600, "leader"))
    o.append(txt(SPAN + 400, -3600 - 6*draw.U, "+3.60", "dimtxt", "start"))
    o.append(mtag(2500, -250, 2000, -4700, "P2", "SKIRT PELAT 2 mm", "middle"))
    o.append(mtag(6000, -2040, 5600, -4260, "W1", "PAPAN PINUS 400\u00d740", "middle"))
    o.append(mtag(9000, -2500, 9200, -4700, "P8", "PLAT DEK BORDES 8 mm", "middle"))
    o.append(mtag(11000, -1250, 12000, -4260, "P2", "PLAT RISER 2 mm", "middle"))
    o.append(mtag(14500, -3100, 14600, -4700, "W2", "SANDARAN PANEL PINUS 40 mm", "middle"))
    o.append(mtag(SPAN, -1650, 17200, -4260, "H3", "BALUSTRADE HOLLOW 40\u00d740", "middle"))
    o.append(txt(SPAN/2, -3800, "SANDARAN BELAKANG — RANGKA HOLLOW + PANEL KAYU", "lbl"))
    o.append(txt(SPAN/2, 1700,
                 "TAMPAK DEPAN (dari sisi lapangan) — skirt penutup kolong 2 mm, "
                 "muka tier plat riser 2 mm, dek bordes 8 mm, tepi papan pinus 400x40", "note"))
    s.g("lay-notasi", "".join(o))
    return s.render()


# ============ potongan (side / portal / stair) ============
def _section_frame(mode="portal"):
    H = 4200
    s = SVG(0, 0, (-PAD*0.9, -H, DEPTH + 2*PAD, H + PAD*1.4))
    o = []
    if mode != "stair":
        for t in range(1, TIERS+1):
            yf, z = tier_front(t), deck_z(t)
            o.append(rect(yf, -z-8, TIER_D, 8, "deckS"))
            o.append(rect(yf, -z-40-8, 400, 40, "pinusS"))
            o.append(rect(yf-2, -z, 2, RISER, "riserS"))
        s.g("lay-dek", "".join(o)); o = []
        for y in ROWS:
            top = col_top(y)
            o.append(rect(y-50, -top, 100, top, "colS"))
        s.g("lay-kolom", "".join(o)); o = []
        for t in range(1, TIERS+1):
            yf, z = tier_front(t), deck_z(t)
            o.append(rect(yf-25, -z+5, 50, 100, "beamS"))
            o.append(rect(yf+TIER_D/2-25, -z+8, 50, 100, "stiffS"))
        o.append(rect(DEPTH-25, -2500+5, 50, 100, "beamS"))
        s.g("lay-balok", "".join(o)); o = []
    if mode == "side":
        for t in range(1, TIERS+1):
            z = deck_z(t)
            yf = tier_front(t)
            o.append(rect(yf, -z-1140, TIER_D, 40, "railS"))
            o.append(rect(yf, -z-590, TIER_D, 40, "railS"))
            for i in range(11):
                yy = yf + i*100
                if yy > yf + TIER_D: break
                o.append(rect(yy-20, -z-1100, 40, 1100, "balS"))
            o.append(rect(yf, -z-100, TIER_D, 100, "toeS"))
        s.g("lay-railing", "".join(o)); o = []
        for (p, q) in [(3000, 4000), (4000, 5000)]:
            o.append(line(p, 0, q, -col_top(q), "braceS"))
            o.append(line(q, 0, p, -col_top(p), "braceS"))
        s.g("lay-brace", "".join(o)); o = []
    if mode == "stair":
        # profil anak tangga menerus 0 -> 2500
        for t in range(1, TIERS+1):
            yf, z0 = tier_front(t), deck_z(t) - RISER
            for k in range(ST_N):
                y0 = yf + k*ST_T
                zk = z0 + (k+1)*ST_R
                w = ST_T if k < ST_N-1 else TIER_D - 2*ST_T
                o.append(rect(y0, -zk-4, w, 4, "treadS"))
                o.append(rect(y0-4, -zk, 4, ST_R, "riserS"))
                o.append(rect(y0, -zk-8, 50, 5, "nosingS"))
        # stringer sebagai garis zig-zag
        pts = [(0, 0)]
        for t in range(1, TIERS+1):
            yf, z0 = tier_front(t), deck_z(t) - RISER
            for k in range(ST_N):
                y0 = yf + k*ST_T
                zk = z0 + (k+1)*ST_R
                w = ST_T if k < ST_N-1 else TIER_D - 2*ST_T
                pts += [(y0, -zk), (y0+w, -zk)]
        o.append(pline(pts, "stringerS"))
        s.g("lay-tangga", "".join(o)); o = []
        o.append(rect(2938-CONC_H/2, -2500, CONC_H, 2500, "concS"))
        o.append(txt(2938, -2680, "BUKAAN TANGGA A+B 2000 \u2014 2 LINTASAN BERSIH 700", "note"))
        s.g("lay-beton", "".join(o)); o = []
        # tepi dek kiri-kanan jalur (garis putus)
        for t in range(1, TIERS+1):
            z = deck_z(t)
            o.append(line(tier_front(t), -z, tier_front(t)+TIER_D, -z, "ghost"))
        s.g("lay-dek", "".join(o)); o = []
    for y in ROWS if mode != "stair" else []:
        o.append(rect(y-75, 0, 150, 10, "bpS"))
        o.append(rect(y-75, 10, 150, 10, "karetS"))
    if o:
        s.g("lay-bp", "".join(o)); o = []
    o.append(line(-400, 0, DEPTH+400, 0, "slab"))
    o.append(dim_h(0, DEPTH, 900, "5000"))
    for t in range(1, TIERS+1):
        o.append(dim_h(tier_front(t), tier_front(t)+TIER_D, 500, "1000"))
    o.append(dim_v(0, -2500, -560, "2500"))
    for t in range(1, TIERS+1):
        o.append(dim_v(-deck_z(t)+RISER, -deck_z(t), DEPTH+560, "500"))
    if mode != "stair":
        o.append(dim_v(-deck_z(3)+5, -deck_z(3)+105, tier_front(3)-160, "100"))
        o.append(dim_h(tier_front(2), tier_front(2)+400, -deck_z(2)-320, "400"))
        o.append(dim_h(tier_front(4), tier_front(4)+TIER_D/2, -deck_z(4)-200, "500"))
        o.append(dim_h(ROWS[1]-75, ROWS[1]+75, 330, "150"))
    else:
        o.append(dim_h(tier_front(2), tier_front(2)+ST_T, 300, "267"))
        o.append(dim_v(-ST_R, 0, -300, "167"))
    s.g("lay-dim", "".join(o)); o = []
    if mode != "stair":
        o.append(mtag(tier_front(4)+500, -deck_z(4)-8, -1000, -3900, "P8", "PLAT BORDES 8 mm", "start"))
        o.append(mtag(tier_front(3)+2, -deck_z(3)+55, -1000, -3560, "H1", "BALOK HOLLOW 50\u00d7100\u00d72,3", "start"))
        o.append(mtag(tier_front(5)+200, -deck_z(5)-30, -1000, -3220, "W1", "PAPAN PINUS 400\u00d740", "start"))
        o.append(mtag(tier_front(3), -deck_z(3)+260, -1000, -2880, "P2", "PLAT RISER 2 mm", "start"))
        o.append(mtag(ROWS[2], 12, 2600, 1320, "B8", "BASE PLATE 150\u00d7150\u00d78 + KARET 10 mm", "middle"))
        o.append(mtag(tier_front(4)+TIER_D/2, -deck_z(4)+60, 6300, -3900, "H1", "STIFFENER 50\u00d7100\u00d72,3 @500", "end"))
    else:
        o.append(mtag(600, -370, 1400, -3400, "P4", "PLAT TEKUK BORDES 4 mm", "start"))
        o.append(mtag(300, -180, 1400, -3080, "F1", "CAT EPOXY KUNING 50 mm (nosing)", "start"))
        o.append(mtag(2938+CONC_H/2, -1900, 6300, -3400, "C1", "KOLOM BETON EKSISTING 600\u00d7500", "end"))
    if mode == "side":
        o.append(mtag(tier_front(3)+500, -deck_z(3)-1140, 6300, -3560, "H2", "RAIL HOLLOW 40\u00d740\u00d72", "end"))
        o.append(mtag(tier_front(3)+300, -deck_z(3)-700, 6300, -3220, "H3", "BALUSTER 40\u00d740\u00d72,8 @100", "end"))
        o.append(mtag(tier_front(2)+500, -deck_z(2)-50, 6300, -2880, "P2", "TOE-BOARD PELAT 2 mm", "end"))
    s.g("lay-notasi", "".join(o))
    return s

def s05():
    return _section_frame("side").render()

def s06():
    return _section_frame("portal").render()

def s07():
    return _section_frame("stair").render()

# ============ S-08 DETAIL TANGGA ============
def s08():
    s = SVG(0, 0, (-620, -1500, 2700, 2150))
    o = []
    z0 = 0
    for k in range(ST_N):
        y0 = k*ST_T
        zk = (k+1)*ST_R
        w = ST_T if k < ST_N-1 else 466
        o.append(rect(y0, -zk-4, w, 4, "treadS"))
        o.append(rect(y0-4, -zk, 4, ST_R, "riserS"))
        o.append(rect(y0, -zk-8, 50, 5, "nosingS"))
        o.append(dim_h(y0, y0+ST_T if k < ST_N-1 else y0+466, 180, f"{ST_T if k<ST_N-1 else 466}"))
        o.append(dim_v(-zk, -zk+ST_R, y0-120, f"{ST_R}"))
    o.append(pline([(0,0), (0,-ST_R), (ST_T,-ST_R), (ST_T,-2*ST_R),
                    (2*ST_T,-2*ST_R), (2*ST_T,-3*ST_R), (2*ST_T+466,-3*ST_R)], "stringerS"))
    s.g("lay-tangga", "".join(o)); o = []
    o.append(dim_h(0, 2*ST_T+466, 340, "1000 (satu tier)"))
    o.append(dim_v(-3*ST_R, 0, -420, "500"))
    o.append(dim_h(0, 50, -3*ST_R-160, "50 cat"))
    o.append(dim_v(-ST_R-4, -ST_R, 2*ST_T+180, "4"))
    o.append(mtag(400, -ST_R-4, 700, -430, "P4"))
    o.append(mtag(25, -3*ST_R-6, 300, -740, "F1"))
    o.append(mtag(2*ST_T+400, -3*ST_R, 2*ST_T+700, -740, "H1"))
    o.append(txt(680, -880, "2R + T = 2(167) + 267 = 601 mm  (rentang nyaman 600–650)", "note"))
    o.append(txt(680, -740, "PLAT TEKUK BORDES 4 mm • NOSING = CAT EPOXY KUNING 50 mm, TIDAK MENONJOL", "note"))
    o.append(txt(680, 420, "3 OPTREDE 167 + 3 ANTREDE 267 PER TIER — SATU TIER NAIK 500 mm", "note"))
    s.g("lay-notasi", "".join(o))
    return s.render()

# ============ S-09 DETAIL RAILING ============
def s09():
    s = SVG(0, 0, (-900, -1900, 3300, 2900))
    o = []
    o.append(rect(0, 0, 2000, 5, "deckS"))
    o.append(rect(0, -100, 2000, 100, "toeS"))
    for i in range(21):
        x = i*100
        o.append(rect(x-20, -1100, 40, 1100, "balS"))
    o.append(rect(0, -1140, 2000, 40, "railS"))
    o.append(rect(0, -590, 2000, 40, "railS"))
    s.g("lay-railing", "".join(o)); o = []
    o.append(dim_h(0, 100, 320, "100 maks (celah bersih)"))
    o.append(dim_v(-1100, 0, -320, "1100"))
    o.append(dim_v(-550, 0, 2300, "550"))
    o.append(dim_v(-100, 0, -560, "100"))
    o.append(dim_h(0, 2000, 560, "2000 (tipikal per tier)"))
    o.append(dim_v(-1140, -1100, 2300, "40"))
    o.append(dim_h(0, 40, -1260, "40"))
    o.append(mtag(1900, -1120, 2160, -1330, "H2"))
    o.append(mtag(1800, -800, 2160, -960, "H3"))
    o.append(mtag(1700, -50, 2160, -300, "P2"))
    o.append(mtag(1500, 3, 2160, 120, "P8"))
    s.g("lay-dim", "".join(o)); o = []
    o.append(txt(1000, -1400, "BALUSTRADE ANTI-PANJAT — BALUSTER VERTIKAL, TANPA GARIS HORIZONTAL YANG BISA DIPIJAK", "note"))
    o.append(txt(1000, 700, "TIANG HOLLOW 40x40x2,8 @100  •  RAIL HOLLOW 40x40x2  •  TOE-BOARD PLAT 2 mm t=100", "note"))
    s.g("lay-notasi", "".join(o))
    return s.render()

# ============ S-10 DETAIL BASE PLATE ============
def s10():
    s = SVG(0, 0, (-700, -1400, 2600, 2200))
    o = []
    # tampak samping
    o.append(rect(0, 0, 150, 10, "bpS"))
    o.append(rect(0, 10, 150, 10, "karetS"))
    o.append(rect(25, -700, 100, 700, "colS"))
    o.append(line(-200, 20, 400, 20, "slab"))
    o.append(f'<path d="M25,0 l-22,0 l22,-22 z" class="weld"/>')
    o.append(f'<path d="M125,0 l22,0 l-22,-22 z" class="weld"/>')
    o.append(dim_h(0, 150, 220, "150"))
    o.append(dim_v(0, 10, -120, "10"))
    o.append(dim_v(10, 20, -320, "10 karet"))
    o.append(txt(560, -560, "LAS SUDUT a=4 mm KELILING", "note", "start"))
    o.append(line(120, -520, 540, -570, "leader"))
    # denah base plate
    ox = 1500
    o.append(rect(ox, -300, 150, 150, "bp"))
    o.append(rect(ox+50, -275, 50, 100, "col"))
    o.append(dim_h(ox, ox+150, 20, "150"))
    o.append(dim_v(-300, -150, ox-120, "150"))
    o.append(txt(ox+75, -420, "DENAH", "note"))
    o.append(txt(75, -900, "TAMPAK", "note"))
    s.g("lay-bp", "".join(o)); o = []
    o.append(dim_h(25, 125, -820, "100"))
    o.append(mtag(75, 5, 620, 300, "B8"))
    o.append(mtag(75, 15, 620, 480, "K1"))
    o.append(mtag(75, -400, 620, -180, "H1"))
    o.append(txt(900, 640, "TUMPUAN SENDI — KOLOM DUDUK LEPAS DI ATAS KARET 10 mm, TANPA DYNABOLT KE PELAT LANTAI", "note"))
    o.append(txt(900, 880, "TEKANAN TUMPU RENCANA 0,57 MPa  •  PELAT 150x150x8 (BJ 37)", "note"))
    s.g("lay-notasi", "".join(o))
    return s.render()

# ============ S-11 DETAIL SAMBUNGAN ============
def s11():
    """Empat detail sambungan, tiap detail punya sel sendiri supaya teks tidak bertabrakan."""
    PITCH = 1500
    s = SVG(0, 0, (-750, -1400, PITCH*4, 2150))
    o = []

    def detail(k, tag, name, body, notes):
        ox = k * PITCH
        o.append(txt(ox, -1180, tag, "dtitle"))
        o.append(txt(ox, -1180 + 13*draw.U, name, "note"))
        o.extend(body(ox))
        o.append(draw.txt_lines(ox, 330, notes, "note"))
        if k:
            o.append(line(ox - PITCH/2, -1300, ox - PITCH/2, 640, "ghost"))

    def d1(ox):
        return [rect(ox-40, -900, 40, 900, "colS"),
                rect(ox-260, -560, 480, 50, "beamS"),
                f'<path d="M{ox-40:.0f},-560 l-26,0 l26,-26 z" class="weld"/>',
                f'<circle cx="{ox-80}" cy="-535" r="16" class="bolt"/>',
                f'<circle cx="{ox-80}" cy="-585" r="16" class="bolt"/>',
                rect(ox-100, -610, 60, 110, "gusset"),
                dim_h(ox-260, ox+220, 130, "480")]

    def d2(ox):
        return [rect(ox-160, -900, 40, 900, "colS"),
                poly([(ox-160,-620),(ox+40,-620),(ox-160,-420)], "gusset"),
                line(ox+40, -620, ox+260, -840, "braceS"),
                f'<path d="M{ox-140:.0f},-600 l-26,26 l-26,-26 z" class="weld"/>',
                dim_h(ox-160, ox+40, 130, "200")]

    def d3(ox):
        return [rect(ox-40, -900, 500, 900, "concS"),
                rect(ox-130, -560, 90, 120, "gusset"),
                line(ox-330, -500, ox-130, -500, "anchorS"),
                f'<circle cx="{ox-85}" cy="-520" r="18" class="bolt"/>',
                f'<circle cx="{ox-85}" cy="-460" r="18" class="bolt"/>',
                dim_h(ox-40, ox+460, 130, "500")]

    def d4(ox):
        return [rect(ox-300, -60, 600, 5, "deckS"),
                rect(ox-300, -55, 600, 50, "beamS"),
                rect(ox-30, -300, 40, 240, "balS"),
                f'<path d="M{ox-30:.0f},-60 l-24,0 l24,-24 z" class="weld"/>',
                dim_v(-300, -60, ox+230, "240")]

    o.append(mtag(-200, -535, -560, -930, "H1"))
    o.append(mtag(PITCH+150, -730, PITCH+430, -930, "H2"))
    o.append(mtag(2*PITCH+200, -700, 2*PITCH+430, -930, "C1"))
    o.append(mtag(3*PITCH-10, -200, 3*PITCH+330, -930, "H3"))
    o.append(mtag(3*PITCH-200, -60, 3*PITCH-560, -700, "P8"))
    detail(0, "D1", "Balok tepi \u2192 kolom", d1,
           ["2\u00d7 baut M12 gr.4.6", "+ pelat siku 6 mm", "atau las a=4 mm 2\u00d780"])
    detail(1, "D2", "Bracing \u2192 kolom", d2,
           ["Pelat buhul 6 mm", "las a=4 mm dua sisi 40 mm"])
    detail(2, "D3", "Strut anchor \u2192 kolom beton", d3,
           ["Pelat 6 mm", "+ 2\u00d7 dynabolt M10", "kedalaman 80 mm"])
    detail(3, "D4", "Tiang railing \u2192 dek", d4,
           ["Las sudut a=4 mm", "keliling profil"])
    s.g("lay-detail", "".join(o))
    return s.render()


# ============ S-12 EXPLODED AXONOMETRIC ============
def s12():
    E = 3800  # jarak ledak antar lapis
    items = []
    def layer(dz, cls, draw):
        return draw(dz)
    o = []
    # 1. rangka kolom + balok  (dz = 0)
    b = []
    for x in PORTAL:
        for y in ROWS:
            b.append(iso_box(x-25, y-50, 0, 50, 100, col_top(y), "ax-top c-col", "ax-l c-col", "ax-r c-col"))
    for t in range(1, TIERS+1):
        yf, z = tier_front(t), deck_z(t)
        for (a, bb) in SEGMENTS:
            b.append(iso_box(a, yf-25, z-100, bb-a, 50, 100, "ax-top c-beam", "ax-l c-beam", "ax-r c-beam"))
    o.append(f'<g class="ax-layer" data-layer="rangka">{"".join(b)}</g>')
    # 2. dek plat bordes 8 mm (dz = E)
    b = []
    for t in range(1, TIERS+1):
        yf, z = tier_front(t), deck_z(t) + E
        for (a, bb) in SEGMENTS:
            b.append(iso_box(a, yf, z, bb-a, TIER_D, 8, "ax-top c-deck", "ax-l c-deck", "ax-r c-deck"))
    o.append(f'<g class="ax-layer" data-layer="dek">{"".join(b)}</g>')
    # 3. papan pinus (dz = 2E)
    b = []
    for t in range(1, TIERS+1):
        yf, z = tier_front(t), deck_z(t) + 2*E
        for (a, bb) in SEGMENTS:
            b.append(iso_box(a, yf, z, bb-a, 400, 40, "ax-top c-pin", "ax-l c-pin", "ax-r c-pin"))
    o.append(f'<g class="ax-layer" data-layer="pinus">{"".join(b)}</g>')
    # 4. tangga (dz = 3E)
    b = []
    for (a, bb) in AISLES:
        for t in range(1, TIERS+1):
            yf, z0 = tier_front(t), deck_z(t) - RISER + 3*E
            for k in range(ST_N):
                y0 = yf + k*ST_T
                w = ST_T if k < ST_N-1 else TIER_D - 2*ST_T
                b.append(iso_box(a, y0, z0 + (k+1)*ST_R, bb-a, w, 4, "ax-top c-stair", "ax-l c-stair", "ax-r c-stair"))
    o.append(f'<g class="ax-layer" data-layer="tangga">{"".join(b)}</g>')
    # 5. railing (dz = 4E)
    b = []
    for x in (0, SPAN):
        for t in range(1, TIERS+1):
            yf, z = tier_front(t), deck_z(t) + 4*E
            for i in range(0, 11):
                yy = yf + i*100
                if yy > yf + TIER_D: break
                b.append(iso_box(x-20, yy-20, z, 40, 40, 1100, "ax-top c-rail", "ax-l c-rail", "ax-r c-rail"))
    o.append(f'<g class="ax-layer" data-layer="railing">{"".join(b)}</g>')
    # 6. base plate (dz = -E)
    b = []
    pts = [(x, y) for x in PORTAL for y in ROWS]
    for (x, y) in pts:
        b.append(iso_box(x-75, y-75, -E, 150, 150, 10, "ax-top c-bp", "ax-l c-bp", "ax-r c-bp"))
    o.append(f'<g class="ax-layer" data-layer="baseplate">{"".join(b)}</g>')

    xs, ys = [], []
    for x in (0, SPAN):
        for y in (0, DEPTH):
            for z in (-E, 2500 + 4*E + 1100):
                px, py = iso(x, y, z)
                xs.append(px); ys.append(py)
    minx = min(xs) - 1600
    miny, maxy = min(ys) - 1600, max(ys) + 1600
    labx = max(xs) + 1200                      # semua label rata kiri di satu garis
    maxx = labx + 215 * draw.U                 # ruang untuk teks label
    s = SVG(0, 0, (minx, miny, maxx - minx, maxy - miny))
    s.add("".join(o))
    # label lapis
    labels = [("BASE PLATE 150x150x8 + KARET 10", -E), ("RANGKA HOLLOW 50x100x2,3", 1400),
              ("PLAT DEK BORDES 8 mm", 2500+E), ("PAPAN PINUS 400x40", 2500+2*E),
              ("PLAT TEKUK TANGGA 4 mm", 2500+3*E), ("RAILING HOLLOW 40x40 + TOE-BOARD 2 mm", 2500+4*E+900)]
    lb = []
    for name, z in labels:
        _, py = iso(SPAN + 900, DEPTH, z)
        lb.append(txt(labx, py, name, "axlbl", "start"))
        px2, py2 = iso(SPAN, DEPTH, z)
        lb.append(line(px2, py2, labx - 160, py, "leader"))
    s.g("lay-notasi", "".join(lb))
    return s.render()
