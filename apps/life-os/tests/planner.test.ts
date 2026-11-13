import { beforeEach, describe, expect, it } from "vitest";
import { db, LifeOSDB, setDB } from "@/db/db";
import { DEFAULT_PLANNER, SUGGESTED_TEMPLATE, ensureDefaults } from "@/db/defaults";
import type { Task } from "@/db/types";
import { autoPlan, dayCapacity, dayItems, freeSlots, mergeIntervals, nowAndNext, planCandidates } from "@/domain/planner";
import { timeToMinutes } from "@/lib/dates";
import { uid } from "@/lib/utils";
import { createTask } from "@/services/life-service";
import { applyDayTemplate, applyPlan, createBlock, recordFocusSession, restoreTasks, scheduleTask } from "@/services/planner-service";

const DAY = "2026-11-13";
const h = (t: string) => timeToMinutes(t);

function task(id: string, extra: Partial<Task> = {}): Task {
  return {
    id,
    title: id,
    date: DAY,
    time: null,
    durationMin: null,
    priority: 0,
    status: "todo",
    subtasks: [],
    postponed: 0,
    order: 0,
    createdAt: "2026-11-01T00:00:00Z",
    updatedAt: "2026-11-01T00:00:00Z",
    ...extra,
  };
}

beforeEach(async () => {
  const fresh = new LifeOSDB(`test-${uid()}`);
  setDB(fresh);
  await ensureDefaults(fresh);
});

describe("intervals", () => {
  it("merges overlapping intervals and finds free gaps", () => {
    expect(mergeIntervals([{ start: 60, end: 120 }, { start: 100, end: 150 }, { start: 200, end: 210 }])).toEqual([
      { start: 60, end: 150 },
      { start: 200, end: 210 },
    ]);
    expect(freeSlots([{ start: h("09:00"), end: h("10:00") }], h("08:00"), h("12:00"))).toEqual([
      { start: h("08:00"), end: h("09:00") },
      { start: h("10:00"), end: h("12:00") },
    ]);
  });
});

describe("auto-plan", () => {
  const settings = { ...DEFAULT_PLANNER, dayStart: "08:00", dayEnd: "18:00", focusStart: "09:00", focusEnd: "12:00", bufferMin: 10, defaultTaskMin: 60 };

  it("puts high priority in the high-energy window, respects events and breaks", () => {
    const meeting = { start: h("09:00"), end: h("10:00") };
    const r = autoPlan({
      date: DAY,
      candidates: [task("baja", { priority: 1, durationMin: 30 }), task("alta", { priority: 3, durationMin: 90 }), task("media", { priority: 2 })],
      busy: [meeting],
      settings,
      nowMin: null,
    });
    const alta = r.placed.find((p) => p.taskId === "alta")!;
    expect(alta.inFocusWindow).toBe(true);
    expect(alta.start).toBe(h("10:10")); // after the meeting + 10 min break
    expect(alta.end).toBe(h("11:40"));
    // nothing overlaps the meeting or another placed task (with the break)
    const all = [...r.placed].sort((a, b) => a.start - b.start);
    for (let i = 1; i < all.length; i++) expect(all[i].start).toBeGreaterThanOrEqual(all[i - 1].end + 10);
    for (const p of all) expect(p.end <= meeting.start - 10 || p.start >= meeting.end + 10).toBe(true);
    expect(r.unplaced).toEqual([]);
  });

  it("never plans in the past and reports what does not fit", () => {
    const r = autoPlan({
      date: DAY,
      candidates: [task("larga", { durationMin: 600 }), task("corta", { durationMin: 30 })],
      busy: [],
      settings,
      nowMin: h("16:52"),
    });
    expect(r.placed.map((p) => [p.taskId, p.start])).toEqual([["corta", h("17:00")]]);
    expect(r.unplaced.map((u) => u.taskId)).toEqual(["larga"]);
  });

  it("orders overdue and in-progress work before new work of the same priority", () => {
    const r = autoPlan({
      date: DAY,
      candidates: [task("nueva", { priority: 2, durationMin: 30 }), task("atrasada", { priority: 2, durationMin: 30, date: "2026-11-10" }), task("en-curso", { priority: 2, durationMin: 30, inProgress: true })],
      busy: [],
      settings,
      nowMin: null,
    });
    expect(r.placed.map((p) => p.taskId)).toEqual(["atrasada", "en-curso", "nueva"]);
  });
});

describe("now / next and capacity", () => {
  it("finds the current and next block and the free time of the day", () => {
    const items = [
      { key: "a", kind: "block" as const, id: "a", title: "Correos", start: h("08:00"), end: h("08:30"), color: "sky" },
      { key: "b", kind: "task" as const, id: "b", title: "Video", start: h("09:00"), end: h("11:00"), color: "orange" },
    ];
    const { now, next } = nowAndNext(items, h("08:15"));
    expect(now?.title).toBe("Correos");
    expect(next?.title).toBe("Video");
    expect(dayCapacity(items, { dayStart: "08:00", dayEnd: "18:00" })).toEqual({ window: 600, planned: 150, free: 450, overbooked: false });
  });

  it("lists tasks waiting for a time: today's and overdue, not done, without time", () => {
    const list = [task("hoy"), task("con-hora", { time: "10:00" }), task("atrasada", { date: "2026-11-01" }), task("hecha", { status: "done" }), task("manana", { date: "2026-11-14" })];
    expect(planCandidates(list, DAY, DAY).map((t) => t.id)).toEqual(["hoy", "atrasada"]);
    expect(planCandidates(list, "2026-11-14", DAY).map((t) => t.id)).toEqual(["manana"]);
  });
});

describe("planner services", () => {
  it("schedules, applies and undoes an auto-plan; blocks and templates show on the day", async () => {
    const a = await createTask({ title: "Videos ALI", date: "2026-11-11", priority: 3 });
    const b = await createTask({ title: "Buscar clientes", date: DAY });
    const previous = await applyPlan(DAY, [{ taskId: a, title: "", start: h("09:00"), end: h("10:30"), inFocusWindow: true }]);
    expect(await db().tasks.get(a)).toMatchObject({ date: DAY, time: "09:00", durationMin: 90 });
    await restoreTasks(previous);
    expect(await db().tasks.get(a)).toMatchObject({ date: "2026-11-11", time: null });

    await scheduleTask(b, DAY, "14:00", 30);
    await createBlock({ date: DAY, title: "Almuerzo", start: "12:30", end: "13:30", category: "personal" });
    // "Almuerzo 12:30" already exists, so the template skips it instead of duplicating it.
    expect(await applyDayTemplate(SUGGESTED_TEMPLATE, DAY)).toBe(SUGGESTED_TEMPLATE.blocks.length - 1);
    expect(await applyDayTemplate(SUGGESTED_TEMPLATE, DAY)).toBe(0); // no duplicates
    const items = dayItems(DAY, await db().tasks.toArray(), await db().events.toArray(), DEFAULT_PLANNER, () => "slate");
    expect(items.find((i) => i.kind === "task")).toMatchObject({ title: "Buscar clientes", start: h("14:00"), end: h("14:30") });
    expect(items.filter((i) => i.kind === "block").length).toBe(SUGGESTED_TEMPLATE.blocks.length);
  });

  it("records focus time on the task", async () => {
    const id = await createTask({ title: "Generar Video Youtube", date: DAY });
    await recordFocusSession({ date: DAY, startedAt: "2026-11-13T14:00:00Z", endedAt: "2026-11-13T14:25:00Z", minutes: 25, title: "Generar Video Youtube", taskId: id, completed: true });
    await recordFocusSession({ date: DAY, startedAt: "2026-11-13T15:00:00Z", endedAt: "2026-11-13T15:10:00Z", minutes: 10, title: "Generar Video Youtube", taskId: id, completed: false });
    expect((await db().tasks.get(id))!.actualMin).toBe(35);
    expect(await db().focusSessions.count()).toBe(2);
  });
});
