"""Recorta una hoja de stickers con fondo magenta (o verde) liso: cada sticker sale como PNG con fondo transparente,
sin el borde blanco de sticker, en el orden de la hoja (renglón por renglón).

Uso: python3 herramientas/imagenes/recortar_stickers.py hoja.jpg carpeta-salida [--con-borde] [--huecos 3,10]
     -> carpeta-salida/01.png, 02.png, ... y hoja-revision.jpg (cada recorte numerado sobre gris)
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

src, out = sys.argv[1], sys.argv[2]
con_borde = '--con-borde' in sys.argv
# --huecos 3,10: en esos recortes también quita lo blanco encerrado (es borde que quedó atrapado)
HUECOS = {int(x) for x in (sys.argv[sys.argv.index('--huecos') + 1].split(',') if '--huecos' in sys.argv else [])}
MAX = 440  # lado mayor de cada imagen
os.makedirs(out, exist_ok=True)
a = np.asarray(Image.open(src).convert('RGB')).astype(np.int16)
H, W = a.shape[:2]
bgc = np.median(np.r_[a[:24, :24].reshape(-1, 3), a[-24:, -24:].reshape(-1, 3)], 0)
dist = np.abs(a - bgc).max(2)
near = dist < 70
lab, _ = ndi.label(near)
edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
bg = np.isin(lab, list(edge))
fg = ~bg
fg = ndi.binary_opening(fg, iterations=2)
cl, n = ndi.label(fg)
areas = ndi.sum(fg, cl, range(1, n + 1))
objs = ndi.find_objects(cl)
items = [(i + 1, s) for i, s in enumerate(objs) if areas[i] > H * W * .004]
# orden: renglones por la altura del centro
cent = [((s[0].start + s[0].stop) / 2, (s[1].start + s[1].stop) / 2, i, s) for i, s in items]
cent.sort()
rows, cur = [], []
for c in cent:
    if cur and c[0] - cur[-1][0] > H * .12:
        rows.append(cur); cur = []
    cur.append(c)
rows.append(cur)
order = [c for r in rows for c in sorted(r, key=lambda t: t[1])]

lum = a.mean(2)
sat = a.max(2) - a.min(2)
thumbs = []
for k, (cy, cx, i, s) in enumerate(order, start=1):
    y0, y1 = max(0, s[0].start - 4), min(H, s[0].stop + 4)
    x0, x1 = max(0, s[1].start - 4), min(W, s[1].stop + 4)
    m = ndi.binary_fill_holes(cl[y0:y1, x0:x1] == i)
    m = ndi.binary_dilation(m, iterations=2) & ~bg[y0:y1, x0:x1] | m
    sub = a[y0:y1, x0:x1]
    L = lum[y0:y1, x0:x1]
    alpha = m.astype(float)
    if not con_borde:
        # el borde blanco: lo claro y sin color que toca el fondo
        white = (L > 200) & (sat[y0:y1, x0:x1] < 40) & m
        # la mezcla del blanco con el fondo (rosita si el fondo es magenta, verdecito si es verde)
        sb = sub.astype(float)
        t = np.clip(((255 - sb) * (255 - bgc)).sum(2) / max(1, ((255 - bgc) ** 2).sum()), 0, 1)
        mix = np.abs(sb - (255 - t[..., None] * (255 - bgc))).max(2) < 40
        outside = ~m
        wl, wn = ndi.label(white | outside | (mix & m))
        touch = set(np.unique(wl[outside])) - {0}
        rim = np.isin(wl, list(touch)) & (white | mix)
        keep = m & ~rim
        # huecos blancos encerrados que también son del borde (entre los tallos de unas cerezas, por ejemplo)
        if k in HUECOS:
            pocket = white & keep
            pl, pn = ndi.label(pocket)
            if pn:
                pa = ndi.sum(pocket, pl, range(1, pn + 1))
                keep &= ~np.isin(pl, [j + 1 for j, v in enumerate(pa) if v >= 150])
        # restos de fondo (puntitos del color del fondo)
        bgish = (np.abs(sub - bgc).max(2) < 60) & keep
        bl, bn = ndi.label(bgish)
        if bn:
            ba = ndi.sum(bgish, bl, range(1, bn + 1))
            out_ = ndi.binary_dilation(~keep, iterations=2)
            # solo los que tocan lo de afuera (lo rosita dentro de un corazón se queda)
            kill = [j + 1 for j, v in enumerate(ba) if v < 1500 and (out_ & (bl == j + 1)).any()]
            keep &= ~np.isin(bl, kill)
        # quita pelusitas y rayitas delgadas que quedaron de la orilla del borde
        kl, kn = ndi.label(keep)
        if kn:
            ka = ndi.sum(keep, kl, range(1, kn + 1))
            ok = []
            for j, sl in enumerate(ndi.find_objects(kl)):
                lng = max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start)
                if ka[j] >= 25 and (ka[j] / lng >= 3.5 or ka[j] == ka.max()):
                    ok.append(j + 1)
            keep = np.isin(kl, ok)
        # orilla suave: el gris entre la raya negra y el blanco se vuelve raya semitransparente
        ring = keep & ~ndi.binary_erosion(keep, iterations=2)
        alpha = keep.astype(float)
        soft = ring & (L > 70)
        alpha[soft] = np.clip((255 - L[soft]) / 200, 0, 1)
        rgb = sub.copy()
        dark = np.array([30, 24, 32])
        rgb[soft] = dark
        sub = rgb
    else:
        # sin tocar el borde blanco; solo la orilla contra el fondo suave
        ring = m & ~ndi.binary_erosion(m, iterations=2)
        alpha[ring] = np.clip(dist[y0:y1, x0:x1][ring] / 120, 0, 1)
    ys, xs = np.nonzero(alpha > .02)
    by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    P = 6
    rgba = np.zeros((by1 - by0 + 2 * P, bx1 - bx0 + 2 * P, 4), np.uint8)
    rgba[P:-P, P:-P, :3] = sub[by0:by1, bx0:bx1].clip(0, 255)
    rgba[P:-P, P:-P, 3] = (alpha[by0:by1, bx0:bx1] * 255).astype(np.uint8)
    im = Image.fromarray(rgba)
    if max(im.size) > MAX:
        sc = MAX / max(im.size)
        im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    im.save(f'{out}/{k:02d}.png', optimize=True)
    thumbs.append(im)

# hoja de revisión
cell = 180
cols = 6
rv = Image.new('RGB', (cell * cols, cell * ((len(thumbs) + cols - 1) // cols)), (120, 130, 140))
d = ImageDraw.Draw(rv)
for k, t in enumerate(thumbs):
    t = t.copy(); t.thumbnail((cell - 20, cell - 20))
    x, y = (k % cols) * cell, (k // cols) * cell
    rv.paste(t, (x + (cell - t.width) // 2, y + (cell - t.height) // 2), t)
    d.text((x + 4, y + 2), f'{k + 1:02d}', fill=(255, 255, 255))
rv.save(f'{out}/hoja-revision.jpg', quality=85)
print(os.path.basename(src), len(thumbs), 'recortes')
