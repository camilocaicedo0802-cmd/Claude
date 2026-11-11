import { beforeEach, describe, expect, it } from "vitest";
import { db, LifeOSDB, setDB } from "@/db/db";
import { ensureDefaults } from "@/db/defaults";
import { buildJobViews, jobFinance, paymentsByJob, totalReceivables } from "@/domain/clients";
import { bestStreak, currentStreak, logsIndex } from "@/domain/habits";
import { buildAgenda } from "@/domain/agenda";
import { summarizeBalances } from "@/domain/finance";
import { fromMajor } from "@/lib/money";
import { uid } from "@/lib/utils";
import {
  addClientPayment,
  createClient,
  createJob,
  deleteClientPayment,
  deleteJob,
  setJobStatus,
  updateClientPayment,
  updateJob,
} from "@/services/clients-service";
import {
  createAccount,
  createObligation,
  createTransaction,
  deleteTransaction,
  payObligation,
  updateTransaction,
} from "@/services/finance-service";
import {
  createHabit,
  createTask,
  postponeTask,
  rescheduleTask,
  setHabitCount,
  setTaskDone,
} from "@/services/life-service";
import { exportBackup, parseBackup, restoreBackup } from "@/services/settings-service";

const M = fromMajor;
const TODAY = "2026-11-11";

beforeEach(async () => {
  const fresh = new LifeOSDB(`test-${uid()}`);
  setDB(fresh);
  await ensureDefaults(fresh);
});

async function bank(opening = 0) {
  return createAccount({ name: "Banco", type: "bank", openingBalance: M(opening), openingDate: TODAY, spendable: true, color: "iris" });
}

async function statusId(kind: string) {
  return (await db().jobStatuses.toArray()).find((s) => s.kind === kind)!.id;
}

async function views() {
  const d = db();
  return buildJobViews(await d.jobs.toArray(), await d.clients.toArray(), await d.jobStatuses.toArray(), await d.clientPayments.toArray(), TODAY);
}

describe("acceptance: escenario de clientes", () => {
  it("keeps production status and payment status independent", async () => {
    const clientId = await createClient({ name: "Ana", status: "active", tags: [] });
    const jobId = await createJob({
      clientId,
      title: "Video",
      requestedAt: TODAY,
      dueDate: "2026-11-20",
      price: M(800_000),
      priority: "medium",
      statusId: await statusId("doing"),
    });
    await addClientPayment({ jobId, amount: M(300_000), date: TODAY, kind: "partial" });
    let v = (await views())[0];
    expect(v.finance.balance).toBe(M(500_000));
    expect(v.finance.state).toBe("partial");

    await setJobStatus(jobId, await statusId("delivered"));
    v = (await views())[0];
    expect(v.kind).toBe("delivered");
    expect(v.isOpen).toBe(false);
    expect(v.finance.balance).toBe(M(500_000)); // delivered but still owed
    expect(v.finance.state).toBe("partial");
    expect(totalReceivables(await views())).toBe(M(500_000));
  });
});

describe("Flujo A: cliente y dinero", () => {
  it("records the advance once as real income and the rest as a receivable", async () => {
    const accountId = await bank(0);
    const clientId = await createClient({ name: "Bruno", status: "active", tags: [] });
    const jobId = await createJob(
      { clientId, title: "Logo", requestedAt: TODAY, price: M(500_000), priority: "high", statusId: await statusId("new") },
      { amount: M(200_000), date: TODAY, accountId },
    );
    const d = db();
    const txs = await d.transactions.toArray();
    expect(txs).toHaveLength(1);
    expect(txs[0]).toMatchObject({ kind: "income", amount: M(200_000), clientId, jobId });
    const payments = await d.clientPayments.toArray();
    expect(payments[0].transactionId).toBe(txs[0].id);
    expect(txs[0].clientPaymentId).toBe(payments[0].id);

    const balances = summarizeBalances(await d.accounts.toArray(), txs);
    expect(balances.liquid).toBe(M(200_000)); // the 300.000 owed is NOT liquid
    expect(totalReceivables(await views())).toBe(M(300_000));
  });

  it("does not create income when no receiving account is chosen", async () => {
    const clientId = await createClient({ name: "Caro", status: "active", tags: [] });
    const jobId = await createJob({ clientId, title: "Web", requestedAt: TODAY, price: M(100_000), priority: "low", statusId: await statusId("new") });
    await addClientPayment({ jobId, amount: M(50_000), date: TODAY, kind: "advance" });
    expect(await db().transactions.count()).toBe(0);
    expect(await db().clientPayments.count()).toBe(1);
  });

  it("rejects payments above the agreed price unless the price is explicitly adjusted", async () => {
    const accountId = await bank();
    const clientId = await createClient({ name: "Dani", status: "active", tags: [] });
    const jobId = await createJob({ clientId, title: "Fotos", requestedAt: TODAY, price: M(300_000), priority: "low", statusId: await statusId("new") });
    await addClientPayment({ jobId, amount: M(200_000), date: TODAY, kind: "advance", accountId });
    await expect(addClientPayment({ jobId, amount: M(150_000), date: TODAY, kind: "final", accountId })).rejects.toMatchObject({ code: "overpayment" });
    expect(await db().transactions.count()).toBe(1);
    await addClientPayment({ jobId, amount: M(150_000), date: TODAY, kind: "final", accountId, adjustPrice: true });
    expect((await db().jobs.get(jobId))!.price).toBe(M(350_000));
    await expect(updateJob(jobId, { price: M(100_000) })).rejects.toThrow(/no puede ser menor/);
  });

  it("keeps payment and income movement consistent on edit and void", async () => {
    const accountId = await bank();
    const other = await createAccount({ name: "Nequi", type: "wallet", openingBalance: 0, openingDate: TODAY, spendable: true, color: "violet" });
    const clientId = await createClient({ name: "Eva", status: "active", tags: [] });
    const jobId = await createJob({ clientId, title: "Reel", requestedAt: TODAY, price: M(400_000), priority: "low", statusId: await statusId("new") });
    const paymentId = await addClientPayment({ jobId, amount: M(100_000), date: TODAY, kind: "advance", accountId });

    await updateClientPayment(paymentId, { amount: M(150_000), accountId: other });
    let txs = await db().transactions.toArray();
    expect(txs).toHaveLength(1);
    expect(txs[0]).toMatchObject({ amount: M(150_000), accountId: other });

    // Editing the movement from Finanzas updates the payment too.
    await updateTransaction(txs[0].id, { amount: M(120_000) });
    expect((await db().clientPayments.get(paymentId))!.amount).toBe(M(120_000));
    await expect(updateTransaction(txs[0].id, { amount: M(900_000) })).rejects.toThrow(/precio acordado/);

    // Removing the account removes the income; voiding the payment leaves nothing behind.
    await updateClientPayment(paymentId, { accountId: null });
    expect(await db().transactions.count()).toBe(0);
    await updateClientPayment(paymentId, { accountId });
    expect(await db().transactions.count()).toBe(1);
    await deleteClientPayment(paymentId);
    expect(await db().transactions.count()).toBe(0);
    expect(await db().clientPayments.count()).toBe(0);
  });

  it("voids the client payment when its movement is deleted from Finanzas", async () => {
    const accountId = await bank();
    const clientId = await createClient({ name: "Fer", status: "active", tags: [] });
    const jobId = await createJob(
      { clientId, title: "Banner", requestedAt: TODAY, price: M(90_000), priority: "low", statusId: await statusId("new") },
      { amount: M(90_000), date: TODAY, accountId },
    );
    const [t] = await db().transactions.toArray();
    await deleteTransaction(t.id);
    expect(await db().clientPayments.count()).toBe(0);
    const payments = paymentsByJob(await db().clientPayments.toArray()).get(jobId) ?? [];
    expect(jobFinance((await db().jobs.get(jobId))!, payments, TODAY).balance).toBe(M(90_000));
  });

  it("deleting a job reverts its income movements", async () => {
    const accountId = await bank();
    const clientId = await createClient({ name: "Gabi", status: "active", tags: [] });
    const jobId = await createJob(
      { clientId, title: "Post", requestedAt: TODAY, price: M(50_000), priority: "low", statusId: await statusId("new") },
      { amount: M(20_000), date: TODAY, accountId },
    );
    await deleteJob(jobId);
    expect(await db().transactions.count()).toBe(0);
    expect(await db().clientPayments.count()).toBe(0);
  });
});

describe("Flujo B y C: agenda conectada", () => {
  it("shows job deliveries and obligations in the agenda, following date changes", async () => {
    const accountId = await bank(1_000_000);
    const clientId = await createClient({ name: "Hugo", status: "active", tags: [] });
    const jobId = await createJob({ clientId, title: "Catálogo", requestedAt: TODAY, dueDate: "2026-11-13", price: M(100_000), priority: "low", statusId: await statusId("doing") });
    const obligationId = await createObligation({ name: "Internet", type: "utilities", amount: M(90_000), startDate: "2026-11-15", recurrence: { freq: "monthly", interval: 1 }, accountId });
    const agenda = async () => {
      const d = db();
      return buildAgenda({
        from: TODAY,
        to: "2026-11-30",
        today: TODAY,
        events: await d.events.toArray(),
        tasks: await d.tasks.toArray(),
        jobViews: await views(),
        obligations: await d.obligations.toArray(),
        plannedIncomes: await d.plannedIncomes.toArray(),
        transactions: await d.transactions.toArray(),
        clients: await d.clients.toArray(),
      });
    };
    let items = await agenda();
    expect(items.find((i) => i.kind === "delivery")!.date).toBe("2026-11-13");
    expect(items.find((i) => i.kind === "obligation")).toMatchObject({ date: "2026-11-15", done: false });

    await updateJob(jobId, { dueDate: "2026-11-25" });
    await payObligation({ obligationId, dueDate: "2026-11-15", amount: M(90_000), date: TODAY, accountId });
    items = await agenda();
    expect(items.filter((i) => i.kind === "delivery").map((i) => i.date)).toEqual(["2026-11-25"]);
    expect(items.find((i) => i.kind === "obligation")).toMatchObject({ done: true });
    const balances = summarizeBalances(await db().accounts.toArray(), await db().transactions.toArray());
    expect(balances.liquid).toBe(M(910_000));
  });

  it("pays a credit card obligation as a transfer, not as a second expense", async () => {
    const accountId = await bank(1_000_000);
    const visa = await createAccount({ name: "Visa", type: "credit", openingBalance: 0, openingDate: TODAY, spendable: false, color: "slate", creditLimit: M(2_000_000) });
    await createTransaction({ kind: "expense", amount: M(300_000), date: TODAY, accountId: visa });
    const obligationId = await createObligation({ name: "Tarjeta", type: "card", amount: M(300_000), startDate: "2026-11-25", recurrence: null, accountId, cardAccountId: visa });
    await payObligation({ obligationId, dueDate: "2026-11-25", amount: M(300_000), date: TODAY, accountId });
    const txs = await db().transactions.toArray();
    expect(txs.filter((t) => t.kind === "expense")).toHaveLength(1);
    const b = summarizeBalances(await db().accounts.toArray(), txs);
    expect(b.creditDebt).toBe(0);
    expect(b.liquid).toBe(M(700_000));
  });
});

describe("acceptance: escenario de agenda", () => {
  it("creates five tasks, completes three, reschedules one and lists the pending ones", async () => {
    const ids: string[] = [];
    for (const title of ["Uno", "Dos", "Tres", "Cuatro", "Cinco"]) ids.push(await createTask({ title, date: TODAY }));
    for (const id of ids.slice(0, 3)) await setTaskDone(id, true);
    await rescheduleTask(ids[3], "2026-11-14");
    const tasks = await db().tasks.toArray();
    const pending = tasks.filter((t) => t.status === "todo");
    expect(pending.map((t) => t.title).sort()).toEqual(["Cinco", "Cuatro"]);
    expect(tasks.find((t) => t.id === ids[3])!.date).toBe("2026-11-14");
    expect(tasks.filter((t) => t.status === "done")).toHaveLength(3);
  });

  it("spawns the next instance of a recurring task exactly once", async () => {
    const id = await createTask({ title: "Revisar finanzas", date: "2026-01-31", recurrence: { freq: "monthly", interval: 1 } });
    const next = await setTaskDone(id, true);
    expect(next).not.toBeNull();
    expect((await db().tasks.get(next!))!.date).toBe("2026-02-28");
    await setTaskDone(id, false);
    expect(await setTaskDone(id, true)).toBeNull(); // re-completing does not duplicate
    const third = await setTaskDone(next!, true);
    expect((await db().tasks.get(third!))!.date).toBe("2026-03-31"); // anchored on the 31st, no drift
    expect(await db().tasks.count()).toBe(3);
  });

  it("counts postponements", async () => {
    const id = await createTask({ title: "Llamar", date: "2026-11-09" });
    await postponeTask(id, 1, TODAY);
    const t = await db().tasks.get(id);
    expect(t!.date).toBe("2026-11-12"); // overdue tasks move from today
    expect(t!.postponed).toBe(1);
  });
});

describe("acceptance: escenario de hábitos", () => {
  it("computes streaks on scheduled days only (Monday to Friday)", async () => {
    const habitId = await createHabit({ name: "Ejercicio", icon: "dumbbell", color: "rose", schedule: { type: "days", days: [1, 2, 3, 4, 5] }, target: 1, startDate: "2026-11-02" });
    // Week of Nov 2: Mon–Fri all done. Weekend skipped (not scheduled). Week of Nov 9: Mon, Tue done.
    for (const d of ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06", "2026-11-09", "2026-11-10"]) {
      await setHabitCount(habitId, d, 1);
    }
    const habit = (await db().habits.get(habitId))!;
    const index = logsIndex(await db().habitLogs.toArray());
    // Today (Wed 11) is still pending: the streak is not broken yet.
    expect(currentStreak(habit, index, TODAY)).toBe(7);
    await setHabitCount(habitId, TODAY, 1);
    const index2 = logsIndex(await db().habitLogs.toArray());
    expect(currentStreak(habit, index2, TODAY)).toBe(8);
    expect(bestStreak(habit, index2, TODAY)).toBe(8);
    // Missing Thursday breaks the streak the next scheduled day.
    expect(currentStreak(habit, index2, "2026-11-13")).toBe(0);
    // Logging twice on the same day never duplicates.
    await setHabitCount(habitId, TODAY, 1);
    expect(await db().habitLogs.where("habitId").equals(habitId).count()).toBe(8);
  });
});

describe("backup", () => {
  it("exports and restores every table", async () => {
    await bank(123_000);
    await createTask({ title: "Respaldar" });
    const backup = parseBackup(JSON.stringify(await exportBackup()));
    const fresh = new LifeOSDB(`test-${uid()}`);
    setDB(fresh);
    await restoreBackup(backup);
    expect(await db().accounts.count()).toBe(1);
    expect((await db().tasks.toArray())[0].title).toBe("Respaldar");
    expect(() => parseBackup("{}")).toThrow(/respaldo/);
  });
});
