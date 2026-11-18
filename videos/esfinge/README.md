# ¿Napoleón le voló la nariz a la Esfinge? — Veredicto: mito

Short vertical (1080×1920, 30 fps, ~64 s) hecho con Remotion, con personajes y fondos dibujados por código.

## Voz

- Google AI Studio (Gemini 2.5 Flash TTS), voz **Charon**, con dirección por frase en `scripts/guion.py`.
- Se generaron 3 tomas y se eligió la más expresiva (rango de tono 24,5 semitonos; el short de Napoleón tenía 16,2).
- `scripts/alinear.py --tempo 1.1` transcribe con Whisper, alinea con el guion (alineación difusa: acepta
  "esfinje" = "Esfinge" y dos palabras oídas juntas, como "pobrella" = "pobre ya"), recorta solo silencios reales
  y deja `public/voz.wav` + `public/voz-palabras.json`.

## Escenas

Gancho → la Esfinge ya chata → 1798, Napoleón llega con sus cañones → "¿quién más iba a ser?" →
la leyenda (soldados disparándole a la nariz, en sepia) → de guía en guía → "ya era el bajito" →
Norden la dibuja chata en 1737 → línea de tiempo (Napoleón nace en 1769) → el fanático de 1378 →
sentencia → la piedra de Rosetta → hoy está en Londres → veredicto: mito.

Utilería nueva en `src/componentes/Egipto.tsx` (Esfinge con o sin nariz, cañón, piedra de Rosetta, vitrina,
línea de tiempo…) y fondos en `src/escenarios/Escenarios.tsx` (`EscDesierto`, `EscMuseo`, `EscPergamino`).

## Generar

```bash
npm ci
python3 scripts/sonidos.py --duracion-musica 66
npx remotion render src/index.ts Completo out/completo.mp4
SOLO_AUDIO=1 npx remotion render src/index.ts Completo out/audio.wav --codec=wav
ffmpeg -i out/completo.mp4 -i out/audio.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le out/mux.mkv
bash scripts/masterizar.sh out/mux.mkv out/completo-final.mp4
```

Mezcla verificada: la voz queda por encima de efectos y música en todas las ventanas de 100 ms (margen mediano 26,9 dB);
máster a −14,1 LUFS integrados, pico real −2,0 dBTP.
