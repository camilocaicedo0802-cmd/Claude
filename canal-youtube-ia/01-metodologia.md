# Metodología, accesos y lo que necesito de ti

Este documento responde a la primera petición del proyecto: cómo organizo el análisis, qué datos puedo conseguir y cuáles no, cómo compartirme canales, cómo trabajar por lotes, qué información tuya necesito y en qué orden vamos a trabajar.

## 1. Cómo organizo el análisis

Cada canal pasa por el mismo proceso, en este orden. Así un canal del lote 3 se puede comparar con uno del lote 1.

| Paso | Qué hago | Herramienta | Resultado |
|---|---|---|---|
| 1. Ficha cuantitativa | Fecha de creación, suscriptores, vistas, videos, frecuencia, duración, idioma original, pistas de audio dobladas | Página pública del canal + yt-dlp | `datos/canales.csv` |
| 2. Historial de crecimiento | Suscriptores, vistas y videos día a día desde la creación | vidIQ (`channel_stats`) | `datos/hitos_crecimiento.csv` |
| 3. Inventario de videos | Todos los videos y Shorts públicos, con vistas y fecha | yt-dlp (lista) + vidIQ (datos exactos de los candidatos) | `datos/videos.csv` |
| 4. Rendimiento relativo | Múltiplo de cada video sobre la mediana de sus 10 vecinos (5 antes, 5 después) | Script propio | `03-ranking-videos.md` |
| 5. Revisión visual | Hojas de contacto con las miniaturas de los mejores y los peores videos de cada canal, revisadas imagen por imagen | Descarga de miniaturas públicas | Sección "Miniaturas" de cada ficha |
| 6. Lectura profunda (fase 2) | Transcripción, hook, estructura, ritmo, recursos visuales de 10 a 20 videos por canal | Subtítulos públicos o vidIQ (`video_transcript`) | Pendiente |
| 7. Comparación cruzada (fase 4) | Matriz de patrones con evidencia y facilidad de adaptación | Todo lo anterior | Pendiente |

**Por qué el "múltiplo sobre los vecinos" y no la media del canal.** Un canal que pasó de 1.000 a 100.000 suscriptores tiene una media histórica que no sirve para juzgar ni sus primeros videos ni los últimos. Comparar cada video con los 10 publicados a su alrededor, en el mismo formato (largo o Short), aísla el efecto del tema y del empaquetado del efecto del tamaño del canal en ese momento. Es el mismo principio de los "outliers" de vidIQ, pero calculado con todos los videos del canal y no con una muestra.

**Cómo etiqueto la evidencia.** En todos los documentos:

- **Dato**: medido, con fuente y fecha de consulta.
- **Estimación**: calculada a partir de datos con un supuesto explícito.
- **Hipótesis**: interpretación mía que hay que validar. Nunca la presento como causa.

## 2. Qué puedo obtener directamente y qué no

Probado en esta sesión, no supuesto.

| Información | Fuente | ¿Acceso? | Coste y límites |
|---|---|---|---|
| Lista completa de videos y Shorts con título, duración y vistas | YouTube público (yt-dlp) | Sí | Gratis. Una petición por pestaña. Las vistas vienen redondeadas (±15 % frente al dato exacto en 296 videos verificados) y algunas vienen en 0 |
| Fecha exacta, vistas exactas, likes, comentarios, descripción, etiquetas | vidIQ (`get_videos_by_ids`) o yt-dlp video a video | Sí | vidIQ: 5 créditos por cada 50 videos. yt-dlp video a video provoca bloqueos de YouTube (ver nota) |
| Idioma original, títulos traducidos, pistas de audio dobladas | yt-dlp | Sí | Gratis. Descubrí así que Te Lo Pinto Fácil, Estrictamente y Lịch Sử Ngoại Truyện publican en español y vietnamita: YouTube me mostraba sus títulos traducidos al inglés |
| Fecha de creación, país declarado, totales | Página "Acerca de" | Sí | Gratis |
| Historial diario de suscriptores y vistas | vidIQ (`channel_stats`) | Sí | 5 créditos por canal |
| Miniaturas | Servidor público de imágenes de YouTube | Sí | Gratis. Las reviso como imagen, no las describo por el título |
| Transcripciones | Subtítulos públicos (yt-dlp) o vidIQ (`video_transcript`) | Parcial | yt-dlp gratis pero bloqueado ahora mismo; vidIQ 5 créditos por video |
| Ver el video (animación, ritmo de cortes, música, voz) | Descarga del video o fotogramas | Por ahora no | Bloqueado por YouTube en esta sesión. Alternativas abajo |
| Volumen de búsqueda, competencia, palabras relacionadas, tendencias | vidIQ (`keyword_research`) | Sí | 5 créditos por consulta |
| Google Trends | Sin integración directa | Parcial | Puedes exportarme el CSV desde trends.google.com |
| Suscriptores del canal el día que publicó un video | Historial de vidIQ | Sí, en los canales con historial | Para el resto, no |
| CTR, retención, duración media, fuentes de tráfico, ingresos de canales ajenos | Solo los ve el dueño en YouTube Studio | **No, para nadie** | Ninguna herramienta pública los tiene. vidIQ y similares solo estiman |
| Edad, país e intereses de la audiencia de canales ajenos | Privado | No | Solo puedo inferirlo como hipótesis, por idioma, tema y comentarios |
| Métricas de nuestro propio canal | YouTube Studio | Cuando exista el canal | Exportaciones de Studio (CSV) o capturas |

**Presupuesto de vidIQ.** Tu cuenta tiene 150 créditos al mes (se renuevan el 27 de noviembre de 2026). En esta fase usé 55: 30 en el historial de 6 canales y 25 en datos exactos de 250 videos. Quedan **95 créditos (19 consultas)**. Propongo reservarlos así: 50 para investigación de palabras clave en la fase 3, 30 para transcripciones de los videos clave que no pueda sacar gratis y 15 de margen.

**Nota sobre el bloqueo.** Al pedir metadatos video a video desde este contenedor, YouTube respondió primero "HTTP 429" (demasiadas peticiones) y luego "Sign in to confirm you're not a bot". Paré para no prolongar el bloqueo. Suele ser temporal. Para la fase 2 tengo tres vías, de más barata a más cara:

1. Reintentar subtítulos y fotogramas con yt-dlp, despacio, cuando se levante el bloqueo (gratis).
2. Transcripciones de vidIQ solo para los videos clave (5 créditos cada una).
3. Que tú me pases capturas de pantalla de los primeros 30 segundos de los videos que más te interesen. Solo si las dos primeras fallan.

## 3. Cómo compartirme canales

Lo que ya me pasaste sirve tal cual. La URL repetida de Some Guy Who Knows Stuff (`/videos` y `/featured`) es el mismo canal y lo conté una vez. Para próximos lotes, una línea por canal:

```
@handle | qué te gusta de él (formato, estética, crecimiento, tema) | tipo: competidor directo / inspiración de formato / inspiración visual
```

Ejemplo: `@SquireExplains | creció a 10k en 26 días con Shorts | inspiración de formato`

Si tienes **videos concretos** que te gustan, pega sus URLs: los analizo primero y en profundidad. La columna "tipo" no es obligatoria. Cambia el peso que le doy al canal en la recomendación de nicho, porque un canal que solo te gusta por la estética no debería empujar la elección del tema.

## 4. Trabajo por lotes

- **Tamaño:** 4 a 6 canales por lote. Con más, la lectura profunda de la fase 2 se vuelve superficial.
- **Mismo proceso:** los scripts de `scripts/` repiten exactamente los pasos 1 a 5 y añaden las filas al mismo `datos/videos.csv`. Ningún lote tiene su propia métrica.
- **Coste por lote en vidIQ:** unos 5 créditos por canal (historial) más 5 por cada 50 videos con datos exactos.
- **Cierre de cada lote:** actualizo la tabla comparativa y la matriz de patrones. No hago un informe aislado por lote, para que las conclusiones salgan siempre de todos los canales juntos.

## 5. Lo que necesito de ti

Solo lo que cambia decisiones. Si no respondes, sigo con el supuesto de la tercera columna y lo marco como supuesto.

| Pregunta | Por qué importa | Supuesto si no respondes |
|---|---|---|
| ¿En qué país resides? | Disponibilidad del Programa de Socios, cuenta de AdSense, impuestos y retenciones | Un país donde el programa está disponible; verifico requisitos generales |
| ¿Idioma del canal: español, inglés o ambos? | Define la competencia, el CPM esperado y qué referentes pesan más | Evalúo español e inglés en paralelo en la fase 5 |
| ¿Cuántas horas por semana puedes dedicar? | Limita la frecuencia real. Uno de los referentes publica un video de 30 minutos al día | 10 a 15 horas por semana |
| ¿Presupuesto mensual para herramientas? | Voz, imagen, animación y música cambian mucho según el plan | 0 a 50 USD al mes al inicio, y escalar con resultados |
| Este repositorio contiene tus portafolios de editor de video y diseñador audiovisual (motion graphics). ¿Vas a animar y editar tú? | Es una ventaja competitiva real. La mayoría de estos canales parecen apoyarse en imagen generada y animación mínima | Sí: tú animas y editas, la IA acelera guion, voz e ilustración |
| ¿Voz propia, voz IA o ambas? ¿Mostrarías la cara? | Identidad de marca, coste y políticas de contenido sintético | Voz IA o voz propia, sin cara |
| ¿Hay temas que no quieres tocar (violencia gráfica, guerra, política actual, religión)? | Los temas más vistos en estos canales son muertes, torturas y guerra | Evitamos política actual y gore explícito |
| ¿Ya tienes un canal creado? | Un canal con historial no empieza de cero (Simple Paint existe desde 2017 pero sus videos visibles empiezan en 2025) | Canal nuevo |

## 6. Estructura de trabajo

Primero investigamos, después identificamos oportunidades, luego definimos la identidad visual y al final construimos el sistema de producción. Propongo **un cambio de orden respecto a tu plan**: revisar las políticas de monetización (tu fase 10) antes de elegir nicho. Las reglas sobre contenido repetitivo o producido en masa, y sobre temas con publicidad limitada, descartan formatos que de otro modo parecerían ganadores. Elegir nicho sin ese filtro obligaría a rehacer la recomendación.

| Bloque | Fases | Entregables (numeración de tu lista) | Estado |
|---|---|---|---|
| A. Investigación | 1. Canales | 1 (informe comparativo), 3 (base de datos) | **Hecho para los 8 canales** (`02-analisis-canales.md`, `datos/`) |
| | 2. Mejores videos | 2 (ranking) | Ranking cuantitativo hecho (`03-ranking-videos.md`); falta la lectura de guion, hook y producción |
| | 3. Palabras clave (vidIQ) | parte de 4 y 5 | Pendiente |
| | 4. Patrones | 4 (matriz) | Primeras hipótesis en `02-analisis-canales.md` |
| B. Oportunidad | 10. Políticas y monetización (adelantada) | 10 | Pendiente, con fuentes oficiales de YouTube |
| | 5. Nicho y posicionamiento | 5, 6 | Pendiente |
| C. Marca | 6. Identidad visual | 7 | Pendiente. Sin nombres ni logos hasta cerrar el bloque B |
| D. Sistema | 7. Producción con IA, 8. SEO y empaquetado, 9. Retención | 8, 9 | Pendiente |
| E. Ejecución | 11. Plan de 90 días, 12. Dashboard | 11, 12, 13, 14 | Pendiente |
