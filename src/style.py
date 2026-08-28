# -*- coding: utf-8 -*-
"""Sistem visual: ruang gelap tunggal (kalkir terbalik / layar plot CAD), presisi-instrumen. Ground bone, satu aksen kuning nosing,
satu panggung gelap untuk 3D (satu-satunya gerakan besar di halaman)."""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Archivo:wght@400;500;600;700&'
         'family=JetBrains+Mono:wght@400;500;600&'
         'family=Schibsted+Grotesk:wght@400;500;600&display=swap">')

CSS = r"""
*,*::before,*::after{box-sizing:border-box}
/* Halaman ini sengaja berkomitmen pada satu dunia gelap — tidak mengikuti tema penonton. */
:root{
  --paper:#0A0B0D; --surface:#111316; --sunk:#0D0F12;
  --ink:#EDEEF0; --muted:#8E959C; --faint:#5C646C;
  --hair:#1D2126; --rule:#2B3037;
  --accent:#E0A62A; --accent-soft:#3A2E12;
  --stage:#08090B; --stage-ink:#E8E9EA; --stage-hair:#1B1F24;
  --steel:#98A0A8; --dim:#69717A; --line:#2B3037;
  --ok:#6FB58C; --warn:#D5A153; --crit:#D97A66;
  --e-out:cubic-bezier(0.23,1,0.32,1);
  --e-io:cubic-bezier(0.77,0,0.175,1);
  --pad:clamp(16px,4vw,40px);
}
html{-webkit-text-size-adjust:100%; scroll-behavior:smooth; background:#0A0B0D}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"Schibsted Grotesk",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:15.5px; line-height:1.62; -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}
h1,h2,h3,.snum,.sname,.pill,.bname,.mini,.pk-name,.ix-name{
  font-family:Archivo,"Schibsted Grotesk",sans-serif}
.num,code,.fv,.bsub,.mono,.ix-n,.ix-s{font-family:"JetBrains Mono",ui-monospace,monospace;
  font-variant-numeric:tabular-nums; font-feature-settings:"zero" 1}
::selection{background:var(--accent);color:#0A0B0D}

/* ---------- reveal ---------- */
.rv{opacity:0; transform:translate3d(0,16px,0);
  transition:opacity .55s var(--e-out), transform .55s var(--e-out)}
.rv.in{opacity:1; transform:none}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .rv{opacity:1; transform:none; transition:none}
  .ln i{transform:none!important; opacity:1!important}
  *{animation:none!important}
}

/* ---------- header ---------- */
.top{position:sticky;top:0;z-index:40;background:rgba(10,11,13,.78);
  backdrop-filter:saturate(1.3) blur(16px);border-bottom:1px solid var(--hair)}
.top-in{max-width:1320px;margin:0 auto;padding:11px var(--pad);
  display:flex;gap:18px;align-items:center;justify-content:space-between}
.brand{display:flex;gap:11px;align-items:center;min-width:0}
.mark{width:22px;height:22px;flex:0 0 auto;border:1.5px solid var(--ink);
  background:repeating-linear-gradient(135deg,var(--ink) 0 1.5px,transparent 1.5px 5px)}
.bname{font-weight:600;font-size:15px;letter-spacing:-.015em;line-height:1.15;white-space:nowrap}
.bsub{font-size:10.5px;color:var(--muted);letter-spacing:.03em;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.pills{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;min-width:0;
  mask-image:linear-gradient(90deg,transparent,#000 12px,#000 calc(100% - 12px),transparent)}
.pills::-webkit-scrollbar{display:none}
.pill{font-size:11px;font-weight:500;letter-spacing:.05em;text-decoration:none;color:var(--faint);
  padding:5px 9px;white-space:nowrap;border-radius:2px;
  transition:color .18s var(--e-out),background .18s var(--e-out)}
@media (hover:hover) and (pointer:fine){.pill:hover{color:var(--ink);background:var(--surface)}}
.pill:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:900px){.bsub{display:none}}
@media (max-width:760px){
  .top-in{flex-wrap:wrap;gap:5px;padding:8px var(--pad) 6px}
  .brand{flex:1 1 100%;min-width:0}
  .bname{font-size:13px;overflow:hidden;text-overflow:ellipsis}
  .pills{flex:1 1 100%;margin:0 calc(-1 * var(--pad));padding:0 var(--pad)}
}

.wrap{max-width:1320px;margin:0 auto;padding:0 var(--pad) 120px;
  display:flex;flex-direction:column}

/* ---------- hero ---------- */
.hero{padding:clamp(56px,13vh,150px) 0 clamp(34px,6vw,60px)}
.eyebrow{font-family:"JetBrains Mono",monospace;font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--accent);margin:0 0 clamp(18px,3vw,30px);
  opacity:0;animation:fadeUp .7s var(--e-out) .05s forwards}
h1{font-size:clamp(40px,10.5vw,124px);line-height:.95;letter-spacing:-.045em;
  margin:0 0 clamp(20px,3vw,34px);font-weight:600;max-width:13ch}
.ln{display:block;overflow:hidden;padding-bottom:.06em}
.ln i{display:block;font-style:normal;transform:translate3d(0,110%,0);opacity:.001;
  animation:lineUp .95s var(--e-out) forwards}
.ln:nth-child(1) i{animation-delay:.10s}
.ln:nth-child(2) i{animation-delay:.19s}
.ln:nth-child(3) i{animation-delay:.28s}
@keyframes lineUp{to{transform:none;opacity:1}}
@keyframes fadeUp{from{opacity:0;transform:translate3d(0,10px,0)}to{opacity:1;transform:none}}
.lede{max-width:58ch;color:var(--muted);margin:0 0 clamp(28px,5vw,46px);
  font-size:clamp(15px,1.7vw,17.5px);opacity:0;animation:fadeUp .8s var(--e-out) .42s forwards}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));
  border-top:1px solid var(--rule);opacity:0;animation:fadeUp .8s var(--e-out) .55s forwards}
.fact{padding:14px 16px 16px 0;border-bottom:1px solid var(--hair)}
.fk{display:block;font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);
  margin-bottom:4px}
.fv{display:block;font-size:clamp(15px,2vw,18px);font-weight:500;letter-spacing:-.01em}

/* ---------- indeks lembar ---------- */
.ixwrap{margin:clamp(60px,10vw,120px) 0 0;padding-top:clamp(24px,4vw,36px);
  border-top:1px solid var(--rule)}
.ixlist{display:flex;flex-direction:column;margin-top:clamp(16px,3vw,26px)}
.ix{display:grid;grid-template-columns:74px 1fr auto;gap:16px;align-items:baseline;
  padding:clamp(13px,1.8vw,20px) 0;border-bottom:1px solid var(--hair);
  text-decoration:none;color:var(--ink);
  transition:opacity .28s var(--e-out),padding-left .34s var(--e-out)}
.ix-n{font-size:11px;letter-spacing:.1em;color:var(--accent)}
.ix-name{font-size:clamp(19px,3.4vw,38px);font-weight:600;letter-spacing:-.03em;line-height:1.05}
.ix-s{font-size:10.5px;color:var(--faint);white-space:nowrap}
@media (hover:hover) and (pointer:fine){
  .ixlist:hover .ix{opacity:.32}
  .ixlist .ix:hover{opacity:1;padding-left:14px}
}
.ix:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
#ixprev{position:fixed;top:0;left:0;width:330px;height:236px;pointer-events:none;z-index:60;
  background:var(--sunk);border:1px solid var(--rule);border-radius:3px;overflow:hidden;
  opacity:0;transform:translate3d(-50%,-50%,0) scale(.94);
  transition:opacity .26s var(--e-out),transform .34s var(--e-out);will-change:transform}
#ixprev.on{opacity:1;transform:translate3d(-50%,-50%,0) scale(1)}
#ixprev svg{width:100%;height:100%;display:block}
@media (max-width:900px){#ixprev{display:none}}

/* ---------- lembar gambar ---------- */
.sheet{margin:clamp(28px,4vw,52px) 0 0;background:var(--surface);
  border:1px solid var(--hair);border-radius:3px;overflow:hidden;scroll-margin-top:96px}
.shead{display:flex;align-items:baseline;gap:12px;padding:16px var(--pad) 0;flex-wrap:wrap}
.snum{font-family:"JetBrains Mono",monospace;font-weight:500;font-size:11px;letter-spacing:.1em;
  color:var(--accent)}
.sname{font-size:clamp(17px,2.4vw,22px);font-weight:600;letter-spacing:-.02em;flex:1;min-width:0}
.sscale{font-family:"JetBrains Mono",monospace;font-size:10.5px;color:var(--faint)}
.sdesc{margin:8px 0 0;padding:0 var(--pad);color:var(--muted);max-width:74ch;font-size:14px}
.ctrls{display:flex;gap:5px;flex-wrap:wrap;padding:14px var(--pad) 13px;align-items:center}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:11px;border:1px solid var(--hair);
  padding:4px 9px;cursor:pointer;user-select:none;background:var(--sunk);border-radius:2px;
  color:var(--ink);transition:border-color .18s var(--e-out),opacity .18s var(--e-out)}
.chip input{margin:0;accent-color:var(--accent);width:11px;height:11px}
.chip:has(input:not(:checked)){opacity:.38}
@media (hover:hover) and (pointer:fine){.chip:hover{border-color:var(--rule)}}
.chip:focus-within{outline:2px solid var(--accent);outline-offset:1px}
.reset{font:inherit;font-size:11px;background:none;border:1px solid var(--hair);
  padding:4px 10px;cursor:pointer;color:var(--muted);border-radius:2px;
  transition:color .18s var(--e-out),border-color .18s var(--e-out)}
@media (hover:hover) and (pointer:fine){.reset:hover{color:var(--ink);border-color:var(--rule)}}
.frame{position:relative;overflow:hidden;background:var(--sunk);border-top:1px solid var(--hair);
  height:min(66vh,580px);touch-action:none;cursor:grab}
.frame.drag{cursor:grabbing}
.pan{width:100%;height:100%;transform-origin:0 0}
.hint{position:absolute;right:10px;bottom:9px;font-size:10px;color:var(--faint);
  font-family:"JetBrains Mono",monospace;pointer-events:none;opacity:.8}
svg.dwg{width:100%;height:100%;display:block}

/* ---------- mode layar penuh ---------- */
body.locked{overflow:hidden}
.sheet.full{position:fixed;inset:0;z-index:90;margin:0;border:none;border-radius:0;
  display:flex;flex-direction:column;background:var(--surface)}
.sheet.full .sdesc{display:none}
.sheet.full .frame{flex:1 1 auto;height:auto;min-height:0}
.sheet.full .shead{padding-top:12px}
.navf{display:none;gap:4px;margin-left:auto}
.sheet.full .navf{display:flex}
.sheet.full .sscale{margin-left:0}
.meas-btn{margin-left:auto}
.navf button,.expand,.meas-btn{font:inherit;font-size:11px;background:none;
  border:1px solid var(--hair);padding:4px 10px;cursor:pointer;color:var(--muted);border-radius:2px;
  transition:color .18s var(--e-out),border-color .18s var(--e-out)}
@media (hover:hover) and (pointer:fine){
  .navf button:hover,.expand:hover,.meas-btn:hover{color:var(--ink);border-color:var(--rule)}}
.navf button:disabled{opacity:.3;cursor:default}
.expand[aria-pressed="true"],.meas-btn[aria-pressed="true"]{color:#0A0B0D;background:var(--accent);
  border-color:var(--accent)}
.frame.measuring{cursor:crosshair}
.frame.measuring .hint::after{content:" · mode ukur"}

/* ---------- tombol lompat dari 3D ke lembar ---------- */
.pk-jump{display:inline-flex;margin-top:11px;font:inherit;font-size:11px;padding:5px 10px;
  border:1px solid var(--accent);background:none;color:var(--accent);cursor:pointer;border-radius:2px;
  transition:background .18s var(--e-out),color .18s var(--e-out)}
@media (hover:hover) and (pointer:fine){.pk-jump:hover{background:var(--accent);color:#0A0B0D}}

/* ---------- blok teks ---------- */
.block{margin:clamp(60px,10vw,120px) 0 0;padding-top:clamp(26px,4vw,38px);
  border-top:1px solid var(--rule);scroll-margin-top:96px}
h2{font-size:clamp(26px,5vw,52px);margin:0 0 14px;letter-spacing:-.038em;font-weight:600;
  text-wrap:balance;line-height:1.02}
h3.sub{font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--faint);
  margin:clamp(30px,4vw,44px) 0 12px;font-weight:600}
.spek{display:grid;grid-template-columns:repeat(auto-fit,minmax(272px,1fr));gap:0;margin-top:24px;
  border-top:1px solid var(--hair)}
.skgroup{padding:18px 24px 20px 0;border-bottom:1px solid var(--hair)}
.skgroup h3{margin:0 0 12px;font-size:10.5px;letter-spacing:.15em;text-transform:uppercase;
  color:var(--accent);font-weight:600}
.skgroup dl{margin:0;display:grid;grid-template-columns:minmax(90px,auto) 1fr;gap:7px 18px}
.skgroup dt{color:var(--faint);font-size:13px}
.skgroup dd{margin:0;font-size:13.5px}

/* ---------- tabel ---------- */
.tw{overflow-x:auto;border:1px solid var(--hair);background:var(--surface);border-radius:3px;
  -webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:13px;min-width:620px}
th,td{padding:9px 13px;text-align:left;border-bottom:1px solid var(--hair);vertical-align:top}
th{font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);
  font-weight:600;white-space:nowrap;background:var(--sunk);position:sticky;top:0;z-index:1}
td.num,th.num{text-align:right;font-family:"JetBrains Mono",monospace;font-variant-numeric:tabular-nums}
tfoot td{font-weight:600;border-bottom:none;background:var(--sunk)}
@media (hover:hover) and (pointer:fine){tbody tr:hover{background:var(--sunk)}}
.bar{display:inline-block;width:52px;height:4px;background:var(--hair);margin-right:8px;
  vertical-align:middle;border-radius:2px;overflow:hidden}
.bar i{display:block;height:100%}
.bar.ok i{background:var(--ok)} .bar.warn i{background:var(--warn)} .bar.crit i{background:var(--crit)}

.wastebar{display:flex;gap:20px;flex-wrap:wrap;margin:18px 0 8px;padding:14px 16px;
  background:var(--surface);border:1px solid var(--hair);border-radius:3px}
.wastebar label{display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--muted)}
.wastebar input{width:62px;font:inherit;font-family:"JetBrains Mono",monospace;padding:5px 8px;
  border:1px solid var(--rule);background:var(--sunk);color:var(--ink);text-align:right;
  border-radius:2px;transition:border-color .18s var(--e-out)}
.wastebar input:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.tot{margin:20px 0 0;font-size:15px;color:var(--muted)}
.tot b{font-family:"JetBrains Mono",monospace;font-size:19px;color:var(--ink)}
.callout{margin-top:22px;padding:14px 16px;border-left:2px solid var(--accent);
  background:var(--surface);font-size:13px;color:var(--muted);border-radius:0 3px 3px 0}
.callout b{color:var(--ink)}
.foot{margin-top:clamp(60px,9vw,100px);padding-top:22px;border-top:1px solid var(--rule);
  display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:11.5px;
  color:var(--faint)}

/* ---------- panggung 3D ---------- */
#tiga-d{border-top:none;padding-top:0}
.stage-wrap{margin:clamp(60px,10vw,120px) calc(-1 * var(--pad)) 0;background:var(--stage);
  color:var(--stage-ink);padding:clamp(34px,6vw,64px) var(--pad) clamp(28px,4vw,44px);
  border-top:1px solid var(--hair);border-bottom:1px solid var(--hair)}
.stage-wrap h2{color:var(--stage-ink)}
.stage-wrap .lede{color:#949BA2;opacity:1;animation:none}
.v3{display:grid;grid-template-columns:1fr 300px;gap:14px;margin-top:24px}
.v3-stage{position:relative;background:#0A0C0E;border:1px solid var(--stage-hair);
  height:min(70vh,620px);overflow:hidden;cursor:grab;touch-action:none;border-radius:3px}
.v3-stage.drag{cursor:grabbing}
#cv3{display:block;width:100%;height:100%}
.v3-hud{position:absolute;left:12px;bottom:10px;font-family:"JetBrains Mono",monospace;
  font-size:10px;color:#5E666E;pointer-events:none}
.v3-side{display:flex;flex-direction:column;gap:10px}
.v3-card{background:#111417;border:1px solid var(--stage-hair);padding:13px 14px;border-radius:3px}
.pk-eyebrow{font-size:9.5px;letter-spacing:.15em;text-transform:uppercase;color:#6B737B;
  margin-bottom:9px;font-weight:600}
.pk-name{font-size:15.5px;font-weight:600;line-height:1.25;margin-bottom:9px;color:var(--stage-ink);
  letter-spacing:-.015em}
.pk-dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:5px 12px;font-size:12px;color:#AEB5BC}
.pk-dl dt{color:#6B737B}
.pk-dl dd{margin:0;font-family:"JetBrains Mono",monospace}
#ex{width:100%;accent-color:var(--accent);margin:2px 0 10px}
.v3-row{display:flex;gap:6px;flex-wrap:wrap}
.mini{font:inherit;font-size:11px;padding:5px 10px;border:1px solid var(--stage-hair);
  background:#0A0C0E;color:#9BA3AB;cursor:pointer;border-radius:2px;
  transition:color .18s var(--e-out),border-color .18s var(--e-out)}
@media (hover:hover) and (pointer:fine){.mini:hover{color:var(--stage-ink);border-color:#3A4149}}
.mini:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.legend{display:flex;flex-direction:column;gap:4px;max-height:230px;overflow-y:auto}
.lg{display:flex;align-items:center;gap:8px;font-size:11.5px;cursor:pointer;user-select:none;
  color:#AEB5BC;transition:opacity .18s var(--e-out)}
.lg input{margin:0;width:11px;height:11px;accent-color:var(--accent)}
.lg .sw{width:11px;height:11px;flex:0 0 auto;border-radius:1px}
.lg:has(input:not(:checked)){opacity:.35}

/* ---------- mobile ---------- */
.sheet-toggle{display:none}
@media (max-width:860px){
  .wrap>#tiga-d{order:-1}
  .wrap>.hero{order:-2}
  .v3{grid-template-columns:1fr;gap:0}
  .v3-stage{height:62vh;border-radius:3px 3px 0 0}
  .v3-side{position:sticky;bottom:0;background:#0A0C0E;border:1px solid var(--stage-hair);
    border-top:none;border-radius:0 0 3px 3px;padding:0;gap:0;
    max-height:0;overflow:hidden;transition:max-height .34s var(--e-io)}
  .v3-side.open{max-height:64vh;overflow-y:auto}
  .v3-card{border:none;border-bottom:1px solid var(--stage-hair);border-radius:0}
  .sheet-toggle{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;
    padding:11px;background:#111417;border:1px solid var(--stage-hair);border-top:none;
    color:#9BA3AB;font:inherit;font-size:12px;cursor:pointer}
  .sheet-toggle .grip{width:34px;height:3px;border-radius:2px;background:#333A41}
  .frame{height:52vh}
  table{min-width:520px}
  .skgroup{padding-right:0}
  .sheet.full .ctrls{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-bottom:10px}
  .sheet.full .ctrls::-webkit-scrollbar{display:none}
  .sheet.full .chip,.sheet.full .meas-btn,.sheet.full .expand,.sheet.full .reset{flex:0 0 auto}
  .sheet.full .shead{padding-bottom:0}
  .ix{grid-template-columns:60px 1fr;gap:10px}
  .ix-s{grid-column:2;font-size:10px}
}
@media (max-width:520px){
  .facts{grid-template-columns:1fr 1fr}
  .frame{height:46vh}
  .v3-stage{height:56vh}
}

/* ---------- kontrol BOQ ---------- */
.boqbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:18px 0 4px;
  padding:11px 13px;background:var(--surface);border:1px solid var(--hair);border-radius:3px}
.boqbar .bgrow{flex:1 1 auto}
.sw{display:inline-flex;align-items:center;gap:7px;font-size:12px;cursor:pointer;user-select:none;
  padding:5px 11px;border:1px solid var(--hair);border-radius:2px;background:var(--sunk);
  transition:border-color .18s var(--e-out),color .18s var(--e-out)}
.sw input{margin:0;width:13px;height:13px;accent-color:var(--accent)}
.sw:has(input:checked){border-color:var(--accent);color:var(--accent)}
@media (hover:hover) and (pointer:fine){.sw:hover{border-color:var(--rule)}}
.seg{display:inline-flex;border:1px solid var(--hair);border-radius:2px;overflow:hidden}
.seg button{font:inherit;font-size:11px;padding:6px 11px;border:none;cursor:pointer;
  background:var(--sunk);color:var(--muted);border-right:1px solid var(--hair);
  transition:background .18s var(--e-out),color .18s var(--e-out)}
.seg button:last-child{border-right:none}
.seg button.on{background:var(--accent);color:var(--paper);font-weight:600}
@media (hover:hover) and (pointer:fine){.seg button:not(.on):hover{color:var(--ink)}}
.addrow{font:inherit;font-size:10.5px;margin-left:9px;padding:2px 8px;cursor:pointer;
  border:1px solid var(--hair);background:var(--sunk);color:var(--muted);border-radius:2px;
  letter-spacing:0;text-transform:none}
@media (hover:hover) and (pointer:fine){.addrow:hover{color:var(--accent);border-color:var(--accent)}}
.pin{width:104px;font:inherit;font-family:"JetBrains Mono",monospace;font-size:12px;
  padding:3px 7px;border:1px solid var(--hair);background:var(--sunk);color:var(--ink);
  text-align:right;border-radius:2px}
.pin:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
td.cel{outline:none;min-width:38px}
td.cel:focus{background:color-mix(in srgb,var(--accent) 14%,transparent);
  box-shadow:inset 0 0 0 1px var(--accent)}
tbody td.cel{border-bottom:1px dashed var(--rule)}
.delrow{font:inherit;font-size:13px;line-height:1;width:22px;height:22px;cursor:pointer;
  border:1px solid var(--hair);background:var(--sunk);color:var(--faint);border-radius:2px}
@media (hover:hover) and (pointer:fine){.delrow:hover{color:var(--crit);border-color:var(--crit)}}
td.num{white-space:nowrap}
#rekap table{min-width:340px}
#rekap tfoot td{font-size:15px}

/* ---------- panel ekspor ---------- */
.exportbox{margin:10px 0 4px;padding:14px 15px;background:var(--surface);
  border:1px solid var(--hair);border-radius:3px}
.exrow{display:grid;gap:9px;grid-template-columns:repeat(auto-fit,minmax(212px,1fr))}
.exbtn{display:flex;flex-direction:column;gap:5px;text-align:left;font:inherit;cursor:pointer;
  padding:12px 13px;background:var(--sunk);border:1px solid var(--hair);border-radius:2px;
  color:var(--ink);transition:border-color .18s var(--e-out),transform .18s var(--e-out)}
.exbtn b{font-family:Archivo,sans-serif;font-size:13px;letter-spacing:-.01em}
.exbtn span{font-size:11.5px;color:var(--muted);line-height:1.45}
.exbtn i{font-style:italic}
@media (hover:hover) and (pointer:fine){.exbtn:hover{border-color:var(--accent);transform:translateY(-1px)}}
.exbtn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.exnote{margin:11px 0 0;font-size:11.5px;color:var(--faint);line-height:1.5}
.exnote b{color:var(--muted)}

/* ---------- tata letak cetak: hanya BOQ + daftar potong ---------- */
@media print{
  @page{size:A3 landscape;margin:12mm}
  :root{
    --paper:#fff;--surface:#fff;--sunk:#fff;--stage:#fff;
    --ink:#111;--muted:#333;--faint:#666;--hair:#bbb;--rule:#777;--accent:#8A5F08;
    --ok:#2F6B45;--warn:#8A5E10;--crit:#8E3223;
  }
  html,body{background:#fff!important;color:#111!important}
  body>*{display:none!important}
  body>main.wrap{display:block!important;max-width:none;padding:0}
  .wrap>*{display:none!important}
  .wrap>#boq,.wrap>#potong{display:block!important;margin:0 0 8mm;padding:0;border:none}
  .boqbar,.exportbox,.hint,.lede,.wastebar .ponly{display:none!important}
  .wastebar{border:none;padding:0 0 3mm;background:none;font-size:9pt}
  .wastebar input{border:none;background:none;width:auto}
  .rv{opacity:1!important;transform:none!important}
  h2{font-size:14pt;margin:0 0 3mm}
  h3.sub{font-size:8pt;margin:5mm 0 2mm;color:#000}
  .addrow{display:none!important}
  .tw{overflow:visible!important;border:none;background:none}
  table{min-width:0!important;font-size:8.5pt;width:100%}
  thead{display:table-header-group}
  tr{break-inside:avoid}
  th{position:static!important;background:#EEE!important;color:#333!important;
    border-bottom:1px solid #333}
  td,th{padding:1.4mm 2mm}
  td.cel{border-bottom:1px solid #ddd!important;box-shadow:none!important;background:none!important}
  .pin{border:none;background:none;text-align:right;width:auto;font-size:8.5pt}
  tfoot td{background:#F4F4F4!important}
  #rekap table{min-width:0}
  .tot{font-size:10pt}
}

.exname{margin-top:11px;font-size:12px;color:var(--muted)}
.exname input{font:inherit;font-size:12.5px;padding:5px 9px;margin-left:7px;min-width:220px;
  border:1px solid var(--hair);background:var(--sunk);color:var(--ink);border-radius:2px}
.exload{margin-top:11px;display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap}
.exload textarea{flex:1 1 320px;font-family:"JetBrains Mono",monospace;font-size:11px;
  padding:8px 10px;border:1px solid var(--hair);background:var(--sunk);color:var(--ink);
  border-radius:2px;resize:vertical}
.exmsg{font-size:11.5px;align-self:center}
.exmsg.ok{color:var(--ok)} .exmsg.bad{color:var(--crit)}

.revnote{margin:10px 0 0;padding:10px 13px;border-left:2px solid var(--accent);
  background:var(--surface);border-radius:0 2px 2px 0;font-size:12px;line-height:1.5;
  color:var(--muted)}
.revnote b{color:var(--ink)}

.matleg{margin:14px 0 0;padding:14px 16px;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
.matleg .mlh{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.matleg dl{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;margin:0}
.matleg dt{font-family:var(--mono,monospace);font-weight:700;color:var(--accent);font-size:12px}
.matleg dd{margin:0;font-size:12.5px;color:var(--muted);line-height:1.5}
.matleg dd b{color:var(--ink);font-weight:600}
@media(max-width:640px){.matleg dl{grid-template-columns:auto 1fr;gap:3px 8px}.matleg dd{font-size:11.5px}}

/* --- odometer angka + bar volume --- */
.odo{display:inline-block;white-space:nowrap}
.odo .oc{display:inline-block}
.odo .oc.roll{overflow:hidden;height:1.1em;line-height:1.1em;vertical-align:bottom}
.odo .oc.roll>b{display:block;font-weight:inherit;transform:translateY(0);will-change:transform}
.odo .oc.roll.go>b{transform:translateY(-1.1em);transition:transform .44s cubic-bezier(.22,.75,.2,1)}
.odo .oc.roll i{display:block;font-style:normal;height:1.1em;line-height:1.1em}
.vb{display:block;height:2px;margin:0 0 3px auto;width:100%;max-width:120px;background:var(--accent);
    opacity:.5;transform-origin:right center;transform:scaleX(0);
    transition:transform .5s cubic-bezier(.22,.75,.2,1);border-radius:2px}
.usel-all{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;color:var(--muted)}
.usel-all select,.usel select{background:var(--surface);color:var(--ink);border:1px solid var(--line);
  border-radius:7px;padding:4px 6px;font:inherit;font-size:12px}
.usel-cell{white-space:nowrap}
@media(prefers-reduced-motion:reduce){.odo .oc.roll.go>b{transition:none}.vb{transition:none}}

/* --- penawaran --- */
.ofdoc{margin-top:14px}
.ofpage{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:26px 28px}
.ofhead{display:flex;gap:20px;align-items:flex-start;justify-content:space-between;
  border-bottom:2px solid var(--ink);padding-bottom:14px}
.ofco{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1}
.ofconm{font-size:17px;font-weight:700;color:var(--ink);letter-spacing:-.01em}
.ofcosm{font-size:12.5px;color:var(--muted)}
.oflogo{width:118px;min-height:56px;display:flex;flex-direction:column;align-items:flex-end;gap:6px}
.oflogo img{max-width:118px;max-height:64px;object-fit:contain}
.oflogobtn{font-size:11px;color:var(--accent);cursor:pointer;border:1px dashed var(--line);
  padding:4px 8px;border-radius:7px}
.oftitle{margin:16px 0 12px;font-size:15px;letter-spacing:.16em;text-transform:uppercase;
  text-align:center;color:var(--ink)}
.ofmeta{display:grid;grid-template-columns:1fr 1fr;gap:2px 22px;margin-bottom:18px}
.ofmr{display:grid;grid-template-columns:118px 1fr;gap:8px;font-size:12.5px;padding:3px 0;
  border-bottom:1px dotted var(--line)}
.ofmr>span:first-child{color:var(--muted)}
.ofmr>span:last-child{color:var(--ink)}
.ofh4{margin:18px 0 8px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.oftab{width:100%;border-collapse:collapse;font-size:12.5px}
.oftab th{text-align:left;font-weight:600;color:var(--muted);border-bottom:1px solid var(--line);
  padding:6px 8px;font-size:11px;letter-spacing:.08em;text-transform:uppercase}
.oftab td{padding:6px 8px;border-bottom:1px solid var(--line);color:var(--ink)}
.oftab tfoot td{font-weight:700;border-top:2px solid var(--ink);border-bottom:none}
.oftab tr.ofsum td{font-weight:700;border-top:2px solid var(--ink)}
.ofnote{font-size:11.5px;color:var(--muted);margin:6px 0 0}
.okmsg{color:#4ea36b}.warnmsg{color:#d08a2c}
.ofph{color:var(--muted);opacity:.6}
.ofin{width:100%;background:transparent;border:1px solid var(--line);border-radius:6px;
  padding:4px 7px;color:var(--ink);font:inherit;font-size:12.5px}
.ofin[type=number]{width:76px}
.ofcols{display:grid;grid-template-columns:1fr 1fr;gap:0 26px}
.oflist{margin:0;padding-left:18px;font-size:12.5px;color:var(--ink)}
.oflist li{margin:3px 0;display:flex;gap:6px;align-items:center}
.oflist li .ofin{flex:1}
.ofnum{list-style:decimal}
.ofsign{display:flex;justify-content:flex-end;margin-top:26px}
.ofsigbox{width:230px;text-align:center;font-size:12.5px}
.ofsigd{color:var(--muted)}
.ofsigsp{height:54px}
.ofsignm{font-weight:700;border-top:1px solid var(--ink);padding-top:5px;color:var(--ink)}
.ofsigrl{color:var(--muted);font-size:11.5px}
.ofex{margin-top:14px}
.ofhint{margin-bottom:10px}
/* gantt */
.gwrap{border:1px solid var(--line);border-radius:9px;overflow-x:auto}
.grow{display:flex;align-items:center;border-bottom:1px solid var(--line);min-height:30px}
.grow:last-child{border-bottom:none}
.ghead{background:color-mix(in srgb,var(--ink) 6%,transparent)}
.gnm{width:230px;min-width:230px;padding:5px 9px;font-size:12px;color:var(--ink);
  display:flex;gap:5px;align-items:center}
.gnm .ofin{font-size:11.5px;padding:3px 5px}
.gnm .ofin[type=number]{width:52px}
.gbars{display:flex;flex:1;min-width:220px}
.gw{flex:1;text-align:center;font-size:10px;color:var(--muted);padding:4px 0}
.gc{flex:1;height:13px;margin:0 1px;border-radius:3px;background:color-mix(in srgb,var(--ink) 7%,transparent)}
.gc.on{background:var(--accent);opacity:.85}
.gact{width:34px;text-align:center}
@media(max-width:760px){.ofmeta,.ofcols{grid-template-columns:1fr}.ofpage{padding:18px 16px}
  .gnm{width:150px;min-width:150px}}
/* cetak A4 khusus penawaran */
@media print{
  body.printing-of>*{display:none !important}
  body.printing-of>main.wrap{display:block !important}
  body.printing-of main.wrap>*:not(#penawaran){display:none !important}
  body.printing-of main.wrap>#penawaran{display:block !important;margin:0;padding:0;border:none}
  body.printing-of #penawaran>h2,body.printing-of #penawaran>.lede,
  body.printing-of #penawaran .boqbar,body.printing-of #penawaran .ofex,
  body.printing-of #penawaran .ofhint{display:none !important}
  body.printing-of .ofpage{border:none;border-radius:0;padding:0;background:#fff;color:#000}
  body.printing-of .ofin{border:none;padding:0}
  body.printing-of{background:#fff}
  body.printing-of .ofh4{break-after:avoid}
  body.printing-of table,body.printing-of .gwrap{break-inside:avoid}
}
"""
