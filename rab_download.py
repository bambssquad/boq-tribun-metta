"""Visible format picker using the existing local XLSX writer and print actions."""
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent

def build(dist):
 tools=BeautifulSoup((dist/'tools.html').read_text(encoding='utf-8'),'html.parser')
 script=next(s.text for s in tools.find_all('script') if 'const XL=(function()' in s.text)
 start=script.index('const XL=(function()')
 end=script.index('})();',script.index('return {book, S};',start))+5
 (dist/'assets/r04/xlsx.js').write_text(script[start:end],encoding='utf-8')
 for name,target in [('tools.html','#boq'),('r04.html','#rab')]:
  soup=tools if name=='tools.html' else BeautifulSoup((dist/name).read_text(encoding='utf-8'),'html.parser')
  bar=BeautifulSoup('''<div class="rab-download" role="group" aria-label="Unduh RAB"><strong>Unduh RAB</strong><div class="rab-formats" role="group" aria-label="Format berkas"><button type="button" data-rab-format="xlsx" aria-pressed="true">Excel (.xlsx)</button><button type="button" data-rab-format="pdf" aria-pressed="false">PDF</button></div><button type="button" id="rab-download-action">Unduh Excel</button><span id="rab-download-hint">Menggunakan harga dan pengaturan saat ini.</span></div>''','html.parser')
  soup.select_one(target).select_one('h2').insert_after(bar)
  if name=='r04.html':
   lib=soup.new_tag('script',src='assets/r04/xlsx.js');soup.select_one('script[src="assets/r04/app.js"]').insert_before(lib)
  else:
   js=soup.new_tag('script');js.string="""(()=>{let format='xlsx';const buttons=document.querySelectorAll('[data-rab-format]');buttons.forEach(b=>b.addEventListener('click',()=>{format=b.dataset.rabFormat;buttons.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.getElementById('rab-download-action').textContent=format==='xlsx'?'Unduh Excel':'Simpan PDF';document.getElementById('rab-download-hint').textContent=format==='xlsx'?'Menggunakan harga dan pengaturan saat ini.':'Pada dialog cetak, pilih Simpan sebagai PDF.';}));document.getElementById('rab-download-action').addEventListener('click',()=>document.getElementById(format==='xlsx'?'exXlsx':'exPdf').click());})();""";soup.body.append(js)
  style=soup.new_tag('style');style.string=(ROOT/'rab_download.css').read_text(encoding='utf-8');soup.body.append(style)
  (dist/name).write_text(str(soup),encoding='utf-8')
