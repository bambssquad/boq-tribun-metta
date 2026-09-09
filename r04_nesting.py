"""Deterministic guillotine rectangle nesting; kerf and edge trim explicit."""
def pack(parts,width=2400,height=1200,trim=10,kerf=3):
 best=None
 keys=[lambda p:p[1]*p[2],lambda p:max(p[1:]),lambda p:min(p[1:]),lambda p:p[1]+p[2],lambda p:p[1],lambda p:p[2],lambda p:(p[1],-p[2]),lambda p:(p[2],-p[1])]
 for key,score,split,prefer_rotation in [(k,s,t,r) for k in keys for s in range(5) for t in range(2) for r in range(2)]:
  sheets=[]
  for ident,w,h in sorted(parts,key=key,reverse=True):
   fits=[]
   for si,s in enumerate(sheets):
    for fi,(x,y,W,H) in enumerate(s['free']):
     for ww,hh in [(w,h),(h,w)]:
      if ww<=W+1e-8 and hh<=H+1e-8:
       metric=[min(W-ww,H-hh),W*H-ww*hh,max(W-ww,H-hh),si*width*height+y*width+x,0 if (ww!=w)==bool(prefer_rotation) else width*height][score]
       fits.append((metric,0 if (ww!=w)==bool(prefer_rotation) else 1,si,fi,ww,hh))
   if not fits:
    sheets.append(dict(free=[(trim,trim,width-2*trim,height-2*trim)],parts=[]));si=len(sheets)-1;fi=0
    W,H=width-2*trim,height-2*trim
    variants=[(0 if (ww!=w)==bool(prefer_rotation) else 1,ww,hh) for ww,hh in [(w,h),(h,w)] if ww<=W and hh<=H]
    if not variants:raise ValueError(f'Part exceeds trimmed stock: {ident}, {w}, {h}')
    _,ww,hh=min(variants)
   else:_,_,si,fi,ww,hh=min(fits)
   s=sheets[si];x,y,W,H=s['free'].pop(fi);s['parts'].append(dict(id=ident,x=x,y=y,w=ww,h=hh))
   # Split to preserve the larger remaining full dimension.
   if (W-ww>H-hh)==bool(split):new=[(x+ww+kerf,y,W-ww-kerf,H),(x,y+hh+kerf,ww,H-hh-kerf)]
   else:new=[(x+ww+kerf,y,W-ww-kerf,hh),(x,y+hh+kerf,W,H-hh-kerf)]
   s['free'] += [r for r in new if r[2]>.001 and r[3]>.001]
  if best is None or (len(sheets),-max((W*H for s in sheets for x,y,W,H in s['free']),default=0))<(len(best),-max((W*H for s in best for x,y,W,H in s['free']),default=0)):best=sheets
 return [s['parts'] for s in best]
