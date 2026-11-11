/**
 * Calendar dates are stored as plain strings in the user's configured time zone:
 *   DateStr "YYYY-MM-DD", TimeStr "HH:mm".
 * "Today" is computed with Intl in the configured zone (America/Bogota by default), never
 * from the device clock's zone. Date arithmetic runs on naive dates anchored at noon so
 * daylight-saving jumps can never move a date to the previous day.
 */
export type DateStr = string;
export type TimeStr = string;

export const DEFAULT_TIME_ZONE = "America/Bogota";

const partsCache = new Map<string, Intl.DateTimeFormat>();

function zoneFormatter(timeZone: string) {
  let f = partsCache.get(timeZone);
  if (!f) {
    f = new Intl.DateTimeFormat("en-CA", {
      timeZone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hourCycle: "h23",
    });
    partsCache.set(timeZone, f);
  }
  return f;
}

export function zonedNow(timeZone: string = DEFAULT_TIME_ZONE, at: Date = new Date()) {
  let parts: Intl.DateTimeFormatPart[];
  try {
    parts = zoneFormatter(timeZone).formatToParts(at);
  } catch {
    parts = zoneFormatter(DEFAULT_TIME_ZONE).formatToParts(at);
  }
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? "00";
  const hour = get("hour") === "24" ? "00" : get("hour");
  return {
    date: `${get("year")}-${get("month")}-${get("day")}` as DateStr,
    time: `${hour}:${get("minute")}` as TimeStr,
    hour: Number(hour),
  };
}

export function todayIn(timeZone?: string): DateStr {
  return zonedNow(timeZone).date;
}

export function isDateStr(value: unknown): value is DateStr {
  return typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value);
}

export function parseDate(d: DateStr): Date {
  const [y, m, day] = d.split("-").map(Number);
  return new Date(y, m - 1, day, 12, 0, 0, 0);
}

export function toDateStr(date: Date): DateStr {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function addDays(d: DateStr, n: number): DateStr {
  const date = parseDate(d);
  date.setDate(date.getDate() + n);
  return toDateStr(date);
}

/** Adds months clamping to the last day (Jan 31 + 1 month = Feb 28/29). */
export function addMonths(d: DateStr, n: number, anchorDay?: number): DateStr {
  const [y, m, day] = d.split("-").map(Number);
  const targetDay = anchorDay ?? day;
  const total = (m - 1) + n;
  const ty = y + Math.floor(total / 12);
  const tm = ((total % 12) + 12) % 12;
  const last = daysInMonthOf(ty, tm + 1);
  return toDateStr(new Date(ty, tm, Math.min(targetDay, last), 12));
}

export function addYears(d: DateStr, n: number): DateStr {
  return addMonths(d, n * 12);
}

export function daysInMonthOf(year: number, month1: number): number {
  return new Date(year, month1, 0, 12).getDate();
}

export function daysInMonth(d: DateStr): number {
  const [y, m] = d.split("-").map(Number);
  return daysInMonthOf(y, m);
}

/** Whole days from a to b (b - a). */
export function diffDays(a: DateStr, b: DateStr): number {
  const ms = parseDate(b).getTime() - parseDate(a).getTime();
  return Math.round(ms / 86_400_000);
}

export function weekday(d: DateStr): number {
  return parseDate(d).getDay();
}

export function startOfWeek(d: DateStr, weekStartsOn: number = 1): DateStr {
  const wd = weekday(d);
  const delta = (wd - weekStartsOn + 7) % 7;
  return addDays(d, -delta);
}

export function endOfWeek(d: DateStr, weekStartsOn: number = 1): DateStr {
  return addDays(startOfWeek(d, weekStartsOn), 6);
}

export function startOfMonth(d: DateStr): DateStr {
  return `${d.slice(0, 7)}-01`;
}

export function endOfMonth(d: DateStr): DateStr {
  return `${d.slice(0, 7)}-${String(daysInMonth(d)).padStart(2, "0")}`;
}

export function monthKey(d: DateStr): string {
  return d.slice(0, 7);
}

export function addMonthKey(key: string, n: number): string {
  return addMonths(`${key}-01`, n).slice(0, 7);
}

export function minDate(a: DateStr, b: DateStr): DateStr {
  return a <= b ? a : b;
}

export function maxDate(a: DateStr, b: DateStr): DateStr {
  return a >= b ? a : b;
}

export function eachDay(from: DateStr, to: DateStr): DateStr[] {
  const out: DateStr[] = [];
  let cur = from;
  let guard = 0;
  while (cur <= to && guard < 3700) {
    out.push(cur);
    cur = addDays(cur, 1);
    guard++;
  }
  return out;
}

export function inRange(d: DateStr, from: DateStr, to: DateStr): boolean {
  return d >= from && d <= to;
}

export function timeToMinutes(t: TimeStr): number {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}

export function minutesToTime(min: number): TimeStr {
  const clamped = Math.max(0, Math.min(24 * 60 - 1, Math.round(min)));
  return `${String(Math.floor(clamped / 60)).padStart(2, "0")}:${String(clamped % 60).padStart(2, "0")}`;
}

// ── Formatting (Spanish) ──────────────────────────────────────────────────────

const fmtCache = new Map<string, Intl.DateTimeFormat>();
function fmt(opts: Intl.DateTimeFormatOptions) {
  const key = JSON.stringify(opts);
  let f = fmtCache.get(key);
  if (!f) {
    f = new Intl.DateTimeFormat("es-CO", { ...opts, timeZone: "UTC" });
    fmtCache.set(key, f);
  }
  return f;
}

function utc(d: DateStr): Date {
  const [y, m, day] = d.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, day, 12));
}

const clean = (s: string) => s.replace(/\./g, "").replace(/\s+de\s+/g, " ");

/** 11/11/2026 */
export function formatDateNumeric(d: DateStr): string {
  const [y, m, day] = d.split("-");
  return `${day}/${m}/${y}`;
}

/** "mié 11 nov" */
export function formatDateShort(d: DateStr): string {
  return clean(fmt({ weekday: "short", day: "numeric", month: "short" }).format(utc(d)));
}

/** "11 nov" */
export function formatDayMonth(d: DateStr): string {
  return clean(fmt({ day: "numeric", month: "short" }).format(utc(d)));
}

/** "miércoles, 11 de noviembre" */
export function formatDateLong(d: DateStr): string {
  return fmt({ weekday: "long", day: "numeric", month: "long" }).format(utc(d));
}

/** "noviembre 2026" */
export function formatMonthYear(d: DateStr): string {
  return fmt({ month: "long", year: "numeric" }).format(utc(d));
}

/** "nov" */
export function formatMonthShort(d: DateStr): string {
  return clean(fmt({ month: "short" }).format(utc(d)));
}

/** "lun" */
export function formatWeekdayShort(d: DateStr): string {
  return clean(fmt({ weekday: "short" }).format(utc(d)));
}

export const WEEKDAY_LABELS = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
export const WEEKDAY_SHORT = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
export const WEEKDAY_LETTER = ["D", "L", "M", "X", "J", "V", "S"];

export function orderedWeekdays(weekStartsOn: number): number[] {
  return Array.from({ length: 7 }, (_, i) => (weekStartsOn + i) % 7);
}

/** "Hoy", "Mañana", "Ayer", "en 3 días", "hace 2 días", or "mié 11 nov". */
export function formatRelativeDay(d: DateStr, today: DateStr): string {
  const diff = diffDays(today, d);
  if (diff === 0) return "Hoy";
  if (diff === 1) return "Mañana";
  if (diff === -1) return "Ayer";
  if (diff > 1 && diff <= 6) return `en ${diff} días`;
  if (diff < -1 && diff >= -6) return `hace ${-diff} días`;
  return formatDateShort(d) + (d.slice(0, 4) !== today.slice(0, 4) ? ` ${d.slice(0, 4)}` : "");
}

export function formatTime(t: TimeStr): string {
  const [h, m] = t.split(":").map(Number);
  const suffix = h < 12 ? "a. m." : "p. m.";
  const hh = h % 12 === 0 ? 12 : h % 12;
  return `${hh}:${String(m).padStart(2, "0")} ${suffix}`;
}

export function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `${h} h ${m} min` : `${h} h`;
}

export function greetingFor(hour: number): string {
  if (hour < 5) return "Buenas noches";
  if (hour < 12) return "Buenos días";
  if (hour < 19) return "Buenas tardes";
  return "Buenas noches";
}

/** ISO instant for audit timestamps (createdAt / updatedAt). */
export function nowISO(): string {
  return new Date().toISOString();
}
