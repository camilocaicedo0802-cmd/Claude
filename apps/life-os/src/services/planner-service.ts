import { db } from "@/db/db";
import type { DayTemplate, DayTemplateBlock, EventCategory, FocusSession, Task } from "@/db/types";
import { addDays, minutesToTime, nowISO, timeToMinutes, type DateStr, type TimeStr } from "@/lib/dates";
import { uid } from "@/lib/utils";
import type { PlanProposal } from "@/domain/planner";
import { DomainError } from "./common";

/** Puts a task on the timeline (or moves it): date + start time + duration. */
export async function scheduleTask(taskId: string, date: DateStr, start: TimeStr, durationMin?: number) {
  const patch: Partial<Task> = { date, time: start, updatedAt: nowISO() };
  if (durationMin !== undefined) patch.durationMin = Math.max(5, Math.round(durationMin));
  await db().tasks.update(taskId, patch);
}

/** Takes a task off the timeline; it stays on its date without a time. */
export async function unscheduleTask(taskId: string) {
  await db().tasks.update(taskId, { time: null, updatedAt: nowISO() });
}

/** Applies an auto-plan. Returns the previous values so the change can be undone. */
export async function applyPlan(date: DateStr, proposals: PlanProposal[]) {
  const d = db();
  return d.transaction("rw", d.tasks, async () => {
    const previous: Array<Pick<Task, "id" | "date" | "time" | "durationMin">> = [];
    for (const p of proposals) {
      const t = await d.tasks.get(p.taskId);
      if (!t) continue;
      previous.push({ id: t.id, date: t.date ?? null, time: t.time ?? null, durationMin: t.durationMin ?? null });
      await d.tasks.update(t.id, { date, time: minutesToTime(p.start), durationMin: p.end - p.start, updatedAt: nowISO() });
    }
    return previous;
  });
}

export async function restoreTasks(previous: Array<Pick<Task, "id" | "date" | "time" | "durationMin">>) {
  const d = db();
  await d.transaction("rw", d.tasks, async () => {
    for (const p of previous) await d.tasks.update(p.id, { date: p.date, time: p.time, durationMin: p.durationMin, updatedAt: nowISO() });
  });
}

/** Moves unfinished tasks of a day to another date, keeping their order but clearing the time. */
export async function moveTasksTo(taskIds: string[], date: DateStr) {
  const d = db();
  await d.transaction("rw", d.tasks, async () => {
    for (const id of taskIds) {
      const t = await d.tasks.get(id);
      if (!t || t.status === "done") continue;
      await d.tasks.update(id, { date, time: null, postponed: (t.postponed ?? 0) + 1, updatedAt: nowISO() });
    }
  });
}

// ── Time blocks and templates ────────────────────────────────────────────────

export async function createBlock(input: { date: DateStr; title: string; start: TimeStr; end: TimeStr; category: EventCategory }) {
  if (!input.title.trim()) throw new DomainError("Ponle un nombre al bloque.");
  if (timeToMinutes(input.end) <= timeToMinutes(input.start)) throw new DomainError("El bloque debe terminar después de empezar.");
  const now = nowISO();
  const id = uid();
  await db().events.add({
    id,
    title: input.title.trim(),
    date: input.date,
    startTime: input.start,
    endTime: input.end,
    allDay: false,
    recurrence: null,
    category: input.category,
    exceptions: [],
    kind: "block",
    createdAt: now,
    updatedAt: now,
  });
  return id;
}

/** Moves an event or block to a new start time, keeping its length. */
export async function moveEventTime(id: string, start: TimeStr) {
  const e = await db().events.get(id);
  if (!e || !e.startTime) return;
  if (e.recurrence) throw new DomainError("Es un evento que se repite: cámbialo desde su formulario.");
  const length = (e.endTime ? timeToMinutes(e.endTime) : timeToMinutes(e.startTime) + 60) - timeToMinutes(e.startTime);
  await db().events.update(id, { startTime: start, endTime: minutesToTime(timeToMinutes(start) + length), updatedAt: nowISO() });
}

export async function resizeEvent(id: string, minutes: number) {
  const e = await db().events.get(id);
  if (!e || !e.startTime) return;
  await db().events.update(id, { endTime: minutesToTime(timeToMinutes(e.startTime) + Math.max(15, minutes)), updatedAt: nowISO() });
}

export async function saveDayTemplate(name: string, blocks: DayTemplateBlock[], replaceId?: string) {
  if (!name.trim()) throw new DomainError("Ponle un nombre a la plantilla.");
  if (blocks.length === 0) throw new DomainError("Este día no tiene bloques para guardar.");
  const d = db();
  await d.transaction("rw", d.settings, async () => {
    const s = await d.settings.get("app");
    const list = s?.dayTemplates ?? [];
    const template: DayTemplate = { id: replaceId ?? uid(), name: name.trim(), blocks: [...blocks].sort((a, b) => a.start.localeCompare(b.start)) };
    const next = replaceId ? list.map((t) => (t.id === replaceId ? template : t)) : [...list, template];
    await d.settings.update("app", { dayTemplates: next, updatedAt: nowISO() });
  });
}

export async function deleteDayTemplate(id: string) {
  const d = db();
  await d.transaction("rw", d.settings, async () => {
    const s = await d.settings.get("app");
    await d.settings.update("app", { dayTemplates: (s?.dayTemplates ?? []).filter((t) => t.id !== id), updatedAt: nowISO() });
  });
}

/** Creates the template's blocks on a date. Blocks that would duplicate one already there are skipped. */
export async function applyDayTemplate(template: DayTemplate, date: DateStr): Promise<number> {
  const d = db();
  return d.transaction("rw", d.events, async () => {
    const existing = (await d.events.where("date").equals(date).toArray()).filter((e) => e.kind === "block");
    let created = 0;
    for (const b of template.blocks) {
      if (existing.some((e) => e.title === b.title && e.startTime === b.start)) continue;
      const now = nowISO();
      await d.events.add({ id: uid(), title: b.title, date, startTime: b.start, endTime: b.end, allDay: false, recurrence: null, category: b.category, exceptions: [], kind: "block", createdAt: now, updatedAt: now });
      created++;
    }
    return created;
  });
}

export async function clearDayBlocks(date: DateStr) {
  const d = db();
  await d.transaction("rw", d.events, async () => {
    const blocks = (await d.events.where("date").equals(date).toArray()).filter((e) => e.kind === "block" && !e.recurrence);
    await d.events.bulkDelete(blocks.map((b) => b.id));
  });
}

// ── Focus sessions ───────────────────────────────────────────────────────────

/** Records a focus session and adds the minutes to the task it was for. */
export async function recordFocusSession(input: Omit<FocusSession, "id">) {
  if (input.minutes < 1) return null;
  const d = db();
  return d.transaction("rw", [d.focusSessions, d.tasks], async () => {
    const id = uid();
    await d.focusSessions.add({ ...input, id, minutes: Math.round(input.minutes) });
    if (input.taskId) {
      const t = await d.tasks.get(input.taskId);
      if (t) await d.tasks.update(t.id, { actualMin: (t.actualMin ?? 0) + Math.round(input.minutes), updatedAt: nowISO() });
    }
    return id;
  });
}

export function tomorrowOf(date: DateStr) {
  return addDays(date, 1);
}
