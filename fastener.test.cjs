const assert=require('node:assert/strict'),d=require('./assets/r04/data.json');
const rows=Object.fromEntries(d.rows.map(r=>[r.code,r]));
assert.equal(rows.M14,undefined);
assert.equal(rows.M14B.qty,693);assert.equal(rows.M14N.qty,693);assert.equal(rows.M14W.qty,1386);
assert.equal(['M14B','M14N','M14W'].reduce((n,k)=>n+rows[k].qty*rows[k].price,0),693*7500);
for(const k of ['M11','M12','M13','M14B','M14N','M14W','M15','M16']){const r=rows[k];assert.ok(r.supplier);assert.ok(r.specification);assert.ok(r.price_basis.includes('Estimasi'));assert.ok(d.sources[r.source][1].startsWith('https://'));}
assert.equal(rows.M16.qty,d.fastener_basis.cover_screws_purchase);
console.log('PASS: split fasteners preserve cost and count, no duplicate package, supplier/specification and estimate basis included.');
