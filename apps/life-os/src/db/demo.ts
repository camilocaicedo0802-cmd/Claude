/**
 * Demo data. It is written only into the separate "lifeos-demo" database, never into the
 * user's real records, and the UI shows a permanent "Modo demo" banner while it is active.
 */
import { addDays, addMonths, nowISO, startOfMonth, todayIn, type DateStr } from "@/lib/dates";
import { fromMajor } from "@/lib/money";
import { uid } from "@/lib/utils";
import type { LifeOSDB } from "./db";
import type {
  Account,
  CalendarEvent,
  Client,
  ClientPayment,
  Habit,
  HabitLog,
  Job,
  Obligation,
  PlannedIncome,
  Task,
  Transaction,
} from "./types";

function rng(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
}

const M = (pesos: number) => fromMajor(pesos);

export async function seedDemo(d: LifeOSDB) {
  if ((await d.accounts.count()) > 0) return; // already seeded
  const settings = await d.settings.get("app");
  const today = todayIn(settings?.timeZone);
  const now = nowISO();
  const ts = { createdAt: now, updatedAt: now };
  const rand = rng(42);
  const cats = await d.categories.toArray();
  const cat = (key: string) => cats.find((c) => c.systemKey === key)!.id;

  await d.settings.update("app", { userName: "Demo", onboardingCompleted: true, safetyReserve: M(200000) });

  const acc = (name: string, type: Account["type"], opening: number, color: string, extra: Partial<Account> = {}): Account => ({
    id: uid(),
    name,
    type,
    openingBalance: M(opening),
    openingDate: addDays(today, -60),
    spendable: type !== "savings" && type !== "credit",
    color,
    archived: false,
    order: 0,
    creditLimit: null,
    ...ts,
    ...extra,
  });
  const cash = acc("Efectivo", "cash", 150000, "amber");
  const bank = acc("Cuenta Bancolombia", "bank", 1800000, "iris");
  const nequi = acc("Nequi", "wallet", 250000, "violet");
  const savings = acc("Ahorros", "savings", 3000000, "emerald");
  const visa = acc("Tarjeta Visa", "credit", 0, "slate", { creditLimit: M(5000000) });
  const accounts = [cash, bank, nequi, savings, visa].map((a, i) => ({ ...a, order: i }));
  await d.accounts.bulkAdd(accounts);

  const txs: Transaction[] = [];
  const tx = (t: Partial<Transaction> & Pick<Transaction, "kind" | "amount" | "date" | "accountId">) =>
    txs.push({ id: uid(), ...ts, ...t } as Transaction);

  // Daily life over the last 40 days.
  for (let i = 40; i >= 0; i--) {
    const date = addDays(today, -i);
    if (rand() < 0.75) tx({ kind: "expense", amount: M(Math.round((12000 + rand() * 38000) / 100) * 100), date, accountId: rand() < 0.5 ? cash.id : nequi.id, categoryId: cat("food"), description: rand() < 0.5 ? "Mercado" : "Almuerzo" });
    if (rand() < 0.5) tx({ kind: "expense", amount: M(rand() < 0.6 ? 2950 * 2 : 18000), date, accountId: nequi.id, categoryId: cat("transport"), description: rand() < 0.6 ? "Transporte" : "Taxi" });
    if (rand() < 0.15) tx({ kind: "expense", amount: M(Math.round((25000 + rand() * 60000) / 1000) * 1000), date, accountId: visa.id, categoryId: cat("leisure"), description: rand() < 0.5 ? "Cine" : "Salida con amigos" });
    if (rand() < 0.07) tx({ kind: "expense", amount: M(Math.round((40000 + rand() * 120000) / 1000) * 1000), date, accountId: visa.id, categoryId: cat("shopping"), description: "Ropa" });
  }
  tx({ kind: "income", amount: M(2500000), date: addDays(startOfMonth(today), 0), accountId: bank.id, categoryId: cat("salary"), description: "Retainer agencia" });
  tx({ kind: "transfer", amount: M(300000), date: addDays(today, -6), accountId: bank.id, toAccountId: nequi.id, description: "Recarga Nequi" });

  // Obligations.
  const obl = (name: string, type: Obligation["type"], amount: number, start: DateStr, extra: Partial<Obligation> = {}): Obligation => ({
    id: uid(),
    name,
    type,
    amount: M(amount),
    startDate: start,
    recurrence: { freq: "monthly", interval: 1 },
    accountId: bank.id,
    categoryId: null,
    active: true,
    settled: {},
    ...ts,
    ...extra,
  });
  const monthStart = startOfMonth(today);
  const rent = obl("Arriendo", "rent", 1100000, addDays(monthStart, 4), { categoryId: cat("housing") });
  const internet = obl("Internet y TV", "utilities", 98000, addDays(monthStart, 14), { categoryId: cat("utilities") });
  const energy = obl("Energía", "utilities", 85000, addDays(monthStart, 17), { categoryId: cat("utilities") });
  const phone = obl("Plan celular", "utilities", 55000, addDays(monthStart, 21), { categoryId: cat("utilities"), accountId: nequi.id });
  const spotify = obl("Spotify", "subscription", 17900, addDays(monthStart, 9), { categoryId: cat("subscriptions"), accountId: visa.id });
  const loan = obl("Cuota préstamo portátil", "installment", 320000, addDays(monthStart, 27), { categoryId: cat("debts"), recurrence: { freq: "monthly", interval: 1, count: 12 } });
  const card = obl("Pago tarjeta Visa", "card", 600000, addDays(monthStart, 24), { cardAccountId: visa.id });
  const obligations = [rent, internet, energy, phone, spotify, loan, card];
  await d.obligations.bulkAdd(obligations);
  // Pay the occurrences already due this month.
  for (const o of obligations) {
    if (o.startDate <= addDays(today, -1) && o.id !== energy.id) {
      const isCard = o.type === "card";
      tx({
        kind: isCard ? "transfer" : "expense",
        amount: o.amount,
        date: o.startDate,
        accountId: o.accountId!,
        toAccountId: isCard ? visa.id : null,
        categoryId: isCard ? null : o.categoryId,
        description: `Pago: ${o.name}`,
        obligationId: o.id,
        occurrenceDate: o.startDate,
      });
    }
  }

  const planned: PlannedIncome = {
    id: uid(),
    name: "Retainer agencia",
    amount: M(2500000),
    startDate: addMonths(monthStart, 1),
    recurrence: { freq: "monthly", interval: 1 },
    confirmed: true,
    accountId: bank.id,
    categoryId: cat("salary"),
    active: true,
    settled: {},
    ...ts,
  };
  await d.plannedIncomes.add(planned);

  await d.budgets.bulkAdd([
    { id: uid(), categoryId: cat("food"), amount: M(900000), ...ts },
    { id: uid(), categoryId: cat("transport"), amount: M(250000), ...ts },
    { id: uid(), categoryId: cat("leisure"), amount: M(250000), ...ts },
    { id: uid(), categoryId: cat("shopping"), amount: M(200000), ...ts },
  ]);

  const emergency = { id: uid(), name: "Fondo de emergencia", target: M(6000000), targetDate: null, isEmergencyFund: true, accountId: savings.id, color: "emerald", archived: false, ...ts };
  const trip = { id: uid(), name: "Viaje a Cartagena", target: M(2000000), targetDate: addMonths(today, 6), isEmergencyFund: false, accountId: savings.id, color: "sky", archived: false, ...ts };
  await d.goals.bulkAdd([emergency, trip]);
  await d.goalContributions.bulkAdd([
    { id: uid(), goalId: emergency.id, amount: M(2600000), date: addDays(today, -50), note: "Saldo inicial", ...ts },
    { id: uid(), goalId: trip.id, amount: M(400000), date: addDays(today, -20), ...ts },
  ]);

  // Clients and jobs.
  const statuses = (await d.jobStatuses.toArray()).sort((a, b) => a.order - b.order);
  const st = (kind: string) => statuses.find((s) => s.kind === kind)!.id;
  const client = (name: string, company: string, service: string, status: Client["status"], tags: string[]): Client => ({
    id: uid(),
    name,
    company,
    phone: "3001234567",
    whatsapp: "3001234567",
    email: `${name.split(" ")[0].toLowerCase()}@ejemplo.com`,
    serviceType: service,
    status,
    tags,
    notes: undefined,
    archived: false,
    ...ts,
  });
  const c1 = client("Laura Gómez", "Café Origen", "Edición de video", "active", ["recurrente"]);
  const c2 = client("Andrés Ruiz", "Ruiz Arquitectos", "Diseño de marca", "active", ["nuevo"]);
  const c3 = client("Valentina Mora", "Estudio Mora", "Motion graphics", "active", []);
  const c4 = client("Fundación Semilla", "", "Contenido para redes", "paused", ["ONG"]);
  await d.clients.bulkAdd([c1, c2, c3, c4]);

  const job = (c: Client, title: string, price: number, status: string, due: number | null, payDue: number | null, priority: Job["priority"] = "medium"): Job => ({
    id: uid(),
    clientId: c.id,
    title,
    description: undefined,
    requestedAt: addDays(today, -20),
    dueDate: due === null ? null : addDays(today, due),
    price: M(price),
    priority,
    statusId: st(status),
    paymentDueDate: payDue === null ? null : addDays(today, payDue),
    tags: [],
    archived: false,
    statusChangedAt: now,
    ...ts,
  });
  const j1 = job(c1, "Reels de lanzamiento (x4)", 800000, "doing", 1, 10, "high");
  const j2 = job(c2, "Manual de marca", 1500000, "review", 4, 15);
  const j3 = job(c3, "Animación de logo", 500000, "delivered", -5, -2);
  const j4 = job(c1, "Video institucional", 1200000, "todo", 12, 30);
  const j5 = job(c4, "Parrilla de contenido", 600000, "new", 9, null, "low");
  const j6 = job(c3, "Intro para YouTube", 350000, "done", -1, 5);
  await d.jobs.bulkAdd([j1, j2, j3, j4, j5, j6]);

  const clientsCat = cat("clients");
  const pay = (j: Job, amount: number, date: DateStr, kind: ClientPayment["kind"], accountId: string | null) => {
    const paymentId = uid();
    let transactionId: string | null = null;
    if (accountId) {
      transactionId = uid();
      txs.push({ id: transactionId, kind: "income", amount: M(amount), date, accountId, categoryId: clientsCat, description: `${kind === "advance" ? "Anticipo" : "Abono"}: ${j.title}`, clientId: j.clientId, jobId: j.id, clientPaymentId: paymentId, ...ts });
    }
    return { id: paymentId, clientId: j.clientId, jobId: j.id, amount: M(amount), date, kind, accountId, transactionId, ...ts } satisfies ClientPayment;
  };
  await d.clientPayments.bulkAdd([
    pay(j1, 300000, addDays(today, -15), "advance", bank.id),
    pay(j2, 750000, addDays(today, -12), "advance", bank.id),
    pay(j3, 200000, addDays(today, -25), "advance", nequi.id),
    pay(j6, 350000, addDays(today, -2), "final", bank.id),
  ]);
  await d.jobTemplates.bulkAdd([
    { id: uid(), name: "Reel para redes", description: "Edición de un reel vertical de hasta 60 s con subtítulos.", price: M(200000), durationDays: 3, priority: "medium", ...ts },
    { id: uid(), name: "Animación de logo", description: "Animación 2D de logo, 5–8 s, entrega en MP4 y GIF.", price: M(450000), durationDays: 7, priority: "medium", ...ts },
  ]);
  await d.activities.bulkAdd(
    [c1, c2, c3, c4].map((c) => ({ id: uid(), at: now, clientId: c.id, type: "client" as const, message: "Cliente creado (demo)" })),
  );

  await d.transactions.bulkAdd(txs);

  // Tasks.
  const task = (title: string, date: DateStr | null, extra: Partial<Task> = {}): Task => ({
    id: uid(),
    title,
    date,
    time: null,
    durationMin: null,
    priority: 0,
    status: "todo",
    completedAt: null,
    area: "personal",
    recurrence: null,
    seriesId: null,
    clientId: null,
    jobId: null,
    followUp: null,
    subtasks: [],
    postponed: 0,
    order: 0,
    ...ts,
    ...extra,
  });
  const t1 = task("Exportar reels de Café Origen", today, { priority: 3, area: "clientes", clientId: c1.id, jobId: j1.id, durationMin: 120, time: "09:00" });
  const t2 = task("Revisar correcciones del manual", today, { priority: 2, area: "clientes", clientId: c2.id, jobId: j2.id, durationMin: 60 });
  const t3 = task("Cobrar saldo de la animación de logo", today, { priority: 2, area: "clientes", clientId: c3.id, jobId: j3.id, followUp: "collect" });
  const t4 = task("Pagar la energía", addDays(today, -1), { priority: 1, area: "finanzas" });
  const t5 = task("Ir al gimnasio", today, { area: "salud", time: "18:30", durationMin: 60, status: "done", completedAt: now });
  const t6 = task("Planear contenido de la semana", addDays(today, 1), { area: "trabajo", durationMin: 45, recurrence: { freq: "weekly", interval: 1 }, seriesStart: addDays(today, 1) });
  t6.seriesId = t6.id;
  const t7 = task("Comprar regalo de cumpleaños de mamá", addDays(today, 3), { area: "personal" });
  const t8 = task("Llamar a la Fundación Semilla", addDays(today, 2), { area: "clientes", clientId: c4.id, followUp: "contact" });
  const t9 = task("Leer sobre presupuesto base cero", null, { area: "estudio" });
  await d.tasks.bulkAdd([t1, t2, t3, t4, t5, t6, t7, t8, t9]);
  await d.dayPlans.put({ date: today, priorities: [t1.id, t2.id, t3.id] });

  const ev = (title: string, date: DateStr, start: string | null, end: string | null, category: CalendarEvent["category"], extra: Partial<CalendarEvent> = {}): CalendarEvent => ({
    id: uid(),
    title,
    date,
    startTime: start,
    endTime: end,
    allDay: !start,
    recurrence: null,
    category,
    exceptions: [],
    ...ts,
    ...extra,
  });
  await d.events.bulkAdd([
    ev("Llamada con Andrés (manual de marca)", today, "11:00", "11:45", "clientes", { clientId: c2.id }),
    ev("Almuerzo familiar", addDays(today, 2), "13:00", "15:00", "familia"),
    ev("Clase de inglés", addDays(today, -2), "19:00", "20:00", "estudio", { recurrence: { freq: "weekly", interval: 1 } }),
    ev("Cita médica", addDays(today, 5), "08:00", "09:00", "salud"),
  ]);

  // Habits with history.
  const habit = (name: string, icon: string, color: string, schedule: Habit["schedule"], target = 1, unit?: string): Habit => ({
    id: uid(),
    name,
    icon,
    color,
    schedule,
    target,
    unit,
    startDate: addDays(today, -45),
    archived: false,
    order: 0,
    ...ts,
  });
  const habits = [
    habit("Hacer ejercicio", "dumbbell", "rose", { type: "days", days: [1, 2, 3, 4, 5] }),
    habit("Leer 20 minutos", "book-open", "iris", { type: "daily" }),
    habit("Tomar agua", "glass-water", "sky", { type: "daily" }, 8, "vasos"),
    habit("Planificar mi día", "list-checks", "amber", { type: "daily" }),
  ].map((h, i) => ({ ...h, order: i }));
  await d.habits.bulkAdd(habits);
  const logs: HabitLog[] = [];
  for (const h of habits) {
    for (let i = 45; i >= 1; i--) {
      const date = addDays(today, -i);
      const p = i < 6 ? 0.95 : 0.72;
      if (rand() < p) logs.push({ id: `${h.id}:${date}`, habitId: h.id, date, count: h.target, updatedAt: now });
    }
  }
  logs.push({ id: `${habits[3].id}:${today}`, habitId: habits[3].id, date: today, count: 1, updatedAt: now });
  logs.push({ id: `${habits[2].id}:${today}`, habitId: habits[2].id, date: today, count: 3, updatedAt: now });
  await d.habitLogs.bulkPut(logs);
}
