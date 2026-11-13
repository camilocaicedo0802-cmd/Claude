# West Home Improvement · Reel 4 — Meta Ads: del jacuzzi a una ducha enorme (South Tulsa)

Video vertical de 36,5 s (1080×1920, 30 fps) para pauta en Meta. No había guion: la historia se armó con los mejores
fragmentos de Peter (transcritos palabra por palabra en `words.json` y `chunks.json`, pausas cortadas). El B-roll y las
fotos reales del proyecto llevan el video, y Peter sale a cámara solo en el hook, a mitad de la historia y en el CTA.

| Tiempo | Voz | Imagen | Texto |
| --- | --- | --- | --- |
| 0–1,3 | This customer came at us… | Peter a cámara desde el primer cuadro | Hook: SOUTH TULSA · SHOWER REMODEL / THEY HAD 2 PROBLEMS… |
| 1,3–5,9 | …with a couple of problems. One, they needed to remodel an existing shower | Foto del baño viejo → punch-in a la ducha vieja | PROBLEM #1 / OLD SHOWER |
| 5,9–11,0 | And two, they had a jacuzzi tub that was not usable space anymore | Peter → fotos del baño viejo | PROBLEM #2 / UNUSED JACUZZI TUB |
| 11,0–15,6 | We suggested to turn the jacuzzi tub area into the new shower area | Fotos de demolición y de la base de la ducha | JACUZZI (tachado) → NEW SHOWER |
| 15,6–18,7 | creating this massive, beautiful new shower | Drop de la música: Félix abre la puerta de vidrio → plano héroe | MASSIVE / BEAUTIFUL NEW SHOWER |
| 18,7–23,1 | and turn the old shower area into a storage closet | Félix abre el clóset → repisas | STORAGE CLOSET |
| 23,1–29,8 | completely transforming their space, giving them functionality and features that they really wanted | Recorrido de la ducha, Félix en la banca, montaje al ritmo: nicho, regadera, grifería, ducha de mano | FUNCTIONALITY, BUILT-IN BENCH, CUSTOM NICHE, RAIN SHOWER HEAD, NEW FIXTURES, HANDHELD SPRAY |
| 29,8–33,1 | Remember, our shower remodels start at $9,800 | Peter → ducha terminada | STARTING AT $9,800 (contador) |
| 33,1–33,9 | Reach out today. | Peter | REACH OUT TODAY |
| 33,9–36,5 | | Ducha terminada (corte de la música y drop sobre el logo) | READY FOR YOUR DREAM SHOWER? / SEND US A MESSAGE / logo / Shower remodels · Tulsa & surrounding areas |

- Todos los textos van detrás de las personas (recorte por cuadro con U2-Net), sin emojis, con Poppins y tracking cerrado.
  Los subtítulos se acomodan solos para no tapar personas ni chocar con los títulos (`layout` en `overlays.py`).
- SFX solo de la librería del cliente (`video/sfx-library`): teclado en cada texto, pops y golpes en palabras clave,
  whooshes en transiciones, riser y golpe en el reveal, golpe y brillo cuando cae el precio.
- Música: la pista original de 100 BPM del reel 1 (ElevenLabs Music v2.5). No se generó una nueva porque los créditos de
  Higgsfield están agotados. Una sola pasada de la pista: el drop cae en el reveal (15,6 s) y el corte/drop final en el logo.
- No hay foto del jacuzzi: mientras Peter habla de él se ven el baño viejo (vanity y mesón) y luego la demolición.
