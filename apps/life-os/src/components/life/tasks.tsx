"use client";

import * as React from "react";
import { CheckCheck, Inbox, ListTodo, Plus, Search } from "lucide-react";
import { useData, useToday } from "@/hooks/data";
import type { Task } from "@/db/types";
import { addDays, endOfWeek, formatDateLong, instantToDate, startOfWeek, type DateStr } from "@/lib/dates";
import { matches } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/form-controls";
import { Chip, Segmented } from "@/components/ui/misc";
import { Card, EmptyState } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { TaskItem, usePriorityToggle } from "./bits";
import { QuickCapture } from "./today";

type View = "pendientes" | "hoy" | "semana" | "vencidas" | "sin-fecha" | "completadas";
const VIEW_LABEL: Record<View, string> = {
  pendientes: "Pendientes",
  hoy: "Hoy",
  semana: "Próximos 7 días",
  vencidas: "Vencidas",
  "sin-fecha": "Algún día",
  completadas: "Completadas",
};

export function TasksPage() {
  const data = useData();
  const today = useToday();
  const { openForm } = useUI();
  const { priorities, toggle } = usePriorityToggle(today);
  const [view, setView] = React.useState<View>("pendientes");
  const [priority, setPriority] = React.useState<"all" | "3" | "2" | "1">("all");
  const [groupBy, setGroupBy] = React.useState<"day" | "week">("day");
  const [query, setQuery] = React.useState("");

  React.useEffect(() => {
    const v = new URLSearchParams(window.location.search).get("vista") as View | null;
    if (v && v in VIEW_LABEL) setView(v);
  }, []);

  const base = data.tasks
    .filter((t) => (view === "completadas" ? t.status === "done" : t.status === "todo"))
    .filter((t) => {
      switch (view) {
        case "hoy":
          return t.date === today || (!!t.date && t.date < today);
        case "semana":
          return !!t.date && t.date >= today && t.date <= addDays(today, 7);
        case "vencidas":
          return !!t.date && t.date < today;
        case "sin-fecha":
          return !t.date;
        default:
          return true;
      }
    })
    .filter((t) => priority === "all" || t.priority === Number(priority))
    .filter((t) => matches([t.title, t.description, t.notes, data.clients.find((c) => c.id === t.clientId)?.name], query));

  const groups = React.useMemo(() => groupTasks(base, today, groupBy, data.settings.weekStartsOn, view === "completadas", data.settings.timeZone), [base, today, groupBy, data.settings.weekStartsOn, view, data.settings.timeZone]);
  const counts = {
    pendientes: data.tasks.filter((t) => t.status === "todo").length,
    vencidas: data.tasks.filter((t) => t.status === "todo" && t.date && t.date < today).length,
  };

  return (
    <SectionPage
      section="vida"
      title="Tareas"
      description={`${counts.pendientes} pendientes${counts.vencidas ? ` · ${counts.vencidas} atrasadas` : ""}`}
      actions={
        <Button onClick={() => openForm({ kind: "task" })}>
          <Plus /> Tarea completa
        </Button>
      }
    >
      <QuickCapture defaultDate={view === "sin-fecha" ? null : today} placeholder="Captura rápida: escribe y pulsa Enter (detalles después)" />

      <div className="space-y-3">
        <div className="no-scrollbar -mx-4 flex gap-1.5 overflow-x-auto px-4 sm:mx-0 sm:flex-wrap sm:px-0">
          {(Object.keys(VIEW_LABEL) as View[]).map((v) => (
            <Chip key={v} active={view === v} onClick={() => setView(v)}>
              {VIEW_LABEL[v]}
              {v === "vencidas" && counts.vencidas > 0 && <span className="text-expense tabular">{counts.vencidas}</span>}
            </Chip>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative min-w-0 flex-1 basis-56">
            <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar tareas" className="pl-9" aria-label="Buscar tareas" />
          </div>
          <Segmented
            ariaLabel="Prioridad"
            size="sm"
            value={priority}
            onChange={setPriority}
            options={[
              { value: "all", label: "Todas" },
              { value: "3", label: "Alta" },
              { value: "2", label: "Media" },
              { value: "1", label: "Baja" },
            ]}
          />
          <Segmented
            ariaLabel="Agrupar"
            size="sm"
            value={groupBy}
            onChange={setGroupBy}
            options={[
              { value: "day", label: "Por día" },
              { value: "week", label: "Por semana" },
            ]}
          />
        </div>
      </div>

      {base.length === 0 ? (
        <Card>
          <EmptyState
            icon={view === "completadas" ? <CheckCheck /> : view === "sin-fecha" ? <Inbox /> : <ListTodo />}
            title={view === "completadas" ? "Aún no completas tareas" : view === "vencidas" ? "Nada atrasado" : "No hay tareas aquí"}
            description={view === "sin-fecha" ? "Lo que captures sin fecha queda aquí hasta que decidas cuándo hacerlo." : "Usa la captura rápida de arriba: solo el título, el resto después."}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {groups.map((g) => (
            <section key={g.key}>
              <h3 className={`mb-1.5 px-1 text-[13px] font-semibold first-letter:uppercase ${g.tone === "overdue" ? "text-expense" : ""}`}>
                {g.label} <span className="font-normal text-muted-foreground tabular">· {g.tasks.length}</span>
              </h3>
              <Card className="px-1 py-1">
                {g.tasks.map((t) => (
                  <TaskItem key={t.id} task={t} showDate={groupBy === "week" || g.key === "overdue"} onPriorityToggle={() => toggle(t.id)} isPriority={priorities.includes(t.id)} />
                ))}
              </Card>
            </section>
          ))}
        </div>
      )}
    </SectionPage>
  );
}

interface Group {
  key: string;
  label: string;
  tone?: "overdue";
  tasks: Task[];
}

function groupTasks(tasks: Task[], today: DateStr, by: "day" | "week", weekStartsOn: number, completed: boolean, timeZone: string): Group[] {
  const sorted = [...tasks].sort((a, b) =>
    completed ? (b.completedAt ?? "").localeCompare(a.completedAt ?? "") : (a.date ?? "9999").localeCompare(b.date ?? "9999") || b.priority - a.priority || (a.time ?? "99").localeCompare(b.time ?? "99"),
  );
  if (completed) {
    const map = new Map<string, Task[]>();
    for (const t of sorted) {
      const d = instantToDate(t.completedAt ?? t.updatedAt, timeZone);
      const list = map.get(d);
      if (list) list.push(t);
      else map.set(d, [t]);
    }
    return [...map.entries()].map(([d, list]) => ({ key: d, label: `Completadas el ${formatDateLong(d)}`, tasks: list }));
  }
  const groups = new Map<string, Group>();
  const add = (key: string, label: string, t: Task, tone?: "overdue") => {
    const g = groups.get(key);
    if (g) g.tasks.push(t);
    else groups.set(key, { key, label, tone, tasks: [t] });
  };
  const thisWeekEnd = endOfWeek(today, weekStartsOn);
  for (const t of sorted) {
    if (!t.date) continue;
    if (t.date < today) add("overdue", "Atrasadas", t, "overdue");
    else if (by === "day") {
      const label = t.date === today ? "Hoy" : t.date === addDays(today, 1) ? "Mañana" : formatDateLong(t.date);
      add(t.date, label, t);
    } else {
      const ws = startOfWeek(t.date, weekStartsOn);
      const label = t.date <= thisWeekEnd ? "Esta semana" : ws === addDays(startOfWeek(today, weekStartsOn), 7) ? "Próxima semana" : `Semana del ${formatDateLong(ws)}`;
      add(`w-${ws}`, label, t);
    }
  }
  for (const t of sorted) if (!t.date) add("none", "Algún día (sin fecha)", t);
  return [...groups.values()];
}
