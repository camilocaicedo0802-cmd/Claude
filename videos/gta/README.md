# GTA existe por un bug — Veredicto: real

Short vertical (1080×1920, 30 fps, ~59 s) hecho con Remotion, con personajes, carros y fondos dibujados por código.

## Marca y derechos

No se usa el logo ni el arte oficial del juego. El nombre «GRAND THEFT AUTO» se escribe con rotulación propia
(fuente Bowlby One, licencia SIL OFL, en `public/fuentes/bowlby-latin.woff2`), y la caja del juego, el mapa visto
desde arriba, los carros y el marcador son dibujos originales. El contexto real viene de los datos:
*Race'n'Chase* (nombre de trabajo), DMA Design en Dundee (1995), BMG Interactive (distribuidora) y la polémica
británica de 1997.

## Voz

- Google AI Studio (Gemini 2.5 Flash TTS), voz **Charon**, dirección por frase en `scripts/guion.py`.
- 3 tomas; se eligió la más expresiva (rango de tono 17,2 semitonos).
- `scripts/alinear.py --tempo 1.1` alinea con Whisper (alineación difusa) y recorta solo silencios reales.

## Piezas nuevas

- `src/componentes/Gamer.tsx`: monitor de tubo, mapa del juego visto desde arriba con carros y choques, marcador de
  estrellas y dinero, pantalla de código, el «bug» (un bicho), insecticida, botón de cancelar, máquina de escribir,
  celular de los 90, carro de lado, caja del juego y el nombre con rotulación propia.
- Fondos: `EscOficina90`, `EscCalleNoche`, `EscParlamento`.
- Efectos de sonido nuevos en `scripts/sonidos.py`: sirena, choque, derrape, motor y máquina de escribir.

## Generar

```bash
npm ci
python3 scripts/sonidos.py --duracion-musica 61
npx remotion render src/index.ts Completo out/completo.mp4
SOLO_AUDIO=1 npx remotion render src/index.ts Completo out/audio.wav --codec=wav
ffmpeg -i out/completo.mp4 -i out/audio.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le out/mux.mkv
bash scripts/masterizar.sh out/mux.mkv out/completo-final.mp4
```

Mezcla verificada: la voz queda por encima de efectos y música en todas las ventanas de 100 ms (margen mediano 26,3 dB);
máster a −14,2 LUFS, pico real −2,4 dBTP.
