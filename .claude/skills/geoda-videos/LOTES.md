# Lotes de producción GEODA (5 videos por chat, en el orden del brief)

Lote 1 (A1-01 a A1-06) lo hace el primer chat. Los lotes siguen el orden del brief (A1 → A11).
Los personajes pueden ser distintos en cada video (no hace falta repetirlos entre videos ni entre chats).
Voces (Gemini TTS, H = hombre, M = mujer): cada lote tiene dos voces sugeridas (una M y una H) para que dos chats no usen
la misma voz al mismo tiempo; dentro de un video, cada personaje conserva su voz. Las notas son sugerencias.

## Lote 2 (4 videos: el A1-06 lo hace el chat del lote 1)
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A1-07 | Faceless / motion graphics | 36 s | 1 piedra te dura 1 año (ahorro) | Faceless/motion: gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 2 | GEO-BOFU-A1-08 | UGC con avatar IA | 21 s | Black Friday | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 3 | GEO-TOFU-A2-01 | UGC con avatar IA | 27 s | Paga contraentrega | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 4 | GEO-TOFU-A2-02 | Estilo Pixar (3D) | 27 s | Navidad / regalo | Pixar: Geo (la piedra) diseñado a partir de fotos reales de la piedra (misma forma y color); frascos genéricos sin marca; cerrar con 2 s de producto real. |
- **Voces sugeridas:** Aoede (M) y Fenrir (H)

## Lote 3
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A2-03 | Testimonio | 30 s | Envío a toda Colombia | Testimonio generado: sin contar resultados como reales. |
| 2 | GEO-TOFU-A2-04 | Podcast | 39 s | Black Friday | Podcast: WAN 3.0 con audio nativo, una toma larga por persona y su plano solo cuando habla (ref. `pipeline/build_a105.py`; se puede reutilizar `kit/personajes/podcast/`). |
| 3 | GEO-MOFU-A2-05 | Diario de 14 días | 45 s | Black Friday | Diario 14 días: la misma persona y la misma voz en los 14 días del video. |
| 4 | GEO-MOFU-A2-06 | Comparación piedra vs frasco | 33 s | Combo 2x para regalar | Comparación: frascos genéricos sin marca. |
| 5 | GEO-BOFU-A2-07 | UGC con avatar IA | 21 s | Combo 2x para regalar | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
- **Voces sugeridas:** Callirrhoe (M) y Orus (H)

## Lote 4
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-BOFU-A2-08 | Unboxing | 21 s | Llévala hoy | Unboxing: producto real; manos sin cara. |
| 2 | GEO-TOFU-A3-01 | Comparación piedra vs frasco | 24 s | 1 piedra te dura 1 año (ahorro) | Comparación: frascos genéricos sin marca. |
| 3 | GEO-TOFU-A3-02 | Claymation (stop-motion IA) | 27 s | Llévala hoy | Claymation: prompt base del brief (plastilina, 12 fps), ref. `pipeline/build_a103_v2.py`. |
| 4 | GEO-TOFU-A3-03 | Demo de producto (macro) | 24 s | Paga contraentrega | Demo: producto real animado (ref. `pipeline/build_a102_v3.py`). |
| 5 | GEO-TOFU-A3-04 | Estilo Pixar (3D) | 27 s | Navidad / regalo | Pixar: Geo (la piedra) diseñado a partir de fotos reales de la piedra (misma forma y color); frascos genéricos sin marca; cerrar con 2 s de producto real. |
- **Voces sugeridas:** Autonoe (M) y Enceladus (H)

## Lote 5
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A3-05 | Faceless / motion graphics | 36 s | Envío a toda Colombia | Faceless/motion: gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 2 | GEO-MOFU-A3-06 | Founder | 36 s | Se agota rápido | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
| 3 | GEO-BOFU-A3-07 | UGC con avatar IA | 21 s | Se agota rápido | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 4 | GEO-TOFU-A4-01 | Duración / báscula | 27 s | 1 piedra te dura 1 año (ahorro) | Duración/báscula: producto real en la báscula (foto real animada). |
| 5 | GEO-TOFU-A4-02 | Street interview | 27 s | Black Friday | Street: WAN 3.0 con audio nativo y ruido de calle (ref. `pipeline/build_a104.py`; se puede reutilizar `kit/personajes/calle/`). |
- **Voces sugeridas:** Despina (M) y Iapetus (H)

## Lote 6
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A4-03 | Claymation (stop-motion IA) | 27 s | 1 piedra te dura 1 año (ahorro) | Claymation: prompt base del brief (plastilina, 12 fps), ref. `pipeline/build_a103_v2.py`. |
| 2 | GEO-MOFU-A4-04 | Faceless / motion graphics | 33 s | 1 piedra te dura 1 año (ahorro) | Faceless/motion: gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 3 | GEO-MOFU-A4-05 | Podcast | 39 s | Combo 2x para regalar | Podcast: WAN 3.0 con audio nativo, una toma larga por persona y su plano solo cuando habla (ref. `pipeline/build_a105.py`; se puede reutilizar `kit/personajes/podcast/`). |
| 4 | GEO-BOFU-A4-06 | UGC con avatar IA | 21 s | Se agota rápido | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 5 | GEO-BOFU-A4-07 | Founder | 21 s | Combo 2x para regalar | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
- **Voces sugeridas:** Erinome (M) y Umbriel (H)

## Lote 7
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A5-01 | Demo de producto | 27 s | Llévala hoy | Demo: producto real animado (ref. `pipeline/build_a102_v3.py`). |
| 2 | GEO-TOFU-A5-02 | POV | 24 s | Envío a toda Colombia | POV: voz interior. |
| 3 | GEO-TOFU-A5-03 | Estilo Pixar (3D) | 27 s | Navidad / regalo | Pixar: Geo (la piedra) diseñado a partir de fotos reales de la piedra (misma forma y color); frascos genéricos sin marca; cerrar con 2 s de producto real. |
| 4 | GEO-MOFU-A5-04 | Comparación piedra vs frasco | 33 s | Se agota rápido | Comparación: frascos genéricos sin marca. |
| 5 | GEO-MOFU-A5-05 | Testimonio | 33 s | Navidad / regalo | Testimonio generado: sin contar resultados como reales. |
- **Voces sugeridas:** Laomedeia (M) y Algieba (H)

## Lote 8
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-BOFU-A5-06 | UGC con avatar IA | 18 s | Black Friday | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 2 | GEO-TOFU-A6-01 | UGC con avatar IA | 27 s | Paga contraentrega | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 3 | GEO-TOFU-A6-02 | Claymation (stop-motion IA) | 27 s | Black Friday | Claymation: prompt base del brief (plastilina, 12 fps), ref. `pipeline/build_a103_v2.py`. |
| 4 | GEO-MOFU-A6-03 | Diario de 14 días | 51 s | Combo 2x para regalar | Diario 14 días: la misma persona y la misma voz en los 14 días del video. |
| 5 | GEO-MOFU-A6-04 | Podcast | 42 s | Paga contraentrega | Podcast: WAN 3.0 con audio nativo, una toma larga por persona y su plano solo cuando habla (ref. `pipeline/build_a105.py`; se puede reutilizar `kit/personajes/podcast/`). |
- **Voces sugeridas:** Achernar (M) y Algenib (H)

## Lote 9
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-BOFU-A6-05 | UGC con avatar IA | 21 s | Llévala hoy | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 2 | GEO-BOFU-A6-06 | Founder | 21 s | Se agota rápido | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
| 3 | GEO-TOFU-A7-01 | UGC con avatar IA | 24 s | Envío a toda Colombia | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 4 | GEO-TOFU-A7-02 | Street interview | 27 s | Paga contraentrega | Street: WAN 3.0 con audio nativo y ruido de calle (ref. `pipeline/build_a104.py`; se puede reutilizar `kit/personajes/calle/`). |
| 5 | GEO-TOFU-A7-03 | POV | 24 s | Llévala hoy | POV: voz interior. |
- **Voces sugeridas:** Gacrux (M) y Rasalgethi (H)

## Lote 10
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A7-04 | Faceless / motion graphics | 33 s | Envío a toda Colombia | Faceless/motion: gráficos sobre fotos reales (ref. `pipeline/motion_v3.py`). |
| 2 | GEO-MOFU-A7-05 | Testimonio | 33 s | Se agota rápido | Testimonio generado: sin contar resultados como reales. |
| 3 | GEO-BOFU-A7-06 | UGC con avatar IA | 18 s | Combo 2x para regalar | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 4 | GEO-TOFU-A8-01 | UGC con avatar IA (storytime) | 36 s | 1 piedra te dura 1 año (ahorro) | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 5 | GEO-TOFU-A8-02 | Estilo Pixar (3D) | 30 s | Navidad / regalo | Pixar: Geo (la piedra) diseñado a partir de fotos reales de la piedra (misma forma y color); frascos genéricos sin marca; cerrar con 2 s de producto real. |
- **Voces sugeridas:** Pulcherrima (M) y Alnilam (H)

## Lote 11
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-MOFU-A8-03 | Founder | 39 s | Llévala hoy | Founder: el brief dice que NO se inventa. Pedir a Camilo el video real del fundador o su autorización para clonar avatar y voz; sin eso, dejarlo pendiente. |
| 2 | GEO-BOFU-A8-04 | Testimonio (recopilación de reseñas) | 24 s | Navidad / regalo | Reseñas: NO se inventan. Pedir a Camilo las reseñas reales antes de producirlo. |
| 3 | GEO-TOFU-A9-01 | UGC con avatar IA | 24 s | Envío a toda Colombia | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 4 | GEO-TOFU-A9-02 | Podcast | 36 s | Black Friday | Podcast: WAN 3.0 con audio nativo, una toma larga por persona y su plano solo cuando habla (ref. `pipeline/build_a105.py`; se puede reutilizar `kit/personajes/podcast/`). |
| 5 | GEO-MOFU-A9-03 | Demo de producto | 33 s | Navidad / regalo | Demo: producto real animado (ref. `pipeline/build_a102_v3.py`). |
- **Voces sugeridas:** Vindemiatrix (M) y Schedar (H)

## Lote 12
| # | Video | Formato | Duración | CTA | Nota |
|---|---|---|---|---|---|
| 1 | GEO-TOFU-A10-01 | Street interview | 27 s | Paga contraentrega | Street: WAN 3.0 con audio nativo y ruido de calle (ref. `pipeline/build_a104.py`; se puede reutilizar `kit/personajes/calle/`). |
| 2 | GEO-TOFU-A10-02 | POV | 21 s | Llévala hoy | POV: voz interior. |
| 3 | GEO-MOFU-A10-03 | UGC con avatar IA | 33 s | Envío a toda Colombia | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 4 | GEO-TOFU-A11-01 | UGC con avatar IA (mamá) | 27 s | 1 piedra te dura 1 año (ahorro) | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
| 5 | GEO-BOFU-A11-02 | UGC con avatar IA (familia) | 21 s | Combo 2x para regalar | UGC: voz en off storytime, la avatar no mueve los labios (ref. `pipeline/build_a101_v2.py`). |
- **Voces sugeridas:** Sulafat (M) y Sadachbia (H)
