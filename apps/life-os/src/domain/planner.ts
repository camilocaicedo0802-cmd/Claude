/**
 * Day planner rules (pure). Times are minutes from 00:00 of the planned day.
 * Auto-planning is deliberately simple and explainable: rank tasks, then place each one
 * in the first free gap that fits, preferring the high-energy window for high priority.
 */
import type { CalendarEvent, PlannerSettings, Task } from "@/db/types";
import { minutesToTime, timeToMinutes, type DateStr } from "@/lib/dates";
import { occurrencesBetween } from "@/lib/recurrence";
import { eventDuration } from "./agenda";

export interface Interval {
  start: number;
  end: number;
}

export interface PlanItem extends Interval {
  key: string;
  kind: "task" | "event" | "block";
  title: string;
  /** Task id or event id. */
  id: string;
  color: string;
  done?: boolean;
  recurring?: boolean;
  priority?: number;
}

export function mergeIntervals(list: Interval[]): Interval[] {
  const sorted = list.filter((i) => i.end > i.start).sort((a, b) => a.start - b.start);
  const out: Interval[] = [];
  for (const i of sorted) {
    const last = out[out.length - 1];
    if (last && i.start <= last.end) last.end = Math.max(last.end, i.end);
    else out.push({ ...i });
  }
  return out;
}

/** Gaps of at least `minLen` minutes inside [from, to] not covered by `busy`. */
export function freeSlots(busy: Interval[], from: number, to: number, minLen = 10): Interval[] {
  const out: Interval[] = [];
  let cursor = from;
  for (const b of mergeIntervals(busy)) {
    if (b.end <= cursor) continue;
    if (b.start >= to) break;
    if (b.start - cursor >= minLen) out.push({ start: cursor, end: Math.min(b.start, to) });
    cursor = Math.max(cursor, b.end);
  }
  if (to - cursor >= minLen) out.push({ start: cursor, end: to });
  return out.filter((s) => s.end - s.start >= minLen);
}

export function taskMinutes(task: Pick<Task, "durationMin">, settings: Pick<PlannerSettings, "defaultTaskMin">): number {
  return Math.max(5, task.durationMin ?? settings.defaultTaskMin);
}

export const EVENT_CATEGORY_COLOR: Record<CalendarEvent["category"], string> = {
  personal: "iris",
  trabajo: "sky",
  clientes: "violet",
  salud: "rose",
  familia: "amber",
  estudio: "teal",
  otro: "slate",
};

/** Everything already placed on the day: timed tasks, events and time blocks. */
export function dayItems(date: DateStr, tasks: Task[], events: CalendarEvent[], settings: Pick<PlannerSettings, "defaultTaskMin">, categoryColor: (key?: string | null) => string): PlanItem[] {
  const items: PlanItem[] = [];
  for (const t of tasks) {
    if (t.date !== date || !t.time) continue;
    const start = timeToMinutes(t.time);
    items.push({
      key: `task:${t.id}`,
      kind: "task",
      id: t.id,
      title: t.title,
      start,
      end: start + taskMinutes(t, settings),
      color: categoryColor(t.area),
      done: t.status === "done",
      priority: t.priority,
    });
  }
  for (const e of events) {
    if (e.allDay || !e.startTime) continue;
    if (!occurrencesBetween(e.date, e.recurrence, date, date).length || e.exceptions?.includes(date)) continue;
    const start = timeToMinutes(e.startTime);
    items.push({
      key: `event:${e.id}`,
      kind: e.kind === "block" ? "block" : "event",
      id: e.id,
      title: e.title,
      start,
      end: start + Math.max(15, eventDuration(e)),
      color: EVENT_CATEGORY_COLOR[e.category] ?? "slate",
      recurring: !!e.recurrence,
    });
  }
  return items.sort((a, b) => a.start - b.start || a.end - b.end);
}

/** Tasks waiting for a time on `date`: due that day or overdue (when planning today), not done, no time. */
export function planCandidates(tasks: Task[], date: DateStr, today: DateStr): Task[] {
  return tasks.filter((t) => t.status === "todo" && !t.time && !!t.date && (t.date === date || (date === today && t.date < today)));
}

/** Higher score = plan first: priority, then overdue, then due date, then effort points. */
export function rankTasks(tasks: Task[], date: DateStr): Task[] {
  const score = (t: Task) => t.priority * 1000 + (t.date && t.date < date ? 300 : 0) + (t.inProgress ? 150 : 0) + (t.points ?? 0);
  return [...tasks].sort((a, b) => score(b) - score(a) || (a.date ?? "").localeCompare(b.date ?? "") || a.createdAt.localeCompare(b.createdAt));
}

export interface PlanProposal {
  taskId: string;
  title: string;
  start: number;
  end: number;
  inFocusWindow: boolean;
}

export interface AutoPlanResult {
  placed: PlanProposal[];
  unplaced: Array<{ taskId: string; title: string; minutes: number }>;
  freeAfter: number;
}

export function autoPlan(input: {
  date: DateStr;
  candidates: Task[];
  busy: Interval[];
  settings: PlannerSettings;
  /** Current minute when planning today, so nothing lands in the past. */
  nowMin: number | null;
}): AutoPlanResult {
  const { settings } = input;
  const dayStart = timeToMinutes(settings.dayStart);
  const dayEnd = timeToMinutes(settings.dayEnd);
  const from = input.nowMin === null ? dayStart : Math.max(dayStart, Math.ceil((input.nowMin + 5) / 5) * 5);
  const focus = { start: timeToMinutes(settings.focusStart), end: timeToMinutes(settings.focusEnd) };
  const buffer = Math.max(0, settings.bufferMin);
  // Busy time keeps a breathing gap on both sides.
  const occupied: Interval[] = input.busy.map((b) => ({ start: b.start - buffer, end: b.end + buffer }));
  const placed: PlanProposal[] = [];
  const unplaced: AutoPlanResult["unplaced"] = [];

  for (const task of rankTasks(input.candidates, input.date)) {
    const minutes = taskMinutes(task, settings);
    const slots = freeSlots(occupied, from, dayEnd, 5);
    const fits = (s: Interval) => s.end - s.start >= minutes;
    let start: number | null = null;
    let inFocusWindow = false;
    if (task.priority >= 3) {
      for (const s of slots) {
        const a = Math.max(s.start, focus.start);
        const b = Math.min(s.end, focus.end);
        if (b - a >= minutes) {
          start = a;
          inFocusWindow = true;
          break;
        }
      }
    }
    if (start === null) {
      const slot = slots.find(fits);
      if (slot) {
        start = slot.start;
        inFocusWindow = start >= focus.start && start + minutes <= focus.end;
      }
    }
    if (start === null) {
      unplaced.push({ taskId: task.id, title: task.title, minutes });
      continue;
    }
    placed.push({ taskId: task.id, title: task.title, start, end: start + minutes, inFocusWindow });
    occupied.push({ start: start - buffer, end: start + minutes + buffer });
  }

  const freeAfter = freeSlots(occupied, from, dayEnd, 5).reduce((s, x) => s + (x.end - x.start), 0);
  return { placed: placed.sort((a, b) => a.start - b.start), unplaced, freeAfter };
}

export function nowAndNext(items: PlanItem[], nowMin: number) {
  const active = items.filter((i) => !i.done);
  const now = active.find((i) => i.start <= nowMin && nowMin < i.end) ?? null;
  const next = active.filter((i) => i.start > nowMin).sort((a, b) => a.start - b.start)[0] ?? null;
  return { now, next };
}

/** Planned minutes inside the day window, and what is still free. */
export function dayCapacity(items: PlanItem[], settings: Pick<PlannerSettings, "dayStart" | "dayEnd">) {
  const start = timeToMinutes(settings.dayStart);
  const end = timeToMinutes(settings.dayEnd);
  const window = Math.max(0, end - start);
  const planned = mergeIntervals(items.filter((i) => !i.done).map((i) => ({ start: Math.max(start, i.start), end: Math.min(end, i.end) }))).reduce((s, i) => s + Math.max(0, i.end - i.start), 0);
  return { window, planned, free: Math.max(0, window - planned), overbooked: planned > window };
}

export function snap(minutes: number, step = 15): number {
  return Math.round(minutes / step) * step;
}

export function clampToDay(minutes: number): number {
  return Math.max(0, Math.min(24 * 60 - 15, minutes));
}

export function toTime(minutes: number): string {
  return minutesToTime(clampToDay(minutes));
}
