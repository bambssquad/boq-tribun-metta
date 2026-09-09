from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent
def build(dist):
 p=dist/'tools.html';s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser');budget=s.select_one('#anggaran')
 budget.select_one('h2').string='RAB & penawaran.'
 for selector in ['.pitch-budget-grid','#fastener-rab']:
  e=budget.select_one(selector)
  if e:e.decompose()
 legacy=s.new_tag('div',id='rab-quantity-panel',hidden='')
 for ident in ['rincian-boq','rincian-penawaran']:
  e=budget.select_one('#'+ident);e.extract();legacy.append(e)
 legacy.select_one('#rincian-boq')['open']=''
 controls=BeautifulSoup('''<div class="rab-mode" role="group" aria-label="Jenis RAB"><button type="button" data-rab-mode="full" aria-pressed="true">RAB lengkap</button><button type="button" data-rab-mode="quantity" aria-pressed="false">Kalkulator kuantitas</button></div><div id="rab-full-panel"><span id="fastener-rab"></span><p>Seluruh material, baut, sekrup, cat, jasa, overhead, laba dan pajak. Harga serta unduhan Excel/PDF tersedia di bawah.</p><p id="rab-frame-status" role="status">Memuat rincian RAB…</p><iframe id="rab-full-frame" title="RAB lengkap METTA: harga, pemasok dan penawaran" src="r04.html?embed=rab" style="width:100%;height:1200px;border:0;display:block" loading="lazy"></iframe></div>''','html.parser')
 budget.append(controls);budget.append(legacy)
 css=s.new_tag('style');css.string='.rab-mode{display:flex;flex-wrap:wrap;gap:8px;padding:12px;margin:22px 0;background:#ffffffbb;border:1px solid #fff;border-radius:18px;backdrop-filter:blur(28px);-webkit-backdrop-filter:blur(28px)}.rab-mode button{padding:12px 20px;min-height:44px;border-radius:12px;border:1px solid #aaa;background:#fff;color:#222}.rab-mode button[aria-pressed=true]{background:#222!important;color:#fff!important}#rab-full-panel[hidden],#rab-quantity-panel[hidden]{display:none!important}@media print{.rab-mode,#rab-full-panel{display:none!important}body.printing-of #anggaran>#rab-quantity-panel{display:block!important}body.printing-of #rab-quantity-panel>#rincian-boq{display:none!important}}';s.body.append(css)
 js=s.new_tag('script',src='assets/unified-rab.js');s.body.append(js);p.write_text(str(s),encoding='utf-8')
 p=dist/'r04.html';r=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 flag=r.new_tag('script');flag.string="if(new URLSearchParams(location.search).get('embed')==='rab')document.documentElement.classList.add('rab-embedded');";r.head.append(flag)
 css=r.new_tag('style');css.string='.rab-embedded{background:transparent;scroll-behavior:auto}.rab-embedded body{background:transparent}.rab-embedded header,.rab-embedded .intro,.rab-embedded #gambar,.rab-embedded #analisis,.rab-embedded #berat,.rab-embedded #sumber,.rab-embedded footer{display:none!important}.rab-embedded main{max-width:none;padding:0}.rab-embedded #rab{padding-top:0}.rab-embedded #rab>.eyebrow,.rab-embedded #rab>h2{display:none}.rab-embedded section{padding:20px 0}.rab-embedded #penawaran-r04{border-top:1px solid #bbb}';r.head.append(css)
 js=r.new_tag('script',src='assets/unified-rab-embed.js');r.body.append(js);p.write_text(str(r),encoding='utf-8')
 for name in ['tools.html','index.html']:
  p=dist/name;s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
  for a in s.select('a[href]'):
   if a['href'] in ['r04.html#rab','r04.html#penawaran-r04']:a['href']='tools.html#anggaran' if name=='index.html' else '#anggaran'
  p.write_text(str(s),encoding='utf-8')
 for name in ['unified-rab.js','unified-rab-embed.js']:(dist/'assets'/name).write_bytes((ROOT/name).read_bytes())
