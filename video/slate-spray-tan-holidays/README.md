# SLATE · Spray Tan Holidays (reel 9:16)

Reel vertical (1080×1920, 30 fps, 22,6 s) para SLATE Tulsa: reservas de spray tan para Thanksgiving,
fiestas de Navidad y Año Nuevo. Mantiene la línea gráfica de `slate-blueberry-boost` y toma de la
referencia (reel inmobiliario de 40 s) su dinamismo: cortes cada ~1 s, transiciones con zoom-blur,
tarjetas de vidrio esmerilado y tipografía grande cinética. **Sin emojis en pantalla** (pedido de la clienta).

Depende de `../slate-blueberry-boost/edit/engine.py` (copiarlo junto a `st_engine.py`).

## Guion → escenas

| Escena | Tiempo | Voz | Pantalla | Imagen |
| --- | --- | --- | --- | --- |
| 1 Hook | 0–3,2 s | "If you live in Tulsa and love a good spray tan, this one's for you." | Píldora de vidrio "TULSA, OK" desde el primer cuadro · "SPRAY TAN LOVERS, / *this is for you!*" | Línea de bronceado → aplicación → ella frente a SLATE |
| 2 Holidays | 3,2–8,05 s | "Thanksgiving's only a week away, then we're heading straight into Christmas parties and New Year's." | "THANKSGIVING" (hojas otoñales) · "CHRISTMAS / *parties*" (nieve y bokeh cálido) · "NEW YEAR'S" (confeti dorado), cada uno en su palabra | Ella en recepción, aplicación, resultados |
| 3 Tip | 8,05–14,55 s | "And remember to make sure you book your spray tan two days in advance before your event, your tan has time to fully develop." | "SPRAY TAN TIP" · "BOOK" · **"2 DAYS BEFORE"** · *your event* · calendario de vidrio (evento 20, reservar 18, flecha "2 DAYS") · "fully / *developed.*" | Ella en el banco, aplicación, resultado final |
| 4 Cierre | 14,55–22,6 s | "Holiday appointments are booking up fast, so make sure to book your appointment to get your holiday glow." | "HOLIDAY SPOTS / *are filling up!*" · "BOOK YOUR / *holiday glow*" · tarjeta SLATE "Book your holiday glow / SLATE TULSA" | Mejores resultados, cortes rápidos |

## Audio

- Voz: 6 tomas en crudo (IMG_7055–7063), una por frase; el "and" murmurado antes de "then we're heading"
  se dejó como pausa (`VOICE_MUTE`). Voz a −15 LUFS antes del master; master −13,9 LUFS, pico −1,7 dBFS.
- Música: pista original moderna y femenina con un toque navideño sutil (ElevenLabs Music v2.5 vía
  Higgsfield, 117 BPM), ~12 LU por debajo de la voz; arranca en el primer beat.
- SFX sutiles en cada cambio de texto o festividad: sparkle/ding/ting (extraídos del primer reel de
  referencia) y whoosh/pop sintetizados (`synth_sfx.py`).

## Render

```bash
export STDIR=/ruta/st FONT_DIR=/ruta/fonts      # STDIR con raw/ (contenido en crudo) y b/ (b-roll de Drive)
python3 edit/st_render.py out/video_noaudio.mp4
python3 edit/st_mix.py sfx /ruta/music.wav out/mix.wav
ffmpeg -i out/mix.wav -af "volume=1.1dB,alimiter=limit=0.82:attack=2:release=60:level=disabled" out/mix_master.wav
ffmpeg -i out/video_noaudio.mp4 -i out/mix_master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest final.mp4
```
