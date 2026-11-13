# SLATE · Reel "Holiday spray tan" (Remotion)

Reel vertical 1080×1920 a 30 fps (21.9 s) editado con Remotion siguiendo el
estilo del reel de referencia. La guía de estilo con valores medidos está en
[`estilo.md`](estilo.md).

## Estructura

| Ruta | Qué es |
| --- | --- |
| `estilo.md` | Guía de estilo del referente + correcciones aprobadas |
| `src/SlateReel.tsx` | Línea de tiempo completa (tomas, b-roll, títulos, subtítulos, SFX, música) con todos los tiempos en fotogramas |
| `src/components/Shots.tsx` | Reencuadre de tomas 4K (zoom/punch-in sobre la cara) y b-roll |
| `src/components/Graphics.tsx` | Títulos en cascada, ítems numerados, barra 1–10, calendario, halo, subtítulos, iconos, cierre |
| `src/theme.ts` | Fuentes (Inter Display + Instrument Serif Italic) y colores del referente |
| `analysis/` | Análisis del referente: hojas de fotogramas, tiras de animación, espectrogramas, transcripciones Whisper |
| `scripts/` | Preparación de material y utilidades de análisis |

## Material (no está en git)

El vídeo en crudo, el b-roll, los SFX y la música pesan demasiado para git.
Se descargan de las carpetas de Drive del cliente y se preparan con:

```bash
scripts/prep_talking.sh   # tomas a cámara: 30 fps, etalonaje cálido, voz a -16 LUFS → public/raw
scripts/prep_broll.sh     # b-roll elegido, recortado y etalonado → public/broll
```

`public/sfx` contiene los SFX del pack 1 que usa el referente y el tecleo para los textos (normalizados a −3 dBFS);
`public/brand` el logo vectorizado y las fuentes Black Mango / Jimmy Script extraídas del manual; y
`public/music/music_v1.mp3` la base generada con IA (Higgsfield · ElevenLabs Music v2).

## Comandos

```bash
npm run dev                                          # Remotion Studio
npx remotion render SlateReel out/slate_reel.mp4     # exportar
node scripts/stills.mjs 120 330 495                  # fotogramas sueltos para revisar
```
