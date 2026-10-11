# Promo editor de video & motion designer (Remotion)

Video publicitario vertical **1080×1920 · 30 fps · 30 s** hecho con [Remotion](https://remotion.dev), siguiendo la
dirección de arte analizada en [`estilo.md`](estilo.md) (referencia @danushkmotion): fondo #F0F0F0 con retícula de
puntos, tarjetas moradas con degradado, Inter ExtraBold Italic, recortes en B/N que rompen el borde de la tarjeta,
arcos punteados, conectores y transiciones con motion blur.

## Estructura

| Escena | Frames | Locución | Recursos |
|---|---|---|---|
| `S1Intro` | 0–166 | ¿Necesitas editor…? / fluidez, ritmo, calidad | píldora → tarjeta (objeto compartido), recorte que rompe el borde, onda, chips |
| `S2Monitor` | 160–366 | algo más que simples cortes / edición dinámica, motion graphics, animaciones 3D | monitor con timeline (cortes con cuchilla), editor de gráficos con keyframes, cámara 3D (three.js) |
| `S3Demo` | 357–466 | transiciones fluidas, color grading, sound design | transiciones dentro de la tarjeta, antes/después + ruedas de color, pistas de audio |
| `S4Atencion` | 464–596 | captar la atención / audiencia mirando | teléfono con reel y subtítulos dinámicos, retención 92 %, contador de vistas |
| `S5Formatos` | 588–676 | reels que impactan / anuncios que venden | tarjeta reel + anuncio con cursor y clic |
| `S6Destaca` | 670–773 | tú tienes la idea / un video que destaca | storyboard punteado → tarjeta pulida (match cut) → zoom out entre tarjetas grises |
| `S7CTA` | 767–900 | ¿listo… siguiente nivel? ¡Hablemos! | escalones de nivel, recorte que emerge, cierre "hablemos." + botón |

Los tiempos de cada palabra están en `src/cues.ts` (generado con faster-whisper sobre la locución editada).

## Comandos

```bash
npm install
npm run studio        # previsualizar y ajustar
npm run render        # → out/promo.mp4
```

Audio (se regenera solo si cambias tiempos o la cue list `src/sfx.json`):

```bash
python3 -I tools/editar_voz.py assets/voz.mp3 public/audio/voz_edit.wav   # recorta silencios + tempo ×1,19
python3 -I tools/audio.py                                                 # música + SFX + mezcla (−14 LUFS)
```

`tools/preview.sh nombre f1 f2 …` genera una hoja de contacto de frames en `out/prev_nombre.jpg`.

## Recursos

- Fotos: Unsplash (licencia Unsplash, uso comercial permitido). Recortes con `rembg` (`tools/recortes.py`).
- Música y efectos: sintetizados desde cero en `tools/audio.py` (sin samples de terceros).
- Fuente: Inter (SIL OFL), incluida en `public/fonts`.

Para usar **clips de trabajos reales**, coloca los videos en `public/clips/` y sustituye los `<Img>` de las pantallas
(monitor, tarjeta de S3, teléfono, reel) por `<OffthreadVideo src={staticFile('clips/…')} />`.
