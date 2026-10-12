# Juan Camilo Caicedo · Portafolios

Dos webs de portafolio construidas con el material real de Juan Camilo Caicedo (Canva + Google Drive):

| Web | Carpeta | Enfoque | Puerto local |
| --- | --- | --- | --- |
| **Editor de video** | `apps/editor` | Solo video: showreel, motion graphics, edición, reels | 3001 |
| **Diseñador digital y audiovisual** | `apps/disenador` | Piezas gráficas, campañas con IA, redes y video | 3002 |

Las dos comparten la misma identidad visual ("Corte final": negro, blanco y rojo; Poppins + Playfair Display Italic), los mismos componentes y un único archivo de datos de proyectos.

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
    projects.ts      TODOS los proyectos (tipados) y en qué web aparece cada uno
    profile.ts       nombre, WhatsApp, correo, redes, textos "Sobre mí"
    site-content.ts  hero, filtros, habilidades, herramientas, proceso, métricas
    media.ts         rutas de video/poster y lectura del manifest
    types.ts         tipos Project, Metric, Category, Tool...
  components/        Nav, reproductores, tarjetas, modal, reveals, botones
  sections/          Hero, MotionShowcase, SelectedWorks, About, Skills, Toolkit,
                     Impact, Process, Contact, FeaturedPieces, CaseStudy
  styles/theme.css   tokens de color, tipografía, curvas de animación
media/
  sources.json       inventario completo de Drive (IDs, duración, resolución)
  selection.json     videos curados + cortes del showreel
  out/               videos web, previews, posters, piezas e índice (manifest.json)
scripts/
  media/build_media.py   transcodifica y arma el showreel con ffmpeg
  sync-media.mjs         copia media/out a cada app
docs/AUDITORIA.md
```

## Cómo agregar o editar un proyecto

1. **Video nuevo:** súbelo a la carpeta de Drive y agrega una línea en `media/selection.json`:
   ```json
   { "slug": "mi-video", "driveId": "<id del archivo en Drive>", "posterAt": 0.5, "previewAt": 0.1 }
   ```
   `posterAt` y `previewAt` son fracciones de la duración (0 a 1): de dónde sale el fotograma de portada y dónde empieza la preview de 6 s.
2. Ejecuta `npm run media:build` (descarga el original de Drive si no está en `media/raw/`, genera MP4, preview, poster y actualiza `media/out/manifest.json`).
3. Agrega el proyecto en `packages/core/src/content/projects.ts` copiando una entrada existente:
   ```ts
   {
     slug: "mi-proyecto",
     title: "Título",
     client: "Cliente",            // solo si es real
     categories: ["Video Editing", "Reels & Short Form"],
     description: "Qué es y qué se hizo.",
     media: { kind: "video", video: "mi-video" },
     role: "Edición y motion graphics",
     tools: ["After Effects", "Premiere Pro"], // solo si están verificadas
     priority: 30,                 // menor número = más arriba
     sites: ["editor", "disenador"],
     source: "Drive: ...",
     caseStudy: { objective: "...", process: ["...", "..."] }, // opcional
   }
   ```
   Para piezas gráficas usa `media: { kind: "images", images: [img("archivo", "texto alternativo")] }` con imágenes `.webp` en `media/out/pieces/` (y su tamaño en `media/out/pieces.json`).
4. Para que un proyecto aparezca en la sección destacada, agrega su `slug` a `motionProjects` (o `featuredTiles` en diseñador) en `apps/<web>/app/site.tsx`.

**Métricas:** edita `reelMetrics` y `campaignMetrics` en `site-content.ts`. Para atar métricas a un proyecto concreto usa el campo `metrics` del proyecto; se muestran en su caso de estudio.

**Redes sociales:** agrega `{ label: "Instagram", href: "https://..." }` en `profile.socials`; aparecen en el footer y en los datos estructurados.

**Showreel:** los cortes están en `media/selection.json > showreel.segments` (video, segundo de inicio, duración). Borra `media/out/videos/showreel.*` y ejecuta `npm run media:build`.

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

**Vercel (recomendado):** crea dos proyectos desde el mismo repositorio.
- Proyecto 1: *Root Directory* `apps/editor`.
- Proyecto 2: *Root Directory* `apps/disenador`.
- Framework Next.js, comando por defecto (`npm run build`). Deja activada la opción de incluir archivos fuera del Root Directory (necesita `packages/` y `media/`).
- Define `NEXT_PUBLIC_SITE_URL` y `NEXT_PUBLIC_OTHER_SITE_URL` en cada proyecto y asigna los dominios.

**Netlify / Cloudflare Pages / cualquier hosting estático:** ejecuta `npm run build` y publica `apps/editor/out` y `apps/disenador/out`.

**Videos en producción:** los videos pesan unos 100 MB por web. Funcionan servidos desde el propio hosting, pero para mejor velocidad y para no depender de los límites del plan, súbelos a un almacenamiento con CDN (Cloudflare R2, Bunny, S3 + CloudFront) y define `NEXT_PUBLIC_MEDIA_BASE`.

## Video

- Cada clip tiene `videos/<slug>.mp4` (H.264, máx. 1280 px), `previews/<slug>.mp4` + `.webm` (6 s sin audio para hover) y `posters/<slug>.webp`.
- Las tarjetas muestran el poster y solo descargan la preview al pasar el cursor; nunca suenan dos videos a la vez.
- Los videos completos solo se descargan al abrir el reproductor (`preload` mínimo).
- El showreel del hero es un montaje real de 12 cortes de los proyectos (33 s), con autoplay silenciado, loop y controles de pausa y sonido.
- `python3 scripts/media/build_media.py --raw media/raw --webm-full` genera además versiones WebM completas para navegadores sin H.264 (duplica el peso; no hacen falta en Chrome, Safari, Edge ni Firefox).

## Pruebas realizadas

Con Playwright (Chromium) sobre el build de producción de las dos webs:

| Prueba | Resultado |
| --- | --- |
| Desktop 1440, tablet 820, móvil 390 (más 1024 y 1280 para el nav) | Sin scroll horizontal; nav en una línea; capturas revisadas y corregidas |
| Showreel del hero | Autoplay silenciado, play/pausa y sonido funcionan |
| Previews al pasar el cursor | Se cargan bajo demanda y se reproducen |
| Modal de video | Abre, reproduce, foco en "Cerrar", flechas cambian de video, Esc cierra y devuelve el foco |
| Filtros de Selected Works | Todos 26, Video Editing 8, vuelve a 26; `aria-pressed` correcto |
| Casos de estudio | 26 + 21 páginas estáticas, video o galería, anterior/siguiente |
| WhatsApp | `https://wa.me/573187227063?text=...` con el mensaje codificado; botón flotante en móvil y tablet |
| Títulos y reveals | Ningún título queda oculto tras recorrer la página |
| Imágenes | Ninguna rota |
| Open Graph | `/og.png` 1200×630 generado en el build |
| Detector de Impeccable | Sin antipatrones estructurales; contraste corregido (ver limitaciones) |

Nota: el Chromium de pruebas no incluye el códec H.264, así que la reproducción se verificó con las versiones WebM. Los navegadores reales usan el MP4.

## Limitaciones pendientes

- **Material que no está en Drive:** los videos de Beleza, los reels y el video de YouTube de María Elena Badillo, y tres videos de Ryhar existen solo dentro del Canva 2. Súbelos a Drive y agrégalos con los pasos de arriba.
- **Métricas:** los reels de 207.283 y 259.373 visualizaciones se muestran sin asociarlos a un video, como pediste. Si me dices cuáles son, se enlazan a su proyecto. Los montos de pauta no se publican porque la moneda no aparece en las capturas.
- **Redes sociales:** no había URLs en las fuentes; el footer no muestra redes hasta que las agregues.
- **Contraste del rojo:** `#E50914` sobre `#080808` da 4,2:1. Se usa solo en titulares grandes, numeración y elementos gráficos (cumple AA para texto grande), nunca en texto de cuerpo.
- **Dominio:** define `NEXT_PUBLIC_SITE_URL` al publicar para que canonical, sitemap y Open Graph usen tu dominio.
