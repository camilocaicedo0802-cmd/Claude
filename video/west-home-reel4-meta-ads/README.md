# West Home Improvement · Reel 4 — Meta Ads: del jacuzzi a una ducha enorme (South Tulsa)

**v6 (ajuste del cliente: "bájale a la música y pon algo más chill y acompañante"):**
- **Música:** "MUSICA LOFI (Sin Copyright) #25", de la carpeta del cliente. Es lo-fi suave en tono mayor, sin melodía
  protagonista, y de las candidatas "chill" es la que menos energía tiene en la banda de la voz (1,5–5 kHz). Al no ser una
  canción comercial, es más segura que "1901" para anuncios pagados.
  - Se eligió con CLAP (`tools/prompts3.json` y `tools/prompts4.json`).
- **Estructura:**
  - Bajo los problemas va la pausa de la pista (solo acordes, sin bajo ni batería).
  - El bajo y la batería suave vuelven en el reveal (144,10 s de la pista → 15,57 s): una subida suave, no un drop.
  - Es una sola pieza continua, sin empalmes, y se desvanece con el video.
- **Volumen:** la música quedó 3,5 dB más baja que en la v5 (−33 LUFS de cama).
  - Queda ~21 dB bajo la voz en los problemas y ~18,5 dB después del reveal (en la v5 eran ~15 dB).
  - La pausa sin bajo se subió 3 dB para que no desaparezca.
  - El máster sigue en −14,3 LUFS.

**v5 (ajuste del cliente: "la música no va con la vibe"):**
- **Música nueva:** Phoenix, "1901" (instrumental), de la carpeta de música del cliente. Es brillante, optimista y con
  impulso, más de anuncio de transformación. Class Act sonaba épica y orquestal, como un tráiler.
- **Cómo se eligió:** analicé las candidatas de la carpeta con CLAP (`tools/clap_rank.py`, laion/clap-htsat-unfused),
  comparándolas con descripciones de estilo.
  - Class Act dio 94 % "épica orquestal de tráiler".
  - "1901" dio 81 % "pop alegre y positivo", sin voz cantada.
- **Sincronía:**
  - La intro de sintetizador va bajo la parte de los problemas. Antes de la batería hay un pequeño corte del bajo, y la
    batería entra (13,64 s de la pista) justo en el reveal de la ducha (15,57 s).
  - Como el video necesita ~1,9 s más de intro, los primeros compases salen de 4 compases más adelante del mismo vamp y la
    pista vuelve atrás en un tiempo fuerte, en el mismo punto del ciclo de acordes.
  - El logo cae en el tiempo 3 del compás.
  - La música sigue durante el cierre y se desvanece con el video, sin silencio.
- **Mezcla:** EQ suave (−2,5 dB a 3 kHz) para dejar espacio a la voz, ducking de −8,5 dB y máster a −14,3 LUFS. La imagen
  es la misma de la v4.
- **Ojo con la licencia:** "1901" es una canción comercial. En anuncios pagados de Meta puede silenciarse o rechazarse si no
  tiene licencia.

**v4 (ajustes del cliente):**
- **11,0–12,6 s:** se quitó la foto del baño viejo y desordenado. En "We suggested to turn the jacuzzi tub area" ahora se
  ve a Peter hablando a cámara, con su recorte BiRefNet, y el whip sigue igual.
- **"$9,800 dollars":** el tramo terminaba en 3,40 s de IMG_9121 y cortaba "dollars" a la mitad. Ahora termina en 3,62 s, en
  el silencio después de la palabra, con 0,06 s antes de "Reach out today".
  - El video dura 0,18 s más (36,67 s).
  - El final se reacomodó para que el logo siga cayendo en el segundo drop de la música (34,77 s). SEND US A MESSAGE entra
    0,5 s después de la toma de Peter.

**v3 (ajuste del cliente):** las fotos del "antes" de la v2 se veían limpias y ya remodeladas. Se cambiaron por baños feos,
viejos y sin remodelar, todos de Unsplash con licencia libre (créditos en `credits_web.json`):

| Tiempo | Voz | Foto |
| --- | --- | --- |
| 1,26–2,78 | …with a couple of problems. | Baño de azulejo verde azulado de los 70–80, oscuro, con cortina sobre la tina y tapete manchado (Devon Wilson) |
| 2,78–4,20 | One, they needed to remodel | Ducha de esquina de los 90 con azulejo terracota y cenefa (Lisa Anna) |
| 4,20–5,93 | an existing shower | Mezcladora de ducha cromada, sucia y con sarro (Howard Lee) |
| 7,89–9,34 | that was not usable | Tina de esquina tipo jacuzzi de los 90, paredes verde salvia y cuadros de conchas (Jake Johnson) |
| 9,34–11,01 | space anymore | Tina rayada vista desde arriba, azulejo turquesa agrietado (Francesca Grima) |
| 11,01–12,59 | We suggested to turn the jacuzzi tub area | (v4: se quitó; ahora sale Peter a cámara) |

- Se mantiene el grade apagado `before` y las dos fotos reales del proceso de esta ducha (IMG_8311/8312) en "into the new
  shower area".
- `edit/prep_web.py` recorta cada foto a 9:16 con su centro (`WEB_V3` en `timeline.py`) a 1620×2880.
- Música, textos, tiempos y el resto del video no cambian. Solo se volvieron a renderizar los primeros 18,4 s.

**v2 (ajustes del cliente):**
- Se quitó la píldora SOUTH TULSA · SHOWER REMODEL del inicio.
- **Antes:** las fotos del "antes" de la v1 eran de otro proyecto, así que se quitaron. Ahora cada imagen corresponde a lo que
  dice Peter. Las fotos de Unsplash tienen licencia libre (créditos en `credits_web.json`) y un color apagado de "antes":
  - "a couple of problems": baño de los 2000 con tina de hidromasaje y ducha.
  - "an existing shower": cancel de vidrio viejo y ducha de azulejo cansada.
  - "a jacuzzi tub that was not usable space anymore": tina con jets.
  - "turn the jacuzzi tub area": jacuzzi.
  - "into the new shower area": las dos fotos reales del proceso de esta ducha (IMG_8311/8312: azulejo a medio poner, ventana,
    banca y nicho).
- **Música:** "Class Act" (Reprise / ANBR, 150 BPM), de la carpeta del cliente. Es música de producción con licencia, mejor
  para anuncios pagados que una canción comercial.
  - Su primer drop (51,8 s) cae en el reveal de la ducha (15,57 s).
  - Un compás antes del logo la pista salta 22 compases hasta su segundo drop (106,2 s), que cae en el logo (34,77 s).
- **Recortes:** BiRefNet-portrait (como los reels 2 y 3).
- **Sonido:** los subtítulos entran sin sonido.

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
