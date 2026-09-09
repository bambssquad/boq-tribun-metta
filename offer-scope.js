'use strict';
function offerScopeTotals(base,mode,categories,settings){
 const names={all:'Semua pekerjaan',material:'Material',labor:'Upah jasa',custom:'Kategori pilihan'};
 const items=base.items.filter(r=>mode==='all'||mode==='material'&&r.category==='Material'||mode==='labor'&&r.category==='Upah'||mode==='custom'&&categories.includes(r.category));
 const groups={};items.forEach(r=>groups[r.category]=(groups[r.category]||0)+r.amount);
 const safe=x=>Number.isFinite(+x)?Math.max(0,+x):0,direct=items.reduce((n,r)=>n+r.amount,0),oh=Math.round(direct*safe(settings.overhead)/100),profit=Math.round((direct+oh)*safe(settings.profit)/100),pretax=direct+oh+profit,tax=Math.round(pretax*safe(settings.tax)/100);
 return {...base,items,groups,direct,oh,profit,pretax,tax,total:pretax+tax,scopeLabel:mode==='custom'?names.custom+' — '+(categories.join(', ')||'belum dipilih'):names[mode]};
}
if(typeof module!=='undefined')module.exports={offerScopeTotals};
