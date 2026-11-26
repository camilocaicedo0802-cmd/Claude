# GEODA · Reglas de producción de los 60 videos

Ajustes acordados con Camilo. Se aplican a **todos** los videos, a los ya hechos (al corregirlos) y a los próximos.
El montador (`pipeline/builder.py`) ya trae estas reglas por defecto.

## Contenido y guion
1. **El brief manda**: guion, `prompt_visual_IA`, CTA y reglas de compliance de cada video salen del **brief corregido**
   (`brief_v2/guiones_60.json`, reglas en `brief_v2/brief_reglas.txt`; reemplaza al CSV anterior). Cambios solo cuando el producto real lo exige (ej.: es un stick con tapa, no una caja).
2. **Sin precios** en voz ni en pantalla, salvo que Camilo lo indique.
3. **Black Friday** solo si la oferta de temporada es real; si no, CTA neutro (K3, K5, K6, K7). Cuando haya duda se exportan las dos versiones.
4. **Sin el rótulo "Recreación con IA"** en ningún video. Al publicar, activar la etiqueta de contenido IA de Meta/TikTok.
5. **Etiqueta del producto tal cual la landing en TODAS las tomas** (Desodorante · GEODA · 100% NATURAL · EFECTIVO Y SEGURO · 24h).
   - **Etiqueta perfecta o sin etiqueta**: si la etiqueta no puede quedar bien pegada sobre el tubo, la toma se cambia, se recorta
     (encuadre sin el producto) o se deja el tubo sin etiqueta. Nunca letras dobles, fantasmas ni etiqueta que se salga del tubo.
   - Revisión cuadro a cuadro a resolución completa de cada toma con producto, y solo se usan los tramos limpios
     (cuando el stick gira de lado, se corta antes; si hace falta, el tramo bueno va en cámara lenta).
   - **Primeros planos nuevos**: imagen 1k con la foto real del producto como referencia (Higgsfield marketing-studio, US$0,053)
     → Kling 3.0 720p sin giros (para planos quietos, misma imagen de inicio y de fin) → `pipeline/label_fix.py --tube --wipe`.
   - Si el clip ya trae la etiqueta bien (sale de una imagen hecha con la foto real del producto y no gira), se deja la
     etiqueta original del clip, sin capa encima (pedido de Camilo en A1-05, 0:32). Aplica a los videos desde el A1-05;
     A1-01 a A1-04 se dejan como están.
   - Si existe una foto real del producto que sirva para la toma, se usa la foto fija (ej. `mano.png`) en vez del clip animado.
   - `label_fix.py`: detecta la etiqueta (SIFT contra la etiqueta real), borra la zona (`--wipe`), pega las letras reales con la luz
     del tubo, la recorta a la silueta del tubo (`--tube`) y deja los dedos por delante. `--flip` = etiqueta invertida.
   - **Etiqueta quieta sobre el tubo**: se mueve solo con el producto. El movimiento cuadro a cuadro sale del flujo óptico
     del tubo y la detección solo corrige la deriva lenta (sin temblor ni "nado" de la etiqueta).
   - **Zoom lento (Ken Burns) con precisión de subpíxel** (no `zoompan` de ffmpeg, que avanza a saltos de 1 px).
   - Con luz cálida (sets, interiores) el tubo blanco se ve anaranjado: la detección de piel y la silueta del tubo se ajustan al
     tono propio del tubo para no confundirlo con la mano. Si la IA inventa otra etiqueta (otro diseño), se borra el cuerpo del
     tubo y se pega la real con las proporciones del producto (52 % del alto del cuerpo, 94 % del ancho).
   - **Orientación real**: con la piedra hacia abajo (ej. pasándola por el antebrazo) la etiqueta se ve invertida (`--flip`).
   - No hacer zoom digital fuerte sobre el producto en clips de 720p.
   - Ningún texto, subtítulo ni gráfico (X roja, íconos) tapa la etiqueta: el montador detecta su zona en cada plano.
5b. **Agua**: se moja solo la punta de la piedra (gotas o un hilo de agua sobre la piedra). El tubo y la etiqueta quedan secos;
    nunca chorro sobre todo el tubo.
6. En grabaciones de la landing no mostrar las tarjetas con "Te dura 3/5 años" ni precios tachados.

## Hook
7. Texto del hook visible desde el **fotograma 1** hasta el **segundo 3**, en dos líneas y dos colores (blanco + amarillo).
   Si al seguir en pantalla taparía una cara del plano siguiente, se corta al terminar el hook.
8. La voz arranca en el fotograma 1. Fotograma 1 con interrupción de patrón (impacto, movimiento, objeto inesperado).

## Textos y subtítulos
9. **Ningún texto pisa la cara** de una persona ni de un personaje (plastilina, Pixar), con separación clara
   (detector de rostros + cajas manuales para personajes animados; margen arriba por el pelo y bajo el mentón).
10. **Subtítulos siempre**, palabra por palabra, **en la parte de abajo** (y≈1450 en 1080×1920) y tamaño 66 px.
    Solo suben si abajo hay una cara o un gráfico clave (ej.: la X roja); nunca bajan de la zona de la UI de TikTok/Reels.
11. **No repetir textos**: si el titular (texto en pantalla del guion) dice lo mismo que la voz, se quita el titular y queda el subtítulo.
    Si el texto del hook dice lo mismo que la voz, queda el texto del hook sin subtítulo.
    Con la tarjeta CTA en pantalla no hay subtítulo. Los emojis del guion (❌ ✅ 💧 💨) van como íconos sin texto.

## Voces y avatares
12. **Voces alternadas por video**: mujer, hombre, mujer, hombre… (A1-02 mujer, A1-01 hombre, A1-03 mujer, A1-04 hombre, …).
    Una sola voz por video (mismo modelo y misma voz en todas sus frases).
13. El avatar **habla a cámara solo en algunos videos/tomas** donde haga falta (UGC, street interview, podcast, testimonio, founder).
13b. **Videos con dos personajes (podcast, entrevista)**: un solo clip largo de WAN 3.0 por personaje con todas sus frases
    (máx. 30 s; si no alcanza, el segundo clip arranca del último cuadro del primero), así cada voz es la misma en todo el video.
    **La conversación va completa y tal cual el guion**: nunca se confía en los tiempos por palabra que da el modelo
    (se desfasan hasta 1-2 s). Se miden las pausas reales del audio (`pipeline/tools/pauses.py`), se arma cada frase con sus
    tramos y se verifica transcribiendo cada frase sola (`pipeline/tools/verify_lines.py`): debe decir exactamente el guion,
    sin palabras de la frase vecina. Si hay duda en una palabra, pregunta cerrada con opciones (`pipeline/tools/choice.py`).
    Cada corte cae en silencio (se comprueba la energía en los bordes). Si el que habla hace algo que no sirve (ej. gira el
    producto), se corta al otro escuchando o a un inserto, pero la voz sigue completa.
    **Sincronía de labios**: la voz que suena siempre es de quien mueve la boca en pantalla. Si se corta al otro personaje
    (escuchando) o a un plano general, se usa solo un tramo donde esa persona tiene la boca quieta (se mide el movimiento
    de la boca cuadro a cuadro) y, en el plano general, el tramo en que habla quien tiene la voz.
    Efecto de sonido suave en cada corte de conversación (el brief pide sonido en cada corte).
14. Tomas donde el avatar habla: **WAN 3.0** con audio nativo en la API de Higgsfield (US$0,075/s en 720p): mejor calidad/precio
    (voz 9,5/10; Veo no está en la API, solo en la cuenta web). Imagen de inicio con aire sobre la cabeza para el texto del hook.

## Costos y herramientas
15. Usar la **API de Higgsfield** (secreto de red) para generar. No hacer pruebas A/B: usar directo el de mejor calidad/precio.
16. Generación en **720p** (Kling 3.0 estándar, US$0,071/s) para tomas sin diálogo; exportación final **1080×1920, 30 fps, H.264**.
17. Ahorro: reutilizar escenas que encajen con el guion, b-roll gratis (Mixkit), imágenes gratis (Magnific, 20/día;
    si se agotan, Higgsfield 1k calidad media, US$0,053), voz gratis (Gemini TTS), música y efectos de Mixkit.
18. Informar el costo en USD de cada video al terminarlo.

## CTA
21. **Tarjeta final con ambiente** (desde el A1-05): el producto real (recorte de la foto de la landing) va sobre un baño o
    ambiente que lo haga lucir (mesón, luz natural, plantas, toalla), no sobre un fondo blanco liso.

## Brief corregido (v2): reglas nuevas
22. **Awareness por etapa**: TOFU = problema/mito/dato primero, el producto entra tarde como descubrimiento y el CTA empieza
    con "Se llama GEODA…"; sin marca en el hook ("tu piedra", "tu GEODA"), sin combos ni precio por mes. MOFU compara y rompe
    objeciones (nunca empieza con la oferta). BOFU: oferta, combo, garantía, contraentrega.
23. **Compliance**: nada de primeros planos de la axila ni zooms al cuerpo (planos medios con ropa); no decir "24 horas",
    "100 % natural", "sin aluminio", "antitranspirante", segundos de aplicación, ni otra duración que "1 piedra dura 1 año";
    sin preguntas por atributos personales; nadie de la calle/IA cuenta resultados como real.
24. **Ritmo**: plano nuevo cada 2,5-3 s; cortar respiraciones y pausas de más de 0,3 s; efecto de sonido en cada corte
    (en conversaciones, suave); loop abierto en los primeros 6 s.
25. **Producto real**: en pantalla antes del segundo 10, al menos un plano real de 2-3 s (macro o en la mano) y en el cierre;
    los últimos 2-3 s: producto real + CTA en texto + "Pago contraentrega · Envío gratis".
26. **Duración por etapa**: TOFU 21-39 s · MOFU 30-51 s · BOFU 18-24 s.
27. **Versiones**: cada corrección se sube como v2, v3… (no se sobrescribe).
28. **Etiqueta encajada al tarro**: ocupa el 94 % del ancho visible del tubo, centrada (como en la foto de la landing);
    `label_fix.py --fit` mide los bordes reales del tubo. Si el stick está inclinado en la mano, se sigue el giro sin recentrar.

## Decisiones de Camilo sobre el brief corregido (25-nov)
29. **Sin rótulo 'Recreación con IA'** (decisión final de Camilo, 25-nov): se quitó de todos los videos (A1-01 v3, A1-04 v3,
    A1-05 v6, A1-06). Al publicar, activar la etiqueta de contenido IA de la plataforma (ver regla 4).
30. **Sin precios** salvo que Camilo lo indique: el CTA Black Friday va como 'Paga 2 lleva 3', sin $99.990.
31. **Zona segura del brief**: ~250 px arriba, 450-670 px abajo y 140 px a la derecha libres de texto (montador: SAFE_TOP 250,
    SAFE_BOT 1250, SAFE_RIGHT 940); el botón/toque de la landing también se baja fuera de la barra superior.
32. **UGC con avatar = voz en off (storytime)**: la avatar no mueve los labios; una sola toma de voz por personaje
    (`tools/tts_multi.py`), cortada por pausas y verificada frase por frase. Así nunca hay labios desfasados.
33. **Hooks animados sobre fotos reales** (destellos, tachado, X que cae, reloj) en vez de pedirle a la IA que mueva el
    producto: la etiqueta queda perfecta. Los subtítulos no tapan la piedra ni la etiqueta (`sub_y` por fila si hace falta).

35. **Personajes**: pueden ser distintos en cada video; dentro de un video, cada personaje conserva su cara y su voz.
36. **Avatar siempre en video** (desde el A1-06): nunca imágenes fijas de una persona/avatar; cada vez que sale, es un clip
    haciendo una acción. Solo tramos con la boca cerrada mientras suena una voz que no es suya (o tomas de espaldas, de lejos
    o en primera persona). Fotos fijas solo para producto, fondos y gráficos.
37. **Siglas y palabras en inglés** se pronuncian completas y como suenan en español: "POV" se dice "pov" (una palabra), nunca deletreado.
38. **Nada se repite entre el hook y el cuerpo**: si el guion pone la misma frase en el hook y en el primer plano, en esa
    variante la frase queda solo en el hook y ese plano se QUITA (no se dejan planos sin voz); para no salir del rango de
    duración se alargan un poco los demás planos con acción y el cierre.

39. **Nada de escenas estáticas** (Camilo, 25-nov): todos los planos se mueven. Personas, fondos y producto son video
    (Kling/WAN o animación propia); una foto fija con zoom NO cuenta. Producto real: la foto real animada (giro, destellos,
    brillo) o fondo en video + producto compuesto cuadro a cuadro (`tools/endcard_anim.py`). Cierre: `kit/producto/endcard_bano_anim.mp4`.
40. **La piedra no deja residuo**: nunca marca blanca, espuma, polvo, crema ni rastro tipo roll-on en la piel o la ropa; la piedra
    es un cristal translúcido que no cambia de forma. Revisar la piel cuadro a cuadro después de cada pasada y usar solo los tramos
    limpios. Truco que funciona: el tramo limpio del clip en ida y vuelta (parece pasadas suaves); en el antebrazo, el tramo inicial
    antes de que aparezca brillo. (Kling con el mismo cuadro de inicio y fin deja la escena casi quieta: no sirve.)
41. **Entrevistas en la calle**: la toma inicial (hook) muestra el plano completo de la entrevista, presentador y entrevistado
    en cuadro, con el presentador haciendo la pregunta con el micrófono (solo él mueve los labios).

42. **Un hook distinto por versión** (Camilo, 25-nov): si un video sale con varios CTA (principal + alternos), cada versión
    arranca con un hook diferente. HA y HB del brief van con el CTA principal; para cada CTA alterno se escriben hooks nuevos
    (HC, HD, …): creativos y llamativos, con escenas distintas a las del cuerpo y a los otros hooks, mismo estilo, misma voz
    y mismas reglas (tercera persona o POV, sin preguntar por atributos personales, sin marca en TOFU). Nombre:
    GEO_..._HC_<FORMATO>_<CTA>_v1.mp4.

43. **Siempre pantalla completa** (Camilo, 25-nov): nunca el video reducido con fondo borroso (`framed`). Si el texto no cabe,
    se busca la zona libre del cuadro (cielo, pared, cuerpos sin caras) con `hook_slots`, `hook_cx` + `hook_maxw` (bloque
    más angosto a un lado) y, para subtítulos, `sub_y` + `sub_cx` + `sub_scale`. Ningún texto sobre caras ni sobre la piedra.

44. **Ningún título ni texto tapa una cara** (Camilo, A1-08), tampoco el pelo o la frente. En planos con persona se genera la
    imagen con el 40 % de arriba vacío (pared/techo) y la cabeza en el centro, Kling con cámara fija, y se ponen cajas
    manuales de cabeza/producto en el montaje. Si no cabe arriba, el texto va al pecho (debajo de la barbilla), nunca encima.

## Entrega
34. Carpeta `GEODA_60/TOFU|MOFU|BOFU/A1…` con las versiones vigentes, `CTA_alternos/` para los re-exports de CTA y un
    `LEEME.txt`; se envía también como .zip.
19. Nombres de ENTREGA (formato de Camilo, 25-nov, desde el lote 2): `<Ángulo> GEO <ETAPA>-<A#>-<NN>-Hook <X>.mp4`,
    ej. `La piedra no te falló GEO MOFU-A1-05-Hook A.mp4`. Cada versión tiene su hook (A, B, C, D…), así que el CTA alterno no
    va en el nombre. Correcciones de algo ya entregado: ` v2`, ` v3`… al final. El montaje usa internamente el nombre técnico
    (GEO_MOFU_A1_05_HA_PODCAST_v6) y `pipeline/tools/nombre_entrega.py` lo traduce al copiar a la carpeta de entrega.
20. **Avisar al celular** (notificación push) con cada respuesta.
