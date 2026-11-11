import { addDays, diffDays, startOfWeek, weekday, type DateStr } from "@/lib/dates";
import type { Habit, HabitLog } from "@/db/types";

export function isScheduled(habit: Habit, date: DateStr): boolean {
  if (date < habit.startDate) return false;
  if (habit.schedule.type === "daily") return true;
  return habit.schedule.days.includes(weekday(date));
}

export function logKey(habitId: string, date: DateStr) {
  return `${habitId}:${date}`;
}

export function logsIndex(logs: HabitLog[]): Map<string, HabitLog> {
  return new Map(logs.map((l) => [l.id, l]));
}

export function isDone(habit: Habit, index: Map<string, HabitLog>, date: DateStr): boolean {
  const log = index.get(logKey(habit.id, date));
  return !!log && log.count >= Math.max(1, habit.target);
}

/**
 * Current streak counted on scheduled days only. Days the habit is not scheduled neither
 * extend nor break the streak. Today counts if already done; if it is still pending, the
 * streak is not broken yet (the day is not over).
 */
export function currentStreak(habit: Habit, index: Map<string, HabitLog>, today: DateStr): number {
  let streak = 0;
  let d = today;
  if (isScheduled(habit, today)) {
    if (isDone(habit, index, today)) streak++;
  }
  d = addDays(today, -1);
  let guard = 0;
  while (d >= habit.startDate && guard < 3660) {
    guard++;
    if (isScheduled(habit, d)) {
      if (isDone(habit, index, d)) streak++;
      else break;
    }
    d = addDays(d, -1);
  }
  return streak;
}

export function bestStreak(habit: Habit, index: Map<string, HabitLog>, today: DateStr): number {
  let best = 0;
  let run = 0;
  let d = habit.startDate;
  let guard = 0;
  while (d <= today && guard < 3660) {
    guard++;
    if (isScheduled(habit, d)) {
      if (isDone(habit, index, d)) {
        run++;
        if (run > best) best = run;
      } else if (d !== today) {
        run = 0;
      }
    }
    d = addDays(d, 1);
  }
  return best;
}

/** Completion rate over scheduled days in [from, today]; today only counts once done. */
export function completionRate(habit: Habit, index: Map<string, HabitLog>, from: DateStr, today: DateStr) {
  let scheduled = 0;
  let done = 0;
  let d = from < habit.startDate ? habit.startDate : from;
  let guard = 0;
  while (d <= today && guard < 3660) {
    guard++;
    if (isScheduled(habit, d)) {
      const ok = isDone(habit, index, d);
      if (d !== today || ok) {
        scheduled++;
        if (ok) done++;
      }
    }
    d = addDays(d, 1);
  }
  return { scheduled, done, rate: scheduled > 0 ? (done / scheduled) * 100 : null };
}

/** Weekly completion percentages for the last `weeks` weeks (oldest first). */
export function weeklyTrend(habits: Habit[], index: Map<string, HabitLog>, today: DateStr, weekStartsOn: number, weeks = 8) {
  const thisWeek = startOfWeek(today, weekStartsOn);
  const out: Array<{ weekStart: DateStr; rate: number | null; done: number; scheduled: number }> = [];
  for (let i = weeks - 1; i >= 0; i--) {
    const ws = addDays(thisWeek, -7 * i);
    const we = addDays(ws, 6);
    let scheduled = 0;
    let done = 0;
    for (const h of habits) {
      const r = completionRate(h, index, ws, we < today ? we : today);
      scheduled += r.scheduled;
      done += r.done;
    }
    out.push({ weekStart: ws, rate: scheduled > 0 ? (done / scheduled) * 100 : null, done, scheduled });
  }
  return out;
}

export function scheduleLabel(habit: Habit): string {
  if (habit.schedule.type === "daily") return "Todos los días";
  const days = [...habit.schedule.days].sort();
  if (days.length === 5 && [1, 2, 3, 4, 5].every((d) => days.includes(d))) return "Lunes a viernes";
  if (days.length === 2 && days.includes(0) && days.includes(6)) return "Fines de semana";
  const names = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];
  const ordered = [1, 2, 3, 4, 5, 6, 0].filter((d) => days.includes(d));
  return ordered.map((d) => names[d]).join(", ");
}

export function daysSince(a: DateStr, b: DateStr) {
  return diffDays(a, b);
}
