import type { Task, TaskCategory, TaskPriority } from "@/db/types";
import { normalize } from "@/lib/utils";
import type { DateStr } from "@/lib/dates";

// ── Tracker stages ───────────────────────────────────────────────────────────

export type TaskStage = "not_started" | "in_progress" | "done";

export const STAGE_LABEL: Record<TaskStage, string> = {
  not_started: "Sin empezar",
  in_progress: "En curso",
  done: "Completada",
};

export const STAGE_COLOR: Record<TaskStage, string> = {
  not_started: "slate",
  in_progress: "sky",
  done: "emerald",
};

export const STAGES: TaskStage[] = ["not_started", "in_progress", "done"];

export function taskStage(t: Pick<Task, "status" | "inProgress">): TaskStage {
  if (t.status === "done") return "done";
  return t.inProgress ? "in_progress" : "not_started";
}

export const PRIORITY_NAME: Record<TaskPriority, string> = { 0: "Sin prioridad", 1: "Baja", 2: "Media", 3: "Alta" };
export const PRIORITY_COLOR: Record<TaskPriority, string> = { 0: "slate", 1: "sky", 2: "amber", 3: "rose" };

export function categoryFor(key: string | null | undefined, categories: TaskCategory[]): TaskCategory | undefined {
  if (!key) return undefined;
  return categories.find((c) => c.key === key) ?? { key, name: key.charAt(0).toUpperCase() + key.slice(1), color: "slate" };
}

/** A friendly default icon from the task title, used when importing without an icon column. */
export function guessIcon(title: string): string | null {
  const t = normalize(title);
  if (/video|reel|youtube|edicion|editar|grabar|clip/.test(t)) return "clapperboard";
  if (/disen|logo|ilustr|dibuj|arte|pint/.test(t)) return "brush";
  if (/foto/.test(t)) return "camera";
  if (/linkedin|perfil|curriculum|hoja de vida|cv\b/.test(t)) return "files";
  if (/portafolio|portfolio|web|pagina/.test(t)) return "globe";
  if (/document|archivo|carpeta|organizar|subir|cargar/.test(t)) return "laptop";
  if (/cliente|propuesta|cotiz|freelance|workana|venta/.test(t)) return "briefcase";
  if (/pagar|cobrar|factura|banco|dinero/.test(t)) return "banknote";
  if (/llamar|whatsapp|mensaje|correo|email/.test(t)) return "send";
  if (/estudi|leer|curso|clase/.test(t)) return "book-open";
  if (/gym|gimnasio|ejercicio|correr/.test(t)) return "dumbbell";
  return null;
}

// ── Import (paste from Notion, Excel, Sheets or plain text) ─────────────────

export interface ImportRow {
  line: number;
  title: string;
  stage: TaskStage;
  priority: TaskPriority;
  /** Existing category key, or the key of a category that will be created. */
  category: string | null;
  points: number | null;
  date: DateStr | null;
  icon: string | null;
}

export interface ImportResult {
  rows: ImportRow[];
  newCategories: TaskCategory[];
  skipped: Array<{ line: number; reason: string }>;
}

type Field = "stage" | "title" | "priority" | "category" | "points" | "date" | "icon";

const HEADER_ALIASES: Record<Field, string[]> = {
  stage: ["estado", "status", "etapa"],
  title: ["tarea", "task", "nombre", "name", "titulo", "title", "pendiente"],
  priority: ["prioridad", "priority"],
  category: ["categoria", "category", "area", "tipo", "proyecto"],
  points: ["puntos", "points", "pts", "esfuerzo"],
  date: ["fecha", "date", "vence", "due", "fecha limite", "deadline"],
  icon: ["icono", "icon"],
};

const MONTHS: Record<string, number> = {
  enero: 1, ene: 1, january: 1, jan: 1,
  febrero: 2, feb: 2, february: 2,
  marzo: 3, mar: 3, march: 3,
  abril: 4, abr: 4, april: 4, apr: 4,
  mayo: 5, may: 5,
  junio: 6, jun: 6, june: 6,
  julio: 7, jul: 7, july: 7,
  agosto: 8, ago: 8, august: 8, aug: 8,
  septiembre: 9, setiembre: 9, sep: 9, sept: 9, september: 9,
  octubre: 10, oct: 10, october: 10,
  noviembre: 11, nov: 11, november: 11,
  diciembre: 12, dic: 12, december: 12, dec: 12,
};

function splitLine(line: string, delimiter: string): string[] {
  if (delimiter === "\t") return line.split("\t").map((c) => c.trim());
  const out: string[] = [];
  let cur = "";
  let quoted = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (quoted) {
      if (ch === '"' && line[i + 1] === '"') {
        cur += '"';
        i++;
      } else if (ch === '"') quoted = false;
      else cur += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === delimiter) {
      out.push(cur.trim());
      cur = "";
    } else cur += ch;
  }
  out.push(cur.trim());
  return out;
}

function detectDelimiter(lines: string[]): string | null {
  const sample = lines.slice(0, 5);
  if (sample.some((l) => l.includes("\t"))) return "\t";
  if (sample.some((l) => l.includes(";"))) return ";";
  if (sample.some((l) => l.includes("|"))) return "|";
  if (sample.every((l) => l.split(",").length >= 3)) return ",";
  return null;
}

export function parseStage(v: string): TaskStage {
  const n = normalize(v);
  if (/curso|progres|proceso|doing|haciendo|empezad/.test(n)) return "in_progress";
  if (/complet|hecho|hecha|done|terminad|listo|lista|finaliz/.test(n)) return "done";
  return "not_started";
}

export function parsePriority(v: string): TaskPriority {
  const n = normalize(v);
  if (/alta|high|urgent|importante|^3$/.test(n)) return 3;
  if (/media|medium|normal|^2$/.test(n)) return 2;
  if (/baja|low|^1$/.test(n)) return 1;
  return 0;
}

export function parseDateText(v: string, fallbackYear: number): DateStr | null {
  const s = normalize(v).split(/→|->| a /)[0].trim();
  if (!s) return null;
  let m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (m) return iso(Number(m[1]), Number(m[2]), Number(m[3]));
  m = s.match(/^(\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{2,4}))?$/);
  if (m) {
    const y = m[3] ? (m[3].length === 2 ? 2000 + Number(m[3]) : Number(m[3])) : fallbackYear;
    return iso(y, Number(m[2]), Number(m[1]));
  }
  // "october 23, 2026", "oct 23 2026"
  m = s.match(/^([a-z]+)\.?\s+(\d{1,2}),?\s*(\d{4})?/);
  if (m && MONTHS[m[1]]) return iso(m[3] ? Number(m[3]) : fallbackYear, MONTHS[m[1]], Number(m[2]));
  // "23 de octubre de 2026", "23 oct 2026"
  m = s.match(/^(\d{1,2})\s+(?:de\s+)?([a-z]+)\.?(?:\s+(?:de\s+)?(\d{4}))?/);
  if (m && MONTHS[m[2]]) return iso(m[3] ? Number(m[3]) : fallbackYear, MONTHS[m[2]], Number(m[1]));
  return null;
}

function iso(y: number, m: number, d: number): DateStr | null {
  if (m < 1 || m > 12 || d < 1 || d > 31) return null;
  const date = new Date(y, m - 1, d, 12);
  if (date.getMonth() !== m - 1) return null;
  return `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
}

function slug(s: string) {
  return normalize(s).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 32) || "categoria";
}

const NEW_CATEGORY_COLORS = ["iris", "teal", "pink", "orange", "sky", "violet", "amber", "emerald"];

/**
 * Parses pasted rows into tasks. Understands a header row in Spanish or English
 * (Estado, Tarea, Prioridad, Categoría, Puntos, Fecha, Icono) in any order; without
 * a header it assumes Notion's order: Estado, Tarea, Prioridad, Categoría, Puntos, Fecha.
 */
export function parseTaskImport(text: string, categories: TaskCategory[], validIcons: string[], today: DateStr): ImportResult {
  const lines = text
    .replace(/\r\n?/g, "\n")
    .split("\n")
    .map((l) => l.replace(/\s+$/, ""))
    .filter((l) => l.trim().length > 0);
  const result: ImportResult = { rows: [], newCategories: [], skipped: [] };
  if (lines.length === 0) return result;
  const delimiter = detectDelimiter(lines);
  const table = lines.map((l) => (delimiter ? splitLine(l, delimiter) : [l.trim()]));

  let order: Array<Field | null>;
  let start = 0;
  const header = table[0].map((c) => normalize(c));
  const headerFields = header.map((h) => (Object.keys(HEADER_ALIASES) as Field[]).find((f) => HEADER_ALIASES[f].includes(h)) ?? null);
  if (headerFields.filter(Boolean).length >= 2 || (headerFields.includes("title") && table[0].length === 1)) {
    order = headerFields;
    start = 1;
  } else if (table[0].length === 1) {
    order = ["title"];
  } else {
    const firstIsStage = /sin empezar|en curso|complet|not started|in progress|done|pendiente|hecho|terminad/.test(normalize(table[0][0]));
    order = firstIsStage ? ["stage", "title", "priority", "category", "points", "date", "icon"] : ["title", "priority", "category", "points", "date", "icon"];
  }

  const year = Number(today.slice(0, 4));
  const known = [...categories];
  const findCategory = (raw: string): string | null => {
    const n = normalize(raw.replace(/\.{2,}|…/g, ""));
    if (!n) return null;
    const exact = known.find((c) => normalize(c.name) === n || c.key === n);
    if (exact) return exact.key;
    const prefix = known.find((c) => normalize(c.name).startsWith(n) || n.startsWith(normalize(c.name)));
    if (prefix) return prefix.key;
    let key = slug(raw);
    while (known.some((c) => c.key === key)) key = `${key}-2`;
    const created = { key, name: raw.replace(/\.{2,}|…/g, "").trim(), color: NEW_CATEGORY_COLORS[result.newCategories.length % NEW_CATEGORY_COLORS.length] };
    known.push(created);
    result.newCategories.push(created);
    return key;
  };

  for (let i = start; i < table.length; i++) {
    const cells = table[i];
    const get = (f: Field) => {
      const idx = order.indexOf(f);
      return idx >= 0 ? cells[idx] ?? "" : "";
    };
    const title = get("title").replace(/^[-*•]\s+/, "").trim();
    if (!title) {
      result.skipped.push({ line: i + 1, reason: "Sin nombre de tarea" });
      continue;
    }
    const iconRaw = normalize(get("icon"));
    const pointsRaw = get("points").replace(",", ".");
    const points = pointsRaw && Number.isFinite(Number(pointsRaw)) ? Math.max(0, Math.round(Number(pointsRaw))) : null;
    result.rows.push({
      line: i + 1,
      title,
      stage: get("stage") ? parseStage(get("stage")) : "not_started",
      priority: get("priority") ? parsePriority(get("priority")) : 0,
      category: get("category") ? findCategory(get("category")) : null,
      points,
      date: get("date") ? parseDateText(get("date"), year) : null,
      icon: iconRaw && validIcons.includes(iconRaw) ? iconRaw : guessIcon(title),
    });
  }
  return result;
}

/** Encodes rows as the plain tab-separated text the importer reads (used for share links). */
export function encodeImportText(rows: string[][]): string {
  return rows.map((r) => r.join("\t")).join("\n");
}
