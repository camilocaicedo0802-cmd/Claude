# GEO-BOFU-A2-07 · UGC con avatar IA (Mariana) · v1

> Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario.

- Mariana, la del diario A2-05 (`kit/personajes/mariana/`): el guion sigue su historia (ya volvió a las blusas sin mangas).
  Voz en off con la regla 47: Gemini TTS **gemini-3.8-flash-tts** (versión completa), voz Callirrhoe, una sola toma con perfil
  expresivo (coqueta, cómplice, baja la voz en "mi secreto"). Sin cambiar tono ni velocidad. Mariana nunca habla a cámara:
  labios cerrados en los tramos usados (el hook A va en cámara lenta y corta antes de la carcajada; el hook D usa en ida y
  vuelta el tramo con sonrisas cerradas).
- Sin precios (CTA K8 combo para regalar; K2 Navidad). Rótulo IA: no (regla vigente: la plataforma lo marca al publicar).
- 4 versiones (18,8 / 18,3 / 24,0 / 23,0 s), nada se repite entre hook y cuerpo:
  - HA (K8): el clóset se abre de golpe y salen volando blusas sin mangas. Se quita B1.
  - HB (K8): tres GEODA reales caen una por una en la palma (animación local con el recorte real, `mg207.py palma`). Se quita B3.
  - HC (K2, hook nuevo): "¿Ya sabes qué regalarle a tus amigas esta Navidad? Yo sí." — envuelve tres GEODA de regalo junto al árbol.
  - HD (K2, hook nuevo): "Este diciembre vuelvo a las blusas sin mangas... y no voy sola." — con dos amigas en una reunión navideña. Se quita B1.
- Cuerpo: elige blusas en el clóset · selfie con GEODA y guiño (subtítulo en el pecho, lejos del pelo y de la piedra) · tres GEODA
  en abanico (local, fondo sin personas) · domicilio contraentrega (A1-09) · guiño con la blusa puesta (plano amplio) ·
  cierre K8: tres GEODA reales, dos con moño, botón Comprar (A2-06); K2: producto real + etiqueta REGALO NAVIDAD + Comprar (A1-08).
- QA: textos fuera de caras, pelo, piedra y etiqueta; -14 LUFS.
- Costo: 7 imágenes (US$0,43) + 30 s de Kling (US$2,14) = US$2,57. Voz gratis.

Montaje: `python3 build.py` (renderiza palma y abanico con mg207.py si faltan; clips en assets.json → G/hf/*_0.mp4).
