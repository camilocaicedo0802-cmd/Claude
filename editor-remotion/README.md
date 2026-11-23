# Editor de vídeo con Remotion

Proyecto independiente del monorepo (no es un workspace). Edita reels verticales **1080×1920 a 60 fps**
siguiendo el estilo medido en [`estilo.md`](estilo.md).

## Qué hay

| Ruta | Contenido |
| --- | --- |
| `estilo.md` | Guía de estilo extraída del vídeo de referencia, con valores concretos y las correcciones aprobadas |
| `analisis/referencia/` | Hojas de contacto, transcripción y comparación de SFX del vídeo de referencia |
| `src/theme.ts` | Colores, tipografías y zonas del lienzo |
| `src/timeline.ts` | Inicio de cada frase y cambios de formato |
| `src/edit/` | El montaje: subtítulos, zooms, b-roll, SFX y la frase escrita |
| `src/components/` | Escenario de vídeo, subtítulos, gráficos, transiciones y testimonio |
| `src/data/` | Palabras con tiempos (Whisper), posición de la cara y origen de cada SFX |
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

Fotogramas sueltos para revisar (segundos):

```bash
node scripts/stills.mjs 1.6 12 36.9
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
python scripts/prep/caras.py
```

```bash
python scripts/prep/preparar_sfx.py
```

`edl.py` contiene la elección de tomas (qué frase sale de qué clip); `tomas.py` lista todas las repeticiones para elegir.

Los SFX salen **solo** de las carpetas del cliente; `src/data/sfx.json` dice de qué archivo viene cada uno.
