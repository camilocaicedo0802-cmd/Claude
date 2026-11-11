import type { DateStr, TimeStr } from "@/lib/dates";
import type { Minor } from "@/lib/money";
import type { Recurrence } from "@/lib/recurrence";

export type ID = string;

export interface Timestamps {
  createdAt: string;
  updatedAt: string;
}

// ── Settings ─────────────────────────────────────────────────────────────────

export type ThemePref = "system" | "light" | "dark";
export type HorizonMode = "nextIncome" | "endOfMonth" | "days";

export interface NotificationPrefs {
  obligations: boolean;
  budgets: boolean;
  jobs: boolean;
  collections: boolean;
  tasks: boolean;
  /** Days before due date to start warning about obligations. */
  obligationLeadDays: number;
}

export interface Settings {
  id: "app";
  userName: string;
  currency: string;
  locale: string;
  timeZone: string;
  weekStartsOn: 0 | 1;
  theme: ThemePref;
  onboardingCompleted: boolean;
  /** Money that the spend engine never treats as available (colchón mínimo). */
  safetyReserve: Minor;
  /** Share of the free margin suggested for leisure when no leisure budget exists. */
  leisureShare: number;
  horizonMode: HorizonMode;
  horizonDays: number;
  /** Count confirmed future income inside the horizon (off by default: conservative). */
  includeConfirmedIncome: boolean;
  /** Reserve planned monthly contributions to savings goals. */
  reserveSavingsGoals: boolean;
  /** Hours per day the user considers available for planned work. */
  availableHoursPerDay: number;
  notifications: NotificationPrefs;
  updatedAt: string;
}

// ── Finance ──────────────────────────────────────────────────────────────────

export type AccountType = "cash" | "bank" | "wallet" | "savings" | "credit" | "other";

export interface Account extends Timestamps {
  id: ID;
  name: string;
  type: AccountType;
  /** Balance at `openingDate`. For credit cards, a negative number is the debt. */
  openingBalance: Minor;
  openingDate: DateStr;
  /** Credit cards only. Never counted as money. */
  creditLimit?: Minor | null;
  /** Whether this money can be spent day to day (savings accounts default to false). */
  spendable: boolean;
  color: string;
  archived: boolean;
  order: number;
}

export type CategoryKind = "expense" | "income";
export type ExpenseNature = "fixed" | "variable" | "discretionary";

export interface Category extends Timestamps {
  id: ID;
  name: string;
  kind: CategoryKind;
  /** Expense categories only. fixed + variable = essential; discretionary = optional. */
  nature?: ExpenseNature;
  icon: string;
  color: string;
  /** Stable key for built-in categories the app links automatically (e.g. "clients", "leisure"). */
  systemKey?: string;
  archived: boolean;
  order: number;
}

export type TransactionKind = "income" | "expense" | "transfer";

export interface Transaction extends Timestamps {
  id: ID;
  kind: TransactionKind;
  /** Always positive. Direction comes from `kind`. */
  amount: Minor;
  date: DateStr;
  time?: TimeStr | null;
  accountId: ID;
  /** Transfers only. */
  toAccountId?: ID | null;
  categoryId?: ID | null;
  description?: string;
  clientId?: ID | null;
  jobId?: ID | null;
  /** Set when this income is the money side of a client payment (1:1). */
  clientPaymentId?: ID | null;
  /** Set when this movement pays an occurrence of an obligation. */
  obligationId?: ID | null;
  /** Set when this income is the receipt of a planned income occurrence. */
  plannedIncomeId?: ID | null;
  /** Due date of the obligation / planned income occurrence this movement settles. */
  occurrenceDate?: DateStr | null;
  recurring?: boolean;
}

export interface Budget extends Timestamps {
  id: ID;
  categoryId: ID;
  /** Monthly limit. */
  amount: Minor;
}

export type ObligationType =
  | "rent"
  | "utilities"
  | "loan"
  | "card"
  | "subscription"
  | "installment"
  | "supplier"
  | "tax"
  | "other";

export type OccurrenceSettlement = "skipped" | "paid-outside";

export interface Obligation extends Timestamps {
  id: ID;
  name: string;
  type: ObligationType;
  /** Amount due per occurrence. */
  amount: Minor;
  /** First due date (anchor of the series). */
  startDate: DateStr;
  recurrence: Recurrence | null;
  accountId?: ID | null;
  /** For card payments: the credit card account being paid (payment becomes a transfer). */
  cardAccountId?: ID | null;
  categoryId?: ID | null;
  notes?: string;
  active: boolean;
  /** Occurrences settled without a movement (paid before using the app, or skipped this time). */
  settled: Record<DateStr, OccurrenceSettlement>;
}

export interface PlannedIncome extends Timestamps {
  id: ID;
  name: string;
  amount: Minor;
  startDate: DateStr;
  recurrence: Recurrence | null;
  /** Confirmed (salary, signed contract) vs uncertain. */
  confirmed: boolean;
  accountId?: ID | null;
  categoryId?: ID | null;
  notes?: string;
  active: boolean;
  settled: Record<DateStr, OccurrenceSettlement>;
}

export interface SavingsGoal extends Timestamps {
  id: ID;
  name: string;
  target: Minor;
  targetDate?: DateStr | null;
  isEmergencyFund: boolean;
  /** Where the money is kept. If that account is not spendable, it is already protected. */
  accountId?: ID | null;
  color: string;
  archived: boolean;
}

export interface GoalContribution extends Timestamps {
  id: ID;
  goalId: ID;
  /** Positive = set aside; negative = withdrawn. */
  amount: Minor;
  date: DateStr;
  note?: string;
}

// ── Clients ──────────────────────────────────────────────────────────────────

export type ClientStatus = "lead" | "active" | "paused" | "inactive";

export interface Client extends Timestamps {
  id: ID;
  name: string;
  company?: string;
  phone?: string;
  whatsapp?: string;
  email?: string;
  serviceType?: string;
  status: ClientStatus;
  tags: string[];
  notes?: string;
  archived: boolean;
}

export type JobStatusKind = "new" | "todo" | "doing" | "review" | "done" | "delivered" | "cancelled";

export interface JobStatus {
  id: ID;
  name: string;
  kind: JobStatusKind;
  order: number;
  color: string;
}

export type Priority = "low" | "medium" | "high" | "urgent";

export interface Job extends Timestamps {
  id: ID;
  clientId: ID;
  title: string;
  description?: string;
  requestedAt: DateStr;
  dueDate?: DateStr | null;
  price: Minor;
  priority: Priority;
  statusId: ID;
  /** When the remaining balance should be collected. */
  paymentDueDate?: DateStr | null;
  notes?: string;
  tags: string[];
  archived: boolean;
  statusChangedAt: string;
}

export type ClientPaymentKind = "advance" | "partial" | "final";

export interface ClientPayment extends Timestamps {
  id: ID;
  clientId: ID;
  jobId: ID;
  amount: Minor;
  date: DateStr;
  kind: ClientPaymentKind;
  /** Receiving account. When set, the payment has exactly one linked income transaction. */
  accountId?: ID | null;
  transactionId?: ID | null;
  note?: string;
}

export interface JobTemplate extends Timestamps {
  id: ID;
  name: string;
  description?: string;
  price: Minor;
  durationDays?: number | null;
  priority: Priority;
}

export interface Activity {
  id: ID;
  at: string;
  clientId?: ID | null;
  jobId?: ID | null;
  type: "client" | "job" | "status" | "payment" | "note" | "task";
  message: string;
}

// ── Life ─────────────────────────────────────────────────────────────────────

export type TaskPriority = 0 | 1 | 2 | 3; // none, low, medium, high
export type TaskStatus = "todo" | "done";
export type LifeArea = "personal" | "trabajo" | "clientes" | "salud" | "hogar" | "estudio" | "finanzas";
export type FollowUpType = "collect" | "proposal" | "info" | "deliver" | "contact" | "review";

export interface Subtask {
  id: ID;
  title: string;
  done: boolean;
}

export interface Task extends Timestamps {
  id: ID;
  title: string;
  description?: string;
  /** null = captured without a date (bandeja de entrada). */
  date?: DateStr | null;
  time?: TimeStr | null;
  durationMin?: number | null;
  priority: TaskPriority;
  status: TaskStatus;
  completedAt?: string | null;
  area?: LifeArea | null;
  recurrence?: Recurrence | null;
  /** Instances of a recurring task share a seriesId. */
  seriesId?: ID | null;
  /** First date of the series: every instance computes the next one from this anchor. */
  seriesStart?: DateStr | null;
  clientId?: ID | null;
  jobId?: ID | null;
  /** Client follow-ups (recordatorios) are tasks with a follow-up type. */
  followUp?: FollowUpType | null;
  subtasks: Subtask[];
  notes?: string;
  /** Times it was postponed (signals procrastination). */
  postponed: number;
  order: number;
}

export interface DayPlan {
  date: DateStr;
  /** Up to three task ids chosen as the day's priorities. */
  priorities: ID[];
}

export type EventCategory = "personal" | "trabajo" | "clientes" | "salud" | "familia" | "estudio" | "otro";

export interface CalendarEvent extends Timestamps {
  id: ID;
  title: string;
  date: DateStr;
  startTime?: TimeStr | null;
  endTime?: TimeStr | null;
  allDay: boolean;
  recurrence?: Recurrence | null;
  category: EventCategory;
  location?: string;
  notes?: string;
  clientId?: ID | null;
  jobId?: ID | null;
  /** Occurrence dates removed from a recurring series. */
  exceptions: DateStr[];
}

export type HabitSchedule = { type: "daily" } | { type: "days"; days: number[] };

export interface Habit extends Timestamps {
  id: ID;
  name: string;
  icon: string;
  color: string;
  schedule: HabitSchedule;
  /** Times per day to count as done (e.g. 8 vasos de agua). */
  target: number;
  unit?: string;
  startDate: DateStr;
  archived: boolean;
  order: number;
}

export interface HabitLog {
  /** `${habitId}:${date}` — one row per habit per day, so logs cannot duplicate. */
  id: string;
  habitId: ID;
  date: DateStr;
  count: number;
  updatedAt: string;
}

export interface WeekPlan {
  weekStart: DateStr;
  priorities: string[];
  review: { completed: string; pending: string; next: string };
  reviewedAt?: string | null;
}

export interface AlertState {
  key: string;
  dismissedAt: string;
}
