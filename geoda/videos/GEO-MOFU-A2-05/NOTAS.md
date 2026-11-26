# GEO-MOFU-A2-05 · Diario de 14 días (selfie) · v1

> Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario.

- Mariana (M, ~26, Cali), avatar nueva: `kit/personajes/mariana/mariana_ref.png`. La misma persona y la misma voz los 14 días:
  voz en off Gemini TTS Callirrhoe (gemini-3.8-flash-lite-tts), una sola toma (la del CTA de Navidad se regrabó igual y quedó
  la original: la "en" de "reparte en Navidad" se funde en las dos). Ella nunca habla a cámara: labios cerrados en todos los
  tramos usados (revisado cuadro a cuadro).
- Guion del brief sin precio ("paga 2 y lleva 3", sin $99.990). Compliance A2: sin fotos de la axila, sensaciones y no
  resultados, "para mí" en primera persona, sin antes/después; brazos arriba solo en plano amplio en el parque.
- 4 versiones (40,8 / 37,8 / 43,8 / 43,6 s):
  - HA (K1 Black Friday): selfie con la piedra + sello rojo '0/14'.
  - HB (K1): la mano tacha el 1 del calendario con marcador rojo. Se quita la fila B1 ('Día uno' repetido).
  - HC (K2 Navidad, hook nuevo): "Me regalaron una piedra de alumbre y me puse un reto" — caja de regalo junto al árbol.
  - HD (K2, hook nuevo): "Mi hermana me retó…" — la hermana señala la piedra.
- Cuerpo: un plano por día (baño, bus, oficina, espejo, calle al sol, cama, mano que tapa la cámara) con el 'DÍA X' del brief;
  B2 mojar (kit); B10 calendario con 14 chulos rojos animado en local (`cal14.py`, el 14 se marca en vivo); B11 sale con blusa sin
  mangas; B12 brazos arriba en el parque (plano amplio); B13 sello 14 días + producto real; B14 cierre con producto real +
  etiqueta BLACK FRIDAY (o REGALO NAVIDAD) + botón Comprar.
- Encuadre: los hooks A y C se rehicieron con el celular más alto (pared libre arriba para el título). En las selfies del cuerpo,
  zoom anclado abajo para que el 'DÍA X' y el subtítulo queden bajo la barbilla (nunca sobre cara ni pelo). Siempre pantalla completa.
- QA: movimiento ≥ 2,9 en todos los planos, -14 LUFS, sin rótulo IA.
- Costo: 17 imágenes (US$1,09) + 80 s de Kling (US$5,71) = US$6,80. Voz gratis.

Montaje: `python3 build.py` (clips en assets.json → G/hf/*_0.mp4; `mg_b10.mp4` del A1-07 y `cta_*.mp4` del A1-08).
