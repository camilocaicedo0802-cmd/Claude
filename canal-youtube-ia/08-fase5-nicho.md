# Fase 5: oportunidad y recomendación de nicho

**Base:** fases 1 a 4 y las políticas de la fase 10 (`07-fase10-monetizacion-politicas.md`).
**Cálculo reproducible:** `scripts/matriz_nicho.py` → `datos/matriz_nicho.csv`.

**Sobre las puntuaciones:** son **juicios míos** (escala de 1 a 5), apoyados en los datos citados, **no mediciones**. Lo medible (demanda, competencia, crecimiento) viene de vidIQ y es una estimación de la herramienta. Por eso abajo pruebo si la recomendación cambia al cambiar los pesos: no cambia.

---

## 1. Los seis enfoques comparados

| Código | Enfoque | De dónde sale |
|---|---|---|
| O1 | Historia de Latinoamérica contada desde preguntas y paradojas (precolombino, conquista, colonia, independencias) | Lịch Sử (fase 2) + demanda por país (fase 3) |
| O2 | Mitos y leyendas de Latinoamérica con su historia real documentada | Crooked (fase 2) + "mitos y leyendas" (fase 3) |
| O3 | **Híbrido:** leyendas + preguntas de historia latinoamericana bajo una misma promesa ("lo que es verdad") | Unión de O1 y O2 |
| O4 | Vida cotidiana e "historia para dormir" (videos de horas) | Estrictamente + "historia para dormir" (fase 3) |
| O5 | Curiosidades globales en catálogo, al estilo Paint | The Paint Explainer, Simple Paint, Some Guy |
| O6 | Segunda Guerra Mundial e historia militar | Te Lo Pinto Fácil, Squire |

## 2. Criterios y pesos

Los criterios son los que pediste. Los pesos reflejan tus prioridades: monetizar pronto y de forma sostenible, diferenciarse y producir con calidad sin publicar en masa.

| Criterio | Peso | Qué mide (5 = mejor) |
|---|---|---|
| Demanda potencial | 12 | Búsquedas estimadas en español latinoamericano y tendencia (fase 3) |
| Competencia | 10 | 5 = baja (índice de vidIQ + incumbentes observados) |
| Diferenciación posible | 12 | Cuánto puede distinguirse un canal nuevo con tu perfil |
| Potencial de viralidad | 8 | Atractivo fuera de la búsqueda (recomendaciones, Shorts) |
| Búsqueda atemporal | 8 | Vigencia de los temas en el tiempo |
| Facilidad de producir constante | 8 | Fuentes disponibles y temas suficientes para años |
| Costo y complejidad | 6 | 5 = bajo |
| Potencial de monetización | 10 | Idoneidad publicitaria, horas de visualización, ingresos alternativos |
| Audiencia fiel | 8 | Identidad, series, recurrencia |
| Riesgo de políticas y derechos | 8 | 5 = riesgo bajo (contenido no auténtico, anuncios limitados, "creado para niños", derechos) |
| Contenido original con IA | 5 | Cuánto aporte humano exige y permite |
| Expansión | 5 | Otros idiomas, formatos y plataformas |

**Cálculo:** total = Σ(puntuación × peso) ÷ 5, sobre 100.

## 3. Matriz ponderada

| Criterio (peso) | O1 Historia | O2 Leyendas | **O3 Híbrido** | O4 Dormir | O5 Curiosidades | O6 Militar |
|---|---|---|---|---|---|---|
| Demanda (12) | 4 | 4 | **5** | 4 | 3 | 4 |
| Competencia (10) | 3 | 3 | 3 | 4 | 2 | 2 |
| Diferenciación (12) | 4 | 4 | 4 | 2 | 2 | 2 |
| Viralidad (8) | 3 | 4 | 4 | 2 | 4 | 4 |
| Atemporal (8) | 5 | 4 | 5 | 4 | 3 | 4 |
| Facilidad constante (8) | 3 | 4 | 3 | 2 | 4 | 3 |
| Costo y complejidad (6) | 3 | 4 | 3 | 2 | 4 | 3 |
| Monetización (10) | 4 | 3 | 4 | 3 | 3 | 2 |
| Audiencia fiel (8) | 4 | 3 | 4 | 3 | 2 | 3 |
| Riesgo políticas y derechos (8) | 4 | 3 | 4 | 2 | 3 | 2 |
| Original con IA (5) | 4 | 4 | 4 | 2 | 3 | 3 |
| Expansión (5) | 3 | 4 | 4 | 3 | 4 | 3 |
| **Total / 100** | **74,2** | **72,8** | **79,2** | **56,6** | **59,4** | **57,6** |

### Justificación de las puntuaciones

**O1. Historia de Latinoamérica**
- **Demanda 4:** "historia de colombia" ~40.000 al mes (+142 %) y "historia de mexico" ~59.000 (+141 %), pero la gente busca por país.
- **Competencia 3:** índices de 46 a 60, con nombres consolidados (Diana Uribe, Academia Play, Felipe Pigna).
- **Diferenciación 4:** casi todo lo existente es resumen escolar o charla; las preguntas con animación y fuentes escasean.
- **Viralidad 3:** los temas nacionales viajan menos entre países.
- **Atemporal 5.**
- **Facilidad 3:** exige mucha investigación.
- **Costo 3:** vestuario y escenarios de época.
- **Monetización 4:** educativo y apto para anunciantes si se evita la violencia gráfica.
- **Audiencia fiel 4:** identidad nacional y series.
- **Riesgo 4:** la política reciente se excluye.
- **Expansión 3.**

**O2. Leyendas**
- **Demanda 4:** "mitos y leyendas" ~53.000 al mes; variantes creciendo (+86 % a +172 %).
- **Competencia 3:** índices de 42 a 58; competidores narradores de terror.
- **Diferenciación 4:** casi nadie cuenta la historia documentada de la leyenda.
- **Viralidad 4:** miedo y reconocimiento en toda la región; funciona bien en Shorts.
- **Atemporal 4:** probable pico en Halloween y Día de Muertos [hipótesis].
- **Facilidad 4:** cientos de leyendas.
- **Costo 4.**
- **Monetización 3:** el terror y el gore limitan los anuncios; parte de la búsqueda es infantil.
- **Audiencia fiel 3:** se viene por una leyenda concreta.
- **Riesgo 3:** miniaturas de terror y riesgo de "creado para niños".
- **Expansión 4:** portugués e inglés.

**O3. Híbrido**
- **Demanda 5:** suma de ambas demandas.
- **Competencia 3:** se pueden escoger las porciones de menor competencia.
- **Diferenciación 4:** posicionamiento único ("lo que es verdad"); bajo de 5 porque dos pilares pueden diluir la marca si no se unen con una promesa clara.
- **Viralidad 4:** las leyendas atraen.
- **Atemporal 5:** la historia retiene.
- **Facilidad 3:** dos tipos de investigación.
- **Costo 3.**
- **Monetización 4:** la historia compensa a las leyendas.
- **Audiencia fiel 4.**
- **Riesgo 4:** el tono documental reduce el riesgo de terror y de "para niños".
- **Expansión 4.**

**O4. Dormir**
- **Demanda 4:** ~159.000 al mes, pero ambigua (cuentos infantiles).
- **Competencia 4:** índice 28.
- **Diferenciación 2:** canales de IA de horas proliferan.
- **Viralidad 2.**
- **Atemporal 4.**
- **Facilidad 2:** producir horas con calidad es inviable a 10-15 h/semana.
- **Costo 2.**
- **Monetización 3.**
- **Audiencia fiel 3:** hábito nocturno.
- **Riesgo 2:** contenido producido en masa.
- **Original con IA 2.**
- **Expansión 3.**

**O5. Curiosidades globales**
- **Demanda 3:** palabras clave con ruido y "lugares prohibidos" cayendo.
- **Competencia 2:** "datos curiosos" con índice 72, clones y versiones dobladas de canales en inglés.
- **Diferenciación 2.**
- **Viralidad 4.**
- **Atemporal 3.**
- **Facilidad 4.**
- **Costo 4.**
- **Monetización 3:** temas morbosos.
- **Audiencia fiel 2.**
- **Riesgo 3.**
- **Original con IA 3.**
- **Expansión 4.**

**O6. Militar**
- **Demanda 4:** grande, pero con mucho peso de Brasil.
- **Competencia 2:** Te Lo Pinto Fácil (585.000 suscriptores) ocupa el título exacto más buscado.
- **Diferenciación 2.**
- **Viralidad 4.**
- **Atemporal 4.**
- **Facilidad 3.**
- **Costo 3.**
- **Monetización 2:** violencia y simbología nazi limitan los anuncios.
- **Audiencia fiel 3.**
- **Riesgo 2.**
- **Original con IA 3.**
- **Expansión 3.**

## 4. ¿Depende el resultado de los pesos?

| Escenario de pesos | 1.º | 2.º | 3.º | Últimos |
|---|---|---|---|---|
| Propuestos | O3 79,2 | O1 74,2 | O2 72,8 | O5 59,4 · O6 57,6 · O4 56,6 |
| Todos iguales | O3 78,3 | O2 73,3 | O1 73,3 | O5 61,7 · O6 58,3 · O4 55,0 |
| Monetización y riesgo primero | O3 79,3 | O1 76,0 | O2 70,3 | O5 58,2 · O4 56,2 · O6 53,9 |
| Demanda y competencia primero | O3 79,8 | O1 73,6 | O2 72,3 | O4 60,4 · O5 59,6 · O6 59,4 |

**Conclusión:** la recomendación es **robusta** a los pesos. El híbrido gana siempre. Los dos componentes, por separado, quedan segundo y tercero. Los otros tres quedan al menos 10 puntos por debajo.

**Advertencia:** la ventaja del híbrido descansa en mi juicio de que los dos pilares se refuerzan. Muchas leyendas latinoamericanas nacen o se transforman en la conquista y la colonia, así que un video puede alimentar al otro. Si la marca no los une con una promesa clara, el híbrido pierde diferenciación. Por eso la propuesta de valor de abajo es una sola frase para ambos.

---

## 5. Recomendación

1. **Nicho principal:** divulgación de historia y cultura de Latinoamérica.
2. **Subnicho:** **"lo que es verdad"** detrás de las leyendas, los misterios y las grandes preguntas de la historia latinoamericana. Precolombino, conquista, colonia e independencias, con anclas en México y Colombia, los mercados con más demanda medida.
3. **Audiencia objetivo** [hipótesis a validar con Studio]:
   - Hispanohablantes de 16 a 35 años en México, Colombia, Perú, Argentina, Chile y la comunidad hispana de EE. UU.
   - Curiosos no académicos que hoy ven explicadores animados y contenido de leyendas.
   - Audiencia secundaria: estudiantes que llegan por búsqueda.
   - **No** es contenido infantil: el canal se configura como "no creado para niños" y el estilo visual evita la estética infantil.
4. **Propuesta de valor:** *"Las leyendas y los misterios de nuestra historia, contados con lo que de verdad dicen las fuentes, y animados como se merecen."*
5. **Posicionamiento diferencial:**
   - **Rigor visible:** fuentes en pantalla y en la descripción, distinción explícita entre "lo documentado" y "lo que cuenta la leyenda".
   - **Neutralidad:** sin política reciente.
   - **Animación de nivel 3** (vectorial, coherente entre miniatura e interior), tu ventaja como diseñador y animador.
   - **Narración en segunda persona y desde una pregunta.**
   - **Alcance pan-latinoamericano** ("de cada país").
6. **Pilares de contenido:**
   - **P1. Leyendas con su historia real.** La Llorona, el Silbón, la Patasola, el Pombero, el Caleuche…
   - **P2. "¿Por qué…?" de la historia latinoamericana.** Paradojas, decisiones y preguntas concretas.
   - **P3. "Así vivías en…".** Vida cotidiana precolombina y colonial, en segunda persona.
   - **P4, ocasional. "De cada país".** Catálogos comparativos que reúnen a toda la región.
7. **Formatos:**
   - **Largo narrativo** de 8 a 12 min (núcleo).
   - **Catálogo largo** de 12 a 15 min, una vez al mes.
   - **Shorts** de 45 a 75 s derivados de cada largo.
   - **Más adelante (mes 3+):** recopilaciones largas de episodios propios para "maratón" o para dormir, solo con 6+ episodios. Es contenido propio reorganizado, a revisar contra la política de contenido reutilizado de la fase 10.
8. **Idioma y mercado inicial:** español latinoamericano **neutro**, sin regionalismos fuertes, con voz de acento neutro. Primeros temas: México y Colombia, más un tema pan-regional al mes. El doblaje a inglés o portugués queda para cuando haya tracción (fase 11, etapa 4).
9. **Duración inicial:** 8 a 12 min en largos y 45 a 75 s en Shorts. Se mantiene estable; la fase 4 mostró que alargar no distingue a los ganadores.
10. **Frecuencia viable** (supuesto: 10-15 h/semana; horas por video en la fase 7, unas 34 h al inicio y unas 22 h con la biblioteca de recursos):
    - **Semanas 1 a 13:** 1 largo cada 2 semanas + 1 a 2 Shorts a la semana. Son 6 largos y unos 15 Shorts en 90 días, con unas 14 h semanales.
    - **Después de los 90 días:** 1 largo cada 10 días con 15 h semanales y la biblioteca hecha. Para publicar 1 largo cada semana hacen falta más de 20 h semanales o un ayudante (fase 7).
    - **No** se publica más rápido a costa de la calidad: la fase 4 mostró que el volumen no es lo que distingue a los que crecen.
11. **Riesgos principales y mitigación:**

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| YouTube lo clasifica como "creado para niños" (por la animación y la búsqueda escolar) | Media | Configurar "no creado para niños"; estilo editorial, no infantil; temas y lenguaje para adultos jóvenes; nada de "para niños" en títulos ni etiquetas (fase 10) |
| Anuncios limitados por violencia o terror (conquista, leyendas) | Media | Sin gore en miniaturas ni descripciones gráficas; contexto educativo explícito; tono documental (fase 10) |
| Contenido no auténtico o producido en masa | Baja si se sigue el sistema | Cada video con investigación propia, guion propio, animación propia y estructura variable; nunca plantillas idénticas ni voz IA sobre imágenes sin aporte (fases 7 y 10) |
| Polarización por política y herida colonial | Media | Excluir la política reciente; presentar varias interpretaciones con fuentes; moderar los comentarios |
| Errores históricos que dañen la credibilidad | Media | Verificación con dos fuentes y fuentes primarias; tarjeta "lo documentado frente a la leyenda"; correcciones fijadas |
| Dilución de marca entre leyendas e historia | Media | Una sola promesa ("lo que es verdad") y una sola plantilla visual para ambos pilares |
| Umbral más alto para entrar en YPP: 8.000 horas en 365 días desde el 1-feb-2027 [dato, fase 10] | Alta: un canal que empieza ahora difícilmente llega a 1.000 suscriptores y 4.000 horas antes de esa fecha | Video largo como núcleo; catálogo mensual y recopilaciones para sumar horas; membresías y Super Thanks desde los 500 suscriptores (fase 10) |
| Crecimiento lento al inicio | Alta | Plan de 90 días como experimento con criterios de decisión (fase 11); los referentes necesitaron de 16 a 52 videos |
| Ingresos por anuncio en español más bajos que en inglés | Probable [hipótesis; sin cifra propia] | Medir el RPM real en Studio; ingresos alternativos (membresías, patrocinios educativos); doblaje en la etapa 4 |
