import { nowISO, DEFAULT_TIME_ZONE } from "@/lib/dates";
import { uid } from "@/lib/utils";
import type { LifeOSDB } from "./db";
import type { Category, ExpenseNature, JobStatus, Settings } from "./types";

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
