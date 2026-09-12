'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const B=require('./boq-revision.js'),data=JSON.parse(fs.readFileSync('assets/r05/boq.json','utf8'));
const context={console,TextEncoder,TextDecoder,Uint8Array,ArrayBuffer,Blob,atob,btoa,setTimeout};
context.window=context;context.self=context;context.navigator={};vm.createContext(context);
for(const file of ['vendor/jspdf.umd.min.js','vendor/jspdf.plugin.autotable.min.js'])vm.runInContext(fs.readFileSync(file,'utf8'),context);
const state={...B.defaults(),date:'2026-09-12',project:'METTA R07 - RAB UNTUK PEMERIKSAAN',extras:true,subtotals:true,componentSubtotals:true};
state.notes='DRAF UNTUK PEMERIKSAAN. Belum menjadi pesanan bahan atau nilai kontrak final.\n'+
 'Acuan: RHS 50x100x2,3; SHS 40x40 acuan 2,0/2,8; pembelian termasuk sisa potong; seluruh biaya pelengkap yang tersedia aktif.\n'+
 'BOQ dasar Rp240.204.729 + pelengkap Rp29.515.000 = Rp269.719.729. Upah Rp90.307.093; material Rp179.412.636.\n'+
 'Belum termasuk overhead, laba dan pajak tambahan. Dampak revisi railing, angkur, penguatan lantai, data pemasok dan logistik aktual belum pasti; item belum dihargai tidak berarti gratis.\n'+
 'RHS model + usulan: pola101batang x32,5kg =3282,5kg; seluruh baja acuan9570,466kg.54batang dari Excel adalah1620/30, bukan daftar potong model.\n'+
 'Subtotal per komponen hanya rekap dari biaya yang sama, tidak ditambahkan lagi. Angka di sini adalah data dasar audit, tidak mengambil edit tersimpan pada browser pengguna.\n'+data.notes.join('\n');
const total=B.totals(B.rows(data,state));assert.equal(total.total,269719729);assert.equal(total.labor,90307093);assert.equal(total.material,179412636);
const doc=B.pdf(data,state,context.jspdf.jsPDF);doc.setCreationDate("D:20260912000000+00'00'");doc.setFileId('A0072026091200000000000000000001');
fs.writeFileSync('assets/r07/METTA-R07-RAB-lengkap.pdf',Buffer.from(doc.output('arraybuffer')));
console.log('RAB PDF:',doc.getNumberOfPages(),'pages;',total.total,'IDR; 40 rows including extras.');
