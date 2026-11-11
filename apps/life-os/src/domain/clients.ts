import { addDays, diffDays, type DateStr } from "@/lib/dates";
import { sumMinor, type Minor } from "@/lib/money";
import type { Client, ClientPayment, Job, JobStatus, JobStatusKind } from "@/db/types";

export type PaymentState = "unbilled" | "unpaid" | "partial" | "paid" | "overdue";

export const PAYMENT_STATE_LABEL: Record<PaymentState, string> = {
  unbilled: "Sin precio",
  unpaid: "Sin pagos",
  partial: "Abonado",
  paid: "Pagado",
  overdue: "Cobro vencido",
};

export const OPEN_KINDS: JobStatusKind[] = ["new", "todo", "doing", "review"];

export interface JobFinance {
  paid: Minor;
  balance: Minor;
  state: PaymentState;
  payments: ClientPayment[];
}

export function paymentsByJob(payments: ClientPayment[]): Map<string, ClientPayment[]> {
  const map = new Map<string, ClientPayment[]>();
  for (const p of payments) {
    const list = map.get(p.jobId);
    if (list) list.push(p);
    else map.set(p.jobId, [p]);
  }
  for (const list of map.values()) list.sort((a, b) => a.date.localeCompare(b.date));
  return map;
}

/** Saldo pendiente = precio acordado − pagos registrados. */
export function jobFinance(job: Job, payments: ClientPayment[], today: DateStr, cancelled = false): JobFinance {
  const paid = sumMinor(payments.map((p) => p.amount));
  const balance = cancelled ? 0 : Math.max(0, job.price - paid);
  let state: PaymentState;
  if (job.price <= 0) state = paid > 0 ? "paid" : "unbilled";
  else if (balance === 0) state = "paid";
  else if (job.paymentDueDate && job.paymentDueDate < today) state = "overdue";
  else if (paid > 0) state = "partial";
  else state = "unpaid";
  return { paid, balance, state, payments };
}

export interface JobView {
  job: Job;
  client: Client | undefined;
  status: JobStatus | undefined;
  kind: JobStatusKind;
  finance: JobFinance;
  isOpen: boolean;
  isOverdue: boolean;
  dueSoon: boolean;
  daysToDue: number | null;
}

export function buildJobViews(
  jobs: Job[],
  clients: Client[],
  statuses: JobStatus[],
  payments: ClientPayment[],
  today: DateStr,
): JobView[] {
  const clientById = new Map(clients.map((c) => [c.id, c]));
  const statusById = new Map(statuses.map((s) => [s.id, s]));
  const byJob = paymentsByJob(payments);
  return jobs.map((job) => {
    const status = statusById.get(job.statusId);
    const kind = status?.kind ?? "new";
    const isOpen = OPEN_KINDS.includes(kind);
    const daysToDue = job.dueDate ? diffDays(today, job.dueDate) : null;
    return {
      job,
      client: clientById.get(job.clientId),
      status,
      kind,
      finance: jobFinance(job, byJob.get(job.id) ?? [], today, kind === "cancelled"),
      isOpen,
      isOverdue: isOpen && daysToDue !== null && daysToDue < 0,
      dueSoon: isOpen && daysToDue !== null && daysToDue >= 0 && daysToDue <= 3,
      daysToDue,
    };
  });
}

export interface ClientSummary {
  client: Client;
  jobs: JobView[];
  billed: Minor;
  collected: Minor;
  balance: Minor;
  overdue: Minor;
  openJobs: number;
  lastActivity: string;
}

export function summarizeClients(clients: Client[], views: JobView[]): ClientSummary[] {
  const byClient = new Map<string, JobView[]>();
  for (const v of views) {
    const list = byClient.get(v.job.clientId);
    if (list) list.push(v);
    else byClient.set(v.job.clientId, [v]);
  }
  return clients.map((client) => {
    const jobs = byClient.get(client.id) ?? [];
    const billable = jobs.filter((j) => j.kind !== "cancelled");
    return {
      client,
      jobs,
      billed: sumMinor(billable.map((j) => j.job.price)),
      collected: sumMinor(jobs.map((j) => j.finance.paid)),
      balance: sumMinor(billable.map((j) => j.finance.balance)),
      overdue: sumMinor(billable.filter((j) => j.finance.state === "overdue").map((j) => j.finance.balance)),
      openJobs: jobs.filter((j) => j.isOpen && !j.job.archived).length,
      lastActivity: [client.updatedAt, ...jobs.map((j) => j.job.updatedAt)].sort().at(-1) ?? client.updatedAt,
    };
  });
}

export function totalReceivables(views: JobView[]): Minor {
  return sumMinor(views.filter((v) => v.kind !== "cancelled").map((v) => v.finance.balance));
}

/** Expected collection dates for receivables with a payment due date (uncertain income). */
export function receivablesByDate(views: JobView[], today: DateStr): Map<DateStr, Minor> {
  const map = new Map<DateStr, Minor>();
  for (const v of views) {
    if (v.finance.balance <= 0 || !v.job.paymentDueDate) continue;
    const d = v.job.paymentDueDate < today ? addDays(today, 1) : v.job.paymentDueDate;
    map.set(d, (map.get(d) ?? 0) + v.finance.balance);
  }
  return map;
}

/**
 * Validates a payment against the agreed price. Returns the excess (>0) when accepting the
 * payment would collect more than the price.
 */
export function paymentExcess(job: Job, existing: ClientPayment[], amount: Minor, ignoreId?: string): Minor {
  const others = sumMinor(existing.filter((p) => p.id !== ignoreId).map((p) => p.amount));
  return Math.max(0, others + amount - job.price);
}

export const CLIENT_STATUS_LABEL: Record<Client["status"], string> = {
  lead: "Prospecto",
  active: "Activo",
  paused: "En pausa",
  inactive: "Inactivo",
};

export const PRIORITY_LABEL: Record<Job["priority"], string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
  urgent: "Urgente",
};

export const PAYMENT_KIND_LABEL: Record<ClientPayment["kind"], string> = {
  advance: "Anticipo",
  partial: "Abono",
  final: "Pago final",
};
