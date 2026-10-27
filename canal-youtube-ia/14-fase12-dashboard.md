# Fase 12: dashboard de seguimiento

**Archivo:** `dashboard_canal.xlsx`. Se abre en Excel o en Google Sheets (Archivo → Importar). Lo genera `scripts/dashboard.py`.

**Revisión:** recalculé el archivo con LibreOffice y no dio errores en ninguna de sus 4.970 fórmulas. Además, comprobé las fórmulas con datos de prueba:

- Los múltiplos y las clasificaciones de 19 filas inventadas coincidieron con el mismo cálculo hecho en Python.
- Los totales de la hoja "Ideas" coinciden con `datos/banco_ideas.csv`.

---

## 1. Hojas

| Hoja | Para qué sirve | Qué escribes tú |
|---|---|---|
| **Leeme** | Leyenda de colores, rutina de uso, método para identificar ganadores y una fila de ejemplo | Nada |
| **Videos** | Una fila por video o Short, con todos los campos que pediste y los cálculos de rendimiento relativo | Columnas A a AE (texto azul). Las 19 filas del plan de 90 días (L1–L6, S1–S13) ya tienen fecha prevista, pilar, tema, término de búsqueda, título y concepto de miniatura |
| **Ideas** | Banco de ideas con la puntuación de la fase 8. Los pesos se pueden editar y el total se recalcula | Puntos de 1 a 5, nuevas ideas y estado |
| **Experimentos** | Hipótesis, variantes y resultado de cada prueba. Cuenta las victorias de cada regla | Una fila por experimento, **antes** de empezar. Ya están H1 a H5 |
| **Resumen** | Indicadores por formato y por pilar, progreso hacia el Programa de Socios y comparación con los escenarios de la fase 11 | Celdas amarillas: datos de Studio y umbrales |
| **Referencias** | Los 8 canales analizados, con suscriptores por vista y días hasta 1k y 10k | Nada |
| **Glosario** | Qué es cada campo, si es público o privado, dónde se obtiene y cuándo se registra | Nada |

## 2. Campos de la hoja Videos

Incluye todos los campos que pediste. Los nombres van en minúscula y sin espacios para que funcionen como filtros y fórmulas.

| Pediste | Columna | Tipo |
|---|---|---|
| Fecha | `fecha_publicacion` | Entrada |
| URL | `url` | Entrada |
| Pilar | `pilar` (P1 a P4, lista desplegable) | Entrada |
| Tema | `tema` | Entrada |
| Palabra clave | `keyword_principal` | Entrada |
| Título | `titulo` | Entrada |
| Concepto de miniatura | `concepto_miniatura` | Entrada |
| Duración | `duracion_min` | Entrada |
| Vistas a 24 h, 7 días y 28 días | `vistas_24h`, `vistas_7d`, `vistas_28d` | Entrada |
| Impresiones | `impresiones_28d` | Entrada |
| CTR | `ctr_28d` | Entrada |
| Duración media vista (AVD) | `avd_min` | Entrada |
| Porcentaje visto | `pct_visto` = AVD ÷ duración | **Fórmula** |
| Retención inicial | `retencion_30s` | Entrada |
| Tiempo de visualización | `horas_vistas_28d` | Entrada |
| Suscriptores | `subs_ganados_28d` | Entrada |
| Fuentes de tráfico | `trafico_busqueda`, `trafico_recomendaciones`, `trafico_shorts` (entrada) y `trafico_otros` (fórmula) | Mixto |
| Costos | `costo_usd` | Entrada |
| Horas | `horas_produccion` | Entrada |
| Estado de monetización | `estado_monetizacion` (lista desplegable) | Entrada |
| Aprendizaje | `aprendizaje` | Entrada |
| Próximo experimento | `proximo_experimento` | Entrada |
| *(añadidos)* | `id`, `estado_video`, `formato`, `cumplimiento_ok` (lista de comprobación de la fase 10) | Entrada |
| *(calculados)* | `mediana_prev5_7d`, `multiplo_7d`, `mediana_prev5_28d`, `multiplo_28d`, `mediana_pct_visto_formato`, `clasificacion`, `costo_por_mil_vistas`, `subs_por_mil_vistas` | **Fórmula** |

Los porcentajes se escriben como fracción: 4,5 % se escribe 0,045. Cada cabecera con un triángulo rojo lleva una nota que explica de dónde sale el dato en Studio.

## 3. Métricas públicas y privadas

| Pública (cualquiera la ve, también en canales ajenos) | Privada (solo tú, en YouTube Studio) | Interna (tu registro) |
|---|---|---|
| Vistas actuales, likes, comentarios, duración, título, fecha y miniatura | Impresiones, CTR, AVD, porcentaje visto, retención, tiempo de visualización, suscriptores por video, fuentes de tráfico, países, ingresos y RPM | Costo imputado, horas de producción, cumplimiento, aprendizaje y experimentos |

Por eso la fase 1 comparó a los canales ajenos solo con métricas públicas. Las privadas no las tiene ninguna herramienta (fase 1, sección 2). En el canal propio, las métricas privadas son las que deciden.

## 4. Cómo se identifica un ganador

Es el mismo principio de la fase 1, aplicado al canal propio:

1. **Múltiplo** = vistas a 28 días ÷ mediana de las vistas a 28 días de los **5 videos anteriores del mismo formato**. Un largo se compara con largos y un Short con Shorts. Así se separa el efecto del tema y del empaquetado del crecimiento general del canal.
2. **Ganador:** múltiplo de **1,5×** o más **y** porcentaje visto igual o mayor que la mediana del formato. La segunda condición evita premiar una miniatura engañosa: muchas vistas con poca retención no cuentan.
3. **Perdedor:** múltiplo de **0,67×** o menos.
4. **A los 7 días** se muestra una clasificación provisional con el múltiplo de 7 días. Sirve para decidir pronto si se reempaqueta (fase 8, sección 6).
5. **Los umbrales** (1,5 y 0,67) se pueden cambiar en "Resumen". Son una convención mía, no una cifra oficial.
6. **Los primeros videos de cada formato** tienen menos de 5 anteriores. El múltiplo usa los que haya, así que es poco fiable hasta el sexto video.

**Qué se hace con un ganador:**

1. Anota en `aprendizaje` qué tenía distinto: tema, título, miniatura, gancho o estructura.
2. Convierte ese rasgo en una hipótesis en la hoja "Experimentos".
3. Pruébalo en el siguiente video.

Un rasgo solo pasa a ser **norma del canal** cuando gana en 3 pruebas. La columna `estado_de_la_regla` de la hoja "Experimentos" lo calcula sola.

## 5. Rutina

| Cuándo | Qué haces | Tiempo |
|---|---|---|
| Al publicar | Rellenas la fila del video: estado, URL, duración, costo, horas y cumplimiento | 5 min |
| A las 24 h | `vistas_24h` | 1 min |
| A los 7 días | `vistas_7d`, `retencion_30s` y el resultado provisional de la prueba A/B | 5 min |
| A los 28 días | El resto de métricas de Studio y el aprendizaje | 10 min |
| Cada semana | Celdas amarillas de "Resumen" (pantalla "Ganar dinero" de Studio) | 5 min |
| Cada mes | Vuelves a puntuar "Ideas" (costo y demanda con vidIQ) y revisas los pilares en "Resumen" | 30 min |
| Día 90 | Informe de 90 días (fase 11, sección 4) con los datos de "Resumen" | 2 h |

**Unos 25 minutos por video**, más 5 minutos a la semana.

## 6. Límites del dashboard

- **Los datos se pasan a mano** desde Studio. Exportar a CSV desde Studio y pegarlo es posible, pero las columnas no coinciden una a una.
- **La API de YouTube Analytics** permitiría automatizarlo. Requiere configurar un proyecto en Google Cloud con OAuth. Lo dejo para cuando el canal tenga datos que lo justifiquen (fase 7, sección 7).
- **El progreso hacia el Programa de Socios** que muestra Studio en "Ganar dinero" es la fuente oficial. El dashboard solo lo copia y lo compara con los tres umbrales de la fase 10.
- **Las cifras de los escenarios** son supuestos de la fase 11, no metas oficiales ni predicciones.
