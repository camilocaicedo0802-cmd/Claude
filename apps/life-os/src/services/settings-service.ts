import { db, DEMO_DB_NAME, LifeOSDB, MODE_STORAGE_KEY, TABLE_NAMES, type DataMode } from "@/db/db";
import { ensureDefaults } from "@/db/defaults";
import type { Settings } from "@/db/types";
import { nowISO } from "@/lib/dates";
import { DomainError } from "./common";

export const THEME_STORAGE_KEY = "lifeos:theme";

export async function updateSettings(patch: Partial<Omit<Settings, "id">>) {
  await db().settings.update("app", { ...patch, updatedAt: nowISO() });
  if (patch.theme && typeof window !== "undefined") {
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, patch.theme);
    } catch {
      /* storage unavailable: theme still applies for this session */
    }
  }
}

// ── Backup ───────────────────────────────────────────────────────────────────

export const BACKUP_FORMAT = "lifeos-backup";
export const BACKUP_VERSION = 1;

export interface Backup {
  format: typeof BACKUP_FORMAT;
  version: number;
  exportedAt: string;
  tables: Record<string, unknown[]>;
}

export async function exportBackup(): Promise<Backup> {
  const d = db();
  const tables: Record<string, unknown[]> = {};
  await d.transaction("r", TABLE_NAMES.map((n) => d.table(n)), async () => {
    for (const name of TABLE_NAMES) tables[name] = await d.table(name).toArray();
  });
  return { format: BACKUP_FORMAT, version: BACKUP_VERSION, exportedAt: nowISO(), tables };
}

export function parseBackup(text: string): Backup {
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    throw new DomainError("El archivo no es un respaldo válido (JSON dañado).");
  }
  const b = data as Partial<Backup>;
  if (!b || b.format !== BACKUP_FORMAT || typeof b.tables !== "object" || !b.tables) {
    throw new DomainError("El archivo no es un respaldo de LIFE OS.");
  }
  if ((b.version ?? 0) > BACKUP_VERSION) {
    throw new DomainError("Este respaldo es de una versión más nueva de LIFE OS.");
  }
  return b as Backup;
}

/** Replaces every table with the backup contents in a single transaction (all or nothing). */
export async function restoreBackup(backup: Backup) {
  const d = db();
  await d.transaction("rw", TABLE_NAMES.map((n) => d.table(n)), async () => {
    for (const name of TABLE_NAMES) {
      const rows = backup.tables[name];
      await d.table(name).clear();
      if (Array.isArray(rows) && rows.length) await d.table(name).bulkPut(rows);
    }
  });
  await ensureDefaults(d);
}

/** Deletes every record in the active database and restores defaults. */
export async function resetAllData() {
  const d = db();
  await d.transaction("rw", TABLE_NAMES.map((n) => d.table(n)), async () => {
    for (const name of TABLE_NAMES) await d.table(name).clear();
  });
  await ensureDefaults(d);
}

// ── Demo mode ────────────────────────────────────────────────────────────────

/** Switches between real and demo data. They are separate databases; switching reloads the app. */
export async function switchMode(mode: DataMode) {
  if (mode === "demo") {
    const demo = new LifeOSDB(DEMO_DB_NAME);
    await demo.open();
    await ensureDefaults(demo);
    const { seedDemo } = await import("@/db/demo");
    await seedDemo(demo);
    demo.close();
  }
  try {
    window.localStorage.setItem(MODE_STORAGE_KEY, mode);
  } catch {
    throw new DomainError("No se pudo cambiar de modo: el navegador bloquea el almacenamiento local.");
  }
  window.location.reload();
}

export async function discardDemo() {
  try {
    window.localStorage.setItem(MODE_STORAGE_KEY, "real");
  } catch {
    /* ignore */
  }
  await new LifeOSDB(DEMO_DB_NAME).delete();
  window.location.reload();
}

/** Asks the browser to keep this site's data even under storage pressure. */
export async function requestPersistentStorage(): Promise<boolean | null> {
  if (typeof navigator === "undefined" || !navigator.storage?.persist) return null;
  try {
    if (await navigator.storage.persisted()) return true;
    return await navigator.storage.persist();
  } catch {
    return null;
  }
}
