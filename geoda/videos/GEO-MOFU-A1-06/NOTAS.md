# GEO-MOFU-A1-06 · POV 'segunda oportunidad' · v2

- Voz: narrador Julián (Gemini TTS Zubenelgenubi, una sola toma). "la mojas" y "para la calle" se regrabaron con la misma voz
  (la primera toma decía "las mojas" y "pa' la calle").
- Planos: primera persona (manos, bus, tablero) + Julián en camiseta y al llegar a casa (en ese clip se usa solo el tramo con la
  boca cerrada). Producto real: lavamanos (recorte real) y estante con 3 unidades reales.
- CTA principal K4 'Últimas unidades del lote' (el brief dice usarlo solo si el inventario de verdad está bajo) + alterno K2 Navidad
  'Paga 2 lleva 3' sin precio (`build.py K2`).
- Ojo: en el hook A el brief repite la misma frase ("le diste una segunda oportunidad") en el hook y en el primer plano.
- Costo: 10 imágenes (US$0,53) + 15 s de Kling (US$1,07) = US$1,60. Voz gratis.

## v2 (regla nueva: el avatar siempre en video haciendo algo)
- Hook A: la mano saca la piedra del cajón y sale el polvo (Kling), reencuadrado para que los textos no tapen la piedra.
- Hook B: la cámara se acerca a la foto de la mamá y una mano endereza la esquina (Kling).
- B3: se pasa GEODA (tramo 0-1,5 s del clip, etiqueta de frente, cámara lenta interpolada).
- B7: llega a casa y cuelga la chaqueta de espaldas, estira el cuello con alivio (los clips de frente entreabrían la boca).
- Costo extra v2: 5 clips Kling de 3 s (US$1,07) + 1 imagen (US$0,05) = US$1,12. Total A1-06: US$2,72.

## v3 (solo el hook A: HA y HA_K2)
- "POV" dicho como una sola palabra en español ("pov"), no deletreado. Para Gemini TTS se escribe "Pob:" (con "Pov:" la "p"
  inicial salía débil y sonaba "of"/"uf"; con "POV" lo deletreaba "pi o vi"). Toma elegida por la señal: una sola sílaba y
  la "p" con su cierre y explosión. vo/HA_t.wav = toma nueva. El HB sigue en v2 (no dice POV).

## v4 (solo el hook A: HA y HA_K2)
- El brief repetía "le diste una segunda oportunidad" en el hook A y en el plano de la ducha. En la variante HA la frase queda
  solo en el hook; la ducha va sin voz (1,8 s con sonido de ducha) y se alargan lavamanos (3,2 s) y cierre (+0,6 s) para
  mantener 30 s (MOFU). Montaje: `build_ha.py`. El HB sigue en v2 (ahí la frase se dice una sola vez).

## v5 (solo el hook A: HA y HA_K2)
- Camilo: quitar la toma de la ducha que no dice nada. El HA pasa del cajón (hook) directo al agua en la piedra.
- Para no bajar de 30 s (MOFU) se alargan 0,2-0,3 s camisa, bus, tablero, llegada a casa y lavamanos, y +1,2 s el cierre.
  Principal 30,0 s · K2 31,1 s. El HB sigue en v2 (ahí la ducha sí lleva "Le diste una segunda oportunidad").
