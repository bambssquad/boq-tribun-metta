// Shared purchasing-weight calculation. Waste enters stock counts, never twice.
function computePurchaseService(rows, barLength, sheetArea, hollowBasis, plateBasis, enabled, rate) {
  const positive=x=>Number.isFinite(+x)&&+x>0?+x:0;
  const bar=positive(barLength)||6, sheet=positive(sheetArea)||2.88;
  const items=[
    ...rows.hollow.map(r=>{const b=hollowBasis(r),units=Math.ceil(positive(b.bars));return {name:r.nm,stock:'lonjor',units,netKg:positive(r.L)*positive(r.kg),purchaseKg:units*bar*positive(r.kg)};}),
    ...rows.plate.map(r=>{const b=plateBasis(r),units=Math.ceil(positive(b.sh)),density=positive(r.t)*7.85+positive(r.sur);return {name:r.nm,stock:'lembar',units,netKg:positive(r.A)*density,purchaseKg:units*sheet*density};})
  ];
  const kg=items.reduce((sum,r)=>sum+r.purchaseKg,0);
  const netKg=items.reduce((sum,r)=>sum+r.netKg,0);
  const unitRate=positive(rate);
  return {items,kg,netKg,extraKg:kg-netKg,rate:unitRate,cost:enabled?kg*unitRate:0,enabled:!!enabled};
}
if(typeof module!=='undefined')module.exports={computePurchaseService};
