const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/build.py','utf8');const handlers={};let renders=0,saves=0;const row={p:0};
const code=source.slice(source.indexOf("document.addEventListener('input',e=>{",source.indexOf('const NUMF=')),source.indexOf("document.addEventListener('blur',e=>{",source.indexOf('const NUMF=')));
vm.runInNewContext(code,{document:{addEventListener:(n,f)=>handlers[n]=f},arr:()=>[row],save:()=>saves++,render:()=>renders++,S:{}});
const el={classList:{contains:s=>s==='pin'},dataset:{t:'H',i:'0'},value:''};
for(const value of ['6','60','600','6000']){el.value=value;handlers.input({target:el});assert.equal(renders,0);assert.equal(el.value,value);}
assert.equal(row.p,6000);handlers.change({target:el});assert.equal(renders,1);
el.value='0';handlers.input({target:el});assert.equal(row.p,0);el.value='';handlers.input({target:el});assert.equal(row.p,null);
const odo=source.slice(source.indexOf('function paintOdo(){'),source.indexOf('\nconst vbar='));assert.ok(!odo.includes('innerHTML'));assert.ok(!odo.includes('requestAnimationFrame'));
console.log('PASS: 6000 typing preserves input, zero/blank persist, committed edits recalculate, currency is static.');
