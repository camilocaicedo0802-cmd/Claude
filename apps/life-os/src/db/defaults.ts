import { nowISO, DEFAULT_TIME_ZONE } from "@/lib/dates";
import { uid } from "@/lib/utils";
import type { LifeOSDB } from "./db";
import type { Category, DayTemplate, ExpenseNature, JobStatus, PlannerSettings, Settings, TaskCategory } from "./types";

export const DEFAULT_TASK_CATEGORIES: TaskCategory[] = [
  { key: "trabajo", name: "Trabajo", color: "orange" },
  { key: "proyecto", name: "Proyecto personal", color: "amber" },
  { key: "hogar", name: "Casa", color: "emerald" },
  { key: "clientes", name: "Clientes", color: "violet" },
  { key: "personal", name: "Personal", color: "iris" },
  { key: "salud", name: "Salud", color: "pink" },
  { key: "estudio", name: "Estudio", color: "teal" },
  { key: "finanzas", name: "Finanzas", color: "sky" },
];

export const DEFAULT_PLANNER: PlannerSettings = {
  dayStart: "07:00",
  dayEnd: "21:00",
  focusStart: "08:00",
  focusEnd: "12:00",
  bufferMin: 10,
  defaultTaskMin: 45,
  pomodoroMin: 25,
  breakMin: 5,
};

/** Suggested starting template; the user edits or replaces it. */
export const SUGGESTED_TEMPLATE: DayTemplate = {
  id: "sugerida",
  name: "Día de trabajo",
  blocks: [
    { title: "Planificar el día", start: "07:30", end: "07:45", category: "personal" },
    { title: "Trabajo profundo", start: "08:00", end: "10:00", category: "trabajo" },
    { title: "Descanso", start: "10:00", end: "10:15", category: "personal" },
    { title: "Correos y mensajes", start: "10:15", end: "10:45", category: "trabajo" },
    { title: "Trabajo profundo", start: "10:45", end: "12:30", category: "trabajo" },
    { title: "Almuerzo", start: "12:30", end: "13:30", category: "personal" },
    { title: "Clientes y reuniones", start: "14:00", end: "16:00", category: "clientes" },
    { title: "Tareas cortas", start: "16:00", end: "17:00", category: "trabajo" },
    { title: "Ejercicio", start: "18:00", end: "19:00", category: "salud" },
  ],
};

export function defaultSettings(): Settings {
  return {
    id: "app",
    userName: "",
    currency: "COP",
    locale: "es-CO",
    timeZone: DEFAULT_TIME_ZONE,
    weekStartsOn: 1,
    theme: "system",
    onboardingCompleted: false,
    safetyReserve: 0,
    leisureShare: 30,
    horizonMode: "nextIncome",
    horizonDays: 30,
    includeConfirmedIncome: false,
    reserveSavingsGoals: true,
    availableHoursPerDay: 8,
    notifications: {
      obligations: true,
      budgets: true,
      jobs: true,
      collections: true,
      tasks: true,
      obligationLeadDays: 3,
    },
    taskCategories: DEFAULT_TASK_CATEGORIES,
    planner: DEFAULT_PLANNER,
    dayTemplates: [],
    updatedAt: nowISO(),
  };
}

type CatSeed = [name: string, icon: string, color: string, systemKey: string, nature?: ExpenseNature];

const EXPENSE_CATEGORIES: CatSeed[] = [
  ["Alimentación", "utensils", "amber", "food", "variable"],
  ["Vivienda", "home", "iris", "housing", "fixed"],
  ["Servicios públicos", "zap", "sky", "utilities", "fixed"],
  ["Transporte", "bus", "teal", "transport", "variable"],
  ["Salud", "heart-pulse", "rose", "health", "variable"],
  ["Educación", "graduation-cap", "violet", "education", "fixed"],
  ["Suscripciones", "repeat", "pink", "subscriptions", "fixed"],
  ["Deudas", "landmark", "slate", "debts", "fixed"],
  ["Compras personales", "shopping-bag", "orange", "shopping", "discretionary"],
  ["Ocio y entretenimiento", "popcorn", "emerald", "leisure", "discretionary"],
  ["Imprevistos", "siren", "rose", "unexpected", "variable"],
  ["Otros", "circle-dashed", "slate", "other-expense", "variable"],
];

const INCOME_CATEGORIES: CatSeed[] = [
  ["Clientes", "briefcase", "emerald", "clients"],
  ["Salario", "wallet", "iris", "salary"],
  ["Ventas", "store", "amber", "sales"],
  ["Trabajos adicionales", "hammer", "teal", "side-jobs"],
  ["Otros ingresos", "circle-plus", "slate", "other-income"],
];

export function defaultCategories(): Category[] {
  const now = nowISO();
  const make = (seed: CatSeed, kind: "expense" | "income", order: number): Category => ({
    id: uid(),
    name: seed[0],
    icon: seed[1],
    color: seed[2],
    systemKey: seed[3],
    nature: seed[4],
    kind,
    archived: false,
    order,
    createdAt: now,
    updatedAt: now,
  });
  return [
    ...EXPENSE_CATEGORIES.map((s, i) => make(s, "expense", i)),
    ...INCOME_CATEGORIES.map((s, i) => make(s, "income", i)),
  ];
}

export function defaultJobStatuses(): JobStatus[] {
  const rows: Array<[string, JobStatus["kind"], string]> = [
    ["Nuevo", "new", "slate"],
    ["Pendiente de iniciar", "todo", "amber"],
    ["En proceso", "doing", "iris"],
    ["En revisión", "review", "violet"],
    ["Terminado", "done", "teal"],
    ["Entregado", "delivered", "emerald"],
    ["Cancelado", "cancelled", "rose"],
  ];
  return rows.map(([name, kind, color], order) => ({ id: uid(), name, kind, color, order }));
}

/** Makes sure a fresh database has settings, categories and job statuses. Idempotent. */
export async function ensureDefaults(database: LifeOSDB): Promise<void> {
  await database.transaction("rw", [database.settings, database.categories, database.jobStatuses], async () => {
    const settings = await database.settings.get("app");
    if (!settings) await database.settings.put(defaultSettings());
    if ((await database.categories.count()) === 0) await database.categories.bulkPut(defaultCategories());
    if ((await database.jobStatuses.count()) === 0) await database.jobStatuses.bulkPut(defaultJobStatuses());
  });
}
