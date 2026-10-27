# Fase 7: sistema de producción con IA

**Fuentes y fecha:** las herramientas, los precios y las licencias se consultaron el 27-oct-2026 en las páginas oficiales de cada servicio. Lo hizo un agente de investigación, y yo integré su informe aquí.

**Cómo leer los precios:**
- Son precios de lista en EE. UU., en dólares y sin impuestos. En Latinoamérica algunos servicios cobran precios locales distintos.
- **NV** significa que el precio o la condición no se pudo confirmar en la página oficial. Varias páginas bloquearon la consulta: Adobe, Midjourney, Leonardo, Canva y Kling. En esos casos uso referencias de terceros y lo indico.

**Valoraciones:** la curva de aprendizaje, el grado de automatización y la calidad son valoraciones mías, no mediciones.

**Tus herramientas:** según tu portafolio, ya usas After Effects, Premiere Pro, Illustrator, Photoshop, Canva, CapCut, ElevenLabs, Midjourney, ChatGPT y Claude. El sistema parte de ellas para no sumar curva de aprendizaje, salvo cuando una licencia lo desaconseja (CapCut, ElevenLabs gratis).

---

## 1. Principio: qué hace la IA y qué haces tú

| La IA acelera | Tú decides y firmas |
|---|---|
| Resúmenes de fuentes, primeros borradores, variantes de títulos y descripciones | **Verificar cada dato contra una fuente primaria o académica.** Distinguir leyenda de hecho. Tratar el contexto indígena y afro sin estereotipos |
| Narración por síntesis de voz, transcripción y subtítulos | Pronunciación de nombres en náhuatl, quechua, muisca, etc. Corrección de subtítulos |
| Fondos, texturas y bocetos de concepto | **Diseño y rig de los personajes principales**, dirección de arte y redibujo al estilo de la casa |
| Investigación de palabras clave | La elección del tema y del ángulo (fase 8) |
| — | Revisar la licencia de cada recurso y llevar el registro. Avisar del contenido sintético realista en Studio (fase 10) |

**Por qué este reparto:**

1. **Monetización.** YouTube permite usar IA para "visualize a unique character and narrative you invented" y para "edit your video scripts". No monetiza el contenido "made with generic or unoriginal templates giving the impression of mass production" (fase 10).
2. **Derechos de autor.** La Oficina de Copyright de EE. UU. (29-ene-2025) dice que "prompts do not alone provide sufficient control". Una imagen generada solo con un prompt no se puede proteger. **Tu rig, tu redibujo y tu montaje sí.**

---

## 2. El flujo en 18 etapas

**Herramienta inicial:** la de la pila de hasta 50 USD (sección 3).
**Horas:** estimación por video largo de 10 minutos, con 2 o 3 Shorts derivados. La primera cifra es el inicio, sin biblioteca de recursos. La segunda es la etapa madura, con biblioteca y plantillas. Es un **supuesto**: lo corregimos con tu registro real de horas en el dashboard.

| # | Etapa | Herramienta inicial | Alternativa | Coste | Curva | Automat. | Calidad | Limitaciones y licencia | Quién | Horas |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Ideas y puntuación | Hoja "Ideas" del dashboard (`datos/banco_ideas.csv`) | Notion gratis | 0 | Baja | Media | — | — | Tú eliges. La IA propone variantes | 0,5 → 0,25 |
| 2 | Palabras clave y demanda | Autocompletado de YouTube + vidIQ gratis (150 créditos al mes) | vidIQ Boost: 19 USD/mes o 199 USD/año | 0 | Baja | Alta | Media (son estimaciones) | Los volúmenes de vidIQ son estimaciones | IA y herramienta; tú interpretas | 0,5 → 0,25 |
| 3 | Investigación de fuentes | Gemini gratis (Deep Research) + Gemini Notebook gratis (antes NotebookLM; 50 fuentes por cuaderno) + archivos (sección 4) | Perplexity gratis (3 Pro al día); Google AI Pro 19,99 USD | 0 | Baja | Alta | Alta para sintetizar | Deep Research mezcla fuentes secundarias: hay que **verificar cada cita** | La IA busca y resume. Tú lees las fuentes primarias | 4 → 3 |
| 4 | Ficha de hechos y verificación | Ficha del expediente (fase 9) + Gemini Notebook (responde solo con tus fuentes) | Claude o ChatGPT gratis | 0 | Baja | Baja | — | Ningún modelo sustituye la verificación | **Tú** | 1 → 0,5 |
| 5 | Esquema | Claude o ChatGPT gratis, con las estructuras de la fase 9 | Claude Pro: 20 USD/mes o 17 USD/mes con pago anual | 0 | Baja | Media | Alta | Los planes gratis tienen límites de uso | La IA propone. Tú eliges la pregunta y el veredicto | 1 → 0,5 |
| 6 | Guion | Claude o ChatGPT gratis + tu reescritura en español neutro | Claude Pro o ChatGPT Plus (20 USD) | 0 | Baja | Media | Alta en redacción | Cada dato del borrador vuelve a la ficha de hechos | Borrador con IA; **voz y ritmo tuyos** | 3 → 2 |
| 7 | Revisión de hechos, ritmo y políticas | Lista de la fase 10, sección 14 + reglas de la fase 9 | Revisor histórico externo cuando haya ingresos | 0 | — | Baja | — | — | **Tú** | 1 → 0,5 |
| 8 | Voz | ElevenLabs Starter: 6 USD/mes o 5 USD/mes con pago anual. Unos 30 minutos al mes, con licencia comercial y clon instantáneo de tu voz | **Tu voz grabada (0)**; Google Chirp 3 HD (1 millón de caracteres gratis al mes, voz es-US); Azure es-MX (0,5 millones gratis) | 6 | Baja | Alta | Alta (el acento depende de la voz elegida; estimación) | **El plan gratis de ElevenLabs no permite uso comercial** y exige poner "elevenlabs.io" en el título. El clon profesional solo puede ser de **tu** voz. PlayHT habría cerrado el 31-dic-2025 (solo fuentes de terceros) | La IA narra. Tú corriges pronunciación y entonación | 1 → 0,5 |
| 9 | Guion visual (lista de planos) | Columna "visual" del guion en Sheets o Docs | Storyboard en Illustrator o Affinity | 0 | Baja | Baja | — | — | **Tú** | 1 → 0,5 |
| 10 | Biblioteca de personajes y escenarios | Illustrator (si lo tienes) o **Affinity (gratis para particulares)** + rigs en After Effects | Moho Debut (59,99 USD, pago único) para rigs de recortes | 0 | Media | Baja | Muy alta | Es la inversión que abarata los videos siguientes | **Tú** | Inversión única de 15 a 20 h en las semanas 1 a 3; luego 1 h por video para ampliarla |
| 11 | Imágenes base con IA | **Recraft Basic**: 12 USD/mes o 10 USD/mes con pago anual. 1.000 créditos, con Flux, GPT Image y Nano Banana, estilos propios y derechos comerciales | Midjourney Basic (10 USD, uso comercial; precio solo en fragmentos indexados); Ideogram Plus (15–20 USD) para texto en imagen | 12 | Baja | Alta | Alta | **El plan gratis de Recraft es solo para uso personal y las imágenes son de Recraft.** Guarda la licencia de cada imagen | La IA genera fondos y bocetos | 2 → 1,5 |
| 12 | Redibujo al estilo de la casa | Photoshop o Illustrator, o Affinity / Photopea gratis | — | 0 | Media | Baja | Muy alta | Es lo que convierte la imagen en obra protegible y no "genérica" | **Tú** | 3 → 1,5 |
| 13 | Animación | **After Effects**: suelto, unos 22,99 USD/mes (**NV**, referencia de terceros) | Cavalry (gratis para particulares); Blender Grease Pencil (gratis) | 23 | Baja para ti | Media (rigs y expresiones) | Muy alta | El precio de Adobe no se pudo verificar | **Tú**. Video con IA solo para planos puntuales (sección 5) | 8 → 5 |
| 14 | Montaje, música y efectos | After Effects / Premiere, o **DaVinci Resolve gratis**. Música de la **Biblioteca de Audio de YouTube** (gratis y sin reclamaciones de Content ID) | Epidemic Creator (9,99 USD/mes con pago anual, 1 canal por plataforma); Freesound solo con licencias CC0 o CC BY | 0 | Media | Baja | Muy alta | **CapCut:** sus "Sounds" son "non-commercial", sus "Commercial Sounds" no cubren YouTube y CapCut obtiene una licencia perpetua y sublicenciable sobre tu contenido. **Música de Suno gratis: sin uso comercial. Udio: no permite descargas** | **Tú** | 3 → 2 |
| 15 | Subtítulos | Subtítulos automáticos de YouTube (se revisan) o **Whisper** (código abierto, licencia MIT, en tu equipo) | Premiere (incluido) | 0 | Baja | Alta | Alta tras revisión | Whisper turbo necesita unos 6 GB de memoria de vídeo | La IA transcribe. Tú corriges nombres propios | 0,5 → 0,25 |
| 16 | Miniatura | Photoshop o Affinity, con la plantilla 1-2-3 de la fase 6 | Canva Pro (12 USD/mes con pago anual) | 0 | Baja | Baja | Muy alta | — | **Tú**. La IA ayuda con fondos | 1,5 → 1 |
| 17 | Metadatos y publicación | Plantilla de la fase 8 + lista de la fase 10 + YouTube Studio | vidIQ (puntuación de títulos) | 0 | Baja | Media | — | Prueba A/B: solo en ordenador | La IA redacta variantes. Tú publicas | 0,5 → 0,25 |
| 18 | Shorts derivados y análisis | After Effects (formato vertical a partir del mismo proyecto) + dashboard | — | 0 | Baja | Media | Alta | Los Shorts no suman horas para el Programa de Socios | **Tú** | 2 → 1,5 |

### Horas por video largo (estimación)

| Momento | Horas por largo con sus Shorts | Supuestos |
|---|---|---|
| Semanas 1 a 6 (sin biblioteca) | **unas 34 h** (suma de la tabla) | Personajes y escenarios nuevos en cada video; curva de aprendizaje de la marca |
| Semanas 7 a 13 (con biblioteca) | **unas 22 h** | Reutilizas el rig del búho, las texturas, los sellos y algunos escenarios |
| Además, una inversión única | 15 a 20 h | Logo, banner, plantillas, rig del búho y primeras texturas (semanas 1 a 3) |

**Consecuencia para la frecuencia, con tus 10 a 15 h semanales** (supuesto de la fase 1):

| Horas a la semana | Inicio (34 h por video) | Etapa madura (22 h por video) |
|---|---|---|
| 10 h | 1 largo cada 3 a 4 semanas | 1 largo cada 2 semanas |
| 15 h | 1 largo cada 2 a 2,5 semanas | 1 largo cada 10 días |
| 20 h | 1 largo cada 1,5 a 2 semanas | casi 1 largo a la semana |

**Corrección a la fase 5:** con 10 a 15 h a la semana **no da para 1 largo semanal** en las semanas 9 a 13. El plan de 90 días (fase 11) usa 1 largo cada 2 semanas, que da **6 largos y unos 15 Shorts en 13 semanas**. Eso suma unas 185 h (17 h de inversión inicial + 3 × 34 h + 3 × 22 h), es decir, **unas 14 h a la semana**. Con 10 h semanales salen 4 largos. Publicar cada semana exige más de 20 h semanales, o un ayudante para la investigación o el redibujo.

---

## 3. Pilas recomendadas

### Pila inicial (hasta 50 USD al mes)

| Tarea | Herramienta | USD/mes |
|---|---|---|
| Animación y montaje | After Effects suelto (**NV**: unos 22,99 USD; Premiere no está incluido). Si ya pagas Creative Cloud, este coste desaparece | 22,99 |
| Imágenes base | Recraft Basic (derechos comerciales, incluye varios modelos) | 12 |
| Voz | ElevenLabs Starter (unos 30 min al mes: unos 3 largos de 10 minutos). Alternativa gratis: tu voz | 6 |
| Investigación y guion | Gemini gratis, Gemini Notebook gratis, Claude o ChatGPT gratis, Perplexity gratis | 0 |
| Música | Biblioteca de Audio de YouTube | 0 |
| Edición alternativa, subtítulos y miniaturas | DaVinci Resolve gratis, Whisper, Affinity o Photopea | 0 |
| SEO y organización | YouTube Studio, vidIQ gratis, Google Sheets (dashboard), Trello o Notion gratis | 0 |
| **Total** | | **unos 41 USD** |

**Margen de 9 USD.** Si el límite del plan gratis frena la escritura, cambia Recraft por Claude Pro con pago anual (17 USD). Las imágenes de base se sacan entonces de archivos de dominio público (sección 4).

**Variante de 0 USD:**

- Cavalry o Blender para animar, y DaVinci Resolve para editar.
- Tu voz.
- Grabados y códices de dominio público como base gráfica: encajan con el estilo grabado de la fase 6.
- Biblioteca de Audio de YouTube.

Es más lenta, pero viable.

### Pila de escalado (unos 216 USD al mes, cuando haya ingresos)

| Herramienta | USD/mes | Para qué |
|---|---|---|
| Adobe Creative Cloud Pro (After Effects, Premiere, Photoshop, Illustrator) | 69,99 (fragmento indexado de adobe.com) | Toda la suite |
| Claude Pro | 20 | Guion y análisis |
| Google AI Pro | 19,99 | Deep Research, Gemini Notebook ampliado y créditos de Flow (video con Veo / Omni) |
| ElevenLabs Creator | 22 | Clon profesional de **tu** voz, unos 121 minutos al mes |
| Midjourney Standard | 30 | Estética y `--sref` para el estilo |
| Runway Standard | 15 | Planos puntuales con IA |
| Epidemic Sound Creator (pago anual) | 9,99 | Música (Pro, 16,99 USD, si haces anuncios o trabajas para clientes) |
| vidIQ Boost | 19 | Palabras clave sin límite de créditos |
| Notion Plus | 10 | Organización |
| **Total** | **unos 216 USD** | |

**Opcionales:**

- Perplexity Pro (20 USD/mes).
- DaVinci Resolve Studio (236 USD, pago único).
- **Presupuesto para un revisor histórico o un ilustrador independiente.** Es lo primero que conviene pagar cuando haya ingresos, porque protege la promesa "Con fuentes".

---

## 4. Archivos y fuentes de imagen: qué se puede usar

| Archivo | ¿Uso comercial de imágenes de dominio público? | Condiciones |
|---|---|---|
| **Biblioteca Digital Hispánica (Biblioteca Nacional de España)** | **Sí**: licencia CC BY 4.0. Su uso "es gratuito y no requiere autorización previa con independencia del uso público" | Citar "Imágenes procedentes de los fondos de la Biblioteca Nacional de España". No usar el logo |
| **Library of Congress** ("Free to Use and Reuse") | **Sí** en esa colección | En el resto, revisar "Rights & Access" en cada ficha |
| **Wikimedia Commons** | **Sí, si la licencia del archivo lo permite** (dominio público, CC0, CC BY, CC BY-SA) | Wikimedia "no ofrece garantía". Rastrear el original y acreditar al autor |
| **Biblioteca Nacional de Colombia** | Sí para obras de dominio público, citando la fuente. No menciona expresamente el uso comercial | Revisar la ficha |
| **PARES (Archivo General de Indias y otros)** | Sí para dominio público, "sin permiso previo", citando archivo, signatura y URL. No menciona expresamente el uso comercial | Lo que no es de dominio público necesita autorización |
| **AGN Colombia** | Condicional: formato de autorización AAD-FO-83 | Tarifas por resolución anual |
| **AGN México** | De pago: 250 por imagen en la lista de 2021; presumo pesos mexicanos | Tarifa actual NV |
| **Mediateca INAH** | **No por defecto**: CC BY-NC-ND 4.0 | Hace falta autorización para otros usos. **La ley mexicana de monumentos exige permiso del INAH para reproducir monumentos con fines comerciales** (según prensa de 2024; consultar antes de usar fotos de zonas arqueológicas mexicanas) |
| **Biblioteca Virtual Miguel de Cervantes** | **No**: solo uso personal y no comercial | Úsala para leer y citar. Saca la imagen de la biblioteca de origen |
| **Internet Archive y Google Books** | Piden un uso no comercial | Busca el original en la institución que lo guarda |

**Regla práctica:** el canal **dibuja** sus escenas y usa los documentos antiguos como **tarjeta de fuente** (fase 9). Cada imagen de archivo lleva su fila en el registro de licencias (sección 6).

---

## 5. Video generado con IA: solo para planos puntuales

| Herramienta | Precio | Licencia | Nota |
|---|---|---|---|
| Runway Standard | 15 USD/mes o 12 USD/mes con pago anual | Uso comercial en todos los planes. Runway puede **entrenar con tus inputs y outputs** | Para un plano de transición o una textura en movimiento |
| Google Veo / Omni (Flow) | Incluido en Google AI Pro | Marca de agua visible y SynthID en la app de Gemini. Términos de uso NV | — |
| Luma Plus | 30 USD/mes o 25 USD/mes con pago anual | Uso comercial solo con suscripción activa. **La marca de agua del plan gratis es permanente** | — |
| Kling y Hailuo | NV (de 7 a 15 USD según terceros) | Los planes gratis tienen marca de agua y no permiten uso comercial | — |

**No se recomienda al inicio, por tres razones:**

1. Encarece la producción.
2. Rompe la coherencia del estilo.
3. La política de YouTube no monetiza "videos that stitch together unrelated or inconsistent AI clips" (fase 10).

Además, si el plano es fotorrealista, obliga a avisar del uso de IA.

---

## 6. Organización de archivos y registro de licencias

```
canal/
├── biblioteca/
│   ├── personajes/      (rigs .aep, ilustraciones .ai/.psd)
│   ├── escenarios/
│   ├── texturas-y-sellos/
│   ├── tipografias/     (Anton, Oswald, Fraunces, Inter: licencia SIL OFL de Google Fonts)
│   └── licencias.csv    (registro único, ver columnas abajo)
└── expedientes/
    └── E001-llorona/
        ├── 01-investigacion/   (ficha del expediente, fuentes en PDF)
        ├── 02-guion/
        ├── 03-voz/
        ├── 04-arte/            (imágenes base de IA + redibujos)
        ├── 05-animacion/
        ├── 06-montaje/
        └── 07-publicacion/     (miniaturas A/B/C, descripción, SRT)
```

Columnas de `licencias.csv`:

```
expediente, archivo, tipo (imagen/música/voz/fuente), origen (herramienta o archivo),
plan o licencia, uso comercial (sí/no), atribución requerida, enlace, fecha
```

---

## 7. Qué se puede automatizar más adelante

Son mejoras de eficiencia para cuando el canal esté en marcha. No hacen falta para empezar.

1. **Ficha del expediente y descripción:** una plantilla que se rellena desde la hoja "Ideas" y genera la descripción con capítulos y fuentes (fase 8).
2. **Subtítulos:** Whisper en lote sobre la voz final, con exportación a SRT.
3. **Expresiones de After Effects** para los sellos, el contador de evidencias y las tarjetas de fuente. Se programan una vez y se reutilizan.
4. **Exportación de datos de Studio** al dashboard cada semana, con un CSV de Studio pegado en la hoja "Videos".

**Lo que no se automatiza:** la verificación de hechos, el redibujo, la animación de los momentos clave y la decisión del tema. Son la diferenciación del canal y lo que exige la política de contenido no auténtico.
