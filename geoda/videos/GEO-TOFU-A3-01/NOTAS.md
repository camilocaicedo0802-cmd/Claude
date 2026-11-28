# GEO-TOFU-A3-01 · Comparación piedra vs frasco · v1

- Costos optimizados (pedido de Camilo): solo 3 escenas nuevas (hooks A, C y D: 3 imágenes + 15 s de Kling = US$1,23).
  Todo lo demás reutiliza clips ya pagados (A1-02, A1-07, A1-09, A2-02, A2-06, A2-08 y kit) y dos animaciones locales
  (`mg301.py`: nubes olor/perfume y la piedra que rebota en la cama).
- Narrador en off Andrés (H, alterna con la voz M del A2-08): Gemini TTS **gemini-3.1-flash-tts-preview** (modelo completo, no
  lite; la cuota diaria del 3.8 estaba agotada), voz Enceladus, una sola toma con perfil expresivo (fastidiado con el frasco,
  entusiasmado con la piedra). En el cierre de Navidad dijo mal "GEODA": se pegó el "Se llama GEODA" de la frase K7 (misma
  toma) al resto de la frase. Todas las frases verificadas.
- Compliance: frascos genéricos sin marca; claims permitidos (piedra mineral, sin perfume, 1 piedra = 1 año); sin precios.
- 4 versiones (32,3 / 33,0 / 34,9 / 34,0 s; TOFU 21-39), sin acelerar la voz:
  - HA (K7 1 piedra = 1 año): el frasco riega líquido sobre el maquillaje en el bolso. Se quita B1 (mismo plano).
  - HB (K7): la piedra mojándose a contraluz + signo "?" ("Esto que parece un cristal... es un desodorante").
  - HC (K2 Navidad, hook nuevo): "¿Buscas un regalo que sí se use todos los días? Mira esto." — GEODA junto a una caja de regalo.
  - HD (K2, hook nuevo): "Hice la cuenta de cuántos frascos de desodorante compro al año." — calculadora y fila de frascos vacíos.
- Cuerpo: bolso regado · frasco que ya no suelta nada · nubes olor/perfume · la mano destapa la piedra + piedra a contraluz ·
  mojar y pasar · la piedra cae en la cama sin daño · cierre K7: GEODA real junto a frascos tachados; K2: GEODA real con moño.
- QA: movimiento ≥ 3 en todos los planos (se dio más zoom a frasco, nubes y revelación); -14 LUFS; textos fuera de la piedra y la etiqueta.

Montaje: `python3 build.py` y normalizar audio a -14 LUFS (loudnorm 2 pasadas, video copiado).

## HB v2 (Camilo: quitar la etiqueta sobrepuesta y dejar la original)
- El clip del grifo (k_macro del A1-02) traía pegada encima la etiqueta real con `label_fix` y se veía doble y torcida.
  Se volvió a descargar el clip original de Kling (`k_macro_orig_0.mp4`, misma URL de Higgsfield) y el hook B usa ese.
  Ojo: la etiqueta que dibujó Kling tiene letras pequeñas imperfectas ("Deonorente", "NATTIRAL"). Sin costo extra.
