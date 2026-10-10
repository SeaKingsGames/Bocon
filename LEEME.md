# Bocón Estudio: versión para instalar

Es la misma app, pero empacada para instalarse como programa en Windows, Mac, Chromebook o Android.
Una vez instalada abre en su propia ventana, aparece en el menú Inicio y funciona sin internet.

## Opción 1: Vercel (recomendada)

1. Sube esta carpeta a un repositorio nuevo de GitHub (por ejemplo `bocon-estudio`).
2. En vercel.com → Add New → Project → importa ese repositorio. No necesita configuración: es una página estática.
3. Abre la dirección que te da Vercel en Chrome o Edge.
4. En la barra de direcciones aparece el ícono de instalar (una pantallita con flecha) → **Instalar Bocón Estudio**.

Cuando subas cambios a GitHub, la app instalada se actualiza sola la siguiente vez que la abras con internet.

## Opción 2: solo en tu compu, sin subir nada

En esta carpeta, abre una terminal y escribe:

    npx serve .

Abre `http://localhost:3000` en Chrome o Edge e instálala con el mismo ícono.
Después de instalarla ya no necesitas tener la terminal abierta.

## Qué cambia frente a la versión dentro de Claude

- Los videos y proyectos se descargan directo a tu carpeta de Descargas.
- Tu proyecto se guarda solo dentro de la app instalada.
- Para pasar un proyecto a otra compu: menú ⋯ → **Guardar proyecto en archivo**, y en la otra → **Abrir proyecto…**

## Archivos

- `index.html`: la app completa
- `sw.js`: hace que funcione sin internet
- `manifest.webmanifest` e `icons/`: nombre e ícono del programa
- `vendor/mp4-muxer.js`: arma el archivo MP4 del render rápido (licencia MIT)
- `vercel.json`: evita que Vercel guarde versiones viejas de la app
