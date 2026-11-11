import { describe, expect, it } from "vitest";
import { addDays, diffDays, startOfWeek, zonedNow } from "@/lib/dates";
import { nextOccurrence, occurrenceAfter, occurrencesBetween } from "@/lib/recurrence";

describe("dates", () => {
  it("computes today in the configured time zone, not the device zone", () => {
    // 2026-11-11T03:30Z is still Nov 10 in Bogotá (UTC-5)
    const at = new Date("2026-11-11T03:30:00Z");
    expect(zonedNow("America/Bogota", at).date).toBe("2026-11-10");
    expect(zonedNow("Europe/Madrid", at).date).toBe("2026-11-11");
  });

  it("does date arithmetic on calendar days", () => {
    expect(addDays("2026-02-28", 1)).toBe("2026-03-01");
    expect(addDays("2024-02-28", 1)).toBe("2024-02-29");
    expect(diffDays("2026-11-11", "2026-12-01")).toBe(20);
    expect(startOfWeek("2026-11-11", 1)).toBe("2026-11-09"); // Wednesday → Monday
    expect(startOfWeek("2026-11-11", 0)).toBe("2026-11-08");
  });
});

describe("recurrence", () => {
  it("keeps monthly rules on the anchor day, clamping short months", () => {
    const r = { freq: "monthly" as const, interval: 1 };
    expect(occurrencesBetween("2026-01-31", r, "2026-01-01", "2026-05-31")).toEqual([
      "2026-01-31",
      "2026-02-28",
      "2026-03-31",
      "2026-04-30",
      "2026-05-31",
    ]);
  });

  it("supports weekdays and every-two-weeks rules", () => {
    const weekdays = { freq: "weekly" as const, interval: 1, byWeekday: [1, 2, 3, 4, 5] };
    expect(occurrencesBetween("2026-11-09", weekdays, "2026-11-09", "2026-11-17")).toEqual([
      "2026-11-09",
      "2026-11-10",
      "2026-11-11",
      "2026-11-12",
      "2026-11-13",
      "2026-11-16",
      "2026-11-17",
    ]);
    const biweekly = { freq: "weekly" as const, interval: 2 };
    expect(occurrencesBetween("2026-11-02", biweekly, "2026-11-01", "2026-12-31")).toEqual([
      "2026-11-02",
      "2026-11-16",
      "2026-11-30",
      "2026-12-14",
      "2026-12-28",
    ]);
  });

  it("stops after a number of installments", () => {
    const r = { freq: "monthly" as const, interval: 1, count: 3 };
    expect(occurrencesBetween("2026-01-15", r, "2025-01-01", "2027-01-01")).toEqual(["2026-01-15", "2026-02-15", "2026-03-15"]);
    expect(occurrenceAfter("2026-01-15", r, "2026-03-15")).toBeNull();
  });

  it("finds the next occurrence far from the anchor efficiently", () => {
    const r = { freq: "daily" as const, interval: 3 };
    // 2.506 days from the anchor; 2506 mod 3 = 1 → next is two days later
    expect(nextOccurrence("2020-01-01", r, "2026-11-11")).toBe("2026-11-13");
    expect(nextOccurrence("2026-12-01", null, "2026-11-11")).toBe("2026-12-01");
    expect(nextOccurrence("2026-10-01", null, "2026-11-11")).toBeNull();
  });
});
