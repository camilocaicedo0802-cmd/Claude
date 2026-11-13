# La Atlántida — contada por uno de sus habitantes

Tercer short del canal (Remotion + Edge TTS). Narrado en primera persona por un atlante, que
aparece en pantalla con la boca sincronizada a la voz.

## Novedades respecto a los anteriores

- **Fondos 100 % por código** (`src/escenarios/Escenarios.tsx`): 13 escenarios ilustrados en SVG,
  sin generación de imágenes ni costo — ciudad en anillos vista desde arriba, canales (normal,
  terremoto e inundada), terraza, palacio, tesoro, plaza, cielo/tormenta, tsunami, ciudad
  hundiéndose de noche, ruinas submarinas, estudio de Platón, mar profundo y libro antiguo.
- **Voz más natural** (`scripts/tts.py`, `es-MX-JorgeNeural`): frases completas, contrastes suaves,
  ritmo de narrador, respiraciones sutiles entre frases y una cadena de audio más cálida
  (EQ, de-esser, compresión suave y un leve ambiente de sala). La narración se verificó con
  Whisper (`faster-whisper`): la transcripción coincide con el guion.
- **Boca sincronizada**: `hablandoEn(f)` en `src/tiempos.ts` mueve la boca del narrador mientras suena una palabra.
- Personajes nuevos: atlante, rey, ciudadana, Poseidón y Platón (`src/componentes/Personaje.tsx`);
  utilería en `src/componentes/Atlantes.tsx`.

## Comandos

```bash
npm install
pip install edge-tts numpy
python3 scripts/sonidos.py --duracion-musica 75
npm run render:completo     # out/completo-final.mp4
```
