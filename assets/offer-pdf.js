'use strict';
const MettaPDF=(()=>{
 let ready;
 const clean=s=>String(s??'').replace(/[–—]/g,'-').replace(/×/g,'x').replace(/↗/g,'');
 function build(o,t,s,PDF){
 const d=new PDF({unit:'mm',format:'a4'});let y=18;
 const text=(str,size=10)=>{d.setFontSize(size);const lines=d.splitTextToSize(clean(str),180);for(const line of lines){if(y>270){d.addPage();y=18;}d.text(line,15,y);y+=size*.45;}y+=3;};
 const table=(head,body)=>{if(y>250){d.addPage();y=18;}d.autoTable({startY:y,head:[head.map(clean)],body:body.map(r=>r.map(clean)),margin:{left:15,right:15,top:18,bottom:20},columnStyles:Object.fromEntries(head.map((h,i)=>[i,/Nilai|Harga|Jumlah|Tagihan|Volume|^%$/.test(h)?{halign:'right'}:{}])),styles:{fontSize:8,cellPadding:2.4,overflow:'linebreak',lineColor:210,lineWidth:.1},headStyles:{fillColor:20,textColor:255},alternateRowStyles:{fillColor:247},rowPageBreak:'avoid'});y=d.lastAutoTable.finalY+8;};
 text('SAP / '+o.company,17);text([o.address,o.phone,o.email].filter(Boolean).join(' | '),9);text('SURAT PENAWARAN HARGA - METTA',14);text('Lingkup: '+t.scopeLabel);table(['Identitas','Keterangan'],[['Nomor',o.number],['Tanggal',o.date],['Klien',o.client],['Lokasi',o.location],['Masa berlaku',o.valid+' hari'],['Pelaksanaan',o.start+' s.d. '+o.end]]);
 const rp=n=>'Rp '+new Intl.NumberFormat('id-ID').format(n);
 table(['Rekap biaya','Nilai'],[...BOQGroups.groups(t.items,o.groupMode).map(g=>[g.name,g.amount]),['Biaya langsung',t.direct],['Overhead '+s.overhead+'%',t.oh],['Laba '+s.profit+'%',t.profit],['Pajak '+s.tax+'%',t.tax],['TOTAL PENAWARAN',t.total]].map(([a,b])=>[a,rp(b)]));
 const a=OfferDocument.amounts(t.total,o.terms);table(['Termin / syarat pembayaran','%','Nilai'],o.terms.map((r,i)=>[r.name,r.pct,rp(a.values[i])]));
 if(o.termDetail){for(let i=0;i<o.terms.length;i++){if(y>230){d.addPage();y=18;}text('Rincian termin '+(i+1)+' - '+o.terms[i].name,11);table(['Pekerjaan / biaya','Nilai pekerjaan','Tagihan termin'],BudgetEdit.termRows(t,o.terms).map(r=>[r[0],rp(r[1]),rp(r[i+2])]));}}
 text('Ketentuan penawaran',11);text(o.notes,9);if(o.bank)text('Pembayaran: '+o.bank,9);if(y>225){d.addPage();y=18;}text('Diajukan oleh: '+o.company+'                         Disetujui oleh: '+o.client,9);y+=24;text((o.signer||'Nama / tanda tangan')+'                         Nama / tanda tangan',9);text(o.role,9);
 if(o.detail!==false){d.addPage();y=18;text('LAMPIRAN - RINCIAN PEKERJAAN',14);for(const group of BOQGroups.groups(t.items,o.groupMode)){if(y>225){d.addPage();y=18;}text(group.name+' - '+rp(group.amount),11);table(['Kode / uraian','Volume','Sat.','Harga','Jumlah'],group.items.map(r=>[r.code+' / '+r.name+(r.supplier?'\n'+r.supplier:''),new Intl.NumberFormat('id-ID',{maximumFractionDigits:4}).format(r.qty),r.unit,rp(r.price),rp(r.amount)]));}text('Total penawaran: '+rp(t.total),11);}
 const pages=d.getNumberOfPages();for(let i=1;i<=pages;i++){d.setPage(i);d.setFontSize(8);d.text(clean((o.number||'SAP')+' | METTA'),15,287);d.text(i+' / '+pages,195,287,{align:'right'});}return d;
 }
 function load(src){return new Promise((resolve,reject)=>{const el=document.createElement('script');el.src=src;el.onload=resolve;el.onerror=()=>reject(Error('PDF library unavailable'));document.head.append(el);});}
 async function download(o,t,s){if(!ready)ready=load('assets/vendor/jspdf.umd.min.js').then(()=>load('assets/vendor/jspdf.plugin.autotable.min.js')).catch(e=>{ready=null;throw e;});await ready;build(o,t,s,window.jspdf.jsPDF).save('SAP-Penawaran-METTA.pdf');}
 return {build,download};
})();
if(typeof window!=='undefined')window.MettaPDF=MettaPDF;
if(typeof module!=='undefined')module.exports=MettaPDF;
