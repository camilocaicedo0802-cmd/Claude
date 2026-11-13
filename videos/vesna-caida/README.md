# La azafata que cayó 10.000 metros sin paracaídas — reel animado

Segundo short del canal, hecho con la misma base que `../cadaver-hitler` (Remotion + Edge TTS):
fondos 3D estilizados + personajes 2D, cámara en movimiento, transiciones de latigazo y subtítulos
de 1–2 palabras (los énfasis salen en MAYÚSCULAS y amarillo).

## Voz con más entonación

- Voz `es-US-AlonsoNeural`: entre 9 voces masculinas en español fue la de mayor variación de tono
  con acento latino neutro.
- El guion está partido en 27 frases, cada una con su velocidad, tono, volumen y pausa
  (`scripts/tts.py`): las exclamaciones suben hasta +30 Hz, el suspenso baja a −10 Hz y se ralentiza.
- `VISIBLE` en `scripts/tts.py` decide cómo se escriben en pantalla palabras que la voz lee distinto
  ("diez mil" → "10.000", "bum" → "¡BOOM!").

## Piezas

| Pieza | Archivo |
|---|---|
| Narración y tiempos por palabra | `public/voz.wav`, `public/voz-palabras.json` (`python3 scripts/tts.py`) |
| Fondos 3D | `public/fondos/*.jpg` (Higgsfield Z Image; `ceremonia` y `tribunal` vienen del short anterior) |
| Música y efectos | `python3 scripts/sonidos.py --duracion-musica 72` (no se suben al repo) |
| Personajes (Vesna, compañera, oficinista, médico, jueces, enfermera) | `src/componentes/Personaje.tsx` |
| Utilería del vuelo (carrito con cara, avión que se parte, cronómetro, ficha RPG, certificado…) | `src/componentes/Vuelo.tsx` |
| Las 29 tomas | `src/escenas/Historia.tsx` |

## Comandos

```bash
npm install
pip install edge-tts numpy
python3 scripts/sonidos.py --duracion-musica 72
npm run render:completo     # out/completo-final.mp4 (audio a -14 LUFS)
```
