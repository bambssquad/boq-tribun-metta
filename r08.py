"""R08 coordination option. Immutable R04 geometry -> explicit geometry/cut/BOQ delta.

This is a measurable proposal, not an approved structural or fabrication design.
"""
import copy, csv, html, json, math
from collections import defaultdict
from pathlib import Path
from shapely.geometry import Polygon, box as rect, mapping
from shapely.ops import unary_union
from r04_model import load_model, box
from revision04 import pack_bars
from r04_nesting import pack

ROOT = Path(__file__).parent
OUT = ROOT/'assets/r08'
PARAMS = dict(revision='R08', x0=5450.0373, x1=6850.0751, depth=5000,
              tier_depth=1000, tier_rise=500, tiers=5, concrete_gap=3,
              stock_length=6000, kerf=3, seat_module=500, mesh_panel_max=800)

def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p, d): (OUT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def polys(g):
    if g.is_empty: return []
    return [g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon' and p.area>1]
def bounds(e): return [min(p[i] for p in e['vertices']) for i in range(3)]+[max(p[i] for p in e['vertices']) for i in range(3)]
def area_parts(p): return unary_union([Polygon(q['outer'],q['holes']) for q in p['parts']])
def measure_stock(cuts):
    stocks=pack_bars([(c['id'],c['length_mm']) for c in cuts])
    owners={c['id']:c['owner'] for c in cuts}; allocated=defaultdict(float); lengths=defaultdict(float)
    for c in cuts: lengths[c['owner']]+=c['length_mm']/1000
    for b in stocks:
        length=sum(L for _,L in b['cuts'])
        for ident,L in b['cuts']: allocated[owners[ident]]+=L/length
    return dict(stocks=stocks,stock_count=len(stocks),cut_count=len(cuts),length_m=sum(lengths.values()),allocated_bars=dict(allocated),lengths_m=dict(lengths))

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    base=read('assets/r05/boq.json'); old=read('assets/r04/data.json'); model=load_model()
    finishes=read('data/finishes-geometry.json'); covers=read('data/r04-cover-parts.json')
    concrete=read('data/r04-concrete-context.json'); catalogue=read('data/r08-mesh-catalogue.json')
    x0,x1=PARAMS['x0'],PARAMS['x1']; strip=rect(x0,-10,x1,5000)
    rc=unary_union([rect(c['lo'][0]-3,c['lo'][1]-3,c['hi'][0]+3,c['hi'][1]+3) for c in concrete])
    stairs=[]; removed_stairs=[]; stair_delta=[]; cuts=[]; shs=[]; flat=[]
    # Snap only the two selected strip edges (<0.2 mm archive noise).
    for s in old['stairs']:
        shape=area_parts(s['profile']); remaining=shape.difference(strip)
        changed=shape.area-remaining.area>100
        if remaining.area<100: removed_stairs.append(s['id'])
        if changed: stair_delta.append(dict(id=s['id'],before_m2=shape.area/1e6,after_m2=remaining.area/1e6))
        for n,p in enumerate(polys(remaining)):
            if p.area<100: continue
            a,b,A,B=p.bounds; w=A-a; depth=B-b
            ident=str(s['id'])+('-R08-'+str(n+1) if changed else '')
            fold=0
            for u,v in zip(p.exterior.coords,list(p.exterior.coords)[1:]):
                if abs(u[1]-v[1])<.01 and (abs(u[1]-b)<.1 or abs(u[1]-B)<.1): fold+=abs(u[0]-v[0])
            blank_depth=math.ceil(depth+100-2*old['bend_deduction'])
            stair=dict(id=ident,source_id=s['id'],x=a,y=b,z=s['z'],width=w,depth=depth,
                       polygon=mapping(p),area_m2=p.area/1e6,net_flat_area=(p.area+fold*(50-old['bend_deduction']))/1e6,
                       fold_length_mm=fold,flat=blank_depth)
            stairs.append(stair); flat.append((ident,math.ceil(w),blank_depth))
            for k in range(math.ceil(w/800)+1):cuts.append(dict(id=ident+'S'+str(k),length_mm=depth-6,owner='B02',origin='retained stair support proposal'))
            for k in range(math.ceil((depth-40)/115)+1):shs.append(dict(id=ident+'C'+str(k),length_mm=w,owner='B03',origin='retained stair cross support proposal'))

    # Replace eight short concrete-side struts and six small closing deck strips
    # inside the selected infill; retaining them would duplicate the new frame/deck.
    removed_native=[]; removed_deck=[]; deck_removed_area=0
    native_geometry=[]
    for e in model['items']:
        a,b,z,A,B,Z=bounds(e)
        inside=a>=x0-.2 and A<=x1+.2 and b<5000 and B>0
        if inside and e['group']=='balok' and A-a<200:
            removed_native.append(e['id']); continue
        if inside and e['group']=='dek':
            removed_deck.append(e['id']);deck_removed_area+=(A-a)*(B-b)/1e6;continue
        native_geometry.append(e)
    live={e['id']:e for e in read('data/quantity-reaudit-live.json')['members']}
    for r in base['rows']:
        if r['id'] not in ['X01','X02','X03','X04','X05','X06','B01']:continue
        for ident in r['revit_ids']:
            if ident in removed_native:continue
            p=live[ident]['props'];cuts.append(dict(id=str(ident),length_mm=p.get('Cut Length',p.get('System Length'))*304.8,owner=r['id'],origin='native archive'))

    infill=[]; wood=[]; frame=[]; new_cuts=[]
    def member(ident,owner,bd,L):
        frame.append(dict(id=ident,group=owner,vertices=box(bd)))
        c=dict(id=ident,owner=owner,length_mm=L,origin='R08 proposed infill');cuts.append(c);new_cuts.append(c)
    # Twenty new posts on the floor below. Base plates stay within the infill strip.
    # RC avoidance forces an asymmetric support position at tiers 3/4; engineer
    # must verify cantilevers, floor reactions, connections and temporary stability.
    post_ys=[[100,900],[1100,1900],[2100,2550],[3300,3900],[4100,4850]]
    post_xs=[x0+70,x1-70]
    for t in range(5):
        y=t*1000; z=(t+1)*500
        shape=rect(x0,y,x1,y+1000).difference(rc)
        infill.append(dict(id=f'I{t+1}',z=z,polygon=mapping(shape),area_m2=shape.area/1e6))
        seat=rect(x0,y,x1,y+400).difference(rc)
        # Only a full 400 mm seat depth counts toward indicative capacity.
        blocked=rc.intersection(rect(x0,y,x1,y+400))
        intervals=[]
        if blocked.is_empty: intervals=[(x0,x1)]
        else:
            aa,bb,AA,BB=blocked.bounds
            intervals=[(x0,max(x0,aa)),(min(x1,AA),x1)]
        wood.append(dict(id=f'W{t+1}',z=z+40,polygon=mapping(seat),area_m2=seat.area/1e6,
                         full_depth_intervals=intervals,seats=sum(math.floor((B-A+1e-6)/500) for A,B in intervals)))
        for i,x in enumerate(post_xs):
            member(f'I{t+1}-G{i}', 'I02',[x-25,y,z-204,x+25,y+1000,z-104],1000)
            for j,yy in enumerate(post_ys[t]):
                member(f'I{t+1}-P{i}{j}','I01',[x-25,yy-50,11,x+25,yy+50,z-204],z-215)
        yylist=[y+50,y+275,y+500,y+725,y+950]
        if t==2:yylist.append(2650)
        if t==3:yylist.append(3225)
        for j,yy in enumerate(sorted(yylist)):
            plan=rect(x0,yy-25,x1,yy+25)
            if plan.intersects(rc):continue
            member(f'I{t+1}-J{j}','I03',[x0,yy-25,z-104,x1,yy+25,z-4],x1-x0)
    rhs=measure_stock(cuts)

    # Front plates remain plate; central stair risers disappear and infill risers,
    # fascia/return and side closures against the two retained stair strips appear.
    plate2=[]; mesh_surfaces=[]
    for p in covers:
        if p['code'].startswith('C2-S') and not p['code'].startswith('C2-ST'):
            mesh_surfaces.append(p);continue
        a,b,z,A,B,Z=p['bounds']; intervals=[(a,A)]
        if p['code'].startswith('C2-ST') and A>x0 and a<x1:
            intervals=[(a,min(A,x0)),(max(a,x1),A)]
        for n,(aa,AA) in enumerate(intervals):
            if AA-aa<.2:continue
            bd=[aa,b,z,AA,B,Z];ds=sorted([AA-aa,B-b,Z-z],reverse=True)
            plate2.append(dict(id=p['code']+f'-{n}',bounds=bd,width=ds[0],height=ds[1],area_m2=ds[0]*ds[1]/1e6))
    for t in range(5):
        y=t*1000;z=(t+1)*500
        for label,bd in [('R',[x0,y-2,z-500,x1,y,z]),('F',[x0,y-2,z,x1,y,z+40]),('C',[x0,y-25,z+38,x1,y,z+40])]:
            # Clip front pieces around the existing RC column when the face crosses it.
            spans=[(x0,x1)]
            for c in concrete:
                if c['lo'][1]-3<=y<=c['hi'][1]+3:
                    spans=[(a,min(A,c['lo'][0]-3)) for a,A in spans]+[(max(a,c['hi'][0]+3),A) for a,A in spans]
            for j,(a,A) in enumerate(spans):
                if A-a<1:continue
                bd2=bd.copy();bd2[0]=a;bd2[3]=A;ds=sorted([A-a,bd2[4]-bd2[1],bd2[5]-bd2[2]],reverse=True)
                plate2.append(dict(id=f'I{t+1}-{label}-{j}',bounds=bd2,width=ds[0],height=ds[1],area_m2=ds[0]*ds[1]/1e6))
        # Only the left edge meets retained stairs. The right edge joins seating.
        for side,x in [('L',x0)]:
            for j,(start,end,h) in enumerate([(0,266.7,333.33),(266.7,533.4,166.67)]):
                bd=[x,y+start,z-h,x+2,y+end,z]
                plate2.append(dict(id=f'I{t+1}-SIDE-{side}{j}',bounds=bd,width=end-start,height=h,area_m2=(end-start)*h/1e6))
    p2stocks=pack([(p['id'],math.ceil(p['width']),math.ceil(p['height'])) for p in plate2])
    p3stocks=pack(flat)

    # Small independent mesh subframes avoid relying on unspecified existing backing.
    # Each subframe occupies its own panel bounds; mesh and clamp overlap the frame.
    mesh_panels=[]; clamp_cuts=[]; fasteners=0
    for p in mesh_surfaces:
        a,b,z,A,B,Z=p['bounds']; w=B-b;h=Z-z
        nx=math.ceil(w/800);ny=math.ceil(h/800)
        for i in range(nx):
            for j in range(ny):
                W=w/nx;H=h/ny;ident=p['code']+f'-M{i}{j}'
                if min(W,H)<=80:raise ValueError('Mesh panel too small for frame')
                mw=W-40;mh=H-40
                mesh_panels.append(dict(id=ident,bounds=[a,b+i*W,z+j*H,A,b+(i+1)*W,z+(j+1)*H],width=mw,height=mh,area_m2=mw*mh/1e6))
                for k,L in enumerate([W,W,H-80,H-80]):shs.append(dict(id=ident+'F'+str(k),owner='M02',length_mm=L,origin='R08 independent mesh frame'))
                for k,L in enumerate([mw,mw,mh,mh]):clamp_cuts.append(dict(id=ident+'K'+str(k),owner='M03',length_mm=L))
                fasteners+=2*(math.ceil(mw/200)+1)+2*(math.ceil(mh/200)+1)
    # SHS provenance is identified by owner B03/M02; avoid repeating the same
    # description on every short cut in the downloadable audit.
    for c in shs:c.pop('origin',None)
    shs_stock=measure_stock(shs); clamps=measure_stock(clamp_cuts)
    mesh_area=sum(p['area_m2'] for p in mesh_panels)
    mesh_options=[]
    for opt in catalogue['options']:
        nests=pack([(p['id'],math.ceil(p['width']),math.ceil(p['height'])) for p in mesh_panels],
                   width=opt['roll_length_m']*1000,height=opt['roll_width_m']*1000,trim=10,kerf=3)
        o=copy.deepcopy(opt);o.update(rolls=len(nests),nesting=nests,net_kg=mesh_area/(o['roll_length_m']*o['roll_width_m'])*o['catalogue_roll_kg'],purchase_kg=len(nests)*o['catalogue_roll_kg'])
        # Explicit cost-planning allowance, not a supplier quote.
        o.update(allowance_rp_per_kg=30000,allowance_cost=len(nests)*o['catalogue_roll_kg']*30000)
        mesh_options.append(o)

    rows=copy.deepcopy(base['rows']); byid={r['id']:r for r in rows}
    def setqty(ident,net,buy,basis):
        r=byid[ident];r.update(net_qty=net,purchase_qty=buy,basis='R08: '+basis,status='Studi koordinasi; ukur dan sahkan sebelum fabrikasi')
    def add(ident,name,material,unit,net,buy,labor,rate,basis,extra=False):
        r=dict(id=ident,name=name,material=material,unit=unit,net_qty=net,purchase_qty=buy,labor_rate=labor,material_rate=rate,basis='R08: '+basis,status='Usulan; tarif allowance bila dinyatakan',extra=extra)
        rows.append(r);byid[ident]=r;return r
    for ident,name in [('I01','Kolom tambahan infill'),('I02','Balok memanjang infill'),('I03','Pengaku silang infill')]:
        r=copy.deepcopy(byid['X01']);r.update(id=ident,name=name,revit_ids=[],status='R08: rangka infill usulan, belum elemen Revit');r.pop('source_row',None);r.pop('verification',None);rows.append(r);byid[ident]=r
    for ident,L in rhs['lengths_m'].items():
        r=byid[ident];oldnet=r['net_qty']; oldvars=copy.deepcopy(r.get('variants',{}))
        # Net RHS mass uses the same effective section assumption as the original
        # case; purchase always uses catalogue kg per 6 m stock.
        for case in ['model','h20','h16']:
            v=base['study']['procurement']['variants'][case];stockkg=v['stock_kg']
            source=next(q for q in base['rows'] if q['id']=='X01')
            kg_m=(source['net_qty'] if case=='model' else source['variants'][case]['net_qty'])/133.5598
            dest=r if case=='model' else r['variants'][case]
            dest.update(net_qty=L*kg_m,purchase_qty=rhs['allocated_bars'][ident]*stockkg,
                        basis=f'R08: {L:.6f} m potongan; alokasi dari {rhs["stock_count"]} stok bersama × {stockkg} kg/batang. Pola layak, minimum belum terbukti.')
        r['revit_ids']=[i for i in r.get('revit_ids',[]) if i not in removed_native]
    shs_ref=byid['B03']
    r=copy.deepcopy(shs_ref);r.update(id='M02',name='Rangka panel mesh',revit_ids=[]);rows.append(r);byid['M02']=r
    for ident in ['B03','M02']:
        r=byid[ident];L=shs_stock['lengths_m'][ident];alloc=shs_stock['allocated_bars'][ident]
        for key in ['reference','s16','s17','s20','s23']:
            dest=r if key=='reference' else r['shs_variants'][key]
            stockkg=dest.get('stock_kg',15.07)
            dest.update(net_qty=L*stockkg/6,purchase_qty=alloc*stockkg,
                        basis=f'R08: {L:.6f} m; alokasi pola {shs_stock["stock_count"]} batang SHS bersama untuk tangga + panel. Railing lama tetap kelompok terpisah.',stock_kg=stockkg)

    deck_area=byid['X09']['net_qty']/31.4-deck_removed_area+sum(p['area_m2'] for p in infill)
    setqty('X09',deck_area*31.4,math.ceil(deck_area*1.1/2.88)*90.432,f'Dek {deck_area:.6f} m2; pembelian ceil(luas × 1,10 / 2,88) lembar 4 mm. Allowance luas, bukan nesting dek.')
    setqty('X10',sum(p['area_m2'] for p in plate2)*15.7,len(p2stocks)*45.216,f'{len(plate2)} potongan pelat depan/sisi infill; {len(p2stocks)} lembar 2 mm 1200×2400 dari nesting.')
    setqty('X11',sum(s['net_flat_area'] for s in stairs)*23.55,len(p3stocks)*67.824,f'{len(stairs)} tapak tekuk; {len(p3stocks)} lembar 3 mm dari blank konservatif. Uji kupon tekuk diperlukan.')
    rows.remove(byid['X12'])
    newpost=20;new_ends=2*sum(c['owner'] in ['I02','I03'] for c in new_cuts)
    stair_ends=2*sum(c['owner']=='B02' for c in cuts)
    main_ends=274-2*len(removed_native)+new_ends
    coupons=[(f'J{i}',90,120) for i in range((main_ends+stair_ends)*2)]+[(f'G{i}',200,200) for i in range(40)]
    p6stocks=pack(coupons)
    setqty('X14',(len(coupons)-40)*.09*.12*47.1+40*.2*.2*47.1,len(p6stocks)*135.648,f'{len(coupons)} pelat 6 mm; {len(p6stocks)} lembar nesting. Pelat 90×120 dan buhul 200×200 adalah allowance sambungan, belum desain baut/las.')
    for ident,factor in [('X15',1),('X17',1),('X18',2)]:
        bolts=660-4*len(removed_native)+new_ends*2;n=bolts*factor;setqty(ident,n,math.ceil(bolts*1.05)*factor,'Dua baut per ujung balok; pengikat lama dikurangi 8 strut, tambah ujung infill, cadangan 5%. Dua ring per baut pembelian.')
    for ident,factor in [('B04',1),('B05',1),('B06',2)]:
        n=stair_ends*2*factor;setqty(ident,n,math.ceil(n*1.05),'Dua baut per ujung penyangga tangga, cadangan 5%.')
    baseplates=pack([(f'BASE{i}',150,150) for i in range(80)]+[(f'IB{i}',140,150) for i in range(newpost)])
    base_buy=len(baseplates)*180.864;new_base_area=newpost*.14*.15
    setqty('X13',80*.15*.15*62.8,base_buy*1.8/(1.8+new_base_area),f'80 base lama 150×150×8 + 20 base infill dinesting bersama dalam {len(baseplates)} lembar; berat beli dialokasikan menurut luas.')
    add('I04','Base plate infill','Pelat 8 mm / 140×150 mm','kg',new_base_area*62.8,base_buy*new_base_area/(1.8+new_base_area),6000,byid['X13']['material_rate'],f'{newpost} pelat baru; berbagi {len(baseplates)} lembar 1200×2400 dengan 80 base lama, bukan dibulatkan terpisah. Tebal/dimensi dan tumpuan harus dihitung.')
    add('I05','Angkur lantai infill','M12 / allowance sambungan, mutu dan penanaman belum dipilih','set',80,84,15000,35000,'4 angkur per 20 base plate + 5%; Rp35.000 material + Rp15.000 pemasangan/set adalah allowance, bukan harga katalog atau kapasitas sah.')
    add('I06','Karet dudukan infill','Karet 140×150×3 mm / allowance','bh',20,20,500,25000,'20 alas baru; lantai/tumpuan dan tekanan kontak belum diverifikasi.')
    add('I07','Angkur lantai kolom utama','M12 / allowance; spesifikasi dan kapasitas belum ditetapkan','set',320,336,15000,35000,'80 base kolom utama × 4 angkur + 5%. Baut M12×40 rangka bukan angkur beton. Cadangan ini melengkapi jalur tumpuan FEM; kekakuan base, karet 10 mm, lantai, mutu beton dan produk angkur harus diverifikasi.')
    seat_L=sum(p['area_m2'] for p in wood)/.4
    setqty('X22',byid['X22']['net_qty']+seat_L,(byid['X22']['net_qty']+seat_L)*1.1,f'Papan baru setara {seat_L:.6f} m × 400×40 mm setelah takikan RC; allowance potong 10%.')
    setqty('X19',500+40,500+40,'500 set lama + 8 set per 5 tingkat infill; pola pengikat kayu harus dirinci.')
    setqty('X16',1,1,'8 titik ikatan RC tersisa setelah 8 strut dihapus. Cadangan biaya proporsional 8/16 × Rp5.000.000; ukuran/kapasitas angkur belum dipilih.')
    byid['X16']['material_rate']=2500000
    byid['E01'].update(name='Backing riser depan dan hardware railing',basis='R08: cadangan Rp3.500.000 untuk backing pelat depan, ujung railing dan penghubung yang belum terukur. Tidak mencakup rangka/penjepit mesh yang sudah dirinci pada M02–M04.')
    # Retain original fastening convention: max 200 mm along rectangle perimeters.
    cover_screws=sum(2*(math.ceil(p['width']/200)+math.ceil(p['height']/200)) for p in plate2)
    setqty('X20',cover_screws,math.ceil(cover_screws*1.05),'Keliling panel pelat / jarak maksimum 200 mm, cadangan 5%; pengikat mesh dihitung terpisah.')
    meshrow=add('M01','Kawat loket penutup sisi','Mesh galvanis / pilih varian','kg',0,0,0,30000,'Massa roll katalog; harga allowance Rp30.000/kg, bukan penawaran pemasok.')
    meshrow['mesh_variants']={o['id']:dict(net_qty=o['net_kg'],purchase_qty=o['purchase_kg'],material=o['label'],basis=f'R08: {o["rolls"]} roll {o["roll_width_m"]}×{o["roll_length_m"]} m × {o["catalogue_roll_kg"]} kg. Luas mesh bersih {mesh_area:.4f} m2. Harga allowance Rp30.000/kg, wajib diganti penawaran. {o["source"]}') for o in mesh_options}
    add('M03','Strip penjepit tepi mesh','Flat bar 30×3 mm / dua sisi vertikal dan horizontal per panel','kg',clamps['length_m']*.7065,clamps['stock_count']*4.239,6000,15000,f'{len(clamp_cuts)} potongan / {clamps["stock_count"]} batang 6 m. Berat teoritis 4,239 kg/batang, tarif material allowance Rp15.000/kg.')['stock_kg']=4.239
    add('M04','Pengikat mesh dan rangka panel','M6 galvanis + mur + ring / allowance','set',fasteners+4*len(mesh_panels),math.ceil((fasteners+4*len(mesh_panels))*1.05),1000,2500,'Penjepit maksimum 200 mm + 4 pengikat panel per rangka. Jarak/kapasitas belum disahkan. Harga material allowance Rp2.500/set.')
    add('M05','Pemasangan dan potong mesh','Panel kawat loket; ujung kawat ditutup strip','m2',mesh_area,mesh_area,35000,0,'Allowance upah Rp35.000/m2; terpisah dari upah rangka, strip dan pengikat.')
    coat=1.1*(rhs['length_m']*.3+(shs_stock['length_m']+8.4254+97.498388)*.16+clamps['length_m']*.066+2*(deck_area+sum(s['net_flat_area'] for s in stairs)+sum(p['area_m2'] for p in plate2)+(byid['X14']['net_qty']/47.1)+1.8+.42))
    setqty('X24',coat,coat,'Luas luar hollow, strip, kedua muka pelat + 10% tepi; mesh galvanis tidak dicat. Tarif per m2 acuan R07 dipertahankan.')
    setqty('E02',sum(s['area_m2'] for s in stairs),sum(s['area_m2'] for s in stairs),'Antiselip sesuai luas tapak tersisa; bukan bidang infill dudukan.')
    setqty('E03',20,20,'Cadangan clear coat 20 L untuk kayu lama + infill; konsumsi aktual mengikuti produk/uji lapangan.')
    setqty('E04',2*len(stairs),2*len(stairs),'Dua tekukan per tapak; takikan RC dan kupon dibahas bengkel.')
    # Four old SHS stair-side posts are not deleted by this option; rail geometry and
    # allowances remain explicitly unchanged, including two posts beside the RC.
    changes=dict(removed_stair_ids=removed_stairs,stair_delta=stair_delta,removed_native_rhs_ids=removed_native,
                 removed_deck_ids=removed_deck,removed_deck_area_m2=deck_removed_area,
                 old_stair_panels=len(old['stairs']),new_stair_panels=len(stairs),new_posts=newpost,
                 new_rhs_cuts=len(new_cuts),old_side_plate_area_m2=sum(p['area_m2'] for p in mesh_surfaces),
                 mesh_area_m2=mesh_area,mesh_panels=len(mesh_panels),infill_deck_area_m2=sum(p['area_m2'] for p in infill),
                 extra_wood_equivalent_m=seat_L,extra_indicative_seats=sum(p['seats'] for p in wood),
                 indicative_seats_by_tier=[p['seats'] for p in wood],clear_passages_mm=[600,600],stair_zones=2)
    notes=[
      'R08 koreksi sketsa: strip x5450–6850 mm pada zona kiri 2 m menjadi dek dan dudukan selebar sekitar 1400 mm. Tangga kanan yang ditandai dihapus; tersisa dua jalur nominal 600 mm pada dua zona. Jumlah jalur bukan pengesahan kapasitas evakuasi.',
      'Lebar 600 mm belum dikurangi pegangan/finishing. Kapasitas evakuasi dan aksesibilitas belum lulus pemeriksaan. Tambahan kursi hanya studi modul 500 mm, bukan kapasitas operasi yang disahkan.',
      'Rangka infill baru 20 kolom, balok, pengaku, base plate, karet dan angkur adalah usulan. RC ditakik dengan celah 3 mm. Tumpuan lantai, lendutan, stabilitas, las/baut dan akses pemasangan belum disahkan.',
      'Mesh hanya penutup luar kanan/kiri. Riser depan tetap pelat. Mesh bukan pengganti railing, penahan kerumunan atau bracing; rangka panel dan penjepit tepi dihitung.',
      'Harga mesh Rp30.000/kg, strip Rp15.000/kg, M6 Rp2.500/set, angkur Rp35.000/set dan upah baru adalah allowance perencanaan, bukan penawaran pemasok. Total RAB adalah estimasi dengan allowance.',
      'Berat beli RHS/SHS mengikuti katalog dan varian tebal. Potongan digabung sesuai kelompok stok. Railing SHS tetap 2+18 batang terpisah. Batang layak dari nesting, minimum belum terbukti. Dek memakai allowance luas 10%, bukan pola potong final.',
      'Sambungan baru memerlukan pengesahan: pelat 90×120×6, base 140×150×8, M12, 4 angkur/kolom dan posisi kolom hanyalah dasar hitung biaya. Jangan bor lantai atau mulai fabrikasi dari paket ini.',
      'Tahapan: ukur kondisi/akses dan lantai; sahkan struktur/evakuasi serta shop drawing; minta penawaran; kunci daftar potong; mock-up tekuk/mesh; fabrikasi dan QC; pasang dengan penyangga sementara; inspeksi dan serah terima. Dokumen R07 menjadi acuan proses umum, bukan gambar R08.'
    ]
    out=dict(revision='R08',params=PARAMS,rows=rows,rhs=rhs,shs=shs_stock,clamps=clamps,changes=changes,
             mesh_options=mesh_options,mesh_candidate=catalogue['candidate'],notes=notes,sources=catalogue,
             nesting=dict(plate2=p2stocks,plate3=p3stocks,plate6=p6stocks,infill_base8=baseplates),
             cuts=dict(rhs=cuts,shs=shs,clamps=clamp_cuts))
    # Keep browser BOQ payload separate from the detailed manufacturing audit.
    payload=copy.deepcopy(out)
    audit=dict(cuts=payload.pop('cuts'),nesting=payload.pop('nesting'),shs_stocks=payload['shs'].pop('stocks'),clamp_stocks=payload['clamps'].pop('stocks'),mesh_nesting={o['id']:o.pop('nesting') for o in payload['mesh_options']})
    write('data.json',payload);write('audit.json',audit)
    geometry=dict(retained_native_ids=[e['id'] for e in native_geometry],native_source='R04 archive: data/model.json plus data/revit-r04-audit.json',retained_finish_ids=[e['id'] for e in finishes['items'] if e['group'] in ['pinus','railing']],finish_source='data/finishes-geometry.json',stairs=stairs,infill=infill,wood=wood,frame=frame,plate2=plate2,mesh=mesh_panels,concrete=concrete)
    write('geometry.json',geometry)
    with (OUT/'daftar-potong.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['profil','stok','id','komponen','panjang_mm','status'])
        for profile,summary,cs in [('RHS50x100',rhs,cuts),('SHS40x40-tangga-mesh',shs_stock,shs),('strip30x3',clamps,clamp_cuts)]:
            lookup={c['id']:c for c in cs}
            for i,b in enumerate(summary['stocks']):
                for ident,L in b['cuts']:w.writerow([profile,i+1,ident,lookup[ident]['owner'],round(L,4),'studi - belum fabrikasi'])
    from r08_drawings import build as drawings
    drawings(out,geometry,OUT)
    return out

if __name__=='__main__':
    d=build();print('R08:',d['rhs']['stock_count'],'RHS;',d['shs']['stock_count'],'SHS tangga+mesh;',d['changes'])
