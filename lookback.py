"""METTA archive presentation inspired by the public Lookback interaction model."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,html
ROOT=Path(__file__).parent

def build(dist):
    tools=BeautifulSoup((dist/'index.html').read_text(encoding='utf-8'),'html.parser')
    back=tools.new_tag('a',href='index.html',attrs={'class':'archive-return'})
    back.string='← Arsip METTA'
    tools.select_one('.look-mast').insert(0,back)
    tools.select_one('title').string='SAP — METTA | Model 3D, gambar dan BOQ'
    brand=tools.select_one('.look-brand');brand.clear();brand.string='SAP';brand['aria-label']='Selaras Adhi Perkasa — proyek METTA'
    brand['title']='Selaras Adhi Perkasa'
    tools.select_one('.look-footer').insert(0,BeautifulSoup('<p class="sap-company-credit">SAP / SELARAS ADHI PERKASA</p>','html.parser'))
    style=tools.new_tag('style');style.string=(ROOT/'monochrome.css').read_text(encoding='utf-8');tools.body.append(style)
    (dist/'tools.html').write_text(str(tools),encoding='utf-8')
    archived=json.loads((ROOT/'assets/technical/manifest.json').read_text(encoding='utf-8'))
    for d in archived:
        d['title']='Arsip R03 / '+d['title'];d['revision']='R03';d['pdf']='assets/technical/METTA-R02-gambar-koordinasi.pdf'
        d['notes']=['Arsip R03. Tangga, penutup dan posisi X digantikan gambar R04.']+d.get('notes',[])
    current=json.loads((ROOT/'assets/r04/drawings.json').read_text(encoding='utf8'))
    for d in current:
        d.update(svg='assets/r04/'+d['code']+'.svg',dxf='assets/r04/'+d['code']+'.dxf',pdf='assets/r04/METTA-R04-tangga-detail.pdf',category='Denah' if d['code'] in ['T-01','T-06'] else 'Detail',revision='R04')
    drawings=current+archived
    e=html.escape
    cards=[]
    for i,d in enumerate(drawings):
        cards.append(f'''<article class="archive-card" data-index="{i}" data-category="{e(d['category'])}"><span class="card-number">{i+1:02}</span><button class="card-open" aria-label="Buka {e(d['code'])}: {e(d['title'])}"><img src="{e(d['svg'])}" alt="{e(d['title'])}" width="1191" height="842" loading="{'eager' if i<3 else 'lazy'}" decoding="async" draggable="false"></button><div class="card-caption"><span>{e(d['code'])}</span><span>{e(d['title'])}</span><span>({e(d['category'])}) · LOD 200</span></div></article>''')
    ticks=''.join(f'<button type="button" data-jump="{i}" aria-label="Ke gambar {d["code"]}"><i></i><span>{i+1:02}</span></button>' for i,d in enumerate(drawings))
    body='''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Arsip desain tribun METTA: 12 gambar koordinasi, model struktur dek bordes 4 mm, dan BOQ interaktif."><title>SAP — Arsip Desain METTA (09/2026)</title><link rel="stylesheet" href="lookback.css"></head><body data-view="timeline" data-brand-compact="false">
<a class="skip" href="#archive-stage">Lewati ke gambar</a>
<div class="entry-mask" aria-hidden="true"><span>SAP / SELARAS ADHI PERKASA</span></div>
<header class="archive-header"><a class="small-brand" href="#timeline" aria-label="Selaras Adhi Perkasa, halaman utama" title="Selaras Adhi Perkasa">SAP</a><span class="header-edition">ARSIP DESAIN METTA / 09.2026</span><button id="menu-toggle" aria-expanded="false" aria-controls="archive-menu">Menu <span aria-hidden="true">+</span></button></header>
<h1 class="archive-logo" aria-label="Selaras Adhi Perkasa — Arsip Desain METTA (09/2026)"><span class="logo-line sap-wordmark"><span>SELARAS ADHI PERKASA</span></span><span class="logo-line archive-project-title"><span>ARSIP DESAIN METTA</span></span><span class="logo-line archive-project-date"><span>(09/2026)</span></span></h1>
<main id="archive-stage" tabindex="-1"><section class="archive-carousel" aria-label="Gambar koordinasi METTA"><div class="archive-track">CARDS</div></section>
<section class="project-page" id="proyek" hidden><p class="mono">METTA / TRIBUN LT 04</p><h2>STRUKTUR BAJA.<br>DEK BORDES 4 MM.</h2><p>Usulan tribun lima tingkat dengan rangka RHS, delapan pengaku silang X, dan bidang duduk papan pinus. Dokumen R03 memuat model koordinasi, gambar teknik, serta kuantitas pekerjaan.</p><dl><div><dt>DIMENSI NOMINAL</dt><dd>17,70 × 5,00 m</dd></div><div><dt>ELEMEN RANGKA</dt><dd>161 batang</dd></div><div><dt>KOLOM / DIAGONAL</dt><dd>80 / 16 batang</dd></div><div><dt>LUAS DEK MODEL</dt><dd>82,345 m²</dd></div></dl><div class="project-links"><a href="tools.html#tiga-d">Model koordinasi 3D ↗</a><a href="tools.html#anggaran">Volume & estimasi biaya ↗</a><a href="tools.html#material">Spesifikasi & pemasok ↗</a><a href="tools.html#penawaran">Template penawaran ↗</a><a href="tools.html#lampiran">Lampiran teknis ↗</a></div><p class="project-stage mono">USULAN TEKNIS / KOORDINASI R03</p></section></main>
<div class="index-filter" hidden><span class="mono">INDEKS / 12 LEMBAR</span><label>Kategori <select id="category"><option>Semua</option><option>Denah</option><option>Potongan</option><option>Detail</option></select></label></div>
<footer class="archive-footer"><nav aria-label="Navigasi arsip"><a href="#timeline" data-view-link="timeline">Timeline,</a><a href="#surf" data-view-link="surf">Surf,</a><a href="#index" data-view-link="index">Indeks,</a><a href="#proyek" data-view-link="proyek">Proyek</a></nav><div class="timeline-scale" aria-label="Pilih gambar">TICKS</div><div class="archive-position"><span id="current-sheet">S-01</span><span> / 12</span><button id="previous" aria-label="Gambar sebelumnya">←</button><button id="next" aria-label="Gambar berikutnya">→</button></div><p class="drag-hint">GESER / SCROLL UNTUK MENELUSURI</p></footer>
<dialog id="archive-menu" aria-label="Menu dokumen METTA"><div class="menu-head"><span>SAP / SELARAS ADHI PERKASA</span><button id="menu-close" aria-label="Tutup menu">Tutup ×</button></div><nav aria-label="Dokumen proyek"><a href="#timeline">01 <span>Arsip gambar</span>↗</a><a href="tools.html#tiga-d">02 <span>Model 3D</span>↗</a><a href="tools.html#boq">03 <span>BOQ & biaya</span>↗</a><a href="tools.html#material">04 <span>Material</span>↗</a><a href="tools.html#pelaksanaan">05 <span>Pelaksanaan</span>↗</a><a href="tools.html#lampiran">06 <span>Lampiran teknis</span>↗</a></nav><p class="mono">DEK 4 MM / 5 TINGKAT / 8 PENGAKU X</p></dialog>
<dialog id="sheet-dialog" aria-labelledby="sheet-title"><div class="sheet-top"><h2 id="sheet-title">Gambar koordinasi</h2><button id="sheet-close">Tutup ×</button></div><div id="sheet-viewport" tabindex="0" aria-label="Gambar interaktif. Geser untuk pan, scroll untuk zoom."><img id="sheet-image" alt="" draggable="false"></div><div class="sheet-controls"><button id="sheet-minus" aria-label="Perkecil">−</button><output id="sheet-scale">100%</output><button id="sheet-plus" aria-label="Perbesar">+</button><button id="sheet-reset">Fit</button><span>GESER / ZOOM</span><button id="sheet-prev" aria-label="Lembar sebelumnya">←</button><button id="sheet-next" aria-label="Lembar berikutnya">→</button></div><details><summary>Catatan gambar</summary><p id="sheet-notes"></p></details><div class="sheet-download"><a id="sheet-dxf" download>DXF ↓</a><a id="sheet-svg" download>SVG ↓</a><a href="assets/technical/METTA-R02-gambar-koordinasi.pdf" target="_blank" rel="noopener">PDF lengkap ↗</a><a href="tools.html#revit-native">Lembar Revit ↗</a></div></dialog>
<noscript><style>.entry-mask{display:none}.archive-carousel{position:relative;overflow:auto;margin-top:45vh}.archive-track{position:relative;display:flex;gap:20px}.archive-card{position:relative!important;flex:0 0 75vw}.archive-footer{position:relative}</style><p>JavaScript diperlukan untuk rotasi galeri dan zoom. <a href="tools.html">Buka dokumen METTA</a></p></noscript>
<script>const METTA_DRAWINGS=DRAWINGS;</script><script src="panzoom.js"></script><script src="lookback.js"></script></body></html>'''.replace('CARDS',''.join(cards)).replace('TICKS',ticks).replace('DRAWINGS;',json.dumps(drawings,ensure_ascii=False)+';')
    body=body.replace('12 gambar koordinasi','6 gambar R04 dan 12 arsip R03').replace('INDEKS / 12 LEMBAR','INDEKS / 18 LEMBAR').replace(' / 12</span>',' / 18</span>').replace('id="current-sheet">S-01','id="current-sheet">T-01')
    body=body.replace('delapan pengaku silang X','sepuluh pengaku silang X').replace('Dokumen R03 memuat model koordinasi, gambar teknik, serta kuantitas pekerjaan.','Revisi R04 memakai tangga pelat tekuk 3 mm dan penutup 2 mm; model, gambar dan RAB terurai tersedia bersama arsip R03.').replace('161 batang','165 batang').replace('80 / 16 batang','80 / 20 batang').replace('USULAN TEKNIS / KOORDINASI R03','USULAN TEKNIS / KOORDINASI R04').replace('8 PENGAKU X','10 PENGAKU X')
    body=body.replace('<a href="assets/technical/METTA-R02-gambar-koordinasi.pdf" target="_blank" rel="noopener">PDF lengkap','<a id="sheet-pdf" href="assets/r04/METTA-R04-tangga-detail.pdf" target="_blank" rel="noopener">PDF revisi terkait')
    body=body.replace('href="tools.html#anggaran"','href="r04.html#rab"').replace('href="tools.html#penawaran"','href="r04.html#penawaran-r04"').replace('href="tools.html#boq"','href="r04.html#rab"')
    (dist/'index.html').write_text(body,encoding='utf-8')
    for name in ['lookback.css','lookback.js','panzoom.js']:(dist/name).write_bytes((ROOT/name).read_bytes())
