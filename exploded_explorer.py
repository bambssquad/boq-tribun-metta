from pathlib import Path
ROOT=Path(__file__).parent

def apply(js,html):
 html=html.replace('<div class="pk-eyebrow">Ledakan struktur</div>','''<div class="pk-eyebrow">Exploded axo</div><div class="v3-row"><button class="mini" data-ex-mode="axo" aria-pressed="true">Axo bertingkat</button><button class="mini" data-ex-mode="catalog" aria-pressed="false">Katalog komponen</button></div><output id="ex-percent" aria-live="polite">0%</output>''')
 html=html.replace('<button class="mini" data-ex="100">Penuh</button></div>','''<button class="mini" data-ex="100">Penuh</button></div><div class="v3-row"><button class="mini" id="ex-play" aria-pressed="false">Putar</button><button class="mini" id="ex-reset">Reset</button></div><p id="ex-hint">Geser untuk memisahkan lapisan struktur.</p>''')
 html=html.replace('<dl class="pk-dl"></dl>','''<dl class="pk-dl"></dl><div class="v3-row"><button class="mini" id="ex-isolate" disabled>Isolasi komponen</button><button class="mini" id="ex-show-all">Lepas isolasi</button></div>''')
 helper=(ROOT/'exploded-catalog.js').read_text(encoding='utf-8')
 js=helper+'\n'+js
 js=js.replace('let sel=null;',"let sel=null,isolated=null;let pieceRefs=[];let exMode='axo',playing=false,anim=0,animTime=0;")
 js=js.replace('const gi=[],bx=[];','const gi=[],bx=[];pieceRefs=[];')
 js=js.replace('const dz=g.fixed?0:',"const dz=g.fixed||exMode==='catalog'?0:")
 old="g.boxes.forEach(b=>{gi.push(k); bx.push(b.length===24?b.map((v,i)=>v+(i%3===2?dz:0)):[b[0],b[1],b[2]+dz,b[3],b[4],b[5]]);});"
 new="g.boxes.forEach((b,bi)=>{if(isolated&&(isolated.g!==k||isolated.bi!==bi))return;pieceRefs.push({g:k,bi,box:b});gi.push(k); bx.push(b.length===24?b.map((v,i)=>v+(i%3===2?dz:0)):[b[0],b[1],b[2]+dz,b[3],b[4],b[5]]);});"
 assert old in js;js=js.replace(old,new)
 js=js.replace('const spread=(10400+2600)*(ex/100);',"const spread=exMode==='catalog'?0:(10400+2600)*(ex/100);")
 marker='  ORD.sort((a,b)=>DEP[b]-DEP[a]);'
 js=js.replace(marker,'''  if(exMode==='catalog'&&ex>0){
    const t=ex/100,grid=ExplodedCatalog.layout(NB,W*.90,H*.86);
    for(let i=0;i<NB;i++){const o=i*8;let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity;
      for(let k=0;k<8;k++){left=Math.min(left,PX[o+k]);right=Math.max(right,PX[o+k]);top=Math.min(top,PY[o+k]);bottom=Math.max(bottom,PY[o+k]);}
      const cell=ExplodedCatalog.target(i,[left,top,right,bottom],grid,W,H,zoom,ox,oy);
      for(let k=0;k<8;k++){PX[o+k]=(1-t)*PX[o+k]+t*(cell.x+(PX[o+k]-cell.cx)*cell.s);PY[o+k]=(1-t)*PY[o+k]+t*(cell.y+(PY[o+k]-cell.cy)*cell.s);}
    }
  }
  if(isolated&&NB===1){const xs=Array.from(PX),ys=Array.from(PY),l=Math.min(...xs),r=Math.max(...xs),t=Math.min(...ys),b=Math.max(...ys),scale=Math.min(W*.7/Math.max(1,r-l),H*.7/Math.max(1,b-t))*zoom;for(let k=0;k<8;k++){PX[k]=W/2+ox+(xs[k]-(l+r)/2)*scale;PY[k]=H/2+oy+(ys[k]-(t+b)/2)*scale;}}
'''+marker)
 js=js.replace("' elemen · ledak '+ex+'%", "' bagian · '+(exMode==='catalog'?'katalog ':'axo ')+Math.round(ex)+'%")
 js=js.replace('Math.min(6,','Math.min(12,')
 js=js.replace('if(e.shiftKey){ox+=dx;oy+=dy;}',"if(e.shiftKey||(exMode==='catalog'&&ex>0)){const dpr=cv.width/cv.getBoundingClientRect().width;ox+=dx*dpr;oy+=dy*dpr;}")
 js=js.replace("if(inside(mx,my,q)){ sel=i;","if(inside(mx,my,q)){ stopExplosion();sel=i;")
 js=js.replace('stage.addEventListener(\'pointercancel\',up);',"stage.addEventListener('pointercancel',e=>{moved=10;up(e);});")
 js=js.replace("const j=JUMP[g.id];",'''  const piece=pieceRefs[sel];
  if(piece){const dims=ExplodedCatalog.dimensions(piece.box);let source=null;const flat=piece.box.length===24?piece.box:null;
    if(flat)source=[...REVISED,...FINISH_GEOMETRY].find(x=>x.group===g.id&&x.vertices.flat().every((v,i)=>Math.abs(v-flat[i])<.001));
    const add=(label,value)=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;dl.append(dt,dd);};
    add('Dimensi geometri',dims.map(x=>x.toLocaleString('id-ID',{maximumFractionDigits:1})).join(' × ')+' mm');
    add('ID sumber',source?.id!=null?String(source.id):'Tidak tersedia untuk bagian ini');
    if(source?.mark)add('Mark',source.mark);
    add('Bagian web',g.id+' / '+(piece.bi+1));
  }
  document.getElementById('ex-isolate').disabled=!piece;
  const j=JUMP[g.id];''')
 js=js.replace("if(!g){nm.textContent=", "if(!g){document.getElementById('ex-isolate').disabled=true;nm.textContent=")
 old="document.getElementById('ex').addEventListener('input',e=>{ex=+e.target.value;quality(true);quality(false);reflow();});"
 new='''function setExplode(value){ex=Math.max(0,Math.min(100,value));document.getElementById('ex').value=ex;document.getElementById('ex-percent').textContent=Math.round(ex)+'%';reflow();}
function stopExplosion(){playing=false;cancelAnimationFrame(anim);anim=0;document.getElementById('ex-play').textContent='Putar';document.getElementById('ex-play').setAttribute('aria-pressed','false');quality(false);}
function playFrame(time){if(!playing)return;const dt=Math.min(80,time-animTime);animTime=time;setExplode(ex+dt/60);if(ex>=100){stopExplosion();return;}anim=requestAnimationFrame(playFrame);}
document.getElementById('ex').addEventListener('input',e=>{stopExplosion();setExplode(+e.target.value);});
document.getElementById('ex-play').addEventListener('click',()=>{if(playing){stopExplosion();return;}if(ex>=100)setExplode(0);playing=true;animTime=performance.now();document.getElementById('ex-play').textContent='Jeda';document.getElementById('ex-play').setAttribute('aria-pressed','true');quality(true);anim=requestAnimationFrame(playFrame);});
document.getElementById('ex-reset').addEventListener('click',()=>{stopExplosion();isolated=null;sel=null;az=.62;el=.60;zoom=1;ox=oy=0;showPick(null);setExplode(0);});
document.getElementById('ex-isolate').addEventListener('click',()=>{if(pieceRefs[sel]){stopExplosion();isolated={g:pieceRefs[sel].g,bi:pieceRefs[sel].bi};sel=0;zoom=1;ox=oy=0;reflow();}});
document.getElementById('ex-show-all').addEventListener('click',()=>{isolated=null;sel=null;showPick(null);reflow();});
document.querySelectorAll('[data-ex-mode]').forEach(b=>b.addEventListener('click',()=>{stopExplosion();exMode=b.dataset.exMode;sel=null;showPick(null);zoom=1;ox=oy=0;document.querySelectorAll('[data-ex-mode]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.getElementById('ex-hint').textContent=exMode==='catalog'?'Komponen disusun sebagai katalog. Ukuran tampilan disesuaikan per bagian; klik untuk dimensi. Seret untuk geser, scroll/pinch untuk zoom.':'Geser untuk memisahkan lapisan struktur. Seret untuk memutar.';reflow();}));
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopExplosion();});
'''
 assert old in js;js=js.replace(old,new)
 js=js.replace('ex=+b.dataset.ex; document.getElementById(\'ex\').value=ex; reflow();',"stopExplosion();setExplode(+b.dataset.ex);")
 js=js.replace('g.off=!ev.target.checked;reflow();','g.off=!ev.target.checked;sel=null;showPick(null);reflow();')
 js=js.replace('function setCtx(on){','function setCtx(on){sel=null;showPick(null);')
 html=html.replace('per lapis. Klik batang atau pelat mana pun — keterangan material, profil, dan beratnya muncul','per lapis atau menjadi katalog komponen. Klik batang atau pelat — profil, dimensi, dan ID sumber tersedia')
 html+='''<style>#ex-percent{display:block;text-align:right;font:600 18px Arial,sans-serif;margin:10px 0}#ex{width:100%;height:30px;accent-color:#111;cursor:ew-resize}#ex-hint{font:12px/1.45 Arial,sans-serif;margin:12px 0 0}.v3-side .mini[aria-pressed=true]{background:#111!important;color:white!important}.v3-side .mini:disabled{opacity:.45;cursor:default}.v3-side .v3-row{flex-wrap:wrap;gap:8px}.v3-side .mini{min-height:40px}#pick .pk-dl dd{overflow-wrap:anywhere}</style>'''
 return js,html
