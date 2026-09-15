"""Draw coordinated R08 plan, sections and mesh detail from generated quantities."""
import html, json
from pathlib import Path

def build(d,g,out):
    def fmt(x,n=0):return f'{x:,.{n}f}'.translate(str.maketrans({',':'.','.':','}))
    def begin(title,subtitle):return ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 850"><defs><pattern id="mesh" width="9" height="9" patternUnits="userSpaceOnUse"><path d="M0 0H9V9" fill="none" stroke="#22866f" stroke-width=".6"/></pattern></defs><rect width="1200" height="850" fill="#faf9f5"/><style>text{font-family:Arial,sans-serif;fill:#183b45;font-size:15px}.small{font-size:12px}.title{font-size:25px;font-weight:bold}.dim{stroke:#52727a;stroke-width:1;fill:none}</style>',f'<text x="40" y="45" class="title">{html.escape(title)}</text><text x="40" y="72">{html.escape(subtitle)}</text>']
    def text(a,x,y,s,cls=''):a.append(f'<text x="{x}" y="{y}" class="{cls}">{html.escape(str(s))}</text>')
    def rect(a,x,y,w,h,fill,stroke='#385b65'):a.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{max(0,w):.3f}" height="{max(0,h):.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
    def polygon(a,p,xf,yf,fill):
        coords=p['coordinates']; polygons=[coords] if p['type']=='Polygon' else coords
        for rings in polygons:
            path=' '.join('M'+' L'.join(f'{xf(x):.3f},{yf(y):.3f}' for x,y in ring)+' Z' for ring in rings)
            a.append(f'<path d="{path}" fill="{fill}" fill-rule="evenodd" stroke="#47636b" stroke-width=".8"/>')
    def end(a,name):
        text(a,40,814,'METTA / R08 / 15 September 2026 / satuan mm / STUDIO KOORDINASI — BELUM UNTUK FABRIKASI','small')
        a.append('</svg>');(out/name).write_text(''.join(a),encoding='utf-8')
    xf=lambda x:70+x*.059;yf=lambda y:180+(5492-y)*.067
    for mode in ['r07','r08']:
        a=begin('01 / Denah '+mode.upper(),'Pilihan B: dua zona tetap; panel tengah 800 mm di zona kiri diisi tribun.' if mode=='r08' else 'Acuan sebelum perubahan. Zona kiri 2000 mm dan zona kanan 600 mm.')
        for t in range(5):
            for x,X in [(0,4850),(6850.0751,12250.0643),(12850.0631,17700)]:
                rect(a,xf(x),yf((t+1)*1000),(X-x)*.059,1000*.067,'#e4e9e6')
                rect(a,xf(x),yf(t*1000+400),(X-x)*.059,400*.067,'#c8a881')
        rect(a,xf(0),yf(5492),17700*.059,492*.067,'#e4e9e6')
        if mode=='r08':
            stairs=g['stairs']
            for p in g['infill']:polygon(a,p['polygon'],xf,yf,'#abddce')
            for p in g['wood']:polygon(a,p['polygon'],xf,yf,'#d6ae70')
        else:
            old=json.loads((Path(__file__).parent/'assets/r04/data.json').read_text(encoding='utf-8'))
            stairs=[dict(polygon={'type':'Polygon','coordinates':[p['outer']]+p['holes']}) for s in old['stairs'] for p in s['profile']['parts']]
        for s in stairs:polygon(a,s['polygon'],xf,yf,'#bfdaee')
        for c in g['concrete']:
            lo,hi=c['lo'],c['hi'];rect(a,xf(lo[0]),yf(hi[1]),(hi[0]-lo[0])*.059,(hi[1]-lo[1])*.067,'#9b9b99')
        for t in range(5):text(a,1130,yf(t*1000+500),f'+{(t+1)*500}','small')
        a.append(f'<path class="dim" d="M70 140H{xf(17700):.2f} M70 130V150 M{xf(17700):.2f} 130V150"/>');text(a,540,128,'17700')
        text(a,350,590,'Zona kiri: 600 + 800 + 600 mm' if mode=='r07' else 'Zona kiri: 600 / INFILL 800 / 600 mm')
        text(a,740,620,'Zona kanan: 600 mm')
        text(a,40,662,'Hijau: infill baru · cokelat: dudukan · biru: tapak tangga · abu-abu gelap: kolom beton')
        text(a,40,693,'R08 mempertahankan tiga strip jalur nominal 600 mm pada dua zona. Lebar efektif belum dikurangi pegangan.')
        text(a,40,720,'Tambahan tempat duduk indikatif: '+str(d['changes']['extra_indicative_seats'])+' (modul 500 mm; baris ke-4 terpotong kolom beton).')
        text(a,40,747,'Kapasitas total operasi, aksesibilitas dan jalur evakuasi belum disahkan; jumlah zona bukan jumlah pintu keluar.')
        end(a,'01-denah-'+mode+'.svg')

    a=begin('02 / Infill 800 mm — rangka dan takikan','RHS 50×100; tebal mengikuti RAB. Posisi ini usulan koordinasi, bukan detail sambungan sah.')
    xx=lambda x:85+(x-d['params']['x0'])*.27; yy=lambda y:140+y*.093
    for p in g['infill']:polygon(a,p['polygon'],xx,yy,'#e4f2e9')
    for e in g['frame']:
        v=e['vertices'];lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
        rect(a,xx(lo[0]),yy(lo[1]),(hi[0]-lo[0])*.27,(hi[1]-lo[1])*.093,'#478985' if e['group']!='I01' else '#e3a34f')
    for c in g['concrete']:
        lo,hi=c['lo'],c['hi']
        if d['params']['x0']<lo[0]<d['params']['x1']:rect(a,xx(lo[0]),yy(lo[1]),(hi[0]-lo[0])*.27,(hi[1]-lo[1])*.093,'#969b98')
    text(a,82,121,'DENAH INFILL / lebar 800')
    for t in range(5):text(a,320,yy(t*1000+500),f'T{t+1} / +{(t+1)*500}','small')
    # Cross section: actual proposed vertical stack, no misleading joist below bearer.
    rect(a,520,170,480,12,'#a2b3bb');text(a,520,153,'POTONGAN MELINTANG / tingkat tipikal')
    rect(a,520,182,480,60,'#78a9a0');text(a,1010,210,'RHS silang','small')
    for x in [562,928]:
        rect(a,x,242,30,60,'#407770');rect(a,x,302,30,200,'#d79a51');rect(a,x-27,502,84,5,'#556979')
    text(a,520,542,'Dek 4 / pengaku tinggi 100 / balok tinggi 100 / kolom / base 8 + karet 3','small')
    for i,s in enumerate([
        '20 kolom baru; 10 balok memanjang; pengaku silang mengikuti daftar potong.',
        'Base usulan 140×150×8; 4 angkur/kolom hanya allowance. Verifikasi lantai wajib.',
        'Takik RC dengan celah 3. Posisi kolom T3/T4 bergeser menghindari beton.',
        'T4: tumpuan depan pada y3300; bagian depan balok menjorok 300 mm.',
        'Periksa kantilever, reaksi lantai, stabilitas, sambungan dan tepi dek di takikan.',
        'Delapan strut pendek dan enam strip dek lama diganti; railing lama dipertahankan.'
    ]):text(a,440,588+i*27,s,'small')
    text(a,40,770,'Elemen infill belum masuk model Revit. Hitungan kuantitas berasal dari geometri usulan pada paket R08.','small')
    end(a,'02-infill.svg')

    a=begin('03 / Penutup sisi kawat loket','Kedua sisi luar menjadi mesh. Riser depan setiap tingkat dan sisi infill tetap pelat.')
    for side,offset in [('KIRI',70),('KANAN',650)]:
        panels=[p for p in g['mesh'] if (p['bounds'][0]<1000)==(side=='KIRI')]
        for p in panels:
            x,y,z,X,Y,Z=p['bounds'];rect(a,offset+y*.085,410-Z*.09,(Y-y)*.085,(Z-z)*.09,'url(#mesh)')
        text(a,offset,140,side)
    rect(a,80,475,330,210,'#335b61');rect(a,96,491,298,178,'url(#mesh)')
    rect(a,96,491,298,8,'#d9aa62');rect(a,96,661,298,8,'#d9aa62')
    rect(a,96,491,8,178,'#d9aa62');rect(a,386,491,8,178,'#d9aa62')
    text(a,80,720,'DETAIL SKEMATIS — ukuran panel dari CSV/JSON','small')
    details=[
       f'{d["changes"]["mesh_panels"]} subframe panel SHS 40×40; ukuran luar maks. 800×800.',
       'Mesh ditumpangkan pada frame; ujung kawat tertutup strip 30×3.',
       'M6 + mur/ring galvanis maks. 200; 4 pengikat frame/panel: allowance.',
       'Rangka panel dan strip masuk berat serta RAB, tidak dianggap gratis.',
       'Bukaan/diameter: 25/1,6; 25/2,0; 50/2,0 mm. Pilih melalui toggle.',
       'Kandidat 25/2,0: bukaan lebih kecil; belum terbukti paling murah/aman.',
       'Harga belum berupa penawaran. Periksa sampel, galvanis dan mutu las.',
       'Mesh ini belum dinilai sebagai pagar penahan orang atau bracing.'
    ]
    for i,s in enumerate(details):text(a,450,492+i*30,s,'small')
    end(a,'03-mesh.svg')

    comparisons=''.join(f'<tr><td>{html.escape(o["label"])}</td><td>{fmt(o["roll_width_m"],1)} × {o["roll_length_m"]}</td><td>{fmt(o["catalogue_roll_kg"],1)}</td><td>{o["rolls"]}</td><td>{fmt(o["purchase_kg"],2)}</td><td>Rp{fmt(o["allowance_cost"])}</td><td><a href="{html.escape(o["source"])}">Katalog</a></td></tr>' for o in d['mesh_options'])
    page='''<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>METTA R08 — infill dan mesh</title><style>body{margin:0;background:#f4f3ed;color:#203f48;font:16px/1.6 Arial}main{max-width:1150px;margin:auto;padding:30px}h1{font-size:38px;line-height:1.15}a{color:#087663}button{padding:12px 18px;border:1px solid #507977;background:white;border-radius:8px;cursor:pointer}button[aria-pressed=true]{background:#1d665e;color:white}.card{background:white;padding:22px;border-radius:12px;margin:20px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}img{width:100%;height:auto}small{color:#64706e}.notice{border-left:5px solid #c38631;padding:15px;background:#fff3d7}</style><main><a href="../../tools.html?design=r08#rab-11sep">← Buka RAB dengan pilihan R08</a><p><a href="METTA-R08-RAB-portrait.pdf" download>PDF RAB portrait acuan tetap</a> — RHS 2,3 / SHS acuan / mesh 25–2,0 / biaya pelengkap aktif. Ekspor pilihan lain melalui RAB.</p><h1>R08 / Infill 800 mm<br>dan penutup mesh</h1><p>Dua zona tangga tetap pada posisi lama. Panel tengah zona kiri menjadi tingkat dan dudukan; bagian sampingnya tetap tangga.</p><p class="notice">Studi koordinasi dan estimasi biaya. Belum untuk fabrikasi atau penetapan kapasitas operasi.</p>'''
    c=d['changes'];page+=f'<div class="card"><b>{d["rhs"]["stock_count"]} batang RHS 6 m</b> · {d["rhs"]["cut_count"]} potongan · {fmt(d["rhs"]["length_m"],3)} m<br>{len(g["stairs"])} panel tangga tersisa · {c["extra_indicative_seats"]} tambahan tempat duduk indikatif · {fmt(c["mesh_area_m2"],3)} m² mesh bersih<br><small>RHS R07 101 batang tidak menjadi target R08. Berat berubah mengikuti tebal. SHS tangga + mesh {d["shs"]["stock_count"]} batang; railing lama 20 batang terpisah.</small></div>'
    page+='''<div class="card"><button data-plan="r08" aria-pressed="true">Gambar R08</button> <button data-plan="r07" aria-pressed="false">Bandingkan R07</button><img id="plan" src="01-denah-r08.svg" alt="Denah R08 infill tengah dan jalur tangga"><p><a href="01-denah-r08.svg" download>Unduh denah R08</a> · <a href="daftar-potong.csv" download>Daftar potong RHS, SHS dan strip</a></p></div><div class="card"><img src="02-infill.svg" alt="Rangka infill dan takikan beton"><img src="03-mesh.svg" alt="Kedua sisi mesh dan detail penjepit"></div><div class="card"><h2>Perbandingan mesh</h2><p>Massa roll dari katalog. Harga di bawah adalah allowance Rp30.000/kg untuk perencanaan, bukan penawaran pemasok. Angka belum mencakup rangka, penjepit dan upah; seluruhnya masuk tabel RAB.</p><div class="scroll"><table><thead><tr><th>Produk</th><th>Roll / m</th><th>Kg/roll</th><th>Roll beli</th><th>Kg beli</th><th>Allowance mesh</th><th>Sumber</th></tr></thead><tbody>'''+comparisons+'</tbody></table></div></div>'
    page+='<div class="card"><h2>Dasar dan urutan pelaksanaan</h2><ol>'+''.join('<li>'+html.escape(n)+'</li>' for n in d['notes'])+'</ol><p><a href="data.json">Kuantitas RAB</a> · <a href="audit.json">Seluruh pola potong dan nesting</a> · <a href="geometry.json">Geometri terkoordinasi</a></p></div>'
    page+='''<script>document.querySelectorAll('[data-plan]').forEach(b=>b.addEventListener('click',()=>{document.getElementById('plan').src='01-denah-'+b.dataset.plan+'.svg';document.querySelectorAll('[data-plan]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}));</script></main></html>'''
    (out/'index.html').write_text(page,encoding='utf-8')
