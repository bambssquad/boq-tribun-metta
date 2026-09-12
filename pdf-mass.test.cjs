const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),B=require('./boq-revision.js');
const data=JSON.parse(fs.readFileSync('assets/r05/boq.json','utf8'));
data.design_scope=JSON.parse(fs.readFileSync('assets/r07/design-scope.json','utf8'));
const ctx={console,TextEncoder,TextDecoder,Uint8Array,ArrayBuffer,Blob,atob,btoa,setTimeout};
ctx.window=ctx;ctx.self=ctx;ctx.navigator={};vm.createContext(ctx);
for(const path of ['vendor/jspdf.umd.min.js','vendor/jspdf.plugin.autotable.min.js'])vm.runInContext(fs.readFileSync(path,'utf8'),ctx);
for(const scope of ['native','full'])for(const thick of ['h16','h20','model'])for(const basis of ['purchase','net']){
 const s={...B.defaults(),scope,case:thick,shs:'s17',basis};const tables=[];
 function PDF(options){const d=new ctx.jspdf.jsPDF(options),table=d.autoTable;d.autoTable=function(options){tables.push(options);return table.call(this,options);};return d;}
 const pdf=B.pdf(data,s,PDF),mass=B.massSummary(data,s),kg=tables.find(t=>t.head[0][0]==='Profil / ketebalan terpilih');
 assert(kg);assert.equal(kg.body[0][3],B.fmt(mass.profiles[0].kg,3));
 assert.equal(kg.foot[2][3],B.fmt(mass.kg,3));
 const components=tables.find(t=>t.head[0][0]==='Komponen (baris satuan kg)');
 assert.equal(components.foot[0][1],B.fmt(mass.kg,3));
 assert.equal(components.foot[0][2],B.fmt(mass.bars,4));
 if(basis==='purchase')assert.equal(kg.body[0][2],String(scope==='native'?97:101));
 assert(Buffer.from(pdf.output('arraybuffer')).subarray(0,4).equals(Buffer.from('%PDF')));
 B.edit(s,'X01','qty',10);assert.notEqual(B.massSummary(data,s).kg,mass.kg);
}
console.log('PASS: 12 actual PDF exports follow scope/thickness/basis with matching profile and component kg/bar subtotals.');
