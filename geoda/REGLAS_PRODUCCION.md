# GEODA · Reglas de producción de los 60 videos

Ajustes acordados con Camilo. Se aplican a **todos** los videos, a los ya hechos (al corregirlos) y a los próximos.
El montador (`pipeline/builder.py`) ya trae estas reglas por defecto.

## Contenido y guion
1. **El brief manda**: guion, `prompt_visual_IA`, CTA y reglas de compliance de cada video salen del brief
   (`guiones_60_videos.csv`). Cambios solo cuando el producto real lo exige (ej.: es un stick con tapa, no una caja).
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
    Sin "whoosh" en cada corte de conversación, solo al entrar a insertos.
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

## Entrega
19. Nombres según el brief: `GEO_[ETAPA]_[ÁNGULO]_[NN]_[HOOK]_[FORMATO]_v[n].mp4`, un archivo por hook (A y B).
20. **Avisar al celular** (notificación push) con cada respuesta.
