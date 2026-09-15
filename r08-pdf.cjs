// Rebuild the explicitly labelled reference PDF; browser exports use live state.
const fs=require('fs'),vm=require('vm'),B=require('./boq-revision.js');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const data=read('assets/r05/boq.json');data.r08=read('assets/r08/data.json');data.design_scope=read('assets/r07/design-scope.json');
const ctx={console,TextEncoder,TextDecoder,Uint8Array,ArrayBuffer,Blob,atob,btoa,setTimeout};
ctx.window=ctx;ctx.self=ctx;ctx.navigator={};vm.createContext(ctx);
for(const p of ['vendor/jspdf.umd.min.js','vendor/jspdf.plugin.autotable.min.js'])vm.runInContext(fs.readFileSync(p,'utf8'),ctx);
const s={...B.defaults(),scope:'r08',case:'model',shs:'reference',mesh:'m20_25',extras:true,subtotals:true,componentSubtotals:true,kgExplanation:true,date:'2026-09-15'};
const pdf=B.pdf(data,s,ctx.jspdf.jsPDF);
fs.writeFileSync('assets/r08/METTA-R08-RAB-portrait.pdf',Buffer.from(pdf.output('arraybuffer')));
console.log({pages:pdf.getNumberOfPages(),...B.totals(B.rows(data,s)),kg:B.massSummary(data,s).kg});
