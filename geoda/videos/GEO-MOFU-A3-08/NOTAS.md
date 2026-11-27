# GEO-MOFU-A3-08 · Podcast "ranking de desodorantes" · v1 (video extra, modelado de un reel de referencia)

- Pedido de Camilo (27-nov): mismo formato del reel que compartió (presentadora en set de podcast que le pone nota a cada
  opción: tarjeta del producto + "X/10"; el producto héroe saca 10/10 y cierra con "si ves el botón aquí abajo…").
  Guion en `brief_v2/guion_a3_08_ranking.md`. Ángulo A3 (La piedra de verdad, no un frasco).
- Compliance: sin marcas de la competencia (aerosol, barra y roll-on genéricos, fotos sin texto ni logo); de ellos solo
  experiencia en primera persona; GEODA con claims permitidos (piedra mineral, sin perfume, ataca la bacteria que causa el
  olor y no lo tapa, se moja la piedra no la axila, no mancha la ropa, 1 piedra = 1 año, garantía 14 días). Sin precios ni
  "se agota el lote" (no hay dato de inventario).
- Presentadora (M, ~34) en set de podcast: `kit/personajes/ranking/set_presentadora.png`. Voz NATIVA de WAN 3.0 (labios
  sincronizados de origen) en 3 tomas (30 + 30 + 24 s); la 2 (242 Hz) y la 3 (213 Hz) igualadas al tono de la 1 (225 Hz)
  con rubberband, formantes conservados. Cada frase usa sus propios tramos; las pausas de más de 0,3 s se cortan con
  salto alternando plano abierto y acercamiento (como el original). Video a 1,2x (MOFU ≤ 51 s).
- Tarjetas (`tarjetas.py`): producto en tarjeta blanca + nota que entra cuando la dice (4/10 aerosol, 5/10 barra, 6/10
  roll-on, 10/10 GEODA en verde con destellos, recorte REAL del producto). GEODA real también en la mesita todo el video.
  En el cierre la nota cambia por el botón Comprar y una mano 👇.
- 4 versiones (44,2 / 48,8 / 48,6 / 48,6 s):
  - HA (K5 contraentrega + envío gratis): abre con la primera nota ("¿Desodorante en aerosol con perfume? Cuatro de diez.").
  - HB (K5): "Le puse nota a todos los desodorantes que he usado. Solo uno sacó diez."
  - HC (K2 Navidad): "Desodorantes, del peor al mejor. El último te va a sorprender."
  - HD (K2): "Probé de todo para el olor de las axilas. Esta es mi nota sincera."
- QA: -14 LUFS, textos fuera de la cara (subtítulos arriba, tarjetas abajo), producto real antes del segundo 10 y en el cierre.
- Costo: 3 imágenes (US$0,16) + 84 s de WAN 3.0 720p (US$6,30) = US$6,46.

Montaje: `python3 build.py` (tomas en assets.json → G/hf/wr_t*_0.mp4).

## v2 (Camilo: el título en la parte de arriba)
- El título del hook (2 líneas, 243-279 px de alto) no cabía en la primera posición y el montador lo bajaba a y≈285-555.
  Ahora cada hook lleva `hook_slots` calculado para que el bloque arranque justo en el borde superior de la zona segura
  (y = 254). Nada más cambia.
