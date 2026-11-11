import { addDays, diffDays, timeToMinutes, type DateStr, type TimeStr } from "@/lib/dates";
import type { Minor } from "@/lib/money";
import { occurrencesBetween } from "@/lib/recurrence";
import type { CalendarEvent, Client, Obligation, PlannedIncome, Task, Transaction } from "@/db/types";
import { obligationOccurrences, plannedIncomeOccurrences } from "./finance";
import type { JobView } from "./clients";

export type AgendaKind = "event" | "task" | "delivery" | "obligation" | "income" | "collection";

export interface AgendaItem {
  key: string;
  kind: AgendaKind;
  date: DateStr;
  time?: TimeStr | null;
  endTime?: TimeStr | null;
  durationMin?: number | null;
  title: string;
  subtitle?: string;
  /** Category or semantic colour token. */
  color: string;
  done?: boolean;
  overdue?: boolean;
  /** A future instance of a recurring task that has not been created yet. */
  projected?: boolean;
  amount?: Minor;
  ref: { type: "event" | "task" | "job" | "obligation" | "plannedIncome"; id: string; date?: DateStr };
}

export interface AgendaInput {
  from: DateStr;
  to: DateStr;
  today: DateStr;
  events: CalendarEvent[];
  tasks: Task[];
  jobViews: JobView[];
  obligations: Obligation[];
  plannedIncomes: PlannedIncome[];
  transactions: Transaction[];
  clients: Client[];
}

export const EVENT_COLORS: Record<CalendarEvent["category"], string> = {
  personal: "iris",
  trabajo: "sky",
  clientes: "violet",
  salud: "rose",
  familia: "amber",
  estudio: "teal",
  otro: "slate",
};

export const EVENT_CATEGORY_LABEL: Record<CalendarEvent["category"], string> = {
  personal: "Personal",
  trabajo: "Trabajo",
  clientes: "Clientes",
  salud: "Salud",
  familia: "Familia",
  estudio: "Estudio",
  otro: "Otro",
};

export function eventDuration(e: Pick<CalendarEvent, "startTime" | "endTime" | "allDay">): number {
  if (e.allDay || !e.startTime) return 0;
  if (!e.endTime) return 60;
  return Math.max(0, timeToMinutes(e.endTime) - timeToMinutes(e.startTime));
}

export function buildAgenda(input: AgendaInput): AgendaItem[] {
  const { from, to, today } = input;
  const clientName = new Map(input.clients.map((c) => [c.id, c.name]));
  const items: AgendaItem[] = [];

  for (const e of input.events) {
    for (const d of occurrencesBetween(e.date, e.recurrence, from, to)) {
      if (e.exceptions?.includes(d)) continue;
      items.push({
        key: `event:${e.id}:${d}`,
        kind: "event",
        date: d,
        time: e.allDay ? null : e.startTime,
        endTime: e.allDay ? null : e.endTime,
        durationMin: eventDuration(e),
        title: e.title,
        subtitle: [e.location, e.clientId ? clientName.get(e.clientId) : null].filter(Boolean).join(" · ") || undefined,
        color: EVENT_COLORS[e.category] ?? "iris",
        ref: { type: "event", id: e.id, date: d },
      });
    }
  }

  for (const t of input.tasks) {
    if (!t.date) continue;
    if (t.date >= from && t.date <= to) {
      items.push({
        key: `task:${t.id}`,
        kind: "task",
        date: t.date,
        time: t.time ?? null,
        durationMin: t.durationMin ?? null,
        title: t.title,
        subtitle: t.clientId ? clientName.get(t.clientId) : undefined,
        color: t.priority === 3 ? "rose" : "slate",
        done: t.status === "done",
        overdue: t.status === "todo" && t.date < today,
        ref: { type: "task", id: t.id },
      });
    }
    // Project future instances of a pending recurring task without creating them.
    if (t.recurrence && t.status === "todo") {
      for (const d of occurrencesBetween(t.seriesStart ?? t.date, t.recurrence, addDays(t.date, 1), to)) {
        if (d < from) continue;
        items.push({
          key: `task:${t.id}:${d}`,
          kind: "task",
          date: d,
          time: t.time ?? null,
          durationMin: t.durationMin ?? null,
          title: t.title,
          color: "slate",
          projected: true,
          ref: { type: "task", id: t.id, date: d },
        });
      }
    }
  }

  for (const v of input.jobViews) {
    if (v.job.archived) continue;
    if (v.isOpen && v.job.dueDate && v.job.dueDate >= from && v.job.dueDate <= to) {
      items.push({
        key: `delivery:${v.job.id}`,
        kind: "delivery",
        date: v.job.dueDate,
        title: `Entrega: ${v.job.title}`,
        subtitle: v.client?.name,
        color: "violet",
        overdue: v.job.dueDate < today,
        ref: { type: "job", id: v.job.id },
      });
    }
    if (v.finance.balance > 0 && v.job.paymentDueDate && v.job.paymentDueDate >= from && v.job.paymentDueDate <= to) {
      items.push({
        key: `collection:${v.job.id}`,
        kind: "collection",
        date: v.job.paymentDueDate,
        title: `Cobrar: ${v.job.title}`,
        subtitle: v.client?.name,
        color: "emerald",
        amount: v.finance.balance,
        overdue: v.job.paymentDueDate < today,
        ref: { type: "job", id: v.job.id },
      });
    }
  }

  for (const o of obligationOccurrences(input.obligations, input.transactions, from, to, today)) {
    if (o.status === "settled") continue;
    items.push({
      key: `obligation:${o.key}`,
      kind: "obligation",
      date: o.dueDate,
      title: `Pagar: ${o.source.name}`,
      color: "amber",
      amount: o.remaining > 0 ? o.remaining : o.amount,
      done: o.remaining === 0,
      overdue: o.status === "overdue",
      ref: { type: "obligation", id: o.source.id, date: o.dueDate },
    });
  }

  for (const p of plannedIncomeOccurrences(input.plannedIncomes, input.transactions, from, to, today)) {
    if (p.status === "settled") continue;
    items.push({
      key: `income:${p.key}`,
      kind: "income",
      date: p.dueDate,
      title: `Ingreso: ${p.source.name}`,
      subtitle: p.source.confirmed ? "Confirmado" : "Por confirmar",
      color: "emerald",
      amount: p.remaining > 0 ? p.remaining : p.amount,
      done: p.remaining === 0,
      ref: { type: "plannedIncome", id: p.source.id, date: p.dueDate },
    });
  }

  return items.sort(compareAgenda);
}

export function compareAgenda(a: AgendaItem, b: AgendaItem) {
  if (a.date !== b.date) return a.date.localeCompare(b.date);
  const at = a.time ? timeToMinutes(a.time) : -1;
  const bt = b.time ? timeToMinutes(b.time) : -1;
  if (at !== bt) return at - bt;
  const order: AgendaKind[] = ["delivery", "obligation", "collection", "income", "event", "task"];
  return order.indexOf(a.kind) - order.indexOf(b.kind) || a.title.localeCompare(b.title);
}

export function occupiedMinutes(items: AgendaItem[]): number {
  let total = 0;
  for (const i of items) {
    if (i.done) continue;
    if (i.kind === "event" || i.kind === "task") total += i.durationMin ?? 0;
  }
  return total;
}

export function daysUntil(today: DateStr, date: DateStr) {
  return diffDays(today, date);
}
