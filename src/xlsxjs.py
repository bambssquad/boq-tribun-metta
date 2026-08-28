# -*- coding: utf-8 -*-
"""Penulis .xlsx murni di browser — zip STORED + CRC32, rumus hidup, tanpa library."""

JS = r"""
// ---------------- penulis XLSX (tanpa library) ----------------
const XL=(function(){
  const T=(()=>{const t=new Uint32Array(256);
    for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0;}
    return t;})();
  const crc32=b=>{let c=0xFFFFFFFF;for(let i=0;i<b.length;i++)c=T[(c^b[i])&0xFF]^(c>>>8);
    return (c^0xFFFFFFFF)>>>0;};
  const enc=s=>new TextEncoder().encode(s);
  const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');

  function zip(files){
    const parts=[], central=[]; let off=0;
    files.forEach(f=>{
      const nm=enc(f.name), data=typeof f.data==='string'?enc(f.data):f.data;
      const c=crc32(data), n=data.length;
      const lh=new Uint8Array(30+nm.length), dv=new DataView(lh.buffer);
      dv.setUint32(0,0x04034b50,true); dv.setUint16(4,20,true); dv.setUint16(6,0,true);
      dv.setUint16(8,0,true); dv.setUint16(10,0,true); dv.setUint16(12,0x2100,true);
      dv.setUint32(14,c,true); dv.setUint32(18,n,true); dv.setUint32(22,n,true);
      dv.setUint16(26,nm.length,true); dv.setUint16(28,0,true);
      lh.set(nm,30);
      parts.push(lh,data);
      const ch=new Uint8Array(46+nm.length), cv=new DataView(ch.buffer);
      cv.setUint32(0,0x02014b50,true); cv.setUint16(4,20,true); cv.setUint16(6,20,true);
      cv.setUint16(8,0,true); cv.setUint16(10,0,true); cv.setUint16(12,0,true);
      cv.setUint16(14,0x2100,true);
      cv.setUint32(16,c,true); cv.setUint32(20,n,true); cv.setUint32(24,n,true);
      cv.setUint16(28,nm.length,true); cv.setUint32(42,off,true);
      ch.set(nm,46);
      central.push(ch);
      off+=lh.length+n;
    });
    let csize=0; central.forEach(c=>csize+=c.length);
    const end=new Uint8Array(22), ev=new DataView(end.buffer);
    ev.setUint32(0,0x06054b50,true); ev.setUint16(8,central.length,true);
    ev.setUint16(10,central.length,true); ev.setUint32(12,csize,true); ev.setUint32(16,off,true);
    let total=off+csize+22, out=new Uint8Array(total), p=0;
    parts.forEach(a=>{out.set(a,p);p+=a.length;});
    central.forEach(a=>{out.set(a,p);p+=a.length;});
    out.set(end,p);
    return out;
  }

  // ---- sel ----
  const col=i=>{let s='';i++;while(i>0){const m=(i-1)%26;s=String.fromCharCode(65+m)+s;i=(i-m-1)/26;}return s;};
  const S={def:0,bold:1,n2:2,n0:3,rp:4,head:5,inp:6,title:7,sec:8};
  const cell=(r,c,v)=>{
    const ref=col(c)+r;
    if(v==null||v==='') return '';
    if(typeof v!=='object')
      return `<c r="${ref}" t="inlineStr"><is><t xml:space="preserve">${esc(v)}</t></is></c>`;
    const s=v.s!=null ? ` s="${v.s}"` : '';
    if(v.f!=null && v.f!=='') return `<c r="${ref}"${s}><f>${esc(v.f)}</f></c>`;
    if(v.n!=null && v.n!=='' && isFinite(v.n)) return `<c r="${ref}"${s}><v>${v.n}</v></c>`;
    if(v.t!=null && v.t!=='')
      return `<c r="${ref}"${s} t="inlineStr"><is><t xml:space="preserve">${esc(v.t)}</t></is></c>`;
    return `<c r="${ref}"${s}/>`;   // sel kosong bergaya (mis. kolom harga yang belum diisi)
  };
  const sheet=(rows,cols)=>{
    let x='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      +'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
    if(cols) x+='<cols>'+cols.map((w,i)=>`<col min="${i+1}" max="${i+1}" width="${w}" customWidth="1"/>`).join('')+'</cols>';
    x+='<sheetData>';
    rows.forEach((row,ri)=>{
      if(!row) return;
      x+=`<row r="${ri+1}">`+row.map((v,ci)=>v==null?'':cell(ri+1,ci,v)).join('')+'</row>';
    });
    return x+'</sheetData></worksheet>';
  };

  const STYLES='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    +'<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    +'<numFmts count="3">'
    +'<numFmt numFmtId="164" formatCode="&quot;Rp&quot;#,##0"/>'
    +'<numFmt numFmtId="165" formatCode="#,##0.00"/>'
    +'<numFmt numFmtId="166" formatCode="#,##0"/></numFmts>'
    +'<fonts count="4">'
    +'<font><sz val="11"/><name val="Calibri"/></font>'
    +'<font><b/><sz val="11"/><name val="Calibri"/></font>'
    +'<font><b/><sz val="16"/><name val="Calibri"/></font>'
    +'<font><b/><sz val="11"/><color rgb="FF9A6A05"/><name val="Calibri"/></font></fonts>'
    +'<fills count="4"><fill><patternFill patternType="none"/></fill>'
    +'<fill><patternFill patternType="gray125"/></fill>'
    +'<fill><patternFill patternType="solid"><fgColor rgb="FFFFF3C4"/><bgColor indexed="64"/></patternFill></fill>'
    +'<fill><patternFill patternType="solid"><fgColor rgb="FFE8E4DA"/><bgColor indexed="64"/></patternFill></fill></fills>'
    +'<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    +'<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    +'<cellXfs count="9">'
    +'<xf xfId="0" numFmtId="0" fontId="0" fillId="0" borderId="0"/>'
    +'<xf xfId="0" numFmtId="0" fontId="1" fillId="0" borderId="0" applyFont="1"/>'
    +'<xf xfId="0" numFmtId="165" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/>'
    +'<xf xfId="0" numFmtId="166" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/>'
    +'<xf xfId="0" numFmtId="164" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/>'
    +'<xf xfId="0" numFmtId="0" fontId="1" fillId="3" borderId="0" applyFont="1" applyFill="1"/>'
    +'<xf xfId="0" numFmtId="164" fontId="1" fillId="2" borderId="0" applyNumberFormat="1" applyFont="1" applyFill="1"/>'
    +'<xf xfId="0" numFmtId="0" fontId="2" fillId="0" borderId="0" applyFont="1"/>'
    +'<xf xfId="0" numFmtId="0" fontId="3" fillId="0" borderId="0" applyFont="1"/>'
    +'</cellXfs></styleSheet>';

  function book(sheets){
    const names=sheets.map(s=>s.name);
    const files=[
      {name:'[Content_Types].xml', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        +'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        +'<Default Extension="xml" ContentType="application/xml"/>'
        +'<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        + names.map((n,i)=>`<Override PartName="/xl/worksheets/sheet${i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')
        +'<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        +'</Types>'},
      {name:'_rels/.rels', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        +'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        +'</Relationships>'},
      {name:'xl/workbook.xml', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        +'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
        + names.map((n,i)=>`<sheet name="${esc(n)}" sheetId="${i+1}" r:id="rId${i+1}"/>`).join('')
        +'</sheets><calcPr calcId="0" fullCalcOnLoad="1"/></workbook>'},
      {name:'xl/_rels/workbook.xml.rels', data:'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        +'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + names.map((n,i)=>`<Relationship Id="rId${i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i+1}.xml"/>`).join('')
        + `<Relationship Id="rId${names.length+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>`
        +'</Relationships>'},
      {name:'xl/styles.xml', data:STYLES},
    ];
    sheets.forEach((s,i)=>files.push({name:`xl/worksheets/sheet${i+1}.xml`, data:sheet(s.rows,s.cols)}));
    return zip(files);
  }
  return {book, S};
})();
"""
