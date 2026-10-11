---
name: motion-graphics
description: Editor de vídeo con Remotion que copia el FORMATO DE EDICIÓN de un vídeo de referencia adjunto (ritmo de cortes, sistema de subtítulos, tipografías, color, transiciones, movimientos de cámara, tipo de b-roll, motion graphics y capas de sonido) y lo aplica a una voz, metraje o tema nuevo. Mide la referencia con scripts (cortes, OCR de subtítulos, paleta, cámara, separación voz/música) y escribe un estilo.md con valores concretos antes de editar. Úsala siempre que el usuario adjunte o mencione un vídeo de referencia (TikTok, Reel, Short, anuncio, vídeo de YouTube) y pida "hazlo igual", "con este estilo/formato", "edita mi audio/voz/guion como este vídeo", "motion graphics", "subtítulos animados palabra a palabra", "b-roll", "reels con Remotion", o quiera replicar la edición de otro creador, aunque no nombre Remotion ni esta skill. English triggers: reference video, match this edit, recreate editing style, animated captions, voiceover video, faceless video, Remotion video.
---

# Motion Graphics: editar como la referencia

La referencia que adjunta el usuario **es la especificación**. Esta skill no impone un estilo propio: mide cómo está editada la referencia y reproduce esa gramática sobre contenido nuevo. Separa siempre dos cosas:

- **Gramática (se copia):** duración de los planos, densidad de eventos, sistema de subtítulos (cuántas palabras, dónde, cómo entran, qué se destaca), tipografías, paleta, textura, catálogo de transiciones, comportamiento de cámara, tipo de b-roll (fotos recortadas, vídeo de stock, iconos, capturas, 3D…), estructura (gancho, desarrollo, cierre) y capas de audio (voz, música, SFX y su relación de volumen).
- **Contenido (se adapta):** los objetos, imágenes, palabras clave y metáforas visuales salen del tema del audio nuevo. Si la referencia usa una bombilla para «idea», el vídeo nuevo usa el objeto que simbolice *su* concepto, tratado igual que la bombilla.

Si en una referencia algo no se puede medir, se marca como **[SUPOSICIÓN]** y se decide de forma coherente con lo que sí se midió.

## Entradas

| Entrada | Necesaria | Si falta |
|---|---|---|
| Vídeo de referencia | sí | Pídelo. Sin referencia la skill no aplica. |
| Voz / audio con la locución | casi siempre | Si hay guion pero no voz, pregunta si quiere TTS (la skill oficial `remotion-markup/voiceover.md` cubre ElevenLabs) o grabarla. Si solo hay tema, propone guion y pide la voz. |
| Metraje propio (A-roll) | solo si la referencia es persona a cámara, pantalla o producto filmado | Si la referencia depende de un metraje que el usuario no tiene, dilo y propone el sustituto más cercano: fotos recortadas, stock o motion graphics. Pregunta antes de cambiar de formato. |
| Música | opcional | Si pide «la misma música», extráela de la referencia (fase 4). Avisa de que los derechos son los de la pista original. |
| Usuario / handle / CTA | si la referencia cierra con firma | Nunca copies el @ de otro creador: deja `@tu.usuario` y pregúntalo. |

Lo que el usuario pida explícitamente manda sobre la referencia: «añade SFX», «subtítulos más grandes», «que sea más largo». Anota en `estilo.md` cada desviación pedida.

## Flujo de trabajo

Trabaja por fases y no avances sin cerrar la anterior. Hay dos puntos de control en los que el usuario debe ver algo: el resumen de 5 líneas (fin de la fase 2) y el borrador renderizado (fin de la fase 5). Si el usuario pidió explícitamente no detenerse, enseña el resumen y continúa.

### Fase 0: Preparar

```bash
bash <skill>/scripts/setup.sh <proyecto> --width 1080 --height 1920 --fps 30
```

- Comprueba e instala Node, ffmpeg, Whisper, librosa, onnxruntime, RapidOCR y Demucs.
- Crea el proyecto Remotion si no existe, instala `@remotion/{media,captions,paths,fonts}` y las skills oficiales (`npx skills add remotion-dev/skills`), y copia la plantilla de componentes a `src/`.
- Usa las dimensiones y los fps de la referencia salvo que el usuario pida otros (`analyze_reference.py` los informa).
- Lee `references/remotion-tecnico.md` antes de programar. Recoge fallos reales ya resueltos.

### Fase 1: Analizar la referencia (medir, no adivinar)

```bash
python3 <skill>/scripts/analyze_reference.py referencia.mp4 analisis_ref --ocr --separate --whisper small --lang es
```

Genera estos archivos:

- `analisis.md` y `analysis.json`: cortes, planos (duración, cámara, color), ritmo, paleta, grano, viñeta, texto en pantalla por OCR (posición, tamaño, palabras por bloque, forma de aparecer, colores, caja de fondo), audio (LUFS, silencios, tempo, voz frente a música, instantes con SFX, % de cortes sonorizados) y transcripción.
- Hojas de contactos: `contact_planos.jpg` (una miniatura por plano) y `contact_2fps_*.jpg`.

Después **mira** el vídeo, porque los números no lo dicen todo:

1. Abre las hojas de contactos y los fotogramas de `frames_cortes/`. Extrae ráfagas a 10–15 fps de los momentos clave (entradas de texto, transiciones) para ver la animación fotograma a fotograma. Los comandos están en `references/analisis.md`.
2. Recorta cada tipografía e identifícala con `scripts/font_match.py`, que compara contra familias de Google Fonts por categoría. Elige la más parecida y márcala como [SUPOSICIÓN] si no es exacta.
3. **Clasifica el formato** con `references/formatos.md`: editorial/collage de motion graphics, persona a cámara con subtítulos dinámicos, b-roll documental, tipografía cinética, edición rápida con ritmo de música, tutorial de pantalla, clip de pódcast, producto/promo, listado/ranking, carrusel de fotos… Muchas referencias son híbridas: anota las proporciones. Ese archivo dice qué medir con más cuidado y cómo construir cada formato.

### Fase 2: estilo.md y resumen

- Copia `assets/estilo_template.md` a `estilo.md` y rellena **cada** sección con valores concretos (px a escala 1080 de ancho, segundos, hex, dB). No uses adjetivos sin número.
- Incluye la tabla de estructura (bloques y tiempos), el catálogo de transiciones con sus duraciones, los sistemas de subtítulos y las reglas de sonido.
- Marca lo supuesto con [SUPOSICIÓN].
- Enseña un **resumen de 5 líneas**: ritmo, subtítulos, b-roll y gráficos, color y textura, sonido.
- `assets/ejemplo/estilo_ejemplo.md` es un estilo.md real terminado. Úsalo para ver el nivel de detalle, nunca como estilo por defecto.

### Fase 3: Planificar sobre el audio nuevo

1. Transcribe con tiempos por palabra. El script ancla las palabras que siguen a una pausa al inicio real de la voz; Whisper llega 0.1–0.3 s tarde ahí.
   ```bash
   python3 <skill>/scripts/transcribe.py voz.mp3 <proyecto>/src/data --model medium --lang es
   ```
2. **Traslada el ritmo, no los tiempos.** Con la duración del audio nuevo y las métricas de la referencia (mediana de plano, cortes/min, eventos/s, alternancia claro/oscuro), calcula cuántas escenas y cambios hacen falta. Ejemplo: referencia con planos de 2.6 s y audio de 42 s → unas 12–16 escenas, con algo nuevo cada 0.2–0.5 s si la referencia lo hace.
3. Escribe un **storyboard** (tabla en el chat o en `estilo.md`) con:
   - escena, rango de tiempo y fondo;
   - objeto o b-roll y su equivalente en la referencia;
   - palabras destacadas (índices de `captions.ts`);
   - transición de entrada y de salida (solo del catálogo medido);
   - SFX.
4. Coloca los cambios de escena en las **pausas** de la voz; las transiciones caen ahí. Los instantes de las palabras clave mandan sobre los eventos visuales.
5. Haz la lista de recursos: qué fotos buscar, qué dibujar en vectorial y qué metraje hace falta.

### Fase 4: Construir

- **Imágenes.** Busca con `scripts/find_images.py search "<objeto>" cand/<obj>` (Openverse, solo licencias reutilizables), mira la `sheet.png` y descarga con `get`. Recorta con `scripts/cutout.py` (`--mono`, `--tint`, contraste…) según el tratamiento medido.
  - Lo que no exista bien en fotos (UI, móviles, tarjetas, iconos, señales, gráficos de datos) se dibuja en vectorial con la estética de la referencia.
  - Guarda los créditos en `CREDITOS.md`. Detalles en `references/assets-y-licencias.md`.
- **Audio.**
  - Música de la referencia: `scripts/reference_audio.py separate` y después `music --duration <s>`.
  - SFX de la referencia: `reference_audio.py sfx`.
  - SFX propios: `scripts/synth_sfx.py`, más la biblioteca de Remotion (`https://remotion.media/<nombre>.wav`).
  - Densidad y volúmenes: `references/sonido.md`.
- **Código.** Parte de la plantilla (`src/`):
  - `theme.ts`: tokens de estilo.
  - `captions/`: `EditorialBlock`, `WordPop` y `KaraokePage`.
  - `components/`: Camera, Cutout, Transitions, Overlays, BrushPath, DashedCircle, Phone, Props, Dissolve.
  - `media/ARoll`.
  - Pon una escena por archivo con tiempos globales en segundos y una `<Sequence>` por escena en `Main.tsx`. Los SFX van en `data/sfx.ts`.
  - Cuando la referencia tenga un elemento que la plantilla no cubre, escríbelo nuevo: la plantilla es un punto de partida, no un límite.
- **Revisión visual antes del render completo.** `OUT_DIR=/tmp/st node scripts/stills.mjs 1.0 2.5 …` renderiza fotogramas sueltos con un solo empaquetado. Móntalos en hojas de contactos y revisa:
  - texto cortado o tapado;
  - trazos que cruzan el texto;
  - objetos fuera de cuadro;
  - legibilidad;
  - coherencia con la referencia.

  Corrige y repite.

### Fase 5: Render, control de calidad y entrega

```bash
npx remotion render Main out/v1.mp4 --concurrency=4 --crf=18
bash <skill>/scripts/finalize.sh out/v1.mp4 ../render/borrador_v1.mp4 -14   # sonoridad + limitador (+ copia ligera si >30 MB)
python3 <skill>/scripts/compare.py referencia.mp4 ../render/borrador_v1.mp4 qa/  # métricas lado a lado
```

- Revisa `qa/comparacion.md`. Cada ⚠ o se justifica por el contenido nuevo o se corrige.
- Mira `qa/lado_a_lado.jpg` y una hoja de contactos a 2 fps del render.
- Entrega el borrador (si pasa de 30 MB, la copia ligera) y una lista breve de **decisiones tomadas**: formato detectado, cómo se trasladó el ritmo, palabras destacadas, equivalencias de objetos, fuentes sustitutas, música, densidad de SFX, sonoridad.
- Indica también lo que falta del usuario: su @, créditos de imágenes, datos inventados (textos de UI, horas, cifras).

### Fase 6: Correcciones que se quedan

Cuando el usuario corrija algo y apruebe el resultado, añádelo a «Correcciones aprobadas» de `estilo.md`, con fecha y en forma de regla reutilizable. Ejemplo: «Subtítulo clave 10 % más grande que en la referencia». Esas reglas mandan sobre la referencia en vídeos futuros con ese mismo `estilo.md`. Si el usuario trae una referencia nueva, crea un `estilo.md` nuevo (o una sección por referencia) y no mezcles estilos sin que lo pida.

## Cómo convertir medidas en decisiones

- **Planos y cortes.** Iguala la mediana de duración de plano y los cortes/min con una tolerancia de ±25 %. Si la referencia apenas tiene cortes duros y casi todo son transiciones animadas, haz lo mismo. Si son cortes secos al ritmo de la música, corta en los beats (`audio.tempo_bpm_estimado` y onsets).
- **Subtítulos** (`texto` del OCR más lo que veas):
  - «palabra a palabra», 1–3 palabras, centrado → `WordPop`;
  - frases de 3–6 palabras con la palabra activa resaltada → `KaraokePage`;
  - una guía pequeña más una palabra clave grande junto al objeto → `EditorialBlock`;
  - solo títulos o rótulos → textos puntuales;
  - sin texto → no pongas subtítulos salvo que el usuario los pida, y en ese caso usa el lenguaje tipográfico de la referencia.
  - Copia la franja vertical, el tamaño (`alto_caja_px_1080`), las mayúsculas, el contorno o la caja, el color de acento y la sincronía.
- **Color y textura.**
  - Paleta → tokens de `theme.ts`.
  - `monocromo: true` → todas las imágenes con `--mono`.
  - Saturación alta → color natural o intensificado.
  - Grano y viñeta → `<Grain opacity>` y `<Vignette strength>` hasta que `compare.py` dé valores parecidos.
- **Cámara.**
  - Estático → nada de deriva.
  - Deriva lenta, pans o zooms → reproduce velocidad (px/s) y zoom/s.
  - Cámara en mano → vibración suave.
  - Zoom punches en cortes de talking-head → `ARoll` con `punches`.
- **Transiciones.** Solo las del catálogo medido y con sus duraciones. Con cortes duros, corte duro. Con un whip cada 4 s, whips cada ~4 s.
- **B-roll.** Mismo tipo de recurso, mismo tratamiento (recorte con sombra, a sangre, en marco, en pantalla de móvil…), mismo tamaño relativo, misma forma de entrar. El objeto debe *simbolizar* lo que dice la voz en ese momento.
- **Sonido.**
  - Iguala `musica_bajo_voz_db` con ±3 dB.
  - SFX con la misma densidad: con `cortes_con_sfx_%` alto, sonoriza cada corte y cada palabra clave; si la referencia apenas tiene SFX, sé sobrio salvo que el usuario pida más.
  - Sonoridad final: ~−14 LUFS (redes) con pico real ≤ −1 dBFS.
- **Estructura.** Copia la forma del gancho (qué pasa en los primeros 1–2 s), cómo escala la tensión, el cierre (pantalla final, firma, CTA) y su duración.

## Problemas técnicos clave (detalle en `references/remotion-tecnico.md`)

- **Fuentes.** Cárgalas con `@remotion/fonts` `loadFont` desde `public/fonts`, que bloquea el render hasta tenerlas. Descárgalas con `font_match.py --download`.
- **Máscaras CSS.** Una `mask-image` sobre texto recorta los rasgos que sobresalen de la caja: `p`, `j` o `g` caligráficas se convierten en «r» o «¡». Añade padding con margen negativo y quita la máscara al terminar la animación.
- **Nada de CSS `transition` ni `animation`.** Todo sale de `useCurrentFrame()`. `HtmlInCanvas` y motion blur nativo necesitan Chrome 149+ con flag: para desenfoque de movimiento usa un filtro SVG direccional (`Push`).
- **Duración de una `<Sequence>`.** Dentro de una `<Sequence>`, `useVideoConfig().durationInFrames` no es fiable para saber cuándo acaba: pasa la duración como prop (`seqDur`).
- **Revisión rápida.** Renderiza fotogramas sueltos con `stills.mjs`. El render completo de 40 s a 1080×1920 tarda unos 4 min con 4 núcleos.
- **Red bloqueada.** Si Wikimedia devuelve 429, se reintenta con espera y un User-Agent descriptivo. Si `dl.fbaipublicfiles.com` está bloqueado, `reference_audio.py` usa un espejo de Hugging Face y verifica el hash.

## Archivos de la skill

| Ruta | Para qué |
|---|---|
| `scripts/setup.sh` | entorno + proyecto Remotion + skills oficiales + plantilla |
| `scripts/analyze_reference.py` | medición completa de la referencia (cortes, cámara, color, OCR, audio, transcripción) |
| `scripts/font_match.py` | identificar tipografías y descargarlas (Google Fonts) |
| `scripts/transcribe.py` | Whisper → `captions.ts` (con inicios corregidos tras pausas) |
| `scripts/find_images.py` | buscar y descargar imágenes con licencia + créditos |
| `scripts/cutout.py` | recortar fondos (BiRefNet) + tratamiento de color |
| `scripts/reference_audio.py` | separar voz/música, música en bucle, SFX de la referencia |
| `scripts/synth_sfx.py` | biblioteca de SFX sintéticos libres |
| `scripts/jumpcut.py` | quitar silencios de un metraje (A-roll) |
| `scripts/make_grain.py` | texturas de grano |
| `scripts/finalize.sh` | sonoridad, limitador y copia ligera |
| `scripts/compare.py` | fidelidad referencia vs borrador |
| `assets/remotion-template/` | componentes Remotion reutilizables (`src/`) y `scripts/stills.mjs` |
| `assets/estilo_template.md` | plantilla de estilo.md |
| `assets/ejemplo/` | caso real completo: estilo.md, storyboard y código de escenas (formato editorial monocromo) |
| `references/analisis.md` | cómo leer el análisis, inspección visual, comandos de ráfagas e identificación de fuentes |
| `references/formatos.md` | catálogo de formatos: qué medir y cómo construir cada uno |
| `references/remotion-tecnico.md` | problemas técnicos resueltos y patrones de código |
| `references/assets-y-licencias.md` | búsqueda de imágenes, recortes, vectores, créditos |
| `references/sonido.md` | separación, música, SFX y mezcla |
