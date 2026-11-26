"""Música de fondo hecha con código (sin derechos de autor), para poner bajita debajo de la voz.
Uso: python3 musica.py --estilo alegre --dur 30 -o musica.wav [--bpm 112] [--semilla 3]
Estilos: alegre, chill, misterio, accion, tonta"""
import argparse, math
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
ESTILOS = {
    # bpm, acordes (MIDI), instrumento del arpegio, bajo, batería (16 pasos por compás: k=bombo s=tarola h=platillo)
    'alegre':   dict(bpm=112, acordes=[[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]], arp='pluck', bajo='bajo',
                     k='x...x...x...x...', s='....x.......x...', h='x.x.x.x.x.x.x.x.', pad=False),
    'chill':    dict(bpm=82, acordes=[[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]], arp='piano', bajo='bajo',
                     k='x.........x.....', s='....x.......x...', h='x.x.x.x.x.x.x.x.', pad=True, vinilo=True, swing=.18),
    'misterio': dict(bpm=88, acordes=[[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]], arp='pizz', bajo='bajo',
                     k='x.......x.......', s='................', h='..x...x...x...x.', pad=True),
    'accion':   dict(bpm=140, acordes=[[50, 53, 57], [46, 50, 53], [48, 52, 55], [45, 49, 52]], arp='pluck', bajo='sierra',
                     k='x...x...x...x...', s='....x.......x...', h='xxxxxxxxxxxxxxxx', pad=False, bajo16=True),
    'tonta':    dict(bpm=120, acordes=[[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]], arp='xilo', bajo='tuba',
                     k='x.......x.......', s='....x.......x...', h='................', pad=False, umpa=True),
}

nf = lambda n: 440 * 2 ** ((n - 69) / 12)
lp = lambda x, f: sosfilt(butter(2, min(f, SR * .45), 'low', fs=SR, output='sos'), x)
hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)

def env(n, a=.005, dec=.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)

def nota(tipo, n, dur, rng):
    m = int(SR * (dur + .6)); t = np.arange(m) / SR; f = nf(n)
    if tipo == 'pluck':
        x = 2 * ((t * f) % 1) - 1; x = lp(x, 900 + 2500 * math.exp(-dur)) * env(m, .003, .25)
    elif tipo == 'piano':
        x = (np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .1 * np.sin(6 * np.pi * f * t))
        x *= env(m, .004, .9) * (1 + .15 * np.sin(2 * np.pi * 4.5 * t))
    elif tipo == 'pizz':
        x = 2 * np.abs(2 * ((t * f) % 1) - 1) - 1; x = lp(x, 1800) * env(m, .002, .14)
    elif tipo == 'xilo':
        x = (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t / .03)) * env(m, .001, .18)
    elif tipo == 'bajo':
        x = (np.sin(2 * np.pi * f * t) + .25 * np.sign(np.sin(2 * np.pi * f * t))) ; x = lp(x, 500) * env(m, .005, .35)
    elif tipo == 'sierra':
        x = lp(2 * ((t * f) % 1) - 1, 700) * env(m, .003, .12)
    elif tipo == 'tuba':
        x = lp(np.sign(np.sin(2 * np.pi * f * t)), 420) * env(m, .02, .16)
    elif tipo == 'pad':
        x = sum(2 * ((t * f * d) % 1) - 1 for d in (.996, 1, 1.004)) / 3
        x = lp(x, 1100) * np.minimum(1, t / .6) * np.minimum(1, np.maximum(0, (dur + .6 - t) / .6))
    return x

def bombo(rng):
    m = int(SR * .35); t = np.arange(m) / SR
    return np.sin(2 * np.pi * (45 * t + 75 * .045 * (1 - np.exp(-t / .045)))) * np.exp(-t / .12)
def tarola(rng):
    m = int(SR * .2); t = np.arange(m) / SR
    return (hp(rng.standard_normal(m), 1800) * .6 + .4 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t / .06)
def platillo(rng):
    m = int(SR * .06); return hp(rng.standard_normal(m), 7000) * np.exp(-np.arange(m) / SR / .015)

def poner(pista, x, t, vol=1., pan=0.):
    i = int(t * SR); j = min(len(pista), i + len(x))
    if i >= len(pista): return
    pista[i:j, 0] += x[:j - i] * vol * (1 - max(0, pan)); pista[i:j, 1] += x[:j - i] * vol * (1 + min(0, pan))

def hacer(estilo='alegre', dur=30., bpm=None, semilla=1):
    E = ESTILOS[estilo]; rng = np.random.default_rng(semilla)
    bpm = bpm or E['bpm']; paso = 60 / bpm / 4; compas = paso * 16
    n = int(SR * (dur + 2)); pista = np.zeros((n, 2))
    swing = E.get('swing', 0)
    k, s, h = bombo(rng), tarola(rng), platillo(rng)
    for b in range(math.ceil(dur / compas) + 1):
        t0 = b * compas; ac = E['acordes'][b % len(E['acordes'])]
        if E['pad']: [poner(pista, nota('pad', x - 12, compas, rng), t0, .1) for x in ac]
        for i in range(16):
            t = t0 + i * paso + (swing * paso if i % 2 else 0)
            if i % 2 == 0:  # arpegio en octavos
                x = ac[(i // 2) % len(ac)] + (12 if (i // 2) >= len(ac) else 0)
                poner(pista, nota(E['arp'], x, paso * 2, rng), t, .22, pan=-.35 if (i // 2) % 2 else .35)
            if E.get('umpa'):
                if i in (0, 8): poner(pista, nota('tuba', ac[0] - 24, paso * 2, rng), t, .55)
                if i in (4, 12): poner(pista, nota('tuba', ac[2] - 24, paso * 2, rng), t, .4)
            elif E.get('bajo16') or i in (0, 6, 8, 14):
                poner(pista, nota(E['bajo'], ac[0] - 24, paso * (1 if E.get('bajo16') else 2), rng), t, .45)
            if b == 0 and i < 8 and estilo != 'misterio': continue  # entrada sin batería
            if E['k'][i] == 'x': poner(pista, k, t, .6)
            if E['s'][i] == 'x': poner(pista, s, t, .3)
            if E['h'][i] == 'x': poner(pista, h, t, .12 if i % 4 else .18, pan=.2)
    if E.get('vinilo'):
        crep = (rng.random(n) > .9996) * rng.standard_normal(n) * .08 + hp(rng.standard_normal(n), 3000) * .004
        pista += crep[:, None]
    ir = rng.standard_normal(int(SR * .9)) * np.exp(-np.arange(int(SR * .9)) / SR / .25)
    for c in range(2): pista[:, c] += .12 * fftconvolve(pista[:, c], ir / np.abs(ir).sum() * 40)[:n]
    pista = pista[:int(SR * dur)]
    fi, fo = int(SR * .3), int(SR * min(1.5, dur / 4))
    pista[:fi] *= np.linspace(0, 1, fi)[:, None]; pista[-fo:] *= np.linspace(1, 0, fo)[:, None]
    rms = np.sqrt((pista ** 2).mean()) or 1
    pista *= 10 ** (-16 / 20) / rms  # más o menos -16 dB
    return np.clip(pista, -.98, .98)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--estilo', default='alegre', choices=ESTILOS); ap.add_argument('--dur', type=float, default=30)
    ap.add_argument('--bpm', type=float); ap.add_argument('--semilla', type=int, default=1); ap.add_argument('-o', '--salida', default='musica.wav')
    a = ap.parse_args()
    wavfile.write(a.salida, SR, (hacer(a.estilo, a.dur, a.bpm, a.semilla) * 32767).astype(np.int16))
    print('Música', a.estilo, f'{a.dur:.1f} s →', a.salida)
