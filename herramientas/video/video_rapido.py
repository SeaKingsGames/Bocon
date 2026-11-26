"""Video de un solo comando: voz + marioneta → MP4 vertical con lip-sync, subtítulos y música.
Uso:
  python3 video_rapido.py voz.mp3 -o video.mp4 [--marioneta ajolote|gato|robot|calavera|mi.marioneta.json]
        [--musica alegre|chill|misterio|accion|tonta|cancion.mp3] [--titulo "Texto arriba"] [--fondo clave|imagen.png]
        [--formato 9:16|16:9|1:1]
Deja junto al video una hoja con cuadros para revisarlo (video.cuadros.jpg).
Para videos con más cosas (gestos, imágenes, cámara, varios personajes) se usa bocon.py directo."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bocon import Bocon
from transcribir import transcribir
from musica import ESTILOS

ap = argparse.ArgumentParser()
ap.add_argument('voz'); ap.add_argument('-o', '--salida', default='video.mp4')
ap.add_argument('--marioneta', default='ajolote'); ap.add_argument('--musica', default='alegre')
ap.add_argument('--titulo'); ap.add_argument('--fondo'); ap.add_argument('--formato', default='9:16')
ap.add_argument('--volumen-musica', type=float, default=.22)
a = ap.parse_args()

palabras = transcribir(a.voz)
with Bocon() as b:
    b.nuevo(a.formato)
    if a.fondo: b.fondo(a.fondo)
    ch = b.marioneta(a.marioneta)
    v = b.voz(ch, a.voz)
    b.subtitulos(ch, palabras, desfase=v['inicio'])
    fin = v['inicio'] + v['dur'] + .5
    if a.titulo: b.texto(a.titulo, 0, fin, y=.14, scale=2.2, wrap=9)
    if a.musica in ESTILOS: b.musica(estilo=a.musica, vol=a.volumen_musica, hasta=fin)
    else: b.musica(a.musica, vol=a.volumen_musica, hasta=fin)
    d = b.dur()
    hoja = os.path.splitext(a.salida)[0] + '.cuadros.jpg'
    b.hoja([round(d * k / 9, 2) for k in range(10)], hoja)
    b.exportar(a.salida)
    if b.errores: print('Errores de la app:', *b.errores[:5], sep='\n  ')
print(f'Listo: {a.salida} ({d:.1f} s) · revisar {hoja}')
