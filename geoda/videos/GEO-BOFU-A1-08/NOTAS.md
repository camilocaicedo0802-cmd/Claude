# GEO-BOFU-A1-08 · UGC con avatar IA (Mateo) · v1

- Avatar: Mateo (H, ~30, Colombia), referencia `kit/personajes/mateo/mateo_ref.png`. El brief dice "la avatar"; se hizo hombre
  para alternar voces entre videos (A1-07 fue mujer). Voz en off: Gemini TTS Fenrir, una sola toma; B5 ("o para regalar") y
  B6 ("Es Black Friday", sonaba "is") se regrabaron con la misma voz. Mateo nunca habla a cámara (labios cerrados).
- Sin precios: "Paga 2 y lleva 3 por $99.990" → "Paga dos y lleva tres"; tarjeta 'BLACK FRIDAY / Paga 2 lleva 3'.
- 4 versiones, un hook distinto cada una:
  - HA (K1 Black Friday): Mateo guarda billetes en la billetera + sello '14 DÍAS'. El hook ya dice la garantía, así que en esta
    versión se quita el plano del calendario (B2) para no repetir (20,3 s).
  - HB (K1): Mateo le da un beso a la piedra y la muestra a cámara (21,0 s).
  - HC (K2 Navidad, hook nuevo): abre un regalo de Navidad y saca la piedra, escéptico, y sonríe (22,5 s).
  - HD (K2 Navidad, hook nuevo): está a punto de botar la piedra a la basura y se arrepiente (21,8 s).
- Cuerpo: B1 montaje mojar (kit) / aplicar (Mateo, solo 0,1-1,0 s: después aparece brillo en la piel) / secar (kit) ·
  B2 señala el 14 en el calendario · B3 el domiciliario le entrega la caja · B4 tres GEODA en la mano · B5 reparte a dos amigos ·
  B6 cierre con producto REAL (endcard animado) + etiqueta colgante BLACK FRIDAY (o REGALO NAVIDAD) + botón Comprar con toques (`cta.py`).
- Movimiento medido en todos los planos (≥ 3,1). Sin rótulo IA. Sin clics de voz.
- Costo: 10 imágenes (US$0,735) + 39 s de Kling (US$2,785) = US$3,52. Voz gratis.

Montaje: `python3 cta.py bf 5.6 && python3 cta.py navidad 6.6 && python3 build.py` (clips de Higgsfield en assets.json → G/hf/k_*_0.mp4).

## v2 (Camilo: ningún título puede tapar la cara)
- Los 4 hooks se rehicieron en plano abierto: imagen con "el 40 % de arriba vacío (pared/techo)" y Kling con cámara fija
  (prompt FRAMING en assets.json, n_*). El título va arriba en la pared; la cabeza de Mateo queda en el centro del cuadro.
- Hook A: el sello '14 DÍAS' pasa entre el título y la cabeza.
- Cajas manuales de cabeza (con pelo) y producto en todos los planos con personas: el detector automático no ve la cara cuando
  Mateo mira hacia abajo. B2: subtítulo a la izquierda (sub_cx) para no tapar ni la cara ni el calendario.
- Arreglo del montador: `place()` descartaba todas las posiciones si el bloque del hook era más ancho que la zona segura y
  lo dejaba siempre arriba (y=360), sin mirar las caras. Ahora solo descarta por alto, y el bloque del hook mide máx. 840 px.
- Costo extra v2: 4 imágenes (US$0,33) + 20 s de Kling (US$1,43) = US$1,76. Total A1-08: US$5,28.
