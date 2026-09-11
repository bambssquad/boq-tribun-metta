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
