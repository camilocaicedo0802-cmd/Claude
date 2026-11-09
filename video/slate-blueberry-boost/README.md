# SLATE · Radiant Blueberry Boost (reel 9:16)

Edición por código de un reel vertical (1080×1920, 30 fps, ~43 s) para SLATE (Tulsa, OK), siguiendo
el estilo del reel de referencia “Sinus Facial”: mismas tipografías, mismos efectos de texto, mismo
ritmo de cortes, efectos de sonido extraídos de la referencia y música similar.

No hay medios pesados aquí (videos de Drive, música ni render final): solo el código, los datos ligeros
y los efectos de sonido extraídos (`sfx/`).

## Material

| Carpeta de Drive | Contenido | Uso |
| --- | --- | --- |
| `b-roll` (IMG_7029, IMG_7032) | Presentadora hablando a cámara, varias tomas | Locución + planos a cámara |
| `Proceso` (MVI_52xx) | Pasos del facial (peel de arándano, limpieza, gua sha, masajes) | B-roll |
| `Después` (IMG_7040) | Resultado final de la piel | B-roll “super dewy” |

## Análisis de la referencia

- **Cortes**: un plano cada ~1,8 s; dos planos a cámara al inicio (el segundo con *punch-in*), luego b-roll.
- **Tipografías** (equivalentes libres, OFL):
  - Títulos en mayúsculas condensadas → **Oswald 500** (“A FACIAL MADE OF”, “THE RADIANT BLUEBERRY BOOST”, “SCULPT”).
  - Acentos en serif itálica → **EB Garamond Italic 600** (“blueberries?”, “firmer,” “& depuff”, “and refreshed.”).
  - Subtítulos → **Poppins Bold** 61 px, letras juntas (−4 % de tracking, espacios entre palabras normales),
    con el brillo de la referencia: halo blanco amplio (σ≈48 px) + sombra oscura fina 3 px abajo. Parámetros
    ajustados midiendo la luminancia alrededor de los subtítulos originales.
  - Línea en negrita sans → **Inter 700** (“calm”). Tarjeta final → **Montserrat**.
- **Efectos de texto**: revelado con destello y partículas (sparkle), máquina de escribir letra a letra,
  palabra serif que entra con zoom y tracking (“Steam,” en la referencia), línea que sube desde desenfocado,
  subtítulos que aparecen palabra por palabra, tarjeta blanca con el logo que se oscurece y texto tecleado.
- **Audio de la referencia**: voz −14,8 LUFS, música ~12 LU por debajo, 117,5 BPM, Do# menor.

## Efectos de sonido extraídos de la referencia (`sfx/`)

1. `tools/separate.py`: HTDemucs (pesos en *safetensors*) separa la voz → pista instrumental.
2. `tools/tonal.py`: máscara de picos tonales para quedarse solo con los efectos (sin restos de música ni
   fricativas de la voz).
3. Resultado: `sparkle.wav` (glissando de campanitas, suena en cada título con destello; se promediaron las
   dos apariciones alineadas), `ding.wav` (campana del *punch-in*/título) y `ting.wav`.
   Se colocan en los mismos momentos equivalentes y con los mismos niveles relativos que en la referencia.

## Locución

`edit/voice_edl.py` lista las mejores tomas (sin muletillas, repeticiones ni “oh sorry”).
`tools/assemble_voice.py` las une, comprime silencios internos largos y guarda el mapa de piezas
(`voice_raw_map.json`) para que los planos a cámara queden sincronizados con los labios.
La transcripción final (`words.json`) alimenta los subtítulos.

## Render

```bash
export FONT_DIR=/ruta/fonts DRIVE=/ruta/drive
python3 edit/render.py out/video_noaudio.mp4         # imagen
python3 edit/mix.py sfx /ruta/musica.wav out/mix.wav  # voz + música + SFX
ffmpeg -i out/mix.wav -af "volume=1.1dB,alimiter=limit=0.82:attack=2:release=60:level=disabled" out/mix_master.wav
ffmpeg -i out/video_noaudio.mp4 -i out/mix_master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest final.mp4
```

`python3 edit/render.py --stills 1.5,6,24.8 carpeta/` genera fotogramas sueltos para revisar.

## Variaciones

`VARIANT` elige el final (por defecto `cta`):

| Variante | Duración | Final |
| --- | --- | --- |
| `cta` | 43,4 s | “If you're in Tulsa… come try the Radiant Blueberry Boost at Slate” + tarjeta SLATE con “Book your… / Tulsa, OK” |
| `nocta` | 38,8 s | Termina en “…to help calm and refresh the skin.” sobre el plano del spray con “calm / and refreshed.”; la música se desvanece |

```bash
VARIANT=nocta python3 edit/render.py out/video_noaudio_nocta.mp4
VARIANT=nocta python3 edit/mix.py sfx /ruta/musica.wav out/mix_nocta.wav
```

En el título del gua sha va “SCULPT / depuff”, sin el signo “&”.

## Música

Pista original instrumental generada con ElevenLabs Music v2.5 (vía Higgsfield): chill R&B/pop,
117 BPM, Do#, piano eléctrico, pads y bajo que entra a los ~16 s, igual que la estructura de la referencia.

## Tipografías

Se descargan del repositorio público de Google Fonts (`github.com/google/fonts`, licencia OFL):
`ofl/oswald/Oswald[wght].ttf`, `ofl/ebgaramond/EBGaramond-Italic[wght].ttf`, `ofl/nunito/Nunito[wght].ttf`,
`ofl/inter/Inter[opsz,wght].ttf`, `ofl/montserrat/Montserrat[wght].ttf`, `ofl/poppins/Poppins-Bold.ttf`
→ carpeta indicada en `FONT_DIR`.

## Verificación de la entrega

- `ffprobe`: 43,4 s (con CTA) y 38,8 s (sin CTA), H.264 1080×1920 a 30 fps, AAC 48 kHz estéreo.
- Loudness integrado −13,9 LUFS, pico −1,6 dBFS; decodificación completa sin errores.
- Transcripción del archivo final: el guion completo se entiende sobre la música.
- `tools/qa.sh` saca el fotograma central de cada plano para revisar encuadres y textos.
