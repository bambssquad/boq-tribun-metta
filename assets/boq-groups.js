'use strict';
const BOQGroups=(()=>{
 const names=['Kolom tribun','Balok tribun','Kolom & balok tribun','Dek tribun','Tangga','Penutup riser & sisi','Bracing & ikatan','Railing & sandaran','Sambungan & tumpuan','Finishing','Fabrikasi & pemasangan','Bahan bantu bengkel','Logistik & pekerjaan pendukung'];
 const mapping={M01:'Kolom & balok tribun',M02:'Pengaku dek & railing',M03:'Railing & sandaran',M04:'Dek tribun',M05:'Tangga',M06:'Penutup riser & sisi',M07:'Sambungan & tumpuan',M08:'Sambungan & tumpuan',M09:'Railing & sandaran',M10:'Sambungan & tumpuan',M11:'Tangga',M12:'Tangga',M13:'Tangga',M17:'Bracing & ikatan',M22:'Railing & sandaran',U01:'Fabrikasi & pemasangan',U02:'Tangga',U03:'Finishing',U04:'Railing & sandaran'};
 function component(r){if(r.component?.trim())return r.component.trim();const code=r.code.replace(/^UK-/,'');if(mapping[code])return mapping[code];if(/^M1[456]/.test(code))return 'Sambungan & tumpuan';if(/^M(18|19|20|21)$/.test(code)||code==='C05')return 'Finishing';if(/^C/.test(code))return 'Bahan bantu bengkel';if(/^U/.test(code))return 'Fabrikasi & pemasangan';return 'Logistik & pekerjaan pendukung';}
 function groups(items,mode='component'){const out=new Map();for(const r of items){const name=mode==='category'?r.category:component(r);if(!out.has(name))out.set(name,{name,items:[],amount:0});const g=out.get(name);g.items.push(r);g.amount+=r.amount;}return [...out.values()];}
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function html(items,mode,row,cols){return groups(items,mode).map(g=>`<tr class="group-heading"><th colspan="${cols}">${esc(g.name)} — Rp ${g.amount.toLocaleString('id-ID')}</th></tr>`+g.items.map(row).join('')).join('');}
 function excel(items,mode,row,cols){return groups(items,mode).flatMap(g=>[(()=>{const a=Array(cols).fill('');a[0]=g.name;a[Math.min(6,cols-1)]=g.amount;return a;})(),...g.items.map(row)]);}
 return {component,groups,html,excel,names};
})();
if(typeof module!=='undefined')module.exports=BOQGroups;
