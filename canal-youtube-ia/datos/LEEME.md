# Diccionario de datos

Consulta: 27 de octubre de 2026. Todas las cifras son públicas o de vidIQ. Ninguna es una métrica privada (CTR, retención, ingresos).

## `videos.csv`

| Columna | Significado |
|---|---|
| `handle` | Canal (sin @) |
| `tab` | `long` (video) o `short` (Short) |
| `id`, `url` | Identificador y enlace del video |
| `title` | Título **original**. Los canales en español y vietnamita se descargaron con su idioma; YouTube muestra traducciones a otros públicos |
| `title_en` | Título traducido que YouTube muestra en inglés, solo en canales no angloparlantes |
| `date` | Fecha de publicación |
| `date_src` | `vidiq` o `yt-dlp` = exacta; `approx` = deducida de "hace X días/meses" (±1 mes en lo reciente, varios meses en videos de más de un año); vacío = sin fecha |
| `age_days` | Días desde la publicación hasta el 27-oct-2026 |
| `duration` | Segundos |
| `views` | Vistas a la fecha de consulta |
| `views_src` | `vidiq`/`yt-dlp` = exactas; `rounded` = de la lista pública, redondeadas (±15 % en 296 videos verificados). Un 0 con `rounded` significa dato ausente |
| `likes`, `comments` | Solo con datos exactos |
| `like_rate` | Likes ÷ vistas × 100 |
| `comment_rate` | Comentarios por cada 1.000 vistas |
| `chapters` | Número de capítulos (solo con datos de yt-dlp) |
| `neigh_median` | Mediana de vistas de los 10 videos publicados alrededor (5 antes y 5 después), en el mismo formato |
| `multiple` | `views ÷ neigh_median`. Es el indicador principal de rendimiento relativo |
| `chan_median` | Mediana de vistas de todo el canal en ese formato |
| `views_per_day` | `views ÷ age_days`. Sirve para comparar videos recientes; favorece a los muy recientes que aún están en su pico |
| `thumb` | Enlace a la miniatura pública |
| `desc_first_line` | Primera línea de la descripción |

## `canales.csv`

Una fila por canal. Columnas no obvias:

- `video_mas_antiguo_con_fecha_exacta`: el video más antiguo **entre los que tienen fecha exacta**. No siempre es el primer video del canal.
- `subidas_por_semana_90d`: publicaciones (videos y Shorts) de los últimos 90 días ÷ 12,86 semanas. En Squire Explains, que tiene 4 semanas de vida, el ritmo real es de ~9 por semana.
- `pct_vistas_top10pct_videos`: porcentaje de todas las vistas que suma el 10 % de videos con más vistas. Mide cuánto depende el canal de unos pocos éxitos.
- `pistas_audio_doblaje`: número de pistas de audio en los videos revisados. Es una muestra, no todos los videos.
- `fecha_1k_subs`, `fecha_10k_subs`: primer día del historial de vidIQ con al menos ese número de suscriptores.

Las medianas excluyen los videos con 0 vistas por dato ausente.

## `hitos_crecimiento.csv`

Hitos extraídos del historial diario de vidIQ. La columna `video_asociado` relaciona un salto de crecimiento con los videos publicados justo antes. **Esa relación es una hipótesis por coincidencia de fechas, no una causa demostrada.**

## `crudos-2026-10-27.tar.gz`

- `flatdate/`: listas de yt-dlp con fechas aproximadas.
- `flatorig/`: listas con títulos en idioma original (Te Lo Pinto Fácil, Estrictamente, Lịch Sử Ngoại Truyện).
- `full/`: metadatos por video de yt-dlp (incluye capítulos y pistas de audio).
- `vidiq/`: respuestas de `vidiq_get_videos_by_ids` y el historial diario de Te Lo Pinto Fácil.

Los historiales diarios de los demás canales se consultaron, pero solo se guardaron sus hitos.

## Fase 2

- `suscriptores_series.csv`: puntos de suscriptores por fecha tomados del historial diario de vidIQ (cada día en canales recientes; días 1 y 15 de cada mes en Te Lo Pinto Fácil). Los suscriptores "al publicar" de `videos_fase2.csv` se **interpolan linealmente** entre esos puntos: son una estimación, con error de unos días.
- `videos_fase2.csv`: los 97 videos seleccionados. `categorias` puede combinar `absoluto`, `relativo`, `reciente`, `canal_pequeno` (los que más vistas por suscriptor sacaron con el canal por debajo de 20.000 suscriptores) y `contraste` (peor múltiplo con datos exactos). `views_per_sub` = vistas actuales ÷ suscriptores al publicar.
- `videos_analizados.csv`: añade rasgos automáticos del título (pregunta, número, superlativo o totalidad, segunda persona) y codificación manual:
  - `sistema_miniatura` y `texto_miniatura`: revisados en las hojas de miniaturas.
  - `produccion_interior`: según los 3 fotogramas automáticos que YouTube publica de cada video; describe el canal, no cada video.
  - `hook`, `estructura`, `llamada_a_la_accion`: solo en los 12 videos con transcripción leída (`transcrito = sí`).

Las transcripciones completas no se guardan en el repositorio por derechos de autor. El informe cita fragmentos breves.

## Fase 3

- `keywords_vidiq.csv`: transcripción de las 5 consultas de palabras clave de vidIQ (modo `research`, con país México o Colombia). Volumen, competencia y puntuación son índices de vidIQ de 0 a 100. `busquedas_mensuales_estimadas` es la estimación de vidIQ para el texto exacto en todos los países. `volumen_pais_consulta` y `mercados_principales` vacíos significan "desconocido", no 0.
- `autocompletar_youtube_2026-10-27.json`: sugerencias del autocompletado de YouTube (`suggestqueries.google.com`, `ds=yt`, `hl=es`) para México, Colombia y Argentina, por grupo de semillas; la clave `ampliacion` tiene la segunda tanda. Indica qué se escribe, sin volumen. Script: `scripts/autocompletar_youtube.py`.
- `outliers_es_historia.csv`: los 42 videos largos en español que vidIQ devolvió como "breakout" para "historia" (últimos 6 meses). La columna `relevante_para_el_nicho` (sí / parcial / no) es mi clasificación.

## Fases 5 y 8

- `matriz_nicho.csv`: puntuaciones (1 a 5) de las 6 opciones de nicho en los 12 criterios, con pesos y total sobre 100. Las puntuaciones son juicios apoyados en las fases 1 a 4, no mediciones. Script: `scripts/matriz_nicho.py` (incluye el análisis de sensibilidad).
- `banco_ideas.csv`: 16 ideas de video con pilar, término de búsqueda principal, evidencia de demanda (vidIQ o autocompletado), puntos en los 8 criterios de la fase 8, total sobre 100 y decisión (≥ 75 producir pronto; 60–74 banco; < 60 reformular o descartar). Script: `scripts/banco_ideas.py`. La hoja "Ideas" del dashboard parte de este archivo.
