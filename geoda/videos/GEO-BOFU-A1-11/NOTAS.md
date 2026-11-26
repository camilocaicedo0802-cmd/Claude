# GEO-BOFU-A1-11 · Faceless / motion graphics · v1

- Voz en off: narrador H, Gemini TTS Iapetus (gemini-3.8-flash-lite-tts), una sola toma; B5 regrabada con la misma voz y
  modelo ("Te la enviamos", sonaba "Te lo"). B5k1 quedó en plural ("las pagas cuando te lleguen"): se dejó así (Paga 2 lleva 3).
- Todo animado en local (`mg11.py`, reutiliza las piezas de `videos/GEO-MOFU-A1-07/mg.py`): fondo con burbujas siempre en
  movimiento y el producto es el recorte REAL.
- 4 versiones:
  - HA (K6 envío gratis): frascos genéricos entran y una señal de PARE los frena junto a GEODA (23,4 s).
  - HB (K6): X roja sobre la piedra que se cae y se vuelve ✓ verde (22,3 s).
  - HC (K1 Black Friday, hook nuevo): fondo oscuro, cae la etiqueta BLACK FRIDAY y llueve confeti (22,6 s).
  - HD (K1, hook nuevo): calendario que corre del 26 al 30 de noviembre + etiqueta BF (22,5 s).
- Cuerpo: B1 problema en 3 cortes (seca: raspa con chispas / guardada mojada en la ducha / se agrieta) · B2 producto con brillo ·
  B3 los 4 pasos · B4 sello de garantía 14 días · B5 K6: mapa de Colombia con pines y camión (del A2-03), tarjeta
  'ENVÍO GRATIS A TODA COLOMBIA / La pagas al recibir'; K1: producto real + etiqueta BLACK FRIDAY + botón Comprar (del A1-08).
- Costo: US$0 (animación local + voz gratis).

Montaje: `python3 build.py` (renderiza las escenas con mg11.py si faltan; `cta_mapa.mp4` y `cta_bf.mp4` salen del A2-03 y A1-08).
