# El cadáver que engañó a Hitler — reel animado

Reel vertical (1080×1920, 30 fps) hecho con **Remotion** y narrado con **Edge TTS**, en el estilo del
video de referencia: fondos 3D estilizados + personajes 2D de cabeza redonda dibujados encima,
cámara siempre en movimiento, transiciones de latigazo y subtítulos de 1–2 palabras.

## Cómo se arma

| Pieza | Archivo | Cómo se genera |
|---|---|---|
| Narración + tiempos de cada palabra | `public/voz.wav`, `public/voz-palabras.json` | `python3 scripts/tts.py` (Edge TTS, frase por frase con su propio ritmo/tono) |
| Fondos 3D | `public/fondos/*.jpg` | Higgsfield, modelo Z Image (0,15 créditos c/u) |
| Música y efectos | `public/musica.wav`, `public/sfx/` | `python3 scripts/sonidos.py` (sintetizados por código, sin derechos) |
| Personajes | `src/componentes/Personaje.tsx` | SVG animado: Hitler, Montagu, Cholmondeley, el espía muerto, soldado |
| Cámara y transiciones | `src/componentes/Toma.tsx` | — |
| Subtítulos | `src/componentes/Subtitulos.tsx` | salen solos de `voz-palabras.json` |

## Comandos

```bash
npm install
pip install edge-tts numpy
python3 scripts/sonidos.py          # música + efectos (no se suben al repo)
npm run studio                      # vista previa interactiva
npm run render:muestra              # out/muestra.mp4 y out/muestra-final.mp4 (audio a -14 LUFS)
```

En la nube de Claude Code, Edge TTS necesita `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt`.
