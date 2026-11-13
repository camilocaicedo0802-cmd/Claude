import { describe, expect, it } from "vitest";
import Dexie from "dexie";
import { LifeOSDB } from "@/db/db";
import { uid } from "@/lib/utils";

describe("database upgrade", () => {
  it("keeps existing data when upgrading from v1 to v2 (focus sessions)", async () => {
    const name = `migr-${uid()}`;
    // Database as it existed before the planner (version 1 only).
    const old = new Dexie(name);
    old.version(1).stores({ tasks: "id, date, status, seriesId, clientId, jobId", settings: "id" });
    await old.open();
    await old.table("tasks").add({ id: "t1", title: "Videos ALI", status: "todo", date: "2026-11-11", subtasks: [], postponed: 0, order: 0, priority: 3 });
    old.close();

    const upgraded = new LifeOSDB(name);
    await upgraded.open();
    expect(upgraded.verno).toBe(2);
    expect((await upgraded.tasks.get("t1"))?.title).toBe("Videos ALI");
    await upgraded.focusSessions.add({ id: "s1", date: "2026-11-13", startedAt: "x", endedAt: "y", minutes: 25, title: "Videos ALI", taskId: "t1", completed: true });
    expect(await upgraded.focusSessions.count()).toBe(1);
    upgraded.close();
  });
});
