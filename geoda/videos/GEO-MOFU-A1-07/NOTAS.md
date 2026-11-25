# GEO-MOFU-A1-07 · Faceless '3 errores' · v1

- Formato: motion graphics, todo animado con Python (`mg.py`), sin personas ni IA de imagen. Fondo claro con manchas que se
  mueven y burbujas que suben todo el tiempo (ninguna escena queda quieta: diferencia media entre cuadros ≥ 3,5 en todas).
- Producto: recorte REAL de la landing (etiqueta real) en todas las escenas; B9 = clip real del kit (`k_tapa`).
- Voz: narradora Valeria (Gemini TTS Zephyr), una sola toma, 13 frases verificadas con STT.
- Escenas: HA 3 X rojas caen alrededor de la piedra (no tapan la etiqueta) · HB alarma roja · B1 piedra seca raspando el brazo
  con chispas (sin marca en la piel) · B2 gotas solo en la piedra · B3 calendario con días en rojo · B4 comentario de foro
  parafraseado (sin cliente ni marca) · B5 calendario completo + confeti · B6 piedra mojada bajo la ducha · B7 grieta animada ·
  B8 4 pasos (el 4 es el producto real tapado) · B9 video real · B10 sello 14 días de garantía · B11 GEODA + frascos tachados.
- CTA K7: '1 PIEDRA = 1 AÑO' / 'Ahorra vs. desodorante' (sin precio). Solo un CTA en el brief → hooks A y B.
- Duración: HA 34,7 s · HB 35,2 s (MOFU 30-51). Sin rótulo IA.
- Arreglo de voz: Gemini TTS ahora devuelve un WAV completo; `tts_multi.py` lo leía como PCM crudo y dejaba un clic al inicio de
  la toma y un "pop" de ~0,15 s al final. Corregido en la herramienta; aquí se limpiaron HA_t (clic) y B11_t (pop).
- Costo: US$0 (sin Higgsfield; voz gratis).

Montaje: `python3 mg.py todas durs.json && python3 mg.py sfx && python3 build.py`
