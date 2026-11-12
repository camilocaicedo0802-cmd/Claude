import { addDays, formatDuration, type DateStr } from "@/lib/dates";
import { countWords } from "@/lib/utils";
import type { Habit, HabitLog, Obligation, Task } from "@/db/types";
import type { AgendaItem } from "./agenda";
import { occupiedMinutes } from "./agenda";
import type { JobView } from "./clients";
import type { Occurrence } from "./finance";
import { isDone, isScheduled, logsIndex } from "./habits";

export interface Insight {
  key: string;
  tone: "neutral" | "warning" | "positive";
  text: string;
  href?: string;
}

export interface BriefInput {
  today: DateStr;
  tasks: Task[];
  jobViews: JobView[];
  obligations: Occurrence<Obligation>[];
}

/**
 * One sentence that summarises the most urgent items of the three areas (Flujo D).
 * Every number comes straight from stored records.
 */
export function dailyBrief({ today, tasks, jobViews, obligations }: BriefInput): string | null {
  const soon = addDays(today, 3);
  const deliveries = jobViews.filter((v) => v.isOpen && !v.job.archived && v.job.dueDate && v.job.dueDate <= soon).length;
  const payments = obligations.filter((o) => o.remaining > 0 && o.dueDate <= soon).length;
  const tasksToday = tasks.filter((t) => t.status === "todo" && t.date === today).length;
  const tasksLate = tasks.filter((t) => t.status === "todo" && t.date && t.date < today).length;
  const parts: string[] = [];
  if (deliveries) parts.push(`${countWords(deliveries, "trabajo", "trabajos")} por entregar`);
  if (payments) parts.push(`${countWords(payments, "pago próximo", "pagos próximos")}`);
  if (tasksToday) parts.push(`${countWords(tasksToday, "tarea pendiente", "tareas pendientes", true)} hoy`);
  if (tasksLate) parts.push(`${countWords(tasksLate, "tarea atrasada", "tareas atrasadas", true)}`);
  if (parts.length === 0) return null;
  const joined = parts.length > 1 ? `${parts.slice(0, -1).join(", ")} y ${parts[parts.length - 1]}` : parts[0];
  return `Tienes ${joined}.`;
}

export interface InsightInput {
  today: DateStr;
  tasks: Task[];
  todayAgenda: AgendaItem[];
  jobViews: JobView[];
  habits: Habit[];
  habitLogs: HabitLog[];
  availableHoursPerDay: number;
}

export function productivityInsights(input: InsightInput): Insight[] {
  const { today } = input;
  const out: Insight[] = [];
  const todays = input.tasks.filter((t) => t.status === "todo" && t.date === today);
  const high = todays.filter((t) => t.priority === 3).length;
  if (todays.length >= 3) {
    out.push({
      key: "tasks-today",
      tone: high >= 2 ? "warning" : "neutral",
      text:
        `Tienes ${countWords(todays.length, "tarea programada", "tareas programadas", true)} para hoy` +
        (high > 0 ? ` y ${high === 1 ? "una es" : `${countWords(high, "", "").trim()} son`} de prioridad alta.` : "."),
      href: "/vida/tareas/",
    });
  }

  const tomorrow = addDays(today, 1);
  for (const v of input.jobViews) {
    if (!v.isOpen || v.job.archived || !v.job.dueDate) continue;
    if (v.job.dueDate === tomorrow && (v.kind === "doing" || v.kind === "todo" || v.kind === "new")) {
      out.push({
        key: `job-tomorrow-${v.job.id}`,
        tone: "warning",
        text: `"${v.job.title}" vence mañana y todavía está ${v.kind === "doing" ? "en proceso" : "sin iniciar"}.`,
        href: `/clientes/trabajos/?trabajo=${v.job.id}`,
      });
    } else if (v.job.dueDate < today) {
      out.push({
        key: `job-late-${v.job.id}`,
        tone: "warning",
        text: `"${v.job.title}" debía entregarse y sigue abierto.`,
        href: `/clientes/trabajos/?trabajo=${v.job.id}`,
      });
    }
  }

  const minutes = occupiedMinutes(input.todayAgenda);
  const available = input.availableHoursPerDay * 60;
  if (minutes > available && available > 0) {
    out.push({
      key: "overbooked",
      tone: "warning",
      text: `Tienes ${formatDuration(minutes)} planificadas hoy y solo ${formatDuration(available)} disponibles. Reprograma algo para mañana.`,
      href: "/vida/semana/",
    });
  }

  const index = logsIndex(input.habitLogs);
  const scheduled = input.habits.filter((h) => !h.archived && isScheduled(h, today));
  if (scheduled.length > 0) {
    const done = scheduled.filter((h) => isDone(h, index, today)).length;
    if (done > 0) {
      out.push({
        key: "habits",
        tone: done === scheduled.length ? "positive" : "neutral",
        text:
          done === scheduled.length
            ? `Completaste todos tus hábitos de hoy (${done}).`
            : `Has completado ${done} de tus ${scheduled.length} hábitos programados hoy.`,
        href: "/vida/habitos/",
      });
    }
  }

  const postponed = input.tasks.filter((t) => t.status === "todo" && t.postponed >= 3);
  if (postponed.length > 0) {
    out.push({
      key: "postponed",
      tone: "neutral",
      text: `"${postponed[0].title}" lleva ${postponed[0].postponed} aplazamientos. ¿Divídela en pasos o decide si sigue siendo necesaria?`,
      href: "/vida/tareas/",
    });
  }
  return out.slice(0, 4);
}
