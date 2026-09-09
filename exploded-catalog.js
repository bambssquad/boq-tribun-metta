'use strict';
const ExplodedCatalog=(()=>{
 function layout(count,width,height){const cols=Math.max(1,Math.ceil(Math.sqrt(count*width/Math.max(1,height)))),rows=Math.max(1,Math.ceil(count/cols));return {cols,rows,cell:Math.min(width/cols,height/rows)*.88};}
 function target(index,bounds,layout,width,height,zoom=1,ox=0,oy=0){const {cols,rows,cell}=layout;const size=Math.max(bounds[2]-bounds[0],bounds[3]-bounds[1],1);return {x:width/2+ox+((index%cols)-(cols-1)/2)*cell*zoom,y:height/2+oy+(Math.floor(index/cols)-(rows-1)/2)*cell*zoom,s:cell*.72*zoom/size,cx:(bounds[0]+bounds[2])/2,cy:(bounds[1]+bounds[3])/2};}
 function dimensions(b){const v=b.length===24?b:Array.from({length:8},(_,i)=>[b[0]+([1,2,5,6].includes(i)?b[3]:0),b[1]+([2,3,6,7].includes(i)?b[4]:0),b[2]+(i>=4?b[5]:0)]).flat();const distance=(a,c)=>Math.hypot(...[0,1,2].map(k=>v[a*3+k]-v[c*3+k]));return [distance(0,1),distance(1,2),distance(0,4)];}
 return {layout,target,dimensions};
})();
if(typeof module!=='undefined')module.exports=ExplodedCatalog;
