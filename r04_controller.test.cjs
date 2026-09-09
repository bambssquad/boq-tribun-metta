const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(){this.events={};this.dataset={};this.attrs={};this.value='';this.checked=false;this.innerHTML='';}
 addEventListener(k,f){this.events[k]=f;}setAttribute(k,v){this.attrs[k]=v;}
 showModal(){this.open=true;}close(){this.open=false;}
 click(){this.events.click?.({target:this});}change(){this.events.change?.({target:this});}
}
(async()=>{
 const data=JSON.parse(fs.readFileSync('assets/r04/data.json','utf8'));
 const els={},get=id=>els[id]??=new Element();
 const filters=['Semua','Material','Bahan habis pakai','Upah','Peralatan dan logistik'].map(f=>{const b=new Element();b.dataset.filter=f;return b;});
 const drawings=Array.from({length:6},(_,i)=>{const b=new Element();b.dataset.sheet='T-0'+(i+1);b.innerText=b.dataset.sheet;return b;});
 const formats=['xlsx','pdf'].map(f=>{const b=new Element();b.dataset.rabFormat=f;return b;});
 const document={getElementById:get,querySelectorAll:q=>q==='[data-filter]'?filters:q==='[data-sheet]'?drawings:q==='[data-rab-format]'?formats:[],createElement:()=>new Element()};
 let saved={},blob,printed=false;
 const window={addEventListener(){},print(){printed=true;}};
 const c={document,window,Intl,Date,Number,Math,JSON,Promise,structuredClone,Blob,console,setTimeout,URL:{createObjectURL:b=>(blob=b,'blob:test'),revokeObjectURL(){}},localStorage:{getItem:()=>null,setItem:(k,v)=>saved[k]=v},fetch:async()=>({ok:true,json:async()=>structuredClone(data)}),createDrawingPanZoom:()=>({reset(){}})};
 c.TextEncoder=TextEncoder;c.Uint8Array=Uint8Array;c.Uint32Array=Uint32Array;c.DataView=DataView;
 vm.createContext(c);vm.runInContext(fs.readFileSync('dist/assets/r04/xlsx.js','utf8'),c);
 vm.runInContext(fs.readFileSync('offer-scope.js','utf8'),c);
 vm.runInContext(fs.readFileSync('client-offer.js','utf8'),c);
 vm.runInContext(fs.readFileSync('r04_app.js','utf8'),c);
 await new Promise(r=>setImmediate(r));
 assert.equal((get('rows').innerHTML.match(/<tr>/g)||[]).length,data.rows.length);
 assert.ok(get('totals').innerHTML.includes('TOTAL ANGGARAN'));
 assert.ok(get('offer-fields').innerHTML.includes('SELARAS ADHI PERKASA'));assert.ok(get('offer-print').innerHTML.includes('Lampiran — Rincian RAB'));
 assert.equal(get('offer-preview').innerHTML,get('offer-print').innerHTML);
 const beforeInput=get('offer-terms').innerHTML;
 get('offer-terms').events.input({target:{dataset:{term:'0',field:'name'},value:'DP setelah kontrak'}});
 assert.ok(get('offer-preview').innerHTML.includes('DP setelah kontrak'));assert.equal(get('offer-terms').innerHTML,beforeInput);
 get('offer-terms').events.input({target:{dataset:{term:'0',field:'pct'},value:'20'}});assert.ok(get('offer-term-total').textContent.includes('90.00%'));assert.equal(get('offer-preview').innerHTML,get('offer-print').innerHTML);
 get('offer-terms').events.change({target:{dataset:{term:'0',field:'pct'},value:'25'}});assert.ok(get('offer-term-total').textContent.includes('95.00%'));
 get('offer-default-terms').click();assert.ok(get('offer-term-total').textContent.includes('100.00%'));
 filters[2].click();assert.ok((get('rows').innerHTML.match(/<tr>/g)||[]).length<data.rows.length);
 get('service').checked=false;get('service').change();assert.ok(get('offer-note').textContent.includes('nonaktif'));
 get('print').click();assert.ok(printed);assert.equal((get('rows').innerHTML.match(/<tr>/g)||[]).length,data.rows.length);
 assert.equal(filters[0].attrs['aria-pressed'],'true');
 drawings[5].click();assert.equal(get('sheet-image').src,'assets/r04/T-06.svg');assert.ok(get('drawing-dialog').open);
 get('close').click();assert.equal(get('drawing-dialog').open,false);
 get('csv').click();const csv=await blob.text();assert.ok(csv.includes('Total'));assert.ok(csv.includes('Fabrikasi + pemasangan baja'));
 get('json').click();const offer=JSON.parse(await blob.text());assert.equal(offer.items.find(r=>r.code==='U01').amount,0);assert.ok(offer.total>0);
 get('reset').click();assert.equal(get('service').checked,true);assert.equal(get('rate').value,6000);
 assert.ok(Object.keys(saved).length);
 filters[2].click();get('rab-download-action').click();
 const bytes=Buffer.from(await blob.arrayBuffer());assert.equal(bytes.readUInt16LE(0),0x4b50);
 assert.ok(bytes.includes(Buffer.from('REKAP')));assert.ok(bytes.includes(Buffer.from('PENGATURAN')));
 assert.ok(bytes.includes(Buffer.from('U01')));assert.ok(bytes.includes(Buffer.from('TOTAL ANGGARAN')));
 assert.ok(bytes.includes(Buffer.from('Sentral Mur Baut Surabaya')));assert.ok(bytes.includes(Buffer.from('PT Jaya Metal Surabaya')));
 formats[1].click();assert.equal(get('rab-download-action').textContent,'Simpan PDF');printed=false;get('rab-download-action').click();assert.ok(printed);assert.equal((get('rows').innerHTML.match(/<tr>/g)||[]).length,data.rows.length);
 formats[0].click();assert.equal(formats[0].attrs['aria-pressed'],'true');
 get('offer-scope').value='labor';get('offer-scope').change();assert.ok(window.MettaOffer.getScope().items.every(r=>r.category==='Upah'));
 assert.ok(window.MettaOffer.getScope().items.find(r=>r.code==='U01').amount>0);
 get('offer-scope-overhead').value='12';get('offer-scope-overhead').change();
 get('offer-terms').events.change({target:{dataset:{term:'0',field:'pct'},value:'25'}});
 get('offer-scope').value='material';get('offer-scope').change();assert.ok(window.MettaOffer.getScope().items.every(r=>r.category==='Material'));assert.equal(window.MettaOffer.get().terms[0].pct,30);
 get('offer-scope').value='labor';get('offer-scope').change();assert.equal(get('offer-scope-overhead').value,12);assert.equal(window.MettaOffer.get().terms[0].pct,25);
 get('offer-excel').click();const scoped=Buffer.from(await blob.arrayBuffer());assert.ok(scoped.includes(Buffer.from('>U01<')));assert.ok(!scoped.includes(Buffer.from('>M01<')));
 get('offer-scope').value='custom';get('offer-scope').change();assert.equal(get('offer-pdf').disabled,true);
 get('offer-scope-categories').events.change({target:{dataset:{offerCategory:'Bahan habis pakai'},checked:true}});assert.ok(window.MettaOffer.getScope().items.every(r=>r.category==='Bahan habis pakai'));assert.equal(get('offer-pdf').disabled,false);
 console.log('PASS: R04 fetch/render, category filter, service toggle, complete print, six-sheet zoom dialog, CSV/JSON and reset.');
})().catch(e=>{console.error(e);process.exitCode=1;});
