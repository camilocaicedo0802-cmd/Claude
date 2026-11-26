# GEO-TOFU-A2-03 · "Testimonio" → recreación con creadora IA (Daniela) · v1

- El brief dice: testimonio solo con persona real y autorización escrita; si se hace con IA deja de ser testimonio y se
  rotula como recreación. Aquí es una creadora IA contando "mi rutina" en primera persona, sin prometer tiempos ni resultados
  ("para mí", "cada piel es distinta"). Sin rótulo en el video (regla de Camilo): al publicar, activar la etiqueta de IA y
  no presentarla como clienta real. Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario.
- Voz: Gemini TTS Callirrhoe, todas las frases con gemini-3.1-flash-tts-preview (el modelo lite y el 3.8 llegaron al límite
  diario ese día). B1 ("a la carrera") y B9 ("GEODA" sonaba "Giuda") regrabadas con el mismo modelo.
- Habla a cámara (HA, HC, B1, B2, B3): Wan 2.7 image-to-video con `audio_url` = la frase de la voz (rellenada al largo del
  clip) → los labios siguen exactamente la voz, que es la misma en todo el video. El resto: voz en off sin labios.
- 4 versiones (sin acelerar), un hook distinto cada una:
  - HA (K6 Envío a toda Colombia): levanta el brazo y dice "Esta es mi rutina…" (30,7 s).
  - HB (K6): la cuchilla cae al lavamanos en cámara lenta (tramo real de la caída, interpolado). El hook ya dice "me rasuraba,
    me ardía": sin B1 (28,3 s).
  - HC (K2 Navidad, hook nuevo): junto al árbol, "Mi regalo de Navidad para mí: dejar de esconder los brazos" (32,3 s).
  - HD (K2, hook nuevo): abre el botiquín casi vacío, "Esto es lo que hay en mi baño ahora" (30,6 s).
- Pasos 1-2-3 con números grandes; el "2" va fijo arriba a la izquierda (`big_y`, nuevo en el montador) para no tapar
  ni la cara ni la piedra.
- Cierre K6: mapa de Colombia con pines que se encienden y un camioncito que recorre la ruta + producto REAL (`mapa.py`).
  K2: cierre de Navidad del A2-02 (producto real + moño).
- Costo: 13 imágenes (US$0,70) + 17 s de Wan 2.7 (US$1,28) + 20 s de Kling (US$1,43) = US$3,40. Voz gratis.
