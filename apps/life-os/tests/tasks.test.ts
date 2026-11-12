import { beforeEach, describe, expect, it } from "vitest";
import { db, LifeOSDB, setDB } from "@/db/db";
import { DEFAULT_TASK_CATEGORIES, ensureDefaults } from "@/db/defaults";
import { parseDateText, parseTaskImport, taskStage } from "@/domain/tasks";
import { uid } from "@/lib/utils";
import { createTask, importTasks, setTaskStage } from "@/services/life-service";

const TODAY = "2026-11-12";
const ICONS = ["clapperboard", "laptop", "brush", "files"];

beforeEach(async () => {
  const fresh = new LifeOSDB(`test-${uid()}`);
  setDB(fresh);
  await ensureDefaults(fresh);
});

describe("import parser", () => {
  it("reads rows copied from a Notion table (no header, tab separated)", () => {
    const text = [
      "Sin Empezar\tVideos ALI\tAlta\tTrabajo\t5\t11/11/2026",
      "En Curso\tVideo la especie absurda\tAlta\tProyecto ...\t5\t09/11/2026",
      "Sin Empezar\tDiseños Spider Man\tAlta\tCasa\t5\t08/11/2026",
      "En Curso\tOrganizar y eliminar archivos compu\tAlta\tProyecto ...\t2\t23/10/2026",
    ].join("\n");
    const r = parseTaskImport(text, DEFAULT_TASK_CATEGORIES, ICONS, TODAY);
    expect(r.skipped).toEqual([]);
    expect(r.newCategories).toEqual([]);
    expect(r.rows.map((x) => [x.title, x.stage, x.priority, x.category, x.points, x.date])).toEqual([
      ["Videos ALI", "not_started", 3, "trabajo", 5, "2026-11-11"],
      ["Video la especie absurda", "in_progress", 3, "proyecto", 5, "2026-11-09"],
      ["Diseños Spider Man", "not_started", 3, "hogar", 5, "2026-11-08"],
      ["Organizar y eliminar archivos compu", "in_progress", 3, "proyecto", 2, "2026-10-23"],
    ]);
    expect(r.rows[0].icon).toBe("clapperboard"); // guessed from the title
    expect(r.rows[2].icon).toBe("brush");
  });

  it("accepts a header in any order, CSV quoting and new categories", () => {
    const text = 'Fecha,Tarea,Categoría,Puntos,Estado,Icono\n2026-12-01,"Comprar regalos, tarjetas",Navidad,3,Completada,files\n,Llamar al contador,,,,';
    const r = parseTaskImport(text, DEFAULT_TASK_CATEGORIES, ICONS, TODAY);
    expect(r.rows[0]).toMatchObject({ title: "Comprar regalos, tarjetas", date: "2026-12-01", points: 3, stage: "done", icon: "files" });
    expect(r.newCategories).toEqual([{ key: "navidad", name: "Navidad", color: expect.any(String) }]);
    expect(r.rows[0].category).toBe("navidad");
    expect(r.rows[1]).toMatchObject({ title: "Llamar al contador", date: null, category: null, points: null });
  });

  it("reads one task per line when there are no columns", () => {
    const r = parseTaskImport("- Pagar arriendo\n• Revisar correo\n\n", DEFAULT_TASK_CATEGORIES, ICONS, TODAY);
    expect(r.rows.map((x) => x.title)).toEqual(["Pagar arriendo", "Revisar correo"]);
  });

  it("understands Spanish, English and numeric dates", () => {
    expect(parseDateText("23/10/2026", 2026)).toBe("2026-10-23");
    expect(parseDateText("October 23, 2026", 2026)).toBe("2026-10-23");
    expect(parseDateText("23 de octubre de 2026", 2026)).toBe("2026-10-23");
    expect(parseDateText("5/1", 2026)).toBe("2026-01-05");
    expect(parseDateText("31/02/2026", 2026)).toBeNull();
  });
});

describe("tracker stages and import", () => {
  it("moves a task between Sin empezar, En curso and Completada", async () => {
    const id = await createTask({ title: "Videos Samantha", date: TODAY });
    const get = async () => taskStage((await db().tasks.get(id))!);
    expect(await get()).toBe("not_started");
    await setTaskStage(id, "in_progress");
    expect(await get()).toBe("in_progress");
    await setTaskStage(id, "done");
    expect(await get()).toBe("done");
    await setTaskStage(id, "in_progress");
    expect(await get()).toBe("in_progress");
    expect((await db().tasks.get(id))!.completedAt).toBeNull();
  });

  it("imports without duplicating when the same list is pasted twice", async () => {
    const r = parseTaskImport("En Curso\tVideos Matcha\tAlta\tTrabajo\t5\t29/10/2026\nSin Empezar\tBuscar clientes\tAlta\tFreelance\t5\t28/10/2026", DEFAULT_TASK_CATEGORIES, ICONS, TODAY);
    expect(await importTasks(r.rows, r.newCategories)).toEqual({ created: 2, skipped: 0 });
    expect(await importTasks(r.rows, r.newCategories)).toEqual({ created: 0, skipped: 2 });
    const tasks = await db().tasks.toArray();
    expect(tasks).toHaveLength(2);
    expect(tasks.find((t) => t.title === "Videos Matcha")).toMatchObject({ inProgress: true, points: 5, area: "trabajo", priority: 3, date: "2026-10-29" });
    const settings = await db().settings.get("app");
    expect(settings!.taskCategories.some((c) => c.name === "Freelance")).toBe(true);
  });
});
