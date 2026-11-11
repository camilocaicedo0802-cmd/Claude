import { db } from "@/db/db";
import type { Activity } from "@/db/types";
import { nowISO } from "@/lib/dates";
import { uid } from "@/lib/utils";

/** An expected, user-facing error: the message is shown as is. */
export class DomainError extends Error {
  constructor(
    message: string,
    public code: string = "invalid",
    public data?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "DomainError";
  }
}

export function errorMessage(error: unknown): string {
  if (error instanceof DomainError) return error.message;
  if (error instanceof Error && error.name === "DomainError") return error.message;
  console.error(error);
  return "No se pudo guardar. Inténtalo de nuevo.";
}

export async function logActivity(entry: Omit<Activity, "id" | "at">) {
  await db().activities.add({ ...entry, id: uid(), at: nowISO() });
}
