"""Conditional linear 3D Euler-Bernoulli frame study; never a capacity certificate."""
import json, math, gzip, hashlib
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, box, shape
from shapely.ops import unary_union
from r04_model import load_model
ROOT=Path(__file__).parent
E=200000.; G=E/2.6
ASSUMPTIONS=[
 'Studi elastis linier orde pertama; bukan keluaran SAP2000/Tekla atau persetujuan fabrikasi.',
 'Semua sambungan rangka dianggap kaku penuh; semua kaki kolom jepit penuh. Kekakuan las, baut, angkur dan lantai belum dibuktikan.',
 'Node pembagian batang yang berjarak kurang dari 5 mm disatukan sepanjang sumbu untuk menghindari elemen numerik sangat pendek; panjang ujung sumber tetap.',
 'Kontak sumbu dalam 110 mm diidealkan sebagai sambungan kaku dengan offset eksak. Daftar offset dan sumber elemen tersedia; kedekatan geometri bukan bukti sambungan.',
 'Profil RHS 50x100: tebal nominal, sudut tajam, E=200000 MPa, nu=0.3. Sumbu kuat mengikuti tinggi 100 mm untuk batang horizontal; orientasi kolom 50 mm arah X dan 100 mm arah Y.',
 'Beban D=1.5 kPa adalah allowance total beban mati, termasuk berat sendiri; tidak ditambah dua kali. L=5 kPa adalah skenario studi dari R06, bukan penetapan beban lokasi.',
 'Tekanan pada dek: sel dipisah di batas tributari tengah antar batang kontak langsung (sumbu sekitar 54 mm di bawah dek), lalu diteruskan sebagai gaya dan kopel dari centroid sel ke sumbu. Pelat kecil tanpa kontak memakai sumbu terdekat. Ukuran sel sepanjang batang maksimum 100 mm untuk keluaran utama. Tangga, pagar, mesh dan SHS tidak masuk model primer ini; toggle SHS tidak mengubah FEM.',
 'Sumbu lokal x dari ujung a ke b; z sedekat mungkin global Z (kolom: global Y); y = z silang x. N,Vy,Vz,T,My,Mz memakai N dan Nmm; i/j adalah gaya nodal lokal elemen.',
 'Studi ukuran sel beban 400, 200 dan 100 mm tersedia; keluaran utama memakai 100 mm. Sensitivitas perpindahan numerik tidak membuktikan asumsi sambungan atau kapasitas.',
 'Luas tekanan berasal dari union proyeksi dek per elevasi dikurangi lubang beton dengan celah 3 mm; berbeda dari kuantitas RAB dan tidak menggantikannya.',
 'Matriks rangka penuh singular: 14 elemen V1 / 6 elemen V2 tanpa jalur ke kolom dikeluarkan dari submodel. Luas tributari yang terlewat dicatat terpisah; bukan beban total bangunan.',
 'Tidak menghitung P-delta, tekuk, pelat lokal, kapasitas sambungan, getaran kerumunan, gempa, angin, pondasi atau interaksi beton. Tidak ada rasio aman/lulus struktur.',
 'V1 = rangka native R04. Tambahan allowance RAB V1 tidak dianggap memiliki sambungan yang sudah terbukti. V2 = rangka native tersisa dan 54 batang infill R08.'
]

SOURCE_FILES=['fem_model.py','r04_model.py','data/model.json','data/revit-r04-audit.json','data/r04-rear-braces.json','assets/r08/geometry.json']
def source_hashes():
 hashes={}
 for name in SOURCE_FILES:
  text=(ROOT/name).read_text(encoding='utf-8')
  if name.endswith('.json'):text=json.dumps(json.loads(text),sort_keys=True,separators=(',',':'))
  hashes[name]=hashlib.sha256(text.encode('utf-8')).hexdigest()
 return hashes

def section(t):
 b,h=50.,100.
 return dict(A=b*h-(b-2*t)*(h-2*t),Iy=(b*h**3-(b-2*t)*(h-2*t)**3)/12,Iz=(h*b**3-(h-2*t)*(b-2*t)**3)/12,J=4*((b-t)*(h-t))**2/(2*(b+h-2*t)/t))

def local_stiffness(L,t):
 s=section(t); k=np.zeros((12,12))
 for ids,val in [([0,6],E*s['A']/L),([3,9],G*s['J']/L)]:
  k[np.ix_(ids,ids)]+=val*np.array([[1,-1],[-1,1]])
 for ids,I,sign in [([1,5,7,11],s['Iz'],1),([2,4,8,10],s['Iy'],-1)]:
  b=np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])*E*I/L**3
  q=np.diag([1,sign,1,sign]);k[np.ix_(ids,ids)]+=q@b@q
 return k

def axes(a,b):
 x=(b-a)/np.linalg.norm(b-a)
 z=np.array([0.,0.,1.])
 if abs(x[2])>.99: z=np.array([0.,1.,0.])
 z-=x*np.dot(z,x);z/=np.linalg.norm(z)
 y=np.cross(z,x)
 return np.array([x,y,z])

def skew(r):return np.array([[0,-r[2],r[1]],[r[2],0,-r[0]],[-r[1],r[0],0.]])
def offset(r):
 T=np.eye(6);T[:3,3:]=-skew(r);return T

def element(a,b,ma,mb,t):
 L=np.linalg.norm(b-a);R=axes(a,b);T=np.zeros((12,12))
 for i,m,p in [(0,ma,a),(6,mb,b)]:
  q=np.zeros((6,6));q[:3,:3]=q[3:,3:]=R;T[i:i+6,i:i+6]=q@offset(p-m)
 k=local_stiffness(L,t);return T.T@k@T,k,T

def centerline(item):
 v=np.array(item['vertices'],float);c=v.mean(0)
 _,_,vh=np.linalg.svd(v-c,full_matrices=False);d=vh[0]
 if item['group']=='kolom' or item['group']=='I01':d=np.array([0.,0.,1.])
 q=(v-c)@d;a=c+q.min()*d;b=c+q.max()*d
 if tuple(a)>tuple(b):a,b=b,a
 return a,b

def closest(a,b,c,d):
 u=b-a;v=d-c;w=a-c;A=u@u;B=u@v;C=v@v;D=u@w;F=v@w;den=A*C-B*B
 if abs(den)<1e-8*A*C:return None
 s=(B*F-C*D)/den;t=(A*F-B*D)/den
 for _ in range(5):
  s=np.clip((B*t-D)/A,0,1);t=np.clip((B*s+F)/C,0,1)
 return float(s),float(t),float(np.linalg.norm(a+s*u-c-t*v))

def create_model(version,cell_mm=400.):
 m=load_model();g=json.loads((ROOT/'assets/r08/geometry.json').read_text());keep=set(g['retained_native_ids'])
 raw=[i for i in m['items'] if i['group'] in ('kolom','balok','stiffener','bracing') and (version=='v1' or i['id'] in keep)]
 if version=='v2':raw+=g['frame']
 beams=[]
 for i in raw:
  a,b=centerline(i);beams.append(dict(id=str(i['id']),group=i['group'],a=a,b=b,ts=[0.,1.]))
 contacts=[]
 for i,x in enumerate(beams):
  for j in range(i):
   y=beams[j];c=closest(x['a'],x['b'],y['a'],y['b'])
   if c and c[2]<=110:
    s,t,d=c;beams[i]['ts'].append(s);beams[j]['ts'].append(t);contacts.append((i,s,j,t,d))
 # Exact area from clipped deck cells, point-load quadrature; no arbitrary load on brace members.
 surfaces=[]
 for i in m['items']:
  if i['group']=='dek' and (version=='v1' or i['id'] in keep):
   v=np.array(i['vertices']);surfaces.append((Polygon(v[:4,:2]),float(v[:,2].max())))
 if version=='v2':surfaces += [(shape(i['polygon']),i['z']) for i in g['infill']]
  # Union coplanar overlaps and remove concrete footprints with the same 3 mm clearance as drawings.
 levels={}
 for poly,z in surfaces:levels.setdefault(round(z,1),[]).append(poly)
 rc=unary_union([box(c['lo'][0]-3,c['lo'][1]-3,c['hi'][0]+3,c['hi'][1]+3) for c in g['concrete']])
 surfaces=[(unary_union(polys).difference(rc),z) for z,polys in levels.items()]
 eligible=[(i,b) for i,b in enumerate(beams) if abs((b['b']-b['a'])[2])<1 and b['group']!='bracing']
 samples=[];area=0.;pressure_resultant=np.zeros(6)
 for poly,z in surfaces:
  x,y,X,Y=poly.bounds
  bearing=[(i,b) for i,b in eligible if abs(b['a'][2]-(z-54))<3]
  if not bearing:bearing=eligible # tiny closing plates have no direct-contact RHS; explicit nearest-axis fallback
  # Split cells at tributary boundaries of parallel deck-contact members.
  ys=sorted(set(round(b['a'][1],3) for i,b in bearing if abs(b['a'][1]-b['b'][1])<1))
  xs=sorted(set(round(b['a'][0],3) for i,b in bearing if abs(b['a'][0]-b['b'][0])<1))
  yc=sorted(set([y,Y]+[float(q) for q in np.arange(y,Y,cell_mm)]+[(a+b)/2 for a,b in zip(ys,ys[1:]) if y<(a+b)/2<Y]))
  xc=sorted(set([x,X]+[float(q) for q in np.arange(x,X,cell_mm)]+[(a+b)/2 for a,b in zip(xs,xs[1:]) if x<(a+b)/2<X]))
  for xx,XX in zip(xc,xc[1:]):
   for yy,YY in zip(yc,yc[1:]):
    cell=poly.intersection(box(xx,yy,XX,YY))
    if cell.area<1e-8:continue
    p=np.array([cell.centroid.x,cell.centroid.y,z-54]);best=None
    for i,b in bearing:
     u=b['b']-b['a'];t=float(np.clip((p-b['a'])@u/(u@u),0,1));dist=np.linalg.norm(p-b['a']-t*u)
     if best is None or dist<best[0]:best=(dist,i,t)
    _,i,t=best;beams[i]['ts'].append(t);samples.append((i,t,cell.area,p));area+=cell.area;ff=np.array([0.,0.,-cell.area/1000]);pressure_resultant[:3]+=ff;pressure_resultant[3:]+=np.cross(p,ff)
 # Split at all contacts/load locations then enforce rigid offsets with exact DOF transformation.
 points=[];lookup={}
 for i,b in enumerate(beams):
  ts=sorted(set(round(t,7) for t in b['ts']));clean=[0.]
  for t in ts[1:-1]:
   if (t-clean[-1])*np.linalg.norm(b['b']-b['a'])>=5 and (1-t)*np.linalg.norm(b['b']-b['a'])>=5:clean.append(t)
  b['ts']=clean+[1.]
  for t in b['ts']:lookup[(i,t)]=len(points);points.append(b['a']+t*(b['b']-b['a']))
 def at(i,t):return lookup[i,min(beams[i]['ts'],key=lambda z:abs(z-t))]
 parent=list(range(len(points)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):parent[find(b)]=find(a)
 for i,s,j,t,d in contacts:union(at(i,s),at(j,t))
 # Coincident subdivision endpoints across all sources, only 0.1 mm numerical tolerance.
 for i,j in cKDTree(np.array(points)).query_pairs(.1):union(i,j)
 groups={}
 for i in range(len(points)):groups.setdefault(find(i),[]).append(i)
 nodes=[];pn={}
 for ids in groups.values():
  n=len(nodes);p=np.mean([points[i] for i in ids],axis=0);nodes.append(dict(id=str(n),x=float(p[0]),y=float(p[1]),z=float(p[2]),support=[]))
  for i in ids:pn[i]=n
 for i,b in enumerate(beams):
  if b['group'] in ('kolom','I01'):
   t=0. if b['a'][2]<b['b'][2] else 1.;nodes[pn[lookup[i,t]]]['support']=[0,1,2,3,4,5]
 members=[]
 for i,b in enumerate(beams):
  for no,(s,t) in enumerate(zip(b['ts'],b['ts'][1:])):
   ia,ib=lookup[i,s],lookup[i,t]
   if np.linalg.norm(points[ia]-points[ib])<.1:continue
   members.append(dict(id=b['id']+'_'+str(no),sourceId=b['id'],start=str(pn[ia]),end=str(pn[ib]),profile='RHS 50x100',group=b['group'],a=points[ia].tolist(),b=points[ib].tolist()))
 loads=np.zeros((len(nodes),6))
 for i,t,ar,centroid in samples:
  ip=at(i,t);n=pn[ip];p=centroid;np_=np.array([nodes[n][k] for k in ('x','y','z')]);f=np.array([0.,0.,-ar/1000]) # force per kPa
  loads[n,:3]+=f;loads[n,3:]+=np.cross(p-np_,f)
 # Diagnose unsupported components; do not fabricate restraints for concrete ties.
 adj={i:set() for i in range(len(nodes))}
 for b in members:adj[int(b['start'])].add(int(b['end']));adj[int(b['end'])].add(int(b['start']))
 active=set(i for i,n in enumerate(nodes) if n['support']);queue=list(active)
 while queue:
  for j in adj[queue.pop()]:
   if j not in active:active.add(j);queue.append(j)
 omitted=[b for b in members if int(b['start']) not in active]
 excluded_load=-float(sum(loads[i,2] for i in range(len(nodes)) if i not in active))
 mapping={old:new for new,old in enumerate(sorted(active))}
 selected=[]
 for i in sorted(active):
  n=nodes[i];n['id']=str(mapping[i]);n['support']=n['support'] or False;selected.append(n)
 members=[b for b in members if int(b['start']) in active]
 for b in members:b['start']=str(mapping[int(b['start'])]);b['end']=str(mapping[int(b['end'])])
 nodes=selected;loads=loads[sorted(active)]
 return dict(pressureResultantPerKPa=pressure_resultant.tolist(),loadCellMm=cell_mm,nodes=nodes,members=members,loadPerKPa=loads.tolist(),areaM2=-float(loads[:,2].sum())/1000,grossDeckAreaM2=area/1e6,excludedTributaryAreaM2=excluded_load/1000,rawAssemblyStatus='singular: unsupported disconnected members',excludedMembers=omitted,excludedSourceIds=sorted(set(b['sourceId'] for b in omitted)),sourceMemberCount=len(beams),analysedSourceMemberCount=len(set(b['sourceId'] for b in members)),rigidOffsets=[dict(sourceA=beams[i]['id'],sourceB=beams[j]['id'],distanceMm=round(d,4)) for i,s,j,t,d in contacts],modelScope='Connected primary RHS subassembly only; unsupported concrete ties excluded; fully rigid joints / fixed bases assumed')

def solve(model,t,pressure):
 nodes=model['nodes']; n=len(nodes)*6;ii=[];jj=[];vv=[];elements=[]
 for b in model['members']:
  i,j=int(b['start']),int(b['end']);a=np.array(b['a']);z=np.array(b['b']);ma=np.array([nodes[i][k] for k in ('x','y','z')]);mb=np.array([nodes[j][k] for k in ('x','y','z')]);ke,k,T=element(a,z,ma,mb,t)
  dof=np.r_[np.arange(i*6,i*6+6),np.arange(j*6,j*6+6)];ii.extend(np.repeat(dof,12));jj.extend(np.tile(dof,12));vv.extend(ke.ravel());elements.append((b,dof,k,T))
 K=coo_matrix((vv,(ii,jj)),shape=(n,n)).tocsc();F=np.array(model['loadPerKPa']).ravel()*pressure
 fixed=[int(nd['id'])*6+d for nd in nodes for d in (nd.get('support') or [])];free=np.setdiff1d(np.arange(n),fixed);u=np.zeros(n)
 try:
  kf=K[free,:][:,free];scale=1/np.sqrt(kf.diagonal());ks=kf.multiply(scale[:,None]).multiply(scale[None,:]).tocsc();lu=splu(ks)
  if np.min(np.abs(lu.U.diagonal()))<1e-11:raise ValueError('Singular/near-mechanism stiffness; no automatic restraints added')
  u[free]=scale*lu.solve(F[free]*scale)
 except Exception as exc:return dict(status='unstable',reason=str(exc))
 R=K@u-F;res=float(np.linalg.norm(R[free])/max(np.linalg.norm(F),1))
 if res>1e-5:return dict(status='failed',reason='Equilibrium residual exceeds 1e-5',summary={'equilibriumError':res})
 forces={}
 for b,dof,k,T in elements:
  q=k@T@u[dof];vals=[float(q[c] if abs(q[c])>=abs(q[c+6]) else q[c+6]) for c in range(6)]
  forces[b['id']]=dict(zip(['N','Vy','Vz','T','My','Mz'],vals));forces[b['id']].update(i=q[:6].tolist(),j=q[6:].tolist())
 disp=u.reshape(-1,6);react=R.reshape(-1,6);reactions={nd['id']:react[i].tolist() for i,nd in enumerate(nodes) if nd['support']}
 force_balance=np.array([sum(v[k] for v in reactions.values())+F.reshape(-1,6)[:,k].sum() for k in range(3)])
 return dict(status='solved',displacements={nd['id']:disp[i].tolist() for i,nd in enumerate(nodes)},reactions=reactions,loads={nd['id']:F.reshape(-1,6)[i].tolist() for i,nd in enumerate(nodes) if np.linalg.norm(F.reshape(-1,6)[i])>0},memberForces=forces,summary=dict(excludedSourceIds=model.get('excludedSourceIds',[]),excludedTributaryAreaM2=model.get('excludedTributaryAreaM2',0),maxDisplacementMm=float(np.linalg.norm(disp[:,:3],axis=1).max()),maxVerticalMm=float(abs(disp[:,2]).max()),equilibriumError=res,forceBalanceN=force_balance.tolist(),appliedVerticalN=float(F.reshape(-1,6)[:,2].sum()),modelScope=model['modelScope']))

def build():
 out=ROOT/'assets/fem';out.mkdir(exist_ok=True)
 versions={v:create_model(v,100.) for v in ('v1','v2')}
 for v,m in versions.items():
  pin=json.loads(json.dumps(m))
  for n in pin['nodes']:
   if n['support']:n['support']=[0,1,2]
  trial=solve(pin,2.3,6.5)
  m['boundarySensitivity']=dict(support='Translations fixed, rotations free: still assumes anchored bases',rhsThickness=2.3,pressureKPa=6.5,status=trial['status'],summary=trial.get('summary'),reason=trial.get('reason'))
 for v,m in versions.items():
  coarse=create_model(v,200.);initial=create_model(v,400.)
  coarse_result=solve(coarse,2.3,6.5);fine_result=solve(m,2.3,6.5);initial_result=solve(initial,2.3,6.5)
  m['discretizationSensitivity']=dict(initialCellMm=400,initialMaxDisplacementMm=initial_result.get('summary',{}).get('maxDisplacementMm'),coarseCellMm=200,fineCellMm=100,rhsThickness=2.3,pressureKPa=6.5,coarseStatus=coarse_result['status'],fineStatus=fine_result['status'])
  if coarse_result['status']==fine_result['status']=='solved':
   a=coarse_result['summary']['maxDisplacementMm'];b=fine_result['summary']['maxDisplacementMm']
   m['discretizationSensitivity'].update(coarseMaxDisplacementMm=a,fineMaxDisplacementMm=b,relativeChange=abs(b-a)/max(abs(b),1e-12),fineEquilibriumError=fine_result['summary']['equilibriumError'],fineAreaM2=m['areaM2'])
  print(v,'discretization',m['discretizationSensitivity'],flush=True)
 model=dict(schemaVersion=1,sourceHashes=source_hashes(),units=dict(length='mm',force='N',moment='Nmm',rotation='rad'),versions=versions,assumptions=ASSUMPTIONS)
 cases=[];solutions={}
 for v,m in versions.items():
  for t in [1.6,2.,2.3]:
   # Linear superposition scales one factorization exactly; no second-order effects.
   r=solve(m,t,1.)
   sid=f'{v}-h{t:g}'
   url=f'assets/fem/solution-{sid}.json.gz'
   solutions[sid]=dict(url=url)
   (ROOT/url).write_bytes(gzip.compress(json.dumps(r,separators=(',',':')).encode('utf-8'),mtime=0))
   for lc,label,p in [('dead','D = 1.5 kPa',1.5),('live','L = 5 kPa',5.),('service','D + L = 6.5 kPa',6.5),('ultimate','1.2D + 1.6L = 9.8 kPa',9.8)]:
    q=dict(status=r['status'],summary=json.loads(json.dumps(r.get('summary',{}))),id=f'{v}-h{t:g}-{lc}',version=v,rhsThickness=t,shsThickness=None,loadCase=lc,label=label,pressureKPa=p,solutionId=sid,resultScale=p)
    if q['status']=='solved':
     for k in ['maxDisplacementMm','maxVerticalMm','appliedVerticalN']:q['summary'][k]*=p
     q['summary']['forceBalanceN']=[x*p for x in q['summary']['forceBalanceN']]
    else:q['reason']=r.get('reason','Solver unavailable')
    cases.append(q)
   print(v,t,r['status'],r.get('summary',r.get('reason')),flush=True)
 (out/'model.json.gz').write_bytes(gzip.compress(json.dumps(model,separators=(',',':')).encode('utf-8'),mtime=0))
 (out/'results.json').write_text(json.dumps(dict(schemaVersion=1,cases=cases,solutions=solutions,assumptions=ASSUMPTIONS),separators=(',',':')),encoding='utf-8')
 return model,cases
if __name__=='__main__':build()
