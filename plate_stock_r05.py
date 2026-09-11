"""Constructive cutting layout for unchanged 6mm connection blanks."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).parent

def build():
    coupons=[f'T-{i+1:03}' for i in range(464)]+[f'R-{i+1:03}' for i in range(548)]
    sheets=[[] for _ in range(5)];cursor=0
    # First stock: 40 unchanged 200x200 gussets and 75 rotated 90x120 coupons.
    for i in range(40):
        sheets[0].append(dict(id=f'G-{i+1:02}',x=10+(i%11)*203,y=10+(i//11)*203,w=200,h=200))
    for row in range(3):
        for col in range(25):
            sheets[0].append(dict(id=coupons[cursor],x=10+col*93,y=822+row*123,w=90,h=120));cursor+=1
    # Remaining stocks mix 10 short rows and 2 rotated rows: capacity 240 each.
    for stock in sheets[1:]:
        for row in range(12):
            w,h,n,xstep,yy=(120,90,19,123,10+row*93) if row<10 else (90,120,25,93,940+(row-10)*123)
            for col in range(n):
                if cursor==len(coupons):break
                stock.append(dict(id=coupons[cursor],x=10+col*xstep,y=yy,w=w,h=h));cursor+=1
    assert cursor==1012
    all_parts=[p for sheet in sheets for p in sheet]
    assert len(all_parts)==len({p['id'] for p in all_parts})==1052
    for sheet in sheets:
        for i,p in enumerate(sheet):
            assert p['x']>=10 and p['y']>=10 and p['x']+p['w']<=2390 and p['y']+p['h']<=1190
            for q in sheet[i+1:]:
                assert p['x']+p['w']+3<=q['x'] or q['x']+q['w']+3<=p['x'] or p['y']+p['h']+3<=q['y'] or q['y']+q['h']+3<=p['y']
    net_area=sum(p['w']*p['h'] for p in all_parts)/1e6
    out=dict(sheet_width_mm=2400,sheet_height_mm=1200,thickness_mm=6,trim_mm=10,kerf_mm=3,
        sheet_count=5,sheet_kg=1.2*2.4*.006*7850,purchase_kg=5*1.2*2.4*.006*7850,
        net_area_m2=net_area,net_kg=net_area*.006*7850,sheets=sheets,
        note='Ukuran beli 120x240 cm. Potongan tetap: 464 kupingan tangga + 548 kupingan rangka 90x120 mm dan 40 buhul 200x200 mm. Massa teoritis; harga mengikuti tarif/kg Excel. Pola layak, bukan bukti optimum global.')
    folder=ROOT/'assets/r05'
    (folder/'pola-pelat6mm.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    with (folder/'pola-pelat6mm.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['Lembar','Kode_potongan','X_mm','Y_mm','Lebar_mm','Tinggi_mm','Tebal_mm'])
        for n,sheet in enumerate(sheets,1):
            for p in sheet:w.writerow([n,p['id'],p['x'],p['y'],p['w'],p['h'],6])
    print('Plate stock: 5 sheets 1200x2400x6mm; 1052 original blanks; 678.24kg purchase; 10mm trim and 3mm kerf verified.')
    return out

if __name__=='__main__':build()
