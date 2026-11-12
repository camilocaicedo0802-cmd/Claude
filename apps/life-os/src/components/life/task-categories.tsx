"use client";

import * as React from "react";
import { ArrowDown, ArrowUp, Plus, Trash2 } from "lucide-react";
import { useData } from "@/hooks/data";
import type { TaskCategory } from "@/db/types";
import { normalize } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/form-controls";
import { Sheet } from "@/components/ui/overlays";
import { ColorPicker } from "@/components/shared/inputs";
import { PALETTE } from "@/components/shared/primitives";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { db } from "@/db/db";
import { nowISO } from "@/lib/dates";
import { updateSettings } from "@/services/settings-service";

/** Edit the tracker's categories: rename, recolour, reorder, add and delete. */
export function CategoriesSheet({ onClose }: { onClose: () => void }) {
  const data = useData();
  const { confirm } = useUI();
  const [open, setOpen] = React.useState(true);
  const [name, setName] = React.useState("");
  const list = data.settings.taskCategories;
  const close = () => {
    setOpen(false);
    setTimeout(onClose, 180);
  };
  const save = (next: TaskCategory[], msg?: string) => runSave(() => updateSettings({ taskCategories: next }), msg);
  const move = (i: number, d: -1 | 1) => {
    const next = [...list];
    [next[i], next[i + d]] = [next[i + d], next[i]];
    void save(next);
  };
  const add = (e: React.FormEvent) => {
    e.preventDefault();
    const n = name.trim();
    if (!n) return;
    if (list.some((c) => normalize(c.name) === normalize(n))) return;
    let key = normalize(n).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "categoria";
    while (list.some((c) => c.key === key)) key = `${key}-2`;
    void save([...list, { key, name: n, color: PALETTE[list.length % PALETTE.length] }], "Categoría agregada").then((ok) => ok && setName(""));
  };
  const remove = async (c: TaskCategory) => {
    const used = data.tasks.filter((t) => t.area === c.key).length;
    const ok = await confirm({
      title: `¿Eliminar la categoría «${c.name}»?`,
      description: used ? `${used} ${used === 1 ? "tarea quedará" : "tareas quedarán"} sin categoría. Las tareas no se borran.` : undefined,
      confirmLabel: "Eliminar",
      destructive: true,
    });
    if (!ok) return;
    await runSave(async () => {
      const d = db();
      await d.transaction("rw", [d.tasks, d.settings], async () => {
        const tasks = await d.tasks.filter((t) => t.area === c.key).toArray();
        for (const t of tasks) await d.tasks.update(t.id, { area: null, updatedAt: nowISO() });
        await d.settings.update("app", { taskCategories: list.filter((x) => x.key !== c.key), updatedAt: nowISO() });
      });
    }, "Categoría eliminada");
  };

  return (
    <Sheet open={open} onOpenChange={(v) => !v && close()} title="Categorías de tareas" description="Cambia nombres y colores; el orden también se usa al agrupar.">
      <ul className="space-y-2">
        {list.map((c, i) => (
          <li key={c.key} className="space-y-2 rounded-lg border border-border p-3">
            <div className="flex items-center gap-1.5">
              <Input
                aria-label="Nombre de la categoría"
                defaultValue={c.name}
                onBlur={(e) => {
                  const v = e.target.value.trim();
                  if (v && v !== c.name) void save(list.map((x) => (x.key === c.key ? { ...x, name: v } : x)), "Categoría renombrada");
                }}
              />
              <Button variant="ghost" size="icon-sm" aria-label="Subir" disabled={i === 0} onClick={() => move(i, -1)}>
                <ArrowUp />
              </Button>
              <Button variant="ghost" size="icon-sm" aria-label="Bajar" disabled={i === list.length - 1} onClick={() => move(i, 1)}>
                <ArrowDown />
              </Button>
              <Button variant="destructive-ghost" size="icon-sm" aria-label={`Eliminar ${c.name}`} onClick={() => remove(c)}>
                <Trash2 />
              </Button>
            </div>
            <ColorPicker colors={PALETTE} value={c.color} onChange={(color) => void save(list.map((x) => (x.key === c.key ? { ...x, color } : x)))} />
          </li>
        ))}
      </ul>
      <form onSubmit={add} className="mt-4 flex gap-2 rounded-lg bg-muted/60 p-3">
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nueva categoría (ej. Freelance)" aria-label="Nueva categoría" />
        <Button type="submit" size="icon" aria-label="Agregar categoría">
          <Plus />
        </Button>
      </form>
    </Sheet>
  );
}
