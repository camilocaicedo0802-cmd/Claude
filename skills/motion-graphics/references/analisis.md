# Analizar una referencia

Objetivo: que `estilo.md` permita reconstruir la edición sin volver a ver el vídeo. Cada afirmación lleva un número (px a escala 1080 de ancho, segundos, hex, dB) o la etiqueta [SUPOSICIÓN].

## 1. Ejecutar el analizador

```bash
python3 scripts/analyze_reference.py ref.mp4 analisis_ref --ocr --separate --whisper small --lang es
```

| Flag | Qué añade | Coste |
|---|---|---|
| (ninguno) | cortes, planos, cámara, color, grano, viñeta, audio básico, hojas de contactos | segundos |
| `--ocr` | texto en pantalla: posición, tamaño, palabras/bloque, aparición, colores, caja | ~0.3 s por fotograma analizado (`--ocr-step 0.25` = 4 por segundo) |
| `--separate` | voz frente a música, nivel relativo, instantes con SFX, % de cortes sonorizados | ~1× la duración en CPU |
| `--whisper small` | transcripción de la referencia, palabras/min | ~1–2× la duración |
| `--sensitivity 1.5` | detecta más cortes (útil si hay cortes suaves no detectados) | — |

## 2. Cómo leer `analisis.md`

- **Ritmo.**
  - `plano_mediana_s` es la cifra más importante para trasladar el ritmo.
  - `cortes_por_min` alto (>40) → edición rápida.
  - Muchos `transiciones_suaves` y pocos cortes → el vídeo «fluye» con transiciones animadas, como un plano secuencia.
  - `tiempo_con_cambio_%` cerca de 100 → nunca hay un fotograma quieto: deriva de cámara, grano o animación constante.
  - `eventos_visuales_por_s` estima cuántas «cosas» pasan por segundo.
- **Cámara por plano.**
  - `estático`, `pan/tilt o deriva` (px/s), `zoom-in/out` (fracción de escala por segundo: 0.05 = +5 % por segundo), `cámara en mano` o `animación interna`.
  - El zoom por cuadrantes es aproximado: confírmalo mirando los fotogramas.
- **Color.**
  - Paleta k-means por plano y global, luminancia, saturación y `tema` claro/oscuro/medio.
  - La alternancia claro/oscuro entre planos suele ser una decisión de estructura (por ejemplo, oscuro para los momentos emocionales).
- **Grano y viñeta.**
  - El grano es la media del Laplaciano en zonas planas: ~3–5 limpio, >7 grano visible.
  - La viñeta es la luminancia de las esquinas dividida por la del centro: ~1.0 sin viñeta, <0.85 marcada.
- **Texto (OCR).**
  - `posicion_vertical_mediana_%` (50 = centro; 70–80 = tercio inferior), `alineacion` y `alto_caja_px_1080` (la altura de la caja ≈ 1.2–1.4 × la altura de mayúscula; el tamaño CSS ≈ altura de caja × 0.9).
  - `palabras_por_caja`, `ratio_mayusculas`, `aparicion` (acumulativa = palabra a palabra; por bloques = se reemplaza), `colores_texto_frecuentes` y `caja_de_fondo_probable_%`.
  - Abre `ocr_timeline.json` para ver qué texto aparece en cada instante y compáralo con `transcripcion.json`. Si el texto coincide con lo que se dice, son subtítulos; si no, son títulos o rótulos.
- **Audio.**
  - `lufs_integrado`, silencios y `tempo_bpm_estimado` (ritmo de la música, no de la voz).
  - En `capas`: `voz_presente`, `musica_bajo_voz_db` (cuántos dB está la música por debajo de la voz), `sfx_candidatos_t` y `cortes_con_sfx_%`.

## 3. Inspección visual (imprescindible)

Abre `contact_planos.jpg` y las `contact_2fps_*.jpg`. Después extrae ráfagas de los momentos clave para ver las animaciones fotograma a fotograma:

```bash
# 15 fps durante 1 s a partir de 3.2 s, en mosaico 5x3
ffmpeg -v error -ss 3.2 -t 1 -i ref.mp4 -vf "fps=15,scale=360:-2,tile=5x3" -frames:v 1 rafaga_3.2.png
# recorte ampliado de una zona (x,y,w,h en px del vídeo original) para identificar tipografía
ffmpeg -v error -ss 3.9 -i ref.mp4 -frames:v 1 -vf "crop=460:130:55:470,scale=1000:-1:flags=lanczos" recorte.png
# medir colores exactos en un fotograma
python3 -c "from PIL import Image; im=Image.open('f.png').convert('RGB'); print(im.getpixel((20,20)))"
```

Anota para cada elemento:

| Elemento | Qué medir |
|---|---|
| Subtítulos | fuente(s), peso, tamaño, color, contorno/sombra/caja, mayúsculas, posición, palabras por bloque, entrada (fade, pop, subida, máscara, máquina de escribir), duración de la entrada en frames, salida, palabra destacada (color, tamaño, fuente distinta), sincronía con la voz |
| Textos no subtitulados | títulos, contadores, etiquetas, flechas, rótulos de lugar o fecha |
| B-roll | tipo (foto recortada, foto a sangre, vídeo, icono, 3D, captura, ilustración), tratamiento (B/N, duotono, saturado), sombra, borde, marco, tamaño relativo, entrada |
| Gráficos | formas (círculos, líneas, flechas, subrayados, trazos de pincel, bandas, marcos), grosor, estilo de dibujo (se dibujan o aparecen) |
| Transiciones | tipo, duración en frames, dirección, desenfoque, SFX asociado |
| Cámara | deriva, zoom continuo, golpes de zoom, sacudidas, inclinación, plano secuencia que viaja entre objetos |
| Gancho y cierre | qué ocurre en los primeros 1.5 s; pantalla final, CTA, firma, negro |

## 4. Identificar tipografías

1. Recorta una palabra limpia (sin trazos encima) y amplíala.
2. Decide la categoría con `python3 scripts/font_match.py --list`: grotesk-heavy, geometric, condensed, rounded, serif-display, script, handwriting, brush-marker, mono o impact-meme.
3. Compara:
   ```bash
   python3 scripts/font_match.py --crop recorte.png --text "creatividad" --category grotesk-heavy --out fuentes.png
   python3 scripts/font_match.py --crop recorte.png --text "aprendiste algo" --category script --dark --out fuentes2.png
   ```
4. Mira formas distintivas: a de uno o dos pisos, terminación de la t, cola de la y/g, R, apertura de la e, contraste del trazo, anchura y espaciado. Si ninguna encaja, prueba con `--families "A:800,B:900"`.
5. Descarga la elegida: `python3 scripts/font_match.py --download "Archivo:800" --dest <proyecto>/public/fonts` y ajusta `src/fonts.ts`.
6. Si la fuente original es comercial (Helvetica Neue, Gilroy, Proxima, Montserrat-like de CapCut…), usa la libre más cercana y anótalo como [SUPOSICIÓN: original X; sustituto Y].

## 5. Resumen de 5 líneas (punto de control)

1. Ritmo y estructura (planos, transiciones, cámara).
2. Subtítulos y textos.
3. B-roll y motion graphics.
4. Color y textura.
5. Sonido (voz, música, SFX y niveles).

Con números. Ejemplo: «3 escenas en 7.7 s sin cortes secos; algo nuevo cada 0.2–0.5 s; cámara siempre en movimiento (535 px de bajada, zoom de 1 a 1.25)».
