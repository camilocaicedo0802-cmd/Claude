# Lotes de producción GEODA (5 videos por chat, en el orden del brief)

Lote 1 (A1-01 a A1-05) ya está entregado. Los lotes siguen el orden del brief (A1 → A11).
Voces (Gemini TTS, H = hombre, M = mujer): los personajes que se repiten tienen voz fija en `geoda/kit/VOCES.md`
(Andrés = Achird, Sofía = Kore, Camila = Leda, Geo = Puck, narrador Pixar = Charon, narradora motion = Zephyr).
Para personajes NUEVOS cada lote usa solo sus dos voces (una de mujer y una de hombre), así dos chats no comparten voz;
si un video necesita más personajes nuevos, usar WAN 3.0 con audio nativo o avisar a Camilo. Registrar cada personaje nuevo en VOCES.md.

## Lote 2
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A1-06 | POV | 30 s | Se agota rápido | POV: voz interior con la voz del lote. |
| 2 | GEO-MOFU-A1-07 | Faceless / motion graphics | 36 s | 1 piedra te dura 1 año (ahorro) | Faceless/motion: narradora Zephyr, gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 3 | GEO-BOFU-A1-08 | UGC con avatar IA | 21 s | Black Friday | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 4 | GEO-TOFU-A2-01 | UGC con avatar IA | 27 s | Paga contraentrega | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 5 | GEO-TOFU-A2-02 | Estilo Pixar (3D) | 27 s | Navidad / regalo | Pixar: Geo (la piedra) con su hoja de personaje fija `kit/personajes/geo/` y voz Puck; narrador Charon. Si la hoja no existe, ver "Personajes recurrentes" en SKILL.md. |
- **Voces para personajes nuevos:** Aoede (M) y Fenrir (H)

## Lote 3
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A2-03 | Testimonio | 30 s | Envío a toda Colombia | Testimonio generado: rótulo IA y sin contar resultados como reales. |
| 2 | GEO-TOFU-A2-04 | Podcast | 39 s | Black Friday | Podcast: el mismo set, presentador e invitada del A1-05 (`kit/personajes/podcast/`), WAN 3.0 con audio nativo, una toma larga por persona (ref. `pipeline/build_a105.py`). |
| 3 | GEO-MOFU-A2-05 | Diario de 14 días | 45 s | Black Friday | Diario 14 días: una sola persona en los 14 días, misma voz del lote. |
| 4 | GEO-MOFU-A2-06 | Comparación piedra vs frasco | 33 s | Combo 2x para regalar | Comparación: frascos genéricos sin marca. |
| 5 | GEO-BOFU-A2-07 | UGC con avatar IA | 21 s | Combo 2x para regalar | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
- **Voces para personajes nuevos:** Callirrhoe (M) y Orus (H)

## Lote 4
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-BOFU-A2-08 | Unboxing | 21 s | Llévala hoy | Unboxing: producto real; manos sin cara. |
| 2 | GEO-TOFU-A3-01 | Comparación piedra vs frasco | 24 s | 1 piedra te dura 1 año (ahorro) | Comparación: frascos genéricos sin marca. |
| 3 | GEO-TOFU-A3-02 | Claymation (stop-motion IA) | 27 s | Llévala hoy | Claymation: narradora Sofía (Kore) y el estilo del A1-03 (`videos/GEO-TOFU-A1-03/assets.json`, ref. `pipeline/build_a103_v2.py`). |
| 4 | GEO-TOFU-A3-03 | Demo de producto (macro) | 24 s | Paga contraentrega | Demo: narrador Andrés (Achird), producto real animado (ref. `pipeline/build_a102_v3.py`). |
| 5 | GEO-TOFU-A3-04 | Estilo Pixar (3D) | 27 s | Navidad / regalo | Pixar: Geo (la piedra) con su hoja de personaje fija `kit/personajes/geo/` y voz Puck; narrador Charon. Si la hoja no existe, ver "Personajes recurrentes" en SKILL.md. |
- **Voces para personajes nuevos:** Autonoe (M) y Enceladus (H)

## Lote 5
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A3-05 | Faceless / motion graphics | 36 s | Envío a toda Colombia | Faceless/motion: narradora Zephyr, gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 2 | GEO-MOFU-A3-06 | Founder | 36 s | Se agota rápido | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
| 3 | GEO-BOFU-A3-07 | UGC con avatar IA | 21 s | Se agota rápido | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 4 | GEO-TOFU-A4-01 | Duración / báscula | 27 s | 1 piedra te dura 1 año (ahorro) | Duración/báscula: producto real en la báscula (foto real animada). |
| 5 | GEO-TOFU-A4-02 | Street interview | 27 s | Black Friday | Street: el mismo presentador del A1-04 (`kit/personajes/calle/`), WAN 3.0 con audio nativo (ref. `pipeline/build_a104.py`). |
- **Voces para personajes nuevos:** Despina (M) y Iapetus (H)

## Lote 6
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A4-03 | Claymation (stop-motion IA) | 27 s | 1 piedra te dura 1 año (ahorro) | Claymation: narradora Sofía (Kore) y el estilo del A1-03 (`videos/GEO-TOFU-A1-03/assets.json`, ref. `pipeline/build_a103_v2.py`). |
| 2 | GEO-MOFU-A4-04 | Faceless / motion graphics | 33 s | 1 piedra te dura 1 año (ahorro) | Faceless/motion: narradora Zephyr, gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 3 | GEO-MOFU-A4-05 | Podcast | 39 s | Combo 2x para regalar | Podcast: el mismo set, presentador e invitada del A1-05 (`kit/personajes/podcast/`), WAN 3.0 con audio nativo, una toma larga por persona (ref. `pipeline/build_a105.py`). |
| 4 | GEO-BOFU-A4-06 | UGC con avatar IA | 21 s | Se agota rápido | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 5 | GEO-BOFU-A4-07 | Founder | 21 s | Combo 2x para regalar | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
- **Voces para personajes nuevos:** Erinome (M) y Umbriel (H)

## Lote 7
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A5-01 | Demo de producto | 27 s | Llévala hoy | Demo: narrador Andrés (Achird), producto real animado (ref. `pipeline/build_a102_v3.py`). |
| 2 | GEO-TOFU-A5-02 | POV | 24 s | Envío a toda Colombia | POV: voz interior con la voz del lote. |
| 3 | GEO-TOFU-A5-03 | Estilo Pixar (3D) | 27 s | Navidad / regalo | Pixar: Geo (la piedra) con su hoja de personaje fija `kit/personajes/geo/` y voz Puck; narrador Charon. Si la hoja no existe, ver "Personajes recurrentes" en SKILL.md. |
| 4 | GEO-MOFU-A5-04 | Comparación piedra vs frasco | 33 s | Se agota rápido | Comparación: frascos genéricos sin marca. |
| 5 | GEO-MOFU-A5-05 | Testimonio | 33 s | Navidad / regalo | Testimonio generado: rótulo IA y sin contar resultados como reales. |
- **Voces para personajes nuevos:** Laomedeia (M) y Algieba (H)

## Lote 8
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-BOFU-A5-06 | UGC con avatar IA | 18 s | Black Friday | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 2 | GEO-TOFU-A6-01 | UGC con avatar IA | 27 s | Paga contraentrega | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 3 | GEO-TOFU-A6-02 | Claymation (stop-motion IA) | 27 s | Black Friday | Claymation: narradora Sofía (Kore) y el estilo del A1-03 (`videos/GEO-TOFU-A1-03/assets.json`, ref. `pipeline/build_a103_v2.py`). |
| 4 | GEO-MOFU-A6-03 | Diario de 14 días | 51 s | Combo 2x para regalar | Diario 14 días: una sola persona en los 14 días, misma voz del lote. |
| 5 | GEO-MOFU-A6-04 | Podcast | 42 s | Paga contraentrega | Podcast: el mismo set, presentador e invitada del A1-05 (`kit/personajes/podcast/`), WAN 3.0 con audio nativo, una toma larga por persona (ref. `pipeline/build_a105.py`). |
- **Voces para personajes nuevos:** Achernar (M) y Algenib (H)

## Lote 9
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-BOFU-A6-05 | UGC con avatar IA | 21 s | Llévala hoy | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 2 | GEO-BOFU-A6-06 | Founder | 21 s | Se agota rápido | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
| 3 | GEO-TOFU-A7-01 | UGC con avatar IA | 24 s | Envío a toda Colombia | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 4 | GEO-TOFU-A7-02 | Street interview | 27 s | Paga contraentrega | Street: el mismo presentador del A1-04 (`kit/personajes/calle/`), WAN 3.0 con audio nativo (ref. `pipeline/build_a104.py`). |
| 5 | GEO-TOFU-A7-03 | POV | 24 s | Llévala hoy | POV: voz interior con la voz del lote. |
- **Voces para personajes nuevos:** Gacrux (M) y Rasalgethi (H)

## Lote 10
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A7-04 | Faceless / motion graphics | 33 s | Envío a toda Colombia | Faceless/motion: narradora Zephyr, gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 2 | GEO-MOFU-A7-05 | Testimonio | 33 s | Se agota rápido | Testimonio generado: rótulo IA y sin contar resultados como reales. |
| 3 | GEO-BOFU-A7-06 | UGC con avatar IA | 18 s | Combo 2x para regalar | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 4 | GEO-TOFU-A8-01 | UGC con avatar IA (storytime) | 36 s | 1 piedra te dura 1 año (ahorro) | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 5 | GEO-TOFU-A8-02 | Estilo Pixar (3D) | 30 s | Navidad / regalo | Pixar: Geo (la piedra) con su hoja de personaje fija `kit/personajes/geo/` y voz Puck; narrador Charon. Si la hoja no existe, ver "Personajes recurrentes" en SKILL.md. |
- **Voces para personajes nuevos:** Pulcherrima (M) y Alnilam (H)

## Lote 11
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A8-03 | Founder | 39 s | Llévala hoy | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
| 2 | GEO-BOFU-A8-04 | Testimonio (recopilación de reseñas) | 24 s | Navidad / regalo | Reseñas: NO se inventan. Pedir a Camilo las reseñas reales antes de producirlo. |
| 3 | GEO-TOFU-A9-01 | UGC con avatar IA | 24 s | Envío a toda Colombia | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 4 | GEO-TOFU-A9-02 | Podcast | 36 s | Black Friday | Podcast: el mismo set, presentador e invitada del A1-05 (`kit/personajes/podcast/`), WAN 3.0 con audio nativo, una toma larga por persona (ref. `pipeline/build_a105.py`). |
| 5 | GEO-MOFU-A9-03 | Demo de producto | 33 s | Navidad / regalo | Demo: narrador Andrés (Achird), producto real animado (ref. `pipeline/build_a102_v3.py`). |
- **Voces para personajes nuevos:** Vindemiatrix (M) y Schedar (H)

## Lote 12
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A10-01 | Street interview | 27 s | Paga contraentrega | Street: el mismo presentador del A1-04 (`kit/personajes/calle/`), WAN 3.0 con audio nativo (ref. `pipeline/build_a104.py`). |
| 2 | GEO-TOFU-A10-02 | POV | 21 s | Llévala hoy | POV: voz interior con la voz del lote. |
| 3 | GEO-MOFU-A10-03 | UGC con avatar IA | 33 s | Envío a toda Colombia | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 4 | GEO-TOFU-A11-01 | UGC con avatar IA (mamá) | 27 s | 1 piedra te dura 1 año (ahorro) | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
| 5 | GEO-BOFU-A11-02 | UGC con avatar IA (familia) | 21 s | Combo 2x para regalar | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`); Camila (Leda) si encaja, si no avatar nueva con la voz del lote. |
- **Voces para personajes nuevos:** Sulafat (M) y Sadachbia (H)
