"""R06 option screening, not a certified whole-structure design.

N, mm, MPa internally. All assumptions and unverified conditions are exported.
No Revit mutation and no silent replacement of the live RAB quantities.
"""
import math,json,csv
from functools import lru_cache
from pathlib import Path
from collections import defaultdict
import numpy as np
from study_r05 import rhs,compression
from r04_model import load_model
from revision04 import pack_bars
ROOT=Path(__file__).parent
OUT=ROOT/'assets/r06'
PARAMS=dict(E=200000.,fy=235.,fu=370.,density=7850.,dead_kPa=1.5,live_kPa=5.,
    thickness_factor=.93,joist_pitch_mm=250.,bearer_span_mm=1060.,column_height_mm=2482.,
    guard_height_mm=1100.,guard_line_kNm=.73,guard_point_kN=.89,
    step_point_kN=1.334,dead_deflection_divisor=360,guard_deflection_limit_mm=11.,
    new_base_allowance_low=250000,new_base_allowance_high=500000,new_bearer_connection_allowance=100000)
SOURCES=[
 ('SNI 1727:2020 — beban; status berlaku','https://pesta.bsn.go.id/produk/detail/12927-sni17272020'),
 ('SNI 1729:2020 — baja; adopsi AISC 360-16','https://pesta.bsn.go.id/produk/detail/12882-sni17292020'),
 ('SNI 7971:2013 — rute desain baja canai dingin bila produknya relevan','https://pesta.bsn.go.id/produk/detail/9714-sni79712013'),
 ('SNI 1726:2019 — gempa; BSN','https://pesta.bsn.go.id/produk/by_ics/626'),
 ('BSN — SNI 2847:2019 dan 1726:2019','https://infopublik.id/kategori/nasional-sosial-budaya/701313/index.html'),
 ('ICC 300-2017 §303 — pembanding khusus tribun, bukan pengganti SNI','https://codes.iccsafe.org/content/ICC3002017/chapter-3-construction?site_type=public'),
 ('AISC — F7 dan contoh penampang efektif','https://www.aisc.org/globalassets/aisc/manual/v15.1-companion/v15.1_vol-1_design-examples.pdf'),
 ('STI — batas kelangsingan lentur HSS','https://steeltubeinstitute.org/resources/width-thickness-requirements-square-rectangular-hss-subject-flexure/'),
 ('STI — elemen langsing pada kolom HSS','https://steeltubeinstitute.org/resources/effects-of-slender-elements-in-hss-compression-members/'),
 ('AISC — faktor tebal menurut standar produk','https://www.aisc.org/aisc/solutions-center/hss/'),
 ('STI — sambungan pelat melintang ke hollow','https://steeltubeinstitute.org/resources/transverse-plate-to-squarerectangular-hss-connections/'),
 ('STI — batas penerapan rumus sambungan','https://steeltubeinstitute.org/resources/hss-limits-of-applicability/'),
 ('AISC — bearing dan tearout lubang baut','https://www.aisc.org/globalassets/modern-steel/archives/2017/05/ataleoftearouts.pdf'),
 ('AISC — getaran lantai dan aktivitas ritmis','https://www.aisc.org/globalassets/aisc/publications/facts-for-steel-buildings-5-vibrations.pdf'),
 ('SMS Perkasa — katalog 27 Agustus, diperiksa 11 September 2026','https://www.smsperkasa.com/produk/besi-hollow-hitam')]

@lru_cache(None)
def section(b,h,t):
    p=rhs(t,b,h);p['Sy']=p['Iy']/(b/2)
    return p

def flexure(b,h,t,span):
    p=section(b,h,t);E=PARAMS['E'];fy=PARAMS['fy'];root=math.sqrt(E/fy)
    lf=(b-3*t)/t;lw=(h-3*t)/t
    # Use elastic first yield only in the compact domain. Refuse to silently
    # claim capacity for noncompact/slender flexural elements or long LTB spans.
    J=4*((b-t)*(h-t))**2/(2*((b-t)+(h-t))/t)
    Lp=.13*E*p['ry']*math.sqrt(J*p['A'])/(fy*p['Z'])
    domain=lf<=1.12*root and lw<=2.42*root and span<=Lp
    hw=h-3*t;cv=min(1.,1.1*math.sqrt(5*E/fy)/(hw/t))
    if hw/t>1.37*math.sqrt(5*E/fy):cv=1.51*5*E/(fy*(hw/t)**2)
    return dict(phiM=.9*fy*p['S'],phiV=.9*.6*fy*(2*hw*t)*cv,
                compact=lf<=1.12*root and lw<=2.42*root,Lp=Lp,domain=domain)

def beam_check(b,h,tn,L,trib,point=0.,dead=1.5,live=5.):
    t=tn*PARAMS['thickness_factor'];p=section(b,h,t);cap=flexure(b,h,t,L)
    qd=dead*trib;ql=live*trib;P=point*1000
    Mu=max((1.2*qd+1.6*ql)*L**2/8,1.2*qd*L**2/8+1.6*P*L/4)
    Vu=max((1.2*qd+1.6*ql)*L/2,1.2*qd*L/2+1.6*P/2)
    delta=max(5*(qd+ql)*L**4/(384*PARAMS['E']*p['Ix']),5*qd*L**4/(384*PARAMS['E']*p['Ix'])+P*L**3/(48*PARAMS['E']*p['Ix']))
    # Occupied line mass; local beam mode only, not the assembled stand mode.
    mass=((dead+live)*1000/9.81*trib)+p['kg_m']
    freq=math.pi/(2*(L/1000)**2)*math.sqrt(PARAMS['E']*1e6*p['Ix']*1e-12/mass)
    ratios=[Mu/cap['phiM'],Vu/cap['phiV'],delta/(L/360)]
    return dict(b=b,h=h,t=tn,span_mm=L,tributary_m=trib,Mu_kNm=Mu/1e6,
       capacity_kNm=cap['phiM']/1e6,bending_ratio=ratios[0],shear_ratio=ratios[1],
       deflection_mm=delta,deflection_limit_mm=L/360,deflection_ratio=ratios[2],
       local_frequency_Hz=freq,compact_domain=cap['domain'],ratio=max(ratios),
       passes_member_screen=bool(cap['domain'] and max(ratios)<=1.))

def guard_check(b,h,tn,spacing=1000,height=1100):
    t=tn*.93;p=section(b,h,t);cap=flexure(b,h,t,height)
    force=max(.73*spacing/1000,.89)*1000
    moment=1.6*force*height;delta=force*height**3/(3*PARAMS['E']*p['Ix'])
    return dict(b=b,h=h,t=tn,spacing_mm=spacing,height_mm=height,Mu_kNm=moment/1e6,
       capacity_kNm=cap['phiM']/1e6,ratio=moment/cap['phiM'],deflection_mm=delta,
       passes_member_screen=bool(cap['domain'] and moment<=cap['phiM'] and delta<=11.),
       note='Cantilever tunggal dengan jepit sempurna, beban garis/titik alternatif, limit lendutan 11mm target proyek. Kekakuan base belum dihitung.')

def geometry():
    m=load_model();columns=[]
    for e in m['items']:
        if e['group']!='kolom':continue
        v=np.array(e['vertices']);lo=v.min(0);hi=v.max(0)
        columns.append(dict(id=e['id'],x=round(float((lo[0]+hi[0])/2)),y=round(float((lo[1]+hi[1])/2)),height=float(hi[2]-lo[2])))
    core=sorted(c['x'] for c in columns if c['y']==0)
    assert len(core)==13 and len(columns)==80
    return m,columns,core

def build():
    OUT.mkdir(exist_ok=True);m,columns,core=geometry()
    boq=json.loads((ROOT/'assets/r05/boq.json').read_text(encoding='utf-8'))
    cuts=[(str(label),float(L)) for s in boq['study']['procurement']['baseline_cuts'] for label,L in s['cuts']]
    variants=boq['study']['procurement']['variants'];rows={r['id']:r for r in boq['rows']}
    baseline_total=next(c['total'] for c in boq['comparison'] if c['case']=='model' and c['basis']=='purchase' and not c['extras'])
    matrix=[]
    stairs=[e for e in json.loads((ROOT/'data/finishes-geometry.json').read_text(encoding='utf-8'))['items'] if e['group']=='tangga']
    for gap in [None,1770,1500,1250,1000,885]:
        added=[]
        if gap:
            for a,b in zip(core,core[1:]):
                n=math.ceil((b-a)/gap)
                added.extend(a+(b-a)*i/n for i in range(1,n))
        axes=sorted(core+added);maxgap=max(b-a for a,b in zip(axes,axes[1:]))
        extra=[];conflicts=[]
        for n,x in enumerate(added):
            for y in range(0,6000,1000):
                height=float(np.mean([c['height'] for c in columns if c['y']==y]))
                extra.append((f'ADD-C-{n}-{y}',height))
                for stair in stairs:
                    points=np.array(stair['vertices']);lo=points.min(0);hi=points.max(0)
                    if lo[0]-25<x<hi[0]+25 and lo[1]-50<y<hi[1]+50 and height+18>lo[2]:
                        conflicts.append(dict(x=round(x,2),y=y,stair_id=stair['id']))
            for tier in range(5):extra.append((f'ADD-B-{n}-{tier}',1060.))
        packed=pack_bars(cuts+extra)
        assert all(b['used']<=6000+1e-7 for b in packed)
        for version in ['model','h20','h16']:
            v=variants[version];t=v['thickness_mm']
            joist=beam_check(50,100,t,maxgap,.25,1.334)
            bearer=beam_check(50,100,t,1060,maxgap/1000)
            # Maximum tributary width is taken conservatively as max gap,
            # depth=1m. Includes 25mm gravity eccentricity and B1 magnification.
            Pu=9.8*maxgap/1000
            column=[]
            for K in [1.,2.]:
                c=compression(2482,t*.93,K);p=section(50,100,t*.93)
                Pe=math.pi**2*PARAMS['E']*p['Iy']/(K*2482)**2/1000
                B1=1/(1-Pu/Pe) if Pu<Pe else math.inf
                mr=Pu*25*1000*B1/(.9*235*p['Sy'])
                pr=Pu/c['phiPn_kN'];interaction=pr+8/9*mr if pr>=.2 else pr/2+mr
                column.append(dict(K=K,Pu_kN=Pu,capacity_kN=c['phiPn_kN'],KLr=c['KLr'],Pe_kN=Pe,
                    amplification=B1,interaction=interaction,passes_screen=bool(interaction<=1 and c['KLr']<=200)))
            purchase_kg=len(packed)*v['stock_kg'];rhs_labor=purchase_kg*6000
            # Comparison only: keep other original quantities and separate new
            # support allowances instead of calling an unpriced redesign cheap.
            old_rhs=sum(round(r['purchase_qty']*r['labor_rate'])+round(r['purchase_qty']*r['material_rate']) for r in boq['rows'][:8])
            original_case=next(c['total'] for c in boq['comparison'] if c['case']==version and c['basis']=='purchase' and not c['extras'])
            estimate=original_case+(len(packed)-101)*(v['stock_price']+v['stock_kg']*6000)
            newcols=6*len(added);newbearers=5*len(added)
            low=estimate+newcols*250000+newbearers*100000
            high=estimate+newcols*500000+newbearers*100000
            matrix.append(dict(key=f'{version}-{gap or "existing"}',thickness_mm=t,target_gap_mm=gap,
                max_gap_mm=maxgap,new_axes=added,axes=axes,columns=80+newcols,added_columns=newcols,
                bearers=65+newbearers,added_bearers=newbearers,stocks=len(packed),purchase_kg=purchase_kg,
                cut_count=len(cuts+extra),added_cut_length_m=sum(L for _,L in extra)/1000,
                stair_conflicts=conflicts,layout_status='KONFLIK POTENSIAL TANGGA; BUKAN GRID SIAP PAKAI' if conflicts else 'Belum verifikasi beton/akses/MEP',
                joist=joist,bearer=bearer,columns_checks=column,
                cost_low=round(low),cost_high=round(high),delta_low=round(low-baseline_total),delta_high=round(high-baseline_total),
                price_status='Estimasi RAB, SHS acuan tetap. Tambahan base/angkur dan sambungan allowance, belum penawaran. Bracing baru, tulangan beton, relokasi jalur dan redesain belum terukur.',
                gravity_screen=bool(joist['passes_member_screen'] and bearer['passes_member_screen'] and column[0]['passes_screen']),
                compliance='BELUM DAPAT DITETAPKAN'))
    profiles=[]
    for b,h in [(40,80),(50,100),(60,120),(75,125)]:
        for t in [1.6,2.,2.3]:profiles.append(beam_check(b,h,t,2040,.25,1.334))
    guard=[guard_check(b,h,t) for b,h in [(40,40),(50,50),(60,60)] for t in [1.6,1.7,2.,2.3,2.8,3.2]]
    stair=[beam_check(40,40,t,800,.115,1.334) for t in [1.6,1.7,2.,2.3]]
    # Main beam load-path envelopes. Neither the edge tributary width nor the
    # transfer-beam condition may be assumed without proving the actual joint.
    edge=[beam_check(50,100,t,2040,w) for t in [1.6,2.,2.3] for w in [.125,.5,1.]]
    connections=[]
    for t in [1.6,1.7,2.,2.3,2.8,6.]:
        td=t*.93 if t<6 else t
        connections.append(dict(t=t,bearing_tearout_per_bolt_kN=.75*min(1.2*23*td*370,2.4*12*td*370)/1000,
            relative_face_plastification=(t/2.3)**2,
            note='Ilustrasi d12, lubang14, tepi30, Fu370; satu dinding, bukan kapasitas sambungan lengkap. Lubang, jarak, blok geser, las, prying dan deformasi muka belum diperiksa.'))
    # Load and reaction envelope; ICC supplementary sway is not seismic design.
    width=17.7;tiers=5;sway_parallel=.350*width*tiers;sway_perpendicular=.146*width*tiers
    load=dict(area_m2=boq['facts']['deck_area_m2'],dead_kN=1.5*boq['facts']['deck_area_m2'],
        live_kN=5*boq['facts']['deck_area_m2'],ultimate_kN=9.8*boq['facts']['deck_area_m2'],
        sway_parallel_kN=sway_parallel,sway_perpendicular_kN=sway_perpendicular,
        sway_moment_parallel_kNm=sway_parallel*1.5,sway_moment_perpendicular_kNm=sway_perpendicular*1.5,
        note='Sway tiap baris pada z0.5/1/1.5/2/2.5m; angka pembanding dibulatkan 0.350/0.146kN/m. Gempa LT4 memerlukan respons gedung; reaksi tidak boleh dibagi rata ke80base.')
    deck=[]
    for span in [250,500,1000]:
        I=1000*4**3/12;S=1000*4**2/6;M=9.8*span**2/8
        deck.append(dict(span_mm=span,ratio=M/(.9*235*S),deflection_mm=5*6.5*span**4/(384*200000*I),
            note='Pelat polos4mm strip1m, UDL satu arah; bukan verifikasi motif bordes, beban titik, sambungan atau diafragma.'))
    mixed=[]
    joist_ids=set(rows['X03']['revit_ids'])
    for version,include_stair in [('h16',False),('h20',False),('h16',True)]:
        v=variants[version];thin=[(id,L) for id,L in cuts if (id.isdigit() and int(id) in joist_ids) or (include_stair and not id.isdigit())];thick=[c for c in cuts if c not in thin]
        a=pack_bars(thin);b=pack_bars(thick)
        newcost=len(a)*(v['stock_price']+v['stock_kg']*6000)+len(b)*(434500+32.5*6000)
        mixed.append(dict(name=f'Joist {v["thickness_mm"]} mm'+(' + penyangga tangga pendek' if include_stair else ' saja')+'; kolom/balok/bracing2.3',thin_stocks=len(a),thick_stocks=len(b),stocks=len(a)+len(b),
            purchase_kg=len(a)*v['stock_kg']+len(b)*32.5,cost=round(baseline_total-old_rhs+newcost),
            saving=round((101*(434500+32.5*6000))-newcost),
            check=beam_check(50,100,v['thickness_mm'],2040,.25,1.334),
            note='Stok dipisah menurut tebal; belum biaya detail tambahan atau penguatan railing.'))
        if include_stair:
            Lmax=max(L for id,L in thin if not id.isdigit())
            mixed[-1]['stair_support_check']=beam_check(50,100,1.6,Lmax,1.,1.334)
            mixed[-1]['note']+=' Penyangga tangga: envelope lebar tributari1m, titik1.334kN; detail tumpuan belum ditetapkan.'
    bracing=[]
    for t in [1.6,2.,2.3]:
        p=section(50,100,t*.93);L=math.hypot(1770,2500);cos=1770/L
        for bays in [1,2,4,8]:
            H=30.975/bays;N=1.6*H/cos
            bracing.append(dict(t=t,active_bays=bays,tension_kN=N,tension_gross_capacity_kN=.9*235*p['A']/1000,
                axial_drift_mm=H*1000/(200000*p['A']/L*cos**2),
                anchor_couple_tension_kN=1.6*H*2.5/1.77,
                note='Bay ilustrasi1.77x2.5m, diagonal tarik saja; distribusi seragam antar bay asumsi. Drift hanya elongasi diagonal, bukan drift rangka total; sambungan/net section/collector belum lulus.'))
    data=dict(revision='R06-STUDI',params=PARAMS,sources=[dict(name=n,url=u) for n,u in SOURCES],
        geometry=dict(core_axes_mm=core,columns=columns,source='Arsip R04; 340/340 ID framing/column masih ada pada pemeriksaan live11Sep. Tiga parameter sampel dibaca; koordinat seluruh node belum diukur ulang.'),
        baseline_total=baseline_total,matrix=matrix,profiles=profiles,guard=guard,stair=stair,edge_beams=edge,
        connections=connections,loads=load,deck=deck,mixed=mixed,bracing=bracing,
        guard_cost_example=dict(profile='SHS60x60x2.3',stocks=18,stock_kg=26,stock_price=346500,
            delta_material_labor=18*((346500+26*6000)-(277000+21.1*6000)),
            note='Contoh ganti18stok kelompok X08 dengan jumlah/panjang tetap; perlu pemilahan tiang vs pegangan, nesting baru dan tambahan detail base. Bukan BOQ final.'),
        thickness_note='0.93 adalah sensitivitas menyerupai produk A500, bukan izin mengasumsikan hollow lokal bersertifikat. Baja lain memerlukan standar produk/rute desain yang benar; Fy235/Fu370 belum diuji.',
        unresolved=['Rangka3D, ketidakstabilan global, imperfection dan P-delta belum diselesaikan.',
            'Distribusi gaya bracing, diafragma dek, sambungan dan slip belum dimodelkan.',
            'Gempa pada LT4, mutu/tebal pelat/tulangan beton dan anchor breakout/pullout belum tersedia.',
            'Getaran global, respons ritmis, damping dan kenyamanan belum diselesaikan.',
            'Railing dan kasus balok transfer dapat mengendalikan; merapatkan kolom tidak otomatis menyelesaikannya.',
            'Titik kolom baru harus diperiksa terhadap tangga, jalur akses, balok beton, rebar dan instalasi.'])
    def clean(x):
        if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
        if isinstance(x,list):return [clean(v) for v in x]
        if isinstance(x,(float,np.floating)):return round(float(x),8) if math.isfinite(x) else None
        return x
    data=clean(data);(OUT/'study.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'perbandingan.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['versi','tebal_mm','bentang_maks_mm','kolom','batang_RHS','kg_beli_RHS','RAB_rendah_Rp','RAB_tinggi_Rp','rasio_joist','rasio_bearer','rasio_kolom_K1','status'])
        for r in data['matrix']:w.writerow([r['key'],r['thickness_mm'],r['max_gap_mm'],r['columns'],r['stocks'],r['purchase_kg'],r['cost_low'],r['cost_high'],r['joist']['ratio'],r['bearer']['ratio'],r['columns_checks'][0]['interaction'],r['compliance']])
    print(json.dumps(dict(options=len(matrix),mixed=mixed,guard_40=[r for r in guard if r['b']==40]),default=float))
    return data

if __name__=='__main__':build()
