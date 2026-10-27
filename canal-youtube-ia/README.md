# Canal de YouTube con IA: investigación y plan

Proyecto para diseñar, desde la evidencia, un canal de YouTube con producción asistida por IA, identidad propia y una ruta realista a la monetización.

## Estado (27-oct-2026)

| Fase | Estado | Documento |
|---|---|---|
| Metodología, accesos y requerimientos | Hecho | [`01-metodologia.md`](01-metodologia.md) |
| Fase 1: análisis de los 8 canales | Hecho (datos, crecimiento, modelo de contenido, miniaturas) | [`02-analisis-canales.md`](02-analisis-canales.md) |
| Fase 2: mejores videos | Hecho: 97 videos seleccionados y codificados, 12 transcripciones leídas, fotogramas revisados | [`03-ranking-videos.md`](03-ranking-videos.md), [`04-fase2-mejores-videos.md`](04-fase2-mejores-videos.md) |
| Fases 3 a 12 | Pendientes | — |

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

Las preguntas están en [`01-metodologia.md`](01-metodologia.md#5-lo-que-necesito-de-ti): país, idioma, horas, presupuesto, si animas tú, voz y temas vetados. Mientras no respondas, avanzo con los supuestos indicados allí.
