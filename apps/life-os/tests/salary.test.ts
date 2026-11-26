import { beforeEach, describe, expect, it } from "vitest";
import { db, LifeOSDB, setDB } from "@/db/db";
import { ensureDefaults } from "@/db/defaults";
import { buildAlerts } from "@/domain/alerts";
import {
  clientPayMode,
  computeSpendCapacity,
  monthlyEquivalent,
  plannedIncomeOccurrences,
  recurringIncomeViews,
  summarizeBalances,
  type FinanceInput,
} from "@/domain/finance";
import { fromMajor, formatMoney } from "@/lib/money";
import { describeRecurrence, nextOccurrence, occurrencesBetween, presetToRecurrence, recurrenceToPreset } from "@/lib/recurrence";
import { uid } from "@/lib/utils";
import { createClient } from "@/services/clients-service";
import {
  createAccount,
  createPlannedIncome,
  deleteTransaction,
  receivePlannedIncome,
  setClientPayPlan,
  skipPlannedIncome,
  updatePlannedIncome,
} from "@/services/finance-service";

const M = fromMajor;
const TODAY = "2026-11-11";

beforeEach(async () => {
  const fresh = new LifeOSDB(`test-${uid()}`);
  setDB(fresh);
  await ensureDefaults(fresh);
});

describe("quincena (two fixed paydays a month)", () => {
  const quincena = presetToRecurrence("semimonthly")!;

  it("pays on the 15th and the 30th, and on the last day of February", () => {
    expect(occurrencesBetween("2026-01-01", quincena, "2026-01-01", "2026-03-31")).toEqual([
      "2026-01-15",
      "2026-01-30",
      "2026-02-15",
      "2026-02-28",
      "2026-03-15",
      "2026-03-30",
    ]);
    expect(occurrencesBetween("2028-02-01", quincena, "2028-02-01", "2028-02-29")).toEqual(["2028-02-15", "2028-02-29"]);
  });

  it("starts at the first payday on or after the start date", () => {
    expect(occurrencesBetween("2026-11-20", quincena, "2026-11-01", "2026-12-31")).toEqual(["2026-11-30", "2026-12-15", "2026-12-30"]);
  });

  it("accepts other paydays, an end date and a number of payments", () => {
    const custom = presetToRecurrence("semimonthly", [20, 5])!;
    expect(custom.byMonthDay).toEqual([5, 20]);
    expect(occurrencesBetween("2026-11-01", { ...custom, until: "2026-12-10" }, "2026-11-01", "2027-03-01")).toEqual(["2026-11-05", "2026-11-20", "2026-12-05"]);
    expect(occurrencesBetween("2026-11-01", { ...custom, count: 3 }, "2026-11-01", "2027-03-01")).toEqual(["2026-11-05", "2026-11-20", "2026-12-05"]);
  });

  it("finds the next payday years after the anchor", () => {
    expect(nextOccurrence("2020-01-01", quincena, "2031-05-16")).toBe("2031-05-30");
  });

  it("round-trips through presets and describes itself", () => {
    expect(recurrenceToPreset(quincena)).toBe("semimonthly");
    expect(recurrenceToPreset({ freq: "monthly", interval: 1 })).toBe("monthly");
    expect(describeRecurrence(quincena)).toBe("Quincenal · días 15 y 30");
  });

  it("converts any periodicity to a monthly equivalent", () => {
    expect(monthlyEquivalent({ amount: M(1_200_000), recurrence: quincena })).toBe(M(2_400_000));
    expect(monthlyEquivalent({ amount: M(3_000_000), recurrence: { freq: "monthly", interval: 1 } })).toBe(M(3_000_000));
    expect(monthlyEquivalent({ amount: M(6_000_000), recurrence: { freq: "monthly", interval: 3 } })).toBe(M(2_000_000));
    expect(monthlyEquivalent({ amount: M(500_000), recurrence: null })).toBe(0);
  });
});

describe("sueldo de un cliente", () => {
  async function setup() {
    const accountId = await createAccount({ name: "Banco", type: "bank", openingBalance: 0, openingDate: "2026-01-01", spendable: true, color: "iris" });
    const clientId = await createClient({ name: "Agencia Norte", status: "active", tags: [] });
    const salaryCat = (await db().categories.toArray()).find((c) => c.systemKey === "salary")!.id;
    const incomeId = await createPlannedIncome({
      name: "Sueldo",
      amount: M(3_000_000),
      startDate: "2026-09-30",
      recurrence: { freq: "monthly", interval: 1 },
      confirmed: true,
      accountId,
      categoryId: salaryCat,
      clientId,
    });
    return { accountId, clientId, incomeId };
  }

  async function views() {
    const d = db();
    return recurringIncomeViews(await d.plannedIncomes.toArray(), await d.transactions.toArray(), TODAY);
  }

  it("registers each payday once, linked to the client and to Finanzas", async () => {
    const { accountId, clientId, incomeId } = await setup();
    await receivePlannedIncome({ plannedIncomeId: incomeId, dueDate: "2026-09-30", amount: M(3_000_000), date: "2026-09-30", accountId });
    await receivePlannedIncome({ plannedIncomeId: incomeId, dueDate: "2026-10-30", amount: M(3_000_000), date: "2026-11-02", accountId });

    const txs = await db().transactions.toArray();
    expect(txs).toHaveLength(2);
    expect(txs.every((t) => t.kind === "income" && t.clientId === clientId && t.plannedIncomeId === incomeId)).toBe(true);
    expect(summarizeBalances(await db().accounts.toArray(), txs).liquid).toBe(M(6_000_000));

    const [v] = await views();
    expect(v.overdue).toHaveLength(0);
    expect(v.next?.dueDate).toBe("2026-11-30");
    expect(v.recent.map((o) => [o.dueDate, o.status])).toEqual([
      ["2026-10-30", "paid"],
      ["2026-09-30", "paid"],
    ]);
    expect(v.receivedYear).toBe(M(6_000_000));
    expect(v.monthly).toBe(M(3_000_000));

    const activity = (await db().activities.toArray()).filter((a) => a.clientId === clientId).map((a) => a.message);
    expect(activity.some((m) => m.startsWith("Pago periódico agregado: Sueldo"))).toBe(true);
    expect(activity.filter((m) => m.startsWith("Sueldo: recibido"))).toHaveLength(2);
  });

  it("flags a payday that passed without being registered, and clears it when received or skipped", async () => {
    const { accountId, incomeId } = await setup();
    await receivePlannedIncome({ plannedIncomeId: incomeId, dueDate: "2026-09-30", amount: M(3_000_000), date: "2026-09-30", accountId });

    let [v] = await views();
    expect(v.overdue.map((o) => o.dueDate)).toEqual(["2026-10-30"]);

    const alerts = () =>
      buildAlerts({
        today: TODAY,
        prefs: { obligations: true, budgets: true, jobs: true, collections: true, tasks: true, obligationLeadDays: 3 },
        obligations: [],
        budgets: [],
        jobViews: [],
        tasks: [],
        capacity: null,
        recurringIncomes: v ? [v] : [],
        format: (m) => formatMoney(m),
      }).filter((a) => a.key.startsWith("salary:"));
    expect(alerts()).toHaveLength(1);
    expect(alerts()[0].title).toMatch(/sin registrar/);

    // A partial receipt keeps it flagged with what is missing.
    await receivePlannedIncome({ plannedIncomeId: incomeId, dueDate: "2026-10-30", amount: M(1_000_000), date: TODAY, accountId });
    [v] = await views();
    expect(v.overdue[0].remaining).toBe(M(2_000_000));

    await skipPlannedIncome(incomeId, "2026-10-30", true);
    [v] = await views();
    expect(v.overdue).toHaveLength(0);
    expect(alerts()).toHaveLength(0);
  });

  it("keeps past periods at their old value after a raise", async () => {
    const { accountId, incomeId } = await setup();
    await receivePlannedIncome({ plannedIncomeId: incomeId, dueDate: "2026-09-30", amount: M(3_000_000), date: "2026-09-30", accountId });
    await receivePlannedIncome({ plannedIncomeId: incomeId, dueDate: "2026-10-30", amount: M(3_000_000), date: "2026-10-30", accountId });

    await updatePlannedIncome(incomeId, { amount: M(3_500_000) }, { amountFrom: "2026-11-01" });

    const d = db();
    const occ = plannedIncomeOccurrences(await d.plannedIncomes.toArray(), await d.transactions.toArray(), "2026-09-01", "2026-12-31", TODAY);
    expect(occ.map((o) => [o.dueDate, o.amount, o.status])).toEqual([
      ["2026-09-30", M(3_000_000), "paid"],
      ["2026-10-30", M(3_000_000), "paid"],
      ["2026-11-30", M(3_500_000), "pending"],
      ["2026-12-30", M(3_500_000), "pending"],
    ]);

    // A second change applies on top of the history, never rewriting received months.
    await updatePlannedIncome(incomeId, { amount: M(4_000_000) }, { amountFrom: "2026-12-01" });
    const after = plannedIncomeOccurrences(await d.plannedIncomes.toArray(), await d.transactions.toArray(), "2026-09-01", "2026-12-31", TODAY);
    expect(after.map((o) => o.amount)).toEqual([M(3_000_000), M(3_000_000), M(3_500_000), M(4_000_000)]);
  });

  it("deleting the movement reopens the period instead of leaving a phantom payment", async () => {
    const { accountId, incomeId } = await setup();
    const txId = await receivePlannedIncome({ plannedIncomeId: incomeId, dueDate: "2026-10-30", amount: M(3_000_000), date: "2026-10-30", accountId });
    await deleteTransaction(txId);
    const [v] = await views();
    expect(v.overdue.map((o) => o.dueDate)).toEqual(["2026-09-30", "2026-10-30"]);
  });

  it("is never available money before it arrives, but sets the spending horizon", async () => {
    const { incomeId } = await setup();
    const d = db();
    const finance: FinanceInput = {
      today: TODAY,
      settings: {
        safetyReserve: 0,
        leisureShare: 30,
        horizonMode: "nextIncome",
        horizonDays: 30,
        includeConfirmedIncome: false,
        reserveSavingsGoals: true,
        weekStartsOn: 1,
      },
      accounts: await d.accounts.toArray(),
      categories: await d.categories.toArray(),
      transactions: await d.transactions.toArray(),
      budgets: [],
      obligations: [],
      plannedIncomes: await d.plannedIncomes.toArray(),
      goals: [],
      contributions: [],
      receivables: 0,
    };
    const r = computeSpendCapacity(finance);
    expect(r.realBalance).toBe(0);
    expect(r.availableToday).toBe(0);
    expect(r.horizon.reason).toBe("nextIncome");
    expect(r.horizon.nextIncome?.date).toBe("2026-11-30");
    expect(r.horizon.end).toBe("2026-11-29");
    expect(incomeId).toBeTruthy();
  });
});

describe("¿cómo te paga? (forma de pago del cliente)", () => {
  async function client() {
    const accountId = await createAccount({ name: "Banco", type: "bank", openingBalance: 0, openingDate: "2026-01-01", spendable: true, color: "iris" });
    const clientId = await createClient({ name: "Estudio Sur", status: "active", tags: [] });
    return { accountId, clientId };
  }
  async function state(clientId: string) {
    const d = db();
    const incomes = (await d.plannedIncomes.toArray()).filter((p) => p.clientId === clientId);
    const views = recurringIncomeViews(incomes, await d.transactions.toArray(), TODAY);
    return { incomes, views, mode: clientPayMode(views) };
  }

  it("a client without a fixed salary is paid per job", async () => {
    const { clientId } = await client();
    expect((await state(clientId)).mode).toBe("job");
    await setClientPayPlan(clientId, { mode: "job" }, TODAY); // no-op
    expect((await state(clientId)).incomes).toHaveLength(0);
  });

  it("monthly, quincenal and weekly create one salary with that periodicity", async () => {
    for (const [mode, expected] of [
      ["monthly", ["2026-11-30", "2026-12-30"]],
      ["semimonthly", ["2026-11-15", "2026-11-30", "2026-12-15", "2026-12-30"]],
      ["weekly", ["2026-11-13", "2026-11-20", "2026-11-27", "2026-12-04"]],
    ] as const) {
      const { clientId } = await client();
      const start = mode === "semimonthly" ? TODAY : mode === "weekly" ? "2026-11-13" : "2026-11-30";
      await setClientPayPlan(clientId, { mode, amount: M(1_000_000), startDate: start, days: mode === "semimonthly" ? [15, 30] : undefined }, TODAY);
      const { incomes, mode: got } = await state(clientId);
      expect(got).toBe(mode);
      expect(incomes).toHaveLength(1);
      expect(incomes[0].name).toBe("Sueldo");
      expect(incomes[0].confirmed).toBe(true);
      expect(occurrencesBetween(incomes[0].startDate, incomes[0].recurrence, TODAY, "2026-12-31").slice(0, expected.length)).toEqual(expected);
    }
  });

  it("changing only the value keeps the received months as they were", async () => {
    const { accountId, clientId } = await client();
    await setClientPayPlan(clientId, { mode: "monthly", amount: M(2_000_000), startDate: "2026-10-30" }, "2026-10-01");
    const [p] = (await state(clientId)).incomes;
    await receivePlannedIncome({ plannedIncomeId: p.id, dueDate: "2026-10-30", amount: M(2_000_000), date: "2026-10-30", accountId });

    await setClientPayPlan(clientId, { mode: "monthly", amount: M(2_400_000), startDate: "2026-11-30" }, TODAY);
    const { incomes, views } = await state(clientId);
    expect(incomes).toHaveLength(1);
    expect(views[0].recent[0].status).toBe("paid");
    expect(views[0].recent[0].amount).toBe(M(2_000_000));
    expect(views[0].next?.amount).toBe(M(2_400_000));
  });

  it("switching monthly → quincenal closes the old series and starts the new one, without touching history", async () => {
    const { accountId, clientId } = await client();
    await setClientPayPlan(clientId, { mode: "monthly", amount: M(2_000_000), startDate: "2026-10-30" }, "2026-10-01");
    const [old] = (await state(clientId)).incomes;
    await receivePlannedIncome({ plannedIncomeId: old.id, dueDate: "2026-10-30", amount: M(2_000_000), date: "2026-10-30", accountId });

    await setClientPayPlan(clientId, { mode: "semimonthly", amount: M(1_100_000), startDate: "2026-11-15", days: [15, 30] }, TODAY);
    const { incomes, views, mode } = await state(clientId);
    expect(mode).toBe("semimonthly");
    expect(incomes).toHaveLength(2);
    const closed = incomes.find((p) => p.id === old.id)!;
    expect(closed.recurrence?.until).toBe("2026-11-14");
    const d = db();
    const all = plannedIncomeOccurrences(incomes, await d.transactions.toArray(), "2026-10-01", "2026-12-31", TODAY);
    expect(all.map((o) => [o.dueDate, o.amount, o.status])).toEqual([
      ["2026-10-30", M(2_000_000), "paid"],
      ["2026-11-15", M(1_100_000), "pending"],
      ["2026-11-30", M(1_100_000), "pending"],
      ["2026-12-15", M(1_100_000), "pending"],
      ["2026-12-30", M(1_100_000), "pending"],
    ]);
    expect(views.filter((v) => !v.ended)).toHaveLength(1);
  });

  it("a salary with no history is simply edited in place", async () => {
    const { clientId } = await client();
    await setClientPayPlan(clientId, { mode: "monthly", amount: M(2_000_000), startDate: "2026-11-30" }, TODAY);
    await setClientPayPlan(clientId, { mode: "weekly", amount: M(500_000), startDate: "2026-11-13" }, TODAY);
    const { incomes, mode } = await state(clientId);
    expect(incomes).toHaveLength(1);
    expect(mode).toBe("weekly");
    expect(incomes[0].amount).toBe(M(500_000));
  });

  it("back to per job ends the salary yesterday but keeps what was received", async () => {
    const { accountId, clientId } = await client();
    await setClientPayPlan(clientId, { mode: "monthly", amount: M(2_000_000), startDate: "2026-10-30" }, "2026-10-01");
    const [p] = (await state(clientId)).incomes;
    await receivePlannedIncome({ plannedIncomeId: p.id, dueDate: "2026-10-30", amount: M(2_000_000), date: "2026-10-30", accountId });

    await setClientPayPlan(clientId, { mode: "job" }, TODAY);
    const { incomes, views, mode } = await state(clientId);
    expect(mode).toBe("job");
    expect(incomes[0].recurrence?.until).toBe("2026-11-10");
    expect(views[0].ended).toBe(true);
    expect(views[0].recent.map((o) => o.status)).toEqual(["paid"]);
    expect((await db().transactions.toArray()).filter((t) => t.plannedIncomeId === p.id)).toHaveLength(1);

    // A salary that never started is removed instead.
    const other = await client();
    await setClientPayPlan(other.clientId, { mode: "weekly", amount: M(300_000), startDate: "2026-11-20" }, TODAY);
    await setClientPayPlan(other.clientId, { mode: "job" }, TODAY);
    expect((await state(other.clientId)).incomes).toHaveLength(0);
  });
});
