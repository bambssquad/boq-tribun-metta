const fs=require('fs'),vm=require('vm'),assert=require('assert');
const data=JSON.parse(fs.readFileSync('assets/r08/viewer.json'));
for(const e of data.items){assert([6,24].includes(e.box.length));assert(e.box.every(Number.isFinite));if(e.box.length===6)assert(e.box.slice(3).every(x=>x>0&&x<18000));}
assert.equal(data.items.filter(e=>e.group==='kolom').length,data.new_posts);
assert.equal(data.mesh.length,60);assert(data.clear_groups.includes('dek'));
const geometry=JSON.parse(fs.readFileSync('assets/r08/geometry.json'));
const quantities=JSON.parse(fs.readFileSync('assets/r08/data.json'));
assert.equal(data.stair_panels,geometry.stairs.length);assert.equal(data.rhs_stocks,quantities.rhs.stock_count);
assert.equal(data.infill_width_mm,Math.round(quantities.params.x1-quantities.params.x0));
assert.equal(data.extra_seats,quantities.changes.extra_indicative_seats);
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
for(const mode of ['a','c']){
 const file=`assets/r08/viewer-${mode}.json`;if(!fs.existsSync(file))continue;
 const payload=JSON.parse(fs.readFileSync(file)),g=JSON.parse(fs.readFileSync(`assets/r08/geometry-${mode}.json`));
 for(const e of g.added_native_items||[]){const rendered=payload.items.find(x=>x.id===e.id);assert(rendered,`${mode}: missing ${e.id}`);assert.deepEqual(rendered.box,e.vertices.flat());}
 assert.equal(payload.items.filter(e=>e.group==='kolom').length,payload.new_posts);
 real.window.MettaModelVersion.apply('v2',payload);
 for(const e of payload.items)assert(real.window.snapshot().find(x=>x.id===e.group).boxes.some(b=>JSON.stringify(b)===JSON.stringify(e.box)));
 console.log(`PASS structure ${mode}: all added physical members and columns match payload`);
}
if(fs.existsSync('assets/r08/options.json')){
 const B=require('./boq-revision.js'),boq=JSON.parse(fs.readFileSync('assets/r05/boq.json'));
 boq.r08=quantities;boq.r08_options=JSON.parse(fs.readFileSync('assets/r08/options.json'));
 const s=B.defaults();s.scope='r08';s.extras=true;const baseline=B.profileKey(s);B.edit(s,'I01','material_rate',123);
 for(const mode of ['a','c'])if(boq.r08_options[mode]){s.structure=mode;assert.notEqual(B.profileKey(s),baseline);assert.notEqual(B.rows(boq,s).find(r=>r.id==='I01').material_rate,123);assert(B.version(s).includes(B.structureLabels[mode]));assert.equal(B.r08Data(boq,s).rhs.stock_count,boq.r08_options[mode].rhs.stock_count);}
 s.structure='baseline';assert.equal(B.rows(boq,s).find(r=>r.id==='I01').material_rate,123);
 console.log('PASS structural modes use independent RAB edits and export captions');
}
