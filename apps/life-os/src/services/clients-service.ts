import { db } from "@/db/db";
import type { Client, ClientPayment, Job, JobStatus, JobTemplate, Transaction } from "@/db/types";
import { nowISO, type DateStr } from "@/lib/dates";
import { formatMoney, type Minor } from "@/lib/money";
import { uid } from "@/lib/utils";
import { PAYMENT_KIND_LABEL } from "@/domain/clients";
import { DomainError, logActivity } from "./common";

// ── Clients ──────────────────────────────────────────────────────────────────

export type ClientInput = Omit<Client, "id" | "createdAt" | "updatedAt" | "archived">;

export async function createClient(input: ClientInput): Promise<string> {
  const name = input.name.trim();
  if (!name) throw new DomainError("El cliente necesita un nombre.");
  const now = nowISO();
  const client: Client = { ...input, name, tags: input.tags ?? [], id: uid(), archived: false, createdAt: now, updatedAt: now };
  const d = db();
  await d.transaction("rw", [d.clients, d.activities], async () => {
    await d.clients.add(client);
    await logActivity({ clientId: client.id, type: "client", message: "Cliente creado" });
  });
  return client.id;
}

export async function updateClient(id: string, patch: Partial<ClientInput & { archived: boolean }>) {
  const d = db();
  await d.transaction("rw", [d.clients, d.activities], async () => {
    await d.clients.update(id, { ...patch, updatedAt: nowISO() });
    if (patch.archived !== undefined) {
      await logActivity({ clientId: id, type: "client", message: patch.archived ? "Cliente archivado" : "Cliente restaurado" });
    }
  });
}

export async function addClientNote(clientId: string, text: string) {
  if (!text.trim()) return;
  const d = db();
  await d.transaction("rw", [d.clients, d.activities], async () => {
    await logActivity({ clientId, type: "note", message: text.trim() });
    await d.clients.update(clientId, { updatedAt: nowISO() });
  });
}

/** Clients with history are archived, never deleted: jobs and payments stay intact. */
export async function deleteClient(id: string): Promise<"deleted" | "archived"> {
  const d = db();
  return d.transaction("rw", [d.clients, d.jobs, d.activities], async () => {
    const jobs = await d.jobs.where("clientId").equals(id).count();
    if (jobs > 0) {
      await d.clients.update(id, { archived: true, updatedAt: nowISO() });
      await logActivity({ clientId: id, type: "client", message: "Cliente archivado" });
      return "archived" as const;
    }
    await d.activities.where("clientId").equals(id).delete();
    await d.clients.delete(id);
    return "deleted" as const;
  });
}

// ── Jobs ─────────────────────────────────────────────────────────────────────

export type JobInput = Omit<Job, "id" | "createdAt" | "updatedAt" | "archived" | "statusChangedAt" | "tags"> & { tags?: string[] };

export interface InitialPayment {
  amount: Minor;
  date: DateStr;
  accountId?: string | null;
  kind?: ClientPayment["kind"];
}

/**
 * Creates a job, optionally with its advance payment (Flujo A). The advance becomes a real
 * income only when a receiving account is chosen.
 */
export async function createJob(input: JobInput, advance?: InitialPayment): Promise<string> {
  const title = input.title.trim();
  if (!title) throw new DomainError("El trabajo necesita un nombre.");
  if (!input.clientId) throw new DomainError("Elige un cliente.");
  if (input.price < 0) throw new DomainError("El precio no puede ser negativo.");
  if (advance && advance.amount > input.price) {
    throw new DomainError("El anticipo no puede superar el precio acordado.");
  }
  const now = nowISO();
  const job: Job = { ...input, title, tags: input.tags ?? [], id: uid(), archived: false, statusChangedAt: now, createdAt: now, updatedAt: now };
  const d = db();
  await d.transaction("rw", [d.jobs, d.clients, d.clientPayments, d.transactions, d.categories, d.activities], async () => {
    await d.jobs.add(job);
    await logActivity({ clientId: job.clientId, jobId: job.id, type: "job", message: `Trabajo creado: ${job.title}` });
    await d.clients.update(job.clientId, { updatedAt: now });
    if (advance && advance.amount > 0) {
      await insertPayment(job, { ...advance, kind: advance.kind ?? "advance" });
    }
  });
  return job.id;
}

export async function updateJob(id: string, patch: Partial<JobInput & { archived: boolean; tags: string[] }>) {
  const d = db();
  await d.transaction("rw", [d.jobs, d.clientPayments, d.activities], async () => {
    const job = await d.jobs.get(id);
    if (!job) throw new DomainError("El trabajo ya no existe.");
    if (patch.price !== undefined) {
      const paid = (await d.clientPayments.where("jobId").equals(id).toArray()).reduce((s, p) => s + p.amount, 0);
      if (patch.price < paid) {
        throw new DomainError(`Ya se registraron ${formatMoney(paid)} en pagos; el precio no puede ser menor.`);
      }
    }
    await d.jobs.update(id, { ...patch, updatedAt: nowISO() });
    if (patch.dueDate !== undefined && patch.dueDate !== job.dueDate) {
      await logActivity({ clientId: job.clientId, jobId: id, type: "job", message: patch.dueDate ? `Nueva fecha de entrega: ${patch.dueDate}` : "Fecha de entrega eliminada" });
    }
    if (patch.price !== undefined && patch.price !== job.price) {
      await logActivity({ clientId: job.clientId, jobId: id, type: "job", message: `Precio actualizado a ${formatMoney(patch.price)}` });
    }
    if (patch.archived !== undefined) {
      await logActivity({ clientId: job.clientId, jobId: id, type: "job", message: patch.archived ? "Trabajo archivado" : "Trabajo restaurado" });
    }
  });
}

export async function setJobStatus(id: string, statusId: string) {
  const d = db();
  await d.transaction("rw", [d.jobs, d.jobStatuses, d.activities], async () => {
    const job = await d.jobs.get(id);
    const status = await d.jobStatuses.get(statusId);
    if (!job || !status || job.statusId === statusId) return;
    const now = nowISO();
    await d.jobs.update(id, { statusId, statusChangedAt: now, updatedAt: now });
    await logActivity({ clientId: job.clientId, jobId: id, type: "status", message: `${job.title} → ${status.name}` });
  });
}

/** Deletes a job and voids its payments together with their linked income movements. */
export async function deleteJob(id: string) {
  const d = db();
  await d.transaction("rw", [d.jobs, d.clientPayments, d.transactions, d.tasks, d.events, d.activities], async () => {
    const job = await d.jobs.get(id);
    if (!job) return;
    const payments = await d.clientPayments.where("jobId").equals(id).toArray();
    for (const p of payments) if (p.transactionId) await d.transactions.delete(p.transactionId);
    await d.clientPayments.where("jobId").equals(id).delete();
    const now = nowISO();
    for (const t of await d.tasks.where("jobId").equals(id).toArray()) await d.tasks.update(t.id, { jobId: null, updatedAt: now });
    for (const e of await d.events.where("jobId").equals(id).toArray()) await d.events.update(e.id, { jobId: null, updatedAt: now });
    await d.jobs.delete(id);
    await logActivity({ clientId: job.clientId, type: "job", message: `Trabajo eliminado: ${job.title}` });
  });
}

// ── Payments ─────────────────────────────────────────────────────────────────

export interface PaymentInput {
  jobId: string;
  amount: Minor;
  date: DateStr;
  kind: ClientPayment["kind"];
  accountId?: string | null;
  note?: string;
  /** Explicit confirmation to raise the agreed price when the payment exceeds it. */
  adjustPrice?: boolean;
}

async function clientsCategoryId(): Promise<string | null> {
  const cat = await db().categories.where("systemKey").equals("clients").first();
  return cat?.id ?? null;
}

async function insertPayment(job: Job, input: Omit<PaymentInput, "jobId">): Promise<string> {
  const d = db();
  const now = nowISO();
  const paymentId = uid();
  let transactionId: string | null = null;
  if (input.accountId) {
    transactionId = uid();
    const tx: Transaction = {
      id: transactionId,
      kind: "income",
      amount: input.amount,
      date: input.date,
      accountId: input.accountId,
      categoryId: await clientsCategoryId(),
      description: `${PAYMENT_KIND_LABEL[input.kind]}: ${job.title}`,
      clientId: job.clientId,
      jobId: job.id,
      clientPaymentId: paymentId,
      createdAt: now,
      updatedAt: now,
    };
    await d.transactions.add(tx);
  }
  const payment: ClientPayment = {
    id: paymentId,
    clientId: job.clientId,
    jobId: job.id,
    amount: input.amount,
    date: input.date,
    kind: input.kind,
    accountId: input.accountId ?? null,
    transactionId,
    note: input.note?.trim() || undefined,
    createdAt: now,
    updatedAt: now,
  };
  await d.clientPayments.add(payment);
  await logActivity({
    clientId: job.clientId,
    jobId: job.id,
    type: "payment",
    message: `${PAYMENT_KIND_LABEL[input.kind]} de ${formatMoney(input.amount)} · ${job.title}${transactionId ? "" : " (sin cuenta receptora)"}`,
  });
  return paymentId;
}

/**
 * Registers a client payment. It never lets payments exceed the agreed price silently:
 * the caller must pass `adjustPrice` after the user confirms, and the price is raised to match.
 */
export async function addClientPayment(input: PaymentInput): Promise<string> {
  if (!Number.isSafeInteger(input.amount) || input.amount <= 0) throw new DomainError("El valor del pago debe ser mayor que cero.");
  const d = db();
  return d.transaction("rw", [d.jobs, d.clientPayments, d.transactions, d.categories, d.activities, d.clients], async () => {
    const job = await d.jobs.get(input.jobId);
    if (!job) throw new DomainError("El trabajo ya no existe.");
    const existing = await d.clientPayments.where("jobId").equals(job.id).toArray();
    const paid = existing.reduce((s, p) => s + p.amount, 0);
    const excess = paid + input.amount - job.price;
    if (excess > 0) {
      if (!input.adjustPrice) {
        throw new DomainError(
          `Este pago supera el saldo pendiente por ${formatMoney(excess)}. Confirma si quieres ajustar el precio acordado.`,
          "overpayment",
          { excess },
        );
      }
      await d.jobs.update(job.id, { price: job.price + excess, updatedAt: nowISO() });
      await logActivity({ clientId: job.clientId, jobId: job.id, type: "job", message: `Precio ajustado a ${formatMoney(job.price + excess)} por un pago mayor` });
      job.price += excess;
    }
    const id = await insertPayment(job, input);
    await d.clients.update(job.clientId, { updatedAt: nowISO() });
    return id;
  });
}

/** Edits a payment and keeps its income movement in sync (create, update or remove it). */
export async function updateClientPayment(id: string, patch: Partial<Omit<PaymentInput, "jobId" | "adjustPrice">>) {
  const d = db();
  await d.transaction("rw", [d.jobs, d.clientPayments, d.transactions, d.categories, d.activities], async () => {
    const payment = await d.clientPayments.get(id);
    if (!payment) throw new DomainError("El pago ya no existe.");
    const job = await d.jobs.get(payment.jobId);
    if (!job) throw new DomainError("El trabajo ya no existe.");
    const next = { ...payment, ...patch };
    if (next.amount <= 0) throw new DomainError("El valor del pago debe ser mayor que cero.");
    const others = (await d.clientPayments.where("jobId").equals(job.id).toArray()).filter((p) => p.id !== id);
    if (others.reduce((s, p) => s + p.amount, 0) + next.amount > job.price) {
      throw new DomainError("Con ese valor los pagos superarían el precio acordado.");
    }
    const now = nowISO();
    let transactionId = payment.transactionId ?? null;
    if (next.accountId) {
      if (transactionId && (await d.transactions.get(transactionId))) {
        await d.transactions.update(transactionId, { amount: next.amount, date: next.date, accountId: next.accountId, updatedAt: now });
      } else {
        transactionId = uid();
        await d.transactions.add({
          id: transactionId,
          kind: "income",
          amount: next.amount,
          date: next.date,
          accountId: next.accountId,
          categoryId: await clientsCategoryId(),
          description: `${PAYMENT_KIND_LABEL[next.kind]}: ${job.title}`,
          clientId: job.clientId,
          jobId: job.id,
          clientPaymentId: id,
          createdAt: now,
          updatedAt: now,
        });
      }
    } else if (transactionId) {
      await d.transactions.delete(transactionId);
      transactionId = null;
    }
    await d.clientPayments.put({ ...next, accountId: next.accountId ?? null, transactionId, updatedAt: now });
    await logActivity({ clientId: job.clientId, jobId: job.id, type: "payment", message: `Pago editado: ${formatMoney(next.amount)}` });
  });
}

/** Voids a payment and reverts its income movement. */
export async function deleteClientPayment(id: string) {
  const d = db();
  await d.transaction("rw", [d.clientPayments, d.transactions, d.activities], async () => {
    const payment = await d.clientPayments.get(id);
    if (!payment) return;
    if (payment.transactionId) await d.transactions.delete(payment.transactionId);
    await d.clientPayments.delete(id);
    await logActivity({ clientId: payment.clientId, jobId: payment.jobId, type: "payment", message: `Pago anulado: ${formatMoney(payment.amount)}` });
  });
}

// ── Statuses and templates ───────────────────────────────────────────────────

export async function saveJobStatus(status: Omit<JobStatus, "id" | "order"> & { id?: string; order?: number }) {
  const d = db();
  if (!status.name.trim()) throw new DomainError("El estado necesita un nombre.");
  if (status.id) {
    await d.jobStatuses.update(status.id, { name: status.name.trim(), kind: status.kind, color: status.color });
    return status.id;
  }
  const order = status.order ?? (await d.jobStatuses.count());
  const id = uid();
  await d.jobStatuses.add({ id, name: status.name.trim(), kind: status.kind, color: status.color, order });
  return id;
}

export async function reorderJobStatuses(ids: string[]) {
  const d = db();
  await d.transaction("rw", d.jobStatuses, async () => {
    for (const [i, id] of ids.entries()) await d.jobStatuses.update(id, { order: i });
  });
}

export async function deleteJobStatus(id: string) {
  const d = db();
  await d.transaction("rw", [d.jobStatuses, d.jobs], async () => {
    const used = await d.jobs.where("statusId").equals(id).count();
    if (used > 0) throw new DomainError(`Hay ${used} trabajo(s) en este estado. Muévelos antes de eliminarlo.`);
    if ((await d.jobStatuses.count()) <= 2) throw new DomainError("Necesitas al menos dos estados.");
    await d.jobStatuses.delete(id);
  });
}

export async function saveTemplate(input: Omit<JobTemplate, "id" | "createdAt" | "updatedAt"> & { id?: string }) {
  if (!input.name.trim()) throw new DomainError("La plantilla necesita un nombre.");
  const now = nowISO();
  if (input.id) {
    await db().jobTemplates.update(input.id, { ...input, updatedAt: now });
    return input.id;
  }
  const id = uid();
  await db().jobTemplates.add({ ...input, id, createdAt: now, updatedAt: now });
  return id;
}

export async function deleteTemplate(id: string) {
  await db().jobTemplates.delete(id);
}
