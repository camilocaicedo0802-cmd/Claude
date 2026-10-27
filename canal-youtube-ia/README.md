# Canal de YouTube con IA: investigación y plan

Proyecto para diseñar, desde la evidencia, un canal de YouTube con producción asistida por IA, identidad propia y una ruta realista a la monetización.

## Estado (27-oct-2026)

| Fase | Estado | Documento |
|---|---|---|
| Metodología, accesos y requerimientos | Hecho | [`01-metodologia.md`](01-metodologia.md) |
| Fase 1: análisis de los 8 canales | Hecho (datos, crecimiento, modelo de contenido, miniaturas) | [`02-analisis-canales.md`](02-analisis-canales.md) |
| Fase 2: mejores videos | Hecho: 97 videos seleccionados y codificados, 12 transcripciones leídas, fotogramas revisados | [`03-ranking-videos.md`](03-ranking-videos.md), [`04-fase2-mejores-videos.md`](04-fase2-mejores-videos.md) |
| Fase 3: palabras clave (español, Latinoamérica) | Hecho con los 35 créditos disponibles; quedan volúmenes sin medir hasta el 27-nov | [`05-fase3-palabras-clave.md`](05-fase3-palabras-clave.md) |
| Fase 4: patrones y matriz comparativa | Hecho | [`06-fase4-patrones.md`](06-fase4-patrones.md) |
| Fase 10: políticas y monetización (adelantada) | Hecho con fuentes oficiales; incluye el cambio de requisitos del 1-feb-2027 | [`07-fase10-monetizacion-politicas.md`](07-fase10-monetizacion-politicas.md) |
| Fase 5: nicho y posicionamiento | Hecho: matriz ponderada de 6 opciones con análisis de sensibilidad | [`08-fase5-nicho.md`](08-fase5-nicho.md) |
| Fase 6: identidad visual | Hecho: nombres comprobados, paleta, tipografías, estilo, prompts y bocetos | [`09-fase6-identidad.md`](09-fase6-identidad.md), [`marca/`](marca/) |
| Fase 7: producción con IA | Hecho: 18 etapas con herramientas, costes, licencias y horas | [`10-fase7-produccion.md`](10-fase7-produccion.md) |
| Fase 8: SEO y empaquetado | Hecho: puntuación de ideas y 6 paquetes de lanzamiento | [`11-fase8-seo-empaquetado.md`](11-fase8-seo-empaquetado.md) |
| Fase 9: retención y estructura | Hecho | [`12-fase9-retencion.md`](12-fase9-retencion.md) |
| Fase 11: plan de 90 días | Hecho: del 2-nov-2026 al 31-ene-2027, con escenarios | [`13-fase11-plan-90-dias.md`](13-fase11-plan-90-dias.md) |
| Fase 12: dashboard | Hecho y verificado | [`dashboard_canal.xlsx`](dashboard_canal.xlsx), [`14-fase12-dashboard.md`](14-fase12-dashboard.md) |
| **Reporte completo (14 entregables)** | **Hecho** | [**`00-REPORTE-COMPLETO.md`**](00-REPORTE-COMPLETO.md) · PDF: [`reporte/Reporte-completo-canal-youtube-IA.pdf`](reporte/Reporte-completo-canal-youtube-IA.pdf) |

## Canales analizados (lote 1)

[@ThePaintExplainer](https://www.youtube.com/@ThePaintExplainer) · [@SimplePaintOfficial](https://www.youtube.com/@SimplePaintOfficial) · [@TeloPintoFacil](https://www.youtube.com/@TeloPintoFacil) · [@SomeGuyWhoKnowsStuff](https://www.youtube.com/@SomeGuyWhoKnowsStuff) · [@thecrookedexplainer](https://www.youtube.com/@thecrookedexplainer) · [@estrictamente](https://www.youtube.com/@estrictamente) · [@lichsungoaitruyen](https://www.youtube.com/@lichsungoaitruyen) · [@SquireExplains](https://www.youtube.com/@SquireExplains)

## Datos

| Archivo | Contenido |
|---|---|
| [`datos/canales.csv`](datos/canales.csv) | Una fila por canal: creación, totales, ritmo, medianas, concentración, engagement, hitos |
| [`datos/videos.csv`](datos/videos.csv) | 1.020 videos y Shorts con vistas, fecha, duración y rendimiento relativo |
| [`datos/hitos_crecimiento.csv`](datos/hitos_crecimiento.csv) | Momentos clave del crecimiento según el historial diario de vidIQ |
| [`datos/suscriptores_series.csv`](datos/suscriptores_series.csv) | Suscriptores por fecha (puntos de vidIQ), para interpolar los suscriptores al publicar |
| [`datos/videos_fase2.csv`](datos/videos_fase2.csv) | Los 97 videos de la fase 2 con su categoría y suscriptores al publicar |
| [`datos/videos_analizados.csv`](datos/videos_analizados.csv) | Lo anterior + rasgos del título, sistema y texto de miniatura, nivel de producción, y gancho, estructura y llamada a la acción de los 12 transcritos |
| [`datos/keywords_vidiq.csv`](datos/keywords_vidiq.csv) | 89 filas de palabras clave de vidIQ (volumen, competencia, búsquedas estimadas, crecimiento, mercados) |
| [`datos/autocompletar_youtube_2026-10-27.json`](datos/autocompletar_youtube_2026-10-27.json) | Sugerencias del autocompletado de YouTube por semilla y país (México, Colombia, Argentina) |
| [`datos/outliers_es_historia.csv`](datos/outliers_es_historia.csv) | 42 videos en español que superaron a su canal ("historia", últimos 6 meses), con relevancia para el nicho |
| [`datos/matriz_nicho.csv`](datos/matriz_nicho.csv) | Matriz ponderada de las 6 opciones de nicho (fase 5) |
| [`datos/banco_ideas.csv`](datos/banco_ideas.csv) | 16 ideas de video puntuadas con el sistema de la fase 8 |
| [`datos/LEEME.md`](datos/LEEME.md) | Diccionario de columnas, fuentes y márgenes de error |
| `datos/crudos-2026-10-27.tar.gz` | Respuestas originales de yt-dlp y vidIQ, para rehacer cálculos sin volver a consultar |

Las miniaturas de terceros que revisé no se guardan en el repositorio, por derechos de autor. Se enlazan desde `videos.csv` (columna `thumb`).

## Cómo rehacer o ampliar los datos

Rehacer los cálculos con los datos guardados, sin consultar YouTube ni vidIQ (comprobado: da el mismo `videos.csv` y el mismo ranking):

```bash
mkdir -p trabajo/data && tar xzf datos/crudos-2026-10-27.tar.gz -C trabajo/data
python3 scripts/construir_dataset.py ./trabajo 2026-10-27   # -> trabajo/data/videos.csv
python3 scripts/ranking_videos.py trabajo/data/videos.csv > 03-ranking-videos.md
```

Añadir canales nuevos:

```bash
pip install yt-dlp pillow
BASE=./trabajo scripts/recolectar.sh @Canal1 @Canal2        # listas públicas -> trabajo/data/flatdate
```

Los datos exactos por video y el historial diario se piden a vidIQ. Están en el archivo de crudos y cuestan créditos: ver `01-metodologia.md`, sección 2.

## Decisiones pendientes de ti

La lista por prioridad está en el entregable 13 del [reporte completo](00-REPORTE-COMPLETO.md#entregable-13-próximas-decisiones-por-prioridad). Las cinco primeras: confirmar el nicho y el nombre, tus horas semanales reales, tu país de residencia, la voz y si ya pagas Adobe Creative Cloud.

Regenerar el dashboard y las puntuaciones:

```bash
python3 scripts/banco_ideas.py      # -> datos/banco_ideas.csv
python3 scripts/matriz_nicho.py     # -> datos/matriz_nicho.csv
python3 scripts/dashboard.py        # -> dashboard_canal.xlsx (abrir y recalcular, o recalcular con LibreOffice)
python3 scripts/reporte_pdf.py FUENTES  # -> reporte/*.pdf (markdown-it-py, pypdf y Playwright de Node; FUENTES = carpeta con local.css de Google Fonts)
```
