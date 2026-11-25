import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
XS=[0,420,726,1010,1288,1578,1868,2156,2576]; YS=[0,285,499,717,925,1134,1405]
files=sys.argv[1:4]
HOLES={0:{(5,2),(1,7)},1:{(5,1),(5,2),(1,0),(0,6),(0,3)},2:{(0,6),(0,7),(1,4),(1,5),(1,7),(2,3),(2,4),(2,5)}}; out=sys.argv[4]
for fi,f in enumerate(files):
    YS=[0,294,501,710,914,1118,1405] if fi==2 else [0,285,499,717,925,1134,1405]
    a=np.asarray(Image.open(f).convert('RGB')).astype(np.int16)
    bg=np.median(a[2:20,2:20].reshape(-1,3),0)
    for r in range(6):
        for c in range(8):
            I=7 if fi<2 else 0
            cell=a[YS[r]+I:YS[r+1]-I, XS[c]+I:XS[c+1]-I]
            d=np.abs(cell-bg).max(2)
            near=d<28
            lab,_=nd.label(near)
            border=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0}
            bgm=np.isin(lab,list(border))
            fg=~bgm
            fg=nd.binary_opening(fg,iterations=1)
            cl,n=nd.label(fg)
            if n==0: print('empty',fi,r,c); continue
            sl=nd.find_objects(cl); areas=nd.sum(fg,cl,range(1,n+1))
            H=cell.shape[0]; keep=np.zeros(n+1,bool)
            big=areas.max()
            for i,s in enumerate(sl):
                h=s[0].stop-s[0].start
                if areas[i]<60: continue
                if fi==0 and s[0].start>H*0.62 and h<42 and areas[i]<big*0.15: continue   # etiquetas de texto
                if areas[i]<big*0.01: continue
                keep[i+1]=True
            fg=keep[cl]
            if fg.sum()<500: print('empty',fi,r,c); continue
            fg=nd.binary_fill_holes(fg)
            tol=16 if fi<2 else 3
            holeish=(np.abs(cell-bg).max(2)<=tol)&fg
            if (r,c) in HOLES[fi]:
                holeish=nd.binary_opening(nd.binary_closing(holeish,iterations=2),iterations=1)&fg
                hl,hn=nd.label(holeish)
                if hn:
                    ha=nd.sum(holeish,hl,range(1,hn+1))
                    kill=np.r_[False,ha>250]
                    fg=fg&~kill[hl]
            # alfa suave en el borde
            ring=nd.binary_dilation(fg,iterations=2)&~fg
            alpha=np.where(fg,1.0,np.where(ring,np.clip(d/60,0,1),0))
            ys,xs=np.nonzero(alpha>0); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
            P=6
            rgba=np.zeros((y1-y0+2*P,x1-x0+2*P,4),np.uint8)
            rgba[P:-P,P:-P,:3]=cell[y0:y1,x0:x1].clip(0,255)
            rgba[P:-P,P:-P,3]=(alpha[y0:y1,x0:x1]*255).astype(np.uint8)
            Image.fromarray(rgba).save(f'{out}/{fi+1}-{r+1}-{c+1}.png',optimize=True)
