"use client";

import * as React from "react";
import { useLiveQuery } from "dexie-react-hooks";
import { db } from "@/db/db";
import { defaultSettings, ensureDefaults } from "@/db/defaults";
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
} from "@/db/types";
import { buildJobViews, receivablesByDate, totalReceivables, type JobView } from "@/domain/clients";
import { budgetStatuses, computeSpendCapacity, pendingObligations, setEngineFormatter, type FinanceInput } from "@/domain/finance";
import { buildAlerts } from "@/domain/alerts";
import { addDays, todayIn, zonedNow } from "@/lib/dates";
import { formatMoney, type Minor } from "@/lib/money";

export interface AppData {
  settings: Settings;
  accounts: Account[];
  categories: Category[];
  transactions: Transaction[];
  budgets: Budget[];
  obligations: Obligation[];
  plannedIncomes: PlannedIncome[];
  goals: SavingsGoal[];
  contributions: GoalContribution[];
  clients: Client[];
  jobs: Job[];
  jobStatuses: JobStatus[];
  jobTemplates: JobTemplate[];
  clientPayments: ClientPayment[];
  activities: Activity[];
  tasks: Task[];
  dayPlans: DayPlan[];
  events: CalendarEvent[];
  habits: Habit[];
  habitLogs: HabitLog[];
  weekPlans: WeekPlan[];
  alertState: AlertState[];
}

const DataContext = React.createContext<AppData | null>(null);

export type DBStatus = "loading" | "ready" | "error";
const StatusContext = React.createContext<{ status: DBStatus; error: string | null }>({ status: "loading", error: null });

export function DataProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = React.useState<DBStatus>("loading");
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    ensureDefaults(db())
      .then(() => !cancelled && setStatus("ready"))
      .catch((e: unknown) => {
        if (cancelled) return;
        console.error(e);
        setError(e instanceof Error ? e.message : String(e));
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const core = useLiveQuery(
    async () => {
      if (status !== "ready") return undefined;
      const d = db();
      const [
        settings,
        accounts,
        categories,
        budgets,
        obligations,
        plannedIncomes,
        goals,
        contributions,
        clients,
        jobs,
        jobStatuses,
        jobTemplates,
        clientPayments,
        activities,
        tasks,
        dayPlans,
        events,
        habits,
        habitLogs,
        weekPlans,
        alertState,
      ] = await Promise.all([
        d.settings.get("app"),
        d.accounts.orderBy("order").toArray(),
        d.categories.orderBy("order").toArray(),
        d.budgets.toArray(),
        d.obligations.toArray(),
        d.plannedIncomes.toArray(),
        d.goals.toArray(),
        d.goalContributions.toArray(),
        d.clients.toArray(),
        d.jobs.toArray(),
        d.jobStatuses.orderBy("order").toArray(),
        d.jobTemplates.toArray(),
        d.clientPayments.toArray(),
        d.activities.orderBy("at").reverse().limit(400).toArray(),
        d.tasks.toArray(),
        d.dayPlans.toArray(),
        d.events.toArray(),
        d.habits.orderBy("order").toArray(),
        d.habitLogs.toArray(),
        d.weekPlans.toArray(),
        d.alertState.toArray(),
      ]);
      return {
        settings: { ...defaultSettings(), ...settings, notifications: { ...defaultSettings().notifications, ...settings?.notifications } },
        accounts,
        categories,
        budgets,
        obligations,
        plannedIncomes,
        goals,
        contributions,
        clients,
        jobs,
        jobStatuses,
        jobTemplates,
        clientPayments,
        activities,
        tasks,
        dayPlans,
        events,
        habits,
        habitLogs,
        weekPlans,
        alertState,
      };
    },
    [status],
  );

  const transactions = useLiveQuery(async () => (status === "ready" ? db().transactions.toArray() : undefined), [status]);

  const value = React.useMemo<AppData | null>(() => {
    if (!core || !transactions) return null;
    return { ...core, transactions };
  }, [core, transactions]);

  // Engine sentences use the configured currency. Set before children compute (idempotent).
  const currency = value?.settings.currency ?? "COP";
  React.useMemo(() => setEngineFormatter((m) => formatMoney(m, { currency })), [currency]);

  return (
    <StatusContext.Provider value={{ status: status === "ready" && !value ? "loading" : status, error }}>
      <DataContext.Provider value={value}>{children}</DataContext.Provider>
    </StatusContext.Provider>
  );
}

export function useDBStatus() {
  return React.useContext(StatusContext);
}

export function useMaybeData(): AppData | null {
  return React.useContext(DataContext);
}

/** Data for screens rendered inside the ready shell. */
export function useData(): AppData {
  const data = React.useContext(DataContext);
  if (!data) throw new Error("useData() used before the database is ready");
  return data;
}

// ── Time ─────────────────────────────────────────────────────────────────────

export function useNow() {
  const data = useMaybeData();
  const tz = data?.settings.timeZone;
  const [now, setNow] = React.useState(() => zonedNow(tz));
  React.useEffect(() => {
    setNow(zonedNow(tz));
    const id = window.setInterval(() => setNow(zonedNow(tz)), 30_000);
    const onVisible = () => document.visibilityState === "visible" && setNow(zonedNow(tz));
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.clearInterval(id);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [tz]);
  return now;
}

export function useToday() {
  return useNow().date;
}

export function todayFor(data: AppData) {
  return todayIn(data.settings.timeZone);
}

// ── Money ────────────────────────────────────────────────────────────────────

export function useMoney() {
  const data = useMaybeData();
  const currency = data?.settings.currency ?? "COP";
  return React.useCallback(
    (amount: Minor, opts: { compact?: boolean; signed?: boolean } = {}) => formatMoney(amount, { currency, ...opts }),
    [currency],
  );
}

// ── Derived data ─────────────────────────────────────────────────────────────

export function useJobViews(): JobView[] {
  const data = useData();
  const today = useToday();
  return React.useMemo(
    () => buildJobViews(data.jobs, data.clients, data.jobStatuses, data.clientPayments, today),
    [data.jobs, data.clients, data.jobStatuses, data.clientPayments, today],
  );
}

export function useFinanceInput(): FinanceInput {
  const data = useData();
  const today = useToday();
  const views = useJobViews();
  return React.useMemo(
    () => ({
      today,
      settings: data.settings,
      accounts: data.accounts,
      categories: data.categories,
      transactions: data.transactions,
      budgets: data.budgets,
      obligations: data.obligations,
      plannedIncomes: data.plannedIncomes,
      goals: data.goals,
      contributions: data.contributions,
      receivables: totalReceivables(views),
    }),
    [data, today, views],
  );
}

export function useCapacity() {
  const input = useFinanceInput();
  return React.useMemo(() => computeSpendCapacity(input), [input]);
}

export function useReceivablesByDate() {
  const views = useJobViews();
  const today = useToday();
  return React.useMemo(() => receivablesByDate(views, today), [views, today]);
}

export function useAlerts() {
  const data = useData();
  const today = useToday();
  const views = useJobViews();
  const capacity = useCapacity();
  const money = useMoney();
  return React.useMemo(() => {
    const obligations = pendingObligations(data.obligations, data.transactions, addDays(today, 14), today);
    const budgets = budgetStatuses(data.budgets, data.categories, data.transactions, today, today);
    const all = buildAlerts({
      today,
      prefs: data.settings.notifications,
      obligations,
      budgets,
      jobViews: views,
      tasks: data.tasks,
      capacity,
      format: money,
    });
    const dismissed = new Set(data.alertState.map((a) => a.key));
    return { all, unread: all.filter((a) => !dismissed.has(a.key)) };
  }, [data, today, views, capacity, money]);
}

export function useCategoryMap() {
  const data = useData();
  return React.useMemo(() => new Map(data.categories.map((c) => [c.id, c])), [data.categories]);
}

export function useAccountMap() {
  const data = useData();
  return React.useMemo(() => new Map(data.accounts.map((a) => [a.id, a])), [data.accounts]);
}
