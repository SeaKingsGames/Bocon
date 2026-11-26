# Kit de video

Para hacer videos con Bocón sin abrir la app: se maneja desde Python con las mismas funciones del programa. No se publica (Vercel solo sube `dist/`).

## Una vez por máquina

```bash
bash herramientas/video/preparar.sh
```

Instala lo de Python, baja Whisper small desde npm (unos 250 MB, porque Hugging Face suele estar bloqueado) y arma las fuentes de la app desde @fontsource. Todo se guarda en `~/.cache/bocon-video`. Si se vuelve a correr, no baja nada de nuevo.

## Video rápido (un comando)

```bash
python3 herramientas/video/video_rapido.py voz.mp3 -o video.mp4 \
  --marioneta ajolote --musica alegre --titulo "Texto de arriba"
```

- `--marioneta`: `ajolote`, `gato`, `robot`, `calavera` o la ruta de un `.marioneta.json`.
- `--musica`: un estilo hecho con código (`alegre`, `chill`, `misterio`, `accion`, `tonta`) o un archivo de audio. Siempre lleva música.
- `--fondo`: clave de un fondo de Bocón o una imagen. `--formato`: `9:16` (default), `16:9` o `1:1`.
- Junto al video deja `video.cuadros.jpg` con 10 cuadros para revisarlo de un vistazo.
- El audio sale en AAC a -14 LUFS (TikTok, Reels, Shorts).

## Videos con más cosas

```python
import sys; sys.path.insert(0, 'herramientas/video')
from bocon import Bocon
from transcribir import transcribir

palabras = transcribir('voz.mp3')            # [{w, a, b}] en segundos
with Bocon() as b:
    b.nuevo('9:16')
    b.fondo('cocina')                         # clave de REC_FONDOS o una imagen
    ch = b.marioneta('mi.marioneta.json')
    v = b.voz(ch, 'voz.mp3')                  # lip-sync automático
    b.subtitulos(ch, palabras, desfase=v['inicio'])
    b.bloques(ch, gestos=[('feliz', 0, 2)], poses=[('saludar', 0, 1.5)])
    b.imagen('manzana.webp', 1, 3, x=.7, y=.35, anim='flotar')
    b.texto('¡Atención!', 0, 2, preset='comic', y=.15)
    b.sonido('pop', 1.0)
    b.musica(estilo='chill')                  # al final: dura lo que dure el video
    b.hoja([0.5, 2, 4], 'revisar.jpg')
    b.exportar('video.mp4')
```

- `b.catalogo()`: las claves de gestos, poses, acciones, estilos de texto, fondos, imágenes y sonidos rápidos.
- `b.js("código", arg)`: para todo lo que no tenga atajo (cámara, movimientos, varias escenas). Ahí están `S`, `cur()`, `newProp`, `fixMove`, etc.
- `b.errores`: errores de la app durante la sesión.
- `b.dialogo(audio, lineas, colores)`: un audio con varias voces. Cada línea va al personaje que la dice (solo él mueve la boca) y sus subtítulos salen de su color.
- `b.mover(id, t0, t1, x=, y=, s=, o=)`: mueve, escala o desvanece un personaje o una imagen (pasa siempre x, y y s).
- `b.desde_imagen('personaje.png', 'Nombre')`: arma una marioneta con «Marioneta desde una imagen» (PNG transparente o fondo verde).
- `b.texto(..., scale=2.5)`: si no le das `wrap`, lo calcula para que el texto quepa a lo ancho (el ancho crece con la escala).
- `b.guardar_proyecto('video.bocon.json')`: solo si se necesita el proyecto para editarlo en Bocón.

## Archivos

- `preparar.sh`: instala y baja lo necesario.
- `fuentes.py`: arma el CSS de fuentes a partir de lo que pide `index.html`.
- `transcribir.py`: Whisper con tiempos por palabra (`python3 transcribir.py voz.mp3`).
- `musica.py`: música de fondo con código, sin derechos de autor (`python3 musica.py --estilo tonta --dur 20`).
- `bocon.py`: abre Bocón sin ventana y trae los atajos.
- `video_rapido.py`: el video de un comando.
