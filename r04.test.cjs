const assert=require('node:assert/strict');
const {r04Totals}=require('./r04_app.js');
const rows=[{code:'M01',category:'Material',qty:2,price:100,kg_per_unit:10},{code:'M11',category:'Material',qty:8,price:5,kg_per_unit:0},{code:'U01',category:'Upah',qty:0,price:6000}];
let t=r04Totals(rows,{service:true,rate:6000,overhead:10,profit:5,tax:12});
assert.equal(t.kg,20);assert.equal(t.direct,120240);assert.equal(t.oh,12024);assert.equal(t.profit,6613);assert.equal(t.tax,16665);assert.equal(t.total,155542);
t=r04Totals(rows,{service:false,rate:6000,overhead:0,profit:0,tax:0});assert.equal(t.total,240);assert.equal(t.items.find(r=>r.code==='U01').price,0);
rows[0].qty=3;t=r04Totals(rows,{service:true,rate:100,overhead:0,profit:0,tax:0});assert.equal(t.kg,30);assert.equal(t.total,3340);
t=r04Totals([{code:'M',qty:-3,price:Infinity,kg_per_unit:10}],{service:true,rate:-1,overhead:-3,profit:NaN,tax:Infinity});assert.equal(t.total,0);
console.log('PASS: purchasing mass, service toggle, OH/profit/tax order, edits and invalid input.');
