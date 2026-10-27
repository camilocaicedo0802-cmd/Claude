# Fase 2: análisis de los mejores videos

**Consulta:** 27 de octubre de 2026.
**Base:** 97 videos seleccionados (10 a 13 por canal) en `datos/videos_analizados.csv`.
**Profundidad:** 12 transcripciones completas (vidIQ), tres fotogramas automáticos de cada uno de los 97 videos y la estructura por capítulos de 148 videos que los declaran en su descripción.

Etiquetas: **[dato]** medido; **[estimación]** calculado con un supuesto; **[hipótesis]** interpretación a validar.

## Qué pude ver y qué no

- **Transcripciones:** solo de 12 videos, elegidos para cubrir los 8 canales y dos casos de contraste. Los otros 85 los analizo por título, miniatura, fotogramas, capítulos y descripción, sin afirmar nada sobre su guion.
- **Producción:** son 3 fotogramas fijos por video, los que YouTube publica automáticamente. No vi los videos en movimiento. No puedo hablar de ritmo de cortes, música, efectos ni calidad de la voz más allá de lo que delata el texto.
- **Por qué no vi los videos:** YouTube sigue bloqueando las descargas desde este contenedor. No intenté esquivar ese bloqueo.
- **CTR, retención y fuentes de tráfico:** son privadas. Cuando digo que algo "funcionó", me refiero a vistas y múltiplo sobre los videos vecinos del mismo canal, nada más.
- **Suscriptores al publicar:** interpolados a partir del historial de vidIQ (`datos/suscriptores_series.csv`). No hay datos para The Paint Explainer ni Simple Paint.

## Selección

Para cada canal tomé los 5 videos con más vistas y los 5 con mayor múltiplo sobre sus vecinos. Les sumé los 3 con más vistas al día entre los publicados en los últimos 60 días, los 3 que más rindieron cuando el canal tenía menos de 20.000 suscriptores y 2 de contraste: los de peor rendimiento relativo con datos exactos. Los Shorts de Te Lo Pinto Fácil quedaron fuera: el canal los abandonó con una mediana de 10.000 vistas.

---

## Resumen

1. **Hay tres niveles de producción, y no son los que sugieren las miniaturas** [dato, por fotogramas]:
   - **Nivel 1 ("Paint"):** monigotes y formas simples, fotos reales de personas y lugares, y un título de sección en mayúsculas arriba. Lo usan The Paint Explainer, Simple Paint y Te Lo Pinto Fácil en sus videos antiguos.
   - **Nivel 2:** fondos pintados con aspecto de imagen generada por IA, con personajes simples encima. Lo usan Estrictamente y Te Lo Pinto Fácil en sus videos recientes; The Crooked Explainer lo mezcla con fotos y fragmentos reales.
   - **Nivel 3:** ilustración o animación vectorial detallada, con personajes constantes. Lo usan Squire Explains y Lịch Sử Ngoại Truyện.
   - **Brecha entre miniatura e interior:** en los canales de nivel 1 y 2 la miniatura es una ilustración semirrealista muy trabajada y el interior es mucho más simple. En Squire, Lịch Sử y Some Guy Who Knows Stuff, miniatura e interior tienen el mismo estilo.
   - **Lo que coincide con los datos** [hipótesis]: los dos canales de 2026 con interior más cuidado y coherente son los que más crecieron en octubre:
     - Squire Explains: +11.700 suscriptores en su primer mes.
     - Lịch Sử Ngoại Truyện: +4.800, frente a +2.700 de The Crooked Explainer y +2.300 de Estrictamente, según vidIQ.
     - Correlación de cuatro canales, no causa.
2. **Nadie abre con saludo, presentación del canal ni petición de suscripción** [dato, 12 de 12]. Los ganadores abren de dos formas:
   - **Tú en la escena:** el espectador es el protagonista ("Imagine you're a knight…", "Estás en 1944…", "Estás de pie en la cima de una colina hace 15.000 años…"). Aparece en 5 de los 12.
   - **Entrada directa al primer caso** con un detalle concreto: nombre, fecha, lugar o cifra ("Jeff Bush. It was the night of February 28th, 2013…", "Pine Gap. … there's a cluster of white spheres… and they aren't buildings"). Aparece en 5 de los 12.
3. **Dato concreto en los primeros 15 segundos en 9 de los 12** [dato]: un nombre, una fecha, una cifra o un lugar. Dos de las tres excepciones también triunfaron:
   - Squire, con una escena hipotética muy vívida y sin fecha hasta 0:48.
   - Some Guy Who Knows Stuff ("So, let's start. Number 10, black holes."), donde el gancho es la cuenta atrás de 10 puntos que promete el título, no la frase.
   - El dato concreto es frecuente, pero no imprescindible.
4. **Las listas dominan, pero los mejores relatos se recuerdan más** [dato + hipótesis]:
   - 7 de los 12 son listas o catálogos (cuentas atrás, "cosas número uno…", escaleras de lo conocido a lo secreto), 4 son relatos y 1 es una antología de casos.
   - Los relatos (Squire, Lịch Sử, Estrictamente) usan técnicas que las listas no tienen: volver al final a la escena del principio, elementos sembrados que se pagan después y una frase final que cierra el círculo.
5. **Técnicas de retención que se repiten** [dato]:
   - Promesas explícitas de respuesta ("in a few minutes, you'll see what it does to you on this field"; en Lịch Sử, "por qué, lo sabrás en un momento"; en Estrictamente, "no empieza donde tú crees").
   - Elementos sembrados que se pagan después: el príncipe con una flecha en la cara reaparece como Enrique V en Agincourt; "recuerda este nombre".
   - Una regla que se repite y al final se invierte: "cada vez que la armadura crece, el escudo se encoge".
   - Puentes entre bloques: "Piensa en lo que eso significa…"; "y aquí es donde las cosas se ponen oscuras".
   - Una frase de remate al final de cada punto y analogías modernas: escudo de armas como "camiseta de equipo"; el combate entre armaduras como "un concurso de abrelatas".
6. **Un gran gancho no rescata un tema que el público del canal no quiere** [dato + hipótesis]:
   - Estrictamente: "¿Cómo Calmaban a los Bebés en la Prehistoria?" tiene uno de los ganchos mejor escritos de la muestra: un padre a las 2 de la madrugada y tres adelantos concretos. Sacó 902 vistas (×0,03). El tema cambia el público: le habla a padres, no al curioso de la historia del canal.
   - The Crooked Explainer: el contraste de la Navidad se publicó el 11 de agosto. La estación lo contamina, así que no permite separar el efecto del guion del de la fecha.
7. **La rigurosidad no es uniforme, y ahí hay un hueco en español** [dato]:
   - **Citan fuentes en la descripción o en el guion:** The Paint Explainer, Squire, Lịch Sử y Estrictamente. Estrictamente, sin embargo, escribe mal muchos nombres de autores ("Robin Dumb", "Colin Renf", "Klaus Schmidth").
   - **Errores en los dos canales en español:**
     - Te Lo Pinto Fácil afirma una especulación como probable ("lo más seguro es que estuvieran involucrados con el arresto Maduro").
     - Estrictamente remata con una cifra sin respaldo ("es de aproximadamente un 90 %").
     - Estrictamente deja símbolos de formato (`**`) sin limpiar en una descripción, señal de texto pegado sin revisar.
   - [Hipótesis]: "historia en español con rigor verificable" es una diferenciación real frente a los referentes hispanos.
8. **El título y la miniatura se reparten el trabajo** [dato, por casos]:
   - En los mejores ejemplos la miniatura **añade** algo que el título no dice:
     - Una respuesta provocadora: "Why Knights Stopped Using Shields" con "USELESS.".
     - El héroe: el título de Lịch Sử nombra el hecho y la miniatura pregunta "¿por qué Francia no pudo vencer a Nguyễn Tri Phương?".
     - Una afirmación más fuerte que el título: "Así se Drogaban los Soldados…" con "TODOS IBAN DROGADOS".
   - Some Guy Who Knows Stuff es la excepción constante: repite el título entero y aun así funciona.
9. **Las etiquetas no son el factor** [dato]. Squire Explains y The Paint Explainer no usan ninguna. Los capítulos son habituales en los videos de lista (The Paint Explainer, Simple Paint, Some Guy Who Knows Stuff), con segmentos medianos de 72 a 106 segundos por punto.
10. **Adaptar al español temas probados en inglés funciona a veces** [dato]. Ejemplos de Te Lo Pinto Fácil:
    - "Cómo Murió Cada Asesino en Serie": 2,7 M.
    - "Las Peores Muertes de Cada Planeta Explicadas" (versión de "What Dying on Every Planet Would Be Like", 13 M en inglés): 852 k.
    - "Cada Gran Error Humano Que Cambió la Historia Para Siempre" (traducción casi literal de un video de 7,9 M de The Paint Explainer): 129 k, ×0,9.

**Ritmo de locución** [estimación por conteo de palabras en segmentos de 15 a 17 segundos]: alrededor de 190 a 200 palabras por minuto en Squire y Estrictamente. Es un ritmo rápido, típico de una voz sintética o editada sin pausas.

---

## Análisis en profundidad de los 12 videos transcritos

Para cada video: ficha, título, miniatura, gancho (5, 15 y 30 segundos), guion, producción, publicación, y qué haría distinto un canal nuevo. Las citas son fragmentos breves.

### 1. Squire Explains: "Why Knights Stopped Using Shields"

**Ficha** [dato]
- Video: [CIYIefUvHq0](https://www.youtube.com/watch?v=CIYIefUvHq0), publicado el 16-oct-2026, 9:24 de duración.
- 1.015.391 vistas en 11 días: ×18,2 sobre sus vecinos.
- El canal tenía unos 3.730 suscriptores al publicarlo: 272 vistas por suscriptor.

**Título**
- **Palabra clave:** "knights shields". Intención: curiosidad, aunque también es una pregunta que la gente busca.
- **Promesa:** resolver una paradoja, porque un escudo protege y parece absurdo abandonarlo.
- **Mecanismo:** "Why" + una contradicción con el sentido común. Es corto (33 caracteres) y concreto.
- **Título alternativo a probar:** "Knights Threw Away Their Shields. Here's Why". Hace la paradoja explícita sin pregunta. Serviría para medir si la pregunta ayuda o resta.

**Miniatura** (vista)
- Caballero con la mascota del canal, encogiéndose de hombros.
- Escudo tachado con señal de prohibido y el texto "USELESS." en blanco con contorno negro.
- Fondo de campamento medieval desenfocado.
- La miniatura **responde provocativamente** a la pregunta del título.

**Gancho**
- **0-5 s:** segunda persona y peligro inminente: "Imagine you're a knight, and any second now, thousands of arrows are going to fall…".
- **5-15 s:** detalles sensoriales (sin caballo, barro, arqueros cerca). Luego se plantea lo que haría cualquiera: "raise his shield".
- **15-30 s:** el giro ("No shield. You left it behind. On purpose."), la pregunta central (0:28) y tres respuestas falsas ("Pride? Stupidity? Some kind of knightly dare?").
- **Promesa explícita:** volver a esa escena ("in a few minutes, you'll see what it does to you on this field").

**Guion**
- **Estructura:**
  - Empieza en la escena del clímax.
  - Retrocede y avanza cronológicamente con "ahora eres…": normando en 1066, caballero cien años después, ballestero genovés en Crécy, armadura de placas.
  - Vuelve a la escena (Agincourt, 5:53).
  - Remata con las armas de fuego y un giro al presente: escudos antidisturbios, el logo de Porsche, el primer escudo del Capitán América.
- **Técnicas:**
  - La regla que se repite ("every time the armour grows, the shield gets smaller") y que al final se invierte.
  - Un personaje sembrado (el príncipe herido) que reaparece como rey en Agincourt.
  - Un mito desmentido: "no necesitabas una grúa para subir al caballo".
  - Pruebas con nombre: un experto de la Wallace Collection y crónicas de la época.
- **Cierre en aforismo:** "The knights threw away their shields. And the shield outlived every one of them." No pide suscripción.

**Producción** (fotogramas)
- Animación vectorial limpia con personajes articulados y la mascota en cada época.
- Fondos detallados y planos cerrados de expresiones.

**Publicación**
- La descripción repite el gancho en segunda persona y resume el recorrido.
- Hashtags (#history, #knights, #medievalhistory), sin etiquetas.

**Para un canal nuevo:** es la estructura más **replicable con valor propio** de la muestra: "¿Por qué dejó de existir X?" contado en segunda persona a través de las épocas. Exige investigación y animación de calidad, justo donde un canal con perfil de motion design puede diferenciarse.

### 2. Squire Explains (Short): "She Went to War Disguised as Her Brother"

**Ficha** [dato]
- Video: [XuOxszx1TU0](https://www.youtube.com/watch?v=XuOxszx1TU0), publicado el 18-oct-2026, 1:05 de duración.
- 2.758.776 vistas en 9 días: ×5,9.
- El canal tenía unos 5.190 suscriptores al publicarlo.

**Título**
- Historia completa en siete palabras: protagonista, disfraz y motivo.
- No hay nombre propio. Nadie busca a "Milunka Savić", así que el título vende la situación.

**Miniatura** (vista)
- Mascota con uniforme de época y el texto "THEY CAN'T FIND OUT".
- La miniatura añade la tensión (el secreto) en lugar de repetir el título.

**Gancho**
- **0-3 s:** toda la paradoja en una frase: "This Serbian soldier could never get wounded, because the doctors would find out she was a girl."
- **3-15 s:** el motivo (su hermano enfermo de tuberculosis) y lo que se jugaba.
- **15-30 s:** empatía ("Imagine knowing one slip of your voice could end everything") y el giro (una granada; los médicos lo descubren).

**Guion**
- **Estructura:** premisa, contexto, empatía, giro, diálogo breve ("I'll wait.") y escalada de cifras (nueve heridas, 23 prisioneros sola).
- **Remate de una palabra:** "Twice." Los créditos y las fuentes van en la descripción.

**Producción:** vertical, con la misma mascota y subtítulos palabra a palabra en mayúsculas.

**Para un canal nuevo:** muestra la versión Short del mismo método, un dilema humano concreto en una sola frase, y se puede convertir después en video largo. Es **atípico** en cifras: los Shorts virales son volátiles. El método, en cambio, se puede replicar.

### 3. The Crooked Explainer: "Actual Dark Truth Behind Every Nursery Rhymes"

**Ficha** [dato]
- Video: [TfEYb9B4ovc](https://www.youtube.com/watch?v=TfEYb9B4ovc), publicado el 5-abr-2026, 13:21 de duración.
- 1.860.304 vistas: ×1.394 sobre sus vecinos.
- El canal tenía unos 7 suscriptores al publicarlo. Despegó unas tres semanas después.

**Título**
- **Palabras clave:** "nursery rhymes" + "dark truth / meaning". Hay búsqueda real detrás: la descripción repite "meaning behind nursery rhymes".
- **Promesa:** el contraste entre lo inocente y lo oscuro, sobre algo que todos conocen desde niños.
- Tiene un error gramatical ("Every Nursery Rhymes") y no le afectó.
- **Título alternativo a probar:** "The Dark True Stories Behind Nursery Rhymes You Sang as a Kid". Añade el "tú" y corrige la gramática.

**Miniatura** (vista)
- Tres personajes con sus canciones etiquetadas: Georgie Porgie con la cara ensangrentada, una niña asustada en "Ring around the Rosie" y un encapuchado con campana y vela en "Oranges & Lemons".

**Gancho**
- **0-15 s:** recita la canción, añade "You've known that since you were three" y suelta el dato brutal: el hombre de la canción fue apuñalado en 1628 y "the city celebrated in the streets".
- **A los 17 s** arranca "Number six", con una cuenta atrás que deja abierto el número uno.
- **Técnica:** el gancho es un adelanto del punto 4, puesto al principio.

**Guion**
- **Cada punto:** la canción cantada, el contexto con nombres y fechas (Nicholas Owen, Ravenscroft 1609, Halliwell 1842), la reinterpretación verso a verso y una frase de cierre ("The soldiers are long gone. The rooms are still there.").
- **Frases cortas y secas,** tal como promete el canal ("No editorialising").
- **El número uno desmiente** el mito más famoso (la peste en "Ring around the Rosie"). Así gana credibilidad y cierra con una reflexión sobre por qué se propagan las historias oscuras.

**Producción:** mezcla de monigotes al estilo de una tira cómica, retratos y documentos históricos, todo sobre textura de papel.

**Publicación:** descripción breve escrita para el buscador, 5 etiquetas, sin capítulos.

**Para un canal nuevo:** es un caso **atípico**: un solo video explica la cuarta parte del canal, y las partes 2 y 3 sacaron el 12 % y el 9 % de su audiencia. La **fórmula sí es replicable**: algo universalmente conocido + su verdad documentada + cuenta atrás + fuentes. Un ejemplo en español serían las canciones infantiles o los refranes hispanos y su origen real (a validar con datos de búsqueda en la fase 3).

### 4. The Crooked Explainer (contraste): "The Actual Dark Truth Behind Every Christmas Tradition"

**Ficha** [dato]
- Video: [PWsO1d05lnM](https://www.youtube.com/watch?v=PWsO1d05lnM), publicado el **11-ago-2026**, 12:58 de duración.
- 3.259 vistas: ×0,06.
- El canal tenía unos 11.700 suscriptores al publicarlo.

**Diferencias con el ganador** [dato]
- Abre con "Krampus", una figura que ya se conoce como oscura, así que no hay contraste entre inocente y oscuro.
- No hay un dato concreto con fecha en los primeros 15 segundos.
- La lista no está numerada.
- Usa más adjetivos ("genuinely terrifying", "monstrous") y menos nombres y fechas.
- Pide la suscripción a mitad del video (7:47).
- Presenta como hecho una conexión discutida entre Santa y Odín ("the bones are Odin's").

**Lectura** [hipótesis]
- Son dos causas posibles y no se pueden separar: un tema de Navidad publicado cuatro meses antes de tiempo y un guion más genérico.
- **Prueba verificable:** si en diciembre de 2026 sus vistas suben con fuerza, la causa principal era la estación. Lo dejo anotado para revisarlo.

### 5. Te Lo Pinto Fácil: "Así se Drogaban los Soldados en la 2ª Guerra Mundial"

**Ficha** [dato]
- Video: [rYhAHKZI_xQ](https://www.youtube.com/watch?v=rYhAHKZI_xQ), publicado el 12-oct-2026, 20:46 de duración.
- 2.025.426 vistas en 15 días: ×15,4.
- El canal tenía unos 569.000 suscriptores al publicarlo.

**Título**
- **Palabras clave:** "drogas segunda guerra mundial", "soldados drogados".
- **Promesa:** "así era". Combina un tema tabú (drogas) con un tema atemporal de enorme interés (la Segunda Guerra Mundial).
- **Título alternativo a probar:** "Las Drogas Secretas que Tomaban los Soldados en la Segunda Guerra Mundial". Más específico ("secretas", "tomaban") y con la palabra clave completa.

**Miniatura** (vista)
- Soldado de dibujo con ojos rojos fumando, sobre una playa de desembarco.
- Texto "TODOS IBAN DROGADOS" en negro y rojo.
- **Riesgo:** la miniatura afirma algo más fuerte que el video (no "todos" iban drogados), lo que puede crear una expectativa que el contenido no cumple.

**Gancho**
- **0-15 s:** segunda persona en 1944, con un objeto misterioso con nombre: "llegan toneladas de una droga llamada el cóctel nazi".
- **15-30 s:** el misterio (tu cuerpo debería haberse rendido) y una escalada: "aquí es donde las cosas empiezan a ponerse oscuras".

**Guion**
- **Estructura:** lista de unas 12 sustancias, sin orden cronológico.
  - Cada una abre con una microescena en segunda persona ("Te meten en un camión con 40 hombres…", "Es agosto de 1914, caes en el barro…").
  - Después vienen los datos.
  - Cada bloque se enlaza con el siguiente con un puente ("Y mientras… un químico estaba a punto de…").
- **Localización:** al hablar de la escopolamina dice "En Colombia hoy la conocen… burundanga". Es un guiño directo al público latinoamericano.
- **Precisión:**
  - Incluye el gas mostaza, que no es una droga, en una lista de drogas.
  - Cuando una afirmación es especulativa, lo dice ("no hay forma de saberlo").

**Producción:** etapa reciente del canal, con fondos pintados tipo IA, monigotes y fotos reales de archivo.

**Publicación:** enlaces a "vídeos similares" al principio de la descripción (enlazado interno), llamada a hacerse miembro y 12 etiquetas.

**Para un canal nuevo:** **replicable** en su estructura ("Así se [hacía X] en [época]" con microescenas en segunda persona), pero con verificación más estricta y miniaturas que no exageren el contenido.

### 6. Te Lo Pinto Fácil: "Todas las Fuerzas Especiales de EEUU Explicadas"

**Ficha** [dato]
- Video: [GerlkKMdGP8](https://www.youtube.com/watch?v=GerlkKMdGP8), publicado el 27-feb-2026, 19:28 de duración.
- 5.087.342 vistas: ×9,0.
- El canal tenía unos 314.000 suscriptores al publicarlo.

**Título:** el catálogo "Todas las X Explicadas", con una palabra clave muy buscada y atemporal. Es el mayor éxito absoluto del canal.

**Miniatura** (vista): tres soldados de dibujo etiquetados ("DELTA FORCE / GREEN BERETS / NIGHT STALKERS"), el del centro con cara de calavera y cuchillo ensangrentado.

**Gancho**
- **0-15 s:** el nombre del primer punto ("Navy Seals.") y luego segunda persona: "Son las 3 de la madrugada y estás temblando dentro del océano".
- **15-30 s:** la prueba concreta del "surf torture".

**Guion**
- **Escalera de lo más conocido a lo más secreto:** SEALs, Rangers, Boinas Verdes, Raiders, Special Tactics, Delta, ISA, Night Stalkers, operaciones psicológicas y CIA.
- **Frases de escalada:** "lo verdaderamente extremo empieza ahora"; "a partir de aquí las cosas se ponen serias de verdad".
- **Cada unidad:** escena en segunda persona, datos (año, tamaño, entrenamiento), operaciones famosas y una "verdad incómoda".
- **Cierre:** "No olvidéis apoyar este tipo de contenido suscribiéndoos…" y un video siguiente.

**Precisión:** contiene especulación presentada como probable (el arresto de Maduro) y afirmaciones difíciles de verificar ("Google Earth la tiene borrosa").

**Para un canal nuevo:** **replicable** en formato, pero es un **éxito de canal grande** (16 vistas por suscriptor). No dice cuánto rendiría en un canal pequeño.

### 7. Estrictamente: "¿Cómo Inventaron los Seres Humanos los Países?"

**Ficha** [dato]
- Video: [D0_gBZHx7R4](https://www.youtube.com/watch?v=D0_gBZHx7R4), publicado el 3-ago-2026, 32:23 de duración.
- 273.683 vistas: ×539.
- El canal tenía unos 2.660 suscriptores al publicarlo. Coincide con el despegue del canal.

**Título**
- "¿Cómo inventaron los humanos X?" pertenece a la familia de los orígenes y aplica a algo que todos dan por hecho.
- **Palabra clave:** "origen de los países".
- **Título alternativo a probar:** "Antes No Existían los Países. Así se Inventaron". Afirmación más contraste, sin pregunta.

**Miniatura** (vista): personajes prehistóricos discutiendo junto a una línea de piedras (una frontera) y el texto "¿PRIMER PAÍS?" en amarillo y blanco.

**Gancho**
- **0-15 s:** "Estás de pie en la cima de una colina hace 15.000 años… No hay ninguna valla, ningún muro…".
- **15-30 s:** el contraste con hoy (pasaportes, fronteras).
- **0:48:** llega la pregunta, con un aviso: "La respuesta no es sencilla. Y no empieza donde tú crees".

**Guion**
- **Argumento cronológico por capas:**
  - El número de Dunbar.
  - Los natufienses.
  - Las tumbas como marcas de territorio.
  - Göbekli Tepe.
  - El grano y los impuestos.
  - Jericó, Uruk y la escritura para llevar cuentas.
  - La primera frontera documentada.
  - Westfalia, Anderson y Gellner.
  - Sykes-Picot, Berlín y Sudán del Sur.
- **Recursos:** puentes repetidos ("Piensa en lo que eso significa…"), un resumen final y un cierre filosófico en segunda persona ("Y cada mañana… te despiertas y te la crees").
- **Problemas** [dato]:
  - Nombres de autores mal escritos o mal pronunciados.
  - Una probabilidad inventada ("aproximadamente un 90 %").
  - [Hipótesis]: parece un guion traducido y leído por una voz sintética sin revisión.

**Producción:** fondos pintados tipo IA, personajes simples recurrentes y subtítulos animados palabra a palabra.

**Publicación:** descripción larga escrita para el buscador, hashtags y 27 etiquetas.

**Para un canal nuevo:** el **tema** ("el origen de lo cotidiano") es muy replicable en español y atemporal. La **ejecución** muestra qué no hacer: 32 minutos con errores de nombres no son un estándar a copiar.

### 8. Estrictamente (contraste): "¿Cómo Calmaban a los Bebés en la Prehistoria? 8 Métodos Sorprendentes"

**Ficha** [dato]
- Video: [Bs_DgBUJz_M](https://www.youtube.com/watch?v=Bs_DgBUJz_M), publicado el 5-sep-2026, 31:06 de duración.
- 902 vistas: ×0,03.
- El canal tenía unos 8.570 suscriptores al publicarlo.

**Gancho**
- Uno de los mejor construidos de la muestra.
- **Escena moderna en segunda persona:** "Son las 2 de la madrugada. El bebé lleva 40 minutos llorando a gritos".
- **Tres adelantos concretos:**
  - Una práctica que "sigue siendo legal".
  - Una que "los hospitales aprobaron brevemente en los 70".
  - Una que "hoy haría que te enviaran a los servicios sociales".

**Por qué no funcionó** [hipótesis]
- El tema y el "tú" del gancho apuntan a padres, no al público que el canal había construido (curiosos de la historia).
- Toca temas delicados (opiáceos a bebés, infanticidio) que pueden limitar la publicidad y la distribución.
- **Lección:** el gancho trabaja sobre las personas a las que YouTube ya le muestra el video. No cambia a quién se lo muestra.

### 9. Some Guy Who Knows Stuff: "10 Horrifying Things Scientists Found In Space"

**Ficha** [dato]
- Video: [vikiJyJtZCs](https://www.youtube.com/watch?v=vikiJyJtZCs), publicado el 18-sep-2025, 15:53 de duración.
- 1.035.262 vistas: ×98,6.
- El canal tenía unos 2.910 suscriptores al publicarlo. Es su primer gran despegue.

**Título**
- Número + emoción ("Horrifying") + autoridad ("Scientists Found") + un tema amplio ("In Space").
- **Título alternativo a probar:** "Scientists Found These 10 Things in Space and Wish They Hadn't". Más narrativo.

**Miniatura** (vista): el título completo en una franja blanca curva y debajo un collage dibujado con un agujero negro, una estrella de neutrones y explosiones.

**Gancho**
- **No hay gancho:** "So, let's start. Number 10, black holes." (0-5 s).
- Abre con el elemento más conocido (los agujeros negros), una puerta de entrada fácil.

**Guion**
- **Cuenta atrás de 10 a 1,** unos 90 segundos por punto.
- **Tono:** humorístico y coloquial ("cosmic ninjas", "not the kind of pasta you want to be").
- **Cierre:** un remate de terror en cada punto y la petición de suscripción al final.
- **Precisión:** especulación presentada sin matiz (el vacío de Boötes vaciado por civilizaciones avanzadas).

**Producción:** dibujo digital propio con personajes simples, coherente con la miniatura.

**Publicación:** capítulos con subtítulos ingeniosos ("Gamma-Ray Bursts — The Universe's Sniper Shots") y 16 etiquetas.

**Para un canal nuevo:** muestra que en una lista larga la promesa la carga el título ("10 cosas"), no la primera frase. Es un éxito **atípico** por su múltiplo (×98,6) y por llegar pronto en la vida del canal.

### 10. The Paint Explainer: "The Most Guarded Places on Earth You Can't Visit"

**Ficha** [dato]
- Video: [yMwWSX_cvrc](https://www.youtube.com/watch?v=yMwWSX_cvrc), publicado el 8-sep-2026, 14:36 de duración.
- 2.376.890 vistas: ×6,6. Su parte 2 lleva 712 k en 27 días.

**Título:** superlativo + "on Earth" + "You Can't Visit". Lo prohibido apela directamente al espectador.

**Miniatura** (vista): cuadrícula de 12 fotos reales etiquetadas (Pine Gap, Area 51, la tumba de Qin Shi Huang, Room 39, Svalbard, Fort Knox, los Archivos Vaticanos…).

**Gancho**
- **0-5 s:** el nombre del primer lugar ("Pine Gap.").
- **5-15 s:** una imagen concreta con misterio: "a cluster of white spheres… and they aren't buildings".

**Guion**
- **Nueve lugares,** cada uno con el mismo esquema: qué se ve, qué es, qué te pasa si intentas entrar y un detalle sorprendente.
  - Los vuelos sin nombre de "Janet".
  - Los ríos de mercurio que confirma el análisis del suelo.
  - La pintura de los guerreros de terracota que se desprende al aire.
  - Los muelles bajo Cheyenne Mountain.
  - Las cajas de semillas que se pasan por rayos X.
  - Los lingotes de 12 kg.
- **Datos:** muy concretos y aparentemente verificados. La descripción enlaza 14 fuentes.

**Producción:** monigotes de Paint sobre fotos reales, con un rótulo de sección en cada lugar.

**Para un canal nuevo:** **replicable** con lugares, archivos o búnkeres de España y Latinoamérica, siempre con fuentes.

### 11. Simple Paint: "The Most Horrifying Ways People Got Trapped"

**Ficha** [dato]
- Video: [BmCDQHzWb9w](https://www.youtube.com/watch?v=BmCDQHzWb9w), publicado el 1-oct-2026, 15:47 de duración.
- 2.980.029 vistas en 26 días: ×7,7.

**Título:** superlativo + emoción ("Horrifying") + una situación universal que da miedo (quedar atrapado).

**Miniatura** (vista)
- Comparación temporal "2009 → 2019": el mismo hombre atrapado entre dos paredes, vivo y luego descompuesto, con una flecha roja.
- Es muy morbosa.

**Gancho**
- **Sin introducción:** "Jeff Bush. It was the night of February 28th, 2013 in Seffner, Florida…".
- Sigue con un detalle cotidiano y un presagio ("on what he thought was solid ground"). En menos de un minuto llega el horror: atrapado vivo e inalcanzable.

**Guion**
- **Seis casos reales narrados con suspense.**
- **Respiro a mitad:** un caso de supervivencia (el submarino Pisces III).
- **Remates finales:**
  - El socavón que se reabre sobre la tumba.
  - "12 minutes of air left".
  - El calendario tachado hasta el 23 de diciembre.

**Riesgos** [hipótesis]
- Las muertes reales narradas en detalle y la miniatura con un cadáver descompuesto pueden limitar la publicidad.
- Usa fotos reales de víctimas.

**Para un canal nuevo:** la técnica de narración de casos es replicable. El tono mórbido y las fotos de víctimas reales no son recomendables para un canal que necesita monetizar pronto. Se revisa en la fase de políticas.

### 12. Lịch Sử Ngoại Truyện: "Vì Sao Pháp Đánh Đà Nẵng 2 Năm Không Xong Phải Bỏ Vào Gia Định?"

En español: "¿Por qué Francia atacó Đà Nẵng durante dos años sin éxito y tuvo que irse a Gia Định?".

**Ficha** [dato]
- Video: [481WMMxY8UY](https://www.youtube.com/watch?v=481WMMxY8UY), publicado el 8-sep-2026, 10:47 de duración.
- 175.610 vistas: ×12,5.
- El canal tenía unos 1.900 suscriptores al publicarlo: 92 vistas por suscriptor.

**Título:** "¿Por qué…?" + una paradoja militar (la potencia que gana pero no avanza). Es historia nacional con orgullo de por medio.

**Miniatura** (vista)
- Plantilla de banderas (Francia y la bandera imperial).
- La pregunta "¿POR QUÉ FRANCIA NO PUDO VENCER A NGUYỄN TRI PHƯƠNG?".
- El mandarín ilustrado señalando la costa.
- **Reparto con el título:** el título cuenta el hecho y la miniatura pone al héroe.

**Gancho**
- **0-15 s:** fecha exacta (1-9-1858), cifras (14 barcos, media hora, 450 cañones capturados).
- **15-30 s:** la paradoja. Solo 100 km hasta Huế, 19 meses y ni un kilómetro de avance, y lo único que dejaron fue "un cementerio de los suyos".
- **0:32-0:47:** el héroe conocido ("su nombre está en las calles de todas las ciudades") y una doble pregunta.

**Guion**
- **Estructura:** contexto, biografía, la estrategia "convertir la defensa en ataque", "tres razones" numeradas, tres intentos franceses y un cierre con la imagen de dos cementerios.
- **Técnicas:**
  - Bucles explícitos: "recuerda este nombre"; "por qué, lo sabrás en un momento".
  - Cartas originales del almirante francés citadas.
  - Avance del siguiente episodio y pantalla final.

**Producción:** ilustración vectorial detallada y constante, con rótulos de fecha.

**Para un canal nuevo:** **muy replicable** para la historia de Colombia y Latinoamérica. La paradoja militar o política, el héroe con nombre de calle, las fuentes primarias y la serie con episodios enlazados encajan con un canal en español con rigor.

---

## Videos no transcritos: hallazgos por canal

Basados en título, miniatura, fotogramas, capítulos y descripción.

| Canal | Patrón de los ganadores | Patrón de los perdedores | Señal más útil |
|---|---|---|---|
| The Paint Explainer | Muerte, castigo, lugares prohibidos y "todo X explicado"; duelos con caras grotescas o cuadrículas de imágenes reales | Cuadrículas de iconos planos sobre conceptos útiles (falacias, mitos de salud); dos videos con título repetido rinden muy distinto (2,38 M frente a 197 k) | La cuadrícula funciona cuando cada celda despierta curiosidad por sí misma |
| Simple Paint | "Las peores muertes en [ámbito]" con duelo de caras dañadas | Política (golpes militares de EE. UU.), cuadrícula de órganos, antihéroes | El ámbito concreto (cuevas, Everest, gamers) multiplica los temas sin cambiar la fórmula |
| Te Lo Pinto Fácil | Segunda Guerra Mundial y militar con un personaje y 2-3 palabras enormes; catálogos de alta búsqueda | Repetir el tema de un éxito ("Todas las PELÍCULAS PROHIBIDAS…", 39 k); cuadrículas de iconos; caricaturas de líderes actuales | Repetir un tema no garantiza el resultado |
| Some Guy Who Knows Stuff | Misterios y espacio; plantilla de título completo | La misma plantilla con temas más "suaves" (minerales, el cuerpo humano) | Recopilaciones largas y calmadas; el tema decide |
| The Crooked Explainer | Contraste inocente y oscuro; personas extraordinarias reales | Navidad fuera de temporada; temas sin contraste | Empezó a ganar seguidores con un pilar nuevo (personas extraordinarias) cuando el anterior se agotó |
| Estrictamente | Orígenes ("¿cómo inventaron…?") y vida cotidiana en Roma y en la Edad Media | Temas dirigidos a padres; Egipto de noche | Su mayor éxito con canal pequeño trata un tema racial sensible (16,6 k con 8 suscriptores): riesgo a vigilar |
| Lịch Sử Ngoại Truyện | "¿Por qué…?" con paradoja y héroe; plantilla constante | Temas con poca paradoja. Las dos miniaturas de estilo fotográfico realista dan resultados opuestos (×0,39 y ×2,2) | La coherencia visual y la serie numerada |
| Squire Explains | Personas insólitas en la guerra, en Shorts; "¿por qué dejó de…?" en largo | En largo: "The ENTIRE History of the Samurai" (×0,53) y "Were War Elephants Actually Useful?" (×0,08) | Un tema amplio de "historia completa" rindió poco; la pregunta concreta, mucho |

## Replicable frente a atípico

**Replicables** (la estructura se puede adaptar con contenido propio, sin copiar):

1. "¿Por qué dejó de existir X?" contado en segunda persona a través de las épocas (Squire).
2. Paradoja de historia nacional con héroe conocido y fuentes primarias, en serie (Lịch Sử).
3. Catálogo de lugares o archivos inaccesibles, con "qué te pasa si intentas entrar" (The Paint Explainer).
4. "Así se [hacía X] en [época]", con microescenas en segunda persona (Te Lo Pinto Fácil, con verificación estricta).
5. Origen de lo cotidiano ("¿cómo se inventó…?"), en una versión más corta y rigurosa (Estrictamente).
6. Algo universalmente conocido y su verdad documentada, en cuenta atrás (The Crooked Explainer).

**Atípicos** (difíciles de reproducir; no conviene planificar contando con ellos):

- "Nursery Rhymes" (×1.394, publicado con 7 suscriptores): sus continuaciones sacaron el 12 % y el 9 %.
- "10 Horrifying Things Scientists Found In Space" (×98,6): guion genérico, despegue temprano del canal.
- "Todas las Fuerzas Especiales de EEUU" (5,1 M): éxito de un canal de 314 k suscriptores.
- Los Shorts de varios millones de Squire: la viralidad en Shorts es volátil.

## Qué queda pendiente

- **Ver los videos en movimiento:** ritmo de cortes, música, voz. Cuando el bloqueo se levante, con 2 o 3 videos por canal. O, si prefieres, con capturas tuyas de los primeros 30 segundos.
- **Comprobar en diciembre de 2026** si "The Actual Dark Truth Behind Every Christmas Tradition" despega. Si lo hace, confirma la estacionalidad.
- **Fase 3:** convertir las seis estructuras replicables en temas candidatos en español y medir su demanda y competencia con vidIQ. Quedan 35 créditos (7 consultas) hasta el 27 de noviembre.
