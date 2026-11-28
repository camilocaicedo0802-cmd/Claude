# La llave del Titanic — veredicto: MEDIO MITO

Short vertical (1080×1920, 30 fps, ~58 s) hecho con Remotion, con personajes y fondos dibujados por código.
Historia: al oficial al que dejan en tierra antes de zarpar se le va en el bolsillo la llave del armario de los
prismáticos; el vigía ve el iceberg a 37 segundos; pero en el puente sí había prismáticos, la noche era sin luna, el mar
un espejo sin espuma, hubo seis avisos de hielo y no frenaron.

## Cuidados

- Es una tragedia real: no se muestra el choque ni a ninguna víctima; el hundimiento solo aparece como titular de
  periódico, y la música de esa parte es un piano sobrio.
- Música y efectos sintetizados y de composición propia (sin grabaciones ni música de las películas).

## Voz

- Narrador: Gemini 2.5 Flash TTS, voz Charon, en **una sola toma** como el short de Napoleón: él mismo actúa las citas
  (la pregunta de la audiencia, la respuesta del vigía y la carta del oficial). `scripts/voz_una_toma.py` toma la
  dirección frase a frase de `scripts/guion.py`.
- Se generaron 3 tomas; la elegida (`tomas/toma_2.flac`) es la más expresiva (12,5 semitonos de rango frente a 7–8 de
  las otras) y Whisper medium la transcribe completa y exacta.
- `scripts/montar_natural.py --tempo 1.10` deja la toma continua y solo ajusta las pausas dentro de los silencios
  reales; luego `scripts/alinear.py --sin-cortes --tempo 1.10` acelera un 10 % con atempo y saca los tiempos por palabra.
- Pausas marcadas (silencio real a −35 dB): 0,92 s antes de «No.» y 0,90 s antes de «era el único que no iba en el
  barco»; las demás quedan naturales (0,4–0,5 s, como en Napoleón). Números dichos en palabras y mostrados en cifras en
  los subtítulos (14, 11:40, ¡37).

## Música y efectos (`scripts/oceano.py`)

- Misterio marino en re menor y 6/8 (bordón de cuerdas y arpa); desde el iceberg entra un pulso que sube la tensión; se
  corta después de «¿Y frenaron?» (silencio para el «No.»); piano melancólico para la carta; se detiene en la pausa de
  «el único que tenía la llave…» y cierra con un acorde para el veredicto.
- Efectos nuevos: campana de la cofa (tres toques), telégrafo Morse y bocina de barco; más los comunes.

## Imagen

- Escenas en `src/escenas/Short.tsx`; utilería y vestuario en `src/escenas/utileria_titanic.tsx` (el Titanic de
  perfil, iceberg, cofa con campana, armario de prismáticos y su llave, muelle, puente, indicador de nudos, sala de la
  audiencia de 1912, marconigramas, carta y cuenta atrás).
- Sin cortes secos: latigazos, zooms y un fundido. Sello «MEDIO MITO» con la palabra «mito», en el último segundo.
- Portadas verticales en `src/Portadas.tsx` (textos dentro de y = 260…1650).

## Render

```bash
python3 scripts/oceano.py
npx remotion render src/index.ts Completo out/video.mp4 --muted
SOLO_AUDIO=1 npx remotion render src/index.ts Completo out/audio.wav --codec=wav
```

Luego se une y se masteriza con ffmpeg (loudnorm en dos pasadas + limitador) a −14 LUFS.
