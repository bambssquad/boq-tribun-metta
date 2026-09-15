"""Analytical and assembly checks, independent from generated numeric answers."""
import json, gzip
from pathlib import Path
import numpy as np
from fem_model import E,G,section,local_stiffness,element,solve,source_hashes

def close(a,b,tol=1e-7):assert abs(a-b)<=tol*max(abs(b),1), (a,b)
def main():
 t=2.;L=3000.;P=1000.;s=section(t);k=local_stiffness(L,t)
 assert np.allclose(k,k.T)
 # Free single element has exactly six rigid body modes after diagonal scaling.
 d=1/np.sqrt(k.diagonal());eig=np.linalg.eigvalsh(k*d[:,None]*d[None,:]);assert sum(abs(eig)<1e-9)==6,eig
 # Cantilever: axial, torsional, both bending directions and end slope.
 F=np.zeros(12);F[6]=P;F[7]=P;F[8]=P;F[9]=P
 u=np.zeros(12);u[6:]=np.linalg.solve(k[6:,6:],F[6:])
 close(u[6],P*L/(E*s['A']));close(u[9],P*L/(G*s['J']))
 close(u[7],P*L**3/(3*E*s['Iz']));close(u[8],P*L**3/(3*E*s['Iy']))
 close(u[11],P*L**2/(2*E*s['Iz']));close(u[10],-P*L**2/(2*E*s['Iy']))
 # Simply supported beam, two exact elements, midspan point load.
 K=np.zeros((18,18))
 for start in [0,6]:K[start:start+12,start:start+12]+=local_stiffness(L/2,t)
 f=np.zeros(18);f[8]=-P
 free=[6,8,4,10,16];u2=np.zeros(18);u2[free]=np.linalg.solve(K[np.ix_(free,free)],f[free]);r=K@u2-f
 close(u2[8],-P*L**3/(48*E*s['Iy']));close(r[2],P/2);close(r[14],P/2)
 # Offset transformation preserves a global rigid body translation/rotation.
 a=np.array([0.,0.,0.]);b=np.array([L,0.,0.]);ma=np.array([0.,100.,25.]);mb=np.array([L,-50.,40.]);ke,kl,T=element(a,b,ma,mb,t)
 theta=np.array([.001,.002,.003]);ur=np.r_[np.cross(theta,ma),theta,np.cross(theta,mb),theta]
 assert np.linalg.norm(ke@ur)<1e-5
 # Unrestrained body must refuse to solve; no weak springs / fallback pins.
 fixture=dict(nodes=[dict(id='0',x=0,y=0,z=0,support=[]),dict(id='1',x=L,y=0,z=0,support=[])],members=[dict(id='b',start='0',end='1',a=a.tolist(),b=b.tolist())],loadPerKPa=[[0,0,0,0,0,0],[0,0,-P,0,0,0]],modelScope='benchmark')
 assert solve(fixture,t,1)['status']=='unstable'
 root=Path(__file__).parent/'assets/fem';model=json.loads(gzip.decompress((root/'model.json.gz').read_bytes()));manifest=json.loads((root/'results.json').read_text());cases=manifest['cases']
 assert model['sourceHashes']==source_hashes(), 'Stale FEM assets: rerun python fem_model.py'
 assert len(cases)==24
 for c in cases:
  sol=json.loads(gzip.decompress((Path(__file__).parent/manifest['solutions'][c['solutionId']]['url']).read_bytes()))
  for key in ['displacements','reactions','loads']:c[key]={k:[x*c['resultScale'] for x in v] for k,v in sol[key].items()}
  c['memberForces']=sol['memberForces']
  assert c['status']=='solved',c
  assert c['summary']['equilibriumError']<1e-6,c['summary']
  assert max(abs(x) for x in c['summary']['forceBalanceN'])<.1,c['summary']
  m=model['versions'][c['version']]
  # Independently preserve original surface pressure force and global moment.
  original=np.array(m['pressureResultantPerKPa'])*c['pressureKPa'];actual=np.zeros(6)
  for nid,v in c['loads'].items():
   nd=m['nodes'][int(nid)];pos=np.array([nd['x'],nd['y'],nd['z']]);actual[:3]+=v[:3];actual[3:]+=np.cross(pos,v[:3])+v[3:]
  assert np.linalg.norm(actual-original)<.01,(actual,original)
  close(-c['summary']['appliedVerticalN'],m['areaM2']*1000*c['pressureKPa'],1e-9)
  # Moment equilibrium around global origin, including applied nodal couples.
  balance=np.zeros(3)
  for key in ['loads','reactions']:
   for nid,v in c[key].items():
    nd=m['nodes'][int(nid)];pos=np.array([nd['x'],nd['y'],nd['z']]);balance+=np.cross(pos,v[:3])+v[3:]
  assert np.linalg.norm(balance)<100.,balance
  assert set(c['memberForces'])==set(b['id'] for b in m['members'])
 for v in ['v1','v2']:
  ms=model['versions'][v];sens=ms['discretizationSensitivity']
  assert sens['coarseStatus']==sens['fineStatus']=='solved'
  close(sens['fineAreaM2'],ms['areaM2'],1e-9)
  close(sens['relativeChange'],abs(sens['fineMaxDisplacementMm']-sens['coarseMaxDisplacementMm'])/sens['fineMaxDisplacementMm'],1e-10)
  assert sens['fineEquilibriumError']<1e-6
  print(v,'200/100 mm displacement sensitivity:',round(sens['relativeChange']*100,4),'percent; not a capacity check')
  d=[next(c['summary']['maxDisplacementMm'] for c in cases if c['version']==v and c['rhsThickness']==t and c['loadCase']=='service') for t in [1.6,2,2.3]]
  assert d[0]>d[1]>d[2],d
 assert model['versions']['v2']['sourceMemberCount']>model['versions']['v1']['sourceMemberCount']
 print('PASS: stiffness symmetry; six rigid modes; axial/torsion/biaxial cantilever; simply supported beam; exact rigid offset; mechanism refusal; 24 cases; force and moment equilibrium; load-area reconciliation; thickness trend; V1/V2 geometry difference.')
if __name__=='__main__':main()
