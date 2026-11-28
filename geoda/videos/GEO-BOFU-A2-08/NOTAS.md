# GEO-BOFU-A2-08 · Unboxing (solo manos) · v1

> Ángulo A2: NO PUBLICAR hasta que Alberto confirme el registro sanitario.

- El brief pide producto y empaque reales "grabados de verdad": aquí van manos generadas con IA y una caja kraft genérica
  (sin logo); el producto es el GEODA real (referencias del producto en las imágenes, recorte real en la cama y el cierre).
  Cuando haya grabación real del empaque se puede reemplazar plano por plano con el mismo montaje.
- Voz en off de Valentina con la regla 47: Gemini TTS gemini-3.8-flash-tts (completo), voz Autonoe, una sola toma
  expresiva (susurra en "Ven, la abrimos juntas", suspenso antes de "la piedra GEODA"). Se grabaron 3 tomas más para sumar
  una frase de garantía: dos pronunciaban mal "GEODA" y la cuota diaria se agotó; se usó la toma 1 completa (no se mezclan
  tomas: cambia el tono). Verificada frase por frase con el transcriptor más preciso.
- Sin precios (K1 no se usó). Sin caras.
- 4 versiones (19,7 / 21,3 / 22,7 / 22,7 s):
  - HA (K3 Llévala hoy): el domiciliario entrega la caja y el billete cambia de mano. Se quita B1 (mismo texto del hook).
  - HB (K3): tijera que corta la cinta en macro (ASMR).
  - HC (K2 Navidad, hook nuevo): "Unboxing de mi regalo de Navidad... para mí misma." — desata el moño rojo junto al árbol.
  - HD (K2, hook nuevo): "Lo que llega en esta caja reemplazó mi desodorante." — sacude la caja cerrada.
  - En A y B esa misma frase va en el cuerpo (fila X) para llegar a la duración BOFU sin cambiar de toma.
- Cuerpo: entrega con pago al recibir (solo 0-1,3 s del clip, de ida y vuelta: después la caja queda flotando) · abre la caja ·
  saca GEODA a la luz · primera aplicación (agua en la punta, kit) · tres GEODA reales sobre la cama (local) · cierre K3:
  producto real + botón Comprar (local, `mg208.py cta_k3`); K2: producto real + etiqueta REGALO NAVIDAD + Comprar (A1-08).
- QA: movimiento ≥ 3 en todos los planos; audio normalizado a -14 LUFS (el montaje quedaba en -16).
- Costo: 7 imágenes (US$0,33) + 30 s de Kling (US$2,14) = US$2,47. Voz gratis.

Montaje: `python3 build.py` y luego normalizar el audio a -14 LUFS (loudnorm de 2 pasadas, video copiado).
