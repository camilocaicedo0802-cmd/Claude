import { addDays, addMonths, diffDays, startOfWeek, weekday, type DateStr } from "./dates";

/**
 * A recurrence rule anchored at a start date. Occurrences are always computed from the
 * anchor (start + k·interval) instead of chaining, so monthly rules anchored on the 31st
 * land on the last day of short months without drifting.
 */
export interface Recurrence {
  freq: "daily" | "weekly" | "monthly" | "yearly";
  interval: number;
  /** Weekly only: 0 = Sunday … 6 = Saturday. Empty/undefined = the start's weekday. */
  byWeekday?: number[];
  /**
   * Monthly only: fixed days of the month (e.g. [15, 30] for a quincena). A day past the end
   * of a short month falls on its last day (30 → 28 Feb). Empty/undefined = the start's day.
   */
  byMonthDay?: number[];
  /** Last date (inclusive) an occurrence may fall on. */
  until?: DateStr | null;
  /** Maximum number of occurrences (e.g. 12 cuotas). */
  count?: number | null;
}

export type RecurrencePreset =
  | "none"
  | "daily"
  | "weekdays"
  | "weekly"
  | "biweekly"
  | "semimonthly"
  | "monthly"
  | "quarterly"
  | "yearly"
  | "custom-days";

/** Default paydays of a quincena: the 15th and the 30th (last day in February). */
export const DEFAULT_SEMIMONTHLY_DAYS = [15, 30];

export const PRESET_LABELS: Record<RecurrencePreset, string> = {
  none: "No se repite",
  daily: "Cada día",
  weekdays: "Lunes a viernes",
  weekly: "Cada semana",
  biweekly: "Cada dos semanas",
  semimonthly: "Quincenal",
  monthly: "Cada mes",
  quarterly: "Cada tres meses",
  yearly: "Cada año",
  "custom-days": "Días específicos",
};

/**
 * `days` are weekdays for "custom-days" and days of the month for "semimonthly".
 */
export function presetToRecurrence(preset: RecurrencePreset, days?: number[]): Recurrence | null {
  switch (preset) {
    case "none":
      return null;
    case "daily":
      return { freq: "daily", interval: 1 };
    case "weekdays":
      return { freq: "weekly", interval: 1, byWeekday: [1, 2, 3, 4, 5] };
    case "weekly":
      return { freq: "weekly", interval: 1 };
    case "biweekly":
      return { freq: "weekly", interval: 2 };
    case "semimonthly":
      return { freq: "monthly", interval: 1, byMonthDay: normalizeMonthDays(days && days.length ? days : DEFAULT_SEMIMONTHLY_DAYS) };
    case "monthly":
      return { freq: "monthly", interval: 1 };
    case "quarterly":
      return { freq: "monthly", interval: 3 };
    case "yearly":
      return { freq: "yearly", interval: 1 };
    case "custom-days":
      return { freq: "weekly", interval: 1, byWeekday: days && days.length ? [...days].sort() : [1] };
  }
}

export function recurrenceToPreset(r: Recurrence | null | undefined): RecurrencePreset {
  if (!r) return "none";
  if (r.freq === "daily" && r.interval === 1) return "daily";
  if (r.freq === "weekly") {
    const days = r.byWeekday ?? [];
    if (r.interval === 1 && days.length === 5 && [1, 2, 3, 4, 5].every((d) => days.includes(d))) return "weekdays";
    if (days.length > 0) return "custom-days";
    return r.interval === 2 ? "biweekly" : "weekly";
  }
  if (r.freq === "monthly") {
    if (r.byMonthDay && r.byMonthDay.length > 1) return "semimonthly";
    return r.interval === 3 ? "quarterly" : "monthly";
  }
  if (r.freq === "yearly") return "yearly";
  return "custom-days";
}

export function describeRecurrence(r: Recurrence | null | undefined): string {
  const preset = recurrenceToPreset(r);
  if (preset === "custom-days" && r?.byWeekday) {
    const names = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];
    return r.byWeekday.map((d) => names[d]).join(", ");
  }
  let label = preset === "semimonthly" && r?.byMonthDay ? `Quincenal · días ${joinDays(r.byMonthDay)}` : PRESET_LABELS[preset];
  if (r?.count) label += ` · ${r.count} veces`;
  return label;
}

/** Sorted, unique days in 1–31. */
export function normalizeMonthDays(days: number[]): number[] {
  return [...new Set(days.map((d) => Math.min(31, Math.max(1, Math.round(d)))))].sort((a, b) => a - b);
}

function joinDays(days: number[]): string {
  const list = normalizeMonthDays(days).map(String);
  return list.length <= 1 ? list.join("") : `${list.slice(0, -1).join(", ")} y ${list[list.length - 1]}`;
}

/** Average number of occurrences per month (0 for a one-off). Used for monthly equivalents. */
export function occurrencesPerMonth(r: Recurrence | null | undefined): number {
  if (!r) return 0;
  const interval = Math.max(1, Math.floor(r.interval || 1));
  switch (r.freq) {
    case "daily":
      return 365.25 / 12 / interval;
    case "weekly":
      return ((r.byWeekday?.length || 1) * 52.1775) / 12 / interval;
    case "monthly":
      return (r.byMonthDay?.length || 1) / interval;
    case "yearly":
      return 1 / (12 * interval);
  }
}

/**
 * All occurrence dates of a series that fall in [from, to], in order.
 * `start` is the first occurrence (the anchor).
 */
export function occurrencesBetween(
  start: DateStr,
  rule: Recurrence | null | undefined,
  from: DateStr,
  to: DateStr,
  limit = 2000,
): DateStr[] {
  if (to < from) return [];
  if (!rule) return start >= from && start <= to ? [start] : [];
  const out: DateStr[] = [];
  const interval = Math.max(1, Math.floor(rule.interval || 1));
  const until = rule.until && rule.until < to ? rule.until : to;
  const maxCount = rule.count ?? Infinity;
  let index = 0; // occurrence index, for count limits

  const push = (d: DateStr) => {
    if (d >= from && d <= until) out.push(d);
  };

  if (rule.freq === "daily") {
    // Jump close to `from` without iterating every past day.
    let k = 0;
    if (from > start) k = Math.floor(diffDays(start, from) / interval);
    if (Number.isFinite(maxCount)) k = Math.min(k, maxCount);
    index = k;
    let d = addDays(start, k * interval);
    while (d <= until && index < maxCount && out.length < limit) {
      push(d);
      index++;
      d = addDays(start, index * interval);
    }
    return out;
  }

  if (rule.freq === "weekly") {
    const days = (rule.byWeekday && rule.byWeekday.length ? rule.byWeekday : [weekday(start)]).slice().sort((a, b) => a - b);
    const week0 = startOfWeek(start, 0); // Sunday-based week of the anchor
    let w = 0;
    if (from > start && !Number.isFinite(maxCount)) {
      w = Math.max(0, Math.floor(diffDays(week0, from) / 7 / interval) * interval - interval);
    }
    let guard = 0;
    while (out.length < limit && guard < 5000) {
      guard++;
      const weekStart = addDays(week0, w * 7);
      if (weekStart > until) break;
      for (const wd of days) {
        const d = addDays(weekStart, wd);
        if (d < start) continue;
        if (index >= maxCount) return out;
        index++;
        push(d);
        if (d > until) break;
      }
      w += interval;
    }
    return out;
  }

  // monthly with fixed days (e.g. quincena on the 15th and 30th)
  if (rule.freq === "monthly" && rule.byMonthDay && rule.byMonthDay.length > 0) {
    const days = normalizeMonthDays(rule.byMonthDay);
    const firstMonth = `${start.slice(0, 7)}-01`;
    let m = 0;
    if (from > start && !Number.isFinite(maxCount)) {
      const monthsBetween =
        (Number(from.slice(0, 4)) - Number(start.slice(0, 4))) * 12 + (Number(from.slice(5, 7)) - Number(start.slice(5, 7)));
      m = Math.max(0, Math.floor(monthsBetween / interval) - 1) * interval;
    }
    let guard = 0;
    while (out.length < limit && guard < 5000) {
      guard++;
      const monthStart = addMonths(firstMonth, m, 1);
      if (monthStart > until) break;
      for (const day of days) {
        const d = addMonths(firstMonth, m, day);
        if (d < start) continue;
        if (d > until || index >= maxCount) return out;
        index++;
        push(d);
      }
      m += interval;
    }
    return out;
  }

  // monthly / yearly
  const stepMonths = rule.freq === "monthly" ? interval : interval * 12;
  const anchorDay = Number(start.slice(8, 10));
  let k = 0;
  if (from > start && !Number.isFinite(maxCount)) {
    const monthsBetween =
      (Number(from.slice(0, 4)) - Number(start.slice(0, 4))) * 12 + (Number(from.slice(5, 7)) - Number(start.slice(5, 7)));
    k = Math.max(0, Math.floor(monthsBetween / stepMonths) - 1);
  }
  index = k;
  let guard = 0;
  while (out.length < limit && guard < 5000 && index < maxCount) {
    guard++;
    const d = addMonths(start, index * stepMonths, anchorDay);
    if (d > until) break;
    push(d);
    index++;
  }
  return out;
}

/** First occurrence on or after `onOrAfter`, or null when the series has ended. */
export function nextOccurrence(start: DateStr, rule: Recurrence | null | undefined, onOrAfter: DateStr): DateStr | null {
  if (!rule) return start >= onOrAfter ? start : null;
  const horizon = addDays(onOrAfter > start ? onOrAfter : start, 800);
  const list = occurrencesBetween(start, rule, onOrAfter, horizon, 1);
  return list[0] ?? null;
}

/** The occurrence strictly after `after`. */
export function occurrenceAfter(start: DateStr, rule: Recurrence | null | undefined, after: DateStr): DateStr | null {
  return nextOccurrence(start, rule, addDays(after, 1));
}
