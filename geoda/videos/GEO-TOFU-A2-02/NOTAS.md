# GEO-TOFU-A2-02 · Estilo Pixar (3D) · v1

- NO PUBLICAR hasta que Alberto confirme el alcance del registro sanitario (ángulo A2, brief). Personajes estilizados, sin
  antes/después, frascos genéricos sin marca, sin 'blanquear'/'aclarar'.
- Personajes (`kit/personajes/pixar/`): Geo = piedra de alumbre translúcida, diseñada con las fotos reales del producto como
  referencia (misma forma y color), ojos grandes y SIN BOCA; Valentina (M, 25). Frascos con cara.
- Voces (Gemini TTS, todas con gemini-3.8-flash-lite-tts): narrador Charon (H), frasco Fenrir, Geo Puck, Valentina Leda.
  B8 (Navidad) se regrabó: decía "Regálalas". Cuota de TTS: si sale 429, reintentar cada ~75 s (no cambiar de modelo).
- Labios: Geo no tiene boca y Valentina va en voz en off (no mueve la boca); el único que mueve la boca es el frasco de B2,
  que es quien grita "¡Más fragancia!".
- 4 versiones (x1,12), un hook distinto cada una:
  - HA (K2 Navidad): frascos con cara de guerra disparan nubes de perfume (32,2 s).
  - HB (K2): Valentina, de frente, pega los brazos al cuerpo, avergonzada (31,2 s).
  - HC (K3 Llévala hoy, hook nuevo): los frascos esconden un secreto (un cajón que brilla) (28,2 s).
  - HD (K3, hook nuevo): "Alerta en el baño": los frascos se esconden de una luz que entra por la puerta (28,6 s).
- Producto REAL: B7 (clip real del kit en la mano, 2 s) y los cierres. Navidad: fondo real de sala con árbol (Kling, cámara
  quieta, en ida y vuelta) + producto real compuesto con `tools/endcard_anim.py` + moño rojo sobre la tapa
  (`kit/producto/mono_rojo.png`). K3: `endcard_bano_anim.mp4`.
- Subtítulos fijos (sub_y) en B2, B5 y B6 para no tapar la cara del frasco ni a Geo (Geo es la piedra).
- Costo: 15 imágenes (US$0,78) + 50 s de Kling (US$3,57) = US$4,35. Voz gratis.
