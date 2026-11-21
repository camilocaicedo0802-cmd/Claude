# Vendió la Torre Eiffel (y quiso repetirlo) — sello: REAL

Short vertical (1080×1920, 30 fps, ~54 s) hecho con Remotion, con personajes y fondos dibujados por código.
Historia: Victor Lustig, 1925, la venta de la torre como chatarra, el soborno que convence y el «vendedor aprendiz»
de su certificado de defunción.

## Voz

- Narrador: Gemini 2.5 Flash TTS, voz Charon, tono de chisme cómplice. Citas: Enceladus (Lustig, susurro seguro, sin
  acento francés) y Kore (la esposa, seca y escéptica, la pregunta sube al final).
- Guion y dirección frase a frase en `scripts/guion.py`. Montaje por frases con pausas digitales exactas
  (`scripts/montar_largo.py`), alineación con Whisper (`scripts/alinear.py --sin-cortes`) y ajuste a los bordes del
  montaje (`scripts/ajustar_tiempos.py`).
- Medido: 199–204 palabras/min. Pausas: 0,28 s después de «Torre Éifel…», 0,56 s antes de «Y eso lo convence»,
  0,30 s antes de «y encima el soborno», 0,43 s después de «¿Y cómo terminó?», 0,32 s después de «pusieron:».
  Ningún otro silencio pasa de 0,2 s. «vendedor aprendiz» un 15 % más lento y nada después.
- Tomas elegidas archivadas en `tomas/` (FLAC).

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

Luego se une y se masteriza a −14 LUFS (pico real ≤ −1 dBTP) con ffmpeg (loudnorm en dos pasadas + limitador).
