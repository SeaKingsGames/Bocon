"""Separa un personaje tipo fruta u objeto (PNG con fondo transparente, sin ojos ni boca, brazos colgando a los lados y piernas abajo)
en piezas para Bocón: el cuerpo grueso (va como cabeza, así gira entero), brazos y pies.

Uso: python3 herramientas/marionetas/separar.py fresa.png /tmp/fresa-piezas
     -> fruta.png, cuerpo.png, armA.png, armB.png, footA.png, footB.png, info.json y ver.png (para revisar: cada pieza de un color)

A es el lado derecho del personaje (a la izquierda de la imagen), B el izquierdo.
Variables opcionales:
  OPEN=0.07   qué tan grueso debe ser algo para ser "cuerpo" (fracción del lado corto)
  INK=95      qué tan oscura es la raya del contorno (0-255)
  FORCE=3:armA,6:footA   manda manchas a una pieza (los números salen con DEBUG=1)
  MIRROR=A    si un brazo casi no se ve (detrás del cuerpo), lo hace en espejo del otro
"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import disk

f = sys.argv[1]
base = os.path.splitext(os.path.basename(f))[0]
out = sys.argv[2] if len(sys.argv) > 2 else f'/tmp/{base}-piezas'
os.makedirs(out, exist_ok=True)
im = np.array(Image.open(f).convert('RGBA'))
H, W = im.shape[:2]
A = im[..., 3]
sil = A > 100
any_px = A > 0
lum = (0.299 * im[..., 0] + 0.587 * im[..., 1] + 0.114 * im[..., 2])
ink = sil & (lum < float(os.environ.get('INK', 95)))
light = sil & ~ink

# núcleo: lo grueso (la fruta); brazos y piernas son delgados y se van
r = max(8, int(min(W, H) * float(os.environ.get('OPEN', .07))))
op = ndi.binary_opening(sil, structure=disk(r))
lab, n = ndi.label(op)
sizes = ndi.sum(op, lab, range(1, n + 1))
core = lab == (1 + int(np.argmax(sizes)))
ys, xs = np.nonzero(core)
fx0, fx1, fy0, fy1 = xs.min(), xs.max(), ys.min(), ys.max()
fcx, fw, fh = (fx0 + fx1) / 2, fx1 - fx0, fy1 - fy0

# manchas claras (el relleno de cada forma)
L, nl = ndi.label(light)
objs = ndi.find_objects(L)
fruit_ids, limbs = [], {'armA': [], 'armB': [], 'footA': [], 'footB': []}
FORCE = dict(p.split(':') for p in os.environ.get('FORCE', '').split(',') if p)
MIRROR = os.environ.get('MIRROR', '')
for i, sl in enumerate(objs, start=1):
    if sl is None:
        continue
    m = L[sl] == i
    area = m.sum()
    if area < 30:
        fruit_ids.append(i)
        continue
    inc = (core[sl] & m).sum() / area
    if os.environ.get('DEBUG'):
        print('mancha', i, 'area', int(area), 'x', sl[1].start, sl[1].stop, 'y', sl[0].start, sl[0].stop, 'en el cuerpo', round(inc, 2))
    yy, xx = np.nonzero(m)
    yy = yy + sl[0].start
    xx = xx + sl[1].start
    cx, cy = xx.mean(), yy.mean()
    y0, y1, x0, x1 = yy.min(), yy.max(), xx.min(), xx.max()
    side = 'A' if cx < fcx else 'B'
    if str(i) in FORCE:
        limbs[FORCE[str(i)]].append(i)
    elif inc >= .5:
        fruit_ids.append(i)
    elif y1 > H * .86 and y0 > fy0 + fh * .55 and abs(cx - fcx) < fw * .45:
        limbs['foot' + side].append(i)
    elif abs(cx - fcx) > fw * .3 and cy > fy0 + fh * .3 and (y1 - y0) > (x1 - x0) * 1.15 and area > W * H * .004:
        limbs['arm' + side].append(i)
    else:
        fruit_ids.append(i)

t = max(4, int(min(W, H) * .028))  # grosor de la raya
fruit_in = np.isin(L, fruit_ids)
near_fruit = ndi.binary_dilation(fruit_in, structure=disk(t))
pieces = {}
limb_only = np.zeros_like(sil)
info = {'W': W, 'H': H, 'core': [int(fx0), int(fy0), int(fx1), int(fy1)]}
for k, ids in limbs.items():
    if not ids:
        continue
    m = np.isin(L, ids)
    reg = m | (ndi.binary_dilation(m, structure=disk(t)) & any_px & ~light)
    reg = ndi.binary_fill_holes(reg)
    # la orillita suave
    reg = reg | (ndi.binary_dilation(reg, iterations=2) & any_px & (A < 230) & ~near_fruit)
    pieces[k] = reg
    limb_only |= reg & ~near_fruit
fruit = any_px & ~limb_only
# quita pedacitos sueltos de la fruta
lf, nf = ndi.label(fruit)
if nf > 1:
    s = ndi.sum(fruit, lf, range(1, nf + 1))
    keep = 1 + int(np.argmax(s))
    small = (lf != keep) & fruit
    # lo suelto chiquito se va con la pieza vecina más cercana (o se queda si es grande)
    for j in range(1, nf + 1):
        if j == keep:
            continue
        mj = lf == j
        if mj.sum() > W * H * .01:
            continue
        fruit &= ~mj
        best, bd = None, 1e9
        for k, reg in pieces.items():
            d = (ndi.binary_dilation(mj, iterations=3) & reg).sum()
            if d and -d < bd:
                best, bd = k, -d
        if best:
            pieces[best] |= mj
if MIRROR in ('A', 'B'):
    src, dst = 'arm' + ('B' if MIRROR == 'A' else 'A'), 'arm' + MIRROR
    ms = np.isin(L, limbs[src])
    md = np.isin(L, limbs[dst])
    sy, sx = np.nonzero(ms)
    dy_, dx_ = np.nonzero(md)
    # en espejo: la orilla de afuera del brazo copiado va donde está la orilla de afuera de lo que se ve
    mx = W - 1 - sx
    ox = (dx_.min() - mx.min()) if MIRROR == 'A' else (dx_.max() - mx.max())
    oy = dy_.min() - sy.min()
    reg = pieces[src]
    ry, rx = np.nonzero(reg)
    nx, ny = W - 1 - rx + ox, ry + oy
    ok = (nx >= 0) & (nx < W) & (ny >= 0) & (ny < H)
    newp = np.zeros_like(sil)
    newp[ny[ok], nx[ok]] = True
    # los pixeles del brazo copiado (para el hombro y la mano)
    mm = np.zeros_like(sil)
    qx, qy = W - 1 - sx + ox, sy + oy
    ok2 = (qx >= 0) & (qx < W) & (qy >= 0) & (qy < H)
    mm[qy[ok2], qx[ok2]] = True
    MIRRORED = {'side': MIRROR, 'mask': mm, 'piece': newp, 'src': src, 'ox': int(ox), 'oy': int(oy)}
else:
    MIRRORED = None
pieces['fruta'] = fruit
# cuerpo: el centro de la fruta sin orillas (queda escondido detrás; sirve de base)
dt = ndi.distance_transform_edt(fruit)
pieces['cuerpo'] = dt > t * 3

# centro de la cara: el círculo más grande que cabe en la fruta (sin hojas)
dcore = ndi.distance_transform_edt(core)
R = float(dcore.max())
cy, cx = np.unravel_index(int(np.argmax(dcore)), dcore.shape)
info.update({'R': R, 'C': [int(cx), int(cy)]})

def save(name, mask):
    o = np.zeros_like(im)
    o[mask] = im[mask]
    Image.fromarray(o).save(f'{out}/{name}.png')

for k, m in pieces.items():
    if MIRRORED and k == 'arm' + MIRRORED['side']:
        continue
    save(k, m)
if MIRRORED:
    s_ = pieces[MIRRORED['src']]
    o = np.zeros_like(im)
    ry, rx = np.nonzero(s_)
    nx, ny = W - 1 - rx + MIRRORED['ox'], ry + MIRRORED['oy']
    ok = (nx >= 0) & (nx < W) & (ny >= 0) & (ny < H)
    o[ny[ok], nx[ok]] = im[ry[ok], rx[ok]]
    Image.fromarray(o).save(f"{out}/arm{MIRRORED['side']}.png")
    pieces['arm' + MIRRORED['side']] = MIRRORED['piece']

# hombro y mano de cada brazo
arms = {}
for side in 'AB':
    k = 'arm' + side
    if k not in pieces:
        continue
    m = MIRRORED['mask'] if MIRRORED and side == MIRRORED['side'] else np.isin(L, limbs[k])
    yy, xx = np.nonzero(m)
    sg = -1 if side == 'A' else 1
    top = yy.min()
    band = yy <= top + (yy.max() - top) * .25
    inner = ((xx - fcx) * sg)[band]
    sel = band.copy()
    sel[band] = inner < inner.min() + W * .03
    S = (float(xx[sel].mean()), float(yy[sel].mean()))
    d2 = (xx - S[0]) ** 2 + (yy - S[1]) ** 2
    j = int(np.argmax(d2))
    Hd = (float(xx[j]), float(yy[j]))
    arms[side] = {'sh': S, 'hand': Hd}
info['arms'] = arms
info['feet'] = [k for k in ('footA', 'footB') if k in pieces]
json.dump(info, open(f'{out}/info.json', 'w'))

# vista de revisión: colores por pieza
v = np.full((H, W, 3), 235, np.uint8)
cols = {'fruta': (240, 200, 60), 'armA': (230, 120, 50), 'armB': (40, 150, 210), 'footA': (60, 190, 100), 'footB': (150, 80, 200)}
for k, c in cols.items():
    if k in pieces:
        v[pieces[k]] = (np.array(c) * .6 + v[pieces[k]] * .4).astype(np.uint8)
v[ink] = (v[ink] * .5).astype(np.uint8)
Image.fromarray(v).save(f'{out}/ver.png')
print(base, {k: int(m.sum()) for k, m in pieces.items()}, 'R', round(R), 'C', info['C'])
