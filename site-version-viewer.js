// Runs inside the existing 3D renderer closure: camera and picking stay shared.
const versionBaseline=GROUPS.map(g=>({boxes:g.boxes.slice(),name:g.name,mat:g.mat,prof:g.prof,note:g.note}));
const sameBox=(b,v)=>b.length===24&&b.every((x,i)=>Math.abs(x-v[i])<.001);
let versionSources=new Map();
window.MettaModelVersion={
 source(box){return versionSources.get(box);},
 thickness(rhs,shs){
  for(const id of ['kolom','balok','stiffener','bracing'])G[id].prof=`RHS 50 × 100 × ${rhs} mm`+(id==='stiffener'?' / pengaku tangga SHS 40 × 40 × '+shs+' mm':'');
  G.railing.prof='SHS 40 × 40 × '+shs+' mm';
  if(sel!==null)showPick(GROUPS[pieceRefs[sel]?.g]);
 },
 apply(version,data,mesh={wire_mm:2,opening_label_mm:25}){
  versionSources=new Map();
  stopExplosion();isolated=null;sel=null;showPick(null);
  GROUPS.forEach((g,i)=>Object.assign(g,versionBaseline[i],{boxes:versionBaseline[i].boxes.slice()}));
  if(version==='v2'){
   const removed=new Set(data.remove_ids),removeBoxes=[...REVISED,...FINISH_GEOMETRY].filter(e=>removed.has(e.id)).map(e=>({group:e.group,v:e.vertices.flat()}));
   for(const g of GROUPS){if(data.clear_groups.includes(g.id))g.boxes=[];else g.boxes=g.boxes.filter(b=>!removeBoxes.some(e=>e.group===g.id&&sameBox(b,e.v)));}
   // Rebuild retained deck using the original concrete-void clipping function.
   REVISED.filter(e=>e.group==='dek'&&!removed.has(e.id)).forEach(e=>{const a=e.vertices[0],b=e.vertices[6];Bcut('dek',...a,b[0]-a[0],b[1]-a[1],b[2]-a[2]);});
   for(const e of data.items){G[e.group].boxes.push(e.box);versionSources.set(e.box,{id:e.id,mark:'R08 / usulan koordinasi'});}
   // True open mesh: individual wire solids, not a filled opaque side plate.
   const wire=mesh.wire_mm,pitch=mesh.opening_label_mm+wire;
   for(const p of data.mesh){
    const [a,y,z,A,Y,Z]=p.bounds,x=(a+A)/2,W=Y-y,H=Z-z,left=x<1000,face=x+(left?-22:22);
    const put=(b)=>G.skirt.boxes.push(b);
    put([x-20,y,z,40,W,40]);put([x-20,y,Z-40,40,W,40]);
    put([x-20,y,z+40,40,40,H-80]);put([x-20,Y-40,z+40,40,40,H-80]);
    for(let yy=y+20;yy<=Y-20+.001;yy+=pitch)put([face-wire/2,yy-wire/2,z+20,wire,wire,H-40]);
    for(let zz=z+20;zz<=Z-20+.001;zz+=pitch)put([face-wire/2,y+20,zz-wire/2,wire,W-40,wire]);
    const clampX=face+(left?-3:0);
    put([clampX,y+20,z+20,3,W-40,30]);put([clampX,y+20,Z-50,3,W-40,30]);
    put([clampX,y+20,z+20,3,30,H-40]);put([clampX,Y-50,z+20,3,30,H-40]);
   }
   Object.assign(G.skirt,{name:'Mesh sisi + rangka panel',mat:'Kawat loket galvanis; rangka SHS dan strip penjepit',prof:`Lubang ${mesh.opening_label_mm} / kawat ${wire} mm`,note:'R08: penutup sisi, bukan pengganti railing atau bracing.'});
   G.tangga.prof=`R08 / ${data.stair_panels} panel tekuk 3 mm`;G.baseplate.note=`V2: 80 dudukan lama + ${data.new_posts} base dan angkur infill usulan. Kapasitas lantai belum disahkan.`;
   for(const k of ['kolom','balok','stiffener'])G[k].note='V2 / geometri arsip + rangka R08 usulan. Penyangga tangga termasuk; profil tiap komponen mengikuti RAB.';
  }
  GROUPS.forEach((g,i)=>{const label=leg.children[i];if(label)label.lastElementChild.textContent=g.name;});
  cv.dataset.siteVersion=version;cv.dataset.stairPanels=String(version==='v2'?data.stair_panels:data.old_stair_panels);cv.dataset.infillColumns=String(version==='v2'?data.new_posts:0);
  dirty=true;if(booted){resize();draw();}
 }
};
