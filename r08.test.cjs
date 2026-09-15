const fs=require('fs'),assert=require('node:assert/strict'),B=require('./boq-revision.js');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const d=read('assets/r05/boq.json');d.design_scope=read('assets/r07/design-scope.json');d.r08=read('assets/r08/data.json');d.r08_options=read('assets/r08/options.json');
for(const structure of ['baseline','a','c'])for(const c of ['model','h20','h16'])for(const shs of ['reference','s16','s17','s20','s23'])for(const mesh of Object.keys(B.meshLabels))for(const basis of ['purchase','net'])for(const extras of [false,true]){
 const s={...B.defaults(),scope:'r08',structure,case:c,shs,mesh,basis,extras,subtotals:true,componentSubtotals:true},rs=B.rows(d,s),tot=B.totals(rs),mass=B.massSummary(d,s),active=B.r08Data(d,s);
 assert.equal(tot.invalid,0);assert.equal(B.totals(B.displayRows(d,{...s,units:'bars'})).total,tot.total);
 assert.equal(B.componentTotals(d,s).reduce((n,r)=>n+r.total,0),tot.total);
 const rhs=mass.profiles.filter(r=>r.name.startsWith('Hollow 50'));
 assert.equal(rhs.length,1);
 if(basis==='purchase')assert(Math.abs(rhs[0].bars-active.rhs.stock_count)<1e-8);
 assert.equal(rs.find(r=>r.id==='M01').qty,active.mesh_options.find(m=>m.id===mesh)[basis+'_kg']);
 assert(B.html(d,s).includes('R08'));assert(B.html(d,s).includes('Rp30.000/kg'));
 assert(B.scopeHtml(d,s).includes(active.rhs.stock_count+' batang'));assert(B.scopeHtml(d,s).toLowerCase().includes('dua jalur'));
 assert(B.sheets(d,s).find(x=>x.name==='AUDIT BATANG').rows.some(r=>r.some(c=>c.n===active.rhs.stock_count)));
 const opposite=structure==='a'?'c':'a',untouched=B.rows(d,{...s,structure:opposite}).find(r=>r.id==='I01').qty;
 const before=B.totals(B.rows(d,{...s,scope:'full'})).total;
 B.edit(s,'I01','qty',10);assert.equal(B.rows(d,{...s,structure:opposite}).find(r=>r.id==='I01').qty,untouched);assert.notEqual(B.totals(B.rows(d,s)).total,tot.total);
 assert.equal(B.totals(B.rows(d,{...s,scope:'full'})).total,before);
 assert.equal(B.rows(d,{...s,mesh:mesh==='m20_25'?'m16_25':'m20_25'}).find(r=>r.id==='I01').qty,rs.find(r=>r.id==='I01').qty);
}
assert.equal(B.normalize({scope:'r08',mesh:'bad'}).mesh,'m20_25');
console.log('PASS: 540 R08 baseline/A/C thickness/SHS/mesh/basis/extras combinations, masses, invariant costs, subtotals, Excel and isolated edits.');
