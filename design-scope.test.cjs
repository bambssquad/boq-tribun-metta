const assert=require('node:assert/strict'),fs=require('fs');
const B=require('./boq-revision.js'),d=JSON.parse(fs.readFileSync('assets/r05/boq.json','utf8'));
d.design_scope=JSON.parse(fs.readFileSync('assets/r07/design-scope.json','utf8'));
const rhsIds=['X01','X02','X03','X04','X05','X06','B01','B02'];
for(const scope of ['native','full'])for(const thickness of ['model','h20','h16'])for(const shs of Object.keys(B.shsLabels)){
 const s={...B.defaults(),scope,case:thickness,shs,extras:true},rs=B.rows(d,s),count=scope==='native'?97:101;
 const mass=d.study.procurement.variants[thickness].stock_kg;
 assert(Math.abs(rs.filter(r=>rhsIds.includes(r.id)).reduce((n,r)=>n+r.qty,0)-count*mass)<1e-7);
 assert.equal(rs.some(r=>r.id==='B02'),scope==='full');
 assert.equal(rs.some(r=>r.id==='B03'),scope==='full');
 const t=B.totals(rs);s.units='bars';s.subtotals=true;s.componentSubtotals=true;
 assert.deepEqual(B.totals(B.displayRows(d,s)),t);
 assert.equal(B.componentTotals(d,s).reduce((n,r)=>n+r.total,0),t.total);
 const sheet=B.sheets(d,s).find(x=>x.name==='AUDIT BATANG');
 assert.equal(sheet.rows[4][1].n,count);
 const cuts=sheet.rows.slice(13);
 assert.equal(cuts.length,scope==='native'?245:361);
 assert(Math.abs(cuts.reduce((n,r)=>n+(r[3].n||0),0)-count*mass)<1e-7);
 const subtotal=B.massSummary(d,s);assert(Math.abs(subtotal.kg-rs.filter(r=>r.unit==='kg').reduce((n,r)=>n+r.qty,0))<1e-7);assert(Math.abs(subtotal.components.reduce((n,r)=>n+r.kg,0)-subtotal.kg)<1e-7);assert(Math.abs(subtotal.components.reduce((n,r)=>n+r.bars,0)-subtotal.bars)<1e-7);assert(Math.abs(subtotal.profiles.filter(r=>r.name.startsWith('Hollow')).reduce((n,r)=>n+r.bars,0)-count)<1e-7);
 assert(!B.scopeHtml(d,s).includes('NaN'));
 assert(B.activeKgHtml(d,s).includes(B.fmt(count*mass,3)));
 if(scope==='full'){const audit=B.auditHtml(d,s);assert(audit.includes(B.fmt(97*mass,2)));assert(audit.includes(B.fmt(101*mass,2)));assert(audit.includes(B.fmt(rs.filter(r=>r.unit==='kg').reduce((n,r)=>n+r.qty,0),2)));}

}
const s=B.defaults();B.edit(s,'X01','qty',123);s.scope='native';assert.notEqual(B.rows(d,s)[0].qty,123);
B.edit(s,'X01','qty',456);assert(B.scopeHtml(d,s).includes('berbeda dari pola stok'));s.scope='full';assert.equal(B.rows(d,s)[0].qty,123);
s.scope='adjusted';assert(B.totals(B.rows(d,s)).invalid);assert.throws(()=>B.sheets(d,s));assert.throws(()=>B.pdf(d,s,()=>{}));
s.case='source';assert.equal(B.scope(s),'full');assert.equal(B.totals(B.rows(d,s)).invalid,0);
for(const scope of ['native','full']){const s={...B.defaults(),scope,extras:true};console.log(scope,B.totals(B.rows(d,s)));}
assert.equal(B.totals(B.rows(d,{...B.defaults(),extras:true})).total,269719729);
console.log('PASS: 30 scope/thickness/SHS combinations, 97/101 stock kg, exports, component totals, isolated edits and unavailable design C.');
