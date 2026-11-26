"""Abre Bocón Estudio sin ventana (Playwright + Chrome) y lo maneja con las funciones de la propia app.

    from bocon import Bocon
    with Bocon() as b:
        b.nuevo('9:16')
        ch = b.marioneta('ajolote')            # o la ruta de un .marioneta.json
        b.voz(ch, 'voz.mp3')
        b.subtitulos(ch, 'voz.palabras.json')  # sale de transcribir.py
        b.musica(estilo='alegre')              # al final: dura lo que dure el video
        b.cuadros([1, 3, 5], 'cuadros/')
        b.exportar('video.mp4')

Para lo que no tenga atajo: b.js("...código de la app...", arg). Ver LEEME.md de esta carpeta."""
import base64, json, mimetypes, os, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
REPO = os.path.abspath(os.path.join(AQUI, '..', '..'))
CACHE = os.environ.get('BOCON_CACHE', os.path.expanduser('~/.cache/bocon-video'))
MARIONETAS = ('ajolote', 'gato', 'robot', 'calavera')


class Bocon:
    def __init__(self, raiz=REPO, puerto=8765, chrome='/usr/bin/google-chrome', esperar=None):
        self.raiz, self.puerto, self.chrome = raiz, puerto, chrome
        self.origen = f'http://localhost:{puerto}'
        # esperar a que se quite el letrero de «Abriendo tu proyecto…»: antes de eso el ejemplo todavía puede cambiar S.format
        self.esperar = esperar or ("typeof S!=='undefined' && S.scenes && S.scenes.length>0 && "
                                   "(!document.getElementById('boot') || document.getElementById('boot').classList.contains('off'))")
        # rutas absolutas al mismo origen de la app: si quedan relativas, el navegador las pide a fonts.googleapis.com y fallan
        self.css = open(os.path.join(CACHE, 'fuentes', 'fuentes.css'), encoding='utf-8').read() \
            .replace('url(/__kit/fuentes/', f'url({self.origen}/__kit/fuentes/')

    # ---------- abrir y cerrar ----------
    def __enter__(self):
        self.pw = sync_playwright().start()
        self.nav = self.pw.chromium.launch(executable_path=self.chrome, args=['--autoplay-policy=no-user-gesture-required'])
        self.ctx = self.nav.new_context(viewport={'width': 1280, 'height': 860}, accept_downloads=True, service_workers='block')
        self.ctx.route('**/*', self._ruta)
        self.page = self.ctx.new_page()
        self.errores = []
        self.page.on('pageerror', lambda e: self.errores.append(str(e)))
        self.page.goto(self.origen + '/index.html')
        self.page.wait_for_function(self.esperar, timeout=90000)
        return self

    def __exit__(self, *a):
        self.nav.close(); self.pw.stop()

    def _ruta(self, route):
        url = route.request.url
        if url.startswith('https://fonts.googleapis.com/'):
            return route.fulfill(status=200, content_type='text/css', body=self.css)
        if not url.startswith(self.origen):
            return route.abort()  # nada de internet: api/config da 404 → modo dev, todo Pro y sin marquita
        ruta = url[len(self.origen):].split('?')[0].split('#')[0]
        if ruta.startswith('/__kit/fuentes/'):
            f = os.path.join(CACHE, 'fuentes', os.path.basename(ruta))
        else:
            f = os.path.join(self.raiz, (ruta.lstrip('/') or 'index.html'))
        f = os.path.normpath(f)
        if os.path.isfile(f) and not ruta.startswith('/api/'):
            tipo = mimetypes.guess_type(f)[0] or 'application/octet-stream'
            return route.fulfill(status=200, content_type=tipo, body=open(f, 'rb').read())
        return route.fulfill(status=404, body='no')

    # ---------- básico ----------
    def js(self, codigo, arg=None):
        """Corre código de la app. Si el código no empieza con 'async' ni '(', se envuelve en una función async."""
        c = codigo.strip()
        if not (c.startswith('async') or c.startswith('(') or c.startswith('function')):
            c = 'async (arg)=>{' + c + '}'
        return self.page.evaluate(c, arg)

    def nuevo(self, formato='9:16'):
        self.js("buildBlank(); cur().chars=[]; S.format=arg; refreshAll();", formato)

    def dur(self):
        return self.js("return movieDur();")

    # ---------- personajes y audio ----------
    def marioneta(self, fuente='ajolote', x=.5, y=None, escala=None, nombre=None):
        """Agrega una marioneta: una de las 4 de la app (ajolote, gato, robot, calavera) o un .marioneta.json.
        Regresa el id del personaje."""
        if fuente in MARIONETAS:
            return self.js("""const o=arg,ch=newChar(o.k);ch.x=o.x;ch.y=o.y==null?.58:o.y;ch.scale=o.s==null?1.9:o.s;
              if(o.n) ch.name=o.n;cur().chars.push(ch);refreshAll();return ch.id;""",
                           {'k': fuente, 'x': x, 'y': y, 's': escala, 'n': nombre})
        datos = json.load(open(fuente, encoding='utf-8'))
        # al importar, la app reacomoda a los que ya estaban: se les regresa su lugar
        return self.js("""const o=arg,antes=cur().chars.map(c=>[c,c.x,c.y,c.scale]);await importPuppetData(o.d);
              for(const [c,x,y,s] of antes){c.x=x;c.y=y;c.scale=s;}const cs=cur().chars,ch=cs[cs.length-1];
              ch.x=o.x;ch.y=o.y==null?.66:o.y;ch.scale=o.s==null?2:o.s;if(o.n) ch.name=o.n;refreshAll();return ch.id;""",
                       {'d': datos, 'x': x, 'y': y, 's': escala, 'n': nombre})

    def _audio(self, ruta, nombre=None):
        b64 = base64.b64encode(open(ruta, 'rb').read()).decode()
        return self.js("""const o=arg,bin=atob(o.b),bytes=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
            const buf=await decode(bytes.buffer.slice(0));const id=regAudio('au'+uid(),{name:o.n,kind:'file',bytes:bytes.buffer,buffer:buf});
            addMedia(id,'aud');return id;""", {'b': b64, 'n': nombre or os.path.basename(ruta)})

    def voz(self, ch, ruta, t=.35):
        """Pone la voz al personaje (lip-sync automático). Regresa {aid, inicio, dur}."""
        aid = self._audio(ruta)
        return self.js("""const o=arg,ch=cur().chars.find(c=>c.id===o.ch),c=addVoiceClip(ch,o.aid,o.t);refreshAll();
            return {aid:o.aid,inicio:c.start,dur:S.audio[o.aid].dur};""", {'ch': ch, 'aid': aid, 't': t})

    def sonido(self, nombre_o_ruta, t, vol=.4):
        """Sonido rápido de Bocón ('pop','caja','error','golpe','whoosh','grillos','clic'…) o un archivo."""
        if os.path.exists(nombre_o_ruta):
            aid = self._audio(nombre_o_ruta)
        else:
            aid = self.js("return qsEnsure(arg);", nombre_o_ruta)
            if not aid: raise ValueError('No existe el sonido rápido ' + nombre_o_ruta)
        return self.js("const o=arg,c=addSfxClip(cur(),null,o.aid,o.t);c.vol=o.v;return c.id;", {'aid': aid, 't': t, 'v': vol})

    def musica(self, ruta=None, estilo='alegre', vol=.22, semilla=1, bpm=None, hasta=None):
        """Música de fondo para toda la escena actual, bajita y bajando sola cuando hablan.
        Sin ruta, la genera con musica.py. Ponla al final, cuando ya está todo lo demás."""
        fin = hasta or self.js("return contentEnd(cur());")
        if ruta is None:
            import numpy as np
            from scipy.io import wavfile
            import musica as gen
            ruta = os.path.join(tempfile.mkdtemp(), f'musica-{estilo}.wav')
            wavfile.write(ruta, gen.SR, (gen.hacer(estilo, fin, bpm, semilla) * 32767).astype(np.int16))
        aid = self._audio(ruta, 'Música de fondo')
        return self.js("""const o=arg,sc=cur();let tr=sc.tracks.find(t=>!t.clips.length);if(!tr){tr=newTrack(sc.tracks.length+1);sc.tracks.push(tr);}
            const c=addSfxClip(sc,tr,o.aid,0);c.vol=o.v;c.duck=true;c.out=Math.min(S.audio[o.aid].dur,o.fin);refreshAll();return c.id;""",
                       {'aid': aid, 'v': vol, 'fin': fin})

    # ---------- subtítulos, fondos e imágenes ----------
    def subtitulos(self, ch, palabras, desfase=.35, estilo='karaoke', color='#ffe14d', y=None, escala=None):
        """Subtítulos palabra por palabra con los tiempos de transcribir.py (desfase = donde empieza la voz)."""
        if isinstance(palabras, str): palabras = json.load(open(palabras, encoding='utf-8'))
        return self.js("""const o=arg,ws=o.w;if(!ws.length) return null;const t0=Math.max(0,ws[0].a+o.d-.04);
            const p=newProp('subs',{name:'Subtítulos',x:.5,y:o.y==null?(S.format==='9:16'?.8:S.format==='1:1'?.84:.86):o.y});
            subsDefaults(p,o.e);p.upper=true;p.hl=o.c;if(o.s) p.scale=o.s;p.text=ws.map(w=>w.w).join(' ');p.t0=t0;p.t1=ws[ws.length-1].b+o.d+.7;p.whole=false;
            p.words=ws.map(w=>({w:w.w,a:Math.round((w.a+o.d-t0)*1000)/1000,b:Math.round((w.b+o.d-t0)*1000)/1000,sp:o.ch,pe:/[.,;:!?…)"»]$/.test(w.w)?1:0,le:0}));
            cur().props.push(p);refreshAll();return p.id;""", {'w': palabras, 'd': desfase, 'e': estilo, 'c': color, 'y': y, 'ch': ch, 's': escala})

    def fondo(self, k_o_ruta):
        """Fondo de Bocón por clave (REC_FONDOS) o una imagen propia."""
        if os.path.exists(k_o_ruta):
            b64 = base64.b64encode(open(k_o_ruta, 'rb').read()).decode()
            return self.js("""const o=arg,r=await fetch('data:'+o.t+';base64,'+o.b),id=await addAsset(await r.blob(),o.n);
                const sc=cur();sc.bg='img';sc.bgImg=id;addMedia(id,'img');refreshAll();return id;""",
                           {'b': b64, 't': mimetypes.guess_type(k_o_ruta)[0] or 'image/png', 'n': os.path.basename(k_o_ruta)})
        return self.js("await useRecFondo(arg);refreshAll();", k_o_ruta)

    def imagen(self, ruta, t0, t1, x=.5, y=.4, escala=1, ent='pop', anim='ninguna', **extra):
        """Imagen propia en escena (PNG/WebP/SVG). Regresa el id de la imagen."""
        b64 = base64.b64encode(open(ruta, 'rb').read()).decode()
        return self.js("""const o=arg,r=await fetch('data:'+o.t+';base64,'+o.b),id=await addAsset(await r.blob(),o.n);addMedia(id,'img');
            const p=newProp('img',Object.assign({aid:id,name:o.n,x:o.x,y:o.y,scale:o.s,t0:o.t0,t1:o.t1,ent:o.e,anim:o.a},o.x2));
            cur().props.push(p);refreshAll();return p.id;""",
                       {'b': b64, 't': mimetypes.guess_type(ruta)[0] or 'image/png', 'n': os.path.basename(ruta),
                        'x': x, 'y': y, 's': escala, 't0': t0, 't1': t1, 'e': ent, 'a': anim, 'x2': extra})

    def texto(self, texto, t0, t1, preset='comic', **extra):
        """Texto en pantalla. El ancho (wrap) crece con la escala: si no se da, se calcula para que quepa en el cuadro."""
        if 'scale' in extra and 'wrap' not in extra:
            extra['wrap'] = round(9 / extra['scale'], 2)
        return self.js("""const o=arg,p=newProp('texto',Object.assign({},TEXT_PRESETS[o.p]||{},{text:o.t,t0:o.t0,t1:o.t1},o.x));
            cur().props.push(p);refreshAll();return p.id;""", {'t': texto, 't0': t0, 't1': t1, 'p': preset, 'x': extra})

    def mover(self, id_, t0, t1, ease='suave', **to):
        """Movimiento de un personaje o imagen hasta to = x, y, s (escala), o (opacidad), r (giro).
        Pasa siempre x, y y s: lo que falte se va al centro y a escala 1."""
        self.js("""const o=arg,sc=cur(),it=sc.chars.find(c=>c.id===o.id)||sc.props.find(p=>p.id===o.id);
            it.moves.push(fixMove({id:'m'+uid(),t0:o.t0,t1:o.t1,ease:o.e,to:o.to}));refreshAll();""",
                {'id': id_, 't0': t0, 't1': t1, 'e': ease, 'to': to})

    def desde_imagen(self, ruta, nombre='Mi personaje'):
        """Marioneta con «Marioneta desde una imagen» (PNG transparente o fondo verde). Regresa el id del personaje.
        La app reacomoda a todos al crearla: acomódalos después."""
        b64 = base64.b64encode(open(ruta, 'rb').read()).decode()
        return self.js("""const o=arg,r=await fetch('data:'+o.t+';base64,'+o.b),f=new File([await r.blob()],o.n+'.'+o.x,{type:o.t});
            await openOneImg(f);$('#oiName').value=o.n;await oiCreate();closeEditor();const cs=cur().chars;return cs[cs.length-1].id;""",
                       {'b': b64, 't': mimetypes.guess_type(ruta)[0] or 'image/png', 'n': nombre, 'x': ruta.rsplit('.', 1)[-1]})

    def dialogo(self, audio, lineas, colores, desfase=.35, y=None):
        """Un audio con varias voces. lineas = [(id_personaje, t_inicio, t_fin, palabras)] en tiempo del audio
        (palabras de transcribir.py que caen en esa línea). Cada línea va como voz del que habla, así solo él mueve
        la boca, y sus subtítulos salen del color de ese personaje (colores = {id: '#hex'})."""
        tmp = tempfile.mkdtemp()
        subs = []
        for i, (ch, t0, t1, ws) in enumerate(lineas):
            clip = os.path.join(tmp, f'linea-{i}.wav')
            args = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{t0:.3f}', '-i', audio] + (['-t', f'{t1 - t0:.3f}'] if t1 else [])
            subprocess.run(args + ['-af', 'afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse', '-ar', '48000', '-ac', '1', clip], check=True)
            self.voz(ch, clip, t=desfase + t0)
            if ws: subs.append([self.subtitulos(ch, ws, desfase=desfase, color=colores.get(ch, '#ffe14d'), y=y), ws[0]['a'] + desfase])
        for (sid, _), (_, sig) in zip(subs, subs[1:]):  # que un subtítulo se quite cuando habla el siguiente
            self.js("const o=arg,p=cur().props.find(q=>q.id===o.id);p.t1=Math.min(p.t1,o.f);refreshAll();", {'id': sid, 'f': sig - .06})

    def catalogo(self):
        """Claves de todo lo que trae Bocón: gestos, poses, acciones, textos, fondos, imágenes y sonidos rápidos."""
        return self.js("""return {gestos:Object.keys(EXPR),poses:Object.keys(POSES),acciones:Object.keys(ACTIONS),
            textos:Object.keys(TEXT_PRESETS),fondos:REC_FONDOS.map(f=>f.k),imagenes:REC_IMGS.map(f=>f.k),sonidos:QS.map(q=>q.k)};""")

    def bloques(self, ch, gestos=(), poses=()):
        """gestos/poses: [(clave, t0, t1), …] — claves de EXPR y POSES/ACTIONS (ver catalogo())."""
        malas = self.js("""const o=arg;return [...o.g.filter(g=>!EXPR[g[0]]).map(g=>'gesto '+g[0]),
            ...o.p.filter(p=>!POSES[p[0]]&&!ACTIONS[p[0]]).map(p=>'pose '+p[0])];""",
                        {'g': [list(x) for x in gestos], 'p': [list(x) for x in poses]})
        if malas: raise ValueError('No existen: ' + ', '.join(malas) + ' (ver b.catalogo())')
        self.js("""const o=arg,ch=cur().chars.find(c=>c.id===o.ch);
            for(const [e,t0,t1] of o.g) ch.exprs.push({id:'e'+uid(),e,t0,t1});
            for(const [p,t0,t1] of o.p) ch.poses.push({id:'q'+uid(),p,t0,t1});refreshAll();""",
                {'ch': ch, 'g': [list(x) for x in gestos], 'p': [list(x) for x in poses]})

    # ---------- revisar y exportar ----------
    def cuadros(self, tiempos, carpeta, ancho=360):
        """Guarda cuadros JPEG del video en esos segundos para revisarlos antes de exportar."""
        os.makedirs(carpeta, exist_ok=True)
        rutas = []
        for t in tiempos:
            url = self.js("""const o=arg;await fontsReady();const [w,h]=EXPORT_SIZE['1080'][S.format],c=document.createElement('canvas');
                c.width=w;c.height=h;drawMovie(c.getContext('2d'),w,h,o.t,{});
                const s=document.createElement('canvas'),k=o.a/w;s.width=o.a;s.height=Math.round(h*k);s.getContext('2d').drawImage(c,0,0,s.width,s.height);
                return s.toDataURL('image/jpeg',.82);""", {'t': t, 'a': ancho})
            r = os.path.join(carpeta, f'cuadro-{t:06.2f}.jpg')
            open(r, 'wb').write(base64.b64decode(url.split(',', 1)[1])); rutas.append(r)
        return rutas

    def hoja(self, tiempos, salida, ancho=270):
        """Todos los cuadros en una sola imagen (más barato de revisar que uno por uno)."""
        rutas = self.cuadros(tiempos, tempfile.mkdtemp(), ancho)
        n = len(rutas); cols = min(n, 5)
        if n == 1:
            subprocess.run(['cp', rutas[0], salida], check=True); return salida
        lay = '|'.join(('+'.join(['w0'] * (i % cols)) or '0') + '_' + ('+'.join(['h0'] * (i // cols)) or '0') for i in range(n))
        filtro = ''.join(f'[{i}:v]' for i in range(n)) + f'xstack=inputs={n}:layout={lay}:fill=black'
        subprocess.run(['ffmpeg', '-v', 'error', '-y'] + sum([['-i', r] for r in rutas], []) +
                       ['-filter_complex', filtro, '-q:v', '3', salida], check=True)
        return salida

    def guardar_proyecto(self, salida):
        with self.page.expect_download(timeout=120000) as d:
            self.js("saveProjectFile();")
        d.value.save_as(salida); return salida

    def exportar(self, salida, res='1080', lufs=-14, tp=-1.5):
        """Exporta con la app y deja el audio en AAC al volumen de TikTok/Reels."""
        crudo = os.path.join(tempfile.mkdtemp(), 'crudo.mp4')
        with self.page.expect_download(timeout=30 * 60 * 1000) as d:
            self.js("runExport({fmt:'mp4',scope:'movie',res:arg});", res)
        d.value.save_as(crudo)
        terminar_audio(crudo, salida, lufs, tp)
        return salida


def terminar_audio(entrada, salida, lufs=-14, tp=-1.5):
    """Audio a AAC con loudnorm de dos pasadas; el video no se vuelve a codificar."""
    med = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', entrada, '-af',
                          f'loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    m = json.loads(med[med.rindex('{'):med.rindex('}') + 1])
    af = (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', entrada, '-c:v', 'copy', '-af', af, '-ar', '48000',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', salida], check=True)
