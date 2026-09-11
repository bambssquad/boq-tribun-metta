"""Reproducible R05 screening; incomplete project design is never marked compliant."""
import json, math
from pathlib import Path
import numpy as np
from r04_model import load_model
from revision04 import pack_bars

ROOT=Path(__file__).parent
PARAMS=dict(E_MPa=200000.,fy_MPa=235.,density_kg_m3=7850.,dead_kPa=1.5,
            live_kPa=5.,point_kN=1.334,phi=.9,deflection_divisor=360.,
            thickness_factors=[1.,.93],joist_tributary_m=.25)

def rhs(t,b=50.,h=100.):
    # Rounded RHS: outside radius 2t, inside radius t. Integrate fillet voids.
    def rounded(B,H,r):
        # Horizontal strips integrate I about both axes via Gauss quadrature.
        nodes,weights=np.polynomial.legendre.leggauss(96)
        area=ix=iy=zx=0.
        for y0,y1 in [(-H/2,-H/2+r),(-H/2+r,0),(0,H/2-r),(H/2-r,H/2)]:
            yy=(nodes+1)*(y1-y0)/2+y0
            dy=np.maximum(np.abs(yy)-(H/2-r),0)
            width=B-2*r+2*np.sqrt(np.maximum(r*r-dy*dy,0))
            ww=weights*(y1-y0)/2
            area+=sum(ww*width);ix+=sum(ww*width*yy**2)
            iy+=sum(ww*width**3/12);zx+=sum(ww*width*np.abs(yy))
        return np.array([area,ix,iy,zx])
    A,Ix,Iy,Z=rounded(b,h,2*t)-rounded(b-2*t,h-2*t,t)
    return dict(t=t,b=b,h=h,A=float(A),Ix=float(Ix),Iy=float(Iy),S=float(Ix/(h/2)),
                Z=float(Z),kg_m=float(A*.00785),ry=float(math.sqrt(Iy/A)))

def beam(span,trib,t,point=None):
    p=rhs(t);E=PARAMS['E_MPa'];fy=PARAMS['fy_MPa'];D=PARAMS['dead_kPa'];L=PARAMS['live_kPa']
    qD=D*trib;qL=L*trib;P=PARAMS['point_kN']*1000 if point is None else point
    Mu=max((1.2*qD+1.6*qL)*span**2/8,1.2*qD*span**2/8+1.6*P*span/4)
    delta=max(5*(qD+qL)*span**4/(384*E*p['Ix']),5*qD*span**4/(384*E*p['Ix'])+P*span**3/(48*E*p['Ix']))
    bf=50-3*t;hw=100-3*t;lamf=bf/t;lamw=hw/t;root=math.sqrt(E/fy)
    # Deliberately use elastic first-yield capacity only where both plates compact.
    # This avoids taking plastic/continuity credit in the preliminary comparison.
    compact=lamf<=1.12*root and lamw<=2.42*root
    phiMy=.9*fy*p['S']
    # Closed thin-wall torsion approximation; Lp check prevents implicit LTB omission.
    J=4*((50-t)*(100-t))**2/(2*((50-t)+(100-t))/t)
    Lp=.13*E*p['ry']*math.sqrt(J*p['A'])/(fy*p['Z'])
    Vu=max((1.2*qD+1.6*qL)*span/2,1.2*qD*span/2+1.6*P/2)
    kv=5.;cv=min(1.,1.1*math.sqrt(kv*E/fy)/lamw)
    if lamw>1.37*math.sqrt(kv*E/fy):cv=1.51*kv*E/(fy*lamw**2)
    phiV=.9*.6*fy*(2*hw*t)*cv
    return dict(span_mm=span,tributary_m=trib,t_design_mm=t,Mu_kNm=Mu/1e6,
                phi_elastic_M_kNm=phiMy/1e6,bending_ratio=Mu/phiMy,
                shear_ratio=Vu/phiV,deflection_mm=delta,limit_mm=span/360,
                deflection_ratio=delta/(span/360),flange_compact=lamf<=1.12*root,
                web_compact=lamw<=2.42*root,Lp_mm=Lp,
                passes_screen=bool(compact and span<=Lp and Mu<=phiMy and Vu<=phiV and delta<=span/360))

def compression(length,t,K=1.):
    p=rhs(t);E=PARAMS['E_MPa'];fy=PARAMS['fy_MPa'];lr=1.4*math.sqrt(E/fy)
    KLr=K*length/p['ry'];Fe=math.pi**2*E/KLr**2
    Fcr=(.658**(fy/Fe))*fy if fy/Fe<=2.25 else .877*Fe
    Ae=p['A'];widths=[]
    for b in [50-3*t,100-3*t]:
        lam=b/t;Fel=(1.38*lr/lam)**2*fy
        be=b if lam<=lr*math.sqrt(fy/Fcr) else min(b,b*(1-.2*math.sqrt(Fel/Fcr))*math.sqrt(Fel/Fcr))
        Ae-=2*(b-be)*t;widths.append(dict(b_mm=b,lambda_value=lam,be_mm=be))
    return dict(length_mm=length,K=K,t_design_mm=t,KLr=KLr,phiPn_kN=.9*Fcr*Ae/1000,
                gross_area_mm2=p['A'],effective_area_mm2=Ae,widths=widths,
                note='Tekan murni E3/E7; belum termasuk momen, goyang, gempa, sambungan dan beton.')

def build():
    m=load_model();a=json.loads((ROOT/'data/revit-2026-09-11-audit.json').read_text(encoding='utf-8'))
    live={e['id']:e for e in a['members']};g={e['id']:e for e in m['items']}
    joists=[];bearers=[]
    for e in m['items']:
        if e['group']!='stiffener':continue
        v=np.array(e['vertices']);lo=v.min(0);hi=v.max(0);r=dict(id=e['id'],lo=lo,hi=hi,center=(lo+hi)/2)
        (joists if hi[0]-lo[0]>hi[1]-lo[1] else bearers).append(r)
    checks=[]
    for j in joists:
        xs=[];y=j['center'][1];z=j['lo'][2]
        for b in bearers:
            if abs(b['hi'][2]-z)>2 or not b['lo'][1]<=y<=b['hi'][1]:continue
            # Only rectangular axis-aligned bearers enter the inferred support list.
            # The four skewed end bearers are handled by the conservative 2000mm floor.
            x=b['center'][0]
            if j['lo'][0]-100<=x<=j['hi'][0]+100:xs.append(float(x))
        xs=sorted(xs);spans=[b-a for a,b in zip(xs,xs[1:])]
        observed=max(spans) if spans else None
        # Use at least 2m for every joist, above the normal ~1.77m spacing.
        span=max(2000.,observed or float(j['hi'][0]-j['lo'][0]))
        cases=[beam(span,.25,t*factor) for t in [2.3,2.0,1.6] for factor in PARAMS['thickness_factors']]
        checks.append(dict(id=j['id'],cut_length_m=live[j['id']]['props']['Cut Length']*.3048,
                           support_x_mm=xs,inferred_max_span_mm=observed,cases=cases,
                           candidate=bool(len(xs)>=2 and all(x['passes_screen'] for x in cases))))
    assert len(joists)==45 and len(bearers)==65
    ids=[c['id'] for c in checks if c['candidate']]
    r04=json.loads((ROOT/'assets/r04/data.json').read_text(encoding='utf-8'))
    cuts=[(label,float(L)) for stock in r04['main_stock'] for label,L in stock['cuts']]
    old_kg=len(r04['main_stock'])*32.5
    variants={}
    price_kg=434500/32.5
    for key,t,stock_kg,stock_price,price_basis in [
        ('model',2.3,32.5,434500,'Katalog SMS Perkasa; sama dengan tarif Excel.'),
        ('h20',2.0,28.26,373900,'Katalog SMS Perkasa, harga tayang 27 Agustus; dibaca 11 September 2026.'),
        ('h16',1.6,22.61,22.61*price_kg,'Estimasi: massa interpolasi katalog 1,5/1,8 mm dan harga/kg Excel 2,3 mm; bukan penawaran 1,6 mm.')]:
        variants[key]=dict(thickness_mm=t,stock_count=len(r04['main_stock']),stock_kg=stock_kg,
            stock_price=stock_price,price_kg=stock_price/stock_kg,purchase_kg=len(r04['main_stock'])*stock_kg,
            net_kg=r04['main_length']*rhs(t)['kg_m'],price_basis=price_basis,
            joist_checks=[beam(2000,.25,t*f) for f in [1.,.93]],
            bearer_checks=[beam(1060,1.77,t*f) for f in [1.,.93]],
            column_checks=[compression(2482,t*f,K) for f in [1.,.93] for K in [1.,2.]])
    data=dict(revision='R05-STUDI',date='2026-09-11',params=PARAMS,
        scope='Perbandingan seluruh hollow 50x100: kolom, rangka, bracing dan usulan penyangga tangga. Susunan, panjang potong, kapasitas dan posisi tangga tetap.',
        sections=[rhs(t) for t in [1.6,2.0,2.3]],joist_checks=checks,candidate_ids=ids,
        bearer_checks=[beam(1060,1.77,t*f) for t in [2.3,2.0,1.6] for f in [1.,.93]],
        column_checks=[compression(2482,t*f,K) for t in [2.3,2.0,1.6] for f in [1.,.93] for K in [1.,2.]],
        procurement=dict(baseline_stock=len(r04['main_stock']),baseline_kg=old_kg,
            cut_length_m=r04['main_length'],baseline_cuts=r04['main_stock'],variants=variants),
        conclusion='Versi 1,6/2,0/2,3 mm adalah perbandingan biaya untuk susunan yang sama. Versi seluruh rangka 1,6 mm tidak lolos kasus penyaringan balok silang pada tebal asumsi 1,488 mm. Tidak satu pun versi dinyatakan memenuhi seluruh pemeriksaan struktur.',
        limitations=['Mutu, tebal aktual, radius sudut dan standar produk belum bersertifikat.',
          'Posisi tumpuan berasal dari geometri arsip yang dicocokkan ID dan panjang aktif; ekspor IFC baru gagal.',
          'Belum ada analisis rangka tiga dimensi, getaran, gempa, sambungan hollow, diafragma dan kapasitas beton LT4.',
          'Bentang, tumpuan dan pengekangan lateral wajib dibuktikan pada detail; hasil penyaringan bukan izin fabrikasi.',
          'Tarif 1,6 mm memakai harga/kg Excel dan perkiraan massa stok; biaya penguatan/sambungan tambahan belum terukur.'],
        sources=[dict(name='SNI 1727:2020',url='https://pesta.bsn.go.id/produk/detail/12927-sni17272020'),
          dict(name='SNI 1729:2020, adopsi AISC360-16',url='https://pesta.bsn.go.id/produk/detail/12882-sni17292020'),
          dict(name='SNI 7971:2013; bila standar produk canai dingin berlaku',url='https://pesta.bsn.go.id/produk/detail/9714-sni79712013'),
          dict(name='AISC360-16 B4, E3/E7, F7, G5',url='https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_june-2019_linked.pdf'),
          dict(name='ICC300-2017 303; pembanding beban tribun',url='https://codes.iccsafe.org/content/ICC3002017/chapter-3-construction?site_type=public'),
          dict(name='Katalog hollow50x100x1,6; tanpa harga/sertifikat',url='https://jualbesi.com/produk/besi-hollow-hitam-50x100x1-6/'),
          dict(name='Harga dan massa stok pembanding1,5/1,8/2,3mm, 11 September2026',url='https://www.smsperkasa.com/produk/besi-hollow-hitam')])
    (ROOT/'data/r05-study.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('STUDY:',len(ids),'joists screened;',len(cuts),'cuts /',len(r04['main_stock']),'stocks for every thickness; full-frame compliance unresolved.')
    return data

if __name__=='__main__':build()
