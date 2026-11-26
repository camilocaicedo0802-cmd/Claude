# GEO-TOFU-A2-04 · Podcast (host + invitada, dos mujeres) · v1

- NO PUBLICAR hasta que Alberto confirme el registro sanitario (ángulo A2). Sin 'aclara'/'blanquea', sin explicaciones médicas.
- Voces NATIVAS de WAN 3.0 (voz y labios salen juntos → sincronía de origen, revisada con `pipeline/tools/lips_strip.py`):
  invitada en 2 tomas (30 s con el hook A/B y todo el cuerpo; 24 s con los dos cierres y los hooks C/D) y host en 1 toma
  (15 s). La toma 2 de la invitada salió un 9 % más aguda (210 vs 192 Hz): se baja con rubberband (formantes conservados,
  no cambia los tiempos → los labios siguen sincronizados). Personajes en `kit/personajes/podcast2/`.
- Cada frase usa su tramo del clip (plano y audio del mismo momento); frases verificadas transcribiéndolas solas.
  "rasurada a la carrera" se oye con las dos "a" unidas (sinalefa normal del habla).
- 4 versiones (36,6-38,2 s), un hook distinto cada una:
  - HA (K1 Black Friday, sin precio): "Yo cambié tres cosas…" empujando los tres objetos.
  - HB (K1): "Perfume, rasurada a la carrera y ropa apretada. Ese era mi combo." (título: mi combo fatal).
  - HC (K2 Navidad, hook nuevo): saca un regalo rojo: "Este año voy a regalar lo que me cambió la rutina."
  - HD (K2, hook nuevo): en primer plano, cerca del micrófono: "Lo que nadie me cree de mi rutina de axilas."
- Pasos 1-2-3 con número grande. Cierres: K1 = producto real + etiqueta BLACK FRIDAY + botón Comprar (A1-08);
  K2 = producto real en la mesa de Navidad con moño (A2-02).
- Costo: 3 imágenes (US$0,21) + 69 s de WAN 3.0 (US$5,18) = US$5,39.
- HD (primer plano de la toma 2): título más compacto y arriba (hook_slots 356, hook_maxw 680) y zoom anclado arriba
  (1,26-1,29) para que la cabeza baje y quede espacio libre entre el título y el pelo.

## v2 (Camilo: a 1,2x)
- Video a 1,2x (imagen y voz juntas; la voz conserva el tono, los labios siguen sincronizados): 30,5-31,8 s.
- Voces con filtro paso alto (90 Hz) y limitador suave: la toma 2 de la invitada traía un golpe de micrófono (plosiva
  saturada) en "de mi rutina" del hook D que a 1,2x se notaba como un "pop".
