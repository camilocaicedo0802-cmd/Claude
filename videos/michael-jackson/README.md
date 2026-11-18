# ¿Napoleón era bajito? — el primer meme de la historia

Cuarto short del canal (Remotion + Edge TTS), con fondos dibujados por código y mezcla con la voz al frente.

## Voz calibrada por medición (`scripts/tts.py`)

Voz `es-US-PalomaNeural` (latina neutra). El guion pedía:

| Indicación | Objetivo | Resultado medido |
|---|---|---|
| Velocidad | ~3 palabras/s (≈183/min) | 2,99 palabras/s (180/min) |
| Gancho | ≈283 Hz | 279–293 Hz |
| Desarrollo (narradora) | ≈186 Hz | 180–188 Hz |
| Conflicto y preguntas | ≈248 Hz | 240–250 Hz |
| Pregunta final | la más fuerte | +3,4 dB sobre cualquier otra frase |

El script sintetiza cada frase, mide su tono (mediana de F0) y su duración, y corrige el
desplazamiento de tono por frase y la velocidad global hasta llegar al objetivo
(los parámetros finales quedan en `scripts/calibracion.json`). La pronunciación se verificó con Whisper.

## Piezas

- `src/escenarios/Escenarios.tsx`: tabla de estaturas (1 cm = 4,6 px; `altoParaCm` da el alto exacto
  de cada personaje), estudio del caricaturista en Londres, salón imperial, mapa de Europa,
  Santa Helena, pizarra, campo de la Guardia y el celular del "primer meme".
- `src/componentes/Napoleon.tsx`: marcas de altura, hoja de caricatura, pluma, periódicos volando,
  comparación de pulgadas, cinta métrica, corazones y lágrimas.
- Personajes nuevos en `src/componentes/Personaje.tsx`: Napoleón, caricaturista, caballero inglés,
  médico, granadero de la Guardia y el "francés promedio".
- `src/mezcla.ts`: efectos y música siempre por debajo de la voz (ducking automático).

## Comandos

```bash
npm install
pip install edge-tts numpy
python3 scripts/sonidos.py --duracion-musica 50
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 scripts/tts.py   # solo si cambias el guion
npm run render:completo
```
