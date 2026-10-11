# Sonido: voz, música y SFX

## Medir la referencia

`analyze_reference.py --separate` da:

- `lufs_integrado`;
- `capas.voz_presente`;
- `capas.musica_bajo_voz_db` (cuánto está la música por debajo de la voz);
- `capas.sfx_candidatos_t` (golpes percusivos en la pista sin voz);
- `capas.cortes_con_sfx_%` (cuántos cortes visuales llevan sonido).

Escucha también los SFX extraídos (`reference_audio.py sfx`) para saber qué tipo de efecto es: whoosh, golpe, pop, clic, riser, glitch, ding.

Una referencia sin voz ni música no es un error: algunos formatos solo llevan música (formato 5) o solo voz.

## Música

- **«La misma música»:**
  ```bash
  python3 scripts/reference_audio.py separate ref.mp4 sep/                      # vocals.wav / no_vocals.wav
  python3 scripts/reference_audio.py music sep/htdemucs/ref/no_vocals.wav public/audio/musica.wav --duration 45
  ```
  - Por defecto se queda con la parte **armónica** (sin los golpes y whooshes que la referencia mezcló encima) y la repite en bucle con fundidos de 1 s.
  - Ajusta `--start` y `--end` para tomar el tramo más limpio (mira el espectrograma con `ffmpeg -lavfi showspectrumpic`).
  - Si la música de la referencia es muy corta, se repetirá mucho: díselo al usuario.
  - `htdemucs_ft` separa mejor pero tarda unas 4 veces más.
- **Música nueva:** la elige o aporta el usuario. Iguala tempo y carácter medidos (BPM, notas dominantes, instrumentación).
- **Nivel:** iguala `musica_bajo_voz_db` con ±3 dB, controlado con el `volume` de `<Audio>` en `Main.tsx`, con fundido de entrada de ~0.6 s y de salida en el cierre. Comprueba en el render: `ffmpeg -ss <pausa> -t 0.4 -i out.mp4 -af volumedetect -f null -` en una pausa frente a un tramo con voz.

## SFX

- **Biblioteca:**
  - `ref_*`: los de la referencia, recortados con `reference_audio.py sfx`. Los primeros que debes probar, porque son los suyos.
  - Sintéticos de `synth_sfx.py`: tick, boom, blip, pop, click, swipe, whoosh, whoosh_long, riser, scribble, sand, glitch, type, shimmer.
  - Remotion: `https://remotion.media/{whoosh,whip,page-turn,switch,mouse-click,ding,shutter-modern,…}.wav` (descárgalos a `public/sfx`).
- **Dónde ponerlos:** según la densidad medida.
  - Con `cortes_con_sfx_%` alto: en cada transición, en la entrada de cada objeto y en cada palabra clave.
  - Con densidad baja: solo en transiciones y en el golpe principal.
  - Si el usuario pide «efectos en cada palabra destacada», hazlo aunque la referencia sea más sobria y anótalo como desviación.
- **Asignación típica:**

  | Evento | Efecto |
  |---|---|
  | entra un objeto | whoosh |
  | palabra clave | pop o golpe suave |
  | transición de empuje o whip | whoosh de transición |
  | iris o corte a negro | impacto |
  | notificación | blip |
  | deslizar | swipe |
  | tachar | scribble |
  | disolver | sand |
  | momento clave emocional | boom |
  | tiempo | tic-tac |

- **Volúmenes:** 0.3–0.8. Los SFX deben oírse sin tapar la voz. Varía el volumen y el tipo para que no suenen repetitivos. Usa `note` en `data/sfx.ts` para saber por qué está cada uno.
- **Sincronía:** el SFX empieza en el frame del evento visual. Para whooshes de transición, adelántalo 0.05–0.1 s.

## Mezcla final

```bash
bash scripts/finalize.sh out/v1.mp4 ../render/borrador_v1.mp4 -14
```

- Normaliza a −14 LUFS (redes; usa −16 para YouTube largo si la referencia es más baja) y limita el pico real a ≈ −1.4 dBFS sin recodificar el vídeo.
- Si el archivo pasa de 30 MB, crea `_preview.mp4` para enviarlo.
