# GEO-BOFU-A1-10 · UGC con avatar IA (Sara) · v1

- Avatar nueva: Sara (M, ~28, Medellín, pelo negro liso con flequillo, argollas doradas, blusa verde salvia),
  referencia `kit/personajes/sara/sara_ref.png`. Voz en off: Gemini TTS Despina (gemini-3.8-flash-lite-tts), una sola toma
  (alterna con el A1-09 y A1-11, que son voz H). Sara nunca habla a cámara: labios cerrados en todos los tramos usados
  (revisado cuadro a cuadro; se descartan B1 desde 3,1 s y B4 antes de 3,3 s porque abre la boca).
- Duración: el guion da ~26 s, así que todo el video va a 1,15x (imagen y voz juntas) → 19,7-23,1 s (BOFU 18-24).
- 4 versiones:
  - HA (K7 1 piedra = 1 año): escéptica mirando la piedra, se encoge de hombros y sonríe (23,0 s).
  - HB (K7): su hermana se ríe en la puerta del baño mientras ella se aplica (23,1 s).
  - HC (K3 'Pruébala hoy', hook nuevo): rutina de mañana en el cuarto, se abotona, toma la piedra del mueble y la muestra (20,6 s).
  - HD (K3, hook nuevo): la abuela le entrega la piedra en la cocina (19,7 s).
- Encuadre FR y SIEMPRE pantalla completa: el título va en la pared de arriba; HA, HB y HD con zoom anclado arriba (baja la
  cabeza sin fondo desenfocado); el HC se regeneró con la cabeza a media altura (s_hc2). B2: subtítulo abajo a la derecha.
- Cuerpo: B1 oficina (incómoda) + inserto del reloj de las 3 p. m. (del A1-09) · B2 muestra GEODA · B3 partida en dos filas
  ("Ahora la mojo," con el grifo del kit / "la paso por la axila limpia y la dejo secar" con el subtítulo fijo abajo a la
  derecha, lejos de la cara y de la piedra) · B4 llega a casa tranquila ·
  B5 K7: frascos genéricos tachados (A1-07) + cierre con producto real, tarjeta '1 PIEDRA = 1 AÑO / Garantía de 14 días';
  K3: cierre con producto real, tarjeta 'PRUÉBALA HOY / La pagas cuando te llegue'.
- Costo: 11 imágenes (US$0,87) + 45 s de Kling (US$3,21) = US$4,09. Voz gratis.

Montaje: `python3 build.py` (clips en assets.json; `mg_b11.mp4` sale de `videos/GEO-MOFU-A1-07/mg.py`).
