const assert=require('node:assert/strict'),G=require('./boq-groups.js');
const rows=[{code:'M04',category:'Material',amount:123,price:99,qty:7},{code:'M05',category:'Material',amount:456,price:10,qty:8},{code:'U02',category:'Upah',amount:12,price:4,qty:3}];const snapshot=JSON.stringify(rows);
for(const mode of ['component','category']){const groups=G.groups(rows,mode);assert.equal(groups.reduce((n,g)=>n+g.amount,0),591);assert.equal(groups.flatMap(g=>g.items).length,3);assert.equal(JSON.stringify(rows),snapshot);}
assert.equal(G.groups(rows,'component').find(g=>g.name==='Tangga').amount,468);
rows[0].component='Kolom tribun';assert.equal(G.component(rows[0]),'Kolom tribun');
assert.ok(G.html(rows,'component',r=>'<tr><td>'+r.code+'</td></tr>',1).includes('Kolom tribun'));
const exported=G.excel(rows,'component',r=>[r.code,r.price,r.qty],8);assert.ok(exported.some(r=>r[0]==='M04'&&r[1]===99));assert.equal(exported.filter(r=>r.length===8).reduce((n,r)=>n+r[6],0),591);
console.log('PASS: grouping and custom groups preserve quantities, prices and totals across layouts/exports.');
