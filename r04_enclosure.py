"""Enclosure scope approved by Bam: all risers and both sides, no back/soffit."""
import math,json
from pathlib import Path
def panels(model,stairs):
 rows=[]
 def split(code,x,y,z,w,h,plane='xz'):
  n=math.ceil(w/1200)
  for i in range(n):rows.append(dict(code=f'{code}-{i+1:02}',x=x+(i*w/n if plane in ['xz','xy'] else 0),y=y+(i*w/n if plane=='yz' else 0),z=z,width=w/n,height=h,plane=plane,t=2))
 # Only the 15 full tier panels, not narrow closing strips around concrete.
 decks=[]
 for e in model['items']:
  if e['group']!='dek':continue
  lo=[min(p[i] for p in e['vertices']) for i in range(3)];hi=[max(p[i] for p in e['vertices']) for i in range(3)]
  if 995<hi[1]-lo[1]<1005 and hi[0]-lo[0]>4000:decks.append((e,lo,hi))
 for e,lo,hi in decks:
  left=lo[0]-25 if abs(lo[0])<.1 else lo[0]
  right=hi[0]+25 if abs(hi[0]-17700)<.1 else hi[0]
  # Front beam projects 25 mm beyond its grid. Put cladding outside that face.
  split('R'+str(e['id']),left,lo[1]-27,hi[2]-500,right-left,500)
  split('F'+str(e['id']),left,lo[1]-27,hi[2],right-left,40)
  cap_left=max(left,-25);cap_right=min(right,17725)
  split('C'+str(e['id']),cap_left,lo[1]-25,hi[2]+38,cap_right-cap_left,25,'xy')
 for side,x in [('L',-27),('R',17725)]:
  for tier in range(5):
   # Split height in 1200-mm bands too: each part fits inside stock.
   height=(tier+1)*500+40;n=math.ceil(height/1200)
   for j in range(n):split(f'S{side}{tier+1}-{j+1}',x,tier*1000-27,j*height/n,1027 if tier==4 else 1000,height/n,'yz')
  for j in range(3):split(f'S{side}TAIL-{j+1}',x,5000,j*2540/3,492,2540/3,'yz')
 for r in stairs:
  # 50-mm folded lip is already in 3-mm pan and must not be counted again.
  # Front edge can be interrupted by a concrete notch; never bridge its void.
  k=0
  for part in r['profile']['parts']:
   for a,b in zip(part['outer'],part['outer'][1:]):
    if abs(a[1]-b[1])<.01 and abs(a[1]-r['y'])<.1:
     k+=1;split('ST'+str(r['id'])+f'-E{k}',min(a[0],b[0]),a[1]-2,r['z']-500/3,abs(a[0]-b[0]),500/3-50)
 # Rectangular clipping against the four concrete columns, with 3 mm fit clearance.
 concrete=json.loads((Path(__file__).parent/'data/r04-concrete-context.json').read_text())
 clipped=[]
 for r in rows:
  axes={'xz':(0,2,1),'yz':(1,2,0),'xy':(0,1,2)}[r['plane']]
  u,v,n=axes;origin=[r['x'],r['y'],r['z']]
  cells=[(origin[u],origin[v],origin[u]+r['width'],origin[v]+r['height'])]
  for c in concrete:
   if origin[n]+2<=c['lo'][n]-3 or origin[n]>=c['hi'][n]+3:continue
   x,y,X,Y=c['lo'][u]-3,c['lo'][v]-3,c['hi'][u]+3,c['hi'][v]+3
   next_cells=[]
   for a,b,A,B in cells:
    l,t,R,T=max(a,x),max(b,y),min(A,X),min(B,Y)
    if l>=R or t>=T:next_cells.append((a,b,A,B));continue
    next_cells += [(a,b,l,B),(R,b,A,B),(l,b,R,t),(l,T,R,B)]
   cells=[p for p in next_cells if p[2]-p[0]>.5 and p[3]-p[1]>.5]
  for i,(a,b,A,B) in enumerate(cells):
   q=dict(r);pos=origin.copy();pos[u]=a;pos[v]=b
   q.update(code=r['code']+f'-P{i+1}',x=pos[0],y=pos[1],z=pos[2],width=A-a,height=B-b)
   clipped.append(q)
 rows=clipped
 area=sum(r['width']*r['height']/1e6 for r in rows)
 for r in rows:r['area']=r['width']*r['height']/1e6;r['kg']=r['area']*15.7
 return dict(panels=rows,area=area,net_kg=area*15.7,assumptions=['Riser500mm +fascia40mm dan return27mm di luar muka rangka. Sisi sampai ekor492mm; belakang/bawah terbuka.','Riser tangga116,667mm;50mm sudah flange3mm. Takikan empat kolom beton diberi celah3mm. Dimensi berasal dari audit geometri, toleransi pemasangan perlu trial fit.'])
