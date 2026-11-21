# Vendió la Torre Eiffel (y quiso repetirlo) — sello: REAL

Short vertical (1080×1920, 30 fps, ~63 s) hecho con Remotion, con personajes y fondos dibujados por código.
Historia: Victor Lustig, 1925, la venta de la torre como chatarra, el soborno que convence y el «vendedor aprendiz»
de su certificado de defunción.

## Voz

- Narrador: Gemini 2.5 Flash TTS, voz Charon, tono de chisme cómplice. Citas: Enceladus (Lustig, susurro seguro, sin
  acento francés) y Kore (la esposa, seca y escéptica, la pregunta sube al final).
- Voz natural, como el short de Napoleón (`scripts/montar_natural.py`): la toma del narrador queda **continua** (no se
  corta por frases ni se estira); solo se insertan las citas en las pausas que deja después de los dos puntos y se
  ajustan las pausas dentro de los silencios reales. Luego `scripts/alinear.py --sin-cortes --tempo 1.12` acelera
  apenas un 12 % con atempo, procesa la voz y saca los tiempos por palabra con Whisper.
  (La primera versión se armaba frase por frase y se aceleraba un 33 % con rubberband: sonaba robótica.)
- Medido (silencio real a −35 dB): 0,29 s después de «Torre Éifel…», 0,48 s antes de «Y eso lo convence», 0,27 s antes
  de «y encima el soborno», 0,39 s después de «¿Y cómo terminó?», 0,26 s después de «pusieron:»; ninguna otra pausa
  pasa de 0,21 s. Whisper reconoce el 98 % del guion. Duración de la voz: 62,1 s (158 palabras/min con pausas).
- Tomas elegidas archivadas en `tomas/` (FLAC): narrador `cap0_1`, Lustig `lustig_1` y `lustig2_1`, esposa `esposa_2`
  (la `esposa_1` decía «estasa»; la 2 dice «estafa» claro y la pregunta sube al final).
- `scripts/voz_una_toma.py` pide a Gemini todo el guion en una sola toma (el narrador actúa también las citas), para
  cuando haya cuota.

## Música y efectos

- `scripts/musette.py`: vals musette propio (acordeón de dos lengüetas, bajo y guitarra en 3/4, la menor). Se corta en
  la pausa del giro, vuelve en «Y eso lo convence», se detiene en «¿Y cómo terminó?» y regresa suave para el final.
- Efectos sintetizados: silbato, tren, chatarra, «shh», suspiro, más los comunes (sello, latigazo, ding, sobres…).
- Mezcla en `src/mezcla.ts`: música con ducking mientras habla la voz.

## Imagen

- Escenas en `src/escenas/Short.tsx`; utilería y vestuario en `src/escenas/utileria_eiffel.tsx`.
- Sin cortes secos: latigazos y zooms. Sello «REAL» en el último segundo; el último encuadre repite el primero.
- Portadas verticales en `src/Portadas.tsx` (textos dentro de y = 260…1650).

## Render

```bash
npx remotion render src/index.ts Completo out/video.mp4 --muted
SOLO_AUDIO=1 npx remotion render src/index.ts Completo out/audio.wav --codec=wav
```

Luego se une y se masteriza con ffmpeg (loudnorm en dos pasadas + limitador). Medido en `out/eiffel-final.mp4`:
−14,1 LUFS, pico real −2,4 dBTP; la música queda 20 dB bajo la voz (mediana mientras se habla); sin cortes secos
ni cuadros negros; Whisper reconoce el 97 % del guion sobre la mezcla.
