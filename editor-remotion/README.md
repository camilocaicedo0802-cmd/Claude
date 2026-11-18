# editor-remotion

Editor de vídeo vertical (1080 × 1920, 60 fps) hecho con [Remotion](https://www.remotion.dev).
Vídeo actual: **"Semilla certificada" — AgroKrack**.

- `estilo.md` — guía de estilo extraída del vídeo de referencia. Es la fuente de verdad: cada
  corrección aprobada se añade ahí (sección 13) y se refleja en `src/estilo.ts`.
- `src/estilo.ts` — los valores de `estilo.md` como constantes (colores, tipografía, tiempos, mezcla).
- `src/datos/edicion.ts` — la edición: tramos de voz, planos, subtítulos, gráficos y efectos.
- `src/datos/palabras.json` — tiempos por palabra de Whisper, afinados con la energía de la voz.
- `src/componentes/` — planos, subtítulos, píldoras, iconos, transición de luz, gráfico y cierre.
- `public/sfx/ORIGEN.md` — de qué archivo del pack del cliente sale cada efecto de sonido.

## Preparar el material (una vez)

El material pesado no está en git; se regenera con estos pasos:

```bash
npm install
```

```bash
./scripts/descargar_crudo.sh
```

```bash
./scripts/preparar_clips.sh
```

```bash
python3 -m venv .venv-whisper && .venv-whisper/bin/pip install faster-whisper scipy
```

```bash
for f in material/crudo/*.mp4; do .venv-whisper/bin/python scripts/transcribir.py "$f" "material/transcripciones/$(basename "$f" .mp4).json" es; done
```

```bash
.venv-whisper/bin/python scripts/preparar_voz.py
```

```bash
./scripts/preparar_musica.sh
```

`scripts/afinar_palabras.py` vuelve a generar `src/datos/palabras.json` a partir de las
transcripciones (necesita además la pasada con VAD que guarda `material/transcripciones/_vad.json`).

## Ver y exportar

```bash
npm run dev
```

```bash
npm run render
```

```bash
node scripts/fotogramas.mjs 0.5 3.9 22.3
```

El último comando saca fotogramas sueltos (en segundos) a `out/stills/` para revisar sin exportar todo.
