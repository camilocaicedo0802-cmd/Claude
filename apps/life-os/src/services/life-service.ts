import { db } from "@/db/db";
import type { CalendarEvent, Habit, Task, WeekPlan } from "@/db/types";
import { addDays, nowISO, type DateStr } from "@/lib/dates";
import { occurrenceAfter } from "@/lib/recurrence";
import { uid } from "@/lib/utils";
import { logKey } from "@/domain/habits";
import type { ImportRow, TaskStage } from "@/domain/tasks";
import type { TaskCategory } from "@/db/types";
import { normalize } from "@/lib/utils";
import { DomainError, logActivity } from "./common";

// ── Tasks ────────────────────────────────────────────────────────────────────

export type TaskInput = Partial<Omit<Task, "id" | "createdAt" | "updatedAt">> & { title: string };

export async function createTask(input: TaskInput): Promise<string> {
  const title = input.title.trim();
  if (!title) throw new DomainError("Escribe qué tienes que hacer.");
  const now = nowISO();
  const id = uid();
  const task: Task = {
    description: undefined,
    date: null,
    time: null,
    durationMin: null,
    priority: 0,
    status: "todo",
    completedAt: null,
    area: null,
    recurrence: null,
    clientId: null,
    jobId: null,
    followUp: null,
    notes: undefined,
    postponed: 0,
    order: Date.now(),
    ...input,
    seriesId: input.recurrence ? input.seriesId ?? id : null,
    seriesStart: input.recurrence ? input.seriesStart ?? input.date ?? null : null,
    subtasks: input.subtasks ?? [],
    title,
    id,
    createdAt: now,
    updatedAt: now,
  };
  if (task.recurrence && !task.date) throw new DomainError("Una tarea recurrente necesita una fecha de inicio.");
  const d = db();
  await d.transaction("rw", [d.tasks, d.activities], async () => {
    await d.tasks.add(task);
    if (task.clientId) await logActivity({ clientId: task.clientId, jobId: task.jobId, type: "task", message: `Tarea: ${task.title}` });
  });
  return id;
}

export async function updateTask(id: string, patch: Partial<Omit<Task, "id" | "createdAt">>) {
  const d = db();
  await d.transaction("rw", d.tasks, async () => {
    const task = await d.tasks.get(id);
    if (!task) return;
    const next = { ...task, ...patch };
    if (next.recurrence && !next.date) throw new DomainError("Una tarea recurrente necesita una fecha.");
    if (next.recurrence && !next.seriesId) next.seriesId = id;
    if (next.recurrence && (!next.seriesStart || (patch.recurrence && !task.recurrence))) next.seriesStart = next.date;
    if (!next.recurrence) next.seriesStart = null;
    await d.tasks.put({ ...next, updatedAt: nowISO() });
  });
}

/**
 * Completes or reopens a task. Completing an instance of a recurring task creates the next
 * instance once: if that date already has an instance of the series, nothing is duplicated.
 */
export async function setTaskDone(id: string, done: boolean): Promise<string | null> {
  const d = db();
  return d.transaction("rw", d.tasks, async () => {
    const task = await d.tasks.get(id);
    if (!task) return null;
    const now = nowISO();
    await d.tasks.update(id, { status: done ? "done" : "todo", completedAt: done ? now : null, inProgress: done ? false : task.inProgress ?? false, updatedAt: now });
    if (!done || !task.recurrence || !task.date) return null;
    // The next date is computed from the series anchor, so monthly rules on the 31st do not drift.
    const anchor = task.seriesStart ?? task.date;
    const next = occurrenceAfter(anchor, task.recurrence, task.date);
    if (!next) return null;
    const seriesId = task.seriesId ?? task.id;
    const siblings = await d.tasks.where("seriesId").equals(seriesId).toArray();
    if (siblings.some((t) => t.date === next)) return null;
    const nextId = uid();
    await d.tasks.add({
      ...task,
      id: nextId,
      seriesId,
      seriesStart: anchor,
      date: next,
      status: "todo",
      completedAt: null,
      inProgress: false,
      postponed: 0,
      subtasks: task.subtasks.map((s) => ({ ...s, id: uid(), done: false })),
      createdAt: now,
      updatedAt: now,
    });
    return nextId;
  });
}

/** Moves a task between "Sin empezar", "En curso" and "Completada". */
export async function setTaskStage(id: string, stage: TaskStage): Promise<string | null> {
  const task = await db().tasks.get(id);
  if (!task) return null;
  if (stage === "done") return task.status === "done" ? null : setTaskDone(id, true);
  if (task.status === "done") await setTaskDone(id, false);
  await db().tasks.update(id, { inProgress: stage === "in_progress", updatedAt: nowISO() });
  return null;
}

/**
 * Creates tasks from imported rows in one transaction. Rows whose title and date already
 * exist are skipped, so pasting the same list twice never duplicates tasks.
 */
export async function importTasks(rows: ImportRow[], newCategories: TaskCategory[] = []): Promise<{ created: number; skipped: number }> {
  const d = db();
  return d.transaction("rw", [d.tasks, d.settings], async () => {
    if (newCategories.length) {
      const settings = await d.settings.get("app");
      const current = settings?.taskCategories ?? [];
      const merged = [...current, ...newCategories.filter((c) => !current.some((x) => x.key === c.key))];
      await d.settings.update("app", { taskCategories: merged, updatedAt: nowISO() });
    }
    const existing = await d.tasks.toArray();
    const seen = new Set(existing.map((t) => `${normalize(t.title)}|${t.date ?? ""}`));
    const now = nowISO();
    let created = 0;
    let skipped = 0;
    for (const [i, r] of rows.entries()) {
      const key = `${normalize(r.title)}|${r.date ?? ""}`;
      if (seen.has(key)) {
        skipped++;
        continue;
      }
      seen.add(key);
      const done = r.stage === "done";
      await d.tasks.add({
        id: uid(),
        title: r.title.trim(),
        date: r.date,
        time: null,
        durationMin: null,
        priority: r.priority,
        status: done ? "done" : "todo",
        completedAt: done ? now : null,
        inProgress: r.stage === "in_progress",
        points: r.points,
        icon: r.icon,
        area: r.category,
        recurrence: null,
        seriesId: null,
        clientId: null,
        jobId: null,
        followUp: null,
        subtasks: [],
        postponed: 0,
        order: Date.now() + i,
        createdAt: now,
        updatedAt: now,
      });
      created++;
    }
    return { created, skipped };
  });
}

export async function rescheduleTask(id: string, date: DateStr | null, time?: string | null) {
  const patch: Partial<Task> = { date, updatedAt: nowISO() };
  if (time !== undefined) patch.time = time;
  await db().tasks.update(id, patch);
}

export async function postponeTask(id: string, days = 1, today?: DateStr) {
  const d = db();
  await d.transaction("rw", d.tasks, async () => {
    const task = await d.tasks.get(id);
    if (!task) return;
    const base = task.date && today && task.date < today ? today : task.date ?? today;
    if (!base) return;
    await d.tasks.update(id, { date: addDays(base, days), postponed: (task.postponed ?? 0) + 1, updatedAt: nowISO() });
  });
}

export async function duplicateTask(id: string): Promise<string | null> {
  const task = await db().tasks.get(id);
  if (!task) return null;
  const { id: _old, createdAt: _c, updatedAt: _u, seriesId: _s, ...rest } = task;
  return createTask({
    ...rest,
    title: `${task.title} (copia)`,
    status: "todo",
    completedAt: null,
    postponed: 0,
    recurrence: null,
    subtasks: task.subtasks.map((s) => ({ ...s, id: uid(), done: false })),
  });
}

export async function deleteTask(id: string) {
  const d = db();
  await d.transaction("rw", [d.tasks, d.dayPlans], async () => {
    await d.tasks.delete(id);
    const plans = await d.dayPlans.toArray();
    for (const p of plans) {
      if (p.priorities.includes(id)) await d.dayPlans.put({ ...p, priorities: p.priorities.filter((x) => x !== id) });
    }
  });
}

export async function toggleSubtask(taskId: string, subtaskId: string) {
  const d = db();
  await d.transaction("rw", d.tasks, async () => {
    const task = await d.tasks.get(taskId);
    if (!task) return;
    await d.tasks.update(taskId, {
      subtasks: task.subtasks.map((s) => (s.id === subtaskId ? { ...s, done: !s.done } : s)),
      updatedAt: nowISO(),
    });
  });
}

export async function setDayPriorities(date: DateStr, priorities: string[]) {
  await db().dayPlans.put({ date, priorities: priorities.slice(0, 3) });
}

// ── Events ───────────────────────────────────────────────────────────────────

export type EventInput = Omit<CalendarEvent, "id" | "createdAt" | "updatedAt" | "exceptions"> & { exceptions?: string[] };

function validateEvent(e: EventInput) {
  if (!e.title.trim()) throw new DomainError("El evento necesita un título.");
  if (!e.allDay && e.startTime && e.endTime && e.endTime <= e.startTime) {
    throw new DomainError("La hora de fin debe ser posterior a la de inicio.");
  }
}

export async function createEvent(input: EventInput): Promise<string> {
  validateEvent(input);
  const now = nowISO();
  const id = uid();
  await db().events.add({ ...input, title: input.title.trim(), exceptions: input.exceptions ?? [], id, createdAt: now, updatedAt: now });
  return id;
}

export async function updateEvent(id: string, patch: Partial<EventInput>) {
  const current = await db().events.get(id);
  if (!current) throw new DomainError("El evento ya no existe.");
  const next = { ...current, ...patch };
  validateEvent(next);
  await db().events.put({ ...next, updatedAt: nowISO() });
}

/** Moves a single occurrence of a recurring event: the series skips that date and a one-off copy is created. */
export async function moveEventOccurrence(id: string, occurrence: DateStr, newDate: DateStr) {
  const d = db();
  await d.transaction("rw", d.events, async () => {
    const e = await d.events.get(id);
    if (!e) return;
    if (!e.recurrence) {
      await d.events.update(id, { date: newDate, updatedAt: nowISO() });
      return;
    }
    await d.events.update(id, { exceptions: [...new Set([...(e.exceptions ?? []), occurrence])], updatedAt: nowISO() });
    const now = nowISO();
    await d.events.add({ ...e, id: uid(), date: newDate, recurrence: null, exceptions: [], createdAt: now, updatedAt: now });
  });
}

export async function deleteEvent(id: string, occurrence?: DateStr) {
  const d = db();
  const e = await d.events.get(id);
  if (!e) return;
  if (occurrence && e.recurrence) {
    await d.events.update(id, { exceptions: [...new Set([...(e.exceptions ?? []), occurrence])], updatedAt: nowISO() });
    return;
  }
  await d.events.delete(id);
}

// ── Habits ───────────────────────────────────────────────────────────────────

export type HabitInput = Omit<Habit, "id" | "createdAt" | "updatedAt" | "archived" | "order">;

export async function createHabit(input: HabitInput): Promise<string> {
  if (!input.name.trim()) throw new DomainError("El hábito necesita un nombre.");
  if (input.schedule.type === "days" && input.schedule.days.length === 0) throw new DomainError("Elige al menos un día.");
  const now = nowISO();
  const id = uid();
  const order = await db().habits.count();
  await db().habits.add({ ...input, name: input.name.trim(), target: Math.max(1, input.target || 1), id, archived: false, order, createdAt: now, updatedAt: now });
  return id;
}

export async function updateHabit(id: string, patch: Partial<HabitInput & { archived: boolean; order: number }>) {
  if (patch.schedule?.type === "days" && patch.schedule.days.length === 0) throw new DomainError("Elige al menos un día.");
  await db().habits.update(id, { ...patch, updatedAt: nowISO() });
}

export async function deleteHabit(id: string) {
  const d = db();
  await d.transaction("rw", [d.habits, d.habitLogs], async () => {
    await d.habitLogs.where("habitId").equals(id).delete();
    await d.habits.delete(id);
  });
}

/** Sets the count for a habit on a date. One row per (habit, date): logs never duplicate. */
export async function setHabitCount(habitId: string, date: DateStr, count: number) {
  const id = logKey(habitId, date);
  if (count <= 0) {
    await db().habitLogs.delete(id);
    return;
  }
  await db().habitLogs.put({ id, habitId, date, count, updatedAt: nowISO() });
}

export async function toggleHabit(habit: Habit, date: DateStr) {
  const log = await db().habitLogs.get(logKey(habit.id, date));
  const target = Math.max(1, habit.target);
  if (target === 1) return setHabitCount(habit.id, date, log && log.count >= 1 ? 0 : 1);
  // Multi-count habits: each tap adds one; tapping when complete resets.
  const current = log?.count ?? 0;
  return setHabitCount(habit.id, date, current >= target ? 0 : current + 1);
}

// ── Week plans ───────────────────────────────────────────────────────────────

export async function saveWeekPlan(weekStart: DateStr, patch: Partial<Omit<WeekPlan, "weekStart">>) {
  const d = db();
  await d.transaction("rw", d.weekPlans, async () => {
    const current = (await d.weekPlans.get(weekStart)) ?? { weekStart, priorities: [], review: { completed: "", pending: "", next: "" } };
    await d.weekPlans.put({ ...current, ...patch, weekStart });
  });
}
