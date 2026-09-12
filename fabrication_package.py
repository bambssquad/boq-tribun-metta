"""R07 review issue. No fabrication approval or new structural capacity is inferred."""
import csv,html,json,hashlib,zipfile,io
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape,A4
from reportlab.graphics.shapes import Drawing,Line,Rect,String,Circle
from reportlab.graphics import renderSVG
from r04_model import load_model

ROOT=Path(__file__).parent;OUT=ROOT/'assets/r07';DATE='12 September 2026'
STATUS='UNTUK PEMERIKSAAN INSINYUR - BELUM UNTUK DIPOTONG / DIFABRIKASI'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def fmt(x,n=2):return f'{x:,.{n}f}'.replace(',','_').replace('.',',').replace('_','.')
def ascii_text(x):return str(x).replace('×','x').replace('²','2').replace('³','3').replace('÷','/').replace('–','-').replace('—','-').replace('→','->').replace('φ','phi').replace('Δ','delta')
def csvwrite(name,headers,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)

SURVEY=[
('U01','Datum dan grid','Tetapkan titik nol lokal tribun terhadap grid gedung; foto titik referensi; ukur semua 80 lokasi dudukan.','Surveyor','F01 / panjang dan posisi kolom'),
('U02','Geometri jadi','Ukur batas tribun, elevasi tier, lebar/depth dudukan, dua area tangga, headroom dan jalur keluar.','Arsitek + surveyor','Bentuk/kapasitas/akses tetap; koreksi salah ukur dicatat'),
('U03','Struktur LT4','Gambar as-built pelat dan balok beton, tebal pelat, mutu beton, tulangan, bukaan dan beban yang sudah bekerja.','Pemilik + insinyur gedung','Reaksi tumpuan dan kapasitas lantai'),
('U04','Titik ikatan beton','Posisi 16 titik usulan, ukuran kolom beton, rebar scan, jarak tepi, kondisi retak, instalasi tertanam.','Surveyor + insinyur','Jenis/jumlah angkur; belum boleh mengebor'),
('U05','Baja pemasok','Sertifikat mutu/standar produk, ukur tebal aktual, dimensi luar, panjang stok dan timbang sampel per profil.','Pemasok + QC','Fy/Fu, tebal desain dan kg per batang'),
('U06','Pelat dan kayu','Pastikan stok tepat 1200x2400; tebal dasar bordes tanpa motif; mutu/kadar air kayu dan sistem antiselip.','Pemasok + QC','Kg pelat, bentang dek, pengikat kayu'),
('U07','Pemakaian','Konfirmasi kapasitas orang yang disetujui, jenis acara, kemungkinan lompat/ritmis, lokasi indoor/outdoor.','Pemilik + arsitek','Beban, getaran, pagar dan jalur evakuasi'),
('U08','Logistik','Ukur pintu/lift/koridor, kapasitas lift dan alat angkat, titik bongkar, batas beban tumpukan LT4.','Kontraktor + pengelola','Ukuran modul, berat angkat, urutan kirim'),
('U09','Sistem fabrikasi','Kemampuan las hollow tipis, prosedur las, welder, alat ukur, kapasitas tekuk dan radius aktual.','Fabrikator','Las, allowance tekuk dan uji rakit'),
('U10','Lingkungan dan finishing','Kondisi korosi, sistem cat yang disetujui, persiapan permukaan, ketebalan film dan waktu curing produk.','Pemilik + pemasok cat','Rencana QC finishing dan pemeliharaan')]

JOINTS=[
('J01','Kolom - base - lantai','80 dudukan; pelat nominal150x150x8 + karet10; konsep dudukan lepas.','N,V,M tiap tumpuan; lentur pelat, bearing beton, punching/shear lantai, geser/guling, karet.','U01,U03; tidak menganggap gesekan cukup atau reaksi terbagi rata'),
('J02','RHS - balok/kolom','RHS50x100x2.3; pelat6 dan bautM12 kelas8.8 masih allowance.','Gaya ujung, eksentrisitas, las, muka hollow, bolt shear/bearing, tearout, block shear, prying/slip.','Jangan mengebor/menetapkan las dari allowance; perlu detail akses las/baut'),
('J03','Bracing - buhul','20 diagonal native; buhul200x200x6 adalah usulan anggaran.','Tarik/tekan diagonal, panjang efektif, gaya pembalikan, tekuk buhul, las/baut, jalur gaya ke gedung.','Model lateral dan kombinasi gempa/sway; jangan anggap X otomatis efektif'),
('J04','Tangga - penyangga','116 penyanggaRHS + pengakuSHS143m masih usulan; pelattekuk3mm.','Jalur tumpuan tiap tapak, beban titik, lendutan/getaran, reaksi ke portal, sambungan tanpa benturan.','T-01 s.d.T-06 arsip untuk koordinasi; allowance tekuk final mengikuti alat'),
('J05','Tiang railing - rangka','40x40 acuan gagal screen kantilever;60x60x2.3 kandidat untuk diperiksa.','Gaya garis/titik, momen dasar, kekakuan base, deformasi mukaRHS, sistem rail horizontal dan isian.','Jangan pesan pengganti sebelum detailbase/ukuran ruang/bukaan disetujui'),
('J06','Strut - kolom beton','16 titik ikatan; cadanganRp5juta bukan16/32angkur terverifikasi.','Gaya grupangkur, jarak tepi, tanam, breakout/pullout/pryout, beton retak dan rebar.','U03,U04; produk angkur dan prosedur bor dipilih insinyur'),
('J07','Dek/kayu/penutup - rangka','Bordes4, pinus40, penutup2; pola sekrup masih usulan.','Bentang dan beban titik, tepi/sambungan dek, cabut/geser sekrup, ekspansi kayu, tepi tajam.','Tentukan apakah dek dihitung sebagai diafragma; jika tidak, sediakan jalur lateral lain')]

STAGES=[
('P01','Ukur dan cocokkan','U01-U10, daftar selisih model/lapangan','Pemilik + surveyor','Foto, sketsa, koordinat dan formulir terisi','Sebelum finalisasi detail'),
('P02','Pemeriksaan desain','Analisis rangka3D, lantai, railing, sambunganJ01-J07, gempa/getaran dan akses','Insinyur + arsitek','Hitungan dan daftar perubahan tertulis','Sebelum penetapan gambar fabrikasi'),
('P03','Terbitkan revisi kerja','Profil, tandaelemen, detail lubang/las, toleransi, daftar potong dan RAB sinkron','Detailer + insinyur','Revisi bertanggal dan disetujui; gambar lama ditarik','Sebelum pemesanan/pemotongan batch'),
('P04','Terima bahan','Cocokkan sertifikat, ketebalan, panjang, timbang dan kondisi bahan','QC + fabrikator','Log bahan dan identitas batch','Sebelum bahan digunakan'),
('P05','Contoh sambungan dan uji rakit','Satu modul representatif dengan tangga/railing kritis; prosedur las/tekuk disetujui','Fabrikator + QC + insinyur','Dimensi, fit-up dan hasil pemeriksaan diterima','Sebelum produksi berulang'),
('P06','Fabrikasi batch','Tandai, potong, deburr, bor/tekuk/las sesuai revisi; catat perubahan dan sisa','Fabrikator + QC','Traveler tiap modul, pemeriksaan las dan ukur','Tidak substitusi profil tanpa persetujuan desain'),
('P07','Finishing dan pengiriman','Siapkan permukaan, cat sesuai lembarproduk, curing, labelmodul dan perlindungan','QC + logistik','Log coating; daftar kemasan dan berat angkat','Rute dan batas bebanLT4 disetujui'),
('P08','Pemasangan','Pasang dari area tumpuan yang disetujui; stabilkan tiap modul sebelum melepas alat','Pelaksana + pengawas','Metode kerja, bracing sementara dan inspeksi tiap tahap','Urutan stabilitas dan alatangkat ditetapkan insinyur'),
('P09','Pemeriksaan akhir','Cek seluruh pengikat, las, kelurusan, railing, tangga, antiselip dan jalur keluar','QC + insinyur + pemilik','Daftar temuan ditutup; uji hanya dengan prosedur tertulis','Sebelum dibuka untuk pengguna'),
('P10','Serah terima dan perawatan','As-built, sertifikat, logQC, kapasitas penggunaan, panduan inspeksi/perbaikan','Kontraktor + pemilik','Berita acara dan dokumen diterima','Operasi setelah persetujuan akhir penanggung jawab')]

def diagrams(geom):
    navy=colors.HexColor('#153143');red=colors.HexColor('#b34327');gray=colors.HexColor('#bfd0d8')
    def new(title):
        d=Drawing(760,470);d.add(Rect(0,0,760,470,fillColor=colors.white,strokeColor=gray));d.add(String(20,443,title,fontSize=17,fillColor=navy));d.add(String(20,424,STATUS,fontSize=9,fillColor=red));return d
    def txt(d,x,y,s,size=10):d.add(String(x,y,ascii_text(s),fontSize=size,fillColor=navy))
    def ln(d,x,y,X,Y):d.add(Line(x,y,X,Y,strokeColor=navy,strokeWidth=1.4))
    d=new('F01 - Denah sumbu lokal dan identitas dudukan')
    cols=sorted(geom['columns'],key=lambda c:(c['y'],c['x']));k=.036;ox=52;oy=160
    for y in range(0,6000,1000):
        d.add(Line(ox,oy+y*k,ox+17700*k,oy+y*k,strokeColor=gray));txt(d,15,oy+y*k,str(y),8)
    for i,c in enumerate(cols,1):
        x=ox+c['x']*k;y=oy+c['y']*k;d.add(Circle(x,y,2.2,fillColor=navy));txt(d,x-7,y+(6 if i%2 else 15),f'C{i:02}',6)
    for i,x in enumerate(geom['core_axes_mm']):txt(d,ox+x*k-10,oy-(18 if i%2 else 30),str(x),7)
    txt(d,20,110,'80 dudukan; angka x/y dalam mm lokal. Koordinat lengkap dan ID Revit: register-kolom.csv.')
    txt(d,20,91,'Hubungan titik nol dengan grid gedung harus diukur (U01). Gambar ini bukan setting-out lapangan.')
    txt(d,20,72,'Posisi tangga, bentuk, kapasitas dan jalur keluar tetap. Kapasitas orang perlu dicatat pada U07.')
    txt(d,20,53,'Tidak menambah kolom pada area tangga. Jarak1770 bukan jarak seragam seluruh model.')
    yield 'F01-denah',d
    d=new('F02 - Sambungan utama untuk koordinasi detail')
    for x,y,title in [(20,205,'J01 / BASE'),(400,205,'J02 / RHS KE PORTAL')]:
        txt(d,x,y+188,title,12)
        d.add(Rect(x+100,y+75,45,90,fillColor=gray,strokeColor=navy));d.add(Rect(x+66,y+67,112,8,fillColor=navy))
        if x==20:
            d.add(Rect(x+62,y+57,120,8,fillColor=red));ln(d,x+20,y+55,x+280,y+55)
            txt(d,x,y+30,'Kolom50x100 / base150x150x8 / karet10',9)
            txt(d,x,y+13,'N,V,M dan kapasitas lantai: belum ditetapkan',9)
        else:
            d.add(Rect(x+145,y+105,115,40,fillColor=gray,strokeColor=navy));d.add(Rect(x+145,y+90,7,65,fillColor=red))
            txt(d,x,y+30,'Pelat6 / M12: usulan anggaran, bukan detailbor',9)
            txt(d,x,y+13,'Las, lubang, tepi, aksesbaut: tentukan dari gaya',9)
    txt(d,20,178,'J03 / BRACING KE BUHUL',12);ln(d,80,112,210,150);ln(d,80,112,210,72)
    d.add(Rect(70,99,24,24,fillColor=red));txt(d,250,138,'20 diagonal: gaya tarik/tekan dan tekuk buhul belum final.')
    txt(d,250,118,'Ukuran buhul200x200x6 di BOQ hanya cadangan geometris.')
    txt(d,20,48,'Skema tidak berskala. Dimensi nominal untuk identifikasi; jangan mengambil ukuran lubang/las dari gambar.')
    yield 'F02-sambungan',d
    d=new('F03 - Railing, tangga dan jalur tumpuan')
    txt(d,20,391,'J05 / RAILING',12);ln(d,95,205,95,353);ln(d,95,345,325,345);ln(d,95,287,325,287)
    d.add(Rect(70,195,50,10,fillColor=red));ln(d,35,194,345,194)
    txt(d,20,172,'h1100 pada studi; tinggi/pagar akhir mengikuti desainakses.',9)
    txt(d,20,151,'40x40: tidak lolos screen kantilever. Kandidat60x60x2.3.',9)
    txt(d,20,130,'Base harus memindahkan momen ke rangka, bukan penutup2mm.',9)
    txt(d,410,391,'J04 / TANGGA',12)
    for i in range(3):
        x=425+i*80;y=210+i*43;ln(d,x,y,x+80,y);ln(d,x+80,y,x+80,y+43)
        d.add(Rect(x+12,y-12,55,7,fillColor=red))
    txt(d,410,172,'Merah: penyangga perlu detail ke portal utama.',9)
    txt(d,410,151,'Pelat3mm dan56bidang: arsip; ukur ulang fit-up.',9)
    txt(d,410,130,'116RHS + pengakuSHS adalah usulan, belum rilis potong.',9)
    txt(d,20,70,'Beban pengguna -> tapak/dek -> balok/pengaku -> kolom -> lantai gedung.')
    txt(d,20,49,'Gaya lateral -> bracing/ikatan -> struktur gedung. Jalur ini harus diperiksa menyeluruh.')
    yield 'F03-railing-tangga',d

def build():
    OUT.mkdir(exist_ok=True);boq=read('assets/r05/boq.json');study=read('assets/r06/study.json');a=boq['quantity_audit'];m=load_model()
    assert a['steel_purchase_kg']==9570.466 and a['full_rhs']['stocks']==101
    sections=[]
    def section(title,paras,headers=(),rows=()):sections.append(dict(title=title,paragraphs=paras,headers=list(headers),rows=[list(r) for r in rows]))
    section('01 / Dasar paket dan keputusan',[
        'Pilihan Bam:1A/2A/3A. Bentuk, kapasitas dan posisi tangga model METTA tetap; profil dan sambungan boleh diperbaiki. Data lapangan belum lengkap. Insinyur struktur memeriksa sebelum fabrikasi.',
        'R07 adalah paket pemeriksaan menuju fabrikasi dan serah terima, bukan gambar yang telah disetujui untuk diproduksi. Jumlah pesanan final menunggu perubahan desain, pengukuran dan persetujuan tertulis.',
        'Model kuantitas: pembacaan545elemen pada11September2026;945parameter cocok. Geometri penutup/pelat tangga masih arsip. Koordinat gambar memakai sumbu lokal tribun, bukan datum setting-out gedung.',
        'Angka kapasitas orang tidak ditebak dari luas dek; pemilik/arsitek harus mencatat kapasitas yang disetujui tanpa menaikkannya.'])
    section('02 / Putusan54 atau101 batang',[
        '54batang adalah1620kgExcel/30kg perbatang, bukan daftar potong.54x6m hanya324m. ModelRHS saja memerlukan552,30m dan pola97batang; model+usulan590,14m memakai pola101batang.97dan101adalah pola layak, bukan minimum global terbukti.',
        'Gunakan101hanya sebagai acuan anggaran lingkup lengkap saat ini. Jangan memesan54untuk memenuhi model ini. Jangan memotong101sebelum revisi sambungan/tangga/railing dikunci.',
        'Berat katalogRHS50x100x2,3:32,5kg/6m.30kg dari Bam adalah pembagiExcel, bukan hasil timbang. Jika produk aktual berbeda, cocokkan sertifikat dan dimensi, lalu revisi berat dan analisis; jangan mengganti kg/batang saja tanpa pemeriksaan produk.'],
        ['Lingkup','Potongan','Panjang m','Batang6m','Kg pembelian'],[
        ['Excel / konversi','Tidak tersedia',324,54,1620],['ModelRHS',245,fmt(a['native_rhs']['length_m']),97,3152.5],['ModelRHS+usulan',361,fmt(a['full_rhs']['length_m']),101,3282.5]])
    checks=[]
    for r in study['matrix'][:3]:checks.append([r['key'],fmt(r['joist']['ratio'],3),fmt(r['bearer']['ratio'],3),'Lolos screen lokal' if r['gravity_screen'] else 'Tidak lolos screen lokal'])
    section('03 / Hitungan struktur dan keputusan profil',[
        'Acuan kerja pemeriksaan: RHS50x100x2,3 dipertahankan untuk rangka utama. Pilihan1,6seluruh rangka tidak diteruskan sebagai desain pelaksanaan karena balok silang tidak lolos screen.2,0memiliki margin lebih kecil; penghematan campuran tetap alternatif, bukan defaultfabrikasi.',
        'AsumsiR06: E200000MPa,Fy235MPa,Fu370MPa,D1,5kPa,L5kPa,faktor tebal0,93 sebagai sensitivitas. Beban dan faktor tebal harus dikonfirmasi terhadap kategori penggunaan serta standar produk nyata.',
        'Beam sederhana: Mu=quL^2/8; Vu=quL/2; delta=5qL^4/(384EI). Untuk titik: Mu=PL/4; delta=PL^3/(48EI). Rasio adalah maksimum pemeriksaan kapasitas/lendutan yang dihitung. Sambungan/tumpuan ideal pada screen belum membuktikan kekakuan nyata.',
        f"Luasdek{fmt(study['loads']['area_m2'])}m2; D{fmt(study['loads']['dead_kN'])}kN; L{fmt(study['loads']['live_kN'])}kN; kombinasi1,2D+1,6L={fmt(study['loads']['ultimate_kN'])}kN untuk asumsi ini. Reaksi tidak boleh dibagi rata ke80dudukan.",
        'Masih wajib diselesaikan: rangka3D/stabilitas/P-delta, gaya bracing dan diafragma, gempaLT4, lantai/angkur beton, getaran global/ritmis, jalur beban tangga dan pagar. R06 memuat hitungan lokal untuk bahan review; bukan sertifikat kepatuhan menyeluruh.'],
        ['Versi','Rasio pengaku','Rasio balok silang','Hasil terbatas'],checks)
    guards=[r for r in study['guard'] if (r['b'],r['t']) in [(40,2.3),(40,2.8),(60,2.3)]]
    section('04 / Revisi kritis sebelum fabrikasi',[
        'Tiangrailing40x40tidak lolos screen kantilever1,1m, bahkan2,8mm.60x60x2,3 adalah kandidat lokal untuk dikaji, belum pengganti yang disetujui. Base, isian, railhorizontal, celah dan akses harus diperiksa bersama.',
        'Jarak kolom tidak otomatis diubah1770menjadi1000. Model memiliki jarak bervariasi sampai2040pada sumbu inti; infill dapat bertabrakan dengan tangga dan menambah tumpuan pada lantai. Bentuk/kapasitas tetap, revisi hanya setelah analisis dan cek lapangan.',
        'Setiap perubahan profil/sambungan mengubah daftar bahan, panjang potong, kg dan harga. Paket ini mempertahankan BOQ acuan agar delta perubahan dapat ditelusuri, bukan menganggap semua item sudah cocok untuk fabrikasi.'],
        ['Tiang','Tebal mm','Rasio lentur','Lendutan mm','Hasil lokal'],[[f"{r['b']}x{r['h']}",r['t'],fmt(r['ratio'],3),fmt(r['deflection_mm']),'Kandidat diperiksa' if r['passes_member_screen'] else 'Tidak lolos'] for r in guards])
    section('05 / Daftar data lapangan',[
        'Isi formulir CSV atau kolom catatan di halamanweb. Lampirkan foto/sketsa dan identitas pengukur. Kolom kosong berarti belum ada bukti; mengisi formulir tidak menerbitkan persetujuan fabrikasi.'],
        ['Kode','Data','Cara/isi minimum','Penanggung jawab','Dampak'],SURVEY)
    section('06 / Register detail sambungan',[
        'F01-F03 adalah gambar koordinasi revisiR07. Detail kerja final harus menambahkan gaya desain, potongan, dimensi lubang/tepi, ukuran dan panjang las, gradebaut, metodekencang, toleransi, akses alat serta nomor revisi.',
        'Tidak menetapkan ukuran las, torsi, panjang tanam angkur atau kapasitas lantai dari allowance harga. Insinyur/fabrikator menetapkannya dari desain dan data produk.'],
        ['Kode','Sambungan','Acuan saat ini','Pemeriksaan yang harus selesai','Data/catatan'],JOINTS)
    totals=[r for r in boq['comparison'] if r['case']=='model' and r['basis']=='purchase']
    section('07 / Daftar bahan dan RAB sampai jadi',[
        'Daftar bahan/RAB disertakan perkomponen. AcuanRHS2,3;SHS2,0/2,8;stokpelat120x240cm. Kg baja9570,466 mencakup usulan dan allowance. Total ini tidak mencakup kepastian biaya revisirailing/angkur atau penguatan lantai yang belum didesain.',
        'Dua lingkup biaya ditampilkan untuk mencegah biaya pelengkap hilang. Semua nilai sebelum overhead,laba,pajak tambahan. Penawaran pemasok, transport/alatangkat aktual dan biaya pemeriksaan desain perlu dikonfirmasi; item yang belum berharga harus ditulis BELUM DIHARGAI, bukan dianggap nol.',
        'Daftar potong memisahkan245potonganRHSmodel dari116usulan. Angka mm adalah panjang model, belum termasuk keputusan sambungan final. CSV memiliki kolom persetujuan yang kosong; bukan fileCNC.'],
        ['Lingkup','Upah Rp','Material Rp','Total Rp'],[['Lengkap + pelengkap' if r['extras'] else 'BOQ dasar',fmt(r['labor'],0),fmt(r['material'],0),fmt(r['total'],0)] for r in totals])
    section('08 / Urutan pekerjaan dan titik pemeriksaan',[
        'Urutan berikut berbasis ketergantungan, bukan janji durasi. Durasi, jumlahpekerja, modul dan kapasitas alatangkat ditetapkan setelahU08dan gambar final. Modul panjang/berat tidak boleh diangkat atau ditumpuk diLT4tanpa rencana yang diperiksa.'],
        ['Tahap','Pekerjaan','Keluaran','PIC','Bukti diterima','Batas sebelum lanjut'],STAGES)
    section('09 / QC, serah terima dan penggunaan',[
        'Sebelum potong: cocokkan revisi, materialbatch, dimensi dan daftar potong. Saat fabrikasi: catat panjangakhir, orientasi, holepattern, prosedurlas, inspeksi dan perbaikan. Toleransi dan cakupanNDTditentukan dokumen desain/prosedur, bukan ditebak di lapangan.',
        'Saat pemasangan: periksa dudukan/karet, leveling, bracingsementara, pengikat dan jalur tumpuan. Jangan melepaskan penahan sementara sebelum modul stabil dan diterima pengawas. Catat pemeriksaan baut sesuai jenis sambungan/metode pemasangan yang disetujui.',
        'Sebelum serah terima: tutup temuan railing/tangga/antiselip/tepi tajam/akses, lengkapi as-built, daftar bahan aktual, logcat/las/baut, sertifikat, kapasitas penggunaan dan panduan perawatan. Uji pembebanan hanya jika ada prosedur tertulis dari insinyur; jangan memakai kerumunan sebagai uji.',
        'Pemilik menetapkan penanggung jawab inspeksi berkala sesuai petunjukinsinyur/pemasok. Periksa kelonggaran, korosi, deformasi, retaklas, antiselip dan kerusakan kayu; hentikan penggunaan area bermasalah sampai diperiksa.',
        'Pengesahan final harus memuat nama pemeriksa, revisigambar/hitungan, tanggal dan batas penggunaan. StatusR07tetap UNTUK PEMERIKSAAN; formulir catatan tidak menggantikan pengesahan.'])
    section('10 / Rujukan dan keterbatasan',[
        'Status katalogBSNdiperiksa12September2026: SNI1727:2020(beban),SNI1729:2020(baja;adopsiAISC360-16),SNI7971:2013(baja canaidingin). Halaman katalog memastikan identitas/status, bukan akses seluruh pasal. Pilihan jalurdesain mengikuti standar produk aktual dan penanggung jawab desain.',
        'GempaSNI1726dan beton/angkurSNI2847harus dipakai sesuai edisi yang berlaku untuk proyek oleh insinyur. Data situs,kelas tanah,responsgedungLT4,beton dan detailangkur belum tersedia.',
        'R06 tetap sumber hitungan lokal. Pembacaan ulang kuantitas11September tidak merupakan surveilapangan atau pemeriksaan mutu. Kg katalog/teoritis tidak sama dengan hasil timbang.'],
        ['Rujukan','Tautan'],[[r['name'],r['url']] for r in study['sources'][:3]])
    # Make compact Indonesian source prose readable without changing numbers.
    import re
    def spaced(s):
        if str(s).startswith('https://'):return str(s)
        return re.sub(r'(?<=[a-zA-Z])(?=\d)|(?<=\d)(?=[a-zA-Z])|(?<=[a-z])(?=[A-Z])',' ',ascii_text(s))
    for sec in sections:
        sec['title']=spaced(sec['title'])
        sec['paragraphs']=[spaced(p) for p in sec['paragraphs']]
        sec['rows']=[[spaced(v) for v in r] for r in sec['rows']]
    cols=sorted(study['geometry']['columns'],key=lambda c:(c['y'],c['x']))
    csvwrite('register-kolom.csv',['mark','revit_id','x_lokal_mm','y_lokal_mm','tinggi_arsip_mm','status'],[[f'C{i:02}',c['id'],c['x'],c['y'],c['height'],STATUS] for i,c in enumerate(cols,1)])
    native={str(e['id']) for e in m['rhs']+m['columns']};cuts=[]
    for n,b in enumerate(boq['study']['procurement']['baseline_cuts'],1):
        for ident,L in b['cuts']:cuts.append([n,ident,L,'Model' if str(ident) in native else 'Usulan belum dimodelkan','RHS50x100x2.3','',STATUS])
    csvwrite('daftar-potong-review.csv',['stok_acuan','id_potongan','panjang_model_mm','asal','profil_acuan','panjang_final_disetujui_mm','status'],cuts)
    csvwrite('form-ukur-lapangan.csv',['kode','data','isi_minimum','PIC','dampak','hasil_ukur','tanggal','bukti_foto_gambar','pemeriksa'],[list(r)+['','','',''] for r in SURVEY])
    csvwrite('register-sambungan.csv',['kode','sambungan','acuan','cek','data','gaya_desain','detail_revisi','pemeriksa','status'],[list(r)+['','','','BELUM FINAL'] for r in JOINTS])
    csvwrite('tahapan-dan-QC.csv',['tahap','pekerjaan','keluaran','PIC','bukti','batas','tanggal_rencana','tanggal_aktual','catatan'],[list(r)+['','',''] for r in STAGES])
    budget=[]
    for r in boq['rows']:
        q=r['purchase_qty'];labor=round(q*r['labor_rate']);material=round(q*r['material_rate'])
        budget.append([r['id'],r['name'],r['material'],q,r['unit'],r['labor_rate'],r['material_rate'],labor,material,labor+material,'Pelengkap' if r['extra'] else 'Dasar',r['verification']])
    csvwrite('RAB-review.csv',['id','pekerjaan','material','volume_beli','satuan','upah_per_satuan','material_per_satuan','jumlah_upah','jumlah_material','total','kelompok','status_verifikasi'],budget)
    issue=dict(revision='R07',date=DATE,status=STATUS,choices=['1A','2A','3A'],fabrication_released=False,sections=sections,
        baseline_steel_kg=9570.466,rhs_bars=101,native_rhs_bars=97,cut_count=len(cuts),survey_count=len(SURVEY),joints_count=len(JOINTS),stages_count=len(STAGES),sources=study['sources'][:3])
    (OUT/'paket.json').write_text(json.dumps(issue,ensure_ascii=False,indent=2),encoding='utf-8')
    draw=list(diagrams(study['geometry']))
    for name,d in draw:(OUT/(name+'.svg')).write_text(renderSVG.drawToString(d),encoding='utf-8')
    make_pdf(sections,draw)
    make_html(sections,draw)
    return issue

def make_pdf(sections,draw):
    styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=13
    styles['Heading1'].fontSize=18;styles['Heading1'].spaceAfter=12
    small=styles['BodyText'].clone('small');small.fontSize=7.5;small.leading=10
    story=[]
    for sec in sections:
        if story:story.append(PageBreak())
        story.append(Paragraph(html.escape(sec['title']),styles['Heading1']))
        for p in sec['paragraphs']:story.extend([Paragraph(html.escape(p),styles['BodyText']),Spacer(1,9)])
        if sec['headers']:
            data=[[Paragraph(html.escape(str(c)),small) for c in row] for row in [sec['headers']]+sec['rows']]
            n=len(sec['headers']);widths=[742/n]*n
            if n==5:widths=[40,95,220,115,272]
            if n==6:widths=[40,90,180,110,170,152]
            if n==2:widths=[240,502]
            t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dfe9ee')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#b9c7cd')),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]));story.append(t)
    for name,d in draw:story.append(PageBreak());story.append(d)
    def footer(c,doc):
        c.saveState();c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#b34327'));c.drawString(40,20,'METTA R07 / '+STATUS);c.setFillColor(colors.black);c.drawRightString(800,20,str(doc.page));c.restoreState()
    doc=SimpleDocTemplate(str(OUT/'METTA-R07-paket-pemeriksaan.pdf'),pagesize=landscape(A4),leftMargin=40,rightMargin=40,topMargin=35,bottomMargin=35,title='METTA R07 - Paket pemeriksaan menuju fabrikasi',author='METTA / prepared for engineering review',invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

def make_html(sections,draw):
    esc=html.escape
    parts=['<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>METTA R07 / Paket pemeriksaan fabrikasi</title><style>body{font:16px/1.65 system-ui,sans-serif;color:#173343;background:#f4f6f6;margin:0}main{max-width:1120px;margin:auto;padding:35px 24px}h1{font-size:38px;line-height:1.2}h2{margin-top:45px}a{color:#06617d}table{border-collapse:collapse;width:100%;font-size:13px;background:white}td,th{padding:10px;border:1px solid #cad5da;vertical-align:top;text-align:left}th{background:#e0e9ed}.scroll{overflow:auto}.status{background:#fff0de;padding:15px;border-left:5px solid #b34327}.downloads{display:flex;flex-wrap:wrap;gap:12px}img{width:100%;background:white;margin:15px 0}textarea{width:95%;min-height:60px}button{padding:10px;cursor:pointer}nav{display:flex;gap:15px;flex-wrap:wrap}@media print{body{background:white}nav,.notes,button{display:none}main{padding:0}.scroll{overflow:visible}h2{break-before:page}tr{break-inside:avoid}}</style><main>',
        '<nav><a href="../../tools.html#rab-11sep">Kembali ke RAB</a><a href="../r06/analisis.html">Hitungan R06</a></nav><p>12 SEPTEMBER 2026 / R07</p><h1>Dari pemeriksaan desain<br>ke fabrikasi dan serah terima.</h1><p class="status"><b>'+STATUS+'</b><br>Pilihan Bam 1A / 2A / 3A. Pengisian catatan tidak menerbitkan persetujuan kerja.</p><div class="downloads">']
    files=[('METTA-R07-RAB-lengkap.pdf','PDF RAB lengkap'),('METTA-R07-paket-pemeriksaan.pdf','PDF paket pemeriksaan'),('daftar-potong-review.csv','Daftar potong review'),('RAB-review.csv','RAB lengkap'),('form-ukur-lapangan.csv','Form ukur'),('register-sambungan.csv','Register sambungan'),('tahapan-dan-QC.csv','Tahapan dan QC'),('register-kolom.csv','Koordinat kolom')]
    parts.extend(f'<a href="{p}" download>{t}</a>' for p,t in files);parts.append('</div>')
    for sec in sections:
        parts.append('<section><h2>'+esc(sec['title'])+'</h2>');parts.extend('<p>'+esc(p)+'</p>' for p in sec['paragraphs'])
        if sec['headers']:
            parts.append('<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(str(c))+'</th>' for c in sec['headers'])+'</tr></thead><tbody>')
            for row in sec['rows']:parts.append('<tr>'+''.join('<td>'+esc(str(c))+'</td>' for c in row)+'</tr>')
            parts.append('</tbody></table></div>')
        parts.append('</section>')
    parts.append('<h2>Gambar koordinasi R07</h2>')
    for name,d in draw:parts.append(f'<a href="{name}.svg" download>Unduh {name}</a><img src="{name}.svg" alt="{name}: gambar koordinasi untuk pemeriksaan">')
    parts.append('<section class="notes"><h2>Catatan data lapangan</h2><p>Tersimpan di perangkat ini; unduh catatan untuk dikirim kepada pemeriksa. Tidak ada perubahan status persetujuan.</p>')
    for code,title,*rest in SURVEY:parts.append(f'<label for="{code}">{code} / {title}</label><textarea id="{code}" data-note="{code}" placeholder="Hasil ukur, tanggal, nama pengukur dan referensi bukti"></textarea>')
    parts.append('<button id="save-notes">Unduh catatan JSON</button><p id="note-status" role="status"></p></section><script>const key="metta-r07-survey-notes";let notes={};try{notes=JSON.parse(localStorage.getItem(key))||{}}catch{}document.querySelectorAll("[data-note]").forEach(el=>{el.value=typeof notes[el.id]==="string"?notes[el.id]:"";el.addEventListener("input",()=>{notes[el.id]=el.value;try{localStorage.setItem(key,JSON.stringify(notes));document.getElementById("note-status").textContent="Catatan tersimpan; status tetap untuk pemeriksaan."}catch{document.getElementById("note-status").textContent="Penyimpanan gagal; unduh catatan JSON."}})});document.getElementById("save-notes").onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({revision:"R07",fabrication_released:false,notes},null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="METTA-R07-catatan-ukur.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};</script></main></html>')
    (OUT/'index.html').write_text(''.join(parts),encoding='utf-8')

if __name__=='__main__':
    d=build();print(f"R07: {d['cut_count']} cuts, {d['survey_count']} survey items, {d['joints_count']} joints, {d['stages_count']} stages; review only.")
