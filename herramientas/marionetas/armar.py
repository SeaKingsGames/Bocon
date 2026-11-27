"""Arma una marioneta de Bocón con las piezas de separar.py: ojos listos, boca gatito, brazos y pies que se mueven.
Uso: python3 herramientas/marionetas/armar.py <Nombre> <carpeta-piezas> <clave> [--guardar]
  -> /tmp/<clave>-gestos.jpg (10 gestos y 3 poses, para revisar)
  con --guardar: recursos/marionetas/<clave>.marioneta.json y <clave>.webp (miniatura saludando)
Ajustes de la cara con AJUSTE='{"ey":-0.12,"my":0.3,"er":0.2,"ex":0.38,"bw":0.62,"dx":0,"ojos":"brillantes","boca":"gatito"}'
(en radios del círculo más grande que cabe en el cuerpo: ey/my altura de ojos y boca, er tamaño de ojo, ex separación, bw ancho de boca).
"""
import sys, json, base64, os
AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(REPO, 'herramientas', 'video'))
from bocon import Bocon

nombre, d, clave = sys.argv[1], sys.argv[2], sys.argv[3]
info = json.load(open(f'{d}/info.json'))
slots = {'cabeza': 'fruta', 'cuerpo': 'cuerpo', 'brazoA': 'armA', 'brazoB': 'armB', 'pieA': 'footA', 'pieB': 'footB'}
files = {k: base64.b64encode(open(f'{d}/{v}.png', 'rb').read()).decode() for k, v in slots.items() if os.path.exists(f'{d}/{v}.png')}
ajuste = json.loads(os.environ.get('AJUSTE', '{}'))

with Bocon() as b:
    pg = b.page
    b.nuevo('1:1')
    b.js("cur().props=[];refreshAll();")
    ch = b.js("""const o=arg,I=o.info,W=I.W,H=I.H,A=o.aj,pp=newPuppet();
      for(const [k,b64] of Object.entries(o.files)){const bin=atob(b64),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i);
        pp.slots[k]=await addAsset(new Blob([u],{type:'image/png'}),'marioneta-'+k+'.png');}
      refSize(pp);
      const [cx,cy]=I.C,R=I.R,[fx0,fy0,fx1,fy1]=I.core,fh=fy1-fy0;
      pp.neck={x:Math.round(cx-W/2),y:Math.round(fy1-fh*.1-H/2)};
      for(const s of ['A','B']){const a=I.arms[s];if(!a) continue;const r=W*.03;
        pp.arms[s]={sh:{x:Math.round(a.sh[0]-W/2),y:Math.round(a.sh[1]+r*.4-H/2)},el:{x:Math.round((a.sh[0]+a.hand[0])/2-W/2),y:Math.round((a.sh[1]+a.hand[1])/2-H/2)}};}
      // cara: en el círculo más grande que cabe en la fruta
      const ey=cy+R*(A.ey??-.12),ex=R*(A.ex??.38),er=R*(A.er??.2),my=cy+R*(A.my??.3);
      pp.eyePts=[{x:Math.round(cx+(A.dx||0)*R-ex-W/2),y:Math.round(ey-H/2),r:Math.round(er)},{x:Math.round(cx+(A.dx||0)*R+ex-W/2),y:Math.round(ey-H/2),r:Math.round(er)}];
      setVecEyes(pp,A.ojos||'brillantes');delete pp.eyePts;
      setVecMouth(pp,A.boca||'gatito');const u=vecUnit(pp);
      pp.g.bocaVec={x:Math.round(cx+(A.dx||0)*R-W/2),y:Math.round(my-H/2),s:Math.round(clamp(R*(A.bw??.62)/(1.44*u),.25,2)*100)/100};
      const ch=newChar('png',{name:o.name,puppet:pp});cur().chars.push(ch);ch.x=.5;ch.y=.6;ch.scale=1.1;refreshAll();return ch.id;""",
               {'files': files, 'info': info, 'name': nombre, 'aj': ajuste})
    pg.wait_for_timeout(600)
    G = [('neutral', 0, 1), ('feliz', 1, 2), ('enojado', 2, 3), ('sorprendido', 3, 4), ('triste', 4, 5), ('guino', 5, 6), ('emocionado', 6, 7), ('confundido', 7, 8), ('malvado', 8, 9), ('dormido', 9, 10)]
    b.bloques(ch, gestos=G, poses=[('saludar', 1, 2.4), ('festejar', 3, 4.4), ('macarena', 5, 10)])
    b.hoja([.5 + i for i in range(10)], f'/tmp/{clave}-gestos.jpg', ancho=300)
    if '--guardar' in sys.argv:
        th = b.js("""const ch=cur().chars.find(c=>c.id===arg),cv=document.createElement('canvas');cv.style.cssText='width:256px;height:256px;position:fixed;left:0;top:0';document.body.appendChild(cv);
          drawAvatar(cv,ch,'feliz',null,'saludar');const u=cv.toDataURL('image/webp',.9);cv.remove();return u;""", ch)
        open(os.path.join(REPO, 'recursos', 'marionetas', f'{clave}.webp'), 'wb').write(base64.b64decode(th.split(',', 1)[1]))
        with pg.expect_download() as dl:
            b.js("exportPuppet(cur().chars.find(c=>c.id===arg));", ch)
        dst = os.path.join(REPO, 'recursos', 'marionetas', f'{clave}.marioneta.json')
        dl.value.save_as(dst)
        print('guardada', dst, os.path.getsize(dst) // 1024, 'KB')
    print('errores', b.errores)
