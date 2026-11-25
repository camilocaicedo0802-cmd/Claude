---
name: geoda-videos
description: Producir un lote de 5 anuncios en video de GEODA (desodorante de piedra de alumbre, Colombia) según el brief de 60 videos, con el pipeline del repo (Higgsfield + Gemini TTS + montador propio), y entregarlos con los nombres y carpetas del brief. Usar cuando Camilo pida "lote N", "los videos GEODA", un ID como GEO-TOFU-A2-01, o correcciones (v2, v3) de un video GEODA.
---

# GEODA · producción de un lote de videos

Camilo produce para Alberto los 60 videos del brief (`geoda/brief_v2/`). Cada chat hace **un lote de 5**, en el orden del brief
(`LOTES.md`, en esta carpeta). El argumento es el número de lote (`lote 3`) o una lista de IDs. Si no viene, pregunta cuál lote hacer.
Habla siempre en español, con frases simples. Al final de **cada respuesta** manda una notificación push corta (regla de Camilo).

## 0. Arranque (una vez por chat)
1. Si el repo no tiene `geoda/` (la sesión clonó otra rama): `git fetch origin claude/brave-gates-edmrub` y
   `git checkout FETCH_HEAD -- geoda .claude/skills/geoda-videos`.
2. `bash geoda/pipeline/setup_work.sh <scratchpad>/geoda` → crea la carpeta de trabajo, enlaza código y kit, escribe `~/.geoda_work`.
3. `python3 geoda/pipeline/smoke_test.py` → debe salir un mp4 de ~7 s (prueba sin costo). Si falla, arreglar antes de gastar.
4. Comprobar servicios (credenciales las pone el proxy; nunca pedir ni pegar llaves):
   `curl -s https://api.higgsfield.ai/models | head -c 80` y una voz corta con `tools/tts_multi.py`.
5. Leer completas: `geoda/REGLAS_PRODUCCION.md` (reglas del cliente, numeradas) y `geoda/brief_v2/brief_reglas.txt` (brief).
   Guion de un video (las claves son los IDs):
   `python3 -c "import json;print(json.load(open('geoda/brief_v2/guiones_60.json'))['GEO-TOFU-A2-01'])"`

## 1. Reglas que más se rompen (resumen; manda REGLAS_PRODUCCION.md)
- **Guion exacto del brief**: cada frase tal cual; hooks A y B = dos archivos (HA, HB). Sin precios salvo que Camilo lo pida
  (Black Friday = "Paga 2 lleva 3", sin $). CTA del brief (K1…K7) + pill "Pago contraentrega · Envío gratis".
- **Zona segura**: ningún texto en los 250 px de arriba, 670 px de abajo ni 140 px de la derecha (el montador ya lo cumple).
- **Hook** en pantalla desde el fotograma 1 hasta el s3, dos líneas (blanca + amarilla). **Voz desde el fotograma 1.**
- **Ningún texto sobre caras, ni sobre la piedra o la etiqueta.** Subtítulos palabra por palabra; no repetir en titular
  lo que ya dice la voz (queda el subtítulo; usar íconos o números grandes).
- **Etiqueta perfecta o sin etiqueta.** Producto real (foto o clip revisado del kit) mínimo 2-3 s y en el cierre.
  Agua solo en la punta de la piedra. Piedra boca abajo → etiqueta invertida.
- **El avatar SIEMPRE en video haciendo algo** (regla de Camilo): nunca una foto fija de una persona o avatar con zoom.
  Toda imagen de una persona (cara, cuerpo o sus manos) se anima con Kling y se usa el clip con una acción (oler, rociar,
  aplicar, abotonarse, escribir, colgar la chaqueta…). Las fotos fijas solo sirven para producto, fondos y gráficos.
- **Labios**: la voz que se oye es de quien mueve los labios. Avatares UGC = voz en off (la avatar no habla a cámara).
  Personas que hablan (podcast, calle) = WAN 3.0 con audio nativo, **una toma larga por persona** y solo su plano cuando habla.
- **Dentro de cada video, un personaje = una cara y una voz** (no cambian a mitad del video). Alternar voz de mujer y de
  hombre entre videos del lote.
- **Rótulo "Recreación con IA"** (lo pone el montador con `ai_label=True`) en avatares, entrevistas, podcast, testimonios generados.
- **Ritmo**: plano nuevo cada 2,5-3 s, sin pausas > 0,3 s, efecto de sonido en cada corte. Duración TOFU 21-39 s,
  MOFU 30-51 s, BOFU 18-24 s (usar `speed` 1.05-1.2 si sobra).
- **Compliance**: sin primeros planos de axila (planos medios con ropa), no decir "24 horas", "100 % natural",
  "sin aluminio", "antitranspirante" ni segundos de aplicación. Founder y reseñas NO se inventan: pedir material real.

## 1b. Personajes
Los personajes **pueden ser distintos en cada video** (decisión de Camilo): no hace falta repetir a Geo, al presentador ni
al podcast entre videos o chats. Si algo del kit sirve (`geoda/kit/personajes/`, `geoda/videos/*/assets.json`), se puede
reutilizar para ahorrar, pero no es obligatorio. Para personajes nuevos, preferir las dos voces del lote (`LOTES.md`).

## 2. Flujo por video
Carpeta del video en el repo: `geoda/videos/<ID>/` (build.py, motion.py si hay, `vo/`, `assets.json`, `NOTAS.md`).
Salidas pesadas (clips, mp4) en la carpeta de trabajo `G` (`cat ~/.geoda_work`): generados en `G/hf`, montaje en `G/<id>/`.

1. **Plan de planos**: tabla fila por fila (HA, HB, B1…, CTA) con la frase, el visual del brief y la fuente de cada plano.
   Antes de generar, reutilizar: `geoda/kit/` (producto real, b-roll revisado, Camila, set de podcast, audio) y los
   `assets.json` de otros videos (`python3 G/tools/assets.py fetch <assets.json> G/hf`).
2. **Generar** (desde `G/hf`, con `./hf.sh submit <endpoint> <nombre>.body.json <nombre>` y `./hf.sh wait <nombre> 900`):
   - Imagen: `marketing-studio/image` · `{"resolution":"1k","aspect_ratio":"9:16","quality":"medium","enhance_prompt":false,
     "prompt":…,"image_urls":[referencias]}` (US$0,053). Personaje con varias escenas en el video: primero una imagen maestra y luego las demás con
     ella como primera referencia ("the SAME woman as the first reference…"). Producto: las 2 URLs de `kit/README.md`.
   - Video sin diálogo: `kling-video/v3.0/std/image-to-video` · `{"prompt":…,"image_url":…,"duration":3-5,"sound":"off",
     "cfg_scale":0.6}` (US$0,071/s). En personas: "She does not speak, lips stay closed". Producto: "keeps exactly the same
     shape and label", sin giros. Kling suele entreabrir la boca al exhalar o sonreír: revisar la boca cuadro a cuadro y usar
     solo los tramos con la boca cerrada; si no alcanzan, pedir la acción de espaldas, de perfil lejano o en primera persona
     (manos) para que no se vea la boca. Para estirar un tramo bueno: cámara lenta con interpolación
     (`ffmpeg -vf "setpts=PTS/0.6,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1"`), nunca congelar una foto.
   - Video con diálogo: `alibaba/wan-3.0/image-to-video` · `{"prompt":…,"image_url":…,"duration":≤15,"resolution":"720p",
     "generate_audio":true}` (US$0,075/s); en el prompt las frases exactas entre «», acento colombiano, "lips perfectly synced".
   - Hooks y planos del producto que deben moverse: animar la **foto real** en Python (destellos, giros, tachado, X que cae,
     reloj, nubes) como `pipeline/motion_v3.py` y `pipeline/motion_a101_v2.py`: la etiqueta no se deforma.
   - Revisar cada clip con una hoja de cuadros (ffmpeg) antes de usarlo: etiqueta, labios cerrados, piedra igual.
   - Guardar enlaces: `python3 G/tools/assets.py save G/hf geoda/videos/<ID>/assets.json <nombres…>`.
3. **Voz** (Gemini TTS, gratis): todas las frases de un personaje en **una** petición →
   `python3 G/tools/tts_multi.py narr.wav <Voz> perfil.txt frases.txt` (perfil = director's notes como en `geoda/videos/*/vo/`).
   Cortar: `pauses.py` (tramos reales por energía; NO usar marcas de tiempo de Gemini, se corren 1-2 s) →
   `verify_lines.py spec.json` (STT de cada frase aislada contra el guion; números "7:00" = "siete" está bien) →
   `cut_lines.py narr.wav vo 'HA:a-b,B1:a-b,…'` → `vo/<KEY>_t.wav` (pausas internas ≤ 0,18 s).
   Audio nativo WAN: mismas herramientas sobre el clip; `clip_audio=True` en la fila (ver `pipeline/build_a104.py`).
4. **Montaje**: copiar `geoda/pipeline/plantilla_build.py` a `geoda/videos/<ID>/build.py` y llenar (claves explicadas en la
   plantilla y en `pipeline/README.md`). Correr `python3 geoda/videos/<ID>/build.py` → `G/<id>/GEO_…_HA_<FMT>_v1.mp4` y HB.
5. **QA obligatorio**: `python3 G/tools/qa_sheet.py <mp4> G/lab/<id>.jpg 1.0 8` y mirar la hoja: textos fuera de caras,
   piedra y etiqueta; dentro de las guías; hook desde el cuadro 1; rótulo; CTA y producto real al final. Si algo falla,
   ajustar cajas protegidas (tercer elemento del plano), `sub_y`, `hook_slots`, `icon_x`, y volver a montar.
6. **Entregar cada video apenas esté** (SendUserFile, HA y HB) con su costo en USD (imágenes + segundos de video).

## 3. Cierre del lote
- Carpeta `GEODA_60/<TOFU|MOFU|BOFU>/<A#>/` con los mp4 vigentes (CTA alternos en `CTA_alternos/`), `LEEME.txt` (video,
  duración, voz, CTA) y `.zip`; enviarlo con SendUserFile.
- Commit y push a la rama de **este** chat solo de lo propio: `geoda/videos/<IDs del lote>/`, voces usadas en
  `geoda/kit/VOCES.md` (como referencia), recursos nuevos reutilizables en `geoda/kit/`. No subir mp4 finales ni clips pesados (van en assets.json).
  Cambios al montador (`builder.py` y tools) solo si son compatibles con lo anterior, y decirlo en el commit y a Camilo.
- Resumen final: videos entregados, costo por video y total, y lo pendiente (p. ej. founder sin material real).

## 4. Problemas conocidos
- Cuota diaria de Gemini TTS (compartida entre chats): una sola petición por personaje y video; `tts_multi.py` prueba varios
  modelos. Si se agota: decirle a Camilo y seguir con lo visual; no cambiar de voz a mitad de un personaje.
- Palabras en inglés o siglas se dicen como suenan en español: "POV" = una sola palabra "pov" (en el texto para TTS escribir
  "Pob:"; "POV" lo deletrea y "Pov" a veces se come la "p"). Verificar con STT y contando sílabas en la señal.
- Gemini texto: usar `gemini-3.1-flash-lite-preview` (los otros suelen estar en 429).
- Higgsfield por MCP puede estar sin créditos: usar la API REST (`hf.sh`), que sí tiene.
- Clips de Kling con la etiqueta mala: usar el tramo bueno, cambiar por foto real animada, o `label_fix.py --tube --wipe --fit`
  (si la etiqueta nativa se ve bien, dejarla: Camilo prefiere la nativa a una sobrepuesta).
- Imágenes de IA pueden meter la piedra antes de tiempo o billetes en dólares: decirlo en el prompt ("pesos colombianos",
  "the stone is NOT in this scene").
