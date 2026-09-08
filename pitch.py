"""Client presentation layer; retain engineering records in an accessible appendix."""
from bs4 import BeautifulSoup

def present(s):
 main=s.select_one('main')
 def fragment(value):return BeautifulSoup(value,'html.parser')
 mast=s.select_one('.look-mast')
 mast.select_one('.look-brand')['href']='#konsep'
 mast.select('a')[1]['href']='#konsep';mast.select('a')[1].string='USULAN TEKNIS / R02'
 mast.select_one('nav').clear()
 mast.select_one('nav').append(fragment('<a href="#konsep">01 Konsep</a><a href="#tiga-d">02 Model</a><a href="#gambar">03 Gambar</a><a href="#material">04 Material</a><a href="#anggaran">05 Biaya</a>'))
 hero=fragment('''<section class="pitch-hero" id="konsep"><div class="pitch-kicker"><span>METTA / TRIBUN LT 04</span><span>USULAN DESAIN · R02</span></div><h1>TRIBUN METTA<br><em>DEK BORDES 4 MM</em></h1><div class="pitch-intro"><p>Usulan tribun lima tingkat dengan rangka baja RHS, dek bordes 4 mm, pengaku silang X, dan papan pinus pada bidang duduk.</p><a class="pitch-link" href="#tiga-d">Tinjau model 3D <span>↘</span></a></div><div class="pitch-metrics"><div><b>17,70 × 5,00</b><span>meter · ukuran tribun</span></div><div><b>04 mm</b><span>usulan ketebalan dek</span></div><div><b>05 tingkat</b><span>susunan area duduk</span></div><div><b>08 X</b><span>konfigurasi pengaku rangka</span></div></div></section>
 <section class="pitch-value" id="nilai-desain"><p class="eyebrow">SISTEM KONSTRUKSI</p><div class="pitch-value-grid"><article><span>01</span><h2>Spesifikasi dek</h2><p>Ketebalan 4 mm mengurangi massa baja dasar dek sebesar 50% dibanding 8 mm pada luas yang sama. Rangka dan motif bordes dihitung terpisah.</p></article><article><span>02</span><h2>Modul rangka</h2><p>Satu profil utama dan pengelompokan potongan menjadi dasar untuk menyederhanakan pengadaan serta perakitan.</p></article><article><span>03</span><h2>Pengadaan material</h2><p>Kandidat pemasok di Surabaya mencakup baja, papan pinus, karet dudukan, dan pelapis. Pilihan dapat disesuaikan dengan anggaran proyek.</p></article></div></section>''')
 mast.insert_after(hero)
 hero_section=s.select_one('.pitch-hero')
 layout=s.new_tag('div',attrs={'class':'hero-layout'})
 copy=s.new_tag('div',attrs={'class':'hero-copy'})
 copy.append(hero_section.select_one('h1').extract())
 copy.append(hero_section.select_one('.pitch-intro').extract())
 layout.append(copy)
 layout.append(fragment('''<figure class="hero-drawing"><figcaption><span>R02 / SISTEM RANGKA BAJA</span><span>S-04</span></figcaption><a href="#gambar" class="hero-sheet" aria-label="Buka galeri gambar teknis tribun"><img src="assets/technical/S-04.svg" alt="Proyeksi tampak depan rangka tribun METTA, panjang 17.700 mm" width="1191" height="842" fetchpriority="high" decoding="async"></a><div class="hero-drawing-info"><span><b>161</b> elemen rangka</span><span><b>80</b> kolom</span><span><b>16</b> diagonal</span></div><a class="hero-sheet-link" href="#tiga-d">Model koordinasi interaktif ↗</a></figure>'''))
 hero_section.select_one('.pitch-kicker').insert_after(layout)
 gallery=s.select_one('#gambar');title=gallery.select_one('.look-title');title.clear()
 for img in gallery.select('img'):
  img['loading']='lazy';img['decoding']='async'
 title.append(fragment('<div><p class="eyebrow">03 / GAMBAR DESAIN</p><h2 id="gallery-title">Denah, potongan,<br>dan detail konstruksi.</h2></div><p class="look-meta">12 GAMBAR<br>DENAH / POTONGAN / DETAIL</p>'))
 strip=s.select_one('.project-strip')
 if strip:strip.decompose()
 model=s.select_one('#tiga-d');model.extract();s.select_one('#nilai-desain').insert_after(model)
 model.select_one('h2').string='02 / Model koordinasi 3D'
 model.select_one('.lede').string='Model koordinasi rangka, dek, tangga, railing, dan bidang duduk. Gunakan rotasi, pemisahan komponen, serta seleksi elemen untuk memeriksa susunan konstruksi.'
 mat=s.select_one('#material');mat.select_one('.eyebrow').string='04 / PILIHAN MATERIAL'
 mat.select_one('h2').clear();mat.select_one('h2').append(fragment('Spesifikasi material<br>dan referensi pemasok.'))
 mat.select_one('.lede').string='Kandidat material dan pemasok Surabaya. Harga katalog per 7 September 2026 menjadi acuan awal; penawaran pemasok digunakan saat pengadaan.'
 articles=mat.select('.material-grid article')
 descriptions=[
  'Lembar 1.200 × 2.400 mm untuk dek. Kebutuhan pembelian mengikuti pembagian panel dan pola potong.',
  'Acuan material rangka utama: 75 batang × Rp434.500 = Rp32.587.500. Kolom, dek dan pekerjaan dihitung terpisah.',
  'Alternatif profil berdinding lebih tebal untuk dibandingkan pada pengembangan detail.',
  'Kandidat papan pinus dari Gunung Anyar Tambak, Surabaya. Dimensi dan finishing dipilih sesuai rancangan area duduk.',
  'Kandidat pemasok karet lembaran di Bratang Gede, Surabaya. Jenis bantalan dipilih sesuai kebutuhan tumpuan.',
  'Kandidat pelapis baja dari Rungkut, Surabaya. Warna dan sistem pelapisan disesuaikan dengan penggunaan ruang.'
 ]
 # Preserve the procurement qualifications, alongside the original engineering basis.
 appendix=fragment('<details class="pitch-appendix" id="lampiran"><summary><span>Lampiran teknis</span><span>Dasar perencanaan, lingkup biaya & berkas kerja ↗</span></summary><div class="appendix-content"><section id="catatan-pengadaan"><h2>Dasar pengadaan</h2></section></div></details>')
 append_body=appendix.select_one('.appendix-content');proc=appendix.select_one('#catatan-pengadaan')
 for i,a in enumerate(articles):
  paragraphs=a.select('p');old=paragraphs[-1]
  note=s.new_tag('p');note.append(fragment('<b>'+a.select_one('h3').get_text()+'</b> · '+old.get_text()))
  proc.append(note);old.string=descriptions[i]
 process=s.select_one('#pelaksanaan');process.select_one('.eyebrow').string='PELAKSANAAN / TAHAP BERIKUTNYA'
 process.select_one('h2').clear();process.select_one('h2').append(fragment('Tahapan koordinasi<br>dan pelaksanaan.'))
 step_titles=['Survei & koordinasi','Pengembangan detail','Pengadaan & pemotongan','Perakitan rangka','Pemasangan & finishing']
 step_copy=['Cocokkan dimensi tribun dengan kondisi lantai, kolom, serta akses ruang.','Selesaikan validasi struktur, sambungan, dan pola panel sebelum produksi.','Konfirmasikan material dan harga, lalu kelompokkan potongan per modul.','Gunakan kode komponen dan urutan kerja yang konsisten pada tiap bagian.','Lanjutkan ke dek, area duduk, tangga, railing, dan lapisan akhir.']
 # The detailed assembly method remains available in the appendix.
 original_process=fragment(str(process));original_process.select_one('section')['id']='metode-perakitan';append_body.append(original_process)
 for i,li in enumerate(process.select('li')):
  li.select_one('b').string=f'{i+1:02} / '+step_titles[i];li.select_one('span').string=step_copy[i]
 process.select_one('.lede').string='Urutan pelaksanaan disusun setelah pengembangan teknis dan lingkup pekerjaan disepakati.'
 for selector in ['#kajian','#potong','#spek','#revit-native']:
  node=s.select_one(selector);node.extract();append_body.append(node)
 # Keep data-quality and cost-boundary notes with the detailed estimate.
 boq=s.select_one('#boq');boq.extract()
 budget=fragment('''<section class="pitch-budget block" id="anggaran"><p class="eyebrow">05 / ESTIMASI BIAYA</p><h2>Estimasi material<br>dan volume pekerjaan.</h2><div class="pitch-budget-grid"><div><span>ACUAN BAHAN RANGKA UTAMA</span><b>Rp32,59<span> juta</span></b><p>75 batang × 6 m · harga katalog 7 September 2026.</p></div><div><p>Acuan ini hanya untuk bahan rangka utama. Kolom, dek, railing, sambungan, fabrikasi, dan pengiriman dihitung terpisah.</p><p>Gunakan rincian BOQ untuk menyesuaikan harga dan menyusun estimasi sesuai lingkup yang dipilih.</p><a href="#rincian-boq">Buka rincian estimasi ↓</a></div></div><details id="rincian-boq" class="pitch-disclosure"><summary>Rincian BOQ & perhitungan biaya</summary></details><details id="rincian-penawaran" class="pitch-disclosure"><summary>Susun penawaran & termin pembayaran</summary></details></section>''')
 budget.select_one('#rincian-boq').append(boq)
 offer=s.select_one('#penawaran');offer.extract();budget.select_one('#rincian-penawaran').append(offer)
 process.insert_after(budget)
 s.select_one('#boq h2').string='Rincian estimasi.'
 append_body.select_one('#potong h2').string='Rencana pemotongan profil'
 s.select_one('#penawaran h2').string='Rekapitulasi penawaran dan termin'
 append_body.select_one('#spek h2').string='Dasar koordinasi konstruksi'
 footer=s.select_one('.look-footer')
 footer.insert_before(fragment('<p class="pitch-stage">Konsep desain untuk pembahasan klien. Validasi struktur dan sambungan diselesaikan sebelum pelaksanaan. <a href="#lampiran">Dasar perencanaan ↗</a></p>'))
 footer.insert_before(appendix)
 footer.select_one('p').clear();footer.select_one('p').append(fragment('METTA / R02<br>DOKUMEN USULAN TEKNIS.'))
 note=s.select_one('#drawing-note');note.extract()
 note_wrap=fragment('<details class="drawing-notes"><summary>Catatan gambar</summary></details>');note_wrap.select_one('details').append(note)
 s.select_one('.dialog-actions').insert_before(note_wrap)
 # Native links continue to work when their targets are inside closed appendices.
 script=s.new_tag('script');script.string="""
(()=>{function reveal(hash){if(!hash||hash==='#')return;let el;try{el=document.getElementById(decodeURIComponent(hash.slice(1)));}catch{return;}if(!el)return;for(let p=el;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;}
document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(a)reveal(a.getAttribute('href'));});
addEventListener('hashchange',()=>reveal(location.hash));reveal(location.hash);})();
 """;main.append(script)
 motion=s.new_tag('script')
 motion.string="""
(()=>{
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 if(reduced.matches||!('IntersectionObserver' in window)||!Element.prototype.animate)return;
 const active=new Set();
 const observer=new IntersectionObserver(entries=>{
  for(const e of entries){if(!e.isIntersecting)continue;observer.unobserve(e.target);
   if(reduced.matches)continue;
   const anim=e.target.animate([{opacity:0,transform:'translateY(18px)'},{opacity:1,transform:'translateY(0)'}],{duration:matchMedia('(max-width:800px)').matches?320:480,easing:'cubic-bezier(.2,.7,.2,1)'});
   active.add(anim);anim.onfinish=anim.oncancel=()=>active.delete(anim);
  }
 },{threshold:.08});
 document.querySelectorAll('.hero-copy,.hero-drawing,.pitch-metrics,.pitch-value-grid article,#tiga-d h2,.look-title,.material-grid article,.assembly-list li,.pitch-budget>h2').forEach(el=>observer.observe(el));
 reduced.addEventListener('change',e=>{if(e.matches){observer.disconnect();active.forEach(a=>a.cancel());active.clear();}});
})();
"""
 main.append(motion)
 return s
