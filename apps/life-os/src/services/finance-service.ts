import { db } from "@/db/db";
import type {
  Account,
  Budget,
  Category,
  GoalContribution,
  Obligation,
  OccurrenceSettlement,
  PlannedIncome,
  SavingsGoal,
  Transaction,
} from "@/db/types";
import { nowISO, type DateStr } from "@/lib/dates";
import type { Minor } from "@/lib/money";
import { uid } from "@/lib/utils";
import { DomainError, logActivity } from "./common";

// ── Accounts ─────────────────────────────────────────────────────────────────

export type AccountInput = Omit<Account, "id" | "createdAt" | "updatedAt" | "archived" | "order"> &
  Partial<Pick<Account, "archived" | "order">>;

export async function createAccount(input: AccountInput): Promise<string> {
  if (!input.name.trim()) throw new DomainError("La cuenta necesita un nombre.");
  const now = nowISO();
  const order = (await db().accounts.count()) + 1;
  const account: Account = {
    ...input,
    name: input.name.trim(),
    creditLimit: input.type === "credit" ? input.creditLimit ?? null : null,
    spendable: input.type === "credit" ? false : input.spendable,
    id: uid(),
    archived: input.archived ?? false,
    order: input.order ?? order,
    createdAt: now,
    updatedAt: now,
  };
  await db().accounts.add(account);
  return account.id;
}

export async function updateAccount(id: string, patch: Partial<AccountInput> & { archived?: boolean }) {
  await db().accounts.update(id, { ...patch, updatedAt: nowISO() });
}

/** Deletes an account without history; accounts with movements are archived instead. */
export async function deleteOrArchiveAccount(id: string): Promise<"deleted" | "archived"> {
  const d = db();
  return d.transaction("rw", [d.accounts, d.transactions], async () => {
    const used =
      (await d.transactions.where("accountId").equals(id).count()) + (await d.transactions.where("toAccountId").equals(id).count());
    if (used > 0) {
      await d.accounts.update(id, { archived: true, updatedAt: nowISO() });
      return "archived" as const;
    }
    await d.accounts.delete(id);
    return "deleted" as const;
  });
}

// ── Categories ───────────────────────────────────────────────────────────────

export async function createCategory(input: Pick<Category, "name" | "kind" | "icon" | "color"> & { nature?: Category["nature"] }) {
  const name = input.name.trim();
  if (!name) throw new DomainError("La categoría necesita un nombre.");
  const existing = await db().categories.where("kind").equals(input.kind).toArray();
  if (existing.some((c) => !c.archived && c.name.toLowerCase() === name.toLowerCase())) {
    throw new DomainError(`Ya existe la categoría "${name}".`);
  }
  const now = nowISO();
  const cat: Category = {
    id: uid(),
    name,
    kind: input.kind,
    nature: input.kind === "expense" ? input.nature ?? "variable" : undefined,
    icon: input.icon,
    color: input.color,
    archived: false,
    order: existing.length,
    createdAt: now,
    updatedAt: now,
  };
  await db().categories.add(cat);
  return cat.id;
}

export async function updateCategory(id: string, patch: Partial<Pick<Category, "name" | "icon" | "color" | "nature" | "archived">>) {
  await db().categories.update(id, { ...patch, updatedAt: nowISO() });
}

// ── Transactions ─────────────────────────────────────────────────────────────

export type TransactionInput = Omit<Transaction, "id" | "createdAt" | "updatedAt">;

function validateTransaction(t: TransactionInput) {
  if (!Number.isSafeInteger(t.amount) || t.amount <= 0) throw new DomainError("El valor debe ser mayor que cero.");
  if (!t.accountId) throw new DomainError("Elige una cuenta.");
  if (t.kind === "transfer") {
    if (!t.toAccountId) throw new DomainError("Elige la cuenta de destino.");
    if (t.toAccountId === t.accountId) throw new DomainError("La cuenta de origen y destino deben ser distintas.");
  }
}

export async function createTransaction(input: TransactionInput): Promise<string> {
  validateTransaction(input);
  const now = nowISO();
  const tx: Transaction = {
    ...input,
    toAccountId: input.kind === "transfer" ? input.toAccountId : null,
    categoryId: input.kind === "transfer" ? null : input.categoryId ?? null,
    description: input.description?.trim() || undefined,
    id: uid(),
    createdAt: now,
    updatedAt: now,
  };
  await db().transactions.add(tx);
  return tx.id;
}

/**
 * Edits a movement. If the movement is the money side of a client payment, the payment
 * is updated in the same database transaction so both records always agree.
 */
export async function updateTransaction(id: string, patch: Partial<TransactionInput>) {
  const d = db();
  await d.transaction("rw", [d.transactions, d.clientPayments, d.jobs, d.activities], async () => {
    const current = await d.transactions.get(id);
    if (!current) throw new DomainError("El movimiento ya no existe.");
    const next = { ...current, ...patch } as Transaction;
    if (current.clientPaymentId && next.kind !== "income") {
      throw new DomainError("Este ingreso viene de un pago de cliente y debe seguir siendo un ingreso.");
    }
    validateTransaction(next);
    if (current.clientPaymentId) {
      const payment = await d.clientPayments.get(current.clientPaymentId);
      if (payment) {
        const job = await d.jobs.get(payment.jobId);
        if (job) {
          const others = await d.clientPayments.where("jobId").equals(job.id).toArray();
          const total = others.filter((p) => p.id !== payment.id).reduce((s, p) => s + p.amount, 0) + next.amount;
          if (total > job.price) {
            throw new DomainError("Con ese valor los pagos superarían el precio acordado del trabajo. Ajusta el precio desde el trabajo.");
          }
        }
        await d.clientPayments.update(payment.id, {
          amount: next.amount,
          date: next.date,
          accountId: next.accountId,
          updatedAt: nowISO(),
        });
        await logActivity({ clientId: payment.clientId, jobId: payment.jobId, type: "payment", message: "Pago editado desde Finanzas" });
      }
    }
    await d.transactions.put({ ...next, updatedAt: nowISO() });
  });
}

/** Deletes a movement. A linked client payment is voided with it (never left orphaned). */
export async function deleteTransaction(id: string) {
  const d = db();
  await d.transaction("rw", [d.transactions, d.clientPayments, d.activities], async () => {
    const tx = await d.transactions.get(id);
    if (!tx) return;
    if (tx.clientPaymentId) {
      const payment = await d.clientPayments.get(tx.clientPaymentId);
      if (payment) {
        await d.clientPayments.delete(payment.id);
        await logActivity({ clientId: payment.clientId, jobId: payment.jobId, type: "payment", message: "Pago anulado (se eliminó su ingreso)" });
      }
    }
    await d.transactions.delete(id);
  });
}

// ── Budgets ──────────────────────────────────────────────────────────────────

export async function setBudget(categoryId: string, amount: Minor) {
  if (!Number.isSafeInteger(amount) || amount <= 0) throw new DomainError("El presupuesto debe ser mayor que cero.");
  const d = db();
  await d.transaction("rw", d.budgets, async () => {
    const existing = await d.budgets.where("categoryId").equals(categoryId).first();
    const now = nowISO();
    if (existing) await d.budgets.update(existing.id, { amount, updatedAt: now });
    else await d.budgets.add({ id: uid(), categoryId, amount, createdAt: now, updatedAt: now } satisfies Budget);
  });
}

export async function deleteBudget(id: string) {
  await db().budgets.delete(id);
}

// ── Obligations ──────────────────────────────────────────────────────────────

export type ObligationInput = Omit<Obligation, "id" | "createdAt" | "updatedAt" | "settled" | "active"> &
  Partial<Pick<Obligation, "active">>;

export async function createObligation(input: ObligationInput): Promise<string> {
  if (!input.name.trim()) throw new DomainError("Ponle un nombre a la obligación.");
  if (input.amount <= 0) throw new DomainError("El valor debe ser mayor que cero.");
  const now = nowISO();
  const o: Obligation = { ...input, name: input.name.trim(), id: uid(), active: input.active ?? true, settled: {}, createdAt: now, updatedAt: now };
  await db().obligations.add(o);
  return o.id;
}

export async function updateObligation(id: string, patch: Partial<ObligationInput>) {
  await db().obligations.update(id, { ...patch, updatedAt: nowISO() });
}

/** Removes an obligation; its past payments stay as normal expenses (unlinked from the series). */
export async function deleteObligation(id: string) {
  const d = db();
  await d.transaction("rw", [d.obligations, d.transactions], async () => {
    const txs = await d.transactions.where("obligationId").equals(id).toArray();
    for (const t of txs) await d.transactions.update(t.id, { obligationId: null, occurrenceDate: null, updatedAt: nowISO() });
    await d.obligations.delete(id);
  });
}

export interface PayObligationInput {
  obligationId: string;
  dueDate: DateStr;
  amount: Minor;
  date: DateStr;
  accountId: string;
  note?: string;
}

/**
 * Registers a (partial or full) payment of one occurrence. The payment *is* the movement:
 * an expense, or a transfer to the card when paying a credit card (so card purchases are not
 * counted twice).
 */
export async function payObligation(input: PayObligationInput): Promise<string> {
  const o = await db().obligations.get(input.obligationId);
  if (!o) throw new DomainError("La obligación ya no existe.");
  const isCard = o.type === "card" && !!o.cardAccountId && o.cardAccountId !== input.accountId;
  return createTransaction({
    kind: isCard ? "transfer" : "expense",
    amount: input.amount,
    date: input.date,
    accountId: input.accountId,
    toAccountId: isCard ? o.cardAccountId : null,
    categoryId: isCard ? null : o.categoryId ?? null,
    description: input.note || `Pago: ${o.name}`,
    obligationId: o.id,
    occurrenceDate: input.dueDate,
  });
}

export async function settleOccurrence(obligationId: string, dueDate: DateStr, settlement: OccurrenceSettlement | null) {
  const d = db();
  await d.transaction("rw", d.obligations, async () => {
    const o = await d.obligations.get(obligationId);
    if (!o) return;
    const settled = { ...(o.settled ?? {}) };
    if (settlement) settled[dueDate] = settlement;
    else delete settled[dueDate];
    await d.obligations.update(obligationId, { settled, updatedAt: nowISO() });
  });
}

// ── Planned income ───────────────────────────────────────────────────────────

export type PlannedIncomeInput = Omit<PlannedIncome, "id" | "createdAt" | "updatedAt" | "settled" | "active">;

export async function createPlannedIncome(input: PlannedIncomeInput): Promise<string> {
  if (!input.name.trim()) throw new DomainError("Ponle un nombre al ingreso.");
  if (input.amount <= 0) throw new DomainError("El valor debe ser mayor que cero.");
  const now = nowISO();
  const p: PlannedIncome = { ...input, name: input.name.trim(), id: uid(), active: true, settled: {}, createdAt: now, updatedAt: now };
  await db().plannedIncomes.add(p);
  return p.id;
}

export async function updatePlannedIncome(id: string, patch: Partial<PlannedIncomeInput & { active: boolean }>) {
  await db().plannedIncomes.update(id, { ...patch, updatedAt: nowISO() });
}

export async function deletePlannedIncome(id: string) {
  const d = db();
  await d.transaction("rw", [d.plannedIncomes, d.transactions], async () => {
    const txs = await d.transactions.where("plannedIncomeId").equals(id).toArray();
    for (const t of txs) await d.transactions.update(t.id, { plannedIncomeId: null, occurrenceDate: null, updatedAt: nowISO() });
    await d.plannedIncomes.delete(id);
  });
}

export async function receivePlannedIncome(input: { plannedIncomeId: string; dueDate: DateStr; amount: Minor; date: DateStr; accountId: string }) {
  const p = await db().plannedIncomes.get(input.plannedIncomeId);
  if (!p) throw new DomainError("El ingreso previsto ya no existe.");
  return createTransaction({
    kind: "income",
    amount: input.amount,
    date: input.date,
    accountId: input.accountId,
    categoryId: p.categoryId ?? null,
    description: p.name,
    plannedIncomeId: p.id,
    occurrenceDate: input.dueDate,
  });
}

export async function skipPlannedIncome(id: string, dueDate: DateStr, skip: boolean) {
  const d = db();
  await d.transaction("rw", d.plannedIncomes, async () => {
    const p = await d.plannedIncomes.get(id);
    if (!p) return;
    const settled = { ...(p.settled ?? {}) };
    if (skip) settled[dueDate] = "skipped";
    else delete settled[dueDate];
    await d.plannedIncomes.update(id, { settled, updatedAt: nowISO() });
  });
}

// ── Savings goals ────────────────────────────────────────────────────────────

export async function createGoal(input: Omit<SavingsGoal, "id" | "createdAt" | "updatedAt" | "archived">, initial?: Minor) {
  if (!input.name.trim()) throw new DomainError("Ponle un nombre a la meta.");
  if (input.target <= 0) throw new DomainError("La meta debe ser mayor que cero.");
  const now = nowISO();
  const goal: SavingsGoal = { ...input, name: input.name.trim(), id: uid(), archived: false, createdAt: now, updatedAt: now };
  const d = db();
  await d.transaction("rw", [d.goals, d.goalContributions], async () => {
    await d.goals.add(goal);
    if (initial && initial > 0) {
      await d.goalContributions.add({ id: uid(), goalId: goal.id, amount: initial, date: now.slice(0, 10), note: "Saldo inicial", createdAt: now, updatedAt: now });
    }
  });
  return goal.id;
}

export async function updateGoal(id: string, patch: Partial<Omit<SavingsGoal, "id" | "createdAt">>) {
  await db().goals.update(id, { ...patch, updatedAt: nowISO() });
}

export async function deleteGoal(id: string) {
  const d = db();
  await d.transaction("rw", [d.goals, d.goalContributions], async () => {
    await d.goalContributions.where("goalId").equals(id).delete();
    await d.goals.delete(id);
  });
}

export async function addContribution(input: Omit<GoalContribution, "id" | "createdAt" | "updatedAt">) {
  if (input.amount === 0) throw new DomainError("El aporte no puede ser cero.");
  const now = nowISO();
  await db().goalContributions.add({ ...input, id: uid(), createdAt: now, updatedAt: now });
}

export async function deleteContribution(id: string) {
  await db().goalContributions.delete(id);
}
