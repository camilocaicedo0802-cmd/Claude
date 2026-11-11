import { addDays, diffDays, formatRelativeDay, type DateStr } from "@/lib/dates";
import type { Minor } from "@/lib/money";
import type { NotificationPrefs, Obligation, Task } from "@/db/types";
import type { BudgetStatus, Occurrence, SpendCapacity } from "./finance";
import type { JobView } from "./clients";

export interface Alert {
  key: string;
  severity: "critical" | "warning" | "info";
  area: "finanzas" | "clientes" | "vida";
  title: string;
  description: string;
  href: string;
}

export interface AlertInput {
  today: DateStr;
  prefs: NotificationPrefs;
  obligations: Occurrence<Obligation>[];
  budgets: BudgetStatus[];
  jobViews: JobView[];
  tasks: Task[];
  capacity: SpendCapacity | null;
  format: (m: Minor) => string;
}

export function buildAlerts(input: AlertInput): Alert[] {
  const { today, prefs, format } = input;
  const out: Alert[] = [];

  if (prefs.obligations) {
    const limit = addDays(today, Math.max(0, prefs.obligationLeadDays));
    for (const o of input.obligations) {
      if (o.remaining <= 0 || o.dueDate > limit) continue;
      const overdue = o.dueDate < today;
      out.push({
        key: `obligation:${o.key}`,
        severity: overdue ? "critical" : "warning",
        area: "finanzas",
        title: overdue ? `${o.source.name} está vencida` : `${o.source.name} vence ${formatRelativeDay(o.dueDate, today).toLowerCase()}`,
        description: `Pendiente: ${format(o.remaining)}`,
        href: "/finanzas/obligaciones/",
      });
    }
  }

  if (prefs.budgets) {
    for (const b of input.budgets) {
      if (b.state === "ok" || !b.category) continue;
      out.push({
        key: `budget:${b.budget.id}:${today.slice(0, 7)}:${b.state}`,
        severity: b.state === "over" ? "critical" : "warning",
        area: "finanzas",
        title: b.state === "over" ? `Superaste el presupuesto de ${b.category.name}` : `${b.category.name} al ${Math.round(b.percent)} % del presupuesto`,
        description:
          b.state === "over"
            ? `Gastaste ${format(b.spent)} de ${format(b.budget.amount)}.`
            : `Te quedan ${format(b.remaining)} este mes.`,
        href: "/finanzas/presupuestos/",
      });
    }
  }

  if (input.capacity?.status === "negative") {
    out.push({
      key: `capacity:negative:${today}`,
      severity: "critical",
      area: "finanzas",
      title: "Tu proyección es negativa",
      description: input.capacity.warnings[0] ?? "Lo comprometido supera tu dinero disponible.",
      href: "/finanzas/",
    });
  }

  for (const v of input.jobViews) {
    if (v.job.archived) continue;
    if (prefs.jobs && v.isOpen && v.job.dueDate) {
      const d = diffDays(today, v.job.dueDate);
      if (d <= 2) {
        out.push({
          key: `job:${v.job.id}:${v.job.dueDate}`,
          severity: d < 0 ? "critical" : "warning",
          area: "clientes",
          title: d < 0 ? `Entrega atrasada: ${v.job.title}` : `Entrega ${formatRelativeDay(v.job.dueDate, today).toLowerCase()}: ${v.job.title}`,
          description: `${v.client?.name ?? "Cliente"} · ${v.status?.name ?? ""}`,
          href: `/clientes/trabajos/?trabajo=${v.job.id}`,
        });
      }
    }
    if (prefs.collections && v.finance.state === "overdue") {
      out.push({
        key: `collect:${v.job.id}:${v.job.paymentDueDate}`,
        severity: "warning",
        area: "clientes",
        title: `Cobro vencido: ${v.client?.name ?? v.job.title}`,
        description: `${v.job.title} · pendiente ${format(v.finance.balance)}`,
        href: `/clientes/cobros/`,
      });
    }
  }

  if (prefs.tasks) {
    const overdue = input.tasks.filter((t) => t.status === "todo" && t.date && t.date < today);
    if (overdue.length > 0) {
      out.push({
        key: `tasks:overdue:${today}:${overdue.length}`,
        severity: "info",
        area: "vida",
        title: overdue.length === 1 ? "Tienes una tarea atrasada" : `Tienes ${overdue.length} tareas atrasadas`,
        description: overdue
          .slice(0, 2)
          .map((t) => t.title)
          .join(" · "),
        href: "/vida/tareas/?vista=vencidas",
      });
    }
  }

  const rank = { critical: 0, warning: 1, info: 2 };
  return out.sort((a, b) => rank[a.severity] - rank[b.severity]);
}
