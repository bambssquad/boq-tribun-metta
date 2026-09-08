const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let frames=[],timers=[],currentFocus=null;
class El{
 constructor(id=''){this.id=id;this.style={};this.dataset={};this.handlers={};this.open=false;this.hidden=false;this.isConnected=true;this.attrs={};this.classList={toggle(){},add(){},remove(){}};this.rect={left:0,top:100,width:300,height:220,bottom:320};}
 addEventListener(n,f){(this.handlers[n]??=[]).push(f)}
 emit(n,e={}){for(const f of this.handlers[n]??[])f({target:this,...e})}
 setAttribute(n,v){this.attrs[n]=v}removeAttribute(n){delete this.attrs[n]}
 getBoundingClientRect(){return this.rect}
 querySelector(s){return this.button}
 closest(){return null}
 focus(){currentFocus=this;this.emit('focus')}
 showModal(){this.open=true}close(){this.open=false;this.emit('close')}
 append(){}remove(){}
 setPointerCapture(id){this.pointer=id}hasPointerCapture(id){return this.pointer===id}releasePointerCapture(){this.pointer=null;this.emit('lostpointercapture')}
}
const els={};const get=s=>els[s]??=new El(s);
const cards=Array.from({length:12},(_,i)=>{const c=new El();c.dataset={index:String(i),category:i<3?'Denah':i<7?'Potongan':'Detail'};c.button=new El();return c});
const jumps=cards.map((_,i)=>{const e=new El();e.dataset.jump=String(i);return e});
const links=['timeline','surf','index','proyek'].map(v=>{const e=new El();e.dataset.viewLink=v;return e});
const body=new El();body.dataset.view='timeline';
const document={body,querySelector:get,querySelectorAll:s=>s==='.archive-card'?cards:s==='[data-jump]'?jumps:s==='[data-view-link]'?links:[],addEventListener(){},createElement:()=>new El()};
const events={},location={hash:'',replace(url){this.redirect=url},assign(url){this.destination=url}};
const reduced={matches:false,addEventListener(){}};const context={document,location,innerWidth:1200,innerHeight:800,Element:El,performance:{now:()=>100},matchMedia:()=>reduced,METTA_DRAWINGS:cards.map((c,i)=>({code:'S-'+String(i+1).padStart(2,'0'),title:'Drawing '+i,svg:'S-'+i+'.svg',dxf:'S-'+i+'.dxf',notes:['note']})),createDrawingPanZoom:()=>({reset(){}}),requestAnimationFrame:f=>(frames.push(f),frames.length),setTimeout:f=>(timers.push(f),timers.length),addEventListener:(n,f)=>events[n]=f,console};context.window=context;context.scrollTo=()=>{};
vm.runInNewContext(fs.readFileSync('lookback.js','utf8'),context);
function settle(){for(let i=0;frames.length&&i<1000;i++){const batch=frames;frames=[];batch.forEach(f=>f())}assert.equal(frames.length,0)}
settle();assert.equal(get('#current-sheet').textContent,'S-01');
assert.equal(body.dataset.brandCompact,'false');
events.wheel({deltaY:120,deltaMode:0,target:new El()});assert.equal(body.dataset.brandCompact,'true');
events.wheel({deltaY:-200,deltaMode:0,target:new El()});assert.equal(body.dataset.brandCompact,'false');
events.wheel({deltaY:200,deltaMode:0,ctrlKey:true,target:new El()});assert.equal(body.dataset.brandCompact,'false');
events.touchstart({touches:[{clientY:300}]});events.touchmove({touches:[{clientY:150}]});assert.equal(body.dataset.brandCompact,'true');
events.touchmove({touches:[{clientY:350}]});assert.equal(body.dataset.brandCompact,'false');events.touchend();
events.keydown({key:'PageDown',target:new El(),preventDefault(){}});assert.equal(body.dataset.brandCompact,'true');
events.keydown({key:'Home',target:new El(),preventDefault(){}});assert.equal(body.dataset.brandCompact,'false');
jumps[11].onclick();settle();assert.equal(get('#current-sheet').textContent,'S-12');
assert.equal(body.dataset.brandCompact,'true');
get('#next').onclick();settle();assert.equal(get('#current-sheet').textContent,'S-01');
get('#previous').onclick();settle();assert.equal(get('#current-sheet').textContent,'S-12');
location.hash='#index';events.hashchange();settle();assert.equal(body.dataset.view,'index');get('#category').onchange({target:{value:'Detail'}});assert.equal(cards.filter(c=>!c.hidden).length,5);
cards[7].button.onclick();settle();assert.equal(get('#sheet-dialog').open,true);assert.match(get('#sheet-title').textContent,/S-08/);get('#sheet-next').onclick();assert.match(get('#sheet-title').textContent,/S-09/);get('#sheet-close').onclick();assert.equal(get('#sheet-dialog').open,false);
location.hash='#surf';events.hashchange();settle();assert.equal(cards.filter(c=>!c.hidden).length,12);assert.equal(body.dataset.view,'surf');
const stage=get('.archive-carousel');stage.emit('pointerdown',{button:0,isPrimary:true,pointerId:1,clientX:100});stage.emit('pointermove',{pointerId:1,clientX:150});stage.emit('pointerup',{pointerId:1});settle();assert.equal(stage.pointer,null);
location.hash='#timeline';events.hashchange();settle();assert.equal(body.dataset.brandCompact,'false');
get('#menu-toggle').onclick();assert.equal(body.dataset.brandCompact,'true');get('#menu-close').onclick();
location.hash='#boq';events.hashchange();assert.equal(location.redirect,'tools.html#boq');
console.log('PASS: SAP identity on wheel, touch, keyboard, menu and navigation; scroll back restores the full company name.');
console.log('PASS: circular forward/back, last-to-first wrap, index filter, sheet navigation, pointer capture release, surf and legacy BOQ route.');
