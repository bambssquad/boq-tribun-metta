"""Conditional A/C structural options: audited geometry and repeatable elastic comparison."""
import json,gzip,copy
from pathlib import Path
import numpy as np
from fem_model import axes
ROOT=Path(__file__).parent;OUT=ROOT/'assets/structural-study'
REMOVED=[1686090,1686099,1686093,1686096,1687999,1688004,1688008,1688011]
def member(id,group,a,b):
 a=np.array(a,float);b=np.array(b,float);r=axes(a,b);u=r[1]*25;v=r[2]*50
 return dict(id=id,group=group,owner='I01' if group=='kolom' else 'X06' if group=='bracing' else 'I03',a=a.tolist(),b=b.tolist(),vertices=np.array([a-u-v,b-u-v,b+u-v,a+u-v,a-u+v,b-u+v,b+u+v,a+u+v]).tolist(),length_mm=float(np.linalg.norm(b-a)),connection='welded' if np.linalg.norm(b-a)<200 else 'bolted_allowance',profile='RHS 50x100',thickness='selected')
def spec():
 OUT.mkdir(exist_ok=True);g=json.loads((ROOT/'assets/r08/geometry.json').read_text());links=[]
 for side,lo in [('L',4850.),('R',12250.)]:
  steps=sorted([s for s in g['stairs'] if abs(s['x']-lo)<1],key=lambda s:s['y'])
  for tier in range(5):
   rows=steps[tier*3:tier*3+3]
   for riser,(lower,upper) in enumerate(zip(rows,rows[1:])):
    y=(lower['y']+lower['depth']+upper['y'])/2
    for edge,x in enumerate([lower['x']-25,lower['x']+lower['width']+25]):links.append(member(f'SR-{side}-{tier+1}-{riser}-{edge}','balok',[x,y,lower['z']-93],[x,y,upper['z']-93]))
 a=copy.deepcopy(links)+[member('SA-HL','balok',[4850.0385,2938,1307],[5550.0574,2938,1307]),member('SA-HR','balok',[12150.0442,2938,1307],[12850.0631,2938,1307])]
 for tier in range(5):
  z=(tier+1)*500;y=tier*1000
  for mark,yy,zz in [('F',y+100,z-426.34),('B',y+900,z-93)]:a.append(member(f'SA-C{tier+1}-{mark}','balok',[5450.0373,yy,zz],[5495.0373,yy,zz]))
 anchors=[dict(id='SA-RC-L',type='existing_rc',sourceColumnId=1675818,point=[5550.0574,2938,1307],restraints=[0,1,2],anchorCount=4),dict(id='SA-RC-R',type='existing_rc',sourceColumnId=1675819,point=[12150.0442,2938,1307],restraints=[0,1,2],anchorCount=4)]
 c=copy.deepcopy(links);bases=[]
 for tier in range(5):
  top=(tier+1)*500;yb=tier*1000
  for side,x0 in [('L',4850.0385),('R',12250.0643)]:
   xs=[x0+50,x0+550];ys=[yb+633.,yb+950.];name=f'{side}{tier+1}'
   for ix,x in enumerate(xs):
    for iy,y in enumerate(ys):
     id=f'SC-{name}-P{ix}{iy}';c.append(member(id,'kolom',[x,y,11],[x,y,top-343]));bases.append(dict(id=id,point=[x,y,11],anchorCount=4))
    c.append(member(f'SC-{name}-G{ix}','balok',[x,ys[0],top-293],[x,ys[1],top-293]))
    c.append(member(f'SC-{name}-BY{ix}','bracing',[x,ys[0],60],[x,ys[1],top-393]))
   for iy,y in enumerate(ys):
    c.append(member(f'SC-{name}-H{iy}','balok',[x0,y,top-193],[x0+600,y,top-193]))
    c.append(member(f'SC-{name}-BX{iy}','bracing',[xs[0],y,60],[xs[1],y,top-393]))
 common=['Studi jalur beban lengkap dua tangga; sambungan kaku, las dan angkur belum dibuktikan kapasitasnya.','60 girder sisi B02 sudah berada dalam RAB dasar; tidak dibeli dua kali. Ditambah40penghubung vertikal antar tingkat tapak menjadi girder bertangga.','Delapan pengikat RC lama dihapus. Profil RHS tetap mengikuti tebal terpilih.','Beban seluruh30tapak diteruskan ke girder sisi sesuai keseimbangan transversal. SHS B03 dan pelat diperiksa terpisah; tidak diasumsikan menambah kekakuan global.']
 options=dict(a=dict(label='A - tangga terikat rangka utama dan beton',welded_existing_stair_ends=80,added_members=a,remove_ids=REMOVED,anchor_groups=anchors,anchor_count=8,anchor_plate_count=2,new_base_count=0,new_bases=[],notes=common+['10cleatRHS45mm menghubungkan sisi dalam tangga kiri ke rangka infill. Duaheader700mm pada landing tengah ditambatkan ke muka beton; ujung lain mengandalkan sambungan ke baja utama.']),c=dict(label='C - tangga dengan rangka kaki dan pengaku',welded_existing_stair_ends=80,added_members=c,remove_ids=REMOVED,anchor_groups=[dict(id=x['id'],type='floor',point=x['point'],restraints=[0,1,2,3,4,5],anchorCount=4) for x in bases],anchor_count=0,anchor_plate_count=0,new_base_count=40,new_bases=bases,notes=common+['Lima kotak penopang per tangga:40kolom,40balok dan40diagonal selain40link. Tanpa tambatan beton utama;40kaki memerlukan verifikasi angkur/lantai.']))
 (OUT/'options-spec.json').write_text(json.dumps(options,indent=2),encoding='utf-8');return options
def analyse():
 from fem_model import create_model,solve,section,source_hashes
 from shapely.geometry import MultiPoint,shape,box
 import math
 options=json.loads((OUT/'options-spec.json').read_text());geom=json.loads((ROOT/'assets/r08/geometry.json').read_text())
 output=dict(sourceHashes=source_hashes(),options={},notes=['Koreksi sumbu diagonal memperbaiki angka lama sekitar24mm; bukan bukti bangunan pernah melendut24mm.','A dan C memasukkan semua30tapak,60girderB02 yang sudah dibeli,40link vertikal baru dan dukungan tiap tier.','Beban D1.5/L5kPa dan tumpuan/las kaku adalah asumsi studi. Semua kaki termasuk80utama perlu verifikasi angkur, lantai, slip/kompresi pad karet.','SHS B03 diasumsikan memindahkan reaksi transversal sebagai balok sederhana; kekakuan SHS tidak menambah kekakuan global.','Screening tegangan gross bukan kapasitas SNI: tekuk, tebal efektif, pelat/sambungan, angkur, beton, gempa, angin dan getaran belum disahkan.'],sources=[dict(title='STI HSS local slenderness',url='https://steeltubeinstitute.org/resources/width-thickness-requirements-square-rectangular-hss-subject-flexure/'),dict(title='AISC stability and second-order analysis',url='https://www.aisc.org/globalassets/modern-steel/archives/2013/04/2013v04_stability.pdf')])
 for option,o in options.items():
  m=create_model('v2',100,option);cases=[]
  for thickness in [1.6,2.,2.3]:
   result=solve(m,thickness,1.);assert result['status']=='solved';sec=section(thickness);ranks=[]
   for b in m['members']:
    for end in ['i','j']:
     N,Vy,Vz,T,My,Mz=np.array(result['memberForces'][b['id']][end])*9.8
     normal=abs(N)/sec['A']+abs(My)*50/sec['Iy']+abs(Mz)*25/sec['Iz'];tauT=abs(T)/(2*(50-thickness)*(100-thickness)*thickness);tauV=1.5*max(abs(Vy)/(100*thickness),abs(Vz)/(200*thickness));vm=math.sqrt(normal*normal+3*(tauT+tauV)**2)
     ranks.append(dict(sourceId=b['sourceId'],memberId=b['id'],end=end,normalMPa=normal,torsionShearMPa=tauT,shearMPa=tauV,grossVonMisesScreenMPa=vm))
   peak=max(ranks,key=lambda x:x['grossVonMisesScreenMPa']);stair=max([r for r in ranks if r['sourceId'].startswith(('SA-','SC-','SR-')) or r['sourceId'].endswith(('S0','S1'))],key=lambda x:x['grossVonMisesScreenMPa']);reactions=[]
   for n in m['nodes']:
    if n.get('supportKind')=='assumed_rc_anchor' or n['support'] and any(abs(n['x']-q['point'][0])<.1 and abs(n['y']-q['point'][1])<.1 for q in o['new_bases']):reactions.append(dict(nodeId=n['id'],anchorId=n.get('anchorId','floor'),point=[n['x'],n['y'],n['z']],ultimate=[v*9.8 for v in result['reactions'][n['id']]]))
   cases.append(dict(rhsThickness=thickness,serviceMaxDisplacementMm=result['summary']['maxDisplacementMm']*6.5,areaM2=m['areaM2'],stairAreaM2=m['stairAreaM2'],peakGrossStress=peak,stairPeakGrossStress=stair,grossYieldScreenExceeded=peak['grossVonMisesScreenMPa']>235,anchorReactions=reactions,equilibriumError=result['summary']['equilibriumError']))
  # 0.2% fictitious horizontal load probes elastic stiffness, NOT an AISC direct-analysis stability check.
  lateral=[]
  for direction in [0,1]:
   lm=copy.deepcopy(m);loads=np.array(lm['loadPerKPa']);loads[:,direction]=-.002*loads[:,2];lm['loadPerKPa']=loads.tolist();trial=solve(lm,2.3,9.8)
   lateral.append(dict(direction='X' if direction==0 else 'Y',notionalFraction=.002,status=trial['status'],maxDisplacementMm=trial.get('summary',{}).get('maxDisplacementMm'),note='Elastic first-order gravity plus illustrative 0.2% lateral only; not seismic/wind or second-order capacity'))
  collisions=[]
  for b in o['added_members']:
   vv=np.array(b['vertices']);z0,z1=vv[:,2].min(),vv[:,2].max();foot=MultiPoint(vv[:,:2]).convex_hull
   for rc in geom['concrete']:
    area=foot.intersection(box(rc['lo'][0],rc['lo'][1],rc['hi'][0],rc['hi'][1])).area
    if area>1 and min(z1,rc['hi'][2])-max(z0,rc['lo'][2])>1:collisions.append([b['id'],'RC',rc['id'],area])
   for st in geom['stairs']:
    if min(z1,st['z'])-max(z0,st['z']-3)>1 and foot.intersection(shape(st['polygon'])).area>1:collisions.append([b['id'],'stair',st['id']])
  assert not collisions,collisions
  output['options'][option]=dict(label=o['label'],addedMemberCount=len(o['added_members']),addedLengthM=sum(b['length_mm'] for b in o['added_members'])/1000,cases=cases,lateralElasticProbe=lateral,collisionCheck=dict(method='Oriented member convex footprint and Z interval vs RC and 3mm tread surfaces; welded member intersections need connection detailing',collisions=collisions))
 # Local B03 and guardrail sensitivity: analytical simple beam/cantilever, separate from frame solver.
 local=[]
 for t in [1.6,1.7,2.,2.3]:
  I=(40**4-(40-2*t)**4)/12;S=I/20;span=550.;q=9.8*.115;point=1.6*1334;M=max(q*span**2/8,1.2*1.5*.115*span**2/8+point*span/4);delta=max(5*6.5*.115*span**4/(384*200000*I),5*1.5*.115*span**4/(384*200000*I)+1334*span**3/(48*200000*I))
  railM=890*1100.;railDelta=890*1100**3/(3*200000*I)
  local.append(dict(shsThickness=t,stairB03SpanMm=span,stairB03GrossBendingMPa=M/S,stairB03DeflectionMm=delta,guardHeightMm=1100,guardPointN=890,guardGrossBendingMPa=railM/S,guardDeflectionMm=railDelta,guardTargetMm=11,guardDeflectionScreenExceeded=railDelta>11,note='Nominal sharp-corner section, Fy235; no local-buckling/connection capacity. Deck3mm must verify load patch, folds and local plate response separately.'))
 output['localShsScreen']=local
 I60=(60**4-(60-2*2.3)**4)/12
 output['guardNextStudy']=dict(optionA=dict(proposal='SHS60x60x2.3 guardpost',pointN=890,heightMm=1100,grossStressMPa=890*1100/(I60/30),deflectionMm=890*1100**3/(3*200000*I60)),optionC=dict(proposal='RetainSHS40x40 with verified knee-brace/continuous rail load path; illustrative restrained height700mm leaves400mm cantilever',freeTipMm=400,deflectionFormula='P*400^3/(3EI), only if lower restraint stiffness and bracing connection capacity proved'),status='Not adopted in drawings/RAB; original guard stiffness failure remains open, deck3mm patch-load/fold check also open')
 (OUT/'analysis.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
 for name,o in output['options'].items():print(name,[(c['rhsThickness'],round(c['serviceMaxDisplacementMm'],3),round(c['peakGrossStress']['grossVonMisesScreenMPa'],1),round(c['stairPeakGrossStress']['grossVonMisesScreenMPa'],1)) for c in o['cases']])
 return output
if __name__=='__main__':
 import sys
 if '--analyse' in sys.argv:analyse()
 else:spec()
