# Fase 1: análisis de los 8 canales de referencia

**Consulta:** 27 de octubre de 2026.
**Fuentes:** páginas públicas de YouTube (listas completas con yt-dlp), vidIQ (historial diario de 6 canales y datos exactos de 346 videos) y revisión directa, imagen por imagen, de las miniaturas de los mejores y peores videos de cada canal.
**Datos:** `datos/canales.csv`, `datos/videos.csv` (1.020 videos y Shorts), `datos/hitos_crecimiento.csv`. Ranking por categorías en `03-ranking-videos.md`.

Etiquetas: **[dato]** medido; **[estimación]** calculado con un supuesto; **[hipótesis]** interpretación a validar. Ninguna hipótesis está presentada como causa.

---

## Resumen

1. **Es un solo género con dos ramas** [dato, por títulos y miniaturas]. Los ocho son canales sin rostro que explican temas con ilustraciones.
   - **Rama 1, catálogos de curiosidades extremas:** "todos los X explicados", "las peores muertes en X", "la verdad oscura detrás de X". La siguen The Paint Explainer, Simple Paint, Te Lo Pinto Fácil, Some Guy Who Knows Stuff y The Crooked Explainer.
   - **Rama 2, historia contada desde una pregunta concreta:** "¿por qué…?", "¿cómo vivían…?". La siguen Squire Explains, Estrictamente y Lịch Sử Ngoại Truyện.
2. **Hoy se puede crecer desde cero en este género, y rápido** [dato]. Los cuatro canales creados en 2026 llegaron a 1.000 suscriptores en 12, 23, 40 y 55 días. Tres de ellos superaron los 10.000 en 26, 102 y 146 días.
3. **El crecimiento llega a saltos, y lo provocan uno a tres videos** [dato]:
   - The Crooked Explainer tenía 40 suscriptores tras 16 videos y cinco semanas. Un solo video ("Actual Dark Truth Behind Every Nursery Rhymes") lleva 1,86 M de vistas, el 24 % de todas las del canal.
   - Estrictamente despegó con su video número ~50, "¿Cómo Inventaron los Seres Humanos los Países?", que multiplicó por 539 a sus vecinos.
4. **Las vistas se concentran en los éxitos, no en el promedio** [dato]. En cada canal, el 10 % de videos con más vistas reúne entre el 33 % y el 72 % del total. Consecuencia práctica [hipótesis]: un canal nuevo se juzga por cuántos intentos con potencial publica y cuánto aprende de ellos, no por su media.
5. **El tema pesa más que la plantilla y que la fórmula del título** [observación + hipótesis]:
   - En las miniaturas de cada canal, los ganadores y los perdedores usan la misma plantilla visual.
   - Comparé los títulos de los 197 videos del quintil superior (por rendimiento relativo) con los 197 del inferior:
     - Las preguntas aparecen igual en ambos grupos (18 % frente a 19 %).
     - Los números aparecen menos entre los ganadores (16 % frente a 19 %).
     - Los superlativos aparecen algo más (54 % frente a 47 %), igual que las muertes o la violencia (18 % frente a 12 %) y el misterio (7 % frente a 3 %).
   - Son señales débiles. Ninguna regla de redacción explica el éxito por sí sola.
6. **Los canales grandes rinden menos por video** [dato]. Mediana histórica frente a mediana de los últimos 90 días:
   - The Paint Explainer: de 1,1 M a 359 k.
   - Simple Paint: de 466 k a 271 k.
   - Te Lo Pinto Fácil: de 342 k a 146 k. Aun así, como publica más, batió su récord mensual de vistas en septiembre de 2026 (16,2 M).
   - La causa no se puede probar con datos públicos [hipótesis]: más canales con el mismo formato, temas agotados o cambios de frecuencia.
7. **El español funciona en este formato** [dato]:
   - Te Lo Pinto Fácil (España): 585 k suscriptores y 116 M de vistas.
   - Estrictamente (España): 13,8 k suscriptores en 4,5 meses.
   - Los dos ofrecen audio doblado a otros idiomas: 16 y 4 pistas de audio en los videos que revisé.
8. **Riesgos a revisar en la fase de políticas** [hipótesis]:
   - Los temas que más rinden (muertes, torturas, guerra, miniaturas con heridas) pueden limitar la publicidad.
   - Publicar un video de 30 minutos al día con producción aparentemente automatizada, como Estrictamente, puede acercarse a la política de contenido repetitivo o producido en masa.
   - The Paint Explainer publica una declaración de uso de IA en la descripción del canal y de sus videos (lo comprobé en el más visto). En ella se distingue de los "canales totalmente automatizados" [dato].

---

## Tabla comparativa

| Canal | Idioma (país) | Creado | Suscriptores | Vistas totales | Videos | Ritmo actual | Mediana por video largo: histórica / últimos 90 días | Duración mediana | Días hasta 1k / 10k | % de vistas en el 10 % top |
|---|---|---|---|---|---|---|---|---|---|---|
| The Paint Explainer | inglés (no declarado) | jul-2023 | 2,01 M | 325,0 M | 169 | 0,9/semana | 1,10 M / 359 k | 11,8 min | sin datos | 34 % |
| Simple Paint | inglés (EE. UU.) | dic-2017 (videos visibles desde abr-2025) | 540 k | 117,5 M | 135 | 1,9/semana | 466 k / 271 k | 14,6 min | sin datos | 43 % |
| Te Lo Pinto Fácil | **español (España)** | abr-2024 | 585 k | 116,0 M | 303 (184 largos, 116 Shorts) | 3,7/semana | 342 k / 146 k | 18,1 min | 28 / 67 | 53 % |
| Some Guy Who Knows Stuff | inglés (EE. UU.) | jun-2025 | 130 k | 20,8 M | 140 | 2,5/semana | 27 k / 24 k | 17,8 min | 54 / 119 | 60 % |
| The Crooked Explainer | inglés (EE. UU.) | mar-2026 | 23,9 k | 7,65 M | 56 | sin videos desde el 30-sep | 10 k / 63 k | 12,3 min | 55 / 146 | **72 %** |
| Estrictamente | **español (España)** | jun-2026 | 13,8 k | 3,40 M | 133 | **7/semana** | 7,6 k / 12 k | **30,0 min** | 23 / 102 | 59 % |
| Lịch Sử Ngoại Truyện | vietnamita (Vietnam) | jul-2026 | 8,7 k | 1,49 M | 50 | 3,2/semana | 16 k / 16 k | 12,4 min | 40 / aún no | 33 % |
| Squire Explains | inglés (no declarado) | **28-sep-2026** | 11,7 k | 12,3 M | 36 (32 Shorts) | ~9/semana | Shorts 107 k · largos 81 k | Shorts 1:08 · largos 9:40 | **12 / 26** | 47 % |

Fuentes: página "Acerca de" (fecha, totales, país), vidIQ (hitos de suscriptores) y `datos/videos.csv` (medianas, ritmo, duración y concentración). "Sin datos" significa que no consulté el historial de vidIQ de ese canal, para ahorrar créditos.

---

## Fichas por canal

### 1. The Paint Explainer · [@ThePaintExplainer](https://www.youtube.com/@ThePaintExplainer)

**Identidad y posicionamiento**
- **Propuesta** [dato]: "I explain interesting stuff". Explicaciones de 8 a 20 minutos organizadas como catálogo: cada planeta, cada nivel del infierno, cada ideología política, cada falacia lógica.
- **Nicho:** curiosidades de historia, ciencia y leyendas. **Subnicho:** "lo peor, lo más extremo, todos los X".
- **Audiencia** [hipótesis]: angloparlantes jóvenes que consumen curiosidad morbosa como entretenimiento. No hace falta saber nada del tema para seguir los videos.
- **Necesidad que cubre:** saber lo más impactante de un tema en 10 minutos.
- **Tono** [hipótesis, por títulos y miniaturas; aún no vi los videos]: irónico y ligero sobre temas oscuros.
- **Uso de IA declarado** [dato]:
  - Voz generada con texto a voz (TTS) genérico.
  - IA como asistente de investigación y guion.
  - Dibujos hechos por un artista humano, con IA solo para escalar o ampliar imágenes.
  - En su video más visto cita fuentes y añade un descargo de responsabilidad. En el canal menciona su inscripción en el registro de AGCOM, el regulador italiano de comunicaciones.
- **Por qué alguien lo elige** [hipótesis]: de estos ocho canales es el más antiguo con este formato (su video visible más antiguo es de noviembre de 2023) y tiene un estilo de dibujo reconocible.
- **Barrera para un canal nuevo:** competir de frente, en inglés y con los mismos temas, contra 2 M de suscriptores.

**Evolución**
- Cuenta creada el 18 de julio de 2023. Primer video visible: "Every Political Ideology Explained in 8 Minutes" (26-nov-2023, 6,59 M de vistas) [dato].
- Ritmo actual: 12 videos en 90 días. La mediana por video cayó de 1,1 M (histórica) a 359 k (últimos 90 días) [dato].
- No consulté su historial diario.

**Modelo de contenido**
- **Pilares** [clasificación preliminar por títulos]:
  - Muertes y castigos: "The Worst Punishments in History", "The Worst Cave Deaths Ever", "How Every Cartel Boss Died".
  - Todo X explicado: planetas, infierno, ideologías, paradojas.
  - Leyendas y anomalías: "Urban Legends That Turned Out to Be True", "Disturbing Scientific Anomalies".
  - Lugares prohibidos: "Most Guarded Places on Earth".
- **Contenido atemporal** casi en su totalidad.
- **Series numeradas** (Pt. 2, 3, 4) [dato]. Resultados desiguales:
  - "Disturbing Scientific Anomalies (Pt. 2)" (5,0 M) superó a la parte 1 (2,7 M).
  - "Every Logical Fallacy Explained (Pt. 2)" (218 k) se quedó en el 5 % de la parte 1 (4,1 M).
- **Títulos repetidos** [dato]: hay videos distintos con el mismo título, por ejemplo dos "The Most Guarded Places on Earth You Can't Visit" y dos "Disturbing Scientific Anomalies" sin número. Pueden ser resubidas o versiones; está por verificar.

**Mejores videos** [dato]
- **Absolutos:**
  - "What Dying on Every Planet Would Be Like": 12,96 M (ene-2025, 8:16).
  - "The Worst Punishments in History": 9,10 M.
  - "The Scariest Urban Legends That Turned Out to Be True": 8,89 M.
- **Relativos:**
  - "Every Level of Hell Explained in 12 Minutes": ×10,2.
  - "The Worst Cave Deaths Ever": ×9,8.
  - "How Every Cartel Boss Died": ×7,3.
- **Reciente:** "The Most Guarded Places on Earth You Can't Visit" (8-sep-2026): 2,38 M, ×6,6, 48 k vistas/día.
- **Peor rendimiento relativo:**
  - Mitos de salud: ×0,09.
  - Falacias lógicas, parte 2: ×0,11.
  - Datos sobre el cuerpo humano: ×0,12.
  - Fugas de prisión: ×0,14.

**Miniaturas** (vistas directamente)
- **Dos sistemas visuales:**
  - **Duelo:** dos personajes de dibujo con detalles grotescos (piel, ojos, calaveras), cada uno con una etiqueta de una o dos palabras en negro sobre blanco ("URANUS / SATURN", "EL MEXICANO / CARRILLO").
  - **Cuadrícula:** de 6 a 18 imágenes pequeñas, cada una con su etiqueta (castigos, leyendas, errores, lugares).
- **Lo que distingue a ganadores de perdedores:** los perdedores también son cuadrículas, pero de iconos planos y coloridos de conceptos abstractos (falacias, mitos de salud). Los ganadores son cuadrículas de imágenes oscuras o reales.
- [Hipótesis]: la cuadrícula funciona cuando cada celda despierta curiosidad por sí misma.

**Replicable frente a circunstancial**
- **Replicable:** el catálogo con límite de tiempo en el título ("en 12 minutos"), las fuentes y la declaración de IA, y explotar los ganadores con nuevas partes.
- **Circunstancial:** la ventaja de haber llegado primero y una audiencia de 2 M.

### 2. Simple Paint · [@SimplePaintOfficial](https://www.youtube.com/@SimplePaintOfficial)

**Identidad y posicionamiento**
- **Propuesta** [dato]: "I'm using paint to explain interesting things in a simple way".
- **Nicho:** muertes, desastres y supervivencia. Su fórmula dominante es **"The Worst [ámbito] Deaths Ever"**: astronautas, deportes, cuevas, gamers, Everest, montañas rusas.
- **Audiencia** [hipótesis]: la misma que The Paint Explainer, con más peso en el morbo y en ámbitos de cultura pop (gamers, deportes).
- **Operación profesional** [dato]:
  - Correo de una agencia de gestión.
  - Canales hermanos: @SimpleVisualsOfficial, @CrimePaintOfficial y @SimplePaintArabic.
  - Audio doblado: hasta unas 20 pistas por video, según los idiomas de subtítulos originales detectados.
  - Etiquetas extensas en los videos revisados.
- **Promesa implícita:** "los casos reales más horribles de X, uno por uno".
- **Barrera:** mismo nicho y mismo estilo que The Paint Explainer, con 540 k suscriptores y una red de canales.

**Evolución**
- La cuenta existe desde diciembre de 2017, pero su video visible más antiguo es del 23-abr-2025 ("The Most Painful Cave Deaths Of All Time") [dato].
- [Hipótesis]: una cuenta antigua reutilizada, o videos antiguos retirados. No se puede saber con datos públicos.
- Ritmo: 24 videos en 90 días. Mediana: de 466 k (histórica) a 271 k (últimos 90 días).

**Modelo de contenido**
- **Pilares:** muertes por ámbito; supervivencia ("How to Survive Every Natural Disaster", "How To Survive Every Apex Predator"); errores humanos; obsesiones ("Gamers Who Took Their Obsession Too Far").
- **Partes 2** [dato]: de 0,6 a 1,7 veces la mediana de sus vecinos. Ninguna se acerca al original.

**Mejores videos** [dato]
- **Absolutos:**
  - "The Worst Astronaut Deaths Ever": 6,07 M.
  - "The Worst Deaths in Every Sport": 6,04 M.
  - "The Most AVOIDABLE Cave Deaths Ever": 5,98 M, ×14,3.
- **Recientes:**
  - "The Most Horrifying Ways People Got Trapped" (1-oct-2026): 2,98 M en 26 días, ×7,7.
  - "How to Survive Every Natural Disaster" (15-oct): 965 k en 12 días.
- **Peor rendimiento relativo:**
  - Órganos del cuerpo explicados: ×0,08.
  - IA y control: ×0,10.
  - Golpes militares de EE. UU. (político): ×0,11.
  - Antihéroes: ×0,13.

**Miniaturas** (vistas directamente)
- **Plantilla casi única:** dos o tres personajes de frente, en ilustración semirrealista de cómic, cada uno con una palabra grande en negro encima ("BULL / CRICKET / MotoGP", "CHERNOBYL / HIROSHIMA", "-40° / -20°", "BEFORE / AFTER", "2009 / 2019"). Las caras muestran la consecuencia: congelado, herido, esqueleto.
- **Perdedores:** rompen la plantilla, con una cuadrícula de órganos, un collage fotográfico o una figura política real.
- [Hipótesis]: la comparación "personaje antes y después, o A frente a B" es su activo visual.

**Replicable frente a circunstancial**
- **Replicable:** la fórmula "[superlativo negativo] + [ámbito concreto]", que genera muchos temas, y la miniatura comparativa con etiquetas de una palabra.
- **Circunstancial:** la red de canales, la agencia y el doblaje a 20 idiomas.

### 3. Te Lo Pinto Fácil · [@TeloPintoFacil](https://www.youtube.com/@TeloPintoFacil)

**Identidad y posicionamiento**
- **Propuesta** [dato, descripción en español]: "Bienvenido a un pequeño rincón donde el conocimiento se dibuja literalmente… con el clásico Paint".
- **Canal en español desde España.** En el video revisado ofrece 16 pistas de audio (español y 15 doblajes), y traduce sus títulos. Por eso YouTube me lo mostró en inglés.
- **Nicho:** explicaciones tipo catálogo, en español. **Subnicho actual:** historia militar y Segunda Guerra Mundial.
- **Audiencia** [hipótesis]: hispanohablantes jóvenes de España y Latinoamérica, más la audiencia que llega por el doblaje. No se puede medir desde fuera.
- **Monetización visible** [dato]: membresías del canal activas, un correo de patrocinios gestionado por una agencia y menciones a sus miembros en las descripciones.
- **Por qué alguien lo elige** [hipótesis]: es el formato de The Paint Explainer, nativo en español y con más temas militares.

**Evolución** [dato, vidIQ]
- **Crecimiento temprano rápido con muy pocos videos:**
  - 1.000 suscriptores el día 28, con 6 videos.
  - 10.000 el día 67, con 10 videos.
  - 100.000 el día 377, con 32 videos.
- **Aceleración en 2026:**
  - 500.000 el 6-ago-2026.
  - Mejor mes en suscriptores: abril de 2026 (+53 k). Su mayor éxito, "Todas las Fuerzas Especiales de EEUU Explicadas" (5,09 M), se publicó el 27 de febrero; la relación entre ambos es una hipótesis.
  - Mejor mes en vistas: septiembre de 2026 (+16,2 M).
- **Cambio de estrategia:**
  - En 2024 publicaba de 0 a 5 videos al mes (vidIQ). Entre agosto y octubre de 2026 publicó de 14 a 17 videos largos al mes (fechas aproximadas).
  - Su mediana por video bajó (146 k en los últimos 90 días), pero las vistas totales suben.
  - [Hipótesis]: más videos con menor media, compensado por más intentos con potencial.
- **Shorts sin resultado** [dato]: 116 Shorts con mediana de 10 k vistas y ninguno en los últimos 30 días.

**Modelo de contenido**
- **Pilares:**
  - Militar y Segunda Guerra Mundial: "La Bestia de Omaha", "Así se Drogaban los Soldados en la 2ª Guerra Mundial", "Mad Jack", "POV: Eres un Soldado Alemán".
  - Todos los X explicados: fuerzas especiales, tipos de tornado, colores de ojos, armas nucleares.
  - Crimen: asesinos en serie, torturas.
  - Formato "Tu vida en cada rango de X": caballeros templarios, yakuza.
- **"POV: eres…"** [dato]: aparece en varios éxitos recientes (×9,6 el soldado alemán).
- **Descripciones con muchas palabras clave** y bloques de enlaces a listas de reproducción.

**Mejores videos** [dato]
- **Absolutos:**
  - "Todas las Fuerzas Especiales de EEUU Explicadas": 5,09 M.
  - "Cada PELÍCULA PROHIBIDA Explicada en 13 Minutos": 3,91 M.
  - "Los 8 Colores de Ojos y Qué Ventaja Evolutiva Esconden": 3,37 M.
- **Relativos y recientes:**
  - "La Bestia de Omaha: El Mayor Ametrallador de la Historia": ×15,8, 2,61 M.
  - "Así se Drogaban los Soldados en la 2ª Guerra Mundial" (12-oct-2026): 2,03 M en 15 días, ×15,7.
  - "Mad Jack": ×12,2.
- **Fracaso instructivo:** "Todas las PELÍCULAS PROHIBIDAS Explicadas en 19 Minutos" (39 k, ×0,05) repitió el tema de su segundo mayor éxito y no funcionó.

**Miniaturas** (vistas directamente)
- **Tres etapas:**
  1. Grupo de personajes etiquetados ("DELTA FORCE / GREEN BERETS / NIGHT STALKERS").
  2. Cuadrículas temáticas: ojos, tornados en círculos de colores, películas.
  3. **Etapa actual:** un solo personaje de dibujo (a menudo un soldado con cara de calavera) y un texto enorme de 2 o 3 palabras en negro y rojo ("BESTIA DE OMAHA", "TODOS IBAN DROGADOS", "MAD JACK").
- Las cuadrículas de iconos ("Todos los Tipos de Propaganda") quedaron entre sus peores resultados.

**Replicable frente a circunstancial**
- **Replicable:** el catálogo en español, los perfiles de personajes históricos extremos y el formato "POV / tu vida en cada rango".
- **Circunstancial:** dos años y medio de historial, la agencia y el doblaje a 15 idiomas.

### 4. Some Guy Who Knows Stuff · [@SomeGuyWhoKnowsStuff](https://www.youtube.com/@SomeGuyWhoKnowsStuff)

**Identidad y posicionamiento**
- **Propuesta** [dato]: "Some guy who knows stuff and explains things about the world". En las descripciones: "Subscribe and chill with me while I explain the universe one strange fact at a time".
- **Nicho:** ciencia, espacio, misterios sin resolver e ingeniería, en recopilaciones de unos 10 puntos.
- **Audiencia** [hipótesis]: gente que ve o escucha mientras se relaja ("chill"). Las duraciones largas (mediana de 17,8 minutos) y el tono calmado apuntan a ese uso.
- **Doblaje** [dato]: 18 pistas en el video revisado.
- **Barrera:** baja en tema, porque misterios y ciencia son inagotables. Alta en ejecución: depende de acertar el tema exacto.

**Evolución** [dato, vidIQ]
- **Primeras semanas:**
  - Cuenta creada el 19-jun-2025.
  - 1.000 suscriptores el día 54, con 16 videos.
  - Un mes estancado en unos 1.100 a 1.300.
- **Primera ola** (8 al 30 de septiembre de 2025, de 1,35 k a 4,4 k suscriptores), asociada [hipótesis] a:
  - "10 Horrifying Things Scientists Found In Space" (18-sep, 1,04 M, ×98,6).
  - "Science Mysteries That Still Can't Be Explained" (26-ago, 483 k, ×63,6).
- **Salto puntual:** +2.500 suscriptores en un día (13-oct-2025), al día siguiente de "The Strangest Things Astronauts Have Seen In Space" (1,40 M).
- **Hitos posteriores:**
  - 100.000 suscriptores el día 359.
  - El 28-jun-2026 su conteo de videos bajó de 109 a 98: retiró o hizo privados 11 videos, por un motivo desconocido.
  - Desde julio de 2026 crece unos 1.000 suscriptores al mes.

**Modelo de contenido**
- **Mediana de 27 k frente a éxitos de más de 1 M:** el más dependiente de éxitos aislados entre los canales grandes. El 10 % top reúne el 60 % de las vistas.
- **Temas de los éxitos:** mitos que resultaron reales, preguntas que la ciencia no explica, el espacio y la ingeniería.
- **El mismo tema puede fallar** [dato]: "Urban Legends That Turned Out To Be Real" sacó 2.400 vistas aquí (×0,1), mientras The Paint Explainer tiene 8,9 M con un título casi igual.

**Miniaturas** (vistas directamente)
- **Plantilla constante:** el **título completo** escrito en una tipografía con remates (serif) gruesa, sobre una franja blanca curva arriba, y debajo un collage dibujado a mano con un personaje de palitos.
- **Contradice la regla de no repetir el título en la miniatura**, y aun así es la plantilla de sus éxitos. Los perdedores usan la misma.

**Replicable frente a circunstancial**
- **Replicable:** recopilaciones largas y calmadas sobre misterios verificables, y una plantilla muy constante y barata.
- **Circunstancial:** el momento de sus primeros éxitos sobre el espacio.

### 5. The Crooked Explainer · [@thecrookedexplainer](https://www.youtube.com/@thecrookedexplainer)

**Identidad y posicionamiento**
- **Propuesta** [dato]: "History has a crooked version of every story you were taught… Dark history. No editorialising".
- **Nicho:** historia oscura. **Subnichos:** la verdad oscura detrás de cosas inocentes (canciones infantiles, cuentos), humanos extraordinarios reales, endogamia.
- **Promesa implícita:** "lo que no te contaron en la escuela".
- **Audiencia** [hipótesis]: adultos jóvenes atraídos por el contraste entre algo infantil y una historia oscura.

**Evolución** [dato, vidIQ]
- **Cinco semanas casi en cero:** 16 videos y 40 suscriptores al 26-abr-2026.
- **Primera ola:**
  - "Actual Dark Truth Behind Every Nursery Rhymes" se publicó el 5 de abril y despegó entre el 28-abr y el 2-may. Tardó unas tres semanas en ser recomendado [hipótesis sobre la causa].
  - 1.000 suscriptores el día 55. Meseta en junio y julio, hasta unos 9.900.
- **Segunda ola:**
  - "The Most Unexplainable Humans in History" (9-ago, 1,39 M) y "The Most Unexplainable Minds in History" (21-ago, 1,36 M) inauguraron un pilar nuevo.
  - 10.000 suscriptores el día 146 y 21.100 a final de septiembre.
- **Sin publicar desde el 30-sep-2026**, pero sigue ganando de 100 a 200 suscriptores al día con el catálogo existente.

**Modelo de contenido**
- **El canal más dependiente de éxitos aislados:** el 10 % top reúne el 72 % de las vistas y un solo video, el 24 %.
- **Partes 2 y 3** de las canciones infantiles: 232 k y 175 k, es decir, el 12 % y el 9 % del original. Aun así superan con mucho a sus vecinos (×38 y ×39).
- **Peor rendimiento:**
  - Navidad oscura: 3,3 k.
  - Cadenas de comida rápida: 1,8 k.
  - Cosas encontradas dentro de humanos: 5 k.

**Miniaturas** (vistas directamente)
- **Tríptico constante:** tres personajes ilustrados de estilo cómic semirrealista, con aspecto de imagen generada por IA [hipótesis], cada uno con una etiqueta de una a tres palabras en negro sobre fondo blanco ("GEORGIE PORGIE / RING AROUND THE ROSIE / ORANGES & LEMONS", "SEES MATH / 2 PAGES AT ONCE / HEARS IT ONCE").
- Los perdedores usan exactamente la misma plantilla.

**Replicable frente a circunstancial**
- **Replicable:** el contraste "algo que conoces de niño" con "la historia real", y las personas extraordinarias reales.
- **Circunstancial:** un solo video explica una cuarta parte del canal.

### 6. Estrictamente · [@estrictamente](https://www.youtube.com/@estrictamente)

**Identidad y posicionamiento**
- **Propuesta** [dato]: "Explico cosas interesantes". Canal en español desde España, con audio doblado a inglés, portugués y árabe.
- **Nicho:** vida cotidiana en el pasado y orígenes de la civilización.
- **Fórmula de título casi única:** una pregunta. "¿Cómo sobrevivían…?", "¿Qué hacía realmente la gente…?", "¿Cómo inventaron los humanos…?".
- **Audiencia** [hipótesis]: curiosos de la historia de "gente común", posiblemente consumida de fondo, por las duraciones de 25 a 60 minutos.
- **Descripciones largas** con viñetas, emojis y muchas etiquetas.

**Evolución** [dato, vidIQ]
- 1.000 suscriptores el día 23. Despegue entre el 3 y el 20 de agosto (de 2.470 a 6.760), coincidiendo con:
  - "¿Cómo Inventaron los Seres Humanos los Países?" (3-ago, 274 k, ×539).
  - "¿Cómo Inventaron los Humanos la Esclavitud?" (4-ago, 162 k).
  - "El arma más letal jamás creada por los humanos prehistóricos" (15-ago, 256 k).
  - "¿Por qué no se levantaban a las 5 AM?" (18-ago, 209 k).
- 10.000 suscriptores el día 102. Hoy 13,8 k.

**Modelo de contenido**
- **Volumen muy alto:** 90 videos en 90 días, con una duración mediana de 30 minutos y varios de 58 a 59.
- **Tasa de acierto baja:** mediana de 7,6 k y muchos videos con menos de 1.000 vistas.
- **Pilares:** prehistoria (orígenes de la sal, de los países, de la esclavitud), Roma ("¿Qué hacía realmente la gente en la antigua Roma durante todo el día?", 294 k), Edad Media (nobles en castillos, 97 k en 7 días) y supervivencia cotidiana (frío, lluvia, camas).
- **Contenido atemporal,** con series temáticas por época.

**Miniaturas** (vistas directamente)
- **Plantilla constante:**
  - Escenas ilustradas muy detalladas, con aspecto de imagen generada por IA [hipótesis].
  - Personajes de estilo "dibujo de palitos con ojos grandes" sobre fondos pintados.
  - Una pregunta corta y enorme en mayúsculas, amarilla y blanca con borde negro ("¿PRIMER PAÍS?", "¿SIN CAMAS?", "¿ESTO ERA LUJO?").
- Los perdedores usan la misma plantilla.

**Replicable frente a circunstancial**
- **Replicable:** el ángulo de vida cotidiana y orígenes en español, y las preguntas cortas en la miniatura.
- **No recomendable copiar:** el volumen diario. Produce muchos videos de muy pocas vistas y puede acercarse a los límites de la política de contenido repetitivo [hipótesis, se revisa en la fase de políticas].

### 7. Lịch Sử Ngoại Truyện · [@lichsungoaitruyen](https://www.youtube.com/@lichsungoaitruyen)

**Identidad y posicionamiento**
- **Propuesta** [dato, traducida]: "historia del mundo contada con animación, donde los imperios caen por razones absurdas… historias reales, fuentes serias. La forma de contarlas no".
- **Nicho:** historia de Vietnam (dinastía Nguyễn, guerra con Francia, Tây Sơn, época antigua) en vietnamita.
- **Títulos casi siempre "Vì sao…?"** ("¿Por qué…?").
- **Fuentes muy detalladas** en cada descripción [dato]: crónicas oficiales, archivos franceses, artículos académicos.
- **Audiencia** [hipótesis]: vietnamitas interesados en su propia historia.
  - Tiene la tasa de likes más baja (0,42 %) y la de comentarios más alta (1,48 por cada 1.000 vistas) del grupo.
  - Hipótesis de la causa: la historia nacional provoca debate.

**Evolución** [dato, vidIQ]
- 1.000 suscriptores el día 40.
- Aceleración en septiembre, con "Vì Sao Pháp Đánh Đà Nẵng 2 Năm Không Xong Phải Bỏ Vào Gia Định?" (176 k, ×12,5).
- Octubre fue su mejor mes (unos 4.800 suscriptores más). Hoy 8,7 k.
- Empezó una serie numerada (TẬP 1 a 5) sobre la historia antigua.

**Miniaturas** (vistas directamente)
- **Plantilla muy constante:**
  - Franja superior de banderas con efecto de papel rasgado.
  - Pregunta en blanco y en mayúsculas a la izquierda ("VÌ SAO…?").
  - Un personaje histórico en ilustración vectorial plana a la derecha.
  - Fondos oscuros y apagados.
- **Excepción:** la única miniatura con estilo fotográfico realista (Mao frente a Chiang) está entre sus peores resultados. Es un solo caso y no permite concluir.

**Lección para nosotros**
- Historia local, en el idioma local y con fuentes rigurosas atrae una audiencia comprometida y creciente sin competir con los gigantes en inglés.
- [Hipótesis]: el equivalente hispano (historia de Colombia y Latinoamérica contada desde una pregunta) merece evaluarse con datos de demanda en la fase 3.

### 8. Squire Explains · [@SquireExplains](https://www.youtube.com/@SquireExplains)

**Identidad y posicionamiento**
- **Propuesta** [dato]: "History's strangest 'why' questions, answered in under a minute by a very smug squire… with hand-drawn animation and the facts checked".
- **Nicho:** historia militar y de guerra contada en Shorts. **Subnicho:** historias insólitas de personas concretas.
- **Mascota recurrente:** un escudero de cabeza redonda y blanca, vestido según la época.
- **Fuentes citadas** en cada descripción [dato].
- **Audiencia** [hipótesis]: el público amplio de Shorts de historia, muy masculino y joven. No se puede verificar.

**Evolución** [dato, vidIQ]
- **El canal más rápido del grupo:** creado el 28-sep-2026.
  - 1.000 suscriptores el día 12.
  - 10.000 el día 26.
  - 12,3 M de vistas y 11,7 k suscriptores el día 28, con 36 publicaciones.
- **Mejores Shorts:**
  - "She Went to War Disguised as Her Brother": 2,76 M en 9 días.
  - "Why This Kamikaze Kept Coming Back…": 1,76 M.
  - "Why Sparta HATED This 300 Survivor": 1,55 M, ×23,5.
- **Primer video largo de éxito:** "Why Knights Stopped Using Shields", 1,02 M en 11 días, ×18. Los otros tres videos largos sacaron entre 9 k y 106 k.

**Modelo de contenido**
- **Pilares:** personas insólitas en guerras, "¿qué pasó con…?" y "¿por qué…?" de historia militar.
- **Shorts** de 0:48 a 1:28.
- **Engagement** [dato]: la tasa de likes más alta del grupo (2,31 %) y muy pocos comentarios (0,21 por cada 1.000 vistas), lo esperable en Shorts.
- **Monetización:** las vistas de Shorts no cuentan como horas de visualización para la monetización de videos largos. El programa tiene una vía propia para Shorts, con requisitos que verificaré en la fuente oficial en la fase de políticas.

**Miniaturas** (vistas directamente)
- **Videos largos:**
  - Ilustración vectorial limpia con la mascota.
  - Texto enorme blanco y redondeado con contorno negro, de una a tres palabras ("USELESS.", "DON'T GO IN!", "ROME VS ELEPHANTS").
  - Fondos simples y planos.
- **Shorts:** la misma mascota y texto con palabras resaltadas en color ("THEY CAN'T FIND OUT", "HE BOMBED AMERICA").

**Replicable frente a circunstancial**
- **Replicable:** la mascota como marca, la pregunta "¿por qué?" en menos de un minuto, las fuentes citadas y usar los Shorts para validar temas antes del video largo. Así parece haber nacido "Why Knights Stopped Using Shields" [hipótesis].
- **Circunstancial:** un mes de vida. Es pronto para saber si el crecimiento se sostiene.

---

## Hipótesis transversales (borrador para la matriz de la fase 4)

**Grupos provisionales:**
- **A:** respaldado por varios canales y con explicación razonable.
- **B:** prometedor pero sin validar.
- **C:** circunstancial.

| # | Recurso | Canales donde lo vi | Evidencia hasta ahora | Facilidad para adaptarlo | Grupo |
|---|---|---|---|---|---|
| 1 | Ilustración propia y reconocible, sin rostro | 8 de 8 | Todas las miniaturas revisadas | Alta (tienes perfil de diseñador y motion) | A como requisito del género, no como causa del éxito |
| 2 | Catálogo "todos los X / cada X explicado" | The Paint Explainer, Simple Paint, Te Lo Pinto Fácil | Aparece en los tops absolutos de los tres | Alta | B |
| 3 | Temas de muerte, peligro y extremos | The Paint Explainer, Simple Paint, The Crooked Explainer, Te Lo Pinto Fácil | Tops de cuatro canales; 18 % frente a 12 % en la comparación de quintiles | Media (riesgo de publicidad limitada) | B |
| 4 | Una pregunta concreta como columna del canal ("¿por qué…?", "¿cómo vivían…?") | Squire Explains, Estrictamente, Lịch Sử Ngoại Truyện | Es el formato del canal, no separa ganadores de perdedores | Alta | B |
| 5 | Personaje o mascota recurrente | Squire Explains, Estrictamente, Some Guy Who Knows Stuff, Te Lo Pinto Fácil | Squire es el que más rápido creció; correlación, no causa | Alta | B |
| 6 | Miniatura comparativa de 2 o 3 personajes etiquetados | Simple Paint, The Paint Explainer, The Crooked Explainer, Te Lo Pinto Fácil | Ganadores y perdedores la usan por igual | Alta | B |
| 7 | Texto en miniatura de 1 a 3 palabras, distinto del título | Squire Explains, Te Lo Pinto Fácil (actual), Estrictamente, Simple Paint | Some Guy Who Knows Stuff repite el título completo y también funciona | Alta | B |
| 8 | Partes 2 y 3 de los éxitos | The Paint Explainer, Simple Paint, The Crooked Explainer, Te Lo Pinto Fácil | Resultado desde 0,01 hasta 1,9 veces el original | Alta | B (es una apuesta, no una garantía) |
| 9 | Audio doblado a varios idiomas | Simple Paint, Some Guy Who Knows Stuff, Te Lo Pinto Fácil, Estrictamente | Lo usan los canales con más alcance; no medí su efecto | Media | B, para la etapa de escalado |
| 10 | Fuentes citadas y declaración de uso de IA | The Paint Explainer, Squire Explains, Lịch Sử Ngoại Truyện | Relevante para la confianza y las políticas, no para las vistas | Alta | A en cumplimiento |
| 11 | Shorts como motor de arranque | Funcionó en Squire Explains (mediana de 107 k); no en Te Lo Pinto Fácil (mediana de 10 k, abandonados) | Dos casos opuestos | Media | B |
| 12 | Videos largos de 17 a 30 minutos o más | Some Guy Who Knows Stuff, Te Lo Pinto Fácil, Estrictamente | Sin datos de retención no se puede saber si suman horas de visualización | Media | B |
| 13 | Historia local en el idioma local | Lịch Sử Ngoại Truyện | Un caso con fuentes rigurosas y crecimiento sostenido | Alta | B |
| 14 | Volumen diario (un video al día o más) | Estrictamente | Mediana de 7,6 k; tasa de acierto baja | Baja | C, con riesgo de políticas |
| 15 | Red de canales hermanos y agencia | Simple Paint, Te Lo Pinto Fácil | Propio de canales ya grandes | Baja al inicio | C |
| 16 | Despegue tardío: el primer éxito llega tras 16 a 50 videos | The Crooked Explainer, Some Guy Who Knows Stuff, Estrictamente (Squire Explains fue la excepción) | Historial diario de vidIQ | No aplica | A como expectativa: hay que planificar para no rendirse antes |

---

## Qué no sé todavía

- **Guiones, ganchos de apertura (hooks) y estructura:** no he leído transcripciones. No digo nada de lo que pasa dentro de los videos. Es la fase 2.
- **Producción audiovisual:** animación, ritmo de cortes, música y calidad de la voz. Todavía no he visto los videos, solo las miniaturas.
- **Fechas:** exactas en 346 videos. En el resto se deducen de "hace X meses": error de ±1 mes en lo reciente y de varios meses en videos de más de un año.
- **Vistas:**
  - Exactas en 346 videos.
  - Redondeadas en el resto, con un error de ±15 % en la muestra verificada.
  - Seis videos aparecen con 0 vistas en la lista pública y no tienen dato exacto. Los excluyo de las medianas y del ranking.
- **Historial de crecimiento:** no consulté The Paint Explainer ni Simple Paint.
- **Métricas privadas** (CTR, retención, fuentes de tráfico, ingresos): imposibles de obtener para canales ajenos. Cualquier cifra de este tipo que veas en internet sobre ellos es una estimación.
- **Audiencias:** todas las descripciones de público son hipótesis.

## Próximo paso propuesto (fase 2)

1. Para cada canal, leer la transcripción de 6 a 10 de los videos del ranking: mezcla de éxito absoluto, éxito relativo, reciente y peor resultado como contraste. Analizar el hook (5, 15 y 30 segundos), la estructura y los recursos de retención.
2. Extraer fotogramas de 2 o 3 videos por canal para analizar la producción, en cuanto YouTube deje de bloquear este contenedor.
3. Con eso, cerrar las columnas de guion y producción de la base de datos y pasar a la fase 3 (palabras clave con vidIQ) centrada en los temas candidatos que salgan de aquí.
