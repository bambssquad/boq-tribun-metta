const assert=require('node:assert/strict'),{offerScopeTotals}=require('./offer-scope.js'),{r04Totals}=require('./r04_app.js'),d=require('./assets/r04/data.json');
const settings={...d.defaults,rate:6000},base=r04Totals(d.rows,settings);
assert.equal(offerScopeTotals(base,'all',[],settings).total,base.total);
const labor=offerScopeTotals(base,'labor',[],settings);assert.equal(labor.items.length,d.rows.filter(r=>r.category==='Upah').length);assert.equal(labor.items.find(r=>r.code==='U01').amount,base.items.find(r=>r.code==='U01').amount);
assert.equal(labor.direct,labor.items.reduce((n,r)=>n+r.amount,0));assert.equal(labor.oh,Math.round(labor.direct*settings.overhead/100));
const empty=offerScopeTotals(base,'custom',[],settings);assert.equal(empty.total,0);assert.equal(empty.items.length,0);
const custom=offerScopeTotals(base,'custom',['Material','Upah'],{overhead:0,profit:0,tax:0});assert.equal(custom.total,base.items.filter(r=>['Material','Upah'].includes(r.category)).reduce((n,r)=>n+r.amount,0));
console.log('PASS: scope totals, full purchasing basis for labor, custom categories and independent rates.');
