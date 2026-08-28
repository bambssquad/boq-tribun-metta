# -*- coding: utf-8 -*-
"""Blok HTML + JS untuk viewer 3D interaktif (canvas 2D, painter's algorithm)."""

HTML_3D = """
<section class="block rv" id="tiga-d">
  <div class="stage-wrap">
  <h2>Model 3D interaktif</h2>
  <p class="lede">Seret untuk memutar, scroll untuk zoom, geser slider untuk meledakkan struktur
  per lapis. Klik batang atau pelat mana pun — keterangan material, profil, dan beratnya muncul
  di panel kanan.</p>

  <div class="v3">
    <div class="v3-stage">
      <canvas id="cv3" aria-label="Model 3D tribun"></canvas>
      <div class="v3-hud">
        <span id="hudCount">—</span>
      </div>
    </div>

    <button class="sheet-toggle" id="sheetTgl" aria-expanded="false" aria-controls="v3side">
      <span class="grip"></span><span id="sheetTglTxt">Kontrol &amp; material</span></button>

    <aside class="v3-side" id="v3side">
      <div class="v3-card" id="pick">
        <div class="pk-eyebrow">Klik elemen di model</div>
        <div class="pk-name">Belum ada yang dipilih</div>
        <dl class="pk-dl"></dl>
      </div>

      <div class="v3-card">
        <div class="pk-eyebrow">Ledakan struktur</div>
        <input type="range" id="ex" min="0" max="100" value="0" aria-label="Jarak ledak">
        <div class="v3-row"><button class="mini" data-ex="0">Rakit</button>
          <button class="mini" data-ex="45">Setengah</button>
          <button class="mini" data-ex="100">Penuh</button></div>
      </div>

      <div class="v3-card">
        <div class="pk-eyebrow">Lapis</div>
        <div id="legend" class="legend"></div>
      </div>

      <div class="v3-card">
        <div class="pk-eyebrow">Tampilan permukaan</div>
        <label class="lg" id="texTgl"><input type="checkbox" id="texCb">
          <span class="sw" style="background:linear-gradient(45deg,#8d949c 25%,transparent 25%,transparent 50%,#8d949c 50%,#8d949c 75%,transparent 75%)"></span>
          <span>Tekstur bordes (motif kembang)</span></label>
      </div>

      <div class="v3-card">
        <div class="pk-eyebrow">Konteks bangunan</div>
        <div class="v3-row"><button class="mini" id="ctxOn">Tampilkan</button>
          <button class="mini" id="ctxOff">Sembunyikan</button></div>
      </div>

      <div class="v3-card">
        <div class="pk-eyebrow">Sudut pandang</div>
        <div class="v3-row"><button class="mini" data-view="iso">Isometri</button>
          <button class="mini" data-view="depan">Depan</button>
          <button class="mini" data-view="samping">Samping</button>
          <button class="mini" data-view="atas">Atas</button></div>
      </div>
    </aside>
  </div>
  </div>
</section>
"""

CSS_3D = ""

JS_3D = r"""
(function(){
const SPAN=17700, DEPTH=5000, TIERS=5, TIER_D=1000, RISER=500;
const PORTAL=[0,1770,3540,7080,8850,10620,14160,15930,17700];
const ROWS=[0,1000,2000,3000,4000,5000];
const AB=[4850,6850], SC=[12250,12850];
const SEG=[[0,4850],[6850,12250],[12850,17700]];
const ST_R=167, ST_T=267, ST_N=3;
const colTop=y=> y>=5000?2500:Math.floor(y/TIER_D)*RISER+RISER;

const GROUPS=[
 {id:'baseplate',lay:-1,name:'Base plate + karet',
  mat:'Pelat baja 8 mm + karet 10 mm',prof:'150 × 150 × 8 + karet 10 mm',
  note:'Tumpuan sendi, duduk lepas tanpa angkur ke lantai',key:'bp'},
 {id:'kolom',lay:0,name:'Kolom tribun',
  mat:'Baja BJ 37 — hollow hitam',prof:'50 × 100 × 2,3 mm · lonjor 6 m',
  note:'5,25 kg/m · gaya 12,8 kN · rasio 0,23 (tekuk λ=118)',key:'col'},
 {id:'balok',lay:0,name:'Balok tepi tier',
  mat:'Baja BJ 37 — hollow hitam',prof:'50 × 100 × 2,3 mm · lonjor 6 m',
  note:'Bentang 1.770 mm · σ 87 MPa · lendutan L/962 · rasio 0,54',key:'beam'},
 {id:'stiffener',lay:0,name:'Stiffener dek',
  mat:'Baja BJ 37 — hollow hitam',prof:'50 × 100 × 2,3 mm — sama dengan balok',
  note:'Bentang plat dek 1.000 → 500 mm · σ 96 MPa · rasio 0,60 · dudukan rata tanpa ganjal',key:'stf'},
 {id:'bracing',lay:0,name:'Bracing X',
  mat:'Baja BJ 37 — hollow',prof:'40 × 40 × 2 mm',note:'4 bay belakang + 2 panel tiap sisi ujung',key:'brc'},
 {id:'dek',lay:1,tex:1,name:'Plat dek',
  mat:'Pelat bordes anti-slip',prof:'tebal 8 mm · lembar 4ft × 8ft, 192 kg',
  note:'64,6 kg/m² · bentang 500 mm · σ 25 MPa · lendutan L/926',key:'dek'},
 {id:'pinus',lay:2,name:'Papan dudukan',
  mat:'Kayu pinus',prof:'400 × 40 mm',note:'Satu papan di muka tiap tier',key:'pin'},
 {id:'tangga',lay:3,tex:1,name:'Anak tangga',
  mat:'Pelat tekuk bordes anti-slip',prof:'tebal 4 mm',
  note:'3 optrede 167 + 3 antrede 267 per tier · panel 267×700 σ maks 111 MPa, lendutan 1,65 mm',key:'stp'},
 {id:'nosing',lay:3,name:'Nosing kontras',
  mat:'Cat epoxy kuning kontras',prof:'lebar 50 mm — rata, tidak menonjol',
  note:'Dicat di atas motif bordes; sengaja bukan strip agar tidak jadi titik sandung',key:'nos'},
 {id:'beton',lay:0,fixed:true,alpha:0.5,name:'Kolom beton eksisting',
  mat:'Beton bertulang gedung',prof:'600 × 500 mm',
  note:'4 kolom menembus tribun — dikelilingi void 50 mm, tidak boleh dipotong',key:'cnc'},
 {id:'void',lay:1,name:'Kerah void 50 mm',
  mat:'Pelat penutup celah 8 mm',prof:'lebar 50 mm keliling',
  note:'Menutup celah 50 mm antara dek dan kolom beton di permukaan injak',key:'vd'},
 {id:'anchor',lay:0,name:'Strut anchor ke kolom beton',
  mat:'Baja BJ 37 — hollow hitam',prof:'50 × 100 × 2,3 mm — sama profil rangka',
  note:'16 titik · pelat 6 mm + 2× dynabolt M10 · gaya 2,1 kN/titik · rasio 0,13',key:'anc'},
 {id:'dinding',lay:0,fixed:true,alpha:0.72,name:'Dinding gym (konteks)',
  mat:'Beton plester, cat eksisting',prof:'melengkung R 165 m · tebal 200 mm',
  note:'Tribun berdiri lepas, jarak bersih minimal 200 mm ke dinding',key:'wl'},
 {id:'jendela',lay:0,fixed:true,alpha:0.45,name:'Kaca jendela gym',
  mat:'Kaca bening pada kusen aluminium',prof:'pias 1.475 × 1.150 mm',
  note:'Konteks — tidak boleh tertutup sandaran tribun',key:'wn'},
 {id:'sandaran',lay:4,name:'Rangka sandaran',
  mat:'Baja BJ 37 — hollow, cat hitam doff',prof:'tiang & rail 60 × 60 mm',
  note:'Tiang @1.475 mm, rail atas +3.600 dan rail bawah +2.500',key:'snd'},
 {id:'sandkayu',lay:4,name:'Panel kayu sandaran',
  mat:'Papan kayu pinus — type SANDARAN PINEWOOD 40mm',prof:'tebal 40 mm · tinggi 1.000 mm',
  note:'Menerus A–C mengikuti busur dinding, offset 200 mm dari tembok',key:'sndk'},
 {id:'kusen',lay:0,fixed:true,name:'Kusen jendela gym',
  mat:'Aluminium eksisting',prof:'kusen 60 mm + mullion',
  note:'Konteks — pembagi pias jendela dinding gym',key:'ksn'},
 {id:'riser',lay:1,name:'Penutup muka tier & samping',
  mat:'Pelat polos 2 mm, tekuk tepi 20 mm',prof:'tinggi 500 mm per tier · panel ujung mengikuti profil tier',
  note:'Non-struktural — menutup muka tier dan sisi ujung kiri-kanan',key:'ris'},
 {id:'skirt',lay:1,name:'Penutup kolong & toe-board',
  mat:'Pelat polos 2 mm, tekuk tepi 20 mm',prof:'skirt tinggi 500 mm · toe-board 100 mm',
  note:'Skirt menutup kolong tribun; toe-board menahan barang jatuh di tepi dek & jalur tangga',key:'skt'},
 {id:'railing',lay:4,name:'Balustrade & railing',
  mat:'Baja BJ 37 — hollow',prof:'baluster 40×40×2,8 · rail 40×40×2',
  note:'Celah bersih ≤100 mm, anti-panjat',key:'rail'},
];
const G={}; GROUPS.forEach(g=>{g.boxes=[];G[g.id]=g;});
const B=(g,x,y,z,dx,dy,dz)=>G[g].boxes.push([x,y,z,dx,dy,dz]);

// kolom beton eksisting + lubang (void 50 mm keliling) yang harus dihindari pelat & balok
const CONC=[[-150,2938],[5850,2938],[11850,2938],[17850,2938]];
const VOID=50;
const CUT=CONC.map(([cx,cy])=>[cx-300-VOID, cy-250-VOID, cx+300+VOID, cy+250+VOID]);
function Bcut(g,x,y,z,dx,dy,dz){
  let parts=[[x,y,dx,dy]];
  CUT.forEach(([x0,y0,x1,y1])=>{
    const out=[];
    parts.forEach(([px,py,pdx,pdy])=>{
      const ax=px, ay=py, bx=px+pdx, by=py+pdy;
      if(x1<=ax||x0>=bx||y1<=ay||y0>=by){ out.push([px,py,pdx,pdy]); return; }
      if(y0>ay) out.push([ax,ay,pdx,y0-ay]);
      if(y1<by) out.push([ax,y1,pdx,by-y1]);
      const m0=Math.max(ay,y0), m1=Math.min(by,y1);
      if(x0>ax) out.push([ax,m0,x0-ax,m1-m0]);
      if(x1<bx) out.push([x1,m0,bx-x1,m1-m0]);
    });
    parts=out;
  });
  parts.forEach(q=>{ if(q[2]>1&&q[3]>1) B(g,q[0],q[1],z,q[2],q[3],dz); });
}

// base plate
const BP=(x,y)=>{B('baseplate',x-75,y-75,-18,150,150,10); B('baseplate',x-75,y-75,-8,150,150,8);};
PORTAL.forEach(x=>ROWS.forEach(y=>BP(x,y)));
[AB[0],AB[1],SC[0],SC[1]].forEach(x=>ROWS.slice(0,5).forEach(y=>BP(x,y)));
// kolom
PORTAL.forEach(x=>ROWS.forEach(y=>B('kolom',x-25,y-50,0,50,100,colTop(y))));
[AB[0],AB[1],SC[0],SC[1]].forEach(x=>ROWS.slice(0,5).forEach(y=>B('kolom',x-25,y-50,0,50,100,colTop(y))));
// balok + stiffener
for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z=t*RISER;
  SEG.forEach(([a,b])=>{Bcut('balok',a,yf-25,z-100,b-a,50,100);
                        Bcut('stiffener',a,yf+TIER_D/2-25,z-100,b-a,50,100);});}
SEG.forEach(([a,b])=>Bcut('balok',a,DEPTH-25,2500-100,b-a,50,100));
// bracing (batang miring didekati sbg rangkaian kubus kecil)
function diag(x1,y1,z1,x2,y2,z2,w){
  const n=26; for(let i=0;i<n;i++){const u=i/n;
    B('bracing',x1+(x2-x1)*u-w/2, y1+(y2-y1)*u-w/2, z1+(z2-z1)*u, w,w, Math.abs(z2-z1)/n+w);}}
[[0,1770],[3540,5310],[8850,10620],[15930,17700]].forEach(([a,b])=>{
  diag(a,DEPTH,0,b,DEPTH,2500,40); diag(b,DEPTH,0,a,DEPTH,2500,40);});
// bracing sisi diganti ikatan langsung ke kolom beton ujung (lihat catatan)
// dek + pinus
for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D,z=t*RISER;
  SEG.forEach(([a,b])=>{Bcut('dek',a,yf,z,b-a,TIER_D,8);
                        Bcut('pinus',a,yf,z+8,b-a,400,40);});}
// tangga + nosing
[AB,SC].forEach(([a,b])=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z0=t*RISER-RISER;
    for(let k=0;k<ST_N;k++){const y0=yf+k*ST_T, w=(k<ST_N-1)?ST_T:TIER_D-2*ST_T;
      B('tangga',a,y0,z0+(k+1)*ST_R,b-a,w,4);
      B('tangga',a,y0-4,z0+k*ST_R,b-a,4,ST_R);
      B('nosing',a,y0,z0+(k+1)*ST_R+4,b-a,50,1);}}});
// kolom beton eksisting (600 x 500) + kerah void + strut anchor
CONC.forEach(([cx,cy])=>B('beton',cx-300,cy-250,-200,600,500,3800));
// kerah void 50 mm di dek yang ditembus kolom beton
CONC.forEach(([cx,cy])=>{
  [1500,2000].forEach(z=>{
    const x0=Math.max(0,cx-350),x1=Math.min(SPAN,cx+350),y0=cy-300,y1=cy+300;
    if(x1-x0<80) return;
    if(cx>AB[0]&&cx<AB[1]) return;
    B('void',x0,y0,z,x1-x0,50,6);
    B('void',x0,y1-50,z,x1-x0,50,6);
    if(cx-350>=0) B('void',x0,y0+50,z,50,y1-y0-100,6);
    if(cx+350<=SPAN) B('void',x1-50,y0+50,z,50,y1-y0-100,6);
  });
});
// strut anchor: 2 kolom dalam x 2 level x 3 arah
[[5850,2938],[11850,2938]].forEach(([cx,cy])=>{
  [1000,2000].forEach(z=>{
    B('anchor',cx-300-700,cy-25,z-50,700,50,100);
    B('anchor',cx+300,cy-25,z-50,700,50,100);
    B('anchor',cx-25,cy+250,z-50,50,700,100);
  });
});
// ikatan rangka ujung ke kolom beton ujung (pengganti bracing sisi)
[0,SPAN].forEach(x=>{[1000,2000].forEach(z=>{
  B('anchor',x-25,2638,z-50,50,312,100);});});
// dinding gym melengkung (busur R 165 m -> sagitta 237 mm) + jendela + sandaran
const R=165000, SAG=237;
const wallY=x=>{const u=(x-SPAN/2)/ (SPAN/2); return DEPTH+520+SAG*(1-u*u);};
const NSEG=24;
for(let i=0;i<NSEG;i++){
  const x0=SPAN*i/NSEG, x1=SPAN*(i+1)/NSEG, w=x1-x0;
  const yy=wallY((x0+x1)/2);
  B('dinding',x0,yy,0,w,200,4600);
  // pias jendela: 2 baris, tiap segmen satu daun, dengan kusen + mullion tengah
  [1500,3000].forEach(z=>{
    const gx=x0+60, gw=w-120, gy=yy-34, gd=68;
    B('kusen',gx-60,gy,z-60,gw+120,gd,60);            // ambang bawah
    B('kusen',gx-60,gy,z+1150,gw+120,gd,60);          // ambang atas
    B('kusen',gx-60,gy,z,60,gd,1150);                 // tiang kusen kiri
    B('kusen',gx+gw,gy,z,60,gd,1150);                 // tiang kusen kanan
    B('kusen',gx+gw/2-25,gy,z,50,gd,1150);            // mullion tengah
    B('jendela',gx,yy-30,z,gw/2-25,60,1150);
    B('jendela',gx+gw/2+25,yy-30,z,gw/2-25,60,1150);
  });
}
// sandaran belakang menerus, offset 200 mm dari muka dinding
for(let i=0;i<NSEG;i++){
  const x0=SPAN*i/NSEG, x1=SPAN*(i+1)/NSEG, w=x1-x0;
  const yy=wallY((x0+x1)/2)-200-60;
  B('sandkayu',x0,yy+10,2560,w,40,1000);              // panel papan kayu 40 mm
  B('sandaran',x0,yy,3560,w,60,40);                    // rail penutup atas
  B('sandaran',x0,yy,2500,w,60,60);                    // rail bawah
  if(i%2===0) B('sandaran',x0,yy,2500,60,60,1100);     // tiang @1475 mm
}
// railing
[0,SPAN].forEach(x=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D,z=t*RISER;
    for(let i=0;i<=10;i++){const yy=yf+i*100; if(yy>yf+TIER_D)break;
      B('railing',x-20,yy-20,z,40,40,1100);}
    B('railing',x-20,yf,z+1060,40,TIER_D,40);
    B('railing',x-20,yf,z+510,40,TIER_D,40);}});

// penutup muka tier (plat riser 2 mm) + panel samping ujung
for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z0=(t-1)*RISER;
  SEG.forEach(([a,b])=>Bcut('riser',a,yf-2,z0,b-a,2,RISER));}
[0,SPAN].forEach((x,i)=>{const xo = i===0 ? -2 : 0;
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D;
    Bcut('riser',x+xo,yf,0,2,TIER_D,t*RISER);}});
// skirt kolong: menutup rongga di bawah dek pada sisi jalur tangga
[AB,SC].forEach(([a,b])=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z=t*RISER;
    B('skirt',a-2,yf,z-RISER,2,TIER_D,RISER);
    B('skirt',b,yf,z-RISER,2,TIER_D,RISER);}});
// skirt kolong sisi belakang (di bawah tier 5 sampai dinding)
SEG.forEach(([a,b])=>B('skirt',a,DEPTH-2,0,b-a,2,2500));
// toe-board 100 mm di tepi dek: ujung kiri-kanan + kedua sisi tiap jalur tangga
[[0,-2],[SPAN,0],[AB[0],-2],[AB[1],0],[SC[0],-2],[SC[1],0]].forEach(([x,d])=>{
  for(let t=1;t<=TIERS;t++){const yf=(t-1)*TIER_D, z=t*RISER;
    B('skirt',x+d,yf,z+8,2,TIER_D,100);}});

const cv=document.getElementById('cv3'), ctx=cv.getContext('2d');
let az=0.62, el=0.60, zoom=1, ox=0, oy=0, ex=0;
const CX=SPAN/2, CY=DEPTH/2, CZ=1100;
const LAYZ=[0,2600,5200,7800,10400]; // offset ledak per lapis (dikali ex)
const LAYBP=-2600;

function palette(){
  const cs=getComputedStyle(document.documentElement);
  const g=n=>cs.getPropertyValue(n).trim();
  return {steel:g('--steel'),ink:g('--ink'),accent:g('--accent'),dim:g('--dim'),
          line:g('--line'),paper:g('--paper'),muted:g('--muted')};
}
let P=palette();
// warna konteks dipatok, bukan diambil dari palet baja, supaya material terbaca
const MAT={dinding:'#8C8478', jendela:'#4E7FA6', kusen:'#9AA1A6', sandkayu:'#B07C42',
           pinus:'#C08A45'};
const BASE=()=>({baseplate:P.accent,kolom:P.steel,balok:P.steel,stiffener:P.steel,
  bracing:P.accent,dek:P.steel,pinus:MAT.pinus,tangga:P.dim,nosing:P.accent,railing:P.steel,
  beton:P.muted,void:P.dim,anchor:P.dim,dinding:MAT.dinding,jendela:MAT.jendela,
  kusen:MAT.kusen,sandkayu:MAT.sandkayu,sandaran:P.steel,riser:P.steel,skirt:P.steel});
const TINT={baseplate:0.95,kolom:1.0,balok:0.72,stiffener:1.25,bracing:1.0,
  dek:1.55,pinus:1.0,tangga:1.0,nosing:1.35,railing:1.3,
  beton:1.35,void:1.35,anchor:0.85,dinding:1.0,jendela:1.15,kusen:1.0,
  sandkayu:1.0,sandaran:0.85,riser:0.62,skirt:0.5};
const COLOR=()=>{const b=BASE(),o={};for(const k in b) o[k]=shade(b[k],TINT[k]);return o;};

const _sc=document.createElement('canvas').getContext('2d');
function shade(hex,f){
  const c=_sc; c.fillStyle=hex;
  const h=c.fillStyle; let r,g,b;
  if(h.startsWith('#')){const v=h.length===4?h.replace(/#(.)(.)(.)/,'#$1$1$2$2$3$3'):h;
    r=parseInt(v.substr(1,2),16);g=parseInt(v.substr(3,2),16);b=parseInt(v.substr(5,2),16);}
  else{const m=h.match(/[\d.]+/g);r=+m[0];g=+m[1];b=+m[2];}
  const mix=(x)=>Math.max(0,Math.min(255,Math.round(x*f)));
  return `rgb(${mix(r)},${mix(g)},${mix(b)})`;
}
function project(x,y,z,W,H,S){
  const ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el);
  const X=(x-CX), Y=(y-CY), Z=(z-CZ);
  const x1=X*ca-Y*sa, y1=X*sa+Y*ca;
  return [W/2+ox+x1*S, H/2+oy-(y1*se+Z*ce)*S, y1*ce-Z*se];
}
const FACES=[[0,1,2,3],[4,5,6,7],[0,1,5,4],[3,2,6,7],[0,3,7,4],[1,2,6,5]];
const LUM=[0.52,1.0,0.88,0.70,0.80,0.64];
let sel=null;
const COARSE = matchMedia('(pointer:coarse)').matches;
let texOn = !COARSE;

// LUT warna: 16 grup x 6 muka, dihitung sekali per perubahan palet — bukan per muka per frame
let FILL=[], FILLSEL=[];
function makeLUT(){
  const C=COLOR(); FILL=[]; FILLSEL=[];
  GROUPS.forEach(g=>{
    const base=C[g.id];
    FILL.push(LUM.map(l=>shade(base,l)));
    FILLSEL.push(LUM.map(l=>shade(base,Math.min(1.4,l*1.55))));
  });
}
makeLUT();

// Geometri dunia disimpan datar; hanya dibangun ulang saat ledak / lapis berubah.
let WX,WY,WZ,PX,PY,DEP,ORD,BG,NB=0,dirty=true;
function rebuild(){
  const gi=[],bx=[];
  GROUPS.forEach((g,k)=>{
    if(g.off) return;
    const dz=g.fixed?0:(g.lay<0?LAYBP:LAYZ[g.lay])*(ex/100);
    g.boxes.forEach(b=>{gi.push(k); bx.push([b[0],b[1],b[2]+dz,b[3],b[4],b[5]]);});
  });
  NB=gi.length;
  WX=new Float32Array(NB*8); WY=new Float32Array(NB*8); WZ=new Float32Array(NB*8);
  PX=new Float32Array(NB*8); PY=new Float32Array(NB*8);
  DEP=new Float32Array(NB); ORD=new Int32Array(NB); BG=new Int16Array(NB);
  for(let i=0;i<NB;i++){
    const b=bx[i], o=i*8, x=b[0],y=b[1],z=b[2],dx=b[3],dy=b[4],dh=b[5];
    WX[o]=x;   WY[o]=y;    WZ[o]=z;
    WX[o+1]=x+dx;WY[o+1]=y; WZ[o+1]=z;
    WX[o+2]=x+dx;WY[o+2]=y+dy;WZ[o+2]=z;
    WX[o+3]=x;   WY[o+3]=y+dy;WZ[o+3]=z;
    for(let k=0;k<4;k++){WX[o+4+k]=WX[o+k];WY[o+4+k]=WY[o+k];WZ[o+4+k]=z+dh;}
    BG[i]=gi[i];
  }
  dirty=false;
}

function draw(){
  if(dirty) rebuild();
  const W=cv.width,H=cv.height;
  const ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el);
  const spread=(10400+2600)*(ex/100);
  const vert=DEPTH*Math.sin(el)+(2500+spread+1100)*Math.cos(el);
  const horiz=(SPAN+DEPTH)*0.72;
  const S=Math.min(W/(horiz*1.12), H/(vert*1.22))*zoom;
  const cx=W/2+ox, cy=H/2+oy;
  for(let i=0;i<NB;i++){
    const o=i*8; let d=0;
    for(let k=0;k<8;k++){
      const X=WX[o+k]-CX, Y=WY[o+k]-CY, Z=WZ[o+k]-CZ;
      const x1=X*ca-Y*sa, y1=X*sa+Y*ca;
      PX[o+k]=cx+x1*S; PY[o+k]=cy-(y1*se+Z*ce)*S; d+=y1*ce-Z*se;
    }
    DEP[i]=d*0.125; ORD[i]=i;
  }
  ORD.sort((a,b)=>DEP[b]-DEP[a]);

  ctx.clearRect(0,0,W,H);
  const edges = !lowQ && zoom>0.85;
  let alpha=1; ctx.globalAlpha=1;
  for(let n=0;n<NB;n++){
    const i=ORD[n], o=i*8, g=GROUPS[BG[i]];
    const a=(g.alpha!==undefined)?g.alpha:1;
    if(a!==alpha){ctx.globalAlpha=a; alpha=a;}
    const isSel = sel===i, lut = isSel?FILLSEL[BG[i]]:FILL[BG[i]];
    for(let fi=0;fi<6;fi++){
      const f=FACES[fi];
      const x0=PX[o+f[0]],y0=PY[o+f[0]],x1=PX[o+f[1]],y1=PY[o+f[1]],
            x2=PX[o+f[2]],y2=PY[o+f[2]],x3=PX[o+f[3]],y3=PY[o+f[3]];
      if(x0*y1-x1*y0 + x1*y2-x2*y1 + x2*y3-x3*y2 + x3*y0-x0*y3 >= 0) continue;
      ctx.beginPath(); ctx.moveTo(x0,y0); ctx.lineTo(x1,y1); ctx.lineTo(x2,y2); ctx.lineTo(x3,y3);
      ctx.closePath();
      ctx.fillStyle=lut[fi]; ctx.fill();
      if(texOn && g.tex && fi===1 && !lowQ){
        // motif kembang digambar di ruang muka: dua vektor tepi, satu jalur, satu stroke
        const ux=(x1-x0), uy=(y1-y0), vx=(x3-x0), vy=(y3-y0);
        const lu=Math.hypot(ux,uy), lv=Math.hypot(vx,vy);
        if(lu>26 && lv>10){
          const nu=Math.min(40,Math.max(2,Math.round(lu/14))), nv=Math.min(14,Math.max(1,Math.round(lv/14)));
          ctx.beginPath();
          for(let a=0;a<nu;a++)for(let b2=0;b2<nv;b2++){
            const su=(a+0.5)/nu, sv=(b2+0.5)/nv, sk=((a+b2)%2)?0.18:-0.18;
            const px=x0+ux*su+vx*sv, py=y0+uy*su+vy*sv;
            const dx2=(ux/nu)*0.34+(vx/nv)*sk, dy2=(uy/nu)*0.34+(vy/nv)*sk;
            ctx.moveTo(px-dx2,py-dy2); ctx.lineTo(px+dx2,py+dy2);
          }
          ctx.strokeStyle='rgba(0,0,0,.30)'; ctx.lineWidth=0.9; ctx.stroke();
        }
      }
      if(edges||isSel){ctx.strokeStyle=isSel?P.accent:'rgba(255,255,255,.13)';
        ctx.lineWidth=isSel?1.6:0.5; ctx.stroke();}
    }
  }
  ctx.globalAlpha=1;
  hud.textContent = NB+' elemen · ledak '+ex+'% · zoom '+zoom.toFixed(2)+'×';
}
const hud=document.getElementById('hudCount');

// satu gambar per frame layar, bukan per event pointer.
// rAF bisa tidak pernah dijalankan kalau halaman dimuat di latar atau di-prerender,
// jadi selalu disiapkan jaring pengaman berbasis timer.
let pend=0, guard=0;
function render(){
  if(pend) return;
  pend=requestAnimationFrame(()=>{pend=0; clearTimeout(guard); guard=0; draw();});
  if(!guard) guard=setTimeout(()=>{
    guard=0;
    if(pend){ cancelAnimationFrame(pend); pend=0; draw(); }
  }, 400);
}
function reflow(){ dirty=true; render(); }

let lowQ=false, qTimer=0;
function resize(){
  const r=cv.parentElement.getBoundingClientRect();
  const full=Math.min(2,window.devicePixelRatio||1);
  const dpr=lowQ?Math.min(1,full):full;
  const w=Math.round(r.width*dpr), h=Math.round(r.height*dpr);
  if(cv.width!==w||cv.height!==h){cv.width=w; cv.height=h;}
  cv.style.width=r.width+'px'; cv.style.height=r.height+'px';
  if(booted) draw(); else render();
}
// saat diputar/di-pinch, turunkan resolusi piksel — di HP ini bedanya 4-9x jumlah piksel
function quality(low){
  clearTimeout(qTimer);
  if(low){ if(!lowQ){lowQ=true; resize();} }
  else qTimer=setTimeout(()=>{lowQ=false; resize();},170);
}
let rTimer=0;
window.addEventListener('resize',()=>{clearTimeout(rTimer);rTimer=setTimeout(resize,120);});

// interaksi — rotasi 1 jari, pinch 2 jari, geser dengan Shift / dua jari
const stage=cv.parentElement;
const pts=new Map();
let moved=0, pinch0=0, zoom0=1, mid0=null;
function mid(){ const a=[...pts.values()];
  return {x:(a[0].x+a[1].x)/2, y:(a[0].y+a[1].y)/2,
          d:Math.hypot(a[0].x-a[1].x, a[0].y-a[1].y)}; }

stage.addEventListener('pointerdown',e=>{
  pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
  stage.setPointerCapture(e.pointerId);
  if(pts.size===1){moved=0; stage.classList.add('drag'); quality(true);}
  if(pts.size===2){const m=mid(); pinch0=m.d; zoom0=zoom; mid0={x:m.x,y:m.y};}
});
stage.addEventListener('pointermove',e=>{
  const p=pts.get(e.pointerId); if(!p) return;
  const dx=e.clientX-p.x, dy=e.clientY-p.y;
  p.x=e.clientX; p.y=e.clientY;
  if(pts.size>=2){
    const m=mid();
    if(pinch0>8){ zoom=Math.max(0.35,Math.min(6, zoom0*(m.d/pinch0))); }
    ox+=(m.x-mid0.x); oy+=(m.y-mid0.y); mid0={x:m.x,y:m.y};
    quality(true); render(); return;
  }
  moved+=Math.abs(dx)+Math.abs(dy);
  if(e.shiftKey){ox+=dx;oy+=dy;}
  else {az+=dx*0.006; el=Math.max(0.05,Math.min(1.45,el+dy*0.005));}
  quality(true); render();
});
function up(e){
  const had=pts.size;
  pts.delete(e.pointerId);
  if(pts.size<2) pinch0=0;
  if(pts.size===0){
    stage.classList.remove('drag'); quality(false);
    if(had===1 && moved<5) pick(e);
  }
}
stage.addEventListener('pointerup',up);
stage.addEventListener('pointercancel',up);
stage.addEventListener('wheel',e=>{e.preventDefault();
  zoom=Math.max(0.35,Math.min(6,zoom*(e.deltaY<0?1.12:1/1.12)));
  quality(true); quality(false); render();},{passive:false});

function pick(e){
  const r=cv.getBoundingClientRect();
  const dpr=cv.width/r.width;
  const mx=(e.clientX-r.left)*dpr, my=(e.clientY-r.top)*dpr;
  for(let n=NB-1;n>=0;n--){
    const i=ORD[n], o=i*8;
    for(let fi=0;fi<6;fi++){
      const f=FACES[fi];
      const q=[[PX[o+f[0]],PY[o+f[0]]],[PX[o+f[1]],PY[o+f[1]]],
               [PX[o+f[2]],PY[o+f[2]]],[PX[o+f[3]],PY[o+f[3]]]];
      let a=0; for(let k=0;k<4;k++){const j=(k+1)%4; a+=q[k][0]*q[j][1]-q[j][0]*q[k][1];}
      if(a>=0) continue;
      if(inside(mx,my,q)){ sel=i; showPick(GROUPS[BG[i]]); render(); return; }
    }
  }
  sel=null; showPick(null); render();
}
function inside(x,y,q){
  let s=false;
  for(let i=0,j=3;i<4;j=i++){
    const xi=q[i][0],yi=q[i][1],xj=q[j][0],yj=q[j][1];
    if(((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi)) s=!s;
  }
  return s;
}
const JUMP={baseplate:['S-10','Detail Base Plate'],kolom:['S-03','Rencana Rangka'],
  balok:['S-03','Rencana Rangka'],stiffener:['S-06','Potongan A\u2013A'],
  bracing:['S-03','Rencana Rangka'],dek:['S-01','Denah Tribun'],pinus:['S-06','Potongan A\u2013A'],
  tangga:['S-08','Detail Tangga'],nosing:['S-08','Detail Tangga'],
  railing:['S-09','Detail Railing'],anchor:['S-11','Detail Sambungan'],
  sandaran:['S-05','Tampak Samping'],sandkayu:['S-05','Tampak Samping'],
  kusen:['S-05','Tampak Samping'],beton:['S-02','Rencana Tumpuan'],
  void:['S-01','Denah Tribun'],dinding:['S-05','Tampak Samping'],jendela:['S-05','Tampak Samping']};
function showPick(g){
  const card=document.getElementById('pick');
  const nm=card.querySelector('.pk-name'), dl=card.querySelector('.pk-dl');
  const old=card.querySelector('.pk-jump'); if(old) old.remove();
  if(!g){nm.textContent='Belum ada yang dipilih';dl.innerHTML='';return;}
  nm.textContent=g.name;
  dl.innerHTML=`<dt>Material</dt><dd>${g.mat}</dd>
    <dt>Ukuran</dt><dd>${g.prof}</dd>
    <dt>Jumlah</dt><dd>${g.boxes.length} bagian</dd>
    <dt>Catatan</dt><dd style="font-family:inherit">${g.note}</dd>`;
  const j=JUMP[g.id];
  if(j){
    const btn=document.createElement('button');
    btn.className='pk-jump'; btn.textContent='Lihat '+j[0]+' \u00b7 '+j[1];
    btn.addEventListener('click',()=>{
      const sec=document.getElementById(j[0]);
      sec.classList.add('in');
      sec.scrollIntoView({behavior:'smooth',block:'start'});
    });
    card.appendChild(btn);
  }
}

// legend
const leg=document.getElementById('legend');
const _LC=COLOR();
GROUPS.forEach(g=>{
  const C=_LC;
  const el2=document.createElement('label'); el2.className='lg';
  el2.innerHTML=`<input type="checkbox" checked><span class="sw" style="background:${C[g.id]}"></span><span>${g.name}</span>`;
  el2.querySelector('input').addEventListener('change',ev=>{g.off=!ev.target.checked;reflow();});
  leg.appendChild(el2);
});
function setCtx(on){
  ['dinding','jendela','kusen','beton'].forEach(id=>{G[id].off=!on;});
  dirty=true;
  document.querySelectorAll('.lg').forEach(l=>{
    const nm=l.textContent.trim();
    if(nm.indexOf('Dinding')===0||nm.indexOf('Kaca jendela')===0||nm.indexOf('Kusen')===0||nm.indexOf('Kolom beton')===0){
      l.querySelector('input').checked=on;}
  });
  render();
}
document.getElementById('ctxOn').addEventListener('click',()=>setCtx(true));
document.getElementById('ctxOff').addEventListener('click',()=>setCtx(false));
document.getElementById('ex').addEventListener('input',e=>{ex=+e.target.value;quality(true);quality(false);reflow();});
(function(){const cb=document.getElementById('texCb'); if(!cb) return;
  cb.checked=texOn;
  cb.addEventListener('change',()=>{texOn=cb.checked; render();});})();
document.querySelectorAll('[data-ex]').forEach(b=>b.addEventListener('click',()=>{
  ex=+b.dataset.ex; document.getElementById('ex').value=ex; reflow();}));
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{
  const v=b.dataset.view;
  if(v==='iso'){az=0.62;el=0.60;}
  if(v==='depan'){az=0;el=0.08;}
  if(v==='samping'){az=-Math.PI/2;el=0.08;}
  if(v==='atas'){az=0;el=1.45;}
  ox=0;oy=0;render();}));
const mq=window.matchMedia('(prefers-color-scheme: dark)');
mq.addEventListener('change',()=>{P=palette(); makeLUT();
  document.querySelectorAll('.lg .sw').forEach((s,i)=>s.style.background=COLOR()[GROUPS[i].id]);
  render();});

// bottom sheet (mobile)
const tgl=document.getElementById('sheetTgl'), side=document.getElementById('v3side');
if(tgl) tgl.addEventListener('click',()=>{
  const on=side.classList.toggle('open');
  tgl.setAttribute('aria-expanded',on?'true':'false');
  document.getElementById('sheetTglTxt').textContent=on?'Tutup panel':'Kontrol & material';
});

// render pertama ditunda sampai panggung mendekati layar → halaman ringan saat dibuka
let booted=false;
const boot=()=>{ if(booted) return; booted=true; resize(); draw(); };
window.__boot3d=boot; window.__resize3d=()=>{ if(booted){ resize(); draw(); } };

const stageEl=document.querySelector('.v3-stage');
function near(){
  if(!stageEl) return false;
  const r=stageEl.getBoundingClientRect();
  return r.height>0 && r.top < innerHeight+280 && r.bottom > -280;
}
function maybeBoot(){
  if(booted){ cleanupBoot(); return; }
  if(near()){ boot(); cleanupBoot(); }
}
function cleanupBoot(){
  cleanupPoll();
  removeEventListener('scroll', maybeBoot);
  removeEventListener('resize', maybeBoot);
  removeEventListener('load', maybeBoot);
  document.removeEventListener('visibilitychange', maybeBoot);
  if(io) io.disconnect();
}
let io=null;
if('IntersectionObserver' in window){
  io=new IntersectionObserver(es=>{ if(es.some(e=>e.isIntersecting)) maybeBoot(); }, {rootMargin:'280px'});
  if(stageEl) io.observe(stageEl);
}
// Cadangan berlapis. Observer dan event scroll ternyata tidak selalu memicu
// (halaman dimuat di latar, lompat anchor, gulir terprogram), jadi patokan
// terakhirnya adalah pemeriksaan berkala yang berhenti sendiri begitu menyala.
addEventListener('scroll', maybeBoot, {passive:true});
addEventListener('resize', maybeBoot);
addEventListener('load', maybeBoot);
document.addEventListener('visibilitychange', maybeBoot);
let poll=setInterval(maybeBoot, 350);
function cleanupPoll(){ if(poll){ clearInterval(poll); poll=0; } }
setTimeout(maybeBoot, 200);

// Patokan terakhir. Di sebagian lingkungan (tab yang dikendalikan otomasi, timer
// yang di-throttle, halaman di-prerender) tidak ada satu pun pemicu di atas yang
// jalan, dan penonton cuma melihat kanvas kosong. Lebih baik gambar sekali setelah
// halaman selesai dimuat daripada berisiko tidak muncul sama sekali; konten utama
// sudah tampil duluan, jadi halaman tetap terasa ringan saat dibuka.
function forceBoot(){ setTimeout(()=>{ if(!booted){ boot(); cleanupBoot(); } }, 1200); }
if(document.readyState==='complete') forceBoot();
else addEventListener('load', forceBoot);
})();
"""
