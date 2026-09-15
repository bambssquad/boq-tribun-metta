"""Shared V1/V2 viewer and drawing integration. Does not alter R08 quantities."""
import json, math, shutil, re
from pathlib import Path
from shapely.geometry import shape, box
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent

def viewer_hook(js):
    marker='window.__boot3d=boot;'
    assert marker in js
    bridge=(ROOT/'site-version-viewer.js').read_text(encoding='utf-8')
    js=js.replace("const add=(label,value)=>", "if(!source&&window.MettaModelVersion)source=window.MettaModelVersion.source(piece.box);\n    const add=(label,value)=>")
    return js.replace(marker,bridge+'\n'+marker)

def build(dist):
    read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
    g=read('assets/r08/geometry.json');d=read('assets/r08/data.json');items=[]
    def add(ident,group,b):
        if all(b[i+3]>b[i] for i in range(3)):items.append(dict(id=ident,group=group,box=b[:3]+[b[i+3]-b[i] for i in range(3)]))
    def extrude(ident,group,poly,z,t):
        p=shape(poly);ps=[p] if p.geom_type=='Polygon' else list(p.geoms)
        for ni,q in enumerate(ps):
            coords=[pt for ring in [q.exterior,*q.interiors] for pt in ring.coords]
            xs=sorted(set(x for x,y in coords));ys=sorted(set(y for x,y in coords))
            for i,(x,X) in enumerate(zip(xs,xs[1:])):
                for j,(y,Y) in enumerate(zip(ys,ys[1:])):
                    cell=box(x,y,X,Y)
                    if cell.area>.1 and q.covers(cell.representative_point()):add(f'{ident}-{ni}-{i}-{j}',group,[x,y,z-t,X,Y,z])
    for e in g['frame']:
        items.append(dict(id=e['id'],group={'I01':'kolom','I02':'balok','I03':'stiffener'}[e['group']],box=[v for p in e['vertices'] for v in p]))
        if e['group']=='I01':
            v=e['vertices'];x=sum(p[0] for p in v)/8;y=sum(p[1] for p in v)/8
            add(e['id']+'-BP','baseplate',[x-70,y-75,3,x+70,y+75,11]);add(e['id']+'-PAD','baseplate',[x-70,y-75,0,x+70,y+75,3])
    for p in g['infill']:extrude(p['id'],'dek',p['polygon'],p['z'],4)
    for p in g['wood']:extrude(p['id'],'pinus',p['polygon'],p['z'],40)
    for p in g['plate2']:add(p['id'],'riser',p['bounds'])
    for s in g['stairs']:
        extrude(s['id'],'tangga',s['polygon'],s['z'],3)
        x,y,z,w,h=s['x'],s['y'],s['z'],s['width'],s['depth']
        p=shape(s['polygon']);qs=[p] if p.geom_type=='Polygon' else list(p.geoms)
        for qi,q in enumerate(qs):
            for i,(u,v) in enumerate(zip(q.exterior.coords,list(q.exterior.coords)[1:])):
                if abs(u[1]-v[1])<.01 and (abs(u[1]-y)<.1 or abs(u[1]-y-h)<.1):
                    yy=y if abs(u[1]-y)<.1 else y+h-3
                    add(f'{s["id"]}-F{qi}-{i}','tangga',[min(u[0],v[0]),yy,z-50,max(u[0],v[0]),yy+3,z-3])
        n=math.ceil((h-40)/115)+1;bays=math.ceil(w/800)
        for k in range(n):
            yy=y+3+k*(h-46)/(n-1);add(f'{s["id"]}C{k}','stiffener',[x,yy,z-43,x+w,yy+40,z-3])
        for k in range(bays+1):
            xx=x+k*(w-50)/bays;add(f'{s["id"]}S{k}','balok',[xx,y+3,z-143,xx+50,y+h-3,z-43])
    x0,x1=d['params']['x0'],d['params']['x1']
    for e in read('data/finishes-geometry.json')['items']:
        if e['group']!='nosing':continue
        v=e['vertices'];a,b,z=[min(p[i] for p in v) for i in range(3)];A,B,Z=[max(p[i] for p in v) for i in range(3)]
        spans=[(a,A)] if B<=0 or b>=5000 else [(a,min(A,x0)),(max(a,x1),A)]
        for i,(aa,AA) in enumerate(spans):add(f'{e["id"]}-N{i}','nosing',[aa,b,z,AA,B,Z])
    payload=dict(remove_ids=d['changes']['removed_native_rhs_ids']+d['changes']['removed_deck_ids'],clear_groups=['dek','tangga','riser','skirt','nosing'],items=items,mesh=g['mesh'],revision='R08',stair_panels=45,rhs_stocks=d['rhs']['stock_count'])
    (ROOT/'assets/r08/viewer.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    for name in ['site-version.js','site-version.css']:
        shutil.copyfile(ROOT/name,dist/'assets'/name)
    shutil.copyfile(ROOT/'assets/r08/viewer.json',dist/'assets/r08/viewer.json')
    p=dist/'tools.html';s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    # Cache geometry and rendering independently; keep the working page lightweight.
    render=next(t for t in s.find_all('script') if 'const GROUPS=' in t.get_text())
    code=render.get_text()
    for variable,name in [('REVISED','model-native.js'),('FINISH_GEOMETRY','model-finishes.js')]:
        match=re.search(r'const '+variable+r'=(\[.*?\]);',code,re.S)
        assert match
        (dist/'assets'/name).write_text(match.group(0),encoding='utf-8')
        code=code.replace(match.group(0),'')
        render.insert_before(s.new_tag('script',src='assets/'+name))
    (dist/'assets/model-renderer.js').write_text(code,encoding='utf-8')
    render.replace_with(s.new_tag('script',src='assets/model-renderer.js'))
    fem=s.new_tag('section',id='analisis-fem');fem.string='FEM rangka primer: memuat model dan hasil studi elastis.'
    s.select_one('#tiga-d').insert_after(fem)
    s.body.append(s.new_tag('link',rel='stylesheet',href='assets/site-version.css'))
    s.body.append(s.new_tag('script',src='assets/site-version.js'))
    import detail_drawings
    detail_drawings.build(dist)
    for name in ['drawing-viewer.css','drawing-viewer.js','fem-viewer.css','fem-viewer.js']:
        shutil.copyfile(ROOT/name,dist/'assets'/name)
        s.body.append(s.new_tag('script',src='assets/'+name) if name.endswith('.js') else s.new_tag('link',rel='stylesheet',href='assets/'+name))
    nav=s.select_one('nav[aria-label="Navigasi utama"]')
    if nav:
        a=s.new_tag('a',href='#analisis-fem');a.string='FEM';nav.append(a)
    p.write_text(str(s),encoding='utf-8')
