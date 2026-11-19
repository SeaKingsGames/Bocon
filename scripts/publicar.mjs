// Arma la copia que se publica en Vercel (carpeta dist/).
// El código legible se queda en index.html; aquí se comprime y se le cambian los nombres
// a variables y funciones para que copiarlo o modificarlo cueste trabajo.
// Se corre solo en Vercel («npm run build»). Para probarlo en tu compu: npm install && npm run build
import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync, statSync } from 'node:fs';
import { minify } from 'terser';
import { minify as cssMin } from 'csso';

const DIST = 'dist';
const AVISO = 'Bocón Estudio © ' + new Date().getFullYear() + ' SeaKingsStudios. Todos los derechos reservados. Prohibido copiarlo o redistribuirlo. https://www.seakingsstudios.com/terminos-bocon';
const kb = n => (n / 1024).toFixed(0) + ' KB';

const src = readFileSync('index.html', 'utf8');
let html = src;

// 1) JavaScript en línea: comprimir y cambiar nombres (también los de nivel superior)
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if (scripts.length !== 1) throw new Error('Esperaba un solo <script> en línea y hay ' + scripts.length);
const js = scripts[0][1];
const out = await minify(js, {
  ecma: 2020, module: false, toplevel: true,
  compress: { passes: 2, toplevel: true },
  mangle: { toplevel: true },
  format: { comments: false, preamble: '/*! ' + AVISO + ' */' }
});
if (!out.code || out.code.length < js.length * .2) throw new Error('La compresión salió vacía o sospechosa');
html = html.replace(scripts[0][0], () => '<script>' + out.code + '</script>');

// 2) CSS en línea
html = html.replace(/<style>([\s\S]*?)<\/style>/g, (_, css) => '<style>' + cssMin(css, { restructure: false }).css + '</style>');

// 3) HTML: sin comentarios ni sangrías (fuera del script y el estilo, que ya quedaron en una línea)
html = html.replace(/<!--(?!\[)[\s\S]*?-->/g, '').split('\n').map(l => l.trim()).filter(Boolean).join('\n');
html = html.replace(/<html([^>]*)>/, (m) => m + '\n<!-- ' + AVISO + ' -->');

// 4) Carpeta para publicar: solo lo que usa la app (no el esquema, las notas ni el código del servidor)
rmSync(DIST, { recursive: true, force: true }); mkdirSync(DIST);
writeFileSync(DIST + '/index.html', html);
for (const f of ['sw.js', 'manifest.webmanifest', 'icons', 'vendor']) cpSync(f, DIST + '/' + f, { recursive: true });

console.log('index.html:', kb(src.length), '→', kb(html.length), '| JS', kb(js.length), '→', kb(out.code.length));
