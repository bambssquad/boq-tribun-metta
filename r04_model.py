"""R04 web projection from saved native element IDs and measured cut lengths."""
import json,copy,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent
def read(name):return json.loads((ROOT/'data'/name).read_text())
def box(bounds):
 x,y,z,X,Y,Z=bounds
 return [[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]]
def load_model():
 m=copy.deepcopy(read('model.json'));audit=read('revit-r04-audit.json');removed=set(audit['removed_ids'])
 m['rhs']=[r for r in m['rhs'] if r['id'] not in removed]+audit['braces']
 m['items']=[r for r in m['items'] if r['id'] not in removed]
 byid={r['id']:r for r in audit['braces']}
 def member(id,a,b,horizontal=False):
  r=byid[id];a=np.array(a,dtype=float);b=np.array(b,dtype=float);axis=(b-a)/np.linalg.norm(b-a)
  cut=r['props']['Cut Length']*304.8;center=(a+b)/2
  if horizontal:
   u=np.array([-axis[1],axis[0],0])*50;v=np.array([0,0,25])
   center[2]=(r['props']['Elevation at Top']+r['props']['Elevation at Bottom'])*152.4-16000
  else:
   u=np.array([0,25,0]);v=np.array([-axis[2],0,axis[0]])*50
   center-=v # top-justified sloping RHS, simplified external solid at LOD200.
  p=center-axis*cut/2;q=center+axis*cut/2
  vertices=[p-u-v,q-u-v,q+u-v,p+u-v,p-u+v,q-u+v,q+u+v,p+u+v]
  m['items'].append(dict(id=id,group='bracing',vertices=np.round(vertices,4).tolist(),mark=r['props']['Mark']))
 for r in read('r04-rear-braces.json'):member(r['id'],[r['x0'],r['y'],r['startZ']],[r['x1'],r['y'],r['endZ']])
 for ids,x0,x1 in [([1694599,1694607],3540,4830),([1694611,1694615],12870,14160)]:
  member(ids[0],[x0,2000,1350],[x1,3000,1350],True)
  member(ids[1],[x0,3000,1290],[x1,2000,1290],True)
 m['revision']='R04';m['provenance']='R03 geometry plus R04 native ID/cut-length readback. External solids at LOD200; connections remain design proposals.'
 assert len(m['rhs'])==165 and len([e for e in m['items'] if e['group']=='bracing'])==20
 return m
def cover_geometry():
 return [dict(id=p['code'],group='skirt' if p['code'].startswith('C2-S') and not p['code'].startswith('C2-ST') else 'riser',vertices=box(p['bounds'])) for p in read('r04-cover-parts.json')]
