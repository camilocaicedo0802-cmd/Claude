# Juan Camilo Caicedo · Portafolio

Portafolio de **editor de video y diseñador digital** construido con el material real de Juan Camilo Caicedo (Canva + Google Drive). La edición de video es el trabajo principal; el diseño, el contenido con IA y la pauta lo acompañan.

| Web | Carpeta | Contenido | Puerto local |
| --- | --- | --- | --- |
| **Portafolio** | `apps/disenador` | Todos los videos y piezas, la sección de landing pages y el perfil | 3002 |

La antigua web de editor de video (`apps/editor`) se unió a esta: su dirección en GitHub Pages ahora redirige al portafolio.

El monorepo incluye además **LIFE OS** (`apps/life-os`, puerto 3003): una aplicación personal de finanzas, clientes y agenda con datos locales en el navegador. Instrucciones y modelo de datos en [`apps/life-os/README.md`](apps/life-os/README.md).

Identidad visual "Corte final": negro, blanco y rojo; Poppins + Playfair Display Italic. Todos los textos están en español; se mantienen en inglés los términos del oficio (motion graphics, reels, UGC, Shorts, hook).

**Orden de los proyectos:** 01 Motion Graphics · 02 Ediciones destacadas · 03 Grow Marketing · 04 Bitácora House · 05 María Elena Badillo · 06 Videos generados con IA · 07 YouTube (Shorts y formato horizontal) · 08 Ryhar · 09 Beleza · 10–20 el resto, en el orden de las carpetas de Drive. Antes de Contacto va la sección **Diseño de landing pages**. El video principal es `promo_editor_motion.mp4`.

- Auditoría de fuentes, inventario y material faltante: [`docs/AUDITORIA.md`](docs/AUDITORIA.md)
- Producto, público y evidencia disponible: [`PRODUCT.md`](PRODUCT.md)
- Dirección visual, tokens, tipografía y motion: [`DESIGN.md`](DESIGN.md)
- Archivo de Figma con variables, estilos y componentes: <https://www.figma.com/design/r7yuPtEhYJmErv5KELN7om>

## Requisitos

- Node.js 20.9 o superior (probado con Node 22).
- Python 3, ffmpeg y poppler (`pdftoppm`), solo si vas a regenerar los medios.

## Instalación y ejecución

```bash
npm install            # instala todo el monorepo
npm run dev:disenador  # http://localhost:3002
```

Antes de arrancar, la app copia `media/out` a su carpeta `public/media` (script `sync-media`).

### Build de producción

```bash
npm run build                      # exporta el portafolio como sitio estático en apps/disenador/out
npm run start -w @jcc/disenador    # lo sirve en :3002
```

## Estructura

```
apps/
  disenador/             Next.js: el portafolio
    app/site.tsx         proyectos, enlaces del menú y secciones
    app/trabajos/[slug]  página de cada proyecto
    app/landings/[slug]  landing page completa
packages/core/src/
  content/
    chapters.ts          los 20 proyectos con sus videos y piezas, en orden
    landings.ts          landing pages (pantallas, textos y rol)
    profile.ts           nombre, WhatsApp, correo, redes, textos "Sobre mí"
    site-content.ts      portada, habilidades, herramientas, proceso, métricas
    media.ts             rutas de video/poster y lectura del manifest
    types.ts             tipos Chapter, VideoItem, Category, Tool...
  components/            Nav, reproductores, tarjetas, visor, reveals, botones
  sections/              Hero, MotionShowcase (proyecto 01), Chapters (trabajos), About,
                         Skills, Toolkit, Impact, Process, LandingShowcase, Contact,
                         ChapterPage, LandingPage
  styles/theme.css       tokens de color, tipografía, curvas de animación
media/
  sources.json           inventario de Drive (IDs, duración, resolución)
  selection.json         cada video y pieza con su ID de Drive
  out/                   videos web, previews, posters, piezas (2 tamaños), manifest.json y pieces.json
scripts/
  media/build_media.py   transcodifica videos, marca de agua, piezas y páginas de PDF
  sync-media.mjs         copia media/out a la app
  relative-export.mjs    deja el export listo para cualquier subcarpeta
  root-redirect.mjs      redirige la raíz de GitHub Pages (la antigua web de editor) al portafolio
docs/AUDITORIA.md
```

## Cómo agregar o editar contenido

Todo el contenido está en `packages/core/src/content/chapters.ts`. Cada proyecto tiene un `number` que define su posición (1 = lo más importante); en cada proyecto se muestran primero los videos y después las piezas.

1. **Archivo nuevo:** súbelo a Drive y agrégalo en `media/selection.json`:
   ```json
   { "slug": "mi-video", "driveId": "<id del archivo en Drive>", "posterAt": 0.5, "previewAt": 0.1 }
   ```
   (en `videos`) o
   ```json
   { "file": "mi-pieza", "driveId": "<id del archivo en Drive>" }
   ```
   (en `pieces`). `posterAt` y `previewAt` son fracciones de la duración (0 a 1): de dónde sale el fotograma de portada y dónde empieza la preview de 6 s.
   - `"watermark": "br"` o `"tr"` graba "Juan Caicedo" (blanco al 60 %) en la esquina inferior o superior derecha del video, la preview y la portada. Se usa en todo el contenido de YouTube: abajo en los horizontales, arriba en los Shorts.
   - En una pieza, `"page": 3` toma esa página de un PDF (workbooks, banners, landing pages).
2. Ejecuta `npm run media:build`: descarga el original de Drive si no está en `media/raw/`, genera MP4, preview, poster y piezas WebP, y actualiza `manifest.json` y `pieces.json`. Los videos de más de 40 s se exportan a 540×960 (o 960×540) para que ningún archivo pase de ~12 MB; los marcados con `"quality": "high"` se mantienen en 720×1280. Un campo `"encode"` cambia la exportación de un video puntual (lo usa el episodio de YouTube de 38 min: 640 px, audio mono, ~53 MB).
3. Agrégalo al proyecto en `chapters.ts`:
   ```ts
   video("mi-video", "Título visible", "Descripción opcional"),
   piece("mi-pieza", "Título visible", "Texto alternativo que describe la imagen"),
   ```
   El cuarto argumento de `video()` acepta opciones:
   - `{ group: "Shorts" }`: el video va en un carrusel propio con ese título dentro del proyecto (así se separan Shorts y formato horizontal en YouTube).
   - `{ excerptOf: 1130 }`: el archivo es un fragmento de un video de 1130 s; la tarjeta dice "Fragmento" y el visor muestra la duración completa. Los videos horizontales de YouTube se publican como fragmentos de 90 s para no pasar el límite de 1 GB de GitHub Pages.
   - `{ longForm: { platform: "YouTube" } }`: video largo en un bloque propio debajo del carrusel.

   Para un proyecto nuevo copia uno existente y dale el `number` de su posición; si va entre dos, suma 1 al `number` de los que quedan después y mueve el bloque en la lista.

**Landing pages:** agrega una entrada en `packages/core/src/content/landings.ts` con sus pantallas (piezas con `"page"` en `selection.json`). Aparece en la sección "Diseño de landing pages" con vista previa en un celular, un botón a la landing completa (`landing-<slug>.html`) y otro a WhatsApp.

**Métricas:** edita `reelMetrics` y `campaignMetrics` en `site-content.ts`.

**Redes sociales:** agrega `{ label: "Instagram", href: "https://..." }` en `profile.socials`; aparecen en el footer y en los datos estructurados.

## Variables de entorno

Todas son opcionales (por ejemplo en Vercel o en `apps/disenador/.env.local`):

| Variable | Para qué |
| --- | --- |
| `NEXT_PUBLIC_SITE_URL` | Dominio final (ej. `https://portafolio.tudominio.com`). Se usa en canonical, sitemap y Open Graph. Sin ella, las URLs absolutas apuntan a `localhost`. |
| `NEXT_PUBLIC_MEDIA_BASE` | URL de un CDN con el contenido de `media/out` (ej. `https://media.tudominio.com`). Si existe, los videos se sirven desde ahí y no se copian a `public/`. |

No hay analítica configurada: no se agregó ningún servicio de terceros sin tu autorización.

## Publicación

Es un sitio estático (`output: "export"`), así que funciona en cualquier hosting estático.

**GitHub Pages (configurado):** el flujo `.github/workflows/pages.yml` construye el portafolio en modo relativo y lo publica cada vez que se actualiza `main`:

- Portafolio: `https://camilocaicedo0802-cmd.github.io/Claude/disenador/`
- `https://camilocaicedo0802-cmd.github.io/Claude/` (donde estaba la web de editor) redirige al portafolio, igual que sus antiguas páginas de proyecto `trabajo-<slug>.html`.
- LIFE OS: `https://camilocaicedo0802-cmd.github.io/Claude/life-os/`

Para activarlo, una sola vez: *Settings → Pages → Build and deployment → Source: GitHub Actions*. GitHub Pages admite hasta 1 GB por sitio; revisa el peso de `media/out` antes de agregar videos largos.

**Vercel:** crea un proyecto con *Root Directory* `apps/disenador`, framework Next.js y comando por defecto (`npm run build`). Deja activada la opción de incluir archivos fuera del Root Directory (necesita `packages/` y `media/`) y define `NEXT_PUBLIC_SITE_URL`.

**Netlify / Cloudflare Pages / cualquier hosting estático:** ejecuta `npm run build` y publica `apps/disenador/out`.

**Carpeta portable (cualquier subcarpeta o servidor de archivos):** `npm run build:relative` genera el portafolio con rutas relativas: los proyectos quedan como `trabajo-<slug>.html` y las landings como `landing-<slug>.html` en la raíz, los archivos de Next en `assets/_next/` y los medios en `media/`.

**Videos en producción:** para mejor velocidad y para no depender de los límites del plan, puedes subir `media/out` a un almacenamiento con CDN (Cloudflare R2, Bunny, S3 + CloudFront) y definir `NEXT_PUBLIC_MEDIA_BASE`. Así también se podrían publicar completos los videos horizontales de YouTube.

## Video

- Cada clip tiene `videos/<slug>.mp4` (H.264, máx. 1280 px), `previews/<slug>.mp4` + `.webm` (6 s sin audio para hover) y `posters/<slug>.webp`.
- Las tarjetas muestran el poster y solo descargan la preview al pasar el cursor; nunca suenan dos videos a la vez.
- Los videos completos solo se descargan al abrir el reproductor (`preload` mínimo).
- El video principal (hero) es `promo_editor_motion.mp4`, con autoplay silenciado, loop y controles de pausa y sonido.
- Las piezas se sirven en dos tamaños (`pieces/sm/` de 720 px para tarjetas y `pieces/` de 1600 px para el visor).
- `python3 scripts/media/build_media.py --raw media/raw --webm-full` genera además versiones WebM completas para navegadores sin H.264 (duplica el peso; no hacen falta en Chrome, Safari, Edge ni Firefox).

## Pruebas realizadas

Con Playwright (Chromium) sobre el build relativo, montado como en GitHub Pages:

| Prueba | Resultado |
| --- | --- |
| Móvil 360 y 390, tablet 820 y desktop 1440 | Sin scroll horizontal (medido sin emulación móvil, que lo esconde al alejar la página), sin errores de consola ni peticiones fallidas en las 22 páginas: inicio, 20 proyectos y la landing |
| Orden y textos | Índice 01–20 en el orden pedido; todos los títulos de sección en español; "Editor de video y diseñador digital" en el título, el menú, la portada y Sobre mí |
| Contenido | Los 117 videos y 102 piezas tienen su tarjeta en el inicio, más las 11 pantallas de la landing |
| YouTube | Grupos Shorts (17) y Formato horizontal (10, con la intro del jet primero); 9 fragmentos de 90 s marcados como tales y con la duración completa en el visor; marca de agua "Juan Caicedo" en videos, previews y portadas |
| Medios | La duración de los 60 archivos web nuevos coincide con su original; todos tienen audio salvo el cierre animado del retiro, que no lo tiene en el original |
| Landing | Vista previa con scroll dentro del celular, botón a `landing-almohadilla-termica.html` y botón de WhatsApp con mensaje |
| Redirecciones | La raíz y una antigua página de proyecto de la web de editor (`trabajo-ryhar.html`) llevan al portafolio |
| Peso | 665 MB publicados, por debajo del límite de 1 GB de GitHub Pages |

Nota: el Chromium de pruebas no incluye el códec H.264, así que no se probó la reproducción con sonido. Los navegadores reales usan el MP4.

## Limitaciones pendientes

- **Videos horizontales de YouTube:** se publican fragmentos de 90 s (sin enlace al video completo, porque los canales no se pueden mencionar). Para publicarlos completos hace falta un almacenamiento externo (ver *Videos en producción*).
- **Métricas:** los reels de 207.283 y 259.373 visualizaciones se muestran sin asociarlos a un video. Los montos de pauta no se publican porque la moneda no aparece en las capturas. Los proyectos nuevos no tienen métricas.
- **Redes sociales:** no había URLs en las fuentes; el footer no muestra redes hasta que las agregues.
- **Contraste del rojo:** `#E50914` sobre `#080808` da 4,2:1. Se usa en titulares grandes, numeración y elementos gráficos (cumple AA para texto grande), nunca en texto de cuerpo. Por decisión de diseño también va en el cargo junto al nombre (menú y footer), un texto pequeño que queda algo por debajo del 4,5:1 que pide AA.
- **Dominio:** define `NEXT_PUBLIC_SITE_URL` al publicar para que canonical, sitemap y Open Graph usen tu dominio.
