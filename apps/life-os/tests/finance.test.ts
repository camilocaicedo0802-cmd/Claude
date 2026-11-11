import { describe, expect, it } from "vitest";
import type { Account, Budget, Category, Obligation, PlannedIncome, Transaction } from "@/db/types";
import { defaultCategories } from "@/db/defaults";
import {
  budgetStatuses,
  computeSpendCapacity,
  obligationOccurrences,
  periodTotals,
  summarizeBalances,
  type FinanceInput,
} from "@/domain/finance";
import { fromMajor } from "@/lib/money";

const M = fromMajor;
const TODAY = "2026-11-11"; // Wednesday
const ts = { createdAt: "2026-11-01T00:00:00Z", updatedAt: "2026-11-01T00:00:00Z" };

function account(id: string, type: Account["type"], opening: number, extra: Partial<Account> = {}): Account {
  return {
    id,
    name: id,
    type,
    openingBalance: M(opening),
    openingDate: "2026-11-01",
    spendable: type !== "savings" && type !== "credit",
    color: "iris",
    archived: false,
    order: 0,
    ...ts,
    ...extra,
  };
}

let n = 0;
function tx(t: Partial<Transaction> & Pick<Transaction, "kind" | "amount" | "date" | "accountId">): Transaction {
  return { id: `t${++n}`, ...ts, ...t } as Transaction;
}

function obligation(id: string, amount: number, startDate: string, extra: Partial<Obligation> = {}): Obligation {
  return {
    id,
    name: id,
    type: "other",
    amount: M(amount),
    startDate,
    recurrence: null,
    active: true,
    settled: {},
    ...ts,
    ...extra,
  };
}

const categories: Category[] = defaultCategories();
const cat = (key: string) => categories.find((c) => c.systemKey === key)!.id;

function input(partial: Partial<FinanceInput>): FinanceInput {
  return {
    today: TODAY,
    settings: {
      safetyReserve: 0,
      leisureShare: 30,
      horizonMode: "endOfMonth",
      horizonDays: 30,
      includeConfirmedIncome: false,
      reserveSavingsGoals: true,
      weekStartsOn: 1,
    },
    accounts: [],
    categories,
    transactions: [],
    budgets: [],
    obligations: [],
    plannedIncomes: [],
    goals: [],
    contributions: [],
    receivables: 0,
    ...partial,
  };
}

describe("balances", () => {
  it("never counts transfers as income/expense nor credit limits as money", () => {
    const accounts = [account("bank", "bank", 1_000_000), account("cash", "cash", 0), account("visa", "credit", 0, { creditLimit: M(5_000_000) })];
    const transactions = [
      tx({ kind: "transfer", amount: M(200_000), date: TODAY, accountId: "bank", toAccountId: "cash" }),
      tx({ kind: "expense", amount: M(150_000), date: TODAY, accountId: "visa", categoryId: cat("shopping") }),
    ];
    const b = summarizeBalances(accounts, transactions);
    expect(b.liquid).toBe(M(1_000_000)); // transfer moved money, did not create it
    expect(b.byAccount.get("cash")).toBe(M(200_000));
    expect(b.creditDebt).toBe(M(150_000));
    expect(b.creditAvailable).toBe(M(4_850_000));
    const totals = periodTotals(transactions, "2026-11-01", "2026-11-30");
    expect(totals.income).toBe(0);
    expect(totals.expense).toBe(M(150_000));
  });
});

describe("acceptance: escenario financiero", () => {
  it("separates real balance from projected spending margin", () => {
    // Saldo inicial $1.000.000, gasto $100.000, obligación $400.000 la próxima semana.
    const accounts = [account("bank", "bank", 1_000_000)];
    const transactions = [tx({ kind: "expense", amount: M(100_000), date: TODAY, accountId: "bank", categoryId: cat("food") })];
    const obligations = [obligation("Arriendo", 400_000, "2026-11-18")];
    const r = computeSpendCapacity(input({ accounts, transactions, obligations }));

    expect(r.realBalance).toBe(M(900_000)); // the obligation is NOT subtracted from the real balance
    expect(r.obligations.total).toBe(M(400_000));
    expect(r.free).toBe(M(900_000) - M(400_000) - r.essentials.total - r.reserves.total);
    expect(r.free).toBeLessThanOrEqual(M(500_000));
    expect(r.status).toBe("ok");
    expect(r.summary).toContain("400.000");
  });

  it("updates the projection once the obligation is paid (no double counting)", () => {
    const accounts = [account("bank", "bank", 1_000_000)];
    const obligations = [obligation("Arriendo", 400_000, "2026-11-18")];
    const transactions = [
      tx({ kind: "expense", amount: M(400_000), date: TODAY, accountId: "bank", obligationId: "Arriendo", occurrenceDate: "2026-11-18" }),
    ];
    const r = computeSpendCapacity(input({ accounts, transactions, obligations }));
    expect(r.realBalance).toBe(M(600_000));
    expect(r.obligations.total).toBe(0);
    expect(r.free).toBe(M(600_000));
  });
});

describe("spend capacity engine", () => {
  it("asks for data instead of inventing a recommendation", () => {
    const r = computeSpendCapacity(input({}));
    expect(r.status).toBe("no-accounts");
    expect(r.availableToday).toBe(0);
    expect(r.missing[0]).toMatch(/cuenta/);
  });

  it("never treats client receivables or unconfirmed income as available", () => {
    const accounts = [account("bank", "bank", 500_000)];
    const plannedIncomes: PlannedIncome[] = [
      { id: "p1", name: "Proyecto incierto", amount: M(2_000_000), startDate: "2026-11-20", recurrence: null, confirmed: false, active: true, settled: {}, ...ts },
    ];
    const r = computeSpendCapacity(input({ accounts, plannedIncomes, receivables: M(3_000_000) }));
    expect(r.free).toBe(M(500_000));
    expect(r.income.uncertain).toBe(M(5_000_000));
    expect(r.notes.join(" ")).toMatch(/clientes te deben/);
  });

  it("uses the next confirmed income as the horizon and only adds it when the user opts in", () => {
    const accounts = [account("bank", "bank", 600_000)];
    const plannedIncomes: PlannedIncome[] = [
      { id: "salary", name: "Salario", amount: M(3_000_000), startDate: "2026-11-15", recurrence: { freq: "monthly", interval: 1 }, confirmed: true, active: true, settled: {}, ...ts },
    ];
    const base = input({ accounts, plannedIncomes });
    base.settings.horizonMode = "nextIncome";
    const r = computeSpendCapacity(base);
    expect(r.horizon.reason).toBe("nextIncome");
    expect(r.horizon.end).toBe("2026-11-14");
    expect(r.horizon.days).toBe(4);
    expect(r.dailyAllowance).toBe(M(150_000));

    const days = input({ accounts, plannedIncomes });
    days.settings.horizonMode = "days";
    days.settings.horizonDays = 30;
    expect(computeSpendCapacity(days).free).toBe(M(600_000));
    days.settings.includeConfirmedIncome = true;
    expect(computeSpendCapacity(days).free).toBe(M(600_000) + M(3_000_000));
  });

  it("reserves essentials from budgets, safety cushion and keeps savings accounts apart", () => {
    const accounts = [account("bank", "bank", 1_000_000), account("savings", "savings", 5_000_000)];
    const budgets: Budget[] = [{ id: "b1", categoryId: cat("food"), amount: M(600_000), ...ts }];
    const transactions = [tx({ kind: "expense", amount: M(100_000), date: "2026-11-05", accountId: "bank", categoryId: cat("food") })];
    const base = input({ accounts, budgets, transactions });
    base.settings.safetyReserve = M(100_000);
    const r = computeSpendCapacity(base);
    // remaining food budget 500.000 spread over the 20 days left (11→30), all inside the horizon
    expect(r.essentials.total).toBe(M(500_000));
    expect(r.reserves.safety).toBe(M(100_000));
    expect(r.startingBalance).toBe(M(900_000));
    expect(r.realBalance).toBe(M(5_900_000));
    expect(r.free).toBe(M(300_000));
    expect(r.dailyAllowance).toBe(M(15_000)); // 300.000 / 20 days
  });

  it("subtracts today's discretionary spending from today's allowance", () => {
    const accounts = [account("bank", "bank", 200_000)];
    const transactions = [tx({ kind: "expense", amount: M(5_000), date: TODAY, accountId: "bank", categoryId: cat("leisure") })];
    const r = computeSpendCapacity(input({ accounts, transactions }));
    // pool = 195.000 + 5.000 = 200.000 over 20 days = 10.000/day; already spent 5.000 today
    expect(r.dailyAllowance).toBe(M(10_000));
    expect(r.availableToday).toBe(M(5_000));
  });

  it("raises a concrete alert when the projection is negative", () => {
    const accounts = [account("bank", "bank", 300_000)];
    const obligations = [obligation("Préstamo", 450_000, "2026-11-20")];
    const r = computeSpendCapacity(input({ accounts, obligations }));
    expect(r.status).toBe("negative");
    expect(r.free).toBe(-M(150_000));
    expect(r.availableToday).toBe(0);
    expect(r.warnings[0]).toMatch(/150\.000/);
  });

  it("includes overdue obligations and warns about card debt without a scheduled payment", () => {
    const accounts = [account("bank", "bank", 1_000_000), account("visa", "credit", -200_000)];
    const obligations = [obligation("Internet", 90_000, "2026-11-05")];
    const r = computeSpendCapacity(input({ accounts, obligations }));
    expect(r.obligations.overdue).toBe(M(90_000));
    expect(r.warnings.some((w) => w.includes("tarjetas"))).toBe(true);
  });
});

describe("obligations", () => {
  it("handles partial payments, settlements and recurring occurrences without duplicates", () => {
    const o = obligation("Arriendo", 1_000_000, "2026-10-05", { recurrence: { freq: "monthly", interval: 1 } });
    const transactions = [
      tx({ kind: "expense", amount: M(1_000_000), date: "2026-10-05", accountId: "bank", obligationId: o.id, occurrenceDate: "2026-10-05" }),
      tx({ kind: "expense", amount: M(400_000), date: "2026-11-05", accountId: "bank", obligationId: o.id, occurrenceDate: "2026-11-05" }),
    ];
    const occ = obligationOccurrences([o], transactions, "2026-10-01", "2026-12-31", TODAY);
    expect(occ.map((x) => [x.dueDate, x.status, x.remaining])).toEqual([
      ["2026-10-05", "paid", 0],
      ["2026-11-05", "overdue", M(600_000)],
      ["2026-12-05", "pending", M(1_000_000)],
    ]);
    const settled = { ...o, settled: { "2026-12-05": "skipped" as const } };
    expect(obligationOccurrences([settled], transactions, "2026-12-01", "2026-12-31", TODAY)[0].status).toBe("settled");
  });
});

describe("budgets", () => {
  it("flags categories near and over the limit within the same month", () => {
    const budgets: Budget[] = [
      { id: "b1", categoryId: cat("food"), amount: M(600_000), ...ts },
      { id: "b2", categoryId: cat("leisure"), amount: M(200_000), ...ts },
    ];
    const transactions = [
      tx({ kind: "expense", amount: M(500_000), date: "2026-11-03", accountId: "bank", categoryId: cat("food") }),
      tx({ kind: "expense", amount: M(250_000), date: "2026-11-04", accountId: "bank", categoryId: cat("leisure") }),
      tx({ kind: "expense", amount: M(999_000), date: "2026-10-30", accountId: "bank", categoryId: cat("food") }), // previous month
    ];
    const s = budgetStatuses(budgets, categories, transactions, TODAY, TODAY);
    const food = s.find((x) => x.budget.id === "b1")!;
    const leisure = s.find((x) => x.budget.id === "b2")!;
    expect(food.spent).toBe(M(500_000));
    expect(food.state).toBe("near");
    expect(food.remaining).toBe(M(100_000));
    expect(leisure.state).toBe("over");
  });
});
