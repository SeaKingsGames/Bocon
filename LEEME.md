# Bocón Estudio: versión para instalar

Es la misma app, pero empacada para instalarse como programa en Windows, Mac, Chromebook o Android.
Una vez instalada abre en su propia ventana, aparece en el menú Inicio y funciona sin internet.
Además, aquí sí se puede usar el micrófono: para **grabar voces** y para el **modo en vivo**.

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

## Modo en vivo con OBS

1. En Bocón Estudio toca **En vivo** (arriba a la derecha) y da permiso al micrófono.
2. Elige el personaje y el fondo verde (o azul o magenta).
3. En OBS: **Fuente → Captura de ventana** → elige la ventana de Bocón Estudio.
4. Clic derecho en la fuente → **Filtros → Chroma key** → mismo color del fondo.
5. Mientras transmites: teclas **1–7** para gestos y **Q W E R T Y U I O** para poses (saludar, señalar, festejar…).
   Arrastra al personaje para moverlo y usa la rueda del mouse para el tamaño. **H** oculta la ayuda.

Si la boca se mueve con ruido de fondo, sube "Ignorar ruido". Si casi no se mueve, sube "Sensibilidad".

## Qué cambia frente a la versión dentro de Claude

- Puedes grabar voces con el micrófono y usar el modo en vivo.
- Los videos y proyectos se descargan directo a tu carpeta de Descargas.
- Tu proyecto y tu biblioteca de personajes se guardan solos dentro de la app instalada.
- Para pasar un proyecto a otra compu: **Archivo → Guardar proyecto en archivo**, y en la otra → **Abrir proyecto…**

## Archivos

- `index.html`: la app completa (incluye gifenc, MIT, para los GIF)
- `sw.js`: hace que funcione sin internet
- `manifest.webmanifest` e `icons/`: nombre e ícono del programa
- `vendor/mp4-muxer.js`: arma el archivo MP4 del render rápido (licencia MIT)
- `vercel.json`: evita que Vercel guarde versiones viejas de la app
