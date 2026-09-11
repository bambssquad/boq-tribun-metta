"""Reviewable engineering study and conceptual drawing sheets, sourced from R06."""
import json,html,math,re
from bs4 import BeautifulSoup
from pathlib import Path
ROOT=Path(__file__).parent;OUT=ROOT/'assets/r06'
def fmt(x,n=2):return 'Tidak stabil / di luar domain' if x is None else f'{x:,.{n}f}'.replace(',','_').replace('.',',').replace('_','.')
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+html.escape(str(x))+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def p(text):return '<p>'+text+'</p>'
def svg_start(title,height=820):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{height}" viewBox="0 0 1400 {height}"><rect width="1400" height="{height}" fill="white"/><style>text{{font-family:Arial,sans-serif;fill:#172a36}}.h{{font-size:24px;font-weight:bold}}.n{{font-size:17px}}.small{{font-size:14px}}</style>',f'<text x="40" y="42" class="h">{title}</text>','<text x="40" y="70" class="n" fill="#b33322">R06 / STUDI KOORDINASI — BUKAN GAMBAR PELAKSANAAN</text>']
def text(x,y,s,size='n'):
    s=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',s)
    return f'<text x="{x}" y="{y}" class="{size}">{html.escape(s)}</text>'
def line(x,y,X,Y,color='#172a36',width=2):return f'<line x1="{x}" y1="{y}" x2="{X}" y2="{Y}" stroke="{color}" stroke-width="{width}"/>'
def drawings(d):
    cols=d['geometry']['columns'];option=next(r for r in d['matrix'] if r['key']=='h16-1000')
    s=svg_start('S-01 / Grid eksisting dan dampak batas jarak 1.000 mm',980)
    for top,added,title in [(125,False,'A. EKSISTING / 80 kolom; koordinat lokal mm'),(545,True,'B. INFILL MAKS.1.000 / 146 kolom; konflik tangga harus diselesaikan')]:
        s.append(text(40,top,title));ox=90;oy=top+45;k=.065
        for a,b in [(4850,6850),(12250,12850)]:
            s.append(f'<rect x="{ox+a*k}" y="{oy}" width="{(b-a)*k}" height="{5000*k}" fill="#fde1d9"/>')
        for y in range(0,6000,1000):s+=[line(ox,oy+y*k,ox+17700*k,oy+y*k,'#aebbc3',1),text(45,oy+y*k+5,str(y),'small')]
        for c in cols:s.append(f'<rect x="{ox+c["x"]*k-3}" y="{oy+c["y"]*k-3}" width="6" height="6" fill="#172a36"/>')
        if added:
            for x in option['new_axes']:
                for y in range(0,6000,1000):s.append(f'<circle cx="{ox+x*k}" cy="{oy+y*k}" r="4" fill="#b33322"/>')
        s.append(text(ox,oy-13,'0'));s.append(text(ox+17700*k-50,oy-13,'17.700'))
        if not added:s.append(text(95,oy+5000*k+26,'Hitam: kolom arsip. Merah muda: proyeksi area tangga; bukan batas bebas untuk menambah kolom.','small'))
    s.append(text(40,960,'Grid gedung Revit berbeda dari sumbu lokal tribun. Titik tambahan merah belum boleh diterapkan ke model.','small'));s.append('</svg>')
    (OUT/'S01-grid.svg').write_text(''.join(s),encoding='utf-8')
    s=svg_start('S-02 / Jalur beban dan pilihan profil campuran',810)
    ox=70;oy=420;k=.19
    for i in range(6):
        x=ox+i*1000*k;h=min((i+1)*500,2500)*.11
        s+=[line(x,oy,x,oy-h,'#172a36',6),line(x-15,oy,x+15,oy,'#172a36',5)]
        if i<5:
            X=x+190;s+=[line(x,oy-h,X,oy-h,'#247a9a',5),line(x,oy-h+12,X,oy-h+12,'#172a36',3)]
    s+=[text(65,470,'Potongan lintang:5tier @1.000mm; naik @500mm. Biru=dek; joist tegak lurus bidang gambar.'),
        text(65,510,'1. Dek bordes4mm → pengaku longitudinal RHS50×100 @250mm.'),
        text(65,540,'2. Pengaku → balok silang → kolom → base/angkur → struktur beton LT4.'),
        text(65,570,'3. Profil campuran studi: joist1,6; kolom/balok/bracing2,3; bentang joist dibatasi hasil audit.'),
        text(65,600,'4. Ukuran100mm harus tegak pada joist. Putaran profil90° memerlukan hitung ulang.'),
        text(65,630,'5. Pelat dek bukan otomatis diafragma; sambungan pengumpul gaya horizontal harus dibuktikan.'),
        text(65,670,'Panjang batang5m bukan bentang bebas5m. Titik dudukan aktual wajib ditunjukkan pada gamtek.','h'),
        text(65,715,'Sambungan dudukan ke muka hollow tipis: beri jalur bearing ke dinding samping / penguatan lokal.'),
        text(65,745,'Dimensi pelat, las, baut dan angkur ditetapkan sesudah gaya tiap sambungan tersedia.')]
    s.append('</svg>');(OUT/'S02-loadpath.svg').write_text(''.join(s),encoding='utf-8')
    s=svg_start('S-03 / Railing dan detail yang wajib direvisi',820)
    for ox,b,t,label in [(120,40,2.3,'40×40×2,3 / tidak cukup pada model kantilever'),(760,60,2.3,'60×60×2,3 / calon pemeriksaan detail')]:
        s += [line(ox,450,ox,150,'#172a36',b/5),line(ox-40,450,ox+40,450,'#172a36',8),line(ox,150,ox+190,150,'#b33322',3),text(ox+30,130,'H titik =0,89kN'),text(ox+20,310,'tinggi1.100mm'),text(ox-60,490,label,'small')]
    s += [text(65,550,'Beban titik tetap mengendalikan walau jarak tiang dari1.000 menjadi500mm.'),
        text(65,585,'Alternatif: profil lebih besar, pengaku balik/return, atau rangka rail yang terbukti membagi beban.'),
        text(65,620,'Rumus kantilever mengasumsikan jepit sempurna. Base fleksibel menambah lendutan.'),
        text(65,655,'Detail baut tembus hollow: sleeve/diaphragm bila diperlukan agar dinding tidak terjepit remuk.'),
        text(65,690,'Pelat6mm yang sama tidak menjamin aman saat dinding hollow ditipiskan.'),
        text(65,735,'STUDI: belum menetapkan jumlah angkur, panjang tanam, pola lubang atau ukuran las final.','h')]
    s.append('</svg>');(OUT/'S03-railing.svg').write_text(''.join(s),encoding='utf-8')

def build():
 d=json.loads((OUT/'study.json').read_text(encoding='utf-8'));drawings(d);parts=[]
 def section(title,body):parts.append('<section><h2>'+title+'</h2>'+body+'</section>')
 section('Kesimpulan untuk keputusan',p('<strong>Jangan langsung mengganti seluruh hollow menjadi1,6mm atau merapatkan semua kolom menjadi1.000mm.</strong> Strategi paling masuk akal untuk dilanjutkan adalah mempertahankan kolom, balok utama dan bracing2,3mm, lalu menipiskan elemen sekunder yang lulus kasus lokal. Railing perlu desain tersendiri. Hasil ini memilih arah studi; belum membuktikan keamanan sistem lengkap.')+
 p('Subtotal kolom, balok, pengaku, bracing, railing dan komponen lain tersedia pada RAB. Semua angka studi di halaman ini adalah kondisi dasar sebelum edit manual RAB; pilihan studi tidak mengubah model atau RAB otomatis.')+
 '<ul><li>340/340 ID kolom/framing audit sebelumnya masih ditemukan pada Revit METTA. Panjang sampel kolom2.482mm, tiang railing1.100mm, dan joist4.850mm dibaca kembali. Koordinat seluruh node masih menggunakan arsip yang direkonsiliasi.</li><li>RHS50×100×1,6 pada bentang lokal2.040mm: joist @250mm lolos penyaringan; balok silang gagal dengan rasio1,158.</li><li>RHS2,0 pada geometri sama: rasio balok silang0,945, margin kecil terhadap asumsi beban/tebal; belum alasan menipiskan semua elemen.</li><li>SHS40×40 setinggi1.100mm tidak memenuhi penyaringan kantilever railing bahkan pada2,8mm. Kekakuan rangka rail nyata harus dibuktikan atau profil/detail diperbesar.</li><li>Infill maksimum1.000mm menghasilkan146kolom dan129stok RHS, serta potensi benturan tangga. Opsi ini bukan penghematan otomatis.</li></ul>')
 section('Dasar standar dan batas kesimpulan',p('SNI1727:2020 untuk beban; SNI1729:2020 mengadopsi AISC360-16 untuk baja struktural. SNI7971:2013 menjadi rute yang perlu diperiksa bila hollow masuk produk baja canai dingin terkait; asal canai dingin saja tidak cukup untuk memilih standar. Gempa dan beton/angkur memerlukan SNI1726:2019 dan SNI2847:2019. Identifikasi produk, sertifikat, geometri sudut dan mutu adalah bagian dari desain, bukan asumsi merek dagang.')+
 p('Katalog BSN mengonfirmasi status dan judul, bukan memberi akses seluruh klausul. Rumus pemeriksaan terbatas memakai sumber primer AISC/STI yang ditautkan; ICC300-2017 dipakai sebagai pembanding khusus tribun. Edisi dan adopsi yang disyaratkan proyek harus dikonfirmasi. Ini bukan audit kepatuhan seluruh klausul SNI.')+
 p('Asumsi: E200.000MPa, Fy235MPa, Fu370MPa, berat jenis7.850kg/m³; sensitivitas tebal0,93nominal; radius luar2t/dalamt. Faktor0,93 tidak menyatakan produk lokal bersertifikat ASTM A500. Limit lendutan balok L/360 dan railing11mm adalah target studi yang perlu disepakati, bukan klaim satu batas SNI berlaku untuk semua komponen.')+
 p('Tidak ada kredit kontinuitas, kekakuan sambungan, aksi komposit, diafragma ataupun kekuatan plastis tanpa bukti. Penampang nonkompak/langsing pada lentur atau bentang di luar domain pengekangan lateral tidak diberi label lulus. Tekan memakai penampang efektif. Kombinasi lentur–tekan dan panjang efektif diperiksa sebagai sensitivitas; bukan pengganti analisis3D/goyang.'))
 section('Beban dan alur gaya',table(['Besaran','Nilai','Makna'],[
 ['Luas dek',fmt(d['loads']['area_m2'])+'m²','Audit floor; bukan luas proyeksi penuh17,7×5m'],
 ['D / L','1,5 / 5,0kPa','D allowance perlu ditimbang ulang saat desain berubah'],
 ['D + L',fmt(d['loads']['dead_kN']+d['loads']['live_kN'])+'kN','Beban vertikal layanan seluruh dek'],
 ['1,2D + 1,6L',fmt(d['loads']['ultimate_kN'])+'kN','Beban vertikal terfaktor'],
 ['Titik tapak','1,334kN','Alternatif UDL untuk elemen tapak; bukan mengganti semua L'],
 ['Railing','0,73kN/m atau0,89kN titik','Alternatif arah paling merugikan; titik mengendalikan @1m'],
 ['Sway sejajar / tegak lurus',fmt(d['loads']['sway_parallel_kN'])+' / '+fmt(d['loads']['sway_perpendicular_kN'])+'kN','Pembanding ICC; lima baris penuh, dua arah tidak serentak']])+
 p('Alur vertikal: bordes → joist @250 → balok silang/tepi → kolom → base/angkur → balok/pelat beton LT4. Bila ada balok transfer yang menerima lebar tributari1m, hasilnya jauh lebih berat daripada balok tepi yang hanya menerima0,125m. Arah dan titik sambungan harus memastikan alur tersebut. Jangan membagi beban total rata ke80kolom untuk mendesain reaksi maksimum.')+
 p('Alur horizontal: rail/penonton → collector → bidang bracing dua arah → base dan ikatan beton. Tidak boleh menganggap sekrup bordes atau pelat penutup otomatis memberi diafragma. Angka sway bukan gaya gempa; di LT4, percepatan lantai dan respons gedung utama dapat mengendalikan.'))
 section('Perbandingan grid dan tebal',p('Geometri eksisting memakai13sumbu kolom pada baris depan dan15pada baris belakang, dengan beberapa posisi khusus tangga. Opsi rapat mempertahankan sumbu lama dan menyisipkan pembagi sama besar pada tiap celah yang melampaui target. Karena itu target1.000 menghasilkan bentang maksimum885mm, bukan persis1.000mm. Angka kolom baru mengasumsikan6kolom dan5balok silang per sumbu tambahan.')+
 table(['Tebal','Target maks.','Bentang aktual maks.','Kolom','Stok RHS','Rasio joist / silang','RAB rendah–tinggi (jt)','Potensi konflik tangga'],[[fmt(r['thickness_mm'],1),r['target_gap_mm'] or 'eksisting',fmt(r['max_gap_mm'],0),r['columns'],r['stocks'],fmt(r['joist']['ratio'],3)+' / '+fmt(r['bearer']['ratio'],3),fmt(r['cost_low']/1e6)+'–'+fmt(r['cost_high']/1e6),len(r['stair_conflicts'])] for r in d['matrix'] if r['target_gap_mm']!=885])+
 p('Rasio≤1 hanya berarti pemeriksaan lokal yang ditampilkan memenuhi asumsi; kolom, railing, sambungan, stabilitas dan beton tetap dapat mengendalikan. Infill pada zona tangga memiliki tabrakan proyeksi/tinggi dari pemeriksaan kotak pembatas; perlu model detail, tidak boleh dipasang begitu saja. Jumlah konflik adalah pasangan kolom–elemen tangga, bukan jumlah kolom unik.')+
 p('Harga dasar RAB2,3mm Rp'+fmt(d['baseline_total'],0)+'. Basis biaya: stok6m dan pola potong, upah RHS6.000/kg; penambahan base/angkur Rp250–500ribu per kolom dan sambungan Rp100ribu per balok silang sebagai allowance. Total mempertahankan SHS acuan dan item lain. Belum memasukkan redesain railing, penambahan bracing/collector, penguatan beton, relokasi utilitas, jasa desain, overhead/laba/pajak tambahan. Rentang bukan penawaran kontraktor.'))
 section('Profil campuran: penghematan setelah pola potong',table(['Pilihan','Stok tipis +2,3','Kg RHS beli','RAB (jt)','Hemat terhadap acuan (jt)'],[[r['name'],str(r['thin_stocks'])+' + '+str(r['thick_stocks']),fmt(r['purchase_kg']),fmt(r['cost']/1e6),fmt(r['saving']/1e6)] for r in d['mixed']])+
 p('Campuran1,6 pada45joist saja menghemat sekitarRp4,21juta. Campuran1,6 padajoist dan116penyangga tangga pendek memakai103stok, bukan101, dan berpotensi menghematRp7,55juta sebelum detail tambahan. Penyangga tangga itu masih usulan; pemeriksaan memakai lebar tributari1m dan titik1,334kN, bukan pengesahan bentuk sambungannya.')+
 p('Campuran joist2,0 justru sekitarRp0,53juta lebih mahal daripada seluruh2,3 pada pola ini: pemisahan tebal menambah stok dari101menjadi108. Ini menunjukkan kilogram bersih saja tidak cukup untuk memilih opsi ekonomis. Harga1,6 masih estimasi; perubahan harga atau pemakaian sisa dapat membalik urutan.')+
 p('Contoh peningkatan18stok kelompok tiang/pegangan keSHS60×60×2,3 menambah material+upah sekitarRp1,78juta, sebelum base/detail dan nesting ulang. Bila dibandingkan dengan acuan lama yang belum dikoreksi railing, potensi bersih campuran agresif turun menjadi sekitarRp5,77juta sebelum biaya lain. Penguatan yang diwajibkan keamanan bukan opsi yang boleh dihapus agar angka tampak murah.'))
 section('Kolom: merapatkan grid tidak sama dengan mengekang goyangan',table(['Tebal','Pu pada2.040','K1: kapasitas / interaksi','K2: kapasitas / interaksi'],[[fmt(r['thickness_mm'],1),fmt(r['columns_checks'][0]['Pu_kN'])+'kN',fmt(r['columns_checks'][0]['capacity_kN'])+'kN / '+fmt(r['columns_checks'][0]['interaction'],3),fmt(r['columns_checks'][1]['capacity_kN'])+'kN / '+fmt(r['columns_checks'][1]['interaction'],3)] for r in d['matrix'] if r['target_gap_mm'] is None])+
 p('Kolom terpanjang2.482mm, eksentrisitas gravitasi25mm arah lemah, amplifikasi elastis1/(1−Pu/Pe); interaksi mengikuti bentukH1 sebagai penyaringan. K1mensyaratkan pengekangan yang terbukti. K2adalah sensitivitas kantilever/goyang; nilai tidak stabil berarti Pu mencapai/melewati Euler pada model tersebut, bukan angka rasio yang boleh dibulatkan. KL/r≤200 dipakai sebagai target kelangsingan studi.')+
 p('Menambah kolom membagi beban vertikal tetapi tidak membuat rangka menjadi braced. Perlu pengaku diagonal dan collector yang menerus ke base. Bracing2,3 tetap dipertahankan pada calon campuran; kedua diagonal tidak otomatis dianggap sama-sama menahan tekan/tarik.'))
 section('Railing: komponen kritis yang terpisah dari kolom tribun',table(['Profil','Tebal','M perlu / kapasitas (kNm)','Lendutan','Status kantilever'],[[f"{r['b']}×{r['h']}",fmt(r['t'],1),fmt(r['Mu_kNm'],3)+' / '+fmt(r['capacity_kNm'],3),fmt(r['deflection_mm'])+'mm','Lolos kasus lokal' if r['passes_member_screen'] else 'Perlu revisi / di luar domain'] for r in d['guard'] if r['b']==40 or (r['b']==50 and r['t'] in [2.3,3.2]) or (r['b']==60 and r['t'] in [2.,2.3])])+
 p('Beban titik0,89kN pada1,1m memberi momen terfaktor1,566kNm. PadaSHS40×40×2,3, kapasitas elastis studi0,773kNm dan lendutan27mm; pada2,8mm masih23,34mm. Untuk jarak≤sekitar1.219mm, beban titik lebih besar daripada beban garis per tiang, sehingga perubahanjarak1.000→500tidak menurunkan kasus pengendali ini.')+
 p('CalonSHS60×60×2,3 memberikan rasio0,834 dan lendutan7,41mm pada jepit ideal. SHS50×50×3,2 hanya margin kecil, rasio0,957. Keduanya belum lolos base, las, angkur atau distribusi sistem rail. Alternatif bila ukuran40mm harus dipertahankan: return/backstay atau rangka yang terbukti mendistribusikan titik ke beberapa tiang; perlu analisis sambungan, tidak boleh mengasumsikan pembagian50:50.'))
 section('Dek, tangga, balok tepi dan ukuran luar lebih kecil',table(['SHS tapak40×40, bentang800mm','Rasio terbesar','Hasil lokal'],[[fmt(r['t'],1)+'mm',fmt(r['ratio'],3),'Lolos' if r['passes_member_screen'] else 'Perlu revisi'] for r in d['stair']])+
 p('Penyaringan pengaku tapak memakai pitch115mm, bentang800mm dan titik1,334kN seluruhnya pada satu batang. Ketebalan1,6 bisa dibahas untuk fungsi ini jika tumpuan dan sambungan terbukti; hasil tersebut tidak berlaku untuk tiang railing dengan profil yang sama.')+
 table(['Balok50×100','Lebar tributari','Rasio pada2.040mm'],[[fmt(r['t'],1)+'mm',fmt(r['tributary_m'],3)+'m',fmt(r['ratio'],3)] for r in d['edge_beams']])+
 p('Balok tepi ringan dan balok transfer harus diberi kode berbeda pada gamtek. Balok2,3 pun melewati penyaringan jika harus membawa lebar1m pada bentang2.040mm. Solusinya dapat berupa tumpuan yang benar, profil lebih tinggi, atau jalur beban lain; bukan sekadar menambah pelat sambungan.')+
 table(['Profil calon joist','Tebal','Rasio @2.040mm','Domain rumus'],[[f"{r['b']}×{r['h']}",fmt(r['t'],1),fmt(r['ratio'],3),'Kompak / bentang sesuai' if r['compact_domain'] else 'Perlu analisis tambahan'] for r in d['profiles']])+
 p('Ukuran40×80 mengurangi tinggi dan kekakuan; bandingkan hasilnya, jangan memilih dari luas penampang saja. Profil60×120/75×125 di tabel merupakan pembanding geometri, bukan konfirmasi stok/harga atau rekomendasi beli. Penampang tipis yang lebih lebar dapat menjadi nonkompak dan memerlukan penampang efektif.')+
 table(['Bordes4mm, strip1m','Rasio UDL','Lendutan UDL'],[[str(r['span_mm'])+'mm',fmt(r['ratio'],3),fmt(r['deflection_mm'],3)+'mm'] for r in d['deck']])+
 p('Mempertahankan pengaku @250mm penting. Merapatkan kolom arah panjang tidak menggantikan pengaku di arah pendek pelat. Strip pelat ini belum memeriksa titik, efek motif, las/sekrup, korosi, tepi bebas atau slip.'))
 section('Sambungan, bracing dan beton LT4',table(['Tebal dinding','Bearing/tearout satu baut contoh','Indeks plastifikasi muka vs2,3'],[[fmt(r['t'],1)+'mm',fmt(r['bearing_tearout_per_bolt_kN'])+'kN',fmt(r['relative_face_plastification'],3)] for r in d['connections']])+
 p('Contoh bautM12, lubang14, jarak tepi30, Fu370: φRn=min(0,75×1,2×Lc×t×Fu;0,75×2,4×d×t×Fu). Ini hanya bearing/tearout satu dinding, bukan kapasitas sambungan. Plastifikasi muka hollow pada geometri/gaya sama sering memiliki ketergantungan t²; dari2,3ke1,6 indeksnya0,484, sehingga pelat6mm yang tetap tebal tidak memulihkan dinding hollow secara otomatis.')+
 p('Gamtek harus menunjukkan jalur bearing, pengaku/doubler atau pelat tembus bila diperlukan, las efektif dan aksesnya, tepi/lubang, sleeve baut tembus, perlindungan korosi dan urutan kerja. Menggandakan kupingan tidak otomatis menggandakan kapasitas bila gaya tetap masuk ke muka hollow yang sama. Batas geometri rumus STI/AISC dan gaya chord harus diperiksa.')+
 table(['Bracing bay contoh1,77×2,5m; t2,3','Tarik diagonal terfaktor','Drift elongasi saja','Tarik pasangan angkur'],[[str(r['active_bays'])+'bay aktif',fmt(r['tension_kN'])+'kN',fmt(r['axial_drift_mm'])+'mm',fmt(r['anchor_couple_tension_kN'])+'kN'] for r in d['bracing'] if r['t']==2.3])+
 p('Tabel bracing membagi sway sejajar secara seragam kejumlah bay yang diasumsikan. Ini bukan pembuktian jumlah bay aktual bekerja. Drift total akan menambah deformasi kolom, collector, las, baut, base dan beton. Angkur menerima kombinasi geser/tarik; dead load penyeimbang belum dikreditkan dalam contoh pasangan angkur.')+
 p('Sebelum pelaksanaan: petakan balok dan pelat LT4, tebal slab, mutu beton, tulangan atas/bawah, jarak tepi dan daerah retak; lakukan pemindaian sebelum bor. Periksa breakout, pullout, pryout, geser–tarik, jarak/kelompok angkur serta lentur/punching beton. Slab tidak boleh dianggap setara fondasi tanah. Ukuran/kelas/panjang tanam angkur belum ditetapkan.'))
 section('Getaran dan sensitivitas',p('Frekuensi lokal joist1,6 pada bentang2.040mm sekitar9,83Hz dengan massaD+L. Nilai ini hanya mode satu batang pada tumpuan kaku; bukan frekuensi tribun. Kelenturan balok silang, kolom, sambungan, base dan lantai gedung menurunkan kekakuan sistem. Frekuensi saja juga tidak membuktikan kenyamanan: perlu respons percepatan, massa modal, damping, aktivitas penonton dan interaksi gedung.')+
 p('Uji final perlu pola beban sebagian/tidak simetris, beban ritmis penonton, tumpuan tidak kaku, ketebalan terukur dan imperfection. Bila kegiatan meliputi melompat/menari bersama, jangan mengubah asumsiD/L menjadi faktor dinamis sembarang; gunakan analisis dinamis yang sesuai. Profil ber-Fylebih tinggi tidak menaikkan modulusE, sehingga belum tentu menyelesaikan lendutan/getaran.'))
 section('Revisi gamtek yang diperlukan',table(['Dokumen','Revisi konkret','Status'],[
 ['S-01 rencana tumpuan','Kodekolom, grid lokal, jarakaktual, zona tangga, titik ke beton; jangan meratakan semua jarak jadi1.770','Studi grid tersedia'],
 ['S-02 denah balok/joist','Pisahkan balok tepi/transfer/silang; arah100mm tegak; pitch250; dukungan tiap joist, bentang bukan panjangpotong','Skema jalur beban tersedia'],
 ['S-03 railing','Pisahkan rail, tiang dan infill; tinggi efektif; return/backstay/profil60calon; base menahan momen','Perlu desain sambungan'],
 ['Detail sambungan','GayaN/V/M, tebal aktual, plate6mm, kupingan, las, sleeve, lubang dan urutan kerja','Tidak boleh copy detail2,3 ke1,6'],
 ['Detail base/angkur','Reaksi maksimum tiap base, beton/tulangan, embedment dan jarak tepi','Menunggu data beton'],
 ['BOQ/pola potong','Pisahkan profil/tebal; hitung ulangstok, sambungan, base, coating dan erection','Studi18opsi +3campuran tersedia'],
 ['Catatan desain','Standar/edisi, mutu bersertifikat, beban, domain/perhitungan, QA fabrikasi','Belum rilis konstruksi']])+
 '<div class="drawings">'+''.join(f'<a href="{name}" target="_blank"><img src="{name}" alt="{label}"></a>' for name,label in [('S01-grid.svg','Rencana grid dan konflik tangga'),('S02-loadpath.svg','Potongan jalur beban'),('S03-railing.svg','Kajian railing')])+'</div>')
 section('Rekomendasi tahap berikut yang spesifik',p('<strong>Prioritas1:</strong> tetapkan model jalur beban dan detail railing. Jangan memilih global1,6 hanya karena RAB paling kecil. <strong>Prioritas2:</strong> verifikasi calon campuranjoist1,6 +elemen utama2,3 pada geometri tetap; masukkan penyangga tangga1,6 hanya sesudah detailnya lolos. <strong>Prioritas3:</strong> optimalkan stok, rail dan sambungan; grid rapat hanya dipakai lokal jika analisis membutuhkannya dan tidak mengganggu tangga/beton.')+
 p('Keputusan aman final belum dapat ditetapkan dari data sekarang. Yang belum selesai adalah analisis3D/dinamis/gempa, sertifikat produk, sambungan dan beton LT4. Gambar S-01/S-02/S-03 adalah gambar studi untuk pembahasan insinyur struktur; bukan pengganti gamtek pelaksanaan atau persetujuan teknis penanggung jawab desain.'))
 section('Sumber primer dan data hitung','<ol>'+''.join(f'<li><a href="{html.escape(r["url"])}">{html.escape(r["name"])}</a></li>' for r in d['sources'])+'</ol>'+p('<a href="study.json" download>Datahitungan JSON</a> · <a href="perbandingan.csv" download>Tabel18opsi CSV</a> · <a href="../../tools.html#rab-11sep">Kembali keRAB editable</a>'))
 css='body{font:16px/1.65 Arial,sans-serif;color:#18313c;background:#edf1f3;margin:0}main{max-width:1200px;margin:auto;padding:32px}header,section{background:white;padding:28px;margin-bottom:18px;border-radius:8px}h1{font-size:34px;line-height:1.2}h2{line-height:1.3}a{color:#12698b}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #d8e0e4;padding:10px;text-align:left}th{background:#eaf0f2}tr:nth-child(even){background:#f8fafb}.tag{color:#a53020;font-weight:bold}.drawings img{width:100%;border:1px solid #ddd;margin:12px 0}button{padding:10px 18px}@media print{body{background:white}main{padding:0}section{break-inside:auto;border:0;padding:10px}h2{break-after:avoid}.scroll{overflow:visible}table{font-size:10px}button{display:none}.drawings img{break-inside:avoid}}'
 document='<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>METTA R06 — studi struktur dan biaya</title><style>'+css+'</style><main><header><p>SAP / METTA / 11 September2026</p><h1>Studi struktur, ketebalan dan efisiensi biaya</h1><p class="tag">R06 • BELUM UNTUK PELAKSANAAN</p><p>18kombinasi grid/tebal, 3opsi campuran, pemeriksaan komponen dan 3lembar skema gamtek.</p><button onclick="window.print()">Cetak / simpan PDF</button></header>'+''.join(parts)+'</main></html>'
 soup=BeautifulSoup(document,'html.parser')
 for node in list(soup.find_all(string=True)):
    if node.parent.name in ['style','script']:continue
    clean=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',str(node))
    node.replace_with(clean)
 (OUT/'analisis.html').write_text(str(soup),encoding='utf-8');print('R06 report and3SVG drawing sheets generated')
if __name__=='__main__':build()
