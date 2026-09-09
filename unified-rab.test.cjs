const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
class El{constructor(){this.hidden=false;this.events={};this.dataset={};this.attrs={};this.style={};}addEventListener(k,f){this.events[k]=f;}setAttribute(k,v){this.attrs[k]=v;}}
const els={},get=x=>els[x]??=new El(),buttons=['full','quantity'].map(mode=>{const e=new El();e.dataset.rabMode=mode;return e;}),link=new El();
const location={origin:'https://example.test',hash:'#anggaran'},events={},child={postMessage(){}};get('rab-full-frame').contentWindow=child;
vm.runInNewContext(fs.readFileSync('unified-rab.js','utf8'),{document:{getElementById:get,querySelectorAll:q=>q==='[data-rab-mode]'?buttons:[link]},window:{addEventListener:(k,f)=>events[k]=f},location,Number,Math});
assert.equal(get('rab-quantity-panel').hidden,true);buttons[1].events.click();assert.equal(get('rab-full-panel').hidden,true);
link.events.click();assert.equal(get('rab-full-panel').hidden,false);assert.equal(buttons[0].attrs['aria-pressed'],'true');
events.message({origin:'https://evil.test',source:child,data:{type:'metta-rab-height',height:999}});assert.equal(get('rab-full-frame').style.height,undefined);
events.message({origin:location.origin,source:child,data:{type:'metta-rab-height',height:3000}});assert.equal(get('rab-full-frame').style.height,'3016px');assert.equal(get('rab-frame-status').hidden,true);
location.hash='#penawaran';events.hashchange();assert.equal(get('rab-quantity-panel').hidden,false);assert.equal(get('rincian-penawaran').open,true);
console.log('PASS: unified RAB toggle, same-hash return, trusted resize and legacy offer routing.');
