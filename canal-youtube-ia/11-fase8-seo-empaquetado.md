# Fase 8: SEO, títulos, miniaturas y descripciones

**Qué incluye este documento:**

- El sistema para puntuar ideas.
- El paquete completo de los 6 primeros videos.
- Las reglas de metadatos.
- El método de pruebas A/B.

**De dónde salen los datos:**

| Tipo | Fuente |
|---|---|
| Demanda | Fase 3: `datos/keywords_vidiq.csv` y `datos/autocompletar_youtube_2026-10-27.json` |
| Patrones de título y miniatura | Fase 4 |
| Identidad visual | Fase 6 |
| Reglas de YouTube | Fase 10 y la ayuda oficial, consultada el 27-oct-2026 |

**Cálculo reproducible:** `scripts/banco_ideas.py` genera `datos/banco_ideas.csv`.

**Cómo leer las etiquetas:**

- **Dato:** viene de una fuente o de una medición.
- **Estimación:** cifra de vidIQ.
- **Hipótesis:** interpretación mía que todavía hay que validar.

**Advertencia sobre los hechos históricos:** los títulos y las descripciones mencionan datos que **se confirman con fuentes en la fase de investigación**, antes de producir. Los marco con "(verificar)". Si un dato no se confirma, el título se cambia. Es la promesa del canal: "Con fuentes. Sin cuentos."

---

## 1. Sistema de puntuación de ideas

Cada idea recibe de 1 a 5 puntos en 8 criterios. **Total = Σ(puntos × peso) ÷ 5**, sobre 100. Las puntuaciones son juicios míos, basados en la evidencia escrita en la columna `evidencia_demanda`.

| Criterio | Peso | 1 punto | 3 puntos | 5 puntos |
|---|---|---|---|---|
| Demanda | 20 | Sin evidencia | Autocompletado en un país, o menos de 5.000 búsquedas al mes en vidIQ | 20.000 búsquedas o más en vidIQ, o autocompletado en 3 países |
| Curiosidad o contraste emocional (fase 4, rasgo 6) | 15 | Dato informativo plano | Tema interesante sin paradoja | Paradoja o misterio que se entiende en un segundo |
| Encaje con la promesa "lo que es verdad" | 15 | No hay creencia que contrastar | La creencia existe, pero el veredicto es difuso | Creencia popular clara y veredicto claro |
| Fuentes disponibles | 15 | Solo tradición oral sin estudiar | Fuentes secundarias | Fuentes primarias y académicas accesibles en español |
| Diferenciación | 10 | El tema ya está cubierto con este ángulo y esta calidad | Está cubierto, pero sin fuentes ni animación propia | Nadie lo cubre con este ángulo (hipótesis) |
| Apto para anunciantes (fase 10) | 10 | No se puede contar sin violencia gráfica ni abuso infantil | Requiere tratarlo de forma no gráfica | Sin riesgo |
| Shorts y serie | 5 | No da para Shorts | Da 1 Short | Da 3 Shorts o más, o abre una serie |
| Costo bajo | 10 | Personajes y escenarios nuevos y complejos | Mezcla de recursos nuevos y reutilizados | Reutiliza la biblioteca de recursos |

**Qué se hace con cada idea según su total:**

- **75 o más:** producir pronto.
- **De 60 a 74:** se queda en el banco de ideas.
- **Menos de 60:** reformular o descartar.

**Cuándo se vuelve a puntuar:**

- El **costo** baja cuando ya existen los recursos. Por ejemplo, "Así vivías en Tenochtitlan" se abarata después del video del lago.
- La **demanda** se corrige cuando haya datos de vidIQ, a partir del 27-nov-2026.

### Banco inicial: 16 ideas

| # | Idea | Pilar | Evidencia de demanda | Total | Decisión |
|---|---|---|---|---|---|
| I01 | La verdadera historia de La Llorona | P1 | Autocompletado en México, Colombia y Argentina; "mitos y leyendas" 53.300 al mes (competencia 42) | **87** | Producir |
| I02 | ¿Por qué Colombia se llama Colombia? | P2 | "historia de colombia" 40.400 al mes (competencia 46, +142 %) | **85** | Producir |
| I04 | El Dorado: lo que sí existió | P1 | Sin medir | **83** | Producir (medir en noviembre) |
| I07 | El chupacabras: cómo nació un monstruo moderno | P1 | Autocompletado en México y Colombia | **82** | Producir |
| I05 | ¿De verdad unos cientos de españoles conquistaron a los mexicas? | P2 | "hernan cortes" 26.200 al mes; autocompletado "porque los españoles conquistaron mexico" | **81** | Producir |
| I10 | ¿Por qué Panamá dejó de ser parte de Colombia? | P2 | "historia de colombia"; la pregunta exacta sin medir | **80** | Producir (mes 2) |
| I09 | ¿Por qué la capital de México está sobre un lago? | P2 | "historia de mexico" 58.900 al mes | **78** | Producir |
| I08 | Las momias de Guanajuato: la historia real | P1 | Autocompletado en México, Colombia y Argentina | **75** | Producir con cuidado: cadáveres, posible publicidad limitada |
| I13 | ¿Por qué los incas no escribían? (los quipus) | P2 | Autocompletado "los incas", mezclado con resultados de música | 74 | Banco |
| I03 | Así vivías si nacías en Tenochtitlan | P3 | "como vivian los aztecas" 4.500 al mes (competencia 40); "tenochtitlan" 21.500 | 71 | Banco (sube después de I09) |
| I06 | Una leyenda de cada país de Latinoamérica | P4 | Autocompletado "leyendas de cada país" | 67 | Banco, como catálogo del mes 2 |
| I14 | Así vivías en la Nueva España | P3 | Autocompletado en México | 65 | Banco |
| I11 | El Silbón: de dónde sale la leyenda | P1 | Autocompletado en Colombia | 63 | Banco |
| I12 | La Patasola, el Mohán y la Madremonte | P1 | Autocompletado | 59 | Reformular (pocas fuentes) |
| I15 | La Nahuala | P1 | Autocompletado, pero quien lo busca quiere la película animada de 2007 | 56 | Descartar: el público buscado es infantil |
| I16 | El Charro Negro | P1 | Autocompletado, pero lo dominan las búsquedas de la película animada de 2018 | 56 | Descartar por la misma razón |

**Qué enseñan las ideas descartadas:**

- Un buen volumen en el autocompletado **no basta**: hay que mirar *quién* busca.
- "La leyenda de la Nahuala" y "del Charro Negro" encabezan el autocompletado porque son títulos de películas animadas.
- Ese público choca con el riesgo de que YouTube clasifique el canal como "creado para niños" (fase 10).

---

## 2. Reglas de metadatos

| Elemento | Regla | Base |
|---|---|---|
| **Título** | Entre 35 y 56 caracteres. Las primeras palabras dicen el tema (La Llorona, Colombia, El Dorado). Usa una de las estructuras de la fase 4: "¿Por qué…?", "La verdadera historia de…", "Lo que es verdad de…" o "Así vivías…". Nunca afirma algo que el video no demuestre | Fase 4 (estructuras) y fase 10 (metadatos engañosos) |
| **Miniatura** | Regla 1-2-3 de la fase 6. El texto completa el título y no lo repite. Debe leerse a 168×94 px. Nada de heridas, cadáveres ni niños en peligro | Fases 4, 6 y 10 |
| **Descripción** | Las 2 primeras líneas dicen la pregunta y el término de búsqueda principal, porque es lo que se ve antes de "más". Después van los capítulos, las **fuentes** y una nota de producción (IA y voz). Al final, la lista de reproducción y 3 hashtags | La ayuda de YouTube dice que "title, thumbnail, and description are more important" que las etiquetas ([146402](https://support.google.com/youtube/answer/146402)) |
| **Capítulos** | El primero empieza en 00:00. Mínimo 3, cada uno de al menos 10 segundos. Los capítulos manuales sustituyen a los automáticos ([9884579](https://support.google.com/youtube/answer/9884579)) | Oficial |
| **Etiquetas** | De 5 a 10: el término principal, las variantes con y sin tilde ("tenochtitlan", "tenochtitlán") y los errores frecuentes. Las etiquetas "play a minimal role in your video's discovery". No hay que poner etiquetas en exceso en la descripción: va contra la política de spam ([146402](https://support.google.com/youtube/answer/146402)) | Oficial |
| **Hashtags** | 3, siempre relacionados con el video. YouTube muestra "up to three" junto al título. Si un video tiene más de 60, se ignoran todos ([6390658](https://support.google.com/youtube/answer/6390658)) | Oficial |
| **Listas de reproducción** | Una por pilar: "Leyendas: lo que es verdad", "¿Por qué…? Historia de Latinoamérica", "Así vivías en…" y "De cada país". El título de la lista incluye el término de búsqueda | Fase 4 (pilares reconocibles) |
| **Pantalla final** | Últimos 20 segundos, después del veredicto. Muestra 1 video relacionado y el botón de suscripción. No se pide suscripción a mitad del video | Fase 4 (rasgo 10) y fase 6 |
| **Comentario fijado** | Fuentes con enlace, más una pregunta concreta. Ejemplo: "¿Qué versión de La Llorona te contaron en tu país?" | Hipótesis: invita a comentar por país |
| **Audiencia** | "No, no es contenido para niños" en todos los videos | Fase 10 |
| **Uso de IA** | Se marca "Sí" solo si hay recreaciones fotorrealistas o música generada con IA como protagonista. Con el estilo ilustrado de la casa, normalmente es "No" | Fase 10 |

### Plantilla de descripción

```
[Línea 1: la pregunta con el término de búsqueda principal]
[Línea 2: la promesa: qué se comprueba y con qué fuentes]

En este video:
• [lo que vas a descubrir 1]
• [lo que vas a descubrir 2]
• [lo que vas a descubrir 3]

Capítulos
00:00 …

Fuentes
1. [fuente primaria con fecha]
2. [fuente académica]
3. [museo o archivo, con enlace]

Cómo hacemos los videos: guion investigado y escrito por el canal; ilustración y animación propias. Algunas imágenes de base se generaron con IA y se redibujaron al estilo del canal. Narración: [voz propia / voz sintética].

▶ Lista: [nombre de la lista]
▶ Siguiente expediente: [título y enlace]

#[tema] #[pilar] #[región]
```

---

## 3. Paquetes de lanzamiento: 6 videos

**Por qué estos seis:**

- Son 6 de las 8 ideas que superan los 75 puntos.
- Mezclan los pilares P1 y P2.
- Reparten los países ancla: 3 de México, 2 de Colombia y 1 de Puerto Rico y la región.
- I10 (Panamá) e I08 (momias) se dejan para el mes 2. Así I08 no coincide con otro tema de muerte en el arranque.

**Cuándo se publica cada uno:** lo fija la fase 11.

**Por qué la búsqueda importa tanto en el lanzamiento:** un canal nuevo recibe poco tráfico de recomendaciones. Por eso el término de búsqueda principal tiene peso propio en estos primeros videos (hipótesis).

### Video 1: La verdadera historia de La Llorona (P1)

| Campo | Contenido |
|---|---|
| **Término de búsqueda principal** | "la verdadera historia de la llorona": autocompletado en México, Colombia y Argentina (dato). No hay volumen medido |
| **Términos secundarios** | "la leyenda de la llorona" (autocompletado en los 3 países), "mitos y leyendas" (53.300 al mes, competencia 42, estimación), "leyendas mexicanas" (22.300 al mes, +125 %, estimación), "mitos y leyendas la llorona" (autocompletado) |
| **Qué busca quien escribe esto** | Saber si existió y de dónde sale. Mezcla curiosidad y algo de miedo. Hay una parte de búsqueda escolar |
| **Audiencia (hipótesis)** | Jóvenes y adultos de toda la región que crecieron con la leyenda. Los que vienen del terror deben sentir que se respeta el misterio |
| **Título principal** | La verdadera historia de La Llorona (según las crónicas) — 56 caracteres |
| **Alternativas** | 1. ¿Existió La Llorona? Esto dicen los documentos (46) · 2. ¿La Llorona ya lloraba antes de la conquista? (45) · 3. Lo que es verdad (y lo que no) de La Llorona (44) · 4. ¿La Llorona era una diosa mexica? (33) · 5. La Llorona antes de ser leyenda (31) |
| **Miniatura A** | La de la fase 6. Una mujer de espaldas con rebozo junto al río y su reflejo borroso. Texto "¿EXISTIÓ?" y sello "¿LEYENDA?" |
| **Miniatura B** | Pantalla dividida: a la izquierda, una figura indígena con atuendo ceremonial, en el estilo grabado; a la derecha, la silueta de La Llorona colonial. Texto "ANTES DE 1519" en cochinilla. Funciona con la alternativa 2 |
| **Miniatura C** | Una página de códice abierta con una mano que señala un párrafo resaltado. Al fondo, la silueta de la mujer. Texto "LO DICE AQUÍ". Promete pruebas |
| **Capítulos (provisionales)** | 00:00 El grito que todos conocemos · 00:50 La versión que te contaron · 02:10 Un presagio antes de la conquista · 04:00 ¿Una diosa mexica? · 05:40 Cómo cambió la leyenda en la colonia · 07:30 Por qué cada país tiene su Llorona · 09:00 Veredicto |
| **Hashtags** | #LaLlorona #leyendas #historiademéxico |
| **Ideas relacionadas** | La Llorona en cada país (Short y P4) · Cihuacóatl: la diosa que gritaba de noche · Los 8 presagios de la conquista |
| **Hipótesis de clic** | Casi todo el mundo en la región conoce La Llorona. La palabra "verdadera" promete un contraste. "Según las crónicas" distingue el video de los canales de terror |
| **Riesgo de expectativa** | Quien busca miedo puede irse cuando empieza la parte documental. **Cómo se mitiga:** abrir con la escena del grito, contada con suspense y sin efectos de susto. El veredicto se presenta como un giro, no como una lección |
| **Riesgos de política** | En la leyenda hay infanticidio. **Cómo se mitiga:** no se muestran niños en el video ni en la miniatura y el acto no se dramatiza (fase 10, sección 5) |
| **Datos que hay que verificar** | El presagio de la mujer que llora en el libro XII del Códice Florentino de Sahagún. La relación con Cihuacóatl: es una interpretación académica y se presenta como tal. Las primeras versiones coloniales escritas y su fecha |

**Descripción**

```
¿Cuál es la verdadera historia de La Llorona? Antes de ser una leyenda de terror, fue un presagio que los informantes de Sahagún asociaron con la llegada de los españoles (verificar cita exacta).
Revisamos las crónicas para separar lo documentado de lo que añadió la tradición.

En este video:
• Qué dice el Códice Florentino sobre una mujer que lloraba de noche
• Por qué algunos historiadores la relacionan con la diosa Cihuacóatl (y por qué otros no)
• Cómo la leyenda cambió en la colonia y por qué cada país tiene su versión

Capítulos
00:00 El grito que todos conocemos
00:50 La versión que te contaron
02:10 Un presagio antes de la conquista
04:00 ¿Una diosa mexica?
05:40 Cómo cambió la leyenda en la colonia
07:30 Por qué cada país tiene su Llorona
09:00 Veredicto

Fuentes
1. Bernardino de Sahagún, Historia general de las cosas de la Nueva España (Códice Florentino), libro XII.
2. [Estudio académico sobre la leyenda: completar en la investigación]
3. [Archivo o museo con la imagen usada: completar]

Cómo hacemos los videos: guion investigado y escrito por el canal; ilustración y animación propias. Algunas imágenes de base se generaron con IA y se redibujaron al estilo del canal.

▶ Lista: Leyendas: lo que es verdad
▶ Siguiente expediente: El Dorado: lo que sí existió

#LaLlorona #leyendas #historiademéxico
```

### Video 2: ¿Por qué Colombia se llama Colombia? (P2)

| Campo | Contenido |
|---|---|
| **Término de búsqueda principal** | "historia de colombia": 40.400 al mes, competencia 46, +142 %, 60 % desde Colombia (estimación). La pregunta exacta no está medida |
| **Términos secundarios** | "por que colombia se llama colombia" (sin medir), "gran colombia", "nueva granada", "francisco de miranda" |
| **Qué busca quien escribe esto** | Curiosidad sobre identidad nacional. Hay una parte escolar |
| **Audiencia (hipótesis)** | Colombianos de 16 a 35 años y la diáspora. También venezolanos, ecuatorianos y panameños, porque compartieron "Colombia" entre 1819 y 1831 |
| **Título principal** | ¿Por qué Colombia se llama Colombia? — 36 caracteres |
| **Alternativas** | 1. ¿Quién le puso el nombre a Colombia? (36) · 2. Colombia cambió de nombre varias veces. ¿Por qué? (49) · 3. Colombia: el nombre que soñó Miranda (36) · 4. Antes de llamarse Colombia, este país se llamaba… (49) · 5. Colombia lleva el nombre de alguien que nunca vino (50, solo si se confirma que Colón no pisó el territorio actual) |
| **Miniatura A** | La de la fase 6. Un navegante desconcertado ante un mapa rotulado "COLOMBIA". Texto "¿POR QUÉ ÉL?" |
| **Miniatura B** | Una línea de tiempo con 4 o 5 rótulos de nombres tachados, del estilo de un sello de archivo, y el último marcado en oro muisca. Texto "5 NOMBRES" (solo si se verifica el número) o "¿Y ANTES?" |
| **Miniatura C** | Miranda ilustrado en estilo grabado con un mapa de toda Hispanoamérica rotulado "COLOMBIA". Texto "ERA TODO". Promesa: el nombre era para todo el continente |
| **Capítulos (provisionales)** | 00:00 Un país con nombre de navegante · 00:40 ¿Colón estuvo aquí? · 02:00 La idea de Miranda · 03:40 1819: nace "Colombia" · 05:20 Nueva Granada, Confederación, Estados Unidos… · 07:30 1886: el nombre definitivo · 08:40 Veredicto |
| **Hashtags** | #Colombia #historiadecolombia #latinoamérica |
| **Ideas relacionadas** | ¿Por qué Panamá dejó de ser parte de Colombia? (I10) · ¿Por qué Venezuela se llama Venezuela? (Short) · Los nombres que casi tuvo cada país (P4) |
| **Hipótesis de clic** | Es una pregunta obvia que casi nadie sabe responder. Además, habla de la identidad del espectador |
| **Riesgo de expectativa** | Bajo. El video tiene que responder pronto (antes del minuto 2) y luego ofrecer un segundo misterio: los cambios de nombre |
| **Riesgos de política** | Ninguno relevante. Se evita la política reciente |
| **Datos que hay que verificar** | Que Colón no pisó el territorio colombiano actual. Que el nombre se atribuye a Miranda. La Ley Fundamental de Angostura (1819). Los nombres oficiales y sus fechas: 1831/1832, 1858, 1863 y 1886 |

**Descripción**

```
¿Por qué Colombia se llama Colombia? El nombre honra a Cristóbal Colón, pero la idea de usarlo para un país vino de Francisco de Miranda y pensaba en todo el continente (verificar).
Recorremos los documentos que fueron cambiando el nombre del país hasta 1886.

En este video:
• Quién propuso el nombre "Colombia" y para qué territorio
• Por qué el país se llamó Nueva Granada, Confederación Granadina y Estados Unidos de Colombia
• Qué pasó en 1886 para que el nombre quedara fijo

Capítulos
00:00 Un país con nombre de navegante
00:40 ¿Colón estuvo aquí?
02:00 La idea de Miranda
03:40 1819: nace "Colombia"
05:20 Nueva Granada, Confederación, Estados Unidos…
07:30 1886: el nombre definitivo
08:40 Veredicto

Fuentes
1. Ley Fundamental de la República de Colombia, Angostura, 17 de diciembre de 1819.
2. Constitución Política de la República de Colombia, 1886.
3. [Estudio académico sobre Miranda y el nombre "Colombia": completar]

Cómo hacemos los videos: guion investigado y escrito por el canal; ilustración y animación propias.

▶ Lista: ¿Por qué…? Historia de Latinoamérica
▶ Siguiente expediente: ¿Por qué Panamá dejó de ser parte de Colombia?

#Colombia #historiadecolombia #latinoamérica
```

### Video 3: El Dorado: lo que sí existió (P1, Colombia)

| Campo | Contenido |
|---|---|
| **Término de búsqueda principal** | "el dorado" o "leyenda de el dorado". **Sin medir.** Es lo primero que se mide cuando se renueven los créditos de vidIQ (27-nov). El término suelto "el dorado" compite con otros usos: películas, aeropuerto, comercios |
| **Términos secundarios** | "laguna de guatavita", "balsa muisca", "muiscas", "museo del oro", "leyendas de colombia" (autocompletado) |
| **Qué busca quien escribe esto** | Saber si existió la ciudad de oro. Curiosidad y aventura |
| **Audiencia (hipótesis)** | Toda la región, más el público de misterios y tesoros perdidos |
| **Título principal** | El Dorado sí existió (pero no era una ciudad) — 45 caracteres |
| **Alternativas** | 1. El Dorado no era un lugar: era una persona (42) · 2. Lo que es verdad de El Dorado (29) · 3. La laguna donde nació El Dorado (31) · 4. ¿Qué buscaban de verdad en El Dorado? (37) · 5. El Dorado: la ceremonia muisca detrás del mito (46) |
| **Miniatura A** | Un cacique cubierto de polvo de oro sobre una balsa, en una laguna oscura, con el oro como única fuente de luz. Texto "NO ERA CIUDAD". Sello "¿LEYENDA?" |
| **Miniatura B** | La silueta de la balsa muisca (pieza de museo, dibujada al estilo de la casa) frente a la ciudad dorada imaginaria, tachada. Texto "ESTO SÍ" con una flecha a la balsa |
| **Miniatura C** | Un conquistador con antorcha frente a una laguna vacía. Texto "¿DÓNDE ESTÁ?". Aprovecha la curiosidad por el tesoro |
| **Capítulos (provisionales)** | 00:00 La ciudad que nadie encontró · 00:45 "El Dorado" era un hombre · 02:15 La ceremonia de Guatavita · 04:00 Lo que cuenta El Carnero · 05:30 La balsa muisca · 07:00 Cuando intentaron vaciar la laguna · 08:40 Veredicto |
| **Hashtags** | #ElDorado #muiscas #historiadecolombia |
| **Ideas relacionadas** | ¿Por qué los conquistadores creían en ciudades de oro? · Los muiscas: así vivías en el altiplano (P3) · Leyendas de tesoros de cada país (P4) |
| **Hipótesis de clic** | El título contradice lo que todos creen ("no era una ciudad"), sin que el espectador pueda adivinar la respuesta. La imagen del oro sobre el agua es muy llamativa |
| **Riesgo de expectativa** | Quien quiera "la ciudad perdida encontrada" puede decepcionarse. **Cómo se mitiga:** el título ya avisa ("no era una ciudad"). El gancho es la ceremonia, que cumple lo que promete el oro |
| **Riesgos de política** | Ninguno relevante |
| **Datos que hay que verificar** | El relato de Juan Rodríguez Freyle en *El Carnero* (siglo XVII) y la distancia temporal con los hechos. La balsa muisca: hallazgo en 1969 y su relación con el ritual (atribuida, no probada). Los intentos de vaciar la laguna de Guatavita y sus fechas |

**Descripción**

```
¿Existió El Dorado? La leyenda de la ciudad de oro nació de algo más pequeño y más real: una ceremonia muisca en la laguna de Guatavita, descrita por los cronistas (verificar).
Separamos la ceremonia documentada del mito que movió expediciones durante siglos.

En este video:
• Por qué "El Dorado" era al principio una persona y no un lugar
• Qué cuenta Juan Rodríguez Freyle en El Carnero y cuánto podemos fiarnos
• Qué muestra la balsa muisca del Museo del Oro

Capítulos
00:00 La ciudad que nadie encontró
00:45 "El Dorado" era un hombre
02:15 La ceremonia de Guatavita
04:00 Lo que cuenta El Carnero
05:30 La balsa muisca
07:00 Cuando intentaron vaciar la laguna
08:40 Veredicto

Fuentes
1. Juan Rodríguez Freyle, Conquista y descubrimiento del Nuevo Reino de Granada (El Carnero), siglo XVII.
2. Museo del Oro, Banco de la República: ficha de la balsa muisca.
3. [Estudio académico sobre el mito de El Dorado: completar]

Cómo hacemos los videos: guion investigado y escrito por el canal; ilustración y animación propias. Algunas imágenes de base se generaron con IA y se redibujaron al estilo del canal.

▶ Lista: Leyendas: lo que es verdad
▶ Siguiente expediente: El chupacabras

#ElDorado #muiscas #historiadecolombia
```

### Video 4: El chupacabras: cómo nació un monstruo moderno (P1, Puerto Rico y México)

| Campo | Contenido |
|---|---|
| **Término de búsqueda principal** | "la leyenda del chupacabras": autocompletado en México y Colombia (dato). Sin volumen medido |
| **Términos secundarios** | "chupacabras", "chupacabras real", "leyendas de terror" (14.200 al mes, +86 %, estimación), "leyendas urbanas" (23.400 al mes, estimación) |
| **Qué busca quien escribe esto** | Saber si es real y de dónde salió. Curiosidad y nostalgia de los 90 |
| **Audiencia (hipótesis)** | Personas de 25 a 40 años que vivieron la ola de los 90, y jóvenes que lo conocen como meme |
| **Título principal** | El chupacabras: cómo nació un monstruo en 1995 — 46 caracteres |
| **Alternativas** | 1. ¿De dónde salió el chupacabras? (31) · 2. La verdadera historia del chupacabras (37) · 3. El chupacabras tiene fecha de nacimiento (40) · 4. Lo que es verdad (y lo que no) del chupacabras (46) · 5. ¿El chupacabras salió de una película? (37, solo si se presenta como hipótesis de un investigador) |
| **Miniatura A** | El chupacabras dibujado como un recorte de periódico de los 90 con la fecha marcada en cochinilla. Texto "NACIÓ EN 1995" |
| **Miniatura B** | Un granjero con linterna frente a un corral vacío, de noche, y la sombra de la criatura en la pared. Texto "¿REAL?" |
| **Miniatura C** | La criatura de perfil junto a un televisor de tubo que la muestra. Texto "LO CREÓ LA TV". Solo si se confirma el papel de los medios |
| **Capítulos (provisionales)** | 00:00 Ocho ovejas en Puerto Rico · 01:00 La descripción que lo cambió todo · 02:40 Quién le puso el nombre · 04:00 De Puerto Rico a México · 05:40 ¿Qué mataba a los animales? · 07:20 Por qué seguimos hablando de él · 08:30 Veredicto |
| **Hashtags** | #chupacabras #leyendasurbanas #misterios |
| **Ideas relacionadas** | Monstruos modernos de Latinoamérica (P4) · ¿Por qué todos los países tienen un monstruo que chupa sangre? · Short: "el nombre lo inventó un humorista" |
| **Hipótesis de clic** | La nostalgia de los 90 y una afirmación concreta (una fecha) que convierte un mito en algo que se puede investigar |
| **Riesgo de expectativa** | Quien quiera "pruebas de que existe" se irá. **Cómo se mitiga:** el veredicto (LEYENDA moderna) se anuncia como una investigación, y las ovejas muertas se presentan como el misterio inicial |
| **Riesgos de política** | Muertes de animales: no mostrar heridas. Tono documental |
| **Datos que hay que verificar** | Los primeros casos de 1995 en Puerto Rico. La atribución del nombre a Silverio Pérez. La hipótesis de Benjamin Radford (*Tracking the Chupacabra*, 2011) sobre la influencia de la película *Species*. La expansión a México en 1996 |

**Descripción**

```
¿De dónde salió el chupacabras? A diferencia de La Llorona, este monstruo tiene fecha y lugar de nacimiento: Puerto Rico, 1995 (verificar).
Reconstruimos cómo una ola de animales muertos se convirtió en la leyenda más famosa de los 90.

En este video:
• Qué pasó en Puerto Rico en 1995 y quién le puso el nombre
• Por qué la descripción de la criatura cambió entre Puerto Rico y México
• Qué explicaciones dieron los investigadores

Capítulos
00:00 Ocho ovejas en Puerto Rico
01:00 La descripción que lo cambió todo
02:40 Quién le puso el nombre
04:00 De Puerto Rico a México
05:40 ¿Qué mataba a los animales?
07:20 Por qué seguimos hablando de él
08:30 Veredicto

Fuentes
1. Benjamin Radford, Tracking the Chupacabra: The Vampire Beast in Fact, Fiction, and Folklore (2011).
2. [Hemeroteca: prensa de Puerto Rico y México de 1995-1996: completar]
3. [Estudio académico sobre leyendas contemporáneas: completar]

Cómo hacemos los videos: guion investigado y escrito por el canal; ilustración y animación propias.

▶ Lista: Leyendas: lo que es verdad
▶ Siguiente expediente: ¿De verdad unos cientos de españoles conquistaron a los mexicas?

#chupacabras #leyendasurbanas #misterios
```

El capítulo "Ocho ovejas" es provisional: la cifra se confirma en la hemeroteca o se cambia.

### Video 5: ¿De verdad unos cientos de españoles conquistaron a los mexicas? (P2)

| Campo | Contenido |
|---|---|
| **Término de búsqueda principal** | "conquista de mexico": autocompletado ("la conquista de mexico", "la conquista de tenochtitlan"). **Respaldo medido:** "hernan cortes" (26.200 al mes, competencia 59, estimación) |
| **Términos secundarios** | "porque los españoles conquistaron mexico" (autocompletado en México, Colombia y Argentina), "tlaxcaltecas", "moctezuma" (20.500 al mes, estimación), "tenochtitlan" (21.500 al mes, estimación) |
| **Qué busca quien escribe esto** | Entender una paradoja de la escuela. Hay debate |
| **Audiencia (hipótesis)** | Mexicanos de 18 a 40 años y público de historia de toda la región |
| **Título principal** | ¿De verdad 500 españoles conquistaron a los mexicas? — 52 caracteres |
| **Alternativas** | 1. ¿Por qué los españoles conquistaron México? (43, coincide con el autocompletado) · 2. Los aliados olvidados de Hernán Cortés (38) · 3. La conquista de México no fue solo española (43) · 4. Tlaxcala: el pueblo que decidió la conquista (44) · 5. Lo que es verdad de la conquista de México (42) |
| **Miniatura A** | Pocos soldados españoles en primer plano y, detrás, un ejército enorme de guerreros tlaxcaltecas que se ve al girar la vista. Texto "¿SOLO 500?" con "500" en cochinilla |
| **Miniatura B** | Cortés en estilo grabado, empequeñecido junto a una multitud de aliados indígenas. Texto "NO ESTABA SOLO" |
| **Miniatura C** | Un mapa del valle de México con flechas de muchos pueblos convergiendo en Tenochtitlan. Texto "TODOS CONTRA…" Pide verificar que no se lea como una toma de partido |
| **Capítulos (provisionales)** | 00:00 La cifra que no cuadra · 01:00 Lo que nos contaron · 02:20 Tlaxcala · 04:00 La viruela · 05:40 Los pueblos sometidos por los mexicas · 07:20 Lo que Cortés no contó en sus cartas · 09:00 Veredicto |
| **Hashtags** | #historiademéxico #conquista #tenochtitlan |
| **Ideas relacionadas** | ¿Por qué la capital de México está sobre un lago? (I09) · Los 8 presagios de la conquista · ¿Cómo conquistaron unos pocos a los incas? (paralelo en Perú) |
| **Hipótesis de clic** | Una paradoja numérica que la gente recuerda de la escuela, con una respuesta que contradice la versión simple |
| **Riesgo de expectativa** | Polarización: el debate "traidores contra aliados". **Cómo se mitiga:** se presentan las razones de cada pueblo con sus fuentes, sin juzgar. Los comentarios se moderan |
| **Riesgos de política** | Es un tema de guerra: tratamiento no gráfico, combates en siluetas o con mapas, sin cadáveres con heridas (fase 10). El sacrificio humano solo se menciona como contexto, sin escenas explícitas |
| **Datos que hay que verificar** | El número de españoles al salir de Cuba (alrededor de 500, según las fuentes). La cifra de aliados tlaxcaltecas: varía mucho según la fuente, así que se da un rango con su procedencia. La epidemia de viruela de 1520 |

**Descripción**

```
¿Cómo pudieron unos 500 españoles conquistar a los mexicas? La respuesta corta: no lo hicieron solos. Tlaxcaltecas y otros pueblos fueron decisivos, y una epidemia hizo el resto (verificar cifras).
Revisamos las cartas de Cortés, la crónica de Bernal Díaz y las fuentes indígenas.

En este video:
• Cuántos españoles llegaron y cuántos aliados tuvieron (con rangos y fuentes)
• Por qué Tlaxcala y otros pueblos se unieron contra los mexicas
• Qué papel tuvo la viruela en la caída de Tenochtitlan

Capítulos
00:00 La cifra que no cuadra
01:00 Lo que nos contaron
02:20 Tlaxcala
04:00 La viruela
05:40 Los pueblos sometidos por los mexicas
07:20 Lo que Cortés no contó en sus cartas
09:00 Veredicto

Fuentes
1. Hernán Cortés, Cartas de relación (segunda y tercera).
2. Bernal Díaz del Castillo, Historia verdadera de la conquista de la Nueva España.
3. Miguel León-Portilla, Visión de los vencidos (1959).
4. Matthew Restall, Los siete mitos de la conquista española (2004).

Cómo hacemos los videos: guion investigado y escrito por el canal; ilustración y animación propias.

▶ Lista: ¿Por qué…? Historia de Latinoamérica
▶ Siguiente expediente: ¿Por qué la capital de México está sobre un lago?

#historiademéxico #conquista #tenochtitlan
```

### Video 6: ¿Por qué la Ciudad de México está sobre un lago? (P2)

| Campo | Contenido |
|---|---|
| **Término de búsqueda principal** | "historia de mexico": 58.900 al mes, competencia 60, +141 % (estimación). La pregunta exacta no está medida |
| **Términos secundarios** | "tenochtitlan" (21.500 al mes, estimación), "chinampas" (8.500 al mes, competencia 40, estimación), "aztlan" (4.400 al mes, competencia 35, estimación), "lago de texcoco", "como vivian los aztecas" (4.500 al mes, competencia 40, estimación) |
| **Qué busca quien escribe esto** | Curiosidad sobre la ciudad. Le interesa a quien vive allí y a quien la visita |
| **Audiencia (hipótesis)** | Residentes de la Ciudad de México y del centro del país, y público de historia antigua |
| **Título principal** | ¿Por qué la Ciudad de México está sobre un lago? — 48 caracteres |
| **Alternativas** | 1. La ciudad que secó su lago (y ahora se hunde) (45) · 2. ¿Por qué los mexicas fundaron su ciudad en el agua? (51) · 3. ¿Dónde quedó el lago de la Ciudad de México? (44) · 4. Tenochtitlan: una capital en medio de un lago (45) · 5. La inundación que duró cinco años (33, verificar la duración) |
| **Miniatura A** | La de la fase 6, adaptada. Vista aérea de Tenochtitlan rodeada de agua y, encima, la silueta actual de la ciudad, que se seca. Texto "AQUÍ HABÍA AGUA". Sello "HISTORIA" |
| **Miniatura B** | Pantalla dividida: canoa en un canal en el año 1500 frente a una calle agrietada en la actualidad. Texto "SE HUNDE" |
| **Miniatura C** | Un águila sobre un nopal en un islote, en estilo códice, con el lago enorme alrededor. Texto "¿POR QUÉ AQUÍ?" |
| **Capítulos (provisionales)** | 00:00 Una capital construida en el agua · 00:50 La señal del águila (leyenda frente a historia) · 02:30 Por qué un lago era buena idea · 04:10 Chinampas y calzadas · 05:40 Los españoles y el agua · 07:10 Secar el lago · 08:40 Por qué la ciudad se hunde · 09:40 Veredicto |
| **Hashtags** | #historiademéxico #tenochtitlan #CDMX |
| **Ideas relacionadas** | Así vivías si nacías en Tenochtitlan (I03, reutiliza los escenarios) · Aztlán: ¿existió? (P1) · La inundación de 1629 (Short) |
| **Hipótesis de clic** | Une historia antigua y un problema actual que el espectador ve en su ciudad: hundimientos e inundaciones |
| **Riesgo de expectativa** | Bajo. El hundimiento actual se explica con datos oficiales y sin alarmismo |
| **Riesgos de política** | Se evita la política reciente (gestión del agua). Se habla del fenómeno, no de culpables actuales |
| **Datos que hay que verificar** | La fecha tradicional de fundación (1325) y su carácter de tradición. La obra del desagüe de Huehuetoca (siglo XVII). La inundación de 1629 y su duración. Datos oficiales de hundimiento actual (fuente institucional) |

**Descripción**

```
¿Por qué la Ciudad de México está sobre un lago? Los mexicas fundaron Tenochtitlan en un islote del lago de Texcoco, y desde entonces la ciudad no ha dejado de pelear con el agua (verificar).
Explicamos por qué fue una buena idea, cómo se secó el lago y por qué hoy la ciudad se hunde.

En este video:
• Qué parte de la fundación es leyenda y qué parte es historia
• Cómo funcionaban las chinampas y las calzadas
• Qué pasó cuando se decidió secar el lago

Capítulos
00:00 Una capital construida en el agua
00:50 La señal del águila (leyenda frente a historia)
02:30 Por qué un lago era buena idea
04:10 Chinampas y calzadas
05:40 Los españoles y el agua
07:10 Secar el lago
08:40 Por qué la ciudad se hunde
09:40 Veredicto

Fuentes
1. Códice Mendoza (lámina de la fundación de Tenochtitlan).
2. Hernán Cortés, Segunda carta de relación (1520), descripción de la ciudad.
3. [Estudio académico sobre el desagüe del valle de México: completar]
4. [Fuente institucional actual sobre el hundimiento: completar]

Cómo hacemos los videos: guion investigado y escrito por el canal; ilustración y animación propias.

▶ Lista: ¿Por qué…? Historia de Latinoamérica
▶ Siguiente expediente: Así vivías si nacías en Tenochtitlan

#historiademéxico #tenochtitlan #CDMX
```

---

## 4. Shorts derivados de cada video largo

Cada video largo da para 2 o 3 Shorts de 45 a 75 segundos. La regla de la fase 4 es una paradoja completa en la primera frase.

| Largo | Short 1 | Short 2 | Short 3 |
|---|---|---|---|
| La Llorona | "Los mexicas oyeron a La Llorona antes de que llegaran los españoles (según Sahagún)" | "¿Cómo se llama La Llorona en tu país?" (mapa de versiones) | — |
| Colombia | "Colombia lleva el nombre de alguien que nunca vino" (solo si se verifica) | "Colombia se llamó Estados Unidos de Colombia" | "El nombre 'Colombia' era para todo el continente" |
| El Dorado | "El Dorado no era una ciudad. Era un hombre" | "Intentaron vaciar una laguna para sacar el oro" | — |
| Chupacabras | "El chupacabras tiene fecha de nacimiento" | "El nombre se lo puso un humorista" (verificar) | — |
| Conquista | "Cortés no conquistó México solo" | "El arma más letal de la conquista no era una espada" (la viruela, con tratamiento no gráfico) | — |
| Lago | "Ciudad de México está construida sobre un lago" | "Una inundación que duró años" (verificar) | "La ciudad se hunde cada año" (con fuente oficial) |

**Empaquetado de los Shorts:**

- **Título:** la frase-paradoja, de menos de 50 caracteres, con 1 o 2 hashtags.
- **Sin miniatura de diseño:** la mayoría de las vistas llega desde el feed. En la cuadrícula del canal se usa el primer fotograma con el sello de la serie.
- **Enlace al video largo:** con la función de video relacionado de Shorts. No la verifiqué en esta consulta: hay que comprobarla en Studio al subir el Short.

**Recordatorio de la fase 10:** las vistas de los Shorts **no cuentan** para las horas de YPP. Su papel es atraer espectadores hacia los videos largos.

---

## 5. Cómo se evalúa el empaquetado

Las métricas son privadas y aparecen en YouTube Studio cuando el canal existe.

| Señal | Qué indica | Con qué se compara | Advertencia |
|---|---|---|---|
| CTR de impresiones en las primeras 24 h y a los 7 días | Si el título y la miniatura atraen clics | La mediana de CTR del propio canal, una vez haya 5 videos | El CTR baja cuando YouTube muestra el video a públicos más amplios. Un CTR bajo con muchas impresiones puede ser mejor que uno alto con pocas |
| Retención en los primeros 30 segundos | Si el video cumple lo que prometió el empaquetado | El promedio del canal | Si el CTR es alto y la retención inicial baja, el empaquetado prometió algo que el video no da |
| AVD y porcentaje visto | Satisfacción y horas para YPP | La mediana del canal por formato | Compara siempre videos del mismo formato |
| Fuentes de tráfico | Si el video vive de búsqueda o de recomendaciones | — | En el lanzamiento se espera más búsqueda (hipótesis) |
| Rendimiento relativo (múltiplo) | Si el video supera a sus vecinos | Vistas a 28 días ÷ mediana de los 5 videos anteriores | Es el mismo método de la fase 1, aplicado al canal propio (fase 12) |

---

## 6. Método de pruebas A/B de título y miniatura

**Función oficial:** "Prueba y compara" ([16391400](https://support.google.com/youtube/answer/16391400)). Permite hasta 3 variantes, solo en ordenador y con funciones avanzadas. Gana la variante con más **tiempo de visualización**, no la de más clics. La prueba dura hasta 2 semanas. No funciona en Shorts ni en videos marcados como "para niños".

**Protocolo:**

1. **Una variable a la vez.** En el mes 1 se prueba solo la miniatura con el mismo título. En el mes 2, el título con la misma miniatura. Si cambian las dos cosas, no se sabe qué funcionó.
2. **Hipótesis escrita antes de la prueba**, en la hoja "Experimentos" del dashboard. Ejemplo: "La miniatura con una pregunta (¿EXISTIÓ?) superará a la de una afirmación (ANTES DE 1519) en tiempo de visualización".
3. **Variantes de verdad distintas:** otro concepto, no otro color. Usa los conceptos A, B y C de cada paquete.
4. **Se activa al publicar** y se deja correr hasta que YouTube dé un resultado (Winner, Performed Same o Inconclusive). No se toca durante la prueba.
5. **Cómo se registra el resultado:**
   - Winner: la regla ganadora se anota en la hoja "Aprendizajes" con la etiqueta "evidencia: 1 prueba".
   - Performed Same: se elige la variante más fiel a la marca.
   - Inconclusive: el resultado no cuenta como aprendizaje.
6. **Una regla se convierte en norma** del canal solo cuando gana en **3 pruebas** de temas distintos. Antes de eso es una hipótesis.
7. **Si el video no despega a los 7 días** (múltiplo menor que 0,5 frente a los 5 anteriores):
   - Se puede reempaquetar una vez, con una variante que no se haya probado.
   - Se anota como experimento.
   - No se reempaqueta más de una vez: si no funciona, el problema suele ser el tema (fase 4).

**Primeras hipótesis a probar** (todas salen de la fase 4):

1. Miniatura con pregunta frente a miniatura con afirmación (Llorona: A frente a B).
2. Personaje con emoción frente a objeto de evidencia (Llorona: A frente a C).
3. Título con "verdadera historia" frente a título con pregunta (¿Existió…?).
4. Número concreto en la miniatura frente a palabra (Conquista: "¿SOLO 500?" frente a "NO ESTABA SOLO").
