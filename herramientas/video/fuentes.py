"""Arma un CSS con las fuentes que pide index.html, sacadas de @fontsource (npm).
Uso: python3 fuentes.py <carpeta_cache>   → deja <cache>/fuentes/fuentes.css y los .woff2
El kit responde con ese CSS cuando la app pide fonts.googleapis.com."""
import json, os, re, subprocess, sys, tarfile, tempfile, urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, '..', '..'))
cache = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/.cache/bocon-video')
dest = os.path.join(cache, 'fuentes')
os.makedirs(dest, exist_ok=True)

html = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
url = re.search(r'https://fonts\.googleapis\.com/css2\?[^"\']+', html).group(0)
pedidas = {}  # familia -> pesos
for fam in urllib.parse.parse_qs(urllib.parse.urlparse(url.replace('&amp;', '&')).query)['family']:
    nombre, _, ejes = fam.partition(':')
    pesos = re.findall(r'\d{3}', ejes.split('@')[-1]) if '@' in ejes else ['400']
    pedidas[nombre] = pesos

lista = os.path.join(dest, 'lista.json')
if os.path.exists(lista) and json.load(open(lista)) == pedidas and os.path.exists(os.path.join(dest, 'fuentes.css')):
    print('Fuentes ya listas'); sys.exit(0)

css = []
with tempfile.TemporaryDirectory() as tmp:
    for nombre, pesos in pedidas.items():
        pkg = '@fontsource/' + nombre.lower().replace(' ', '-')
        try:
            tgz = subprocess.run(['npm', 'pack', '-q', pkg], cwd=tmp, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
        except subprocess.CalledProcessError:
            print('No encontré', pkg, '(se queda la fuente de respaldo)'); continue
        d = os.path.join(tmp, nombre)
        with tarfile.open(os.path.join(tmp, tgz)) as t: t.extractall(d, filter='data')
        base = os.path.join(d, 'package')
        for w in pesos:
            for sub in ('latin-ext', 'latin'):
                f = os.path.join(base, f'{sub}-{w}.css')
                if not os.path.exists(f): continue
                txt = open(f, encoding='utf-8').read()
                for arch in re.findall(r'url\(\./files/([^)]+)\)', txt):
                    src = os.path.join(base, 'files', arch)
                    if os.path.exists(src): open(os.path.join(dest, arch), 'wb').write(open(src, 'rb').read())
                txt = re.sub(r'url\(\./files/([^)]+)\)', r'url(/__kit/fuentes/\1)', txt)
                txt = re.sub(r"font-family:\s*'[^']+'", f"font-family: '{nombre}'", txt)
                css.append(txt)

open(os.path.join(dest, 'fuentes.css'), 'w', encoding='utf-8').write('\n'.join(css))
json.dump(pedidas, open(lista, 'w'))
print('Fuentes listas:', ', '.join(pedidas))
