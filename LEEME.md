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
1. En supabase.com crea un proyecto (o usa uno que ya tengas).
2. **SQL Editor → New query**: pega el contenido de `supabase/esquema.sql` y dale **Run**. Crea la tabla `suscripciones`.
3. **Authentication → URL Configuration**: en *Site URL* y en *Redirect URLs* pon la dirección de tu app en Vercel (por ejemplo `https://bocon.vercel.app`).
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

Los precios se cambian aquí sin tocar código. Quien ya está suscrito conserva el precio con el que entró.

### Qué es gratis y qué es Pro hoy
- **Gratis:** todo el editor; exporta MP4 720p y GIF con la marquita (en video vertical va arriba a la izquierda para no taparse con los botones de TikTok).
- **Pro:** sin marquita (también en vivo), MP4 en 1080p, GIF sin fondo y cuadros PNG sin fondo.
- Si alguien cancela, ya no se le cobra y sigue con Pro hasta el final de lo que pagó.

## Archivos

- `index.html`: la app completa (incluye gifenc, MIT, para los GIF)
- `sw.js`: hace que funcione sin internet
- `manifest.webmanifest` e `icons/`: nombre e ícono del programa
- `vendor/mp4-muxer.js`: arma el archivo MP4 del render rápido (licencia MIT)
- `vercel.json`: evita que Vercel guarde versiones viejas de la app
- `vendor/supabase.js`: cuentas con Supabase (licencia MIT); solo se carga si activas Bocón Pro
- `api/`: el servidor de cuentas y cobros (funciones de Vercel): `config`, `suscribir`, `estado`, `cancelar` y `mp-webhook`
- `supabase/esquema.sql`: la tabla de suscripciones para Supabase
