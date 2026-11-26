# GEO-BOFU-A1-09 · Demo de producto (solo manos) · v1

- Pedido de Camilo (26-nov): el A1 tenía pocos BOFU → 3 BOFU extra (A1-09, A1-10, A1-11) con la estructura
  HOOK → PROBLEMA → PRODUCTO → SOLUCIÓN → CTA. Guiones en `brief_v2/guiones_bofu_extra.md`.
- Voz en off: narrador H, Gemini TTS Orus (gemini-3.8-flash-lite-tts), una sola toma. Ninguna cara en todo el video.
- 4 versiones (un hook distinto cada una):
  - HA (K5 contraentrega): pasa la piedra SECA por el antebrazo + sello 'SECA'. Solo el tramo 0,1-1,35 s del clip (después
    Kling pinta rastro blanco en la piel: la piedra no deja residuo), de ida y vuelta (20,2 s).
  - HB (K5): la mano está a punto de botar GEODA a la caneca y se arrepiente (20,1 s).
  - HC (K2 Navidad, hook nuevo): unas manos abren una caja de regalo con GEODA junto al árbol (19,5 s).
  - HD (K2, hook nuevo): GEODA sobre pizarra oscura con barrido de luz (el primer clip deformó la piedra; se rehízo con cámara fija) (19,0 s).
- Cuerpo: B1 oficina, el reloj marca las 3 p. m. y él despega la camisa de la axila (sin cara) · B2 foto REAL en la mano (Kling) ·
  B3 mojar (kit) / aplicar (solo 0,1-1,2 s) / secar (kit) · B4 la mano tapa la piedra (kit) ·
  B5 K5: domicilio (manos) + cierre con producto real, tarjeta 'PÍDELA HOY / La pagas cuando te llegue / Garantía 14 días';
  K2: producto real con moño junto al árbol (del A2-02), tarjeta 'REGALA GEODA EN NAVIDAD / Paga 2 lleva 3'.
- B5k2 se grabó en plural ("Regálalas… y las pagas cuando te lleguen"): se dejó así (va con Paga 2 lleva 3).
- QA: ningún texto sobre la piedra ni la etiqueta (cajas manuales), sin rótulo IA, -14 LUFS, movimiento ≥ 2,8 (cierre) y ≥ 4 en el resto.
- Costo: 7 imágenes (US$0,49) + 45 s de Kling (US$3,21) = US$3,70. Voz gratis.

Montaje: `python3 build.py` (clips en assets.json → G/hf/*_0.mp4; `xmas_ec_bow.mp4` sale del montaje del A2-02).
