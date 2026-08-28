# -*- coding: utf-8 -*-
"""Helper SVG: transform mm -> px, garis ukur, arsir."""
from geom import *

class SVG:
    def __init__(self, w, h, vb):
        self.w, self.h = w, h
        self.vb = vb            # (minx, miny, width, height) dalam satuan gambar
        self.parts = []
    def add(self, s):
        self.parts.append(s)
    def g(self, cls, body, extra=""):
        self.parts.append(f'<g class="{cls}"{extra}>{body}</g>')
    def render(self, cls="dwg"):
        x, y, w, h = self.vb
        return (f'<svg class="{cls}" viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" '
                f'preserveAspectRatio="xMidYMid meet" role="img">'
                + "".join(self.parts) + "</svg>")

def rect(x, y, w, h, cls="", extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" class="{cls}"{extra}/>'

def line(x1, y1, x2, y2, cls=""):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"/>'

def poly(pts, cls="", extra=""):
    d = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
    return f'<polygon points="{d}" class="{cls}"{extra}/>'

def pline(pts, cls=""):
    d = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
    return f'<polyline points="{d}" class="{cls}"/>'

def txt(x, y, s, cls="lbl", anchor="middle", rot=None):
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" '
            f'text-anchor="{anchor}"{tr}>{s}</text>')

# U = satuan gambar per piksel layar; diset per lembar oleh build.py supaya tanda ukur,
# jarak teks, dan gelembung grid punya ukuran layar yang sama di semua skala.
U = 17.0
def set_u(v):
    global U
    U = float(v)

def dim_h(x1, x2, y, label=None, cls="dim", flip=False):
    """Garis ukur horizontal pada ketinggian y."""
    lab = label if label is not None else f"{abs(int(x2-x1))}"
    o = []
    t = 7 * U
    o.append(line(x1, y - t/2, x1, y + t/2, cls + " tick"))
    o.append(line(x2, y - t/2, x2, y + t/2, cls + " tick"))
    o.append(line(x1, y, x2, y, cls))
    o.append(txt((x1+x2)/2, y - 5*U, lab, "dimtxt"))
    return "".join(o)

def dim_v(y1, y2, x, label=None, cls="dim"):
    lab = label if label is not None else f"{abs(int(y2-y1))}"
    o = []
    t = 7 * U
    o.append(line(x - t/2, y1, x + t/2, y1, cls + " tick"))
    o.append(line(x - t/2, y2, x + t/2, y2, cls + " tick"))
    o.append(line(x, y1, x, y2, cls))
    o.append(txt(x - 5*U, (y1+y2)/2, lab, "dimtxt", rot=-90))
    return "".join(o)

def grid_bubble(x, y, name, r=None):
    if r is None:
        r = 10 * U
    return (f'<g class="bub"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
            + txt(x, y + r*0.32, name, "bubtxt") + "</g>")

# ---------- proyeksi isometrik untuk aksonometri ----------
import math
CA, SA = math.cos(math.radians(30)), math.sin(math.radians(30))

def txt_lines(x, y, lines, cls="note", anchor="middle", lh=1.35, fs=12.0):
    """Teks beberapa baris; jarak baris mengikuti U supaya konsisten di semua skala."""
    step = lh * fs * U
    return "".join(txt(x, y + i*step, s, cls, anchor) for i, s in enumerate(lines))


def iso(x, y, z):
    return ((x - y) * CA, (x + y) * SA - z)

def iso_box(x, y, z, dx, dy, dz, cls_top="ax-top", cls_l="ax-l", cls_r="ax-r", extra=""):
    """Kotak isometrik sederhana: 3 muka."""
    p = lambda a, b, c: iso(x + a, y + b, z + c)
    top = [p(0,0,dz), p(dx,0,dz), p(dx,dy,dz), p(0,dy,dz)]
    left = [p(0,0,0), p(0,dy,0), p(0,dy,dz), p(0,0,dz)]
    frnt = [p(0,0,0), p(dx,0,0), p(dx,0,dz), p(0,0,dz)]
    return (poly(frnt, cls_r, extra) + poly(left, cls_l) + poly(top, cls_top))


# ---------- penanda material (leader + kode / teks penuh) ----------
def mtag(px, py, tx, ty, code, full=None, anchor="start"):
    """Garis penunjuk dari titik elemen (px,py) ke teks di (tx,ty).
    `code` dipakai untuk legenda; `full` = teks yang tampil (kalau None, kodenya)."""
    label = full if full is not None else code
    dot = 2.2 * U
    body = (f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" class="leader"/>'
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{dot:.1f}" class="mdot"/>')
    off = 3.0 * U
    lx = tx + (off if anchor == "start" else (-off if anchor == "end" else 0))
    body += txt(lx, ty - 2.0*U, label, "mtxt", anchor)
    return f'<g class="mtag" data-mat="{code}">{body}</g>'
