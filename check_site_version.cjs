const fs=require('fs'),vm=require('vm'),assert=require('assert');
const data=JSON.parse(fs.readFileSync('assets/r08/viewer.json'));
for(const e of data.items){assert([6,24].includes(e.box.length));assert(e.box.every(Number.isFinite));if(e.box.length===6)assert(e.box.slice(3).every(x=>x>0&&x<18000));}
assert.equal(data.items.filter(e=>e.group==='kolom').length,20);
assert.equal(data.mesh.length,60);assert(data.clear_groups.includes('dek'));
const geometry=JSON.parse(fs.readFileSync('assets/r08/geometry.json'));
for(const plate of geometry.plate2){const e=data.items.find(e=>e.id===plate.id);assert(e);assert.deepEqual(e.box.slice(3),plate.bounds.slice(3).map((v,i)=>v-plate.bounds[i]));}
const groups=[...new Set(['dek',...data.items.map(x=>x.group),'skirt','bracing'])].map(id=>({id,name:id,boxes:[[0,0,0,1,1,1]],prof:'baseline'}));
const setup=`const GROUPS=${JSON.stringify(groups)},G=Object.fromEntries(GROUPS.map(g=>[g.id,g])); const REVISED=[],FINISH_GEOMETRY=[],leg={children:[]},cv={dataset:{}},booted=false;let isolated=null,sel=null,dirty=false;function stopExplosion(){}function showPick(){}function Bcut(){};`;
const ctx={window:{}};vm.createContext(ctx);vm.runInContext(setup+fs.readFileSync('site-version-viewer.js','utf8')+';window.snapshot=()=>GROUPS.map(g=>({id:g.id,boxes:g.boxes,prof:g.prof}));',ctx);
ctx.window.MettaModelVersion.apply('v2',data);const once=JSON.stringify(ctx.window.snapshot());ctx.window.MettaModelVersion.apply('v2',data);assert.equal(JSON.stringify(ctx.window.snapshot()),once,'Repeated V2 must not duplicate geometry');
ctx.window.MettaModelVersion.apply('v1',data);for(const g of ctx.window.snapshot()){assert.equal(g.boxes.length,1);assert.equal(g.prof,'baseline');}
ctx.window.MettaModelVersion.apply('v2',data,{wire_mm:2,opening_label_mm:50});assert.notEqual(JSON.stringify(ctx.window.snapshot()),once);
console.log('PASS global model: finite sizes, 20 infill posts, 60 mesh panels, repeat/restore, mesh density');
const native=fs.readFileSync('dist/assets/model-native.js','utf8');const nativeItems=JSON.parse(native.match(/const REVISED=(.*);/s)[1]);
const expectedDeck=nativeItems.filter(e=>e.group==='dek'&&!data.remove_ids.includes(e.id)).length;
const realSetup=`const GROUPS=${JSON.stringify(groups)},G=Object.fromEntries(GROUPS.map(g=>[g.id,g]));${native}const FINISH_GEOMETRY=[],leg={children:[]},cv={dataset:{}},booted=false;let isolated=null,sel=null,dirty=false;function stopExplosion(){}function showPick(){}function Bcut(g,...b){G[g].boxes.push(b);}REVISED.forEach(e=>{if(G[e.group])G[e.group].boxes.push(e.vertices.flat());});`;
const real={window:{}};vm.createContext(real);vm.runInContext(realSetup+fs.readFileSync('site-version-viewer.js','utf8')+';window.snapshot=()=>GROUPS;',real);real.window.MettaModelVersion.apply('v2',data);
assert.equal(real.window.snapshot().find(g=>g.id==='dek').boxes.length,expectedDeck+data.items.filter(e=>e.group==='dek').length);
for(const e of nativeItems.filter(e=>data.remove_ids.includes(e.id)&&e.group!=='dek'))assert(!real.window.snapshot().find(g=>g.id===e.group).boxes.some(b=>JSON.stringify(b)===JSON.stringify(e.vertices.flat())));
console.log('PASS retained deck reconstruction and removal of native RC struts');

