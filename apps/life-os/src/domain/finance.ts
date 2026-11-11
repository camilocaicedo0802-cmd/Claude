/**
 * Pure financial calculations. Nothing here touches the database: every function takes
 * plain rows and returns plain values, so the rules can be unit-tested in isolation.
 *
 * Rules enforced here:
 * - Transfers move money between accounts; they are never income or expense.
 * - Credit card limits are never money. A card's negative balance is debt.
 * - Future obligations are not subtracted from the real balance until paid; they only
 *   reduce the projected free balance.
 * - Money owed by clients is a receivable, never liquid balance.
 */
import {
  addDays,
  daysInMonth,
  diffDays,
  endOfMonth,
  endOfWeek,
  formatDayMonth,
  minDate,
  startOfMonth,
  type DateStr,
} from "@/lib/dates";
import { divideFloor, prorate, sumMinor, type Minor } from "@/lib/money";
import { occurrencesBetween } from "@/lib/recurrence";
import type {
  Account,
  Budget,
  Category,
  GoalContribution,
  Obligation,
  OccurrenceSettlement,
  PlannedIncome,
  SavingsGoal,
  Settings,
  Transaction,
} from "@/db/types";

// ── Balances ─────────────────────────────────────────────────────────────────

export function accountBalances(accounts: Account[], transactions: Transaction[]): Map<string, Minor> {
  const map = new Map<string, Minor>();
  for (const a of accounts) map.set(a.id, a.openingBalance);
  for (const t of transactions) {
    if (t.kind === "income") {
      map.set(t.accountId, (map.get(t.accountId) ?? 0) + t.amount);
    } else if (t.kind === "expense") {
      map.set(t.accountId, (map.get(t.accountId) ?? 0) - t.amount);
    } else if (t.kind === "transfer") {
      map.set(t.accountId, (map.get(t.accountId) ?? 0) - t.amount);
      if (t.toAccountId) map.set(t.toAccountId, (map.get(t.toAccountId) ?? 0) + t.amount);
    }
  }
  return map;
}

export interface BalanceSummary {
  /** All cash, bank, wallet, savings and other accounts (never credit). */
  liquid: Minor;
  /** Liquid money marked as spendable day to day. */
  spendable: Minor;
  /** Liquid money kept apart (savings accounts by default). */
  protectedSavings: Minor;
  /** Total owed on credit cards. */
  creditDebt: Minor;
  /** Unused credit limit: shown for reference, never counted as money. */
  creditAvailable: Minor;
  byAccount: Map<string, Minor>;
}

export function summarizeBalances(accounts: Account[], transactions: Transaction[]): BalanceSummary {
  const byAccount = accountBalances(accounts, transactions);
  let liquid = 0;
  let spendable = 0;
  let protectedSavings = 0;
  let creditDebt = 0;
  let creditAvailable = 0;
  for (const a of accounts) {
    if (a.archived) continue;
    const bal = byAccount.get(a.id) ?? 0;
    if (a.type === "credit") {
      const debt = Math.max(0, -bal);
      creditDebt += debt;
      if (a.creditLimit) creditAvailable += Math.max(0, a.creditLimit - debt);
      continue;
    }
    liquid += bal;
    if (a.spendable) spendable += bal;
    else protectedSavings += bal;
  }
  return { liquid, spendable, protectedSavings, creditDebt, creditAvailable, byAccount };
}

// ── Period totals ────────────────────────────────────────────────────────────

export function inPeriod(t: { date: DateStr }, from: DateStr, to: DateStr) {
  return t.date >= from && t.date <= to;
}

export function periodTotals(transactions: Transaction[], from: DateStr, to: DateStr) {
  let income = 0;
  let expense = 0;
  for (const t of transactions) {
    if (!inPeriod(t, from, to)) continue;
    if (t.kind === "income") income += t.amount;
    else if (t.kind === "expense") expense += t.amount;
  }
  return { income, expense, net: income - expense };
}

export function expensesByCategory(transactions: Transaction[], from: DateStr, to: DateStr): Map<string, Minor> {
  const map = new Map<string, Minor>();
  for (const t of transactions) {
    if (t.kind !== "expense" || !inPeriod(t, from, to)) continue;
    const key = t.categoryId ?? "uncategorized";
    map.set(key, (map.get(key) ?? 0) + t.amount);
  }
  return map;
}

export function dailyExpenses(transactions: Transaction[], from: DateStr, to: DateStr): Map<DateStr, Minor> {
  const map = new Map<DateStr, Minor>();
  for (const t of transactions) {
    if (t.kind !== "expense" || !inPeriod(t, from, to)) continue;
    map.set(t.date, (map.get(t.date) ?? 0) + t.amount);
  }
  return map;
}

export function isEssential(category: Category | undefined): boolean {
  return !!category && category.kind === "expense" && category.nature !== "discretionary";
}

export function isDiscretionary(category: Category | undefined): boolean {
  // Uncategorised spending is treated as discretionary: the conservative choice.
  return !category || category.nature === "discretionary";
}

// ── Scheduled items: obligations and planned income ─────────────────────────

export type OccurrenceStatus = "paid" | "partial" | "pending" | "overdue" | "settled";

export interface Occurrence<T> {
  key: string;
  source: T;
  dueDate: DateStr;
  amount: Minor;
  paid: Minor;
  remaining: Minor;
  status: OccurrenceStatus;
  settlement?: OccurrenceSettlement;
  movements: Transaction[];
}

function settle<T extends { id: string; amount: Minor; settled: Record<DateStr, OccurrenceSettlement> }>(
  source: T,
  dueDate: DateStr,
  movements: Transaction[],
  today: DateStr,
): Occurrence<T> {
  const paid = sumMinor(movements.map((m) => m.amount));
  const settlement = source.settled?.[dueDate];
  const remaining = settlement ? 0 : Math.max(0, source.amount - paid);
  let status: OccurrenceStatus;
  if (settlement) status = "settled";
  else if (remaining === 0) status = "paid";
  else if (dueDate < today) status = "overdue";
  else if (paid > 0) status = "partial";
  else status = "pending";
  return { key: `${source.id}:${dueDate}`, source, dueDate, amount: source.amount, paid, remaining, status, settlement, movements };
}

function linkedMovements(transactions: Transaction[], field: "obligationId" | "plannedIncomeId") {
  const map = new Map<string, Transaction[]>();
  for (const t of transactions) {
    const id = t[field];
    if (!id || !t.occurrenceDate) continue;
    const key = `${id}:${t.occurrenceDate}`;
    const list = map.get(key);
    if (list) list.push(t);
    else map.set(key, [t]);
  }
  return map;
}

/**
 * Every occurrence of every active obligation due in [from, to]. Occurrences are virtual:
 * a recurring obligation is one row, and payments point at (obligationId, dueDate), so
 * recurring obligations can never duplicate.
 */
export function obligationOccurrences(
  obligations: Obligation[],
  transactions: Transaction[],
  from: DateStr,
  to: DateStr,
  today: DateStr,
  options: { includeInactive?: boolean } = {},
): Occurrence<Obligation>[] {
  const payments = linkedMovements(transactions, "obligationId");
  const out: Occurrence<Obligation>[] = [];
  for (const o of obligations) {
    if (!o.active && !options.includeInactive) continue;
    for (const d of occurrencesBetween(o.startDate, o.recurrence, from, to)) {
      out.push(settle(o, d, payments.get(`${o.id}:${d}`) ?? [], today));
    }
  }
  return out.sort((a, b) => a.dueDate.localeCompare(b.dueDate) || a.source.name.localeCompare(b.source.name));
}

/** Unpaid occurrences due on or before `to`, including overdue ones from the past. */
export function pendingObligations(obligations: Obligation[], transactions: Transaction[], to: DateStr, today: DateStr) {
  const earliest = obligations.reduce<DateStr>((min, o) => (o.startDate < min ? o.startDate : min), to);
  return obligationOccurrences(obligations, transactions, earliest, to, today).filter((o) => o.remaining > 0);
}

export function plannedIncomeOccurrences(
  incomes: PlannedIncome[],
  transactions: Transaction[],
  from: DateStr,
  to: DateStr,
  today: DateStr,
): Occurrence<PlannedIncome>[] {
  const receipts = linkedMovements(transactions, "plannedIncomeId");
  const out: Occurrence<PlannedIncome>[] = [];
  for (const p of incomes) {
    if (!p.active) continue;
    for (const d of occurrencesBetween(p.startDate, p.recurrence, from, to)) {
      out.push(settle(p, d, receipts.get(`${p.id}:${d}`) ?? [], today));
    }
  }
  return out.sort((a, b) => a.dueDate.localeCompare(b.dueDate));
}

// ── Budgets ──────────────────────────────────────────────────────────────────

export type BudgetState = "ok" | "near" | "over";

export interface BudgetStatus {
  budget: Budget;
  category: Category | undefined;
  spent: Minor;
  remaining: Minor;
  percent: number;
  state: BudgetState;
  /** Spending pace: what the month would end at if the current daily rate continues. */
  projected: Minor;
}

export function budgetStatuses(
  budgets: Budget[],
  categories: Category[],
  transactions: Transaction[],
  monthAnchor: DateStr,
  today: DateStr,
): BudgetStatus[] {
  const from = startOfMonth(monthAnchor);
  const to = endOfMonth(monthAnchor);
  const spentBy = expensesByCategory(transactions, from, to);
  const catById = new Map(categories.map((c) => [c.id, c]));
  const isCurrent = today >= from && today <= to;
  const elapsed = isCurrent ? diffDays(from, today) + 1 : daysInMonth(from);
  const total = daysInMonth(from);
  return budgets
    .map((b) => {
      const spent = spentBy.get(b.categoryId) ?? 0;
      const percent = b.amount > 0 ? (spent / b.amount) * 100 : spent > 0 ? 100 : 0;
      const state: BudgetState = percent >= 100 ? "over" : percent >= 80 ? "near" : "ok";
      return {
        budget: b,
        category: catById.get(b.categoryId),
        spent,
        remaining: b.amount - spent,
        percent,
        state,
        projected: elapsed > 0 ? prorate(spent, total, elapsed) : spent,
      };
    })
    .sort((a, b) => b.percent - a.percent);
}

// ── Savings goals ────────────────────────────────────────────────────────────

export function goalProgress(goal: SavingsGoal, contributions: GoalContribution[]) {
  const saved = sumMinor(contributions.filter((c) => c.goalId === goal.id).map((c) => c.amount));
  const remaining = Math.max(0, goal.target - saved);
  return { saved, remaining, percent: goal.target > 0 ? Math.min(100, (saved / goal.target) * 100) : 0 };
}

/** Monthly contribution needed to reach the goal on time (null without a target date). */
export function monthlyNeeded(goal: SavingsGoal, saved: Minor, today: DateStr): Minor | null {
  if (!goal.targetDate || goal.targetDate <= today) return null;
  const remaining = Math.max(0, goal.target - saved);
  const months = Math.max(1, diffDays(today, goal.targetDate) / 30.44);
  return Math.ceil(remaining / months);
}

// ── Spend capacity engine ("¿Cuánto puedo gastar?") ──────────────────────────

export interface FinanceInput {
  today: DateStr;
  settings: Pick<
    Settings,
    | "safetyReserve"
    | "leisureShare"
    | "horizonMode"
    | "horizonDays"
    | "includeConfirmedIncome"
    | "reserveSavingsGoals"
    | "weekStartsOn"
  >;
  accounts: Account[];
  categories: Category[];
  transactions: Transaction[];
  budgets: Budget[];
  obligations: Obligation[];
  plannedIncomes: PlannedIncome[];
  goals: SavingsGoal[];
  contributions: GoalContribution[];
  /** Money clients still owe (receivables). Informative only. */
  receivables: Minor;
}

export interface EssentialLine {
  categoryId: string;
  name: string;
  amount: Minor;
  method: "budget" | "history";
}

export interface SpendCapacity {
  status: "no-accounts" | "ok" | "tight" | "negative";
  today: DateStr;
  horizon: {
    end: DateStr;
    days: number;
    reason: "nextIncome" | "endOfMonth" | "days";
    fallback: boolean;
    nextIncome: { name: string; date: DateStr; amount: Minor } | null;
  };
  balances: BalanceSummary;
  /** Liquid money in all accounts (saldo real). */
  realBalance: Minor;
  /** Money the engine starts from (spendable accounts). */
  startingBalance: Minor;
  obligations: { total: Minor; items: Occurrence<Obligation>[]; overdue: Minor };
  essentials: { total: Minor; lines: EssentialLine[]; method: "budget" | "history" | "mixed" | "none"; historyDays: number };
  reserves: { safety: Minor; goalsSetAside: Minor; goalsPlanned: Minor; total: Minor };
  /** Sum of everything reserved: saldo comprometido. */
  committed: Minor;
  income: { confirmed: Minor; confirmedIncluded: boolean; uncertain: Minor; receivables: Minor };
  /** Saldo libre proyectado al final del horizonte. */
  free: Minor;
  dailyAllowance: Minor;
  todaySpentDiscretionary: Minor;
  availableToday: Minor;
  week: { available: Minor; days: number };
  leisure: { available: Minor; method: "budget" | "share"; budgetRemaining: Minor | null; share: number };
  monthEnd: { date: DateStr; projected: Minor };
  summary: string;
  notes: string[];
  warnings: string[];
  missing: string[];
}

function chooseHorizon(input: FinanceInput) {
  const { today, settings } = input;
  const monthEnd = endOfMonth(today);
  const upcoming = plannedIncomeOccurrences(
    input.plannedIncomes.filter((p) => p.confirmed),
    input.transactions,
    addDays(today, 1),
    addDays(today, 62),
    today,
  ).filter((o) => o.remaining > 0);
  const next = upcoming[0];
  const nextIncome = next ? { name: next.source.name, date: next.dueDate, amount: next.remaining } : null;

  if (settings.horizonMode === "days") {
    const days = Math.max(1, Math.min(120, Math.round(settings.horizonDays || 30)));
    return { end: addDays(today, days - 1), reason: "days" as const, fallback: false, nextIncome };
  }
  if (settings.horizonMode === "nextIncome") {
    if (nextIncome) {
      return { end: addDays(nextIncome.date, -1), reason: "nextIncome" as const, fallback: false, nextIncome };
    }
    return { end: monthEnd, reason: "endOfMonth" as const, fallback: true, nextIncome };
  }
  return { end: monthEnd, reason: "endOfMonth" as const, fallback: false, nextIncome };
}

/** Budget amount for a category prorated over [from, to], spanning month boundaries. */
function budgetNeedInRange(budget: Minor, spentThisMonth: Minor, today: DateStr, end: DateStr): Minor {
  let total = 0;
  const monthEnd = endOfMonth(today);
  // Current month: what is left of the budget, spread over the days left in the month.
  const remainingThisMonth = Math.max(0, budget - spentThisMonth);
  const daysLeftInMonth = diffDays(today, monthEnd) + 1;
  const coveredThisMonth = diffDays(today, minDate(end, monthEnd)) + 1;
  total += prorate(remainingThisMonth, coveredThisMonth, daysLeftInMonth);
  // Following months: full budget, prorated by the days the horizon covers.
  let cursor = addDays(monthEnd, 1);
  while (cursor <= end) {
    const mEnd = endOfMonth(cursor);
    const covered = diffDays(cursor, minDate(end, mEnd)) + 1;
    total += prorate(budget, covered, daysInMonth(cursor));
    cursor = addDays(mEnd, 1);
  }
  return total;
}

export function computeSpendCapacity(input: FinanceInput): SpendCapacity {
  const { today, settings, categories, transactions } = input;
  const notes: string[] = [];
  const warnings: string[] = [];
  const missing: string[] = [];

  const balances = summarizeBalances(input.accounts, transactions);
  const liquidAccounts = input.accounts.filter((a) => !a.archived && a.type !== "credit");
  const horizonInfo = chooseHorizon(input);
  const end = horizonInfo.end < today ? today : horizonInfo.end;
  const days = diffDays(today, end) + 1;
  const catById = new Map(categories.map((c) => [c.id, c]));

  // 1. Obligations due up to the end of the horizon (including overdue).
  const obligationItems = pendingObligations(input.obligations, transactions, end, today);
  const obligationsTotal = sumMinor(obligationItems.map((o) => o.remaining));
  const overdueTotal = sumMinor(obligationItems.filter((o) => o.status === "overdue").map((o) => o.remaining));

  // 2. Essential spending not already represented by obligations.
  const obligationCategories = new Set(input.obligations.filter((o) => o.active && o.categoryId).map((o) => o.categoryId!));
  const monthFrom = startOfMonth(today);
  const spentThisMonth = expensesByCategory(transactions, monthFrom, today);
  const budgetByCat = new Map(input.budgets.map((b) => [b.categoryId, b.amount]));
  const essentialCats = categories.filter(
    (c) => isEssential(c) && !c.archived && !(c.nature === "fixed" && obligationCategories.has(c.id)),
  );

  const expenseTxs = transactions.filter((t) => t.kind === "expense");
  const firstExpense = expenseTxs.reduce<DateStr | null>((min, t) => (!min || t.date < min ? t.date : min), null);
  const historyWindow = 30;
  const historyFrom = addDays(today, -historyWindow);
  const historyDays = firstExpense ? Math.min(historyWindow, Math.max(0, diffDays(maxDateStr(firstExpense, historyFrom), today))) : 0;
  const historyByCat = new Map<string, Minor>();
  for (const t of expenseTxs) {
    if (t.date < historyFrom || t.date >= today || !t.categoryId || t.obligationId) continue;
    historyByCat.set(t.categoryId, (historyByCat.get(t.categoryId) ?? 0) + t.amount);
  }

  const lines: EssentialLine[] = [];
  let usedBudget = false;
  let usedHistory = false;
  for (const c of essentialCats) {
    const budget = budgetByCat.get(c.id);
    if (budget !== undefined) {
      const amount = budgetNeedInRange(budget, spentThisMonth.get(c.id) ?? 0, today, end);
      if (amount > 0) lines.push({ categoryId: c.id, name: c.name, amount, method: "budget" });
      usedBudget = true;
    } else if (historyDays >= 7) {
      const spent = historyByCat.get(c.id) ?? 0;
      if (spent > 0 && c.nature !== "fixed") {
        const amount = prorate(spent, days, historyDays);
        lines.push({ categoryId: c.id, name: c.name, amount, method: "history" });
        usedHistory = true;
      }
    }
  }
  const essentialsTotal = sumMinor(lines.map((l) => l.amount));
  const essentialsMethod = usedBudget && usedHistory ? "mixed" : usedBudget ? "budget" : usedHistory ? "history" : "none";
  if (essentialsMethod === "none") {
    missing.push(
      historyDays < 7
        ? "Define presupuestos para tus gastos esenciales (alimentación, transporte…) o registra al menos una semana de gastos para estimarlos."
        : "No encontré gastos esenciales en tu historial reciente ni presupuestos para ellos; la reserva para esenciales es $0.",
    );
  } else if (usedHistory) {
    notes.push(`Los gastos esenciales sin presupuesto se estiman con tu promedio de los últimos ${historyDays} días.`);
  }

  // 3. Reserves: safety cushion and savings goals.
  const safety = Math.max(0, settings.safetyReserve || 0);
  const accountById = new Map(input.accounts.map((a) => [a.id, a]));
  let goalsSetAside = 0;
  let goalsPlanned = 0;
  for (const g of input.goals) {
    if (g.archived) continue;
    const { saved } = goalProgress(g, input.contributions);
    const acc = g.accountId ? accountById.get(g.accountId) : undefined;
    const moneyInSpendable = !acc || (acc.spendable && acc.type !== "credit");
    if (moneyInSpendable && saved > 0) goalsSetAside += saved;
    if (settings.reserveSavingsGoals) {
      const monthly = monthlyNeeded(g, saved, today);
      if (monthly) goalsPlanned += prorate(monthly, days, 30);
    }
  }
  const reservesTotal = safety + goalsSetAside + goalsPlanned;

  // 4. Income that has not arrived: never counted unless the user opts in (confirmed only).
  const incomesInHorizon = plannedIncomeOccurrences(input.plannedIncomes, transactions, addDays(today, 1), end, today);
  const confirmed = sumMinor(incomesInHorizon.filter((o) => o.source.confirmed).map((o) => o.remaining));
  const uncertainPlanned = sumMinor(
    plannedIncomeOccurrences(input.plannedIncomes, transactions, today, endOfMonth(addDays(today, 31)), today)
      .filter((o) => !o.source.confirmed)
      .map((o) => o.remaining),
  );
  const confirmedIncluded = settings.includeConfirmedIncome && confirmed > 0;

  const startingBalance = balances.spendable;
  const committed = obligationsTotal + essentialsTotal + reservesTotal;
  const free = startingBalance - committed + (confirmedIncluded ? confirmed : 0);

  // 5. Pace: daily allowance; what was already spent today on non-essentials counts against today.
  const todaySpentDiscretionary = sumMinor(
    expenseTxs.filter((t) => t.date === today && !t.obligationId && isDiscretionary(catById.get(t.categoryId ?? ""))).map((t) => t.amount),
  );
  const poolForPace = free + todaySpentDiscretionary;
  const dailyAllowance = poolForPace > 0 ? divideFloor(poolForPace, days) : 0;
  const availableToday = Math.max(0, Math.min(free, dailyAllowance - todaySpentDiscretionary));
  const weekEnd = minDate(endOfWeek(today, settings.weekStartsOn), end);
  const weekDays = diffDays(today, weekEnd) + 1;
  const weekAvailable = Math.max(0, Math.min(free, dailyAllowance * weekDays - todaySpentDiscretionary));

  // 6. Leisure: discretionary budgets if the user set them, otherwise a share of the free margin.
  const discretionaryBudgets = input.budgets.filter((b) => catById.get(b.categoryId)?.nature === "discretionary");
  let leisureAvailable: Minor;
  let leisureMethod: "budget" | "share";
  let budgetRemaining: Minor | null = null;
  if (discretionaryBudgets.length > 0) {
    budgetRemaining = sumMinor(discretionaryBudgets.map((b) => Math.max(0, b.amount - (spentThisMonth.get(b.categoryId) ?? 0))));
    leisureAvailable = Math.max(0, Math.min(budgetRemaining, free));
    leisureMethod = "budget";
  } else {
    leisureAvailable = free > 0 ? Math.floor((free * Math.max(0, Math.min(100, settings.leisureShare))) / 100) : 0;
    leisureMethod = "share";
  }

  // 7. Month-end projection (estimate).
  const monthEndDate = endOfMonth(today);
  const obligationsToMonthEnd = sumMinor(pendingObligations(input.obligations, transactions, monthEndDate, today).map((o) => o.remaining));
  const essentialsToMonthEnd =
    end === monthEndDate ? essentialsTotal : prorate(essentialsTotal, diffDays(today, monthEndDate) + 1, days);
  const confirmedToMonthEnd = sumMinor(
    plannedIncomeOccurrences(input.plannedIncomes, transactions, addDays(today, 1), monthEndDate, today)
      .filter((o) => o.source.confirmed)
      .map((o) => o.remaining),
  );
  const monthEndProjected = startingBalance - obligationsToMonthEnd - essentialsToMonthEnd + confirmedToMonthEnd;

  // 8. Status, warnings, explanation.
  let status: SpendCapacity["status"] = "ok";
  if (liquidAccounts.length === 0) {
    status = "no-accounts";
    missing.unshift("Registra al menos una cuenta (efectivo, banco o billetera) con su saldo actual.");
  } else if (free < 0) {
    status = "negative";
    warnings.push(
      `Te faltarían ${fmt(-free)} para cubrir lo comprometido hasta el ${formatDayMonth(end)}. Revisa obligaciones que puedas aplazar o reduce gastos no esenciales.`,
    );
  } else if (startingBalance > 0 && free < startingBalance * 0.1) {
    status = "tight";
  }
  if (overdueTotal > 0) warnings.push(`Tienes ${fmt(overdueTotal)} en obligaciones vencidas sin pagar.`);
  const coveredCards = new Set(input.obligations.filter((o) => o.active && o.type === "card" && o.cardAccountId).map((o) => o.cardAccountId!));
  const uncoveredDebt = sumMinor(
    input.accounts
      .filter((a) => a.type === "credit" && !a.archived && !coveredCards.has(a.id))
      .map((a) => Math.max(0, -(balances.byAccount.get(a.id) ?? 0))),
  );
  if (uncoveredDebt > 0) {
    warnings.push(`Debes ${fmt(uncoveredDebt)} en tarjetas de crédito sin un pago programado. Agrégalo como obligación para reservarlo.`);
  }
  if (horizonInfo.fallback) {
    notes.push("No tienes un ingreso confirmado registrado: el cálculo llega hasta fin de mes.");
  }
  if (input.receivables > 0) {
    notes.push(`Tus clientes te deben ${fmt(input.receivables)}; no se cuenta como disponible hasta que lo cobres.`);
  }
  if (confirmed > 0 && !confirmedIncluded) {
    notes.push(`Hay ${fmt(confirmed)} en ingresos confirmados dentro del período que no se suman hasta recibirlos.`);
  }

  const parts: string[] = [];
  if (obligationsTotal > 0) parts.push(`${fmt(obligationsTotal)} para obligaciones próximas`);
  if (essentialsTotal > 0) parts.push(`${fmt(essentialsTotal)} para gastos esenciales`);
  if (reservesTotal > 0) parts.push(`${fmt(reservesTotal)} para reservas y metas`);
  let summary: string;
  if (status === "no-accounts") {
    summary = "Aún no sé cuánto dinero tienes. Registra tus cuentas para calcular tu margen.";
  } else if (parts.length === 0) {
    summary = `Tienes ${fmt(startingBalance)} disponibles y nada comprometido hasta el ${formatDayMonth(end)}. Tu margen estimado es de ${fmt(free)}.`;
  } else {
    const joined = parts.length > 1 ? `${parts.slice(0, -1).join(", ")} y ${parts[parts.length - 1]}` : parts[0];
    summary =
      free >= 0
        ? `Tienes ${fmt(startingBalance)} disponibles, pero debes reservar ${joined}. Tu margen estimado para gastos adicionales es de ${fmt(free)}.`
        : `Tienes ${fmt(startingBalance)} disponibles, pero debes reservar ${joined}. Te faltan ${fmt(-free)}.`;
  }

  return {
    status,
    today,
    horizon: { end, days, reason: horizonInfo.reason, fallback: horizonInfo.fallback, nextIncome: horizonInfo.nextIncome },
    balances,
    realBalance: balances.liquid,
    startingBalance,
    obligations: { total: obligationsTotal, items: obligationItems, overdue: overdueTotal },
    essentials: { total: essentialsTotal, lines, method: essentialsMethod, historyDays },
    reserves: { safety, goalsSetAside, goalsPlanned, total: reservesTotal },
    committed,
    income: { confirmed, confirmedIncluded, uncertain: uncertainPlanned + input.receivables, receivables: input.receivables },
    free,
    dailyAllowance,
    todaySpentDiscretionary,
    availableToday: status === "no-accounts" ? 0 : availableToday,
    week: { available: status === "no-accounts" ? 0 : weekAvailable, days: weekDays },
    leisure: { available: status === "no-accounts" ? 0 : leisureAvailable, method: leisureMethod, budgetRemaining, share: settings.leisureShare },
    monthEnd: { date: monthEndDate, projected: monthEndProjected },
    summary,
    notes,
    warnings,
    missing,
  };
}

function maxDateStr(a: DateStr, b: DateStr) {
  return a >= b ? a : b;
}

/**
 * Plain amount formatter used inside engine sentences. The UI re-renders sentences with the
 * user's currency via `setEngineFormatter`.
 */
let engineFormatter: (m: Minor) => string = (m) =>
  `$${Math.round(m / 100)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ".")}`;

export function setEngineFormatter(f: (m: Minor) => string) {
  engineFormatter = f;
}

function fmt(m: Minor) {
  return engineFormatter(m);
}

// ── Cash-flow projection ─────────────────────────────────────────────────────

export interface CashflowPoint {
  date: DateStr;
  /** Conservative: only money you have, minus obligations and estimated essentials. */
  conservative: Minor;
  /** Adds confirmed planned income on its date. */
  withConfirmed: Minor;
  /** Adds uncertain income too (planned unconfirmed and client collections with due date). */
  optimistic: Minor;
  outflow: Minor;
  inflow: Minor;
}

export function cashflowProjection(
  input: FinanceInput,
  days: number,
  essentialsDaily: Minor,
  receivablesByDate: Map<DateStr, Minor> = new Map(),
): CashflowPoint[] {
  const { today, transactions } = input;
  const end = addDays(today, days - 1);
  const start = summarizeBalances(input.accounts, transactions).spendable;
  const pending = pendingObligations(input.obligations, transactions, end, today);
  const outByDate = new Map<DateStr, Minor>();
  for (const o of pending) {
    const d = o.dueDate < today ? today : o.dueDate;
    outByDate.set(d, (outByDate.get(d) ?? 0) + o.remaining);
  }
  const incomes = plannedIncomeOccurrences(input.plannedIncomes, transactions, addDays(today, 1), end, today).filter((o) => o.remaining > 0);
  const confirmedByDate = new Map<DateStr, Minor>();
  const uncertainByDate = new Map<DateStr, Minor>();
  for (const o of incomes) {
    const target = o.source.confirmed ? confirmedByDate : uncertainByDate;
    target.set(o.dueDate, (target.get(o.dueDate) ?? 0) + o.remaining);
  }
  const points: CashflowPoint[] = [];
  let conservative = start;
  let withConfirmed = start;
  let optimistic = start;
  for (let i = 0; i < days; i++) {
    const d = addDays(today, i);
    const out = (outByDate.get(d) ?? 0) + essentialsDaily;
    const confirmedIn = confirmedByDate.get(d) ?? 0;
    const uncertainIn = (uncertainByDate.get(d) ?? 0) + (receivablesByDate.get(d) ?? 0);
    conservative -= out;
    withConfirmed += confirmedIn - out;
    optimistic += confirmedIn + uncertainIn - out;
    points.push({ date: d, conservative, withConfirmed, optimistic, outflow: out, inflow: confirmedIn + uncertainIn });
  }
  return points;
}
