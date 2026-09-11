const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const B=require('./boq-revision.js'),d=JSON.parse(fs.readFileSync('assets/r05/boq.json','utf8'));
for(const expected of d.comparison){const s={...B.defaults(),case:expected.case,basis:expected.basis,extras:expected.extras};const t=B.totals(B.rows(d,s));for(const k of ['total','labor','material'])assert(Math.abs(t[k]-expected[k])<=2,`${expected.case}/${expected.basis}/${k}`);assert.equal(t.invalid,0);}
const s=B.defaults(),base=B.totals(B.rows(d,s));B.edit(s,'X01','qty',0);assert.equal(B.rows(d,s).find(r=>r.id==='X01').total,0);s.basis='net';assert(B.rows(d,s).find(r=>r.id==='X01').qty>0);s.basis='purchase';assert.equal(B.rows(d,s).find(r=>r.id==='X01').qty,0);
B.edit(s,'X01','qty',null);assert.equal(B.totals(B.rows(d,s)).invalid,1);assert.throws(()=>B.sheets(d,s));B.edit(s,'X01','qty',3);B.edit(s,'X01','labor_rate',6000);assert.equal(B.rows(d,s).find(r=>r.id==='X01').labor,18000);
s.case='h16';assert.equal(B.rows(d,s).find(r=>r.id==='X01').labor_rate,6000);assert.notEqual(B.rows(d,s).find(r=>r.id==='X01').qty,3);
for(const [version,mass,label] of [['h16',2283.61,'1,6'],['h20',2854.26,'2,0']]){
 const state={...B.defaults(),case:version},rows=B.rows(d,state);
 assert(Math.abs(rows.slice(0,8).reduce((sum,r)=>sum+r.qty,0)-mass)<1e-6);
 assert(rows.slice(0,8).every(r=>r.material.includes(label)));
 assert.equal(rows.find(r=>r.id==='X07').qty,30.14);
 const audit=B.sheets(d,state)[2].rows.slice(13);assert.equal(audit.length,361);
 assert.equal(audit.filter(r=>typeof r[3].n==='number').length,101);
 assert(Math.abs(audit.reduce((sum,r)=>sum+(r[3].n||0),0)-mass)<1e-6);
 assert(Math.abs(audit.reduce((sum,r)=>sum+(r[4].n||0),0)-mass)<1e-6);
 assert(B.stockHtml(d,state).includes('101 batang'));
}
s.case='source';assert.equal(B.rows(d,s).length,24);const source=B.totals(B.rows(d,s));assert.equal(source.labor,62143000);assert(Math.abs(source.total-218796686)<3);
s.case='model';delete s.profiles.model;const rs=B.rows(d,s);assert.equal(B.totals(rs).total,base.total);assert.equal(rs.filter(r=>r.id==='X18')[0].qty,1386);assert.equal(rs.find(r=>r.id==='B06').qty,976);
const x=B.sheets(d,s);assert.equal(x[0].rows[5][7].f,'ROUND(D6*F6,0)');assert.equal(x[0].rows.at(-1)[9].f,'SUM(J6:J35)');assert.equal(x[1].rows[1][0].t,'X01');
assert.equal(x[2].name,'AUDIT BATANG');assert(Math.abs(rs.find(r=>r.id==='X14').qty-678.24)<1e-7);
B.edit(s,'X01','name','<script>alert(1)</script>');assert(!B.html(d,s).includes('<script>'));assert(B.html(d,s).includes('&lt;script&gt;'));
const sandbox={TextEncoder,Uint8Array,Uint32Array,DataView,Date,Math};vm.runInNewContext(fs.readFileSync('assets/r04/xlsx.js','utf8')+';globalThis.XL=XL',sandbox);const bytes=sandbox.XL.book(x);assert.equal(bytes[0],80);assert.equal(bytes[1],75);
console.log('PASS: all three thickness totals, 361 cuts/101 stocks and allocated kg, independent edits, zero vs blank, source totals, plate sheets, Excel formulas and escaping.');

// Evaluate the export's small arithmetic grammar independently of web totals.
function evaluate(book,sheet,address){const col=address.charCodeAt(0)-65,row=Number(address.slice(1))-1,cell=book.find(x=>x.name===sheet).rows[row]?.[col]||{};if(!cell.f)return cell.n??cell.t??0;
 let formula=cell.f,refs=[];const token=value=>{refs.push(value);return `refs[${refs.length-1}]`;};
 formula=formula.replace(/'([^']+)'!([A-J]\d+)/g,(_,name,addr)=>token(evaluate(book,name,addr)));
 formula=formula.replace(/\b([A-J]\d+):([A-J]\d+)\b/g,(_,a,b)=>{const values=[];for(let i=Number(a.slice(1));i<=Number(b.slice(1));i++)values.push(evaluate(book,sheet,a[0]+i));return token(values);});
 formula=formula.replace(/\b[A-J]\d+\b/g,addr=>token(evaluate(book,sheet,addr))).replace(/(?<![<>=])=(?!=)/g,'===');
 return Function('refs','SUM','ROUND','IF',`return ${formula}`)(refs,(...xs)=>xs.flat().reduce((a,b)=>a+(typeof b==='number'?b:0),0),Math.round,(condition,a,b)=>condition?a:b);
}
for(const shs of ['s16','s17','s20','s23'])for(const version of ['model','h16','h20'])for(const basis of ['purchase','net'])for(const extras of [false,true]){
 const state={...B.defaults(),shs,case:version,basis,extras},component=B.rows(d,state),total=B.totals(component);
 const selected=component.filter(r=>['X07','X08','B03'].includes(r.id));assert.equal(selected.length,3);assert(selected.every(r=>r.material.includes(B.shsLabels[shs].slice(4))));
 if(basis==='purchase')assert(Math.abs(selected.reduce((a,r)=>a+r.qty/r.stock_kg,0)-47)<1e-8);
 state.units='bars';assert.deepEqual(B.totals(B.displayRows(d,state)),total);
 if(basis==='purchase'){const stocks=B.displayRows(d,state).filter(r=>r.stock);assert(Math.abs(stocks.reduce((n,r)=>n+r.qty,0)-148)<1e-8);}
 state.subtotals=true;const entries=B.entries(d,state);assert.equal(entries.filter(r=>r.subtotal).reduce((n,r)=>n+r.total,0),total.total);
 const book=B.sheets(d,state),last=book[0].rows.length;assert.equal(evaluate(book,'RAB 11 SEP','J'+last),total.total);assert.equal(evaluate(book,'RAB 11 SEP','H'+last),total.labor);assert.equal(evaluate(book,'RAB 11 SEP','I'+last),total.material);
 assert(B.html(d,state).includes('Subtotal Batang hollow'));
 state.units='components';const detailBook=B.sheets(d,state);assert.equal(evaluate(detailBook,'RAB 11 SEP','J'+detailBook[0].rows.length),total.total);
}
const shsState={...B.defaults(),shs:'s16'};B.edit(shsState,'X08','qty',0);assert.equal(B.rows(d,shsState).find(r=>r.id==='X08').total,0);shsState.shs='s17';assert(B.rows(d,shsState).find(r=>r.id==='X08').total>0);shsState.shs='s16';assert.equal(B.rows(d,shsState).find(r=>r.id==='X08').total,0);
B.edit(shsState,'X08','qty',null);shsState.units='bars';assert.equal(B.totals(B.displayRows(d,shsState)).invalid,1);assert.throws(()=>B.sheets(d,shsState));
const legacy=B.normalize({case:'model',profiles:{model:{overrides:{X07:{quantities:{purchase:99}}}}}});assert.equal(legacy.shs,'reference');assert.equal(B.rows(d,legacy).find(r=>r.id==='X07').qty,99);
assert.equal(B.normalize({shs:'bad',units:'bad',subtotals:'false'}).subtotals,false);
console.log('PASS: 48 SHS/RHS/basis/extras combinations, 148 stocks, unchanged grouped totals, subtotal/export formulas, independent edits and saved legacy state.');
for(const units of ['components','bars'])for(const subtotals of [false,true])for(const version of ['model','source']){
 const state={...B.defaults(),units,subtotals,case:version,componentSubtotals:true},total=B.totals(B.rows(d,state)),parts=B.componentTotals(d,state);
 assert.equal(parts.reduce((n,r)=>n+r.total,0),total.total);assert(parts.some(r=>r.name==='Kolom'));assert(parts.some(r=>r.name==='Balok'));
 const book=B.sheets(d,state),sheet=book.find(r=>r.name==='SUBTOTAL KOMPONEN');assert.equal(evaluate(book,sheet.name,'D'+sheet.rows.length),total.total);
 assert(B.html(d,state).includes('Subtotal per komponen'));
 B.edit(state,'X01','qty',0);const modified=B.componentTotals(d,state);assert.equal(modified.find(r=>r.name==='Kolom').total,0);
}
console.log('PASS: column/beam/component subtotals reconcile in all views and exported formulas, including manual edits.');

(async()=>{
 const elements=new Map(),storage=new Map();function element(id){if(!elements.has(id))elements.set(id,{dataset:{},listeners:{},addEventListener(k,fn){this.listeners[k]=fn;},querySelectorAll(){return [];},setAttribute(){},innerHTML:'',textContent:''});return elements.get(id);}
 const context={BoqRevision:B,document:{getElementById:element,querySelectorAll:()=>[]},localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},fetch:async()=>({ok:true,json:async()=>d}),console};
 vm.runInNewContext(fs.readFileSync('boq-revision-controller.js','utf8'),context);await new Promise(setImmediate);
 const change=(id,value)=>{const el=element(id);el.value=value;el.listeners.change({target:el});};
 change('br-shs','s17');assert(element('br-rows').innerHTML.includes('SHS 40×40×1,7 mm'));const before=element('br-total').textContent;
 change('br-units','bars');assert.equal(element('br-total').textContent,before);assert(element('br-rows').innerHTML.includes('btg 6m'));assert(element('br-rows').innerHTML.includes('readonly'));
 const subtotal=element('br-subtotals');subtotal.checked=true;subtotal.listeners.change({target:subtotal});assert(element('br-rows').innerHTML.includes('Subtotal Batang hollow'));assert.equal(element('br-total').textContent,before);
 const componentSubtotal=element('br-component-subtotals');componentSubtotal.checked=true;componentSubtotal.listeners.change({target:componentSubtotal});assert(element('br-component-summary').innerHTML.includes('Kolom'));assert(element('br-component-summary').innerHTML.includes('Balok'));assert.equal(element('br-total').textContent,before);
 element('boq-revision').listeners.click({target:{dataset:{brComponents:'1'}}});assert.equal(element('br-units').value,'components');assert(!element('br-rows').innerHTML.includes('readonly'));
 const kgToggle=element('br-kg-explanation');kgToggle.checked=true;kgToggle.listeners.change({target:kgToggle});assert.equal(element('br-kg-panel').hidden,false);assert(element('br-kg-panel').innerHTML.includes('54 dibanding 101'));assert.equal(element('br-total').textContent,before);
 const persisted=JSON.parse(storage.get('metta-boq-september11-v1'));assert.equal(persisted.kgExplanation,true);assert.equal(persisted.shs,'s17');assert.equal(persisted.subtotals,true);
 change('br-case','source');assert.equal(element('br-shs').disabled,true);assert.equal(element('br-units').disabled,true);
 console.log('PASS: controller SHS, stock/component switch, subtotals, persistence and source controls.');
})().catch(error=>{console.error(error);process.exitCode=1;});

assert.equal(B.kgHtml(d,B.defaults()),'');
assert.equal(B.normalize({kgExplanation:'false'}).kgExplanation,false);
for(const selected of ['model','h20','h16','source']) {
 const state={...B.defaults(),case:selected,kgExplanation:true};
 const explanation=B.kgHtml(d,state);
 assert(explanation.includes('590,14'));assert(explanation.includes('minimum global belum terbukti'));assert(!explanation.includes('NaN'));
 assert(explanation.includes('1.662,5'));
 if(selected!=='source') {
  const before=B.totals(B.rows(d,state));state.kgExplanation=false;assert.deepEqual(B.totals(B.rows(d,state)),before);state.kgExplanation=true;
  B.edit(state,'X01','qty',0);assert(!B.kgHtml(d,state).includes('NaN'));
 }
}
console.log('PASS: kg explanation, scope distinction, selected thickness, manual quantities and invariant costs.');
