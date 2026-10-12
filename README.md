# Juan Camilo Caicedo · Portafolios

Dos webs de portafolio construidas con el material real de Juan Camilo Caicedo (Canva + Google Drive):

| Web | Carpeta | Enfoque | Puerto local |
| --- | --- | --- | --- |
| **Editor de video** | `apps/editor` | Solo los videos de cada carpeta | 3001 |
| **Diseñador digital y audiovisual** | `apps/disenador` | Todas las piezas y todos los videos | 3002 |

Las dos comparten la misma identidad visual ("Corte final": negro, blanco y rojo; Poppins + Playfair Display Italic), los mismos componentes y un único archivo de contenido.

El contenido sigue las carpetas numeradas de Drive *Videos y Piezas para portafolio*: cada carpeta es un **capítulo** y su número es su importancia (01 Motion Graphics, 02 María Elena Badillo, 03 Ryhar… 15 Otros proyectos). El video principal de las dos webs es `promo_editor_motion.mp4`.

- Auditoría de fuentes, inventario y material faltante: [`docs/AUDITORIA.md`](docs/AUDITORIA.md)
- Producto, público y evidencia disponible: [`PRODUCT.md`](PRODUCT.md)
- Dirección visual, tokens, tipografía y motion: [`DESIGN.md`](DESIGN.md)
- Archivo de Figma con variables, estilos y componentes: <https://www.figma.com/design/r7yuPtEhYJmErv5KELN7om>

## Requisitos

- Node.js 20.9 o superior (probado con Node 22).
- Python 3 y ffmpeg, solo si vas a regenerar los videos.

## Instalación y ejecución

```bash
npm install            # instala todo el monorepo
npm run dev:editor     # http://localhost:3001
npm run dev:disenador  # http://localhost:3002
```

Antes de arrancar, cada app copia `media/out` a su carpeta `public/media` (script `sync-media`).

### Build de producción

```bash
npm run build          # exporta las dos webs como sitios estáticos
# resultado: apps/editor/out y apps/disenador/out
npm run start -w @jcc/editor      # sirve apps/editor/out en :3001
npm run start -w @jcc/disenador   # sirve apps/disenador/out en :3002
```

## Estructura

```
apps/
  editor/            Next.js: web de editor de video
    app/site.tsx     qué proyectos, enlaces y secciones usa esta web
  disenador/         Next.js: web de diseñador digital y audiovisual
packages/core/src/
  content/
    chapters.ts      los 15 capítulos (carpetas) con sus videos y piezas, en orden
    profile.ts       nombre, WhatsApp, correo, redes, textos "Sobre mí"
    site-content.ts  hero, filtros, habilidades, herramientas, proceso, métricas
    media.ts         rutas de video/poster y lectura del manifest
    types.ts         tipos Project, Metric, Category, Tool...
  components/        Nav, reproductores, tarjetas, modal, reveals, botones
  sections/          Hero, MotionShowcase (capítulo 01), Chapters (trabajos), About,
                     Skills, Toolkit, Impact, Process, Contact, ChapterPage
  styles/theme.css   tokens de color, tipografía, curvas de animación
media/
  sources.json       inventario completo de Drive (IDs, duración, resolución)
  selection.json     cada video y pieza con su ID de Drive
  out/               videos web, previews, posters, piezas (2 tamaños), manifest.json y pieces.json
scripts/
  media/build_media.py   transcodifica videos y convierte piezas con ffmpeg
  sync-media.mjs         copia media/out a cada app
docs/AUDITORIA.md
```

## Cómo agregar o editar contenido

Todo el contenido está en `packages/core/src/content/chapters.ts`. Cada capítulo es una carpeta de Drive y su campo `number` define el orden (1 = lo más importante). La web de editor muestra solo los videos de cada capítulo; la de diseñador muestra videos y piezas.

1. **Archivo nuevo:** súbelo a la carpeta de Drive y agrégalo en `media/selection.json`:
   ```json
   { "slug": "mi-video", "driveId": "<id del archivo en Drive>", "posterAt": 0.5, "previewAt": 0.1 }
   ```
   (en `videos`) o
   ```json
   { "file": "mi-pieza", "driveId": "<id del archivo en Drive>" }
   ```
   (en `pieces`). `posterAt` y `previewAt` son fracciones de la duración (0 a 1): de dónde sale el fotograma de portada y dónde empieza la preview de 6 s.
2. Ejecuta `npm run media:build`: descarga el original de Drive si no está en `media/raw/`, genera MP4, preview, poster y piezas WebP, y actualiza `manifest.json` y `pieces.json`. Los videos de más de 40 s se exportan a 540×960 para que ningún archivo pase de ~12 MB; los marcados con `"quality": "high"` se mantienen en 720×1280.
3. Agrégalo al capítulo en `chapters.ts`:
   ```ts
   video("mi-video", "Título visible"),
   piece("mi-pieza", "Título visible", "Texto alternativo que describe la imagen"),
   ```
   Para un capítulo nuevo copia uno existente y dale el `number` de su carpeta.

**Métricas:** edita `reelMetrics` y `campaignMetrics` en `site-content.ts`.

**Redes sociales:** agrega `{ label: "Instagram", href: "https://..." }` en `profile.socials`; aparecen en el footer y en los datos estructurados.

## Variables de entorno

Todas son opcionales y se definen por app (por ejemplo en Vercel o en `apps/editor/.env.local`):

| Variable | Para qué |
| --- | --- |
| `NEXT_PUBLIC_SITE_URL` | Dominio final (ej. `https://editor.tudominio.com`). Se usa en canonical, sitemap y Open Graph. Sin ella, las URLs absolutas apuntan a `localhost`. |
| `NEXT_PUBLIC_OTHER_SITE_URL` | URL de la otra web; si existe, el footer enlaza entre las dos. |
| `NEXT_PUBLIC_MEDIA_BASE` | URL de un CDN con el contenido de `media/out` (ej. `https://media.tudominio.com`). Si existe, los videos se sirven desde ahí y no se copian a `public/`. |

No hay analítica configurada: no se agregó ningún servicio de terceros sin tu autorización.

## Publicación

Son sitios estáticos (`output: "export"`), así que funcionan en cualquier hosting estático.

**GitHub Pages (configurado):** el flujo `.github/workflows/pages.yml` construye las dos webs en modo relativo y las publica cada vez que se actualiza `main`:

- Editor de video: `https://camilocaicedo0802-cmd.github.io/Claude/`
- Diseñador: `https://camilocaicedo0802-cmd.github.io/Claude/disenador/`

Para activarlo, una sola vez: *Settings → Pages → Build and deployment → Source: GitHub Actions*. Si el primer intento corrió antes de activarlo, vuelve a ejecutarlo desde *Actions → Publicar en GitHub Pages → Run workflow*. El flujo define `NEXT_PUBLIC_SITE_URL` y `NEXT_PUBLIC_OTHER_SITE_URL` solo, así que canonical, sitemap, Open Graph y los enlaces entre las dos webs apuntan a esas direcciones.

**Vercel (recomendado):** crea dos proyectos desde el mismo repositorio.
- Proyecto 1: *Root Directory* `apps/editor`.
- Proyecto 2: *Root Directory* `apps/disenador`.
- Framework Next.js, comando por defecto (`npm run build`). Deja activada la opción de incluir archivos fuera del Root Directory (necesita `packages/` y `media/`).
- Define `NEXT_PUBLIC_SITE_URL` y `NEXT_PUBLIC_OTHER_SITE_URL` en cada proyecto y asigna los dominios.

**Netlify / Cloudflare Pages / cualquier hosting estático:** ejecuta `npm run build` y publica `apps/editor/out` y `apps/disenador/out`.

**Carpeta portable (cualquier subcarpeta o servidor de archivos):** `npm run build:relative` genera las dos webs con rutas relativas: los casos de estudio quedan como `trabajo-<slug>.html` en la raíz, los archivos de Next en `assets/_next/` y los medios en `media/`. Esa carpeta `out` funciona aunque se suba dentro de otra ruta (por ejemplo `https://usuario.github.io/repo/`), sin configurar `basePath`. Es la versión publicada como páginas de claude.ai.

**Videos en producción:** los videos pesan unos 100 MB por web. Funcionan servidos desde el propio hosting, pero para mejor velocidad y para no depender de los límites del plan, súbelos a un almacenamiento con CDN (Cloudflare R2, Bunny, S3 + CloudFront) y define `NEXT_PUBLIC_MEDIA_BASE`.

## Video

- Cada clip tiene `videos/<slug>.mp4` (H.264, máx. 1280 px), `previews/<slug>.mp4` + `.webm` (6 s sin audio para hover) y `posters/<slug>.webp`.
- Las tarjetas muestran el poster y solo descargan la preview al pasar el cursor; nunca suenan dos videos a la vez.
- Los videos completos solo se descargan al abrir el reproductor (`preload` mínimo).
- El video principal (hero) de las dos webs es `promo_editor_motion.mp4`, con autoplay silenciado, loop y controles de pausa y sonido.
- Las piezas se sirven en dos tamaños (`pieces/sm/` de 720 px para tarjetas y `pieces/` de 1600 px para el visor).
- `python3 scripts/media/build_media.py --raw media/raw --webm-full` genera además versiones WebM completas para navegadores sin H.264 (duplica el peso; no hacen falta en Chrome, Safari, Edge ni Firefox).

## Pruebas realizadas

Con Playwright (Chromium) sobre el build de producción de las dos webs (segunda entrega):

| Prueba | Resultado |
| --- | --- |
| Móvil 390, tablet 820 y desktop 1440 | Sin scroll horizontal, sin errores de consola, sin peticiones fallidas, ningún título oculto (home y las 10 + 15 páginas de proyecto) |
| Portada | `promo_editor_motion.mp4` en las dos webs; en móvil y tablet el video va centrado y el título y los botones caben en la primera pantalla |
| Contenido | Editor: 39 videos y 0 piezas en 10 capítulos. Diseñador: 39 videos y 83 piezas en 15 capítulos, en el orden de las carpetas |
| Trabajos | Índice fijo de capítulos, carrusel horizontal por capítulo (deslizable en móvil, flechas en desktop) |
| Visor | Abre videos con sonido y piezas a 1600 px; flechas, teclado (← → Esc) y swipe en móvil; enlace al proyecto completo |
| Videos | Duración de cada archivo web comparada con su original: 39 de 39 completos |
| Versión portable (`build:relative`) | Probada dentro de una subcarpeta y envuelta como página de claude.ai: navegación, visor y casos de estudio sin errores |

Nota: el Chromium de pruebas no incluye el códec H.264, así que la reproducción se verificó con las versiones WebM. Los navegadores reales usan el MP4.

## Limitaciones pendientes

- **Métricas:** los reels de 207.283 y 259.373 visualizaciones se muestran sin asociarlos a un video, como pediste. Si me dices cuáles son, se enlazan a su proyecto. Los montos de pauta no se publican porque la moneda no aparece en las capturas.
- **Redes sociales:** no había URLs en las fuentes; el footer no muestra redes hasta que las agregues.
- **Contraste del rojo:** `#E50914` sobre `#080808` da 4,2:1. Se usa solo en titulares grandes, numeración y elementos gráficos (cumple AA para texto grande), nunca en texto de cuerpo.
- **Dominio:** define `NEXT_PUBLIC_SITE_URL` al publicar para que canonical, sitemap y Open Graph usen tu dominio.
