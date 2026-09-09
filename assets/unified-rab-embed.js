if(new URLSearchParams(location.search).get('embed')==='rab'){
 let pending=false,last=0;
 const measure=()=>{if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;const h=Math.ceil(document.body.getBoundingClientRect().height);if(h!==last){last=h;parent.postMessage({type:'metta-rab-height',height:h},location.origin);}});};
 new ResizeObserver(measure).observe(document.body);
 window.addEventListener('message',e=>{if(e.origin===location.origin&&e.source===parent&&e.data?.type==='metta-rab-measure'){last=0;measure();}});window.addEventListener('load',measure);measure();
}
