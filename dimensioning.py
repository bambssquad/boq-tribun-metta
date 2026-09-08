"""Shared, auditable R03 dimension annotations. Model geometry is not changed."""
import json, math
from pathlib import Path

ROOT=Path(__file__).parent
SOURCE='https://bimforum.org/resource/lod-level-of-development-lod-specification/'

def fmt(v):
    return str(int(round(v))) if abs(v-round(v))<.005 else f'{v:.2f}'.rstrip('0').rstrip('.')

def dimension(d,a,b,offset,height=80,label=None,basis='nominal koordinasi',value=None):
    first_line=len(d.lines)
    a=tuple(map(float,a));b=tuple(map(float,b));length=math.dist(a,b)
    assert length>0
    u=((b[0]-a[0])/length,(b[1]-a[1])/length);n=(-u[1],u[0])
    p=(a[0]+n[0]*offset,a[1]+n[1]*offset);q=(b[0]+n[0]*offset,b[1]+n[1]*offset)
    value=length if value is None else value
    label=fmt(value) if label is None else label
    d.line(p,q,'dim')
    for source,target in [(a,p),(b,q)]:
        d.line(source,(target[0]+n[0]*height*.3,target[1]+n[1]*height*.3),'dim')
        s=height*.3
        d.line((target[0]-s*(u[0]+n[0]),target[1]-s*(u[1]+n[1])),(target[0]+s*(u[0]+n[0]),target[1]+s*(u[1]+n[1])),'dim')
    # Vertical dimensions use horizontal text outside the extension line.
    if abs(u[1])>.9:x=p[0]+height*.6;y=(p[1]+q[1])/2
    else:x=(p[0]+q[0])/2-len(label)*height*.25;y=(p[1]+q[1])/2+height*.6
    d.text(x,y,label,height)
    d.dimensions.append(dict(a=a,b=b,offset=offset,height=height,label=label,value_mm=round(value,4),basis=basis,vector_lines=list(range(first_line,len(d.lines))),vector_label=len(d.labels)-1))

def horizontal(d,a,b,y,offset,height=80,**kw):dimension(d,(a,y),(b,y),offset,height,**kw)
def vertical(d,a,b,x,offset,height=80,**kw):dimension(d,(x,a),(x,b),offset,height,**kw)

def profile(d,x,y,h=12):
    d.rect(x,y,50,100);d.rect(x+2.3,y+2.3,45.4,95.4,'context')
    horizontal(d,x,x+50,y,-22,h)
    vertical(d,y,y+100,x+50,-22,h)
    d.text(x-15,y+125,'RHS 50 x 100 x 2,3',h)
    d.text(x-15,y-55,'t = 2,3 nominal',h)

def annotate(ds):
    for d in ds:
        d.before_dimensions=(len(d.lines),len(d.labels))
    for d in ds[:3]:
        horizontal(d,0,17700,0,-1250,130,label='17700 / sumbu nominal')
        vertical(d,0,5000,17700,-850,120)
        for k in range(10):horizontal(d,k*1770,(k+1)*1770,0,-650,100)
        for k in range(5):vertical(d,k*1000,(k+1)*1000,0,650,100)
        for k in range(11):
            x=k*1770;d.line((x,0),(x,5400),'grid');d.text(x-50,5580,str(k+1),120)
        for k in range(6):d.text(-1150,k*1000-50,chr(65+k),120)
        d.text(0,6000,'GRID NOMINAL 1-11 / A-F; TUMPUAN TAMBAHAN MENGIKUTI MODEL',125)
    ds[0].text(0,6400,'DEK 4 mm / ELEVASI TIER +500 / +1000 / +1500 / +2000 / +2500',125)
    ds[1].text(0,6400,'DUDUKAN 150 x 150; PLAT 8 + KARET 10; DASAR KOLOM +18',125)
    ds[2].text(0,6400,'RHS 50 x 100 x 2,3 / 8 X / NODE BAWAH +150 / TUMPUAN DEK: LIHAT S-06',125)
    d=ds[3]
    horizontal(d,0,17700,0,-700,120)
    for k in range(10):horizontal(d,k*1770,(k+1)*1770,0,-380,90)
    vertical(d,0,2500,17700,-750,120)
    for k in range(5):vertical(d,k*500,(k+1)*500,0,450,85)
    d.text(0,3200,'RHS 50 x 100 x 2,3 / DEK 4 / TINGGI NOMINAL DARI LT4 +0',120)
    for d in ds[4:6]:
        horizontal(d,0,5000,0,-650,90)
        for k in range(5):
            horizontal(d,k*1000,(k+1)*1000,0,-320,65)
            vertical(d,k*500,(k+1)*500,5000,-330,65)
        vertical(d,0,2500,5000,-850,85)
        d.text(0,3020,'RHS 50 x 100 x 2,3 / DEK 4 / DASAR KOLOM +18',80)
        d.text(0,2820,'NODE X +150 / ELEVASI TERHADAP LT4 +0',80)
    d=ds[5]
    d.rect(0,3450,1000,100,'detail')
    for k in range(5):d.line((k*250,3380),(k*250,3550),'detail')
    for k in range(4):horizontal(d,k*250,(k+1)*250,3550,190,55,basis='target studi; bukan jarak terverifikasi setiap elemen')
    d.text(1350,3500,'SKEMA TARGET PENYANGGA DEK 250 mm',65)
    d=ds[6]
    for k in range(5):horizontal(d,k*1000,(k+1)*1000,0,-350,60)
    vertical(d,0,2500,5000,-650,80)
    for k in range(5):vertical(d,k*500,(k+1)*500,5000,-200,60)
    d.text(0,2900,'5 MODUL x 1000 / 15 KENAIKAN x 166,67 (NOMINAL)',80)
    d=ds[7]
    for a,b in [(0,267),(267,534),(534,801),(801,1000)]:horizontal(d,a,b,0,-70,20,basis='modul tangga usulan')
    for k in range(3):vertical(d,k*500/3,(k+1)*500/3,1000,-100,20,basis='modul tangga usulan')
    vertical(d,0,500,1000,-290,25)
    d.text(0,740,'TAPAK 267 / LANDING 199 / DEK 4 mm',30)
    d.text(0,660,'Radius tekuk dan panjang bentangan: belum ditetapkan',22)
    d=ds[8]
    horizontal(d,0,1000,1140,190,42,basis='modul railing ilustrasi')
    horizontal(d,1000,2000,1140,190,42,basis='modul railing ilustrasi')
    vertical(d,0,1100,2040,-300,45,basis='tinggi railing skematis dari datum gambar')
    horizontal(d,180,280,140,250,28,label='100 bersih',basis='bukaan ilustrasi; pertemuan tiang perlu penyesuaian')
    d.text(0,1550,'RAILING SKEMATIS; PROFIL PADA MODEL DIPERTAHANKAN',42)
    d=ds[9]
    vertical(d,0,10,-75,55,6)
    vertical(d,10,18,-75,85,6)
    vertical(d,0,18,-75,120,7,label='18 total')
    horizontal(d,-25,25,198,45,8)
    d.rect(330,0,150,150,'baseplate');d.rect(380,25,50,100,'kolom')
    horizontal(d,330,480,0,-38,10);vertical(d,0,150,480,-35,10)
    d.text(330,180,'DENAH DUDUKAN',10)
    d.text(330,-85,'PLAT 150 x 150 x 8',9);d.text(330,-110,'KARET 150 x 150 x 10',9)
    d.text(-140,290,'RHS 50 x 100 x 2,3 / DIMENSI NOMINAL',12)
    d=ds[10]
    for i in range(4):
        x=(i%2)*1100+720;y=(i//2)*950+160
        profile(d,x,y,14)
    d.text(0,1900,'PENAMPANG RHS RUJUKAN; SKEMA D1-D4 TIDAK DIUKUR UNTUK PRODUKSI',42)
    d.text(0,-270,'Baut, angkur, gusset dan ukuran las: belum ditetapkan',38)
    d=ds[11]
    def iso(x,y,z):return (.866*(x-y),z-.5*(x+y))
    dimension(d,iso(0,5000,0),iso(17700,5000,0),-1400,190,label='17700 / X',value=17700,basis='sumbu 3D nominal, proyeksi isometrik')
    dimension(d,iso(0,0,0),iso(0,5000,0),-1800,160,label='5000 / Y',value=5000,basis='sumbu 3D nominal, proyeksi isometrik')
    dimension(d,iso(17700,0,0),iso(17700,0,2500),-1400,180,label='2500 / Z',value=2500,basis='sumbu 3D nominal, proyeksi isometrik')
    d.text(0,2000,'RHS 50 x 100 x 2,3 / DEK 4 / DUDUKAN 150 x 150 / 8 X',180)
    records=[dict(code=d.code,lod=200,dimensions=d.dimensions) for d in ds]
    (ROOT/'assets/technical/dimensions-R03.json').write_text(json.dumps(dict(revision='R03',units='mm',source=SOURCE,lod_scope='Geometri generik untuk koordinasi; detail tersedia dipertahankan, bukan penetapan LOD lebih tinggi.',sheets=records),ensure_ascii=False,indent=2),encoding='utf8')
    return ds
