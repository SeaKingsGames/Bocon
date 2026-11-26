"""Transcribe un audio en español con tiempos por palabra (Whisper small, sin internet).
Uso: python3 transcribir.py voz.mp3 [-o palabras.json] [--texto "nombres raros, marcas"]
Imprime el texto con tiempos para planear y guarda [{w,a,b}] en segundos (para subtítulos)."""
import argparse, json, os, subprocess
import numpy as np

C = os.environ.get('BOCON_CACHE', os.path.expanduser('~/.cache/bocon-video'))


def transcribir(ruta, idioma='es', texto=None, mostrar=True):
    from faster_whisper import WhisperModel
    # Se decodifica con ffmpeg y se pasa el arreglo: la versión de av que trae faster-whisper choca con algunos archivos.
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', ruta, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.float32)
    m = WhisperModel(os.path.join(C, 'whisper'), device='cpu', compute_type='int8')
    segs, _ = m.transcribe(audio, language=idioma, word_timestamps=True, initial_prompt=texto, beam_size=5)
    palabras = []
    for s in segs:
        if mostrar: print(f'[{s.start:6.2f} – {s.end:6.2f}] {s.text.strip()}')
        for w in s.words or []:
            t = w.word.strip()
            if t: palabras.append({'w': t, 'a': round(w.start, 3), 'b': round(w.end, 3)})
    return palabras


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('audio'); ap.add_argument('-o', '--salida')
    ap.add_argument('--idioma', default='es'); ap.add_argument('--texto', help='pista de vocabulario (nombres, marcas)')
    a = ap.parse_args()
    p = transcribir(a.audio, a.idioma, a.texto)
    salida = a.salida or os.path.splitext(a.audio)[0] + '.palabras.json'
    json.dump(p, open(salida, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'{len(p)} palabras → {salida}')
