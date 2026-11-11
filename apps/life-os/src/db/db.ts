import Dexie, { type Table } from "dexie";
import type {
  Account,
  Activity,
  AlertState,
  Budget,
  CalendarEvent,
  Category,
  Client,
  ClientPayment,
  DayPlan,
  GoalContribution,
  Habit,
  HabitLog,
  Job,
  JobStatus,
  JobTemplate,
  Obligation,
  PlannedIncome,
  SavingsGoal,
  Settings,
  Task,
  Transaction,
  WeekPlan,
} from "./types";

/**
 * Local-first persistence on IndexedDB. Every table uses string UUIDs as primary keys and
 * carries createdAt/updatedAt, so the same rows can later be pushed to a server database
 * (e.g. Supabase/PostgreSQL with Row Level Security) without remapping identifiers.
 */
export class LifeOSDB extends Dexie {
  settings!: Table<Settings, string>;
  accounts!: Table<Account, string>;
  categories!: Table<Category, string>;
  transactions!: Table<Transaction, string>;
  budgets!: Table<Budget, string>;
  obligations!: Table<Obligation, string>;
  plannedIncomes!: Table<PlannedIncome, string>;
  goals!: Table<SavingsGoal, string>;
  goalContributions!: Table<GoalContribution, string>;
  clients!: Table<Client, string>;
  jobs!: Table<Job, string>;
  jobStatuses!: Table<JobStatus, string>;
  jobTemplates!: Table<JobTemplate, string>;
  clientPayments!: Table<ClientPayment, string>;
  activities!: Table<Activity, string>;
  tasks!: Table<Task, string>;
  dayPlans!: Table<DayPlan, string>;
  events!: Table<CalendarEvent, string>;
  habits!: Table<Habit, string>;
  habitLogs!: Table<HabitLog, string>;
  weekPlans!: Table<WeekPlan, string>;
  alertState!: Table<AlertState, string>;

  constructor(name: string) {
    super(name);
    this.version(1).stores({
      settings: "id",
      accounts: "id, type, order",
      categories: "id, kind, systemKey, order",
      transactions:
        "id, date, kind, accountId, toAccountId, categoryId, clientId, jobId, clientPaymentId, obligationId, plannedIncomeId",
      budgets: "id, &categoryId",
      obligations: "id",
      plannedIncomes: "id",
      goals: "id",
      goalContributions: "id, goalId, date",
      clients: "id, name, status",
      jobs: "id, clientId, statusId, dueDate",
      jobStatuses: "id, order",
      jobTemplates: "id",
      clientPayments: "id, clientId, jobId, date, transactionId",
      activities: "id, at, clientId, jobId",
      tasks: "id, date, status, seriesId, clientId, jobId",
      dayPlans: "date",
      events: "id, date, clientId, jobId",
      habits: "id, order",
      habitLogs: "id, habitId, date",
      weekPlans: "weekStart",
      alertState: "key",
    });
  }
}

export const TABLE_NAMES = [
  "settings",
  "accounts",
  "categories",
  "transactions",
  "budgets",
  "obligations",
  "plannedIncomes",
  "goals",
  "goalContributions",
  "clients",
  "jobs",
  "jobStatuses",
  "jobTemplates",
  "clientPayments",
  "activities",
  "tasks",
  "dayPlans",
  "events",
  "habits",
  "habitLogs",
  "weekPlans",
  "alertState",
] as const;

export type TableName = (typeof TABLE_NAMES)[number];

export const REAL_DB_NAME = "lifeos";
export const DEMO_DB_NAME = "lifeos-demo";
export const MODE_STORAGE_KEY = "lifeos:mode";

export type DataMode = "real" | "demo";

export function readMode(): DataMode {
  if (typeof window === "undefined") return "real";
  try {
    return window.localStorage.getItem(MODE_STORAGE_KEY) === "demo" ? "demo" : "real";
  } catch {
    return "real";
  }
}

let instance: LifeOSDB | null = null;

/** The active database. Real and demo data live in separate IndexedDB databases. */
export function db(): LifeOSDB {
  if (!instance) {
    instance = new LifeOSDB(readMode() === "demo" ? DEMO_DB_NAME : REAL_DB_NAME);
  }
  return instance;
}

/** Test hook: swap the active database. */
export function setDB(next: LifeOSDB) {
  instance = next;
}
