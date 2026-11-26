# GEO-MOFU-A2-06 · Comparación piedra vs frasco · v1

> Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario.

- Natalia (M, ~32, Bogotá), avatar nueva: `kit/personajes/natalia/natalia_ref.png`. Voz en off Gemini TTS Aoede
  (gemini-3.8-flash-lite-tts), una sola toma; labios cerrados donde sale. El guion es en primera persona de mujer ("blusa sin
  mangas"), por eso la voz es otra vez M (distinta a la del A2-05).
- Compliance: el frasco es un aerosol genérico SIN marca, logo ni texto; del frasco solo se dice lo verificable o lo que "me
  pasaba"; "experiencia mía"; sin precio (K1 sin $99.990); brazos solo en plano amplio.
- Cambios al guion: el hook B del brief repetía palabra por palabra las dos primeras filas → su voz pasa a "Frasco contra piedra.
  Te muestro la diferencia." En la versión A se quita la fila B7 ("Por eso yo cambié", ya está en el hook).
- 4 versiones (30,9 / 32,0 / 34,1 / 32,9 s):
  - HA (K8 Combo para regalar): el aerosol suelta su nube de perfume en cámara lenta junto a la piedra quieta.
  - HB (K8): pantalla partida roja/verde con 'VS' gigante (animación local).
  - HC (K1 Black Friday, hook nuevo): "Este Black Friday cambié el frasco por una piedra" — una mano saca el aerosol del estante y queda GEODA.
  - HD (K1, hook nuevo): "Lo que nadie te dice del desodorante en frasco" — Natalia compara los dos en la mano.
- Cuerpo: frasco con luz dura / piedra con luz suave / el aerosol que ya no suelta nada / piedra + calendario de 12 meses (local) /
  camiseta negra con rayas blancas / mojar (kit) / guarda el frasco en el cajón / plano amplio con blusa sin mangas / producto real
  en la mano + garantía / cierre: K8 tres GEODA reales (recortes reales) sobre el mesón, dos con moño rojo + botón Comprar
  (`mg206.py cta3`); K1 producto real + etiqueta BLACK FRIDAY + Comprar (del A1-08).
- QA: los planos de estudio (fondo liso) se veían quietos; se les dio más empuje de cámara y más animación a las piezas locales:
  movimiento ≥ 2,7 en todo el video. -14 LUFS, sin rótulo IA, ningún texto sobre la piedra o la etiqueta.
- Costo: 10 imágenes (US$0,58) + 45 s de Kling (US$3,21) = US$3,79. Voz gratis.

Montaje: `python3 build.py` (renderiza las piezas locales con mg206.py si faltan; clips en assets.json → G/hf/*_0.mp4).
