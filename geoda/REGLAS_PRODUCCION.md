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
   - Nunca dejar que la IA invente o deforme la etiqueta: revisar cada toma donde aparezca el producto.
   - Si la etiqueta sale deformada: se reemplaza la toma por material real de la landing o se superpone la etiqueta real.
   - No hacer zoom digital sobre el producto en clips de IA de 720p (deforma la etiqueta).
   - Los primeros planos del producto se generan en 1080p o se hacen con fotos/videos reales.
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
14. Tomas donde el avatar habla: **WAN 3.0** con audio nativo en la API de Higgsfield (US$0,075/s en 720p): mejor calidad/precio
    (Veo no está en la API; solo en la cuenta web). Imagen de inicio con aire sobre la cabeza para el texto del hook.

## Costos y herramientas
15. Usar la **API de Higgsfield** (secreto de red) para generar. No hacer pruebas A/B: usar directo el de mejor calidad/precio.
16. Generación en **720p** (Kling 3.0 estándar, US$0,071/s) para tomas sin diálogo; exportación final **1080×1920, 30 fps, H.264**.
17. Ahorro: reutilizar escenas que encajen con el guion, b-roll gratis (Mixkit), imágenes gratis (Magnific, 20/día;
    si se agotan, Higgsfield 1k calidad media, US$0,053), voz gratis (Gemini TTS), música y efectos de Mixkit.
18. Informar el costo en USD de cada video al terminarlo.

## Entrega
19. Nombres según el brief: `GEO_[ETAPA]_[ÁNGULO]_[NN]_[HOOK]_[FORMATO]_v[n].mp4`, un archivo por hook (A y B).
20. **Avisar al celular** (notificación push) con cada respuesta.
