# Fase 3: palabras clave y demanda en español para Latinoamérica

**Consulta:** 27 de octubre de 2026.

**Fuentes:**
- **vidIQ:** 7 consultas (35 créditos), es decir, todo el saldo hasta la renovación del 27 de noviembre:
  - 5 de investigación de palabras clave.
  - 1 de videos en español que superan a su canal.
  - 1 de análisis de comentarios de la audiencia.
- **Autocompletado de YouTube:** unas 140 consultas gratuitas para México, Colombia y Argentina.
- **Lo aprendido en las fases 1 y 2.**

**Datos:** `datos/keywords_vidiq.csv`, `datos/autocompletar_youtube_2026-10-27.json`, `datos/outliers_es_historia.csv`.

Etiquetas: **[dato]** medido; **[estimación]** cifra de una herramienta o calculada con un supuesto; **[hipótesis]** interpretación a validar.

## Cómo leer estos datos

- **Volumen, competencia y puntuación (0 a 100)** son índices propios de vidIQ. **"Búsquedas mensuales estimadas"** es una estimación de vidIQ para el texto exacto **en todos los países que lo escriben**. Todo lo que viene de vidIQ es [estimación].
- **Términos compartidos con el portugués** ("segunda guerra mundial", "historia", "curiosidades"): el número incluye Brasil. La columna de mercados principales lo muestra (Brasil 43 % en "segunda guerra mundial", 56 % en "curiosidades").
- **Datos de mercados con ruido:** vidIQ asigna Pakistán y Vietnam a "historia de méxico" o "lugares imposibles". Esas filas las uso con cautela.
- **El crecimiento mezcla temporadas.** "independencia de mexico" aparece con −79 % porque la medición llega después de septiembre.
- **El autocompletado** muestra lo que la gente escribe, ordenado por popularidad, **sin volumen**. Está dominado por entretenimiento (series, videojuegos, música), así que lo filtré.
- **No usé Google Trends** porque no tengo integración. Las visitas de Wikipedia en español no estuvieron disponibles: el servicio de Wikimedia rechazó las consultas por exceso de peticiones desde esta red compartida.
- **No busqué en YouTube cada palabra clave** para contar los videos que la cubren: YouTube sigue bloqueando este contenedor y cada búsqueda en vidIQ cuesta 5 créditos. La oferta la estimo con el índice de competencia de vidIQ, los videos que superan a su canal y los nombres de canales que aparecen en el autocompletado.

---

## Resumen

1. **La mejor relación entre demanda y competencia está en mitos y leyendas** [estimación de vidIQ]:
   - "mitos y leyendas": unas 53.000 búsquedas al mes, competencia **42**, puntuación 66. México es el 25 % y Perú el 13 %.
   - Variantes en crecimiento: "leyendas mexicanas" 22.000 (+125 %), "leyendas de terror" 14.000 (+86 %), "leyendas urbanas de terror" 12.600 (+172 %).
   - El autocompletado confirma la demanda por país [dato]: La Llorona, La Nahuala, el Charro Negro, las momias de Guanajuato, El Silbón, La Patasola, "leyendas de cada país".
2. **La historia nacional latinoamericana tiene demanda alta y competencia media**, con intención escolar fuerte [estimación + dato]:
   - "historia de colombia": 40.000 al mes, competencia **46**, +142 %; el 60 % viene de Colombia.
   - "historia de mexico": 59.000, competencia 60, +141 %.
   - "historia de latinoamérica": solo unas 6.000. La gente busca su país, no la región.
   - El autocompletado revela intención escolar ("para niños", "para el icfes", "unam", "resumen", "en 5 minutos") y nombra a quienes ya ocupan el espacio: Diana Uribe, Felipe Pigna, Academia Play, Farid Dieck, "profa Kempis", "el mapa de Sebas".
3. **"Historia para dormir" tiene la mejor puntuación de toda la búsqueda, pero es ambigua** [estimación + dato]:
   - 159.000 al mes, competencia **28**, puntuación 76.
   - El autocompletado mezcla cuentos infantiles para dormir ("para niños", "bebés", "biblia") con historia para adultos ("para adultos", "profundamente", "edad media", "segunda guerra mundial", "egipto").
   - La variante adulta está funcionando en español: canales de unos 5.000 a 15.000 suscriptores sacan entre 48.000 y 99.000 vistas con videos de casi 2 a más de 3 horas. vidIQ marca uno de ellos con la etiqueta de contenido generado con IA.
4. **Civilizaciones antiguas e historia antigua: mucho volumen, pero con peso de España** [estimación]:
   - "historia antigua": 110.000, competencia 48; España es el 32 %.
   - "civilizaciones antiguas": 51.000, competencia 44; España es el 44 %.
   - El ángulo latinoamericano aparece en el autocompletado: "civilizaciones antiguas de américa", "mayas, aztecas e incas", "de colombia".
5. **Los temas precolombinos y de la conquista tienen competencia media** [estimación]:

   | Palabra clave | Búsquedas al mes | Competencia | Crecimiento |
   |---|---|---|---|
   | "los aztecas" | 24.000 | 65 | +161 % |
   | "hernan cortes" | 26.000 | 59 | |
   | "tenochtitlan" | 21.500 | 59 | |
   | "moctezuma" | 20.500 | 56 | |
   | "imperio azteca" | 7.700 | 46 | +77 % |
   | "como vivian los aztecas" | 4.500 | 40 | |
6. **Las curiosidades y los lugares rinden menos en español que en inglés** [estimación + dato]:
   - "lugares prohibidos": solo 7.200 al mes y en caída (−48 %).
   - "lugares ocultos": el autocompletado lo ocupan los videojuegos.
   - "datos curiosos": 246.000, pero con competencia 72.
   - El catálogo de lugares de The Paint Explainer no se traslada tal cual.
7. **La Segunda Guerra Mundial es grande pero tiene dueño** [estimación + dato]:
   - "segunda guerra mundial": 227.000 al mes (el 43 % de Brasil), competencia 61.
   - "toda la historia de la segunda guerra mundial explicada": 27.000 (+185 %). Es casi exactamente el título que usa Te Lo Pinto Fácil ("Toda la Segunda Guerra Mundial Explicada"), con 585.000 suscriptores.
   - No la recomiendo como pilar de un canal nuevo.
8. **Formatos de búsqueda que se repiten en Latinoamérica** [dato, autocompletado]: "en N minutos", "para niños", "documental", "resumen", "countryballs", "de cada país", "la verdadera historia de", "el origen de", "cómo vivían los", "cómo era la vida en".
9. **Lo que rinde hoy en español es un espacio fragmentado** [dato, vidIQ]:
   - De los 42 videos de "historia" que más superaron a su canal en seis meses, solo 8 son del nicho y 12 lo son en parte. El resto es fútbol, videojuegos y pódcasts.
   - Entre los relevantes:
     - Historia para dormir.
     - Versiones en español de canales en inglés. "El Tipo Que Sabe Cosas", por su nombre y sus títulos, parece la versión en español de Some Guy Who Knows Stuff.
     - Un canal grande de historia en español: Historia Incomprendida, 4,5 M de suscriptores.
     - Historia del fútbol latinoamericano: Templos del Fútbol, con 1.100 suscriptores, sacó 58.000 vistas con "La Bombonera en 1940".
     - "La historia detrás del corrido".
   - No hay un formato dominante.
10. **La audiencia pide neutralidad** [dato, evidencia débil]:
    - El análisis de comentarios (muestra de 163 hilos en 22 canales) encontró pocas peticiones repetidas.
    - La queja más extendida es el sesgo y la manipulación en los documentales de historia (4 hilos en 4 canales distintos).
    - Los videos de política reciente de Colombia, Perú y México llenan los comentarios de peleas partidistas.
    - [Hipótesis]: neutralidad y fuentes visibles son una promesa de marca valorada. Evitar la política reciente reduce la polarización y el riesgo publicitario.

---

## Tabla de palabras clave principales

Demanda y competencia de vidIQ, salvo que diga "autocompletado". La oportunidad es mi valoración para un canal **nuevo** en español latinoamericano [hipótesis]. Los títulos son ejemplos: **sus afirmaciones se verifican con fuentes antes de producir**.

### Leyendas y mitos

| Palabra clave | Intención | Demanda al mes | Competencia | Mercado | Quién la cubre | Oportunidad | Título posible | Formato |
|---|---|---|---|---|---|---|---|---|
| mitos y leyendas | Saber las historias; escolar ("para niños", "primaria") | ~53.300 (+19 %) | 42 | México 25 %, Perú 13 % | Canales infantiles y escolares; un juego de cartas chileno con el mismo nombre | **Alta** con el ángulo "lo que es verdad y lo que no" | "Mitos y leyendas de Latinoamérica: qué hay de real en cada uno" | Largo de 12 a 15 min por catálogo + un Short por leyenda |
| leyendas mexicanas | Entretenimiento y miedo | ~22.300 (+125 %) | 58 | México | Narradores de terror, pódcasts (Leyendas Legendarias) | Media | "La historia real detrás de 6 leyendas mexicanas" | Largo; cuenta atrás |
| leyendas de terror | Miedo | ~14.200 (+86 %) | 47 | No consta | Narradores de terror | Media: quien busca miedo puede sentir que un enfoque documental no cumple | Usar solo con miniatura y gancho de suspense real | Largo narrativo |
| leyendas urbanas de terror | Miedo | ~12.600 (+172 %) | 51 | No consta | Narradores de terror | Media | — | — |
| la verdadera historia de la llorona | Comprobar el origen | Sin medir; fuerte en México, Colombia y Argentina (autocompletado) | Sin medir | Pan-latinoamericano | Películas, terror, contenido infantil | **Alta** [hipótesis]: pide exactamente lo que el canal ofrecería | "La verdadera historia de La Llorona, según las crónicas" | Largo de 10 a 12 min, relato con fuentes |
| leyendas de cada país | Comparar países | Sin medir (autocompletado: "de latam", "Perú", "Honduras", "el Silbón") | Sin medir | Pan-latinoamericano | Canales de terror y recopilaciones | **Alta** [hipótesis]: une a todo el público de la región | "Una leyenda de cada país de Latinoamérica (y su origen real)" | Catálogo largo + Shorts por país |
| leyendas de colombia | Local, escolar y terror | Sin medir (autocompletado: Patasola, "reales", "animadas", "para niños") | Sin medir | Colombia | Escolar y terror | Media-alta en Colombia | "La Patasola, El Mohán y La Madremonte: de dónde salen" | Largo o serie |

### Historia de Latinoamérica

| Palabra clave | Intención | Demanda al mes | Competencia | Mercado | Quién la cubre | Oportunidad | Título posible | Formato |
|---|---|---|---|---|---|---|---|---|
| historia de colombia | Escolar, resumen, documental | ~40.400 (+142 %) | 46 | Colombia 60 % | Diana Uribe, contenido escolar, versiones de 4 a 15 minutos | **Alta**, sobre todo con preguntas concretas en lugar de resúmenes | "¿Por qué Colombia se llama Colombia?" | Relato de 8 a 12 min desde una pregunta |
| historia de mexico | Escolar, documental | ~58.900 (+141 %) | 60 | México 47 % | UNAM, "profa Kempis", documentales de televisión | Media-alta | "¿Por qué la capital de México está sobre un lago?" | Relato con pregunta |
| historia de latinoamérica | Académica | ~5.900 a 6.400 | 43 a 45 | No consta | Libros y cátedras universitarias | Baja como palabra clave: se busca por país | — | — |
| independencia de mexico | Escolar, estacional (septiembre) | ~12.300 (−79 % fuera de temporada) | 68 | México | Mucho contenido escolar | Baja-media; solo en temporada | — | Publicar en agosto y septiembre |
| hernan cortes / la conquista de mexico | Historia y debate | ~26.200 / sin medir | 59 / sin medir | México | Documentales, divulgadores | Media-alta con una paradoja concreta | "¿Cómo conquistaron unos pocos cientos de españoles un imperio de millones?" | Relato con paradoja y fuentes |
| tenochtitlan / los aztecas | Curiosidad, escolar | ~21.500 / ~24.200 (+161 %) | 59 / 65 | México | Documentales y canales escolares | Media | "Un día en Tenochtitlan, en segunda persona" | Narrativo largo |
| como vivian los aztecas | Curiosidad, escolar | ~4.500 | **40** | México | Pocos con buena producción [hipótesis] | **Alta** (competencia baja, alinea con "cómo vivían") | "Así vivías si nacías en Tenochtitlan" | Narrativo en segunda persona |
| civilizaciones antiguas | Curiosidad, documental | ~50.800 (+7 %) | 44 | España 44 %, México 13 % | Documentales y canales de misterio ("avanzadas", "perdidas") | Media para Latinoamérica: el ángulo americano se busca menos | "Las civilizaciones de América que existieron antes de los incas" | Catálogo o relato |
| historia antigua | Curiosidad, escolar | ~109.800 (+58 %) | 48 | España 32 % | Documentales, pódcasts, "para dormir" | Media | — | Pilar secundario |

### Formatos largos y otros nichos

| Palabra clave | Intención | Demanda al mes | Competencia | Mercado | Quién la cubre | Oportunidad | Título posible | Formato |
|---|---|---|---|---|---|---|---|---|
| historia para dormir | Dormirse escuchando (infantil y adulto) | ~158.800 (+17 %), mezcla de intenciones | **28** | Vietnam 20 %, España 18 %, Brasil 11 % | Canales nuevos de 2 a 3 horas, algunos con etiqueta de IA | Media: alta demanda, pero riesgo de política y difícil de producir con calidad | "Así se vivía en Tenochtitlan (historia para dormir)" | Recopilación larga hecha con los videos del canal |
| lugares imposibles | Curiosidad | ~93.800 (+35 %) | 45 | Vietnam 46 % (dudoso), España 21 %, México 11 % | Recopilaciones globales | Media-baja (mercado poco fiable) | — | — |
| lugares misteriosos | Curiosidad | ~11.700 (−24 %) | 37 | No consta | Recopilaciones | Media-baja | — | — |
| lugares prohibidos | Curiosidad | ~7.200 (−48 %) | 55 | No consta | "Historia para tontos", Badabun | Baja | — | — |
| datos curiosos | Curiosidad general | ~246.400 (+36 %) | 72 | España 31 %, México 13 % | Muy saturado | Baja | — | — |
| segunda guerra mundial | Historia, escolar | ~227.400, con Brasil 43 % | 61 | Brasil, España, EE. UU. | Te Lo Pinto Fácil, Academia Play, Farid Dieck, documentales | Baja como pilar | — | Ocasional, desde un ángulo latinoamericano |
| toda la historia de la segunda guerra mundial explicada | Resumen completo | ~26.800 (+185 %) | 48 | EE. UU. 30 %, España 20 %, México 20 % | El título exacto de Te Lo Pinto Fácil | Baja: compite de frente con 585 k suscriptores | — | — |
| historia militar | Historia | ~63.300 (+34 %) | 56 | México 19 % | Varios | Media | — | Pilar secundario |

**Volúmenes sin medir.** Las filas "sin medir" (La Llorona, "leyendas de cada país", "leyendas de colombia", "la conquista de mexico") tienen evidencia de demanda por el autocompletado, pero no cifra. Son las primeras que mediría cuando se renueven los créditos.

---

## Grupos de temas: resumen preliminar

No es todavía la matriz ponderada de la fase 5. Resume demanda, competencia y encaje con lo aprendido.

| Grupo | Demanda | Competencia | Tendencia | Encaje con las estructuras de la fase 2 | Riesgos principales | Oportunidad preliminar |
|---|---|---|---|---|---|---|
| **A. Mitos y leyendas de Latinoamérica con "la historia real"** | Media-alta, repartida por países | Media (42 a 58) | Subiendo en las variantes medidas | "Algo que todos conocen y su verdad documentada" (Crooked), "de cada país", Shorts por leyenda | El público de terror espera miedo; intención escolar; posible estacionalidad en Halloween y Día de Muertos [hipótesis] | **Alta** |
| **B. Historia de Latinoamérica contada desde preguntas y paradojas** (Colombia, México, conquista, independencias, precolombinos) | Alta por país (40.000 a 59.000 en Colombia y México) | Media (40 a 60) | Subiendo (+141 % / +142 %) | "Paradoja + héroe conocido + fuentes" (Lịch Sử), "¿Por qué dejó de…?" (Squire), "así vivías en…" | Polarización política; intención escolar; nombres consolidados (Diana Uribe) | **Alta** |
| C. Vida cotidiana e "historia para dormir" | Alta pero ambigua | Baja (28 a 40) | Subiendo | "Así se vivía en…" | Riesgo de contenido producido en masa; mezcla con cuentos infantiles; videos de horas | Media (validar) |
| D. Curiosidades y lugares | Media y con ruido | Media-alta | Bajando en "prohibidos" | Catálogo (The Paint Explainer) | Videojuegos en las búsquedas; mercados mezclados | Media-baja |
| E. Segunda Guerra Mundial e historia militar | Alta | Media-alta, con un competidor dominante en español | Estable | "Así se…" (Te Lo Pinto Fácil) | Competencia directa con Te Lo Pinto Fácil; temas sensibles | Baja como pilar |

**Lectura conjunta** [hipótesis]:
- A y B se refuerzan entre sí: muchas leyendas tienen raíz en la conquista y la colonia.
- Juntos permiten un canal pan-latinoamericano ("una leyenda / una pregunta de cada país") con anclas fuertes en México y Colombia, los dos mercados con más demanda medida.
- C puede ser un **formato derivado** (recopilaciones largas para dormir hechas con los videos del canal) en lugar de un nicho propio. Así se aprovecha su baja competencia sin producir horas de contenido nuevo.

---

## Diez ideas de video derivadas

Para pasar a la fase 8 (empaquetado). Ninguna está validada: son hipótesis con su palabra clave. **Toda afirmación del título se verificará con fuentes antes de producir.**

| # | Idea (título de trabajo) | Palabra clave principal | Demanda | Estructura de la fase 2 que adapta | Formato |
|---|---|---|---|---|---|
| 1 | La verdadera historia de La Llorona, según las crónicas | la verdadera historia de la llorona / leyendas mexicanas | Sin medir / ~22.300 | Algo conocido + verdad documentada | Largo de 10 a 12 min |
| 2 | Una leyenda de cada país de Latinoamérica (y de dónde salió) | leyendas de cada país / mitos y leyendas | Sin medir / ~53.300 | Catálogo "de cada país" | Largo de 15 min + Shorts por país |
| 3 | ¿Por qué Colombia se llama Colombia? | historia de colombia | ~40.400 | Pregunta concreta y paradoja | Relato de 8 a 10 min |
| 4 | Así vivías si nacías en Tenochtitlan | como vivian los aztecas / tenochtitlan | ~4.500 / ~21.500 | Segunda persona, "así se vivía" | Narrativo de 12 min |
| 5 | ¿Cómo conquistaron unos pocos cientos de españoles al imperio azteca? | hernan cortes / la conquista de mexico | ~26.200 / sin medir | Paradoja + fuentes primarias (Lịch Sử) | Relato de 12 a 15 min |
| 6 | Así era la vida en la colonia (y lo que no te contaron en el colegio) | como era la vida en la colonia / en la nueva españa | Sin medir | "Así se vivía en…" | Narrativo de 12 min |
| 7 | El significado real de "Arroz con leche" y otras canciones infantiles | el significado de la cancion arroz con leche | Sin medir | La fórmula de las canciones infantiles de Crooked, en español | Cuenta atrás de 10 a 12 min |
| 8 | La Patasola, El Mohán y La Madremonte: de dónde salen las leyendas de Colombia | leyendas de colombia | Sin medir | Algo conocido + verdad documentada | Largo o serie |
| 9 | Las civilizaciones de América que existieron antes de los incas | civilizaciones antiguas (de américa) | ~50.800 (global) | Catálogo con preguntas | Largo de 12 a 15 min |
| 10 | ¿Por qué la capital de México está construida sobre un lago? | historia de mexico / tenochtitlan | ~58.900 / ~21.500 | Pregunta y paradoja | Relato de 8 a 10 min |

---

## Qué falta y qué necesito

1. **Medir los volúmenes "sin medir"** cuando se renueven los créditos (27 de noviembre, 150 créditos), en este orden:
   - La Llorona, "leyendas de cada país", "leyendas de colombia", "la conquista de mexico", "el significado de la cancion arroz con leche".
   - El modo de preguntas para "leyendas" e "historia de colombia".
   - La validación de 2 o 3 ideas contra los comentarios de la audiencia.
2. **Estacionalidad:** si quieres adelantar, puedes exportarme de Google Trends un CSV comparando "mitos y leyendas", "la llorona", "historia de colombia", "historia de mexico" e "historia para dormir". Región: Latinoamérica o cada país. Período: últimos 5 años. Categoría: YouTube Search. Así veríamos si las leyendas suben con Halloween y el Día de Muertos.
3. **Siguiente fase:** como acordamos, la revisión de políticas y monetización (tu fase 10) **antes** de elegir el nicho. Los grupos A, B y C tienen riesgos distintos:
   - Contenido producido en masa en las recopilaciones largas.
   - Temas sensibles en la conquista y la colonia.
   - Idoneidad publicitaria del terror.
