"""Recover eight oriented member axes from native dimensions, not bounding-box PCA."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent

def corrections():
 m=json.loads((ROOT/'data/model.json').read_text());items={i['id']:i for i in m['items']};props={i['id']:i['props'] for i in m['rhs']};out=[]
 col=[(i['id'],np.array(i['vertices']).mean(0)) for i in m['items'] if i['group']=='kolom']
 for id in [1690235,1690238,1690358,1690361,1690386,1690391,1690396,1690400]:
  item=items[id];v=np.array(item['vertices'],float);c=v.mean(0);p=props[id];cut=p['Cut Length']*304.8;system=p['System Length']*304.8
  if item['group']=='stiffener':
   ys=[2000,3000] if c[1]<3000 else [3000,4000];ends=[];ids=[]
   for y in ys:
    candidates=[(cid,q) for cid,q in col if abs(q[1]-y)<1]
    cid,q=min(candidates,key=lambda pair:pair[1][0]) if c[0]<1000 else max(candidates,key=lambda pair:pair[1][0]);ends.append(q[:2]);ids.append(cid)
   direction=np.r_[ends[1]-ends[0],0.];reference=np.linalg.norm(direction);evidence=dict(columnSourceIds=ids,systemSpanPlanMm=reference,method='Native adjacent outer column centres define plan direction; source Cut Length defines clear axis length')
  else:
   dz=(p['End Level Offset']-p['Start Level Offset'])*304.8;direction=np.array([0.,1000.,dz]);reference=np.linalg.norm(direction);evidence=dict(startLevelOffsetMm=p['Start Level Offset']*304.8,endLevelOffsetMm=p['End Level Offset']*304.8,bayDepthMm=1000.,method='Native Start/End Level Offset defines slope sign; measured rear bay depth 1000 mm; source Cut Length defines clear axis')
  assert abs(reference-system)<1,(id,reference,system)
  x=direction/np.linalg.norm(direction);a=c-x*cut/2;b=c+x*cut/2;z=np.array([0.,0.,1.]);z-=x*(z@x);z/=np.linalg.norm(z);y=np.cross(z,x);u=y*25;w=z*50
  vertices=np.array([a-u-w,b-u-w,b+u-w,a+u-w,a-u+w,b-u+w,b+u+w,a+u+w])
  error=float(max(abs(vertices.min(0)-v.min(0)).max(),abs(vertices.max(0)-v.max(0)).max()))
  assert error<5,(id,error)
  out.append(dict(id=id,group=item['group'],a=a.tolist(),b=b.tolist(),vertices=vertices.tolist(),cutLengthMm=cut,systemLengthMm=system,sourceBoundingBoxMatchMm=error,evidence=evidence,limitation='Axis reconstruction from audited dimensions and adjacent geometry; joint fixity/capacity remains unverified. Not a physical design change.'))
 return out

def build():
 out=ROOT/'data/member-axis-corrections.json';out.write_text(json.dumps(dict(revision='native-axis-correction-1',items=corrections()),indent=2),encoding='utf-8');return out
if __name__=='__main__':print(build())
