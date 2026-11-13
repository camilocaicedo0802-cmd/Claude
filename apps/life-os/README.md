# LIFE OS · Centro de control personal

Aplicación web para organizar tres dimensiones en un solo sistema conectado:

| Pestaña | Para qué sirve |
| --- | --- |
| **Finanzas** | Saldo real, ingresos y gastos, cuentas y tarjetas, obligaciones, presupuestos, análisis y **¿Cuánto puedo gastar?** |
| **Clientes** | CRM personal: clientes, trabajos (tablero Kanban y lista), cobros, abonos, seguimientos |
| **Mi Vida** | Mi día, planificador del día (cronograma por bloques y modo enfoque), tracker de tareas estilo Notion, calendario, hábitos y planificación semanal |

Ajustes se abre desde el encabezado (no es una cuarta sección).

## Cómo ejecutarla

Requisitos: Node.js 20.9 o superior.

```bash
npm install                 # desde la raíz del monorepo
npm run dev:life-os         # http://localhost:3003
```

Otros comandos (desde la raíz):

```bash
npm run test:life-os        # pruebas automáticas (vitest)
npm run build:life-os       # exporta un sitio estático en apps/life-os/out
npm run typecheck -w @jcc/life-os
```

`apps/life-os/out` es HTML/JS estático: se puede publicar en cualquier hosting estático (GitHub Pages, Netlify, Vercel, un servidor propio). Para servirla bajo una subruta, construye con `NEXT_PUBLIC_BASE_PATH=/ruta`. El build termina generando `out/sw.js` (script `scripts/build-sw.mjs`).

## En el celular

- Publicada por el workflow de GitHub Pages en `https://<usuario>.github.io/<repo>/life-os/` (se construye con `NEXT_PUBLIC_BASE_PATH=/<repo>/life-os`).
- **Se instala como app**: Android/Chrome muestra el botón «Instalar» en Mi día y en Ajustes; en iPhone, Safari › Compartir › «Agregar a pantalla de inicio».
- **Funciona sin conexión**: un service worker guarda toda la app en caché en la primera visita. Cuando hay una versión nueva aparece el aviso «Actualizar».
- **Importante en iPhone**: la app instalada guarda sus datos aparte de Safari. Instálala primero y úsala siempre desde su ícono.
- La app instalada pide almacenamiento persistente para que el sistema no borre los datos, y recuerda descargar un respaldo cada dos semanas (en el celular el respaldo se comparte a Drive, Archivos, WhatsApp o correo).

La primera vez aparece un onboarding opcional (moneda, zona horaria, cuentas, gastos fijos, primer cliente o tarea). También puedes explorar con el **modo demo**.

## Planificador del día

`Mi Vida › Planificador` arma el cronograma del día:

- **Cronograma**: tareas con hora, eventos y **bloques de tiempo** (trabajo profundo, correos, almuerzo, ejercicio…). En computador se arrastran tareas desde «Por planificar» a la línea de tiempo y se mueven los bloques; en el celular, cada hueco libre tiene «Usar» para llenarlo.
- **Auto-planificar**: ubica las tareas pendientes del día (y las atrasadas) en los huecos libres: prioridad alta primero y en tus **horas de máxima energía**, respetando eventos y dejando una pausa entre bloques. Muestra el plan antes de aplicarlo y se puede deshacer.
- **Ahora / Siguiente**, capacidad del día (planificado vs. disponible) y sugerencias verificables: cruces de horario, más de 3 h sin pausa, horas de energía libres, más tareas que tiempo.
- **Plantillas de día**: guarda tu rutina ideal y aplícala a cualquier día (sin duplicar bloques). Incluye una plantilla sugerida.
- **Modo enfoque** (Pomodoro): temporizador con barra flotante y vista a pantalla completa; sigue contando aunque cierres la app, avisa con sonido, vibración y notificación, y suma el tiempo real a cada tarea.
- **Cerrar el día**: resumen (completadas, puntos, minutos de enfoque) y mover lo pendiente a mañana en un toque.
- Ajustes › Planificador y enfoque: horario del día, horas de máxima energía, pausa entre bloques, duración por defecto y duración de enfoque/descanso.

## Tracker de tareas

`Mi Vida › Tareas` funciona como una base de datos tipo Notion:

- Columnas **Estado** (Sin empezar, En curso, Completada), **Tarea** (con icono), **Prioridad**, **Categoría** (editables: Trabajo, Proyecto personal, Casa…), **Puntos** y **Fecha**. Cada celda se edita en el lugar.
- Vistas: Pendientes, Esta semana, Tablero (arrastrar entre estados), Completadas y Todas. Filtros, búsqueda, orden y agrupación (categoría, estado, prioridad, día). Totales de tareas y puntos.
- En el celular la tabla se convierte en tarjetas con las mismas propiedades editables.
- **Importar**: pega filas copiadas de Notion, Excel o Google Sheets (o una tarea por línea). También acepta un enlace `…/vida/tareas/#importar=<texto>`: abre el importador con la vista previa. Importar dos veces la misma lista no duplica tareas.

## Cómo se guardan los datos

- **IndexedDB del navegador** (con Dexie), en el propio dispositivo. No se envía nada a ningún servidor.
- Cada tabla usa identificadores UUID y `createdAt`/`updatedAt`, pensados para migrar a una base sincronizada (p. ej. Supabase/PostgreSQL con RLS) sin reescribir los datos.
- El dinero se guarda en **enteros** (unidades menores ×100) para evitar errores de punto flotante.
- Las fechas se guardan como `AAAA-MM-DD` en la **zona horaria configurada** (America/Bogota por defecto), no la del dispositivo.
- **Modo demo**: base de datos separada (`lifeos-demo`). Tus registros reales (`lifeos`) nunca se mezclan con la demo.
- **Respaldo**: Ajustes › Tus datos › Descargar / Restaurar respaldo (JSON). Movimientos y reportes se exportan en CSV.

> **Sincronización entre celular y computador: no disponible.** Cada navegador tiene su propia base. Para pasar datos de un dispositivo a otro usa el respaldo JSON. La sincronización requiere un backend con autenticación que aún no está configurado.

## Modelo de datos (resumen)

| Entidad | Notas |
| --- | --- |
| `settings` | Nombre, moneda, zona horaria, primer día de la semana, tema, reglas del cálculo de gasto, notificaciones |
| `accounts` | Efectivo, banco, billetera, ahorro, otra, **tarjeta de crédito** (su cupo nunca es dinero). `spendable` separa dinero de uso diario del apartado |
| `categories` | Gasto (fijo / variable / discrecional) e ingreso; personalizables |
| `transactions` | Ingreso, gasto o **transferencia** (nunca cuenta como ingreso/gasto). Vínculos explícitos: `clientPaymentId`, `obligationId` + `occurrenceDate`, `plannedIncomeId` |
| `budgets` | Límite mensual por categoría |
| `obligations` | Un registro por compromiso; los vencimientos recurrentes se **calculan** (no se duplican). Los pagos son movimientos vinculados a `(obligación, fecha de vencimiento)`, por lo que admiten pagos parciales |
| `plannedIncomes` | Ingresos previstos, confirmados o inciertos |
| `goals`, `goalContributions` | Metas de ahorro y fondo de emergencia |
| `clients`, `jobs`, `jobStatuses`, `jobTemplates` | Estado de producción (personalizable) separado del estado de cobro |
| `clientPayments` | Anticipos, abonos y pagos finales. Con cuenta receptora tienen **exactamente un** ingreso vinculado |
| `activities` | Historial cronológico por cliente y trabajo |
| `tasks` (+ subtareas), `dayPlans` | Las tareas recurrentes generan la siguiente instancia al completarse, sin duplicar. Los recordatorios de clientes son tareas con tipo de seguimiento |
| `events` | Eventos con recurrencia y excepciones |
| `habits`, `habitLogs` | Un registro por hábito y día (`habitId:fecha`): no puede duplicarse |
| `weekPlans` | Prioridades y revisión semanal |

## Reglas clave

- **¿Cuánto puedo gastar?** parte del dinero disponible para gastar y resta obligaciones hasta el horizonte (incluidas las vencidas), gastos esenciales estimados (presupuestos o historial), colchón de seguridad y reservas para metas. Muestra **Disponible hoy**, **Esta semana** y **Para ocio**, con el cálculo completo visible. Nunca suma dinero de clientes ni ingresos futuros (salvo que actives contar ingresos confirmados). Sin cuentas, explica qué falta en lugar de inventar una cifra.
- El horizonte por defecto va **hasta el día antes del próximo ingreso confirmado** (o fin de mes si no hay uno).
- Pagar una tarjeta desde una obligación es una **transferencia**, para no contar dos veces las compras.
- Un pago de cliente nunca puede superar el precio acordado sin confirmación explícita (en ese caso se ajusta el precio).
- Editar o anular un pago actualiza o revierte su ingreso vinculado, y viceversa.
- Las rachas de hábitos solo cuentan días programados.

## Estado de las funcionalidades

**Completo y funcional:** las tres pestañas con creación, edición, eliminación o archivo; vínculos entre pestañas (pagos ↔ ingresos, entregas y pagos en agenda, recordatorios); app instalable y sin conexión (PWA); búsqueda global (⌘K o /); botón «+» universal y atajos (N, G+F/C/V/A); notificaciones dentro de la app; modo claro y oscuro; onboarding; modo demo; respaldo JSON; exportación CSV; diseño responsivo de 320 px a escritorio.

**Requiere configuración adicional (no implementado):**

- Sincronización entre dispositivos, cuentas de usuario y respaldo en la nube (necesita un backend como Supabase con autenticación y Row Level Security).
- Notificaciones push en segundo plano (las alertas se muestran mientras la app está abierta).

## Pruebas

`npm run test:life-os` ejecuta 36 pruebas sobre IndexedDB simulada (fake-indexeddb), incluidos los escenarios de aceptación: financiero, clientes, agenda, hábitos, transferencias, tarjetas, cobros vinculados, recurrencias y respaldo.

## Estructura

```
src/
  app/                rutas (Next.js App Router, exportación estática)
  db/                 esquema Dexie, tipos, valores iniciales, datos demo
  domain/             reglas puras: finanzas, clientes, hábitos, agenda, alertas, recomendaciones
  services/           escrituras con transacciones (mantienen vínculos consistentes)
  hooks/              datos reactivos (useLiveQuery) y cálculos derivados
  components/         ui (base), shell (navegación, búsqueda, +, notificaciones), forms, finance, clients, life, settings
tests/                pruebas de vitest
```
