'use strict';
const BudgetEdit=(()=>{
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function labor(rows,mode){
  const keep=rows.filter(r=>r.code!=='U01'&&!r.laborTemplate);
  const row=(code,name,qty,unit,price,basis)=>({code,category:'Upah',name,qty,unit,price,basis,status:'Editable',kg_per_unit:0,autoWeight:false,laborTemplate:true});
  if(mode==='activity')return [...keep,...['Pemotongan profil dan pelat','Pengelasan dan perakitan bengkel','Pengeboran sambungan','Pemasangan di lokasi'].map((n,i)=>row('UA'+(i+1),n,'','unit','','Isi volume pekerjaan dan tarif; tekuk, cat dan kayu tetap pada baris tersendiri.'))];
  return [...keep,...rows.filter(r=>r.category==='Material'&&r.kg_per_unit>0).map(r=>row('UK-'+r.code,'Fabrikasi / pemasangan — '+r.name,r.qty*r.kg_per_unit,'kg',6000,'Berat pembelian komponen '+r.code+'; sesuaikan ke berat pekerjaan kontrak. Tidak termasuk tekuk, cat dan kayu.'))];
 }
 function termRows(t,terms){
 const rows=[...BOQGroups.groups(t.items,(typeof window!=='undefined'?window.MettaOffer?.get()?.groupMode:'component')||'component').flatMap(g=>g.items.map(r=>[g.name+' / '+r.code+' / '+r.name,r.amount])),['Overhead',t.oh],['Laba',t.profit],['Pajak',t.tax]],targets=OfferDocument.amounts(t.total,terms),remaining=targets.values.slice();let left=t.total,cumulative=0;
 return rows.map(([name,amount])=>{let shares;
 if(Math.abs(targets.sum-100)<1e-8){let acc=0,previous=0;shares=remaining.map(v=>{acc+=v;const next=left?Math.round(amount*acc/left):0,part=next-previous;previous=next;return part;});shares.forEach((v,i)=>remaining[i]-=v);left-=amount;}
 else {shares=terms.map((term,i)=>Math.round((cumulative+amount)*term.pct/100)-Math.round(cumulative*term.pct/100));cumulative+=amount;}
 return [name,amount,...shares];});
 }

 return {esc,labor,termRows};
})();
if(typeof module!=='undefined')module.exports=BudgetEdit;
if(typeof document!=='undefined')(()=>{
 const $=id=>document.getElementById(id),e=BudgetEdit.esc;
 const fields=[['code','Kode'],['name','Uraian'],['category','Kategori'],['qty','Volume','number'],['unit','Satuan'],['price','Harga satuan','number'],['manualAmount','Jumlah manual (kosong = otomatis)','number'],['supplier','Pemasok'],['specification','Spesifikasi'],['basis','Dasar volume / catatan'],['status','Status'],['supplier_contact','Kontak'],['price_basis','Dasar harga'],['component','Kelompok komponen'],['kg_per_unit','kg per satuan','number']];
 let target='offer',view='Upah';
 const api=()=>target==='main'?window.MettaRAB:window.MettaOffer;
 const get=()=>target==='main'?api().get():api().getRows();
 const set=rows=>{if(target==='main'){window.MettaOffer.clearRows();api().set(rows);}else api().setRows(rows);};
 function render(){if(!window.MettaRAB)return;const id=target+':'+$('offer-scope').value;const state=templates[id];if(state?.active){state[state.active]=get();try{localStorage.setItem('metta-labor-templates-v1',JSON.stringify(templates));}catch{}}$('labor-layout').value=state?.active||'';const rows=get();$('budget-editor-rows').innerHTML=rows.map((r,i)=>view!=='Semua'&&r.category!==view?'':`<tr>${fields.map(([k,label,type])=>`<td><input aria-label="${e(label+' '+r.code)}" data-row="${i}" data-col="${k}" type="${type||'text'}" ${type?'min="0" step="any"':''} ${k==='unit'?'list="budget-units"':''} value="${e(k==='component'?BOQGroups.component(r):r[k])}"></td>`).join('')}<td>${Math.round(r.manualAmount??(+r.qty*+r.price))}</td><td><button data-delete="${i}">Hapus</button></td></tr>`).join('');}
 $('budget-target').addEventListener('change',ev=>{target=ev.target.value;render();});$('budget-category').addEventListener('change',ev=>{view=ev.target.value;render();});
 $('budget-editor-rows').addEventListener('change',ev=>{const {row,col}=ev.target.dataset;if(row===undefined)return;const rows=get();const numeric=['qty','price','manualAmount','kg_per_unit'].includes(col);rows[+row][col]=numeric?(ev.target.value===''?(col==='manualAmount'?null:''):Math.max(0,+ev.target.value||0)):ev.target.value;rows[+row].autoWeight=false;set(rows);render();});
 $('budget-editor-rows').addEventListener('click',ev=>{const i=ev.target.dataset.delete;if(i===undefined)return;const rows=get();rows.splice(+i,1);set(rows);render();});
 $('budget-add').addEventListener('click',()=>{const rows=get();rows.push({code:'X'+Date.now(),name:'Pekerjaan tambahan',category:view==='Semua'?'Upah':view,qty:'',unit:'unit',price:'',kg_per_unit:0,autoWeight:false,basis:'',status:'Editable'});set(rows);render();});
 let templates={};try{templates=JSON.parse(localStorage.getItem('metta-labor-templates-v1'))||{};}catch{};$('labor-layout').addEventListener('change',ev=>{const mode=ev.target.value;if(!mode)return;const id=target+':'+$('offer-scope').value;templates[id]??={};const previous=templates[id].active;if(previous)templates[id][previous]=get();const rows=templates[id][mode]||BudgetEdit.labor(get(),mode);set(rows);templates[id].active=mode;try{localStorage.setItem('metta-labor-templates-v1',JSON.stringify(templates));}catch{};view='Upah';$('budget-category').value=view;render();});
 for(const id of ['offer-detail','term-detail'])$(id).addEventListener('change',()=>{const o=window.MettaOffer.get();o.detail=$('offer-detail').checked;o.termDetail=$('term-detail').checked;window.MettaOffer.refresh();});
 window.addEventListener('rab-ready',()=>{const o=window.MettaOffer.get();$('offer-detail').checked=o.detail!==false;$('term-detail').checked=!!o.termDetail;render();});$('offer-scope').addEventListener('change',render);
})();
