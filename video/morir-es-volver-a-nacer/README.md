# ¿Y si morir es volver a nacer? — montaje por código

Documental de misterio (≈7:25) al estilo de la referencia: grano, viñeta, color cálido y desaturado, titulares
condensados con brillo rojo/amarillo, máquina de escribir roja, cajas de neón, anillos, cifras grandes y fotos enmarcadas.

- **Voz:** Gemini TTS (`gemini-3.8-flash-tts`, voz Charon) generada por bloques con `edit/tts.py`.
- **Material:** stock libre para monetizar (Mixkit Free License, Unsplash, NASA, dominio público de Wikimedia;
  2 grabados CC BY 4.0 de la Wellcome Collection). Inventario y licencias en `work/inventario_stock.json`.
- **Música:** banda sonora original sintetizada (`edit/score_mist.py`), sin muestras ni música de terceros.
- **Motor:** `engine.py`/`gfx.py`/`render.py` + estilo propio `mist.py`; línea de tiempo en `timeline.py`, anclada a
  las palabras de la locución (`work/words.json`, faster-whisper).
- **Mezcla:** `mix.py` (voz −14 LUFS final, música con ducking ≈ −33 LUFS, efectos ≈ −35 LUFS).
- **Extras:** `thumbs_mist.py` (3 miniaturas), `shorts.py` (3 shorts 9:16 con subtítulos), `covers.py` (portadas).

Los medios (videos, audio, imágenes) no se guardan en el repositorio.
