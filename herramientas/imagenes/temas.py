"""Lista de las imágenes por tema (de las hojas en recursos-fuentes/temas/) y cómo se publican.
Uso: python3 herramientas/imagenes/temas.py   (después de recortar cada hoja a /tmp/temas/<hoja>/)
     -> recursos/imagenes/<carpeta>/<nombre>.webp y los renglones para REC_IMGS en /tmp/temas/rec_imgs.js
"""
import os, re, unicodedata
from PIL import Image

# hoja, número, nombre, sección, Pro, va detrás de los personajes
L = """
senales 1 Prohibido el paso|Señales|0|0
senales 2 Precaución (triángulo vacío)|Señales|0|0
senales 3 Flecha a la derecha|Señales|0|0
senales 5 Letrero de madera|Señales|0|0
senales 4 Peatón|Señales|1|0
senales 7 Hombres trabajando|Señales|1|0
senales 8 Discapacidad|Señales|1|0
senales 9 Reciclaje|Señales|1|0
senales 10 Señal redonda amarilla (vacía)|Señales|1|0
senales 11 Señal de prohibido (vacía)|Señales|1|0
senales 12 Información|Señales|1|0
efectos 1 Destello de golpe|Efectos cartoon|0|0
efectos 2 Rayo|Efectos cartoon|0|0
efectos 3 Explosión|Efectos cartoon|0|0
efectos 6 Gotas de agua|Efectos cartoon|0|0
efectos 4 Espiral de mareo|Efectos cartoon|1|0
efectos 5 Fuego verde|Efectos cartoon|1|0
efectos 7 Nube de humo|Efectos cartoon|1|0
efectos 8 Corazón brillante|Efectos cartoon|1|0
efectos 9 Nube de lluvia|Efectos cartoon|1|0
efectos 10 Bomba|Efectos cartoon|1|0
efectos 11 Bola de fuego|Efectos cartoon|1|0
efectos 12 Brillitos|Efectos cartoon|1|0
stickers2 7 Burbujas|Efectos cartoon|1|0
stickers1 4 Sol|Cielo y clima|0|0
stickers1 5 Nube|Cielo y clima|0|0
stickers2 4 Luna|Cielo y clima|0|0
stickers2 8 Arcoíris|Cielo y clima|1|0
stickers2 2 Nube de tormenta|Cielo y clima|1|0
stickers1 2 Lluvia de corazones|Cielo y clima|1|0
stickers2 5 Tornado|Cielo y clima|1|0
stickers2 11 Estrella fugaz|Cielo y clima|1|0
stickers2 12 Estrellita|Cielo y clima|1|0
stickers1 12 Planeta Tierra|Cielo y clima|1|0
stickers1 1 Corona|Stickers|0|0
stickers1 3 Letrero GO|Stickers|0|0
stickers1 9 Trébol|Stickers|0|0
stickers2 1 Trébol de 4 hojas|Stickers|1|0
stickers1 6 Llave|Stickers|1|0
stickers2 6 Llave dorada|Stickers|1|0
stickers1 7 Macarons|Stickers|1|0
stickers1 8 Globo aerostático|Stickers|1|0
stickers1 11 Cohete|Stickers|1|0
stickers1 10 Uvas|Stickers|1|0
stickers2 10 Cerezas|Stickers|1|0
stickers2 9 Hoja|Stickers|1|0
stickers2 3 Letrero DANGER|Stickers|1|0
aparatos2 5 Lavadora|Aparatos|0|1
aparatos2 9 Televisión|Aparatos|0|1
aparatos2 11 Computadora|Aparatos|0|0
aparatos2 6 Secadora|Aparatos|1|1
aparatos2 7 Aspiradora|Aparatos|1|0
aparatos1 7 Aspiradora robot|Aparatos|1|0
aparatos2 8 Plancha y burro|Aparatos|1|0
aparatos1 8 Vaporizador de ropa|Aparatos|1|0
aparatos1 9 Pantalla curva|Aparatos|1|1
aparatos1 11 Laptop|Aparatos|1|0
aparatos2 10 Control de consola|Aparatos|1|0
aparatos1 10 Lentes de realidad virtual|Aparatos|1|0
aparatos1 12 Bocina|Aparatos|1|0
aparatos2 12 Radio|Aparatos|1|0
aparatos2 4 Microondas|Cocina|0|0
aparatos1 4 Microondas y freidora de aire|Cocina|1|0
aparatos1 2 Horno tostador|Cocina|1|0
aparatos2 2 Tostador (2)|Cocina|1|0
aparatos1 3 Licuadora sonriente|Cocina|1|0
aparatos1 1 Procesador de alimentos (2)|Cocina|1|0
aparatos2 1 Batidora de pedestal roja|Cocina|1|0
aparatos2 3 Cafetera de goteo|Cocina|1|0
muebles 1 Sillón de dos plazas|Casa|0|1
muebles 5 Cama|Casa|0|1
muebles 2 Mesa de centro|Casa|0|1
muebles 10 Refrigerador|Casa|0|1
muebles 3 Sillón individual|Casa|1|1
muebles 4 Librero|Casa|1|1
muebles 6 Buró con lámpara|Casa|1|1
muebles 7 Comedor|Casa|1|1
muebles 8 Ropero|Casa|1|1
muebles 9 Estufa|Casa|1|1
muebles 11 Escritorio|Casa|1|1
muebles 12 Cómoda|Casa|1|1
"""
DIR = {'Señales': 'senales', 'Efectos cartoon': 'efectos', 'Cielo y clima': 'cielo', 'Stickers': 'stickers', 'Aparatos': 'aparatos', 'Cocina': 'cocina', 'Casa': 'casa'}
PRE = {'Señales': 'sen', 'Efectos cartoon': 'efe', 'Cielo y clima': 'cie', 'Stickers': 'sti', 'Aparatos': 'apa', 'Cocina': 'coc', 'Casa': 'casa'}
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def key(pre, t):
    w = [x for x in re.split(r'[^A-Za-z0-9]+', unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()) if x]
    return pre + ''.join(x[:1].upper() + x[1:] for x in w)

rows, total = [], 0
for ln in L.strip().splitlines():
    a, rest = ln.split(' ', 2)[:2], ln.split(' ', 2)[2]
    hoja, n = a[0], int(a[1])
    label, cat, pro, atras = rest.split('|')
    d = os.path.join(REPO, 'recursos', 'imagenes', DIR[cat])
    os.makedirs(d, exist_ok=True)
    f = f'{slug(label)}.webp'
    im = Image.open(f'/tmp/temas/{hoja}/{n:02d}.png')
    im.save(os.path.join(d, f), 'WEBP', quality=90, method=6)
    total += os.path.getsize(os.path.join(d, f))
    e = f"{{k:'{key(PRE[cat], label)}',label:'{label}',src:'recursos/imagenes/{DIR[cat]}/{f}',cat:'{cat}'" + (",layer:'atras'" if atras == '1' else '') + (",pro:1" if pro == '1' else '') + '}'
    rows.append(e)
open('/tmp/temas/rec_imgs.js', 'w').write(',\n'.join('  ' + r for r in rows))
print(len(rows), 'imágenes', total // 1024, 'KB')
