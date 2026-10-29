# E001: textos para generar la narración en ElevenLabs

**Video:** "Le hicieron un funeral de Estado a una pierna" (canal Desarmando Relatos).

**Total:** 12.272 caracteres en 9 partes, todas de menos de 2.500 caracteres para que entren en cualquier plan.

Para ver cuántos caracteres te quedan, revisa tu plan en ElevenLabs.

**Los nombres extranjeros están escritos como se pronuncian**, para que la voz no se trabe. Por ejemplo, "Jalapa" en lugar de "Xalapa" o "Ilinói" en lugar de "Illinois". En los subtítulos se usa la ortografía correcta, que está en `guiones/E001-pierna-santa-anna-narracion.txt`.

## Configuración recomendada

| Ajuste | Valor | Por qué |
|---|---|---|
| Modelo | **Eleven Multilingual v2** | Es el más estable y natural en narraciones largas en español. Eleven v3 es más expresivo, pero cambia más de una parte a otra |
| Voz | Masculina, adulta joven, **acento latinoamericano neutro**, estilo narrativo o conversacional | En la Voice Library, filtra por idioma español y acento latinoamericano, y escucha la muestra leyendo un párrafo. Buscamos un "amigo que cuenta historias", no un locutor de radio ni de terror. **Usa la misma voz en las 9 partes** |
| Stability | 40 a 50 % | Más baja suena más viva, pero puede variar entre partes |
| Similarity | 75 % | |
| Style exaggeration | 15 a 25 % | Le da intención sin sonar actuado |
| Speaker boost | Activado | |
| Velocidad | 1.0 (subir a 1.05 si suena lenta) | El guion está calculado a unas 130 a 150 palabras por minuto |
| Formato de descarga | MP3, 44,1 kHz, 128 kbps o más (o WAV) | |

## Cómo hacerlo

1. **Empieza por la parte 01 (el piloto).** Escúchala completa. Si la voz o el ritmo no te convencen, cambia la voz antes de generar las demás.
2. **Genera cada parte por separado.** Si una frase sale rara, regenera solo esa parte: ElevenLabs a veces lee distinto en cada intento.
3. **Nombra los archivos** `E001_01.mp3`, `E001_02.mp3`… hasta `E001_09.mp3`.
4. **Súbelos a la rama** en GitHub (Add file → Upload files) dentro de `canal-youtube-ia/video/E001/audio/`. Yo detecto los tiempos de cada frase con el audio y sincronizo las imágenes y los textos.

**Puntos suspensivos (...):** son pausas dramáticas y ElevenLabs las respeta. No los borres.

## Parte 01 · Bloques 1, 2 y 3: gancho, credibilidad y promesa (PILOTO)

1.140 caracteres · archivo: `E001_01.mp3`

```
México, mil ochocientos cuarenta y dos. Hay desfile, hay cañonazos, hay discursos... para enterrar una pierna.
No es una metáfora. Es la pierna de Antonio López de Santa Anna.
Soldados formados. Versos escritos para la ocasión. Un monumento esperándola.
Y ese funeral ni siquiera es lo más raro. Otra pierna suya sigue hoy en una vitrina. En Estados Unidos.
Quédate, porque al final vas a saber cuál de las dos tuvo el destino más absurdo.

Seguro el nombre de Santa Anna te suena. Es uno de los personajes más discutidos de la historia de México.
Pero esta parte casi nadie la cuenta completa.
Y no es un chisme de internet. Está en periódicos de la época, en biografías serias y en la ficha de un museo.
Lo que no está del todo claro, también te lo voy a decir.

Al terminar este video vas a saber cómo una pierna terminó enterrada con honores de héroe.
Vas a entender por qué, dos años después, la misma ciudad la sacó de su tumba.
Y vas a tener una historia que casi nadie conoce completa.
Al final, el veredicto: ¿verdad, a medias o mito? Y después, una continuación todavía más extraña.
Pero primero, conozcamos al dueño de la pierna.
```

## Parte 02 · Punto 1: El hombre que siempre volvía

940 caracteres · archivo: `E001_02.mp3`

```
Antonio López de Santa Anna nació en Jalapa, Veracruz, en mil setecientos noventa y cuatro.
Fue soldado desde muy joven. Primero peleó del lado de España... y después se pasó al bando de la independencia.
Ese cambio de bando no fue el último. Con los años, se volvió casi una costumbre.
Durante décadas, Santa Anna entró y salió del poder como quien entra y sale de su casa.
Según cómo se cuente, llegó a gobernar México once veces.
Once. En un país que apenas estaba aprendiendo a existir.
A veces era el héroe que iba a salvar a la nación. A veces era el villano al que había que sacar.
Y a veces, simplemente, se retiraba a descansar a su hacienda en Veracruz, un lugar llamado Manga de Clavo.
Ahí estaba a finales de mil ochocientos treinta y ocho. Retirado. Lejos de la capital. Sin cargo.
Hasta que frente a las costas de Veracruz aparecieron barcos de guerra franceses.
¿Y sabes qué venían a cobrar, entre otras cosas? Unos pasteles.
```

## Parte 03 · Punto 2: Una guerra por unos pasteles

1.925 caracteres · archivo: `E001_03.mp3`

```
Evidencia uno de cuatro: la guerra.
Para entender cómo Santa Anna perdió la pierna, primero hay que entrar a una pastelería.
Años antes, en Tacubaya, muy cerca de la capital, unos oficiales mexicanos destrozaron el local de un pastelero francés.
Según su reclamo, se comieron los pasteles y se fueron sin pagar.
El pastelero, de apellido Remontel, exigió una indemnización. Y no era el único francés que reclamaba daños en México.
Francia juntó todos esos reclamos en una sola cuenta: seiscientos mil pesos.
México no pagó. Y Francia mandó su flota.
Bloquearon el puerto de Veracruz durante meses. Bombardearon la fortaleza de San Juan de Ulúa. Y la fortaleza se rindió.
Por eso a ese conflicto se le conoce, con bastante ironía, como la Guerra de los Pasteles.
Ahora sí, imagina la escena.
Es el cinco de diciembre de mil ochocientos treinta y ocho. Estás en Veracruz. Es de madrugada y tropas francesas desembarcan en la ciudad.
Santa Anna, el retirado, se ha vuelto a poner el uniforme. Recorre las calles organizando la defensa.
Los franceses se repliegan hacia sus barcos. Santa Anna los persigue hasta el muelle.
Y en ese momento, un cañón francés dispara hacia la calle.
La metralla lo alcanza. Queda gravemente herido en la pierna izquierda, y los médicos tienen que amputársela.
Santa Anna cree que va a morir. En el parte de guerra que dicta esos días, se despide de la nación como un héroe a punto de entregar la vida.
Pero no muere.
Y esa herida le devuelve algo que había perdido: el aprecio del público.
El hombre que había caído en desgracia ahora era el héroe que dio una pierna por la patria.
La guerra termina meses después, en mil ochocientos treinta y nueve. Y México acaba aceptando pagar los seiscientos mil pesos.
O sea: se pagaron los pasteles... y además se perdió una pierna.
Una pierna enterrada en una hacienda de Veracruz. Fin de la historia, ¿no?
Ni cerca. Lo que viene después parece inventado.
```

## Parte 04 · Punto 3: El funeral de una pierna

1.550 caracteres · archivo: `E001_04.mp3`

```
Evidencia dos de cuatro: el funeral.
Al principio, la pierna se enterró sin mucho ruido en su hacienda, Manga de Clavo.
Pero pasaron los años, y Santa Anna volvió al poder. Otra vez.
En mil ochocientos cuarenta y dos era el presidente de México. Y entonces alguien tuvo una idea.
Una idea que hoy suena a broma... y que en su momento se tomó muy en serio.
Desenterrar la pierna. Llevarla a la capital. Y darle el funeral que, según ellos, merecía un héroe.
Imagina que estás ahí. Es el veintisiete de septiembre de mil ochocientos cuarenta y dos, en la Ciudad de México.
La fecha no es casualidad. Ese día se celebraba un aniversario más de la consumación de la independencia.
Hay soldados formados. Hay una procesión. Hay funcionarios, música y salvas de artillería.
Se leen discursos. Se recitan versos en honor al sacrificio del general.
Y todo ese despliegue acompaña a un solo protagonista: una pierna.
La llevan al cementerio de Santa Paula y la colocan en un monumento, sobre una columna, para que todos la vean.
Ahora piensa en esto un segundo.
Miles de soldados dieron la vida entera en las guerras de ese siglo. Y casi ninguno tuvo una ceremonia así.
¿Por qué una pierna sí?
Porque esa pierna no era solo una pierna. Era propaganda.
Era el recordatorio perfecto: este hombre se sacrificó por México. Quien lo critique, critica al héroe de Veracruz.
Mientras la gente lo quisiera, la pierna sería un símbolo de gloria.
El problema es que la gente... no lo quiso por mucho tiempo.
Dos años. Eso fue lo que duró la pierna en su tumba de honor.
```

## Parte 05 · Punto 4: De héroe a enemigo

1.297 caracteres · archivo: `E001_05.mp3`

```
Evidencia tres de cuatro: la tumba vacía.
Para mil ochocientos cuarenta y cuatro, buena parte del país estaba harta de Santa Anna.
Había nuevos impuestos, gastos enormes y un presidente que parecía gobernar para su propia gloria.
A finales de ese año estalló una revuelta en su contra. Y en la capital, la gente salió a las calles.
Derribaron una estatua suya. Al teatro que llevaba su nombre le quitaron el nombre.
Y entonces alguien se acordó de la pierna.
Una multitud fue al cementerio de Santa Paula. Sacaron la pierna de su monumento. Y la arrastraron por las calles de la ciudad.
La misma pierna. La misma ciudad. Apenas dos años después.
Si alguna vez te preguntaste qué tan rápido puede cambiar la opinión pública... aquí tienes la respuesta, en forma de pierna.
¿Y qué pasó con ella después?
Aquí la historia se vuelve borrosa. Las crónicas no se ponen de acuerdo, y hoy nadie sabe con certeza dónde terminó.
La pierna que tuvo un funeral de Estado, simplemente, se perdió.
Pero Santa Anna no se quedó quieto. Nunca lo hacía. Salió desterrado del país, y poco tiempo después volvió. Otra vez.
Para entonces ya caminaba con otra pierna. Una pierna artificial, hecha en parte de corcho.
Esa también iba a tener una vida muy extraña. Y la iba a llevar mucho más lejos que cualquier desfile.
```

## Parte 06 · Punto 5: La pierna que cruzó la frontera

1.748 caracteres · archivo: `E001_06.mp3`

```
Evidencia cuatro de cuatro: el botín.
En mil ochocientos cuarenta y seis estalla la guerra entre México y Estados Unidos. Y Santa Anna, de regreso del exilio, toma otra vez el mando.
Es abril de mil ochocientos cuarenta y siete. Estás en Cerro Gordo, en Veracruz, sobre el camino que sube hacia la capital.
Desde aquí, el ejército mexicano espera frenar el avance de las tropas del general estadounidense Uínfild Scot.
Pero los estadounidenses encuentran un paso entre los cerros y rodean las posiciones mexicanas.
La defensa se desmorona. Y Santa Anna tiene que huir a toda prisa.
Tan a prisa... que deja atrás su carruaje.
Ahí llegan soldados de un regimiento de voluntarios de Ilinói, el Cuarto de Infantería.
Y dentro del carruaje encuentran algo que no esperaban: una de las piernas artificiales del general.
Algunas crónicas agregan un detalle más: que también encontraron su almuerzo, y que se lo comieron.
Ese detalle está mucho menos documentado que el de la pierna. Así que tómalo con pinzas.
Lo que sí está claro es que la pierna se fue con ellos.
Viajó con los soldados de regreso a Ilinói, como trofeo de guerra.
Durante un tiempo, según se cuenta, se mostró en ferias y reuniones, y había que pagar unas monedas para verla.
Imagina eso: la pierna de un presidente mexicano, de pueblo en pueblo, como atracción de feria.
Con los años, terminó en manos del estado de Ilinói.
Hoy está en el Museo Militar del Estado de Ilinói, en la ciudad de Spríngfild. Dentro de una vitrina. Con su ficha.
La guerra terminó en mil ochocientos cuarenta y ocho. México perdió alrededor de la mitad de su territorio.
Y Estados Unidos, además... se quedó con una pierna.
Pero espera. Porque cuando juntas las dos piernas, aparece algo que casi nadie nota.
```

## Parte 07 · Bloque 5: Punto de inflexión

962 caracteres · archivo: `E001_07.mp3`

```
Piénsalo un momento.
Santa Anna tuvo dos piernas famosas.
Una era de carne y hueso. Recibió desfile, discursos, versos y salvas de cañón. Tuvo tumba de honor en la capital.
Y se perdió.
La otra era de corcho. Un objeto. Un repuesto. Nadie le hizo un funeral.
Y sobrevivió.
La pierna que México honró desapareció en México.
La pierna que México perdió en una derrota es la que se conserva... en el país que lo venció.
Casi ciento ochenta años después, sigue ahí.
Y no es solo una curiosidad de museo. Desde México ha habido peticiones para que la devuelvan.
Desde Ilinói, la respuesta ha sido básicamente la misma: es un trofeo ganado en batalla, y se queda donde está.
Incluso se habla de una segunda pierna artificial del general, de madera, guardada en otro lugar de Ilinói.
Así que la pregunta ya no es por qué un país le hizo un funeral a una pierna.
La pregunta es otra. ¿Quién es dueño de la historia? ¿El que la vivió... o el que se quedó con los pedazos?
```

## Parte 08 · Bloque 6: Reflexión

1.412 caracteres · archivo: `E001_08.mp3`

```
Y si crees que esto es solo una rareza del siglo diecinueve, mira lo que pasó con Santa Anna años después.
Ya viejo y desterrado, vivió un tiempo en Nueva York. Y, como siempre, planeaba volver al poder.
Para financiarse tenía una idea: vender chicle, la resina de un árbol que crece en el sureste de México y en Centroamérica.
El plan era usarla como sustituto del caucho, para fabricar cosas como ruedas o botas.
Un inventor estadounidense, Tómas Ádams, experimentó con ese chicle. Como caucho no funcionó... pero se le ocurrió otra cosa.
Venderlo para masticar.
Así arrancó uno de los primeros negocios de goma de mascar en Estados Unidos.
Sí. El chicle también es parte de esta historia.
Y ahora mira cómo se conecta todo.
Santa Anna fue héroe, villano, otra vez héroe y, para la mayoría, villano al final. Su pierna siguió exactamente el mismo camino que su fama.
Primero la gloria. Después el rechazo. Y al final, el olvido... o una vitrina en otro país.
Así funciona la memoria de los pueblos. No solo recordamos a los líderes. Los convertimos en símbolos.
Y cuando el símbolo deja de servir, lo derribamos.
Ahora te pregunto a ti: ¿cuántos héroes de tu país eran, en su momento, tan discutidos como Santa Anna?
Y por cierto, México no se quedó con una sola extremidad famosa. Casi ochenta años después hubo otra.
Un brazo. El de un general de la Revolución. Y su historia es todavía más difícil de creer.
```

## Parte 09 · Bloques 7 y 8: Cierre, veredicto y llamada a la acción

1.298 caracteres · archivo: `E001_09.mp3`

```
Recapitulemos.
Una guerra que empezó, entre otras cosas, por unos pasteles.
Un general retirado que pierde una pierna en Veracruz y vuelve a ser héroe.
Un funeral de Estado, con desfile y cañonazos, para una pierna.
Una multitud que la saca de su tumba apenas dos años después.
Y una pierna de corcho que cruza la frontera como botín y termina en una vitrina en Spríngfild.
Todo eso le pasó a un solo hombre. Y a una sola pierna. Bueno... a dos.
Ahora sí, el veredicto.
¿Le hicieron un funeral de Estado a la pierna de Santa Anna? ¿Y su pierna artificial sigue en un museo de Estados Unidos?
Veredicto: verdad.
Con matices. Algunas cifras y detalles cambian según la fuente, como cuántas veces gobernó o qué pasó con su almuerzo en Cerro Gordo.
Pero lo esencial está documentado.
Santa Anna perdió una pierna defendiendo Veracruz... y la historia nunca se la devolvió.

Deja tu veredicto en los comentarios: ¿lo sabías, o te lo acabo de arruinar?
En pantalla tienes la historia del brazo de ese general de la Revolución, el que terminó guardado durante décadas dentro de un monumento.
Si esta pierna te pareció absurda, ese brazo te va a parecer imposible.
Y si quieres que cada semana desarmemos otro relato, suscríbete a Desarmando Relatos. Aquí las historias son reales, aunque parezcan mentira.
```
