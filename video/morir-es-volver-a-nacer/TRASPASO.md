# TRASPASO · «¿Y si morir es volver a nacer?»

Documento para continuar la edición en una sesión de Claude Code **en tu PC, dentro de la carpeta Flow**.
Léelo entero antes de tocar nada. Todo el video se monta **por código** (Python + ffmpeg): no hay proyecto de
Premiere/CapCut; la "línea de tiempo" es `edit/timeline.py`.

---

## 1. Estado actual (lo entregado)

| Pieza | Estado | Dónde |
|---|---|---|
| Video largo 7:26, 1080p30, −14 LUFS | ✅ entregado (`VIDEO_FINAL_YouTube_1080p.mp4`, 370 MB) | ya lo tienes |
| 3 miniaturas 1280×720 | ✅ | `entrega/miniatura_1..3.jpg` |
| 3 shorts 1080×1920 + portadas | ✅ | shorts ya entregados; portadas en `entrega/portada_short_1..3.jpg` |
| Descripción, capítulos, créditos | ✅ | `DESCRIPCION_YOUTUBE.txt` (entregado) |
| Código del montaje | ✅ | `edit/` (también en GitHub: `camilocaicedo0802-cmd/Claude`, rama `claude/gifted-galileo-4zx4j0`, carpeta `video/morir-es-volver-a-nacer/`) |

**Siguiente objetivo:** mejorar el video con clips generados en **Google Flow (Veo, plan Ultra)** en lugar de
algunas tomas de stock y gráficos procedimentales (sección 6), volver a renderizar y rehacer los shorts.

---

## 2. Contenido del paquete

```
proyecto_morir_es_nacer/
  TRASPASO.md              ← este documento
  edit/                    ← todo el código (motor + episodio)
  work/guion.txt           ← guion completo
  work/words.json          ← tiempos palabra a palabra de la voz final (faster-whisper)
  work/voz/voz_final.flac  ← LOCUCIÓN FINAL (446,25 s, 48 kHz mono) — es el reloj del video
  work/voz/b00..b06.flac   ← los 7 bloques originales de Gemini TTS (24 kHz)
  work/voz/bloques.json    ← texto de cada bloque
  work/inventario_stock.json ← cada archivo de stock: descripción, fuente, licencia, autor, URL
  work/prompts.json        ← prompts de imágenes (no se usaron: el plan gratuito de la API no genera imágenes)
  assets/score/cue_1..6.flac ← banda sonora ORIGINAL (6 piezas, una por sección)
  assets/fonts/            ← Bebas Neue, Oswald, Poppins, Playfair, Special Elite, JetBrains Mono (OFL/Apache)
  entrega/                 ← miniaturas y portadas
  stock/                   ← (viene en el ZIP 2) videos y fotos de stock por categoría A..N
  out/                     ← aquí se escriben los renders
```

Descomprime **los dos ZIP en la misma carpeta**: el ZIP 2 crea `proyecto_morir_es_nacer/stock/`.

---

## 3. Instalación en Windows (una sola vez)

1. **Python 3.11+** (python.org, marcar "Add to PATH").
2. **ffmpeg** en el PATH: `winget install Gyan.FFmpeg` (cierra y abre la terminal; `ffmpeg -version` debe responder).
3. Dependencias:
   ```
   pip install numpy scipy pillow opencv-python-headless faster-whisper
   ```
   Si `faster-whisper` falla al abrir audio con `av`, no importa: los scripts le pasan el audio ya decodificado.
4. (Solo si vas a generar voz/imagen/música con la API) la clave de AI Studio como variable de entorno
   **en tu PC** (nunca en el código ni en el chat): `setx GEMINI_API_KEY "tu_clave"` y abre una terminal nueva.
   Los scripts `tts.py`, `gen_img.py` y `gem.py` la mandan en la cabecera `x-goog-api-key`.

Todos los comandos se ejecutan **desde la carpeta `proyecto_morir_es_nacer`**.

---

## 4. Cómo funciona el montaje

- `edit/engine.py` compone cada fotograma 1920×1080 a 30 fps (Ken Burns, gradación, texto, grano, viñeta).
- `edit/gfx.py` bases (`Still`, `Video`, `Split`, `Solid`) y transiciones (`fade`, `black`, `flash`, `whip_l/r`,
  `zoom`, `glitch`).
- `edit/mist.py` **el estilo de la referencia**: `Kinetic` (titular condensado con brillo; estilos `w` blanco,
  `r` rojo, `y` amarillo, `s` cursiva roja, `sy` cursiva amarilla, `k` pequeño), `TypeLine` (máquina de escribir
  roja), `NeonBox` (caja roja tipo «Y ESO NO CUADRA»), `Rings`, `BigNumber` (cifra que cuenta), `Polaroid`,
  `Quote` (cita amarilla), `LowerName`, `Dim`, `Tint`, `Blur`, `Flicker`; diagramas `ECG`, `Cycle`, `TimeArrow`;
  fondos `Embers`, `LightTunnel`, `Corridor`; post-efectos `chroma`, `heartbeat`, `shake`.
- `edit/timeline.py` **la línea de tiempo**: un `add(t, base, overlays, tr=…)` por plano. `t` se ancla a la
  voz con `a("frase")`, que busca la frase **en orden** dentro de `work/words.json` (no hace falta escribir
  segundos). Helpers: `kb(clave, mov, grado)` foto con movimiento (`in out l r up down punch`), `vid(clave, inicio,
  velocidad, grado)` video, `pol(clave)` foto enmarcada, `K("TEXTO|w", "acento|s")` texto. `clave` es cualquier
  trozo único del nombre del archivo dentro de `stock/` (p. ej. `"mk_4747"`, `"us_HqhKXIrfz8I"`).
- Gradaciones: `mist` (cálida desaturada, la principal), `mist_red`, `mist_cold`, `sepia`.
- 150 planos, mediana 2,8 s por plano (la referencia: 3–4 s).

### Comandos

```bash
# revisar todos los planos (hojas con el fotograma central de cada plano) → work/mids/mid_*.jpg
python edit/mids.py work/mids 446.25

# render completo (≈ 30–60 min según el PC; usa 4 procesos)
python edit/render.py out/video_mudo.mp4 --workers 4 --total 446.25

# mezcla: voz + música (ducking) + efectos sincronizados → −14 LUFS
python edit/mix.py work/voz/voz_final.flac work/mix_final.wav 446.25

# unir imagen y sonido
ffmpeg -i out/video_mudo.mp4 -i work/mix_final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest out/MASTER.mp4

# versión para YouTube (≈ 370 MB)
ffmpeg -i out/MASTER.mp4 -c:v libx264 -preset slow -crf 20 -maxrate 6400k -bufsize 12800k -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/VIDEO_FINAL_YouTube_1080p.mp4

# shorts (usa el MASTER y la mezcla) → entrega/shorts/*.mp4
python edit/shorts.py out/MASTER.mp4 work/mix_final.wav entrega/shorts

# miniaturas y portadas
python edit/thumbs_mist.py entrega
python edit/covers.py entrega
```

Para re-renderizar solo un tramo: `python edit/render.py out/tramo.mp4 --from 120 --to 180 --total 446.25`.

---

## 5. Guía de estilo (sacada de la referencia, plano a plano)

- Ritmo: plano cada 2,5–4 s; más rápido en el gancho (primer minuto).
- Color oscuro, cálido y desaturado, negros densos, **grano + viñeta** siempre; acentos rojo (#E21E2A) y amarillo (#FFD60A).
- Texto en casi todos los planos, **nunca la frase entera**: 2–5 palabras clave, condensadas en mayúsculas
  (Bebas Neue) con brillo, y una palabra de acento en cursiva serif roja/amarilla.
- Separadores en negro con máquina de escribir roja; preguntas clave en **caja roja de neón** con glitch.
- Fechas/cifras grandes que cuentan; fotos antiguas como polaroid girada; nombres en cursiva bold abajo a la izquierda.
- Voz: masculina grave, español neutro, ~150–160 palabras/min, pausas antes de las preguntas.
- Música: colchones oscuros (drones, pads, piano grave), bajo la voz con ducking; efectos: whoosh, golpes, estática en glitch, tic de máquina de escribir, latido, pitido del monitor.

### Estructura y anclas (tiempos en la voz final)

| Tiempo | Sección | Música |
|---|---|---|
| 0:00 | Gancho: «Imagina que acabas de morir» → túnel de luz → 4 preguntas | cue_1 (dron oscuro) |
| 1:17 | Título «¿Y si morir es volver a nacer?» → el vientre y el nacimiento | cue_2 (latido cálido) |
| 2:07 | Dos túneles: morir y nacer, la memoria se borra | cue_3 (misterio) |
| 3:28 | Los patrones que se repiten | cue_4 (tensión) |
| 4:34 | El tiempo: edificio infinito, laberinto, otras vidas | cue_5 (tic-tac) |
| 6:01 | La pregunta más inquietante → foto de bebé → cierre | cue_6 (piano final) |

---

## 6. Plan con Flow (Veo, plan Ultra): clips a generar

Genera en **16:9, 1080p**, 8 s cada uno, **sin texto, sin logos, sin música** (el audio se descarta). Guárdalos
en `stock/O_flow/` con el nombre indicado (p. ej. `flow_01_tunel.mp4`). Estilo común para añadir a cada prompt:

> *cinematic, dark moody documentary look, low-key lighting, warm amber and deep red tones, volumetric light,
> film grain, shallow depth of field, slow camera movement, photorealistic, no text*

| # | Archivo | Prompt (inglés funciona mejor en Veo) | Reemplaza en `timeline.py` (ancla) |
|---|---|---|---|
| 1 | `flow_01_tunel.mp4` | A lone human silhouette slowly walking down a long dark organic tunnel toward a blinding white light at the end, dust particles floating in the light beams, slow push-in | `a("Una luz al")` y `a("Sientes que")` (hoy `LightTunnel`) |
| 2 | `flow_02_alma.mp4` | Top-down shot of a person lying still in a hospital bed in a dark room, their body slowly dissolving into thousands of glowing golden particles rising upward | `a("Ya no sientes")` |
| 3 | `flow_03_recuerdos.mp4` | Old family photographs floating in darkness, slowly burning at the edges and disintegrating into embers and ash | `a("Los recuerdos")` |
| 4 | `flow_04_vientre.mp4` | A human fetus curled inside the womb, warm red light glowing through the amniotic sac, floating particles, gentle heartbeat movement, medical art realism | `a("pasaste meses")` |
| 5 | `flow_05_canal.mp4` | Point-of-view moving forward through a narrow soft red organic tunnel toward an intense white light opening, abstract and tasteful | `a("Atravesaste")` y `a("que te llevaba")` |
| 6 | `flow_06_ojo_bebe.mp4` | Extreme macro close-up of a newborn baby's eye slowly opening for the first time, bright light reflected in the dark iris | `a("y los abres")` |
| 7 | `flow_07_dos_familias.mp4` | Split composition: left a family mourning at a bedside in cold blue light, right a family welcoming a newborn in warm golden light, same hospital corridor | `a("Una familia te")` (hoy `Split`) |
| 8 | `flow_08_edificio.mp4` | A surreal infinite building seen from outside at night, thousands of lit windows stacked endlessly, each room from a different historical era, slow upward crane shot | `a("de un edificio")` (hoy `Corridor`) |
| 9 | `flow_09_puertas.mp4` | An endless corridor of identical wooden doors, one door slowly opening with warm light pouring out, a small silhouette walking toward it | `a("y vuelve a")` (hoy `Corridor`) |
| 10 | `flow_10_epocas.mp4` | The same man shown across different historical eras side by side — medieval peasant, 1700s sailor, 1920s worker, modern man — same face, same eyes, looking at camera | `a("tal vez ha sido")` |
| 11 | `flow_11_salto.mp4` | A glowing human silhouette made of light leaping between floating rooms suspended in darkness, each room from a different century | `a("en el que la")` |
| 12 | `flow_12_espejo.mp4` | A person standing between two facing mirrors creating infinite reflections receding into darkness, each reflection slightly different, red rim light | `a("solo conocerías")` |

Cómo cambiar un plano (ejemplo, clip 1):

```python
# antes
add(a("Una luz al"), LightTunnel((0.25, 0.7)), [K("UNA LUZ|w", "al final del túnel|sy", t0=0.3, size=120, y=0.78)], tr="flash", td=0.3)
# después
add(a("Una luz al"), vid("flow_01_tunel", 0, 1.0, "mist"), [K("UNA LUZ|w", "al final del túnel|sy", t0=0.3, size=120, y=0.78)], tr="flash", td=0.3)
```

Después: `mids.py` para revisar → render → mezcla (el audio no cambia si no cambian las transiciones) → MASTER → shorts.
En `mix.py` el estruendo grave (`rumble`) suena en los planos con `LightTunnel`; si los cambias por clips, añade
un `place(buf, rumble(...), ...)` equivalente si quieres conservarlo.

**Derechos:** los videos de Veo/Flow generados con tu cuenta se pueden usar en tu canal; añade en la descripción
"Algunas escenas generadas con IA (Google Veo)" y marca en YouTube Studio la casilla de **contenido alterado o sintético**
cuando sea realista.

---

## 7. Lecciones de este proyecto (para no repetirlas)

- **API de Gemini:** las claves nuevas de AI Studio empiezan por `AQ.` y solo funcionan en la cabecera
  `x-goog-api-key` (enviadas como `Authorization: Bearer` dan error). El endpoint compatible con OpenAI devuelve el TTS vacío.
- **Plan gratuito de la API:** voz 10 generaciones/día por modelo; imágenes y Lyria con cuota 0; Veo no aparece.
  El plan **Google AI Ultra no cuenta para la API** (se factura aparte en AI Studio → Set up billing).
- **TTS:** si pones las instrucciones de estilo delante del texto, el modelo **las lee en voz alta**. Usa el formato
  `# AUDIO PROFILE / ## ESCENA / ### NOTAS DEL DIRECTOR / #### TRANSCRIPCIÓN` (ya está en `tts.py`).
  `gemini-3.8-flash-tts` no admite `systemInstruction`. Voz usada: **Charon**. Los bloques 3–5 salieron rápidos
  (175–184 ppm) y se les aplicó `atempo` 0,90–0,95; el bloque 7 `atempo` 0,95.
- **Verificar la voz:** transcribe sin `initial_prompt` (con prompt, Whisper alucina repeticiones).
- **Música:** las piezas sintetizadas brillantes sonaban "MIDI"; se oscurecieron con filtro paso bajo 5,5 kHz.
- **Mixkit:** usar solo clips "Free"; casi la mitad dicen `#videoFree` en el JSON pero son "Restricted". Revisa cada página.
- **Shorts:** los subtítulos se pisaban cuando dos palabras se solapaban en el tiempo: ya está corregido en `shorts.py`.
- En Windows, `subtitles=` de ffmpeg falla con rutas `C:\…`; `shorts.py` ya trabaja con rutas relativas.

---

## 8. Mensaje para empezar la sesión local

Abre Claude Code en la carpeta `Flow` (donde descomprimiste esto) y pega:

> Lee `proyecto_morir_es_nacer/TRASPASO.md` completo. Es un video de YouTube montado por código que vamos a
> continuar. Comprueba la instalación (sección 3) y que `python edit/mids.py work/mids 446.25` funcione desde
> `proyecto_morir_es_nacer`. Luego vamos a integrar los clips de Flow de la sección 6 que yo vaya guardando en
> `stock/O_flow/`, revisar, renderizar y rehacer los shorts.
