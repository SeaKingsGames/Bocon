# Bocón Estudio: versión para instalar

Es la misma app, pero empacada para instalarse como programa en Windows, Mac, Chromebook o Android.
Una vez instalada abre en su propia ventana, aparece en el menú Inicio y funciona sin internet.
Además, aquí sí se puede usar el micrófono: para **grabar voces** y para el **modo en vivo**.

## Opción 1: Vercel (recomendada)

1. Sube esta carpeta a un repositorio nuevo de GitHub (por ejemplo `bocon-estudio`).
2. En vercel.com → Add New → Project → importa ese repositorio. No necesita configuración (las cuentas y cobros de Bocón Pro se activan aparte, más abajo).
3. Abre la dirección que te da Vercel en Chrome o Edge.
4. En la barra de direcciones aparece el ícono de instalar (una pantallita con flecha) → **Instalar Bocón Estudio**.

Cuando subas cambios a GitHub, la app instalada se actualiza sola la siguiente vez que la abras con internet.

## Opción 2: solo en tu compu, sin subir nada

En esta carpeta, abre una terminal y escribe:

    npx serve .

Abre `http://localhost:3000` en Chrome o Edge e instálala con el mismo ícono.
Después de instalarla ya no necesitas tener la terminal abierta.

## Cómo se publica (copia compacta)

El código que se edita es `index.html`, legible como siempre. Al publicar, Vercel corre `npm run build` (`scripts/publicar.mjs`),
que arma la carpeta `dist/` con una copia compacta: comprime el código, le cambia los nombres a variables y funciones,
y deja solo lo que usa la app (sin este LEEME, el esquema ni el código del servidor). Eso es lo que se sirve en la dirección de Bocón.
Las funciones de `api/` se publican igual que antes.

- Para probar la copia compacta en tu compu: `npm install`, `npm run build` y `npx serve dist`.
- Para probar el código legible: `npx serve .` como antes.

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

## Bocón Pro: cuentas y cobros con Mercado Pago

Mientras no pongas las variables de abajo, la app funciona como siempre: **todo abierto y sin cuentas**.
En cuanto las pongas, aparece el botón **Entrar / Hazte Pro** y el plan gratis exporta en 720p con la marquita «Hecho con Bocón».

### 1. Supabase (cuentas)
1. Usa un proyecto de Supabase que ya tengas (por ejemplo el de otra de tus apps) o crea uno. El plan gratis solo deja 2 proyectos activos por persona; Bocón cabe en uno compartido porque solo usa las cuentas y una tabla.
2. **SQL Editor → New query**: pega el contenido de `supabase/esquema.sql` y dale **Run**. Crea las tablas `bocon_suscripciones` y `bocon_dibujos` (no toca las tablas de tu otra app). Se puede volver a correr completo sin perder nada; si ya lo habías corrido antes, basta con la parte «Dibujar con IA».
3. **Authentication → URL Configuration**: en *Redirect URLs* agrega la dirección de Bocón en Vercel (por ejemplo `https://bocon.vercel.app/**`). Si el proyecto es solo de Bocón, ponla también en *Site URL*; si lo compartes, deja el *Site URL* de tu otra app.
   - Si lo compartes, las cuentas son las mismas para las dos apps (un solo usuario y contraseña para todo SeaKings) y los correos de inicio de sesión son los mismos: escríbelos de forma general, por ejemplo «Tu código de SeaKings Studios».
4. Recomendado: **Authentication → Emails → Magic Link**, agrega al correo el código `{{ .Token }}`. Así también se puede entrar escribiendo el código (útil si el enlace se abre en otro navegador, como el de Gmail).
5. Para el lanzamiento conecta un servicio de correo propio (**Authentication → SMTP**, por ejemplo Resend): el de Supabase solo manda unos pocos correos por hora.
6. Opcional: para "Entrar con Google" activa el proveedor Google en **Authentication → Providers** y pon `LOGIN_GOOGLE=1` abajo.

### 2. Mercado Pago (cobros)
1. En mercadopago.com.mx/developers → **Tus integraciones → Crear aplicación** (elige Suscripciones).
2. Copia el **Access Token**. Para probar usa primero las *credenciales de prueba* y un *usuario de prueba comprador*; ya que todo funcione, cambia a las de producción.
3. Recomendado: en tu aplicación → **Webhooks**, pon `https://TU-APP.vercel.app/api/mp-webhook` y marca los eventos de **Planes y suscripciones**. Aunque no los configures, la app revisa el estado del pago cada vez que se abre.

### 3. Vercel (variables)
En tu proyecto → **Settings → Environment Variables**, agrega y luego haz **Redeploy**:

| Variable | Qué es |
|---|---|
| `SUPABASE_URL` | Project URL (Supabase → Project Settings → API) |
| `SUPABASE_ANON_KEY` | la llave pública (anon o *publishable*) |
| `SUPABASE_SERVICE_ROLE_KEY` | la llave secreta (service_role o *secret*). **Nunca la pongas en la app** |
| `MP_ACCESS_TOKEN` | el Access Token de Mercado Pago |
| `APP_URL` | la dirección de tu app, por ejemplo `https://bocon.vercel.app` |
| `PRO_PRECIO_MENSUAL` | por ejemplo `79` (pesos) |
| `PRO_PRECIO_ANUAL` | por ejemplo `690` |
| `PRO_FUNDADOR_PRECIO` y `PRO_FUNDADOR_CUPO` | por ejemplo `49` y `100` (déjalas vacías para no tener precio fundador) |
| `PRO_PRUEBA_DIAS` | días gratis la primera vez, por ejemplo `7` (vacío = sin prueba) |
| `PRO_GRATIS` | correos con Pro de regalo, separados por coma (el tuyo, tus testers) |
| `LOGIN_GOOGLE` | `1` si activaste Google en Supabase |
| `GEMINI_API_KEY` | llave de Gemini para «Dibujar con IA» ([Google AI Studio](https://aistudio.google.com) → Get API key; el nivel gratis no pide tarjeta) |
| `DIBUJOS_POR_MES` | dibujos con IA por cuenta Pro al mes (vacío = 30) |
| `DIBUJOS_GRATIS` | dibujos con IA por cuenta gratis al mes (vacío = 10; `0` = solo Pro) |
| `GEMINI_MODELOS` | opcional: modelos a probar en orden, separados por coma (vacío = `gemini-flash-latest,gemini-flash-lite-latest`) |

Los precios se cambian aquí sin tocar código. Quien ya está suscrito conserva el precio con el que entró.

### Dibujar con IA (Trazo)
- Una IA de texto (Gemini) escribe el dibujo como código SVG, siempre en caricatura con contorno grueso, y Bocón lo vuelve estampita con borde blanco.
- Hay que entrar a la cuenta. Gratis: 10 al mes (`DIBUJOS_GRATIS`); Pro: 30 al mes (`DIBUJOS_POR_MES`). El servidor revisa el plan y lleva la cuenta del mes en `bocon_dibujos`; si la IA falla, el dibujo no se cuenta. Se renueva el día 1 (hora de México).
- Los dibujos gratis gastan del mismo tope diario de Gemini que los de Pro. Si algún día se acaba seguido, baja `DIBUJOS_GRATIS` (o ponlo en `0`) antes que quitarle a Pro.
- Con el nivel gratis de Gemini el tope de peticiones es por proyecto de Google y se ve en AI Studio. Si la página de Trazo también usa Gemini, conviene que tenga su propio proyecto de Google para que no se repartan el tope. En el nivel gratis, Google puede usar lo que se manda para mejorar sus productos.

### Qué es gratis y qué es Pro hoy
- **Gratis:** todo el editor; hasta 2 personajes por escena (las bocas sobre fotos no cuentan); la ropa y accesorios básicos; los efectos de voz listos; los recursos de Bocón sin ✦; texto a voz de hasta 200 letras; «Dibujar con IA» con cuenta, 10 al mes; exporta MP4 720p y GIF con la marquita (en video vertical va arriba a la izquierda para no taparse con los botones de TikTok).
- **Pro:** sin marquita (también en vivo), MP4 en 1080p, GIF sin fondo y cuadros PNG sin fondo; personajes sin límite; la ropa y accesorios marcados con ✦; los fondos, imágenes, gestos y acciones de Bocón marcados con ✦; texto a voz sin límite; guardar tus propios efectos de voz; «Dibujar con IA» con más dibujos al mes (30; Imagen → Dibujar con IA: escribes qué quieres y sale una estampita de caricatura).
- Los límites solo se aplican cuando ya hay cuentas (variables puestas en Vercel). Los proyectos y marionetas que ya traen cosas Pro se abren y se ven igual; el candado solo está al agregar algo nuevo.
- Lo que es Pro se cambia en `index.html`: `ACC_PRO` (accesorios), `REC_PRO` (gestos y acciones de Bocón), `pro:1` en `REC_FONDOS` y `REC_IMGS` (fondos e imágenes de Bocón), `FREE_CHARS` (personajes) y `TTS_FREE` (letras de texto a voz).
- Precios recomendados para el lanzamiento: `PRO_PRECIO_MENSUAL=79`, `PRO_PRECIO_ANUAL=690`, `PRO_FUNDADOR_PRECIO=49`, `PRO_FUNDADOR_CUPO=100`, `PRO_PRUEBA_DIAS=7`.
- Si alguien cancela, ya no se le cobra y sigue con Pro hasta el final de lo que pagó.

## Recursos de Bocón

Fondos, imágenes, ropa, gestos, acciones y sonidos que vienen con la app. Salen de los videos que se van haciendo con Bocón.

- **Fondos:** Escena → Fondo → *Fondos de Bocón…* (también en el menú Agregar). Cada fondo trae versión vertical y horizontal y se cambia sola si cambias el formato del video.
- **Imágenes:** *+ Imagen* abre una ventana para subir la tuya o usar una de Bocón.
- **Gestos y acciones:** salen junto a los demás en el panel del personaje.
- **Ropa:** en *Editar personaje → Ropa*, con las demás.
- **Sonidos:** en *Sonidos rápidos*. Los de *Audios virales* (y el teclado y los pasos) son archivos: se bajan la primera vez que los tocas y quedan guardados dentro del proyecto.

| Recurso | Gratis | Pro ✦ |
|---|---|---|
| Fondos | Súper (pasillo), Sala de servidores, Sala de noche, Recámara de noche, Sala de día, Celda de cárcel, Cocina, Casita (cuarto turquesa), Calle de la colonia | Cuarto de madrugada, Tier list, Puerta de la recámara, Mictlán, Estudio de noticias |
| Imágenes (Súper) | Queso en bolsa, Papitas | Carne en plástico, Pan en bolsa, ¡Sin bolsa! |
| Imágenes (Música) | Grabadora (apagada), Grabadora (sonando) | |
| Imágenes (Redes) | Letrero «Link en mi perfil», Like y compartir, Palomita (sí), Tache (no) | Multitud festejando |
| Imágenes (Cosas) | Vela, Control de videojuego, Calendario (ponle la fecha con texto), Mazo de juez | Polilla (no hay nada) |
| Imágenes (Animales) | Huellita | |
| Imágenes (Noticias) | | Escritorio de noticias (va enfrente del personaje) |
| Imágenes (Dibujos) | Garabato: pollo con ansiedad | |
| Imágenes (Día de Muertos) | | Cempasúchil |
| Imágenes (Casa) | | Cama: cabecera, Cama: cobija |
| Imágenes (Juguetes) | Carrito de juguete | Muñeca, Bloques ABC |
| Imágenes (Sustos) | | Fantasma: señora de vestido azul |
| Imágenes (Cárcel) | Charquito de agua, Gota de agua | |
| Imágenes (Cocina) | Cartón de huevos, Cartón de huevos vacío, Plátano, Molcajete | 143 íconos de cocina: utensilios, ollas y sartenes, aparatos (batidoras, licuadoras, cafeteras, arrocera…), frutas, verduras, panes y comidas (PNG en `recursos/imagenes/cocina/`) |
| Estilos de texto | Noticiero (cintillo rojo) | |
| Ropa | Mandil de mamá | Uniforme naranja, Tubos para el pelo |
| Gestos | Harto, Desvelado, Serio (voz de papá), Aliviado, Malvado (mirada que da miedo), Carcajada (muerto de risa), Llorando de risa (XD), Aguantándose la risa | Silencio incómodo, Incrédulo, Sintiendo la canción, Inocente (yo no fui), Apenado (¡qué bruto!) |
| Acciones | Señalar arriba (der. e izq.), Presionar botón, Cabeceando (sueño), ¡Se me olvidó! (manos a la cabeza), Reírse a carcajadas, Aguantarse la risa (mano en la boca) | Explicar (una mano), Explicar (dos manos), ¿Es en serio?, Balancearse con la música, Regañar (dedo), Secarse la frente, Persignarse, ¡Qué bruto! (palmada en la frente), Tirarse al piso (acostado), Risa histérica (dándose en la pierna), Revolcarse de risa (en el piso) |
| Adornos de los gestos | Ojeras | |
| Sonidos rápidos | Clic (botón), Gotera (plip), Reja (barrotes), Palmada, Ba dum tss (chiste), Entrada de noticiero | |
| Sonidos (archivos) | Audios virales: Vine boom, Among Us: impostor, Rizz, Oh yeah, ¡Nooo!, Gato riendo, M-E-O-W, Pollo gritando, Sorpresa, Idea brillante, Homero quejándose, «¿Pero esto qué es?», «Qué difícil me la pusiste, diablo», «Me salí de mi casa a los 26», POV: yéndome a dormir, «El monte Everest…», Push push push. Además: Teclado de compu, Pasos corriendo | |

Para la gotera de la celda: pon el *Charquito* en el piso y una *Gota* que baje del tubo hasta el charquito con un movimiento *Acelerando* de medio segundo; al llegar, el sonido *Gotera (plip)*.

Para meter personajes a la cama: pon la *Cama: cabecera* (se va sola detrás de los personajes), luego los personajes con la cabeza sobre las almohadas y al final la *Cama: cobija*, que los tapa hasta el cuello.

Para agregar uno nuevo:
1. Pon el archivo en `recursos/fondos/` o `recursos/imagenes/` (WebP; los fondos en 1080×1920 y 1920×1080) y su original editable en `recursos-fuentes/`.
2. Agrega su renglón en `REC_FONDOS` o `REC_IMGS` en `index.html` (`pro:1` si es de Pro; `layer:'atras'` si la imagen va detrás de los personajes). Los gestos van en `EXPR` y las acciones en `ACTIONS`; si son de Pro, agrega su nombre a `REC_PRO`. Los adornos de los gestos van en `EMOTES` (y se dibujan en `drawEmotes`) y los sonidos rápidos en `QS`: los que se hacen con código llevan `f`; los grabados van en `recursos/sonidos/` (MP3, sin silencio al principio y al final, a −16 LUFS) y en `QS` llevan `src` y su duración `d`.
3. Si cambias un archivo que ya estaba, cámbiale el nombre: la app instalada se queda con el que ya había descargado.

Los fondos y las imágenes se copian dentro del proyecto al usarlos (igual que las tuyas), así que el proyecto se ve igual aunque después cambie el recurso.

## Archivos

- `index.html`: la app completa (incluye gifenc, MIT, para los GIF)
- `sw.js`: hace que funcione sin internet
- `manifest.webmanifest` e `icons/`: nombre e ícono del programa
- `vendor/mp4-muxer.js`: arma el archivo MP4 del render rápido (licencia MIT)
- `vercel.json`: evita que Vercel guarde versiones viejas de la app
- `vendor/supabase.js`: cuentas con Supabase (licencia MIT); solo se carga si activas Bocón Pro
- `api/`: el servidor de cuentas y cobros (funciones de Vercel): `config`, `suscribir`, `estado`, `cancelar` y `mp-webhook`; `dibujar` y `_trazo.js` son «Dibujar con IA» (el mismo estilo de la página de Trazo)
- `supabase/esquema.sql`: la tabla de suscripciones para Supabase
- `recursos/`: fondos, imágenes y sonidos que vienen con la app (se publican); `recursos-fuentes/`: sus originales en SVG para editarlos (no se publican)
- `herramientas/video/`: kit para hacer videos con Bocón desde la terminal: transcribir, música de fondo, armar y exportar (no se publica; ver su LEEME)
