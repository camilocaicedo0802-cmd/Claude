# Editor de vídeo con Remotion

Proyecto independiente del monorepo (no es un workspace). Edita reels verticales **1080×1920 a 60 fps**
siguiendo el estilo medido en [`estilo.md`](estilo.md).

Cada reel sale en **dos opciones** con el mismo guion, tomas, música y tiempos:

| Composición | Opción | Formato |
| --- | --- | --- |
| `ArmandoBits` | A | Recorte vertical a pantalla completa, textos sobre el pecho y detrás del sujeto (estilo.md §10) |
| `ArmandoBitsHorizontal` | B | Plano horizontal en una ventana, con tipografías y recursos arriba y abajo (estilo.md §12) |

## Qué hay

| Ruta | Contenido |
| --- | --- |
| `estilo.md` | Guía de estilo extraída del vídeo de referencia, con valores concretos y las correcciones aprobadas |
| `analisis/referencia/` | Hojas de contacto, transcripción y comparación de SFX del vídeo de referencia |
| `src/theme.ts` | Colores, tipografías y zonas del lienzo |
| `src/timeline.ts` | Inicio de cada frase y cambios de formato |
| `src/edit/` | El montaje: subtítulos (delante y detrás del sujeto), zooms, b-roll, SFX y la frase escrita |
| `src/components/` | Escenario de vídeo, subtítulos, gráficos, transiciones y testimonio |
| `src/horizontal/` | Opción B: ventana, zona superior (titulares, palabra gigante), recolocación de subtítulos y gráficos |
| `src/data/` | Palabras con tiempos (Whisper), posición de la cara y de la coronilla, y origen de cada SFX |
| `scripts/prep/*.py` | Guiones de preparación: transcribir, cortar tomas, limpiar voz, preparar SFX |
| `material/` y `public/media/` | Material pesado (tomas, descargas de Drive, modelos). **No se sube a Git** |

## Ver y exportar

```bash
npm install
```

```bash
npm run dev
```

```bash
npx remotion render ArmandoBits out/armando-bits.mp4
```

```bash
npx remotion render ArmandoBitsHorizontal out/armando-bits-opcionB.mp4
```

Si el render completo se queda sin memoria, se puede hacer por tramos de 10 s (reanudable; une los tramos sin
recomprimir y saca solo la imagen, el audio va aparte con `--codec=wav`):

```bash
node scripts/render_tramos.mjs ArmandoBitsHorizontal out/armando-bits-opcionB-render.mp4
```

Fotogramas sueltos para revisar (segundos):

```bash
node scripts/stills.mjs 1.6 12 36.9
```

```bash
node scripts/stills.mjs --comp=ArmandoBitsHorizontal 1.6 12 36.9
```

## Rehacer la preparación desde el material en crudo

Hace falta ffmpeg y Whisper (`pip install openai-whisper`). Con el material en `material/crudo`,
`material/testimonios` y `material/drive`:

```bash
python scripts/prep/transcribir.py material/crudo/*.MOV material/testimonios/*.mp4
```

```bash
python scripts/prep/tomas.py
```

```bash
python scripts/prep/edl.py
```

```bash
python scripts/prep/exportar_tomas.py --force
```

```bash
python scripts/prep/audio_tomas.py
```

```bash
python scripts/prep/caras_seguimiento.py
```

```bash
python scripts/prep/recortar_sujeto.py
```

```bash
python scripts/prep/cabeza_tope.py
```

```bash
python scripts/prep/broll_horizontal.py
```

```bash
python scripts/prep/preparar_sfx.py
```

`edl.py` contiene la elección de tomas (qué frase sale de qué clip); `tomas.py` lista todas las repeticiones para elegir.
`recortar_sujeto.py` genera las capas con transparencia para el texto detrás del sujeto (modelo MODNet en
`material/matting/modnet.onnx`, descargado de Hugging Face `Xenova/modnet`). `cabeza_tope.py` mide en esas capas
la altura de la coronilla, que la opción B usa para que la cabeza sobresalga de la ventana siempre lo mismo.
`broll_horizontal.py` saca el b-roll de la opción B (`public/media/broll/brh_*.mp4`): recortes 16:10 de los mismos clips.

B-roll de internet usado (Mixkit, licencia libre «Stock Video Free License»): clips 41678 (partitura) y 43403 (actriz).

Los SFX salen **solo** de las carpetas del cliente; `src/data/sfx.json` dice de qué archivo viene cada uno.
