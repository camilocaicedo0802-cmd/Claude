# CR7 — vídeo vertical con Remotion

Vídeo de 30 s (1080x1920, 30 fps) sobre Cristiano Ronaldo con el estilo del vídeo de referencia.

- `estilo.md` — guía de estilo extraída de la referencia (valores concretos) + correcciones aprobadas.
- `src/` — composición `CR7` (escenas en `src/scenes/`, tiempos por palabra en `src/data/palabras.ts`).
- `public/` — voz, música limpia, SFX extraídos, fotos, recortes, escudos y fuentes.
- `analisis/` — material del análisis de la referencia (fotogramas, transcripción, SFX).
- `scripts/` — preparación de fondos, fuente condensada, extracción de audio y render.
- `entregas/` — vídeos finales renderizados.
- `CREDITOS.md` — fuentes y licencias de cada recurso.

```bash
npm i
npm run dev                         # Remotion Studio
bash scripts/render.sh out/cr7.mp4  # render + masterizado a -14 LUFS
```
