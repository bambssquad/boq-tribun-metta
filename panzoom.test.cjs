const assert=require('node:assert/strict');
const create=require('./panzoom.js');
function element(){const listeners={};return {style:{},textContent:'',clientHeight:600,classList:{add(){},remove(){}},focus(){},setPointerCapture(){},getBoundingClientRect:()=>({left:10,top:20,width:800,height:600}),addEventListener(n,f){(listeners[n]??=[]).push(f)},fire(n,extra={}){const e={type:n,button:0,pointerType:'mouse',pointerId:1,clientX:110,clientY:120,timeStamp:1000,preventDefault(){this.prevented=true},stopPropagation(){this.stopped=true},...extra};for(const f of listeners[n]||[])f(e);return e}}}
const viewport=element(),img=element(),controls={plus:element(),minus:element(),reset:element(),level:element()};
const {state,reset}=create(viewport,img,controls);
viewport.fire('pointerdown');viewport.fire('pointermove',{clientX:160,clientY:145});
assert.equal(state.x,50);assert.equal(state.y,25);viewport.fire('pointerup');
reset();const wheel=viewport.fire('wheel',{deltaY:-100,deltaMode:0});assert(wheel.prevented);
assert(Math.abs((100-state.x)/state.scale-100)<1e-9,'zoom keeps cursor point anchored');
for(let i=0;i<30;i++)controls.plus.fire('click');assert.equal(state.scale,9);
for(let i=0;i<60;i++)controls.minus.fire('click');assert.equal(state.scale,.5);
controls.reset.fire('click');assert.deepEqual(state,{x:0,y:0,scale:1});
viewport.fire('pointerdown',{pointerType:'touch',pointerId:1,clientX:110,clientY:120});
viewport.fire('pointerdown',{pointerType:'touch',pointerId:2,clientX:210,clientY:120});
viewport.fire('pointermove',{pointerType:'touch',pointerId:2,clientX:310,clientY:120});
assert.equal(state.scale,2);assert.equal(state.x,-100);assert.equal(state.y,-100);
viewport.fire('pointerup',{pointerType:'touch',pointerId:2});
viewport.fire('pointermove',{pointerType:'touch',pointerId:1,clientX:130,clientY:120});assert.equal(state.x,-80);
viewport.fire('pointercancel',{pointerType:'touch',pointerId:1});
const before=state.x;viewport.fire('pointermove',{clientX:900});assert.equal(state.x,before,'cancel ends drag');
const key=viewport.fire('keydown',{key:'ArrowRight'});assert(key.prevented&&key.stopped,'pan does not change sheets');assert.equal(state.x,before+40);
viewport.fire('dblclick');assert.deepEqual(state,{x:0,y:0,scale:1});
controls.plus.fire('click');
for(const time of [2000,2200]){viewport.fire('pointerdown',{pointerType:'touch'});viewport.fire('pointerup',{pointerType:'touch',timeStamp:time});}
assert.equal(state.scale,1,'double tap fits drawing');
console.log('PASS: drag, anchored zoom, pinch-to-pan, limits, cancellation, keyboard and reset.');
