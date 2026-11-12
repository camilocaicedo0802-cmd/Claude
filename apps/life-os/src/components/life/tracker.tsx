"use client";

import * as React from "react";
import { DndContext, DragOverlay, KeyboardSensor, MouseSensor, useDraggable, useDroppable, useSensor, useSensors, type DragEndEvent } from "@dnd-kit/core";
import {
  ArrowDownUp,
  CalendarRange,
  CircleCheck,
  ClipboardPaste,
  Columns3,
  Copy,
  Filter,
  Layers,
  List,
  ListTodo,
  MoreHorizontal,
  Pencil,
  Plus,
  Repeat,
  Search,
  Settings2,
  Tags,
  Trash2,
  Users,
  X,
  CalendarClock,
} from "lucide-react";
import { useData, useToday } from "@/hooks/data";
import { useMediaQuery } from "@/hooks/use-media";
import type { Task, TaskCategory, TaskPriority } from "@/db/types";
import { categoryFor, PRIORITY_COLOR, PRIORITY_NAME, STAGE_COLOR, STAGE_LABEL, STAGES, taskStage, type TaskStage } from "@/domain/tasks";
import { endOfWeek, formatDateLong, formatDateNumeric, formatRelativeDay, startOfWeek, type DateStr } from "@/lib/dates";
import { cn, matches } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/form-controls";
import { Chip } from "@/components/ui/misc";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger, Popover, PopoverContent, PopoverTrigger } from "@/components/ui/overlays";
import { Card, DynamicIcon, EmptyState, toneStyle } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { TonePill } from "@/components/shared/tone-pill";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { createTask, deleteTask, duplicateTask, postponeTask, setTaskStage, updateTask } from "@/services/life-service";
import { ImportSheet } from "./task-import";
import { CategoriesSheet } from "./task-categories";

type View = "pending" | "week" | "board" | "done" | "all";
type SortKey = "date-desc" | "date-asc" | "priority" | "points" | "stage" | "title" | "created";
type GroupKey = "none" | "category" | "stage" | "priority" | "day";

const VIEWS: Array<{ key: View; label: string; icon: React.ReactNode }> = [
  { key: "pending", label: "Pendientes", icon: <ListTodo /> },
  { key: "week", label: "Esta semana", icon: <CalendarRange /> },
  { key: "board", label: "Tablero", icon: <Columns3 /> },
  { key: "done", label: "Completadas", icon: <CircleCheck /> },
  { key: "all", label: "Todas", icon: <List /> },
];

const SORT_LABEL: Record<SortKey, string> = {
  "date-desc": "Fecha: más reciente primero",
  "date-asc": "Fecha: más antigua primero",
  priority: "Prioridad",
  points: "Puntos",
  stage: "Estado",
  title: "Nombre",
  created: "Creación",
};

const GROUP_LABEL: Record<GroupKey, string> = {
  none: "Sin agrupar",
  category: "Categoría",
  stage: "Estado",
  priority: "Prioridad",
  day: "Día",
};

const PREFS_KEY = "lifeos:tracker";

function usePrefs() {
  const [prefs, setPrefs] = React.useState<{ view: View; sort: SortKey; group: GroupKey }>({ view: "pending", sort: "date-desc", group: "none" });
  React.useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(PREFS_KEY) ?? "null");
      if (saved) setPrefs((p) => ({ ...p, ...saved }));
    } catch {
      /* ignore */
    }
  }, []);
  const update = (patch: Partial<typeof prefs>) =>
    setPrefs((p) => {
      const next = { ...p, ...patch };
      try {
        localStorage.setItem(PREFS_KEY, JSON.stringify(next));
      } catch {
        /* ignore */
      }
      return next;
    });
  return [prefs, update] as const;
}

// ── Pills ────────────────────────────────────────────────────────────────────

function PillMenu({ label, trigger, children }: { label: string; trigger: React.ReactNode; children: React.ReactNode }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button type="button" aria-label={label} className="max-w-full rounded-md outline-none focus-visible:ring-2 focus-visible:ring-ring">
          {trigger}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-52">
        {children}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function StageMenu({ task }: { task: Task }) {
  const stage = taskStage(task);
  return (
    <PillMenu label={`Estado de «${task.title}»: ${STAGE_LABEL[stage]}`} trigger={<TonePill color={STAGE_COLOR[stage]}>{STAGE_LABEL[stage]}</TonePill>}>
      {STAGES.map((s) => (
        <DropdownMenuItem
          key={s}
          onSelect={() => s !== stage && runSave(() => setTaskStage(task.id, s), s === "done" ? (task.recurrence ? "Completada · se programó la siguiente" : "Tarea completada") : undefined)}
        >
          <TonePill color={STAGE_COLOR[s]}>{STAGE_LABEL[s]}</TonePill>
        </DropdownMenuItem>
      ))}
    </PillMenu>
  );
}

function PriorityMenu({ task }: { task: Task }) {
  return (
    <PillMenu
      label={`Prioridad de «${task.title}»: ${PRIORITY_NAME[task.priority]}`}
      trigger={task.priority ? <TonePill color={PRIORITY_COLOR[task.priority]} dot={false}>{PRIORITY_NAME[task.priority]}</TonePill> : <span className="px-1 text-xs text-subtle">Vacío</span>}
    >
      {([3, 2, 1, 0] as TaskPriority[]).map((p) => (
        <DropdownMenuItem key={p} onSelect={() => runSave(() => updateTask(task.id, { priority: p }))}>
          {p ? <TonePill color={PRIORITY_COLOR[p]} dot={false}>{PRIORITY_NAME[p]}</TonePill> : <span className="text-muted-foreground">Sin prioridad</span>}
        </DropdownMenuItem>
      ))}
    </PillMenu>
  );
}

function CategoryMenu({ task, categories, onEdit }: { task: Task; categories: TaskCategory[]; onEdit: () => void }) {
  const cat = categoryFor(task.area, categories);
  return (
    <PillMenu label={`Categoría de «${task.title}»: ${cat?.name ?? "sin categoría"}`} trigger={cat ? <TonePill color={cat.color} dot={false}>{cat.name}</TonePill> : <span className="px-1 text-xs text-subtle">Vacío</span>}>
      {categories.map((c) => (
        <DropdownMenuItem key={c.key} onSelect={() => runSave(() => updateTask(task.id, { area: c.key }))}>
          <TonePill color={c.color} dot={false}>
            {c.name}
          </TonePill>
        </DropdownMenuItem>
      ))}
      <DropdownMenuItem onSelect={() => runSave(() => updateTask(task.id, { area: null }))}>
        <span className="text-muted-foreground">Sin categoría</span>
      </DropdownMenuItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem onSelect={onEdit}>
        <Tags /> Editar categorías…
      </DropdownMenuItem>
    </PillMenu>
  );
}

function PointsInput({ task, className }: { task: Task; className?: string }) {
  const [value, setValue] = React.useState(task.points?.toString() ?? "");
  React.useEffect(() => setValue(task.points?.toString() ?? ""), [task.points]);
  const commit = () => {
    const n = value.trim() === "" ? null : Math.max(0, Math.round(Number(value)));
    if (n !== null && !Number.isFinite(n)) return setValue(task.points?.toString() ?? "");
    if (n !== (task.points ?? null)) void runSave(() => updateTask(task.id, { points: n }));
  };
  return (
    <input
      type="number"
      inputMode="numeric"
      min={0}
      aria-label={`Puntos de «${task.title}»`}
      value={value}
      placeholder="—"
      onChange={(e) => setValue(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => e.key === "Enter" && (e.target as HTMLInputElement).blur()}
      className={cn("w-full rounded-md bg-transparent px-1.5 py-1 text-right text-sm tabular outline-none placeholder:text-subtle hover:bg-accent focus:bg-card focus:ring-2 focus:ring-ring/30 [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none", className)}
    />
  );
}

function DateInput({ task, today, className, short }: { task: Task; today: DateStr; className?: string; short?: boolean }) {
  const overdue = task.status === "todo" && !!task.date && task.date < today;
  return (
    <label className={cn("relative block cursor-pointer rounded-md px-1.5 py-1 text-sm tabular hover:bg-accent focus-within:ring-2 focus-within:ring-ring/30", overdue && "font-medium text-expense", !task.date && "text-subtle", className)}>
      <span>{task.date ? (short ? formatRelativeDay(task.date, today) : formatDateNumeric(task.date)) : "Sin fecha"}</span>
      <input
        type="date"
        aria-label={`Fecha de «${task.title}»`}
        value={task.date ?? ""}
        onChange={(e) => runSave(() => updateTask(task.id, { date: e.target.value || null }))}
        className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
      />
    </label>
  );
}

function RowMenu({ task }: { task: Task }) {
  const { openForm, confirm } = useUI();
  const today = useToday();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label={`Más acciones de «${task.title}»`} className="text-muted-foreground">
          <MoreHorizontal />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-52">
        <DropdownMenuItem onSelect={() => openForm({ kind: "task", id: task.id })}>
          <Pencil /> Abrir y editar
        </DropdownMenuItem>
        {task.status === "todo" && (
          <DropdownMenuItem onSelect={() => runSave(() => postponeTask(task.id, 1, today), "Pospuesta para mañana")}>
            <CalendarClock /> Posponer a mañana
          </DropdownMenuItem>
        )}
        <DropdownMenuItem onSelect={() => runSave(() => duplicateTask(task.id), "Tarea duplicada")}>
          <Copy /> Duplicar
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          destructive
          onSelect={async () => {
            if (await confirm({ title: `¿Eliminar «${task.title}»?`, confirmLabel: "Eliminar", destructive: true })) void runSave(() => deleteTask(task.id), "Tarea eliminada");
          }}
        >
          <Trash2 /> Eliminar
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function TaskTitle({ task, categories, className }: { task: Task; categories: TaskCategory[]; className?: string }) {
  const { openForm } = useUI();
  const data = useData();
  const cat = categoryFor(task.area, categories);
  const client = task.clientId ? data.clients.find((c) => c.id === task.clientId) : undefined;
  const subDone = task.subtasks.filter((s) => s.done).length;
  return (
    <button type="button" onClick={() => openForm({ kind: "task", id: task.id })} className={cn("flex min-w-0 items-start gap-2 rounded-md text-left outline-none focus-visible:ring-2 focus-visible:ring-ring", className)}>
      <span style={toneStyle(cat?.color ?? "slate")} className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded tone-soft [&_svg]:size-3.5">
        <DynamicIcon name={task.icon ?? "list-checks"} />
      </span>
      <span className="min-w-0">
        <span className={cn("block text-sm leading-snug font-semibold", task.status === "done" && "text-muted-foreground line-through decoration-border-strong")}>{task.title}</span>
        {(client || task.recurrence || task.subtasks.length > 0) && (
          <span className="mt-0.5 flex flex-wrap items-center gap-x-2 text-xs text-muted-foreground">
            {task.recurrence && <Repeat className="size-3" aria-label="Se repite" />}
            {client && (
              <span className="inline-flex items-center gap-1">
                <Users className="size-3" /> {client.name}
              </span>
            )}
            {task.subtasks.length > 0 && (
              <span>
                {subDone}/{task.subtasks.length} subtareas
              </span>
            )}
          </span>
        )}
      </span>
    </button>
  );
}

// ── Grouping and sorting ─────────────────────────────────────────────────────

const PRIORITY_ORDER: TaskPriority[] = [3, 2, 1, 0];

function sortTasks(list: Task[], sort: SortKey): Task[] {
  const stageRank: Record<TaskStage, number> = { in_progress: 0, not_started: 1, done: 2 };
  return [...list].sort((a, b) => {
    switch (sort) {
      case "date-desc":
        return (b.date ?? "0000").localeCompare(a.date ?? "0000") || b.priority - a.priority;
      case "date-asc":
        return (a.date ?? "9999").localeCompare(b.date ?? "9999") || b.priority - a.priority;
      case "priority":
        return b.priority - a.priority || (a.date ?? "9999").localeCompare(b.date ?? "9999");
      case "points":
        return (b.points ?? -1) - (a.points ?? -1);
      case "stage":
        return stageRank[taskStage(a)] - stageRank[taskStage(b)];
      case "title":
        return a.title.localeCompare(b.title, "es");
      case "created":
        return b.createdAt.localeCompare(a.createdAt);
    }
  });
}

interface Group {
  key: string;
  label: React.ReactNode;
  tasks: Task[];
}

function groupTasks(list: Task[], group: GroupKey, categories: TaskCategory[], today: DateStr): Group[] {
  if (group === "none") return [{ key: "all", label: null, tasks: list }];
  const map = new Map<string, Group>();
  const add = (key: string, label: React.ReactNode, t: Task) => {
    const g = map.get(key);
    if (g) g.tasks.push(t);
    else map.set(key, { key, label, tasks: [t] });
  };
  for (const t of list) {
    if (group === "stage") {
      const s = taskStage(t);
      add(s, <TonePill color={STAGE_COLOR[s]}>{STAGE_LABEL[s]}</TonePill>, t);
    } else if (group === "priority") {
      add(String(t.priority), t.priority ? <TonePill color={PRIORITY_COLOR[t.priority]} dot={false}>{PRIORITY_NAME[t.priority]}</TonePill> : <span className="text-muted-foreground">Sin prioridad</span>, t);
    } else if (group === "category") {
      const c = categoryFor(t.area, categories);
      add(c?.key ?? "none", c ? <TonePill color={c.color} dot={false}>{c.name}</TonePill> : <span className="text-muted-foreground">Sin categoría</span>, t);
    } else {
      const d = t.date;
      const label = !d ? "Sin fecha" : d < today && t.status === "todo" ? "Atrasadas" : d === today ? "Hoy" : formatDateLong(d);
      add(!d ? "~none" : d < today && t.status === "todo" ? "!overdue" : d, <span className="first-letter:uppercase">{label}</span>, t);
    }
  }
  const groups = [...map.values()];
  if (group === "stage") groups.sort((a, b) => STAGES.indexOf(a.key as TaskStage) - STAGES.indexOf(b.key as TaskStage));
  if (group === "priority") groups.sort((a, b) => PRIORITY_ORDER.indexOf(Number(a.key) as TaskPriority) - PRIORITY_ORDER.indexOf(Number(b.key) as TaskPriority));
  if (group === "category") groups.sort((a, b) => categories.findIndex((c) => c.key === a.key) - categories.findIndex((c) => c.key === b.key) || (a.key === "none" ? 1 : -1));
  if (group === "day") groups.sort((a, b) => a.key.localeCompare(b.key));
  return groups;
}

const pointsOf = (list: Task[]) => list.reduce((s, t) => s + (t.points ?? 0), 0);

// ── Page ─────────────────────────────────────────────────────────────────────

export function TrackerPage() {
  const data = useData();
  const today = useToday();
  const { openForm } = useUI();
  const [prefs, setPrefs] = usePrefs();
  const [query, setQuery] = React.useState("");
  const [stages, setStages] = React.useState<TaskStage[]>([]);
  const [priorities, setPriorities] = React.useState<TaskPriority[]>([]);
  const [cats, setCats] = React.useState<string[]>([]);
  const [importOpen, setImportOpen] = React.useState(false);
  const [importText, setImportText] = React.useState("");
  const [categoriesOpen, setCategoriesOpen] = React.useState(false);
  const categories = data.settings.taskCategories;
  const { view, sort, group } = prefs;

  // Links like /vida/tareas/#importar=<texto> open the importer already filled in.
  React.useEffect(() => {
    const readHash = () => {
      const hash = window.location.hash;
      if (!hash.startsWith("#importar=")) return;
      try {
        setImportText(decodeURIComponent(hash.slice("#importar=".length)));
      } catch {
        setImportText("");
      }
      setImportOpen(true);
      window.history.replaceState(null, "", window.location.pathname);
    };
    readHash();
    window.addEventListener("hashchange", readHash);
    const v = new URLSearchParams(window.location.search).get("vista");
    if (v === "vencidas") {
      setPrefs({ view: "pending", group: "day" });
    }
    return () => window.removeEventListener("hashchange", readHash);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const weekStart = startOfWeek(today, data.settings.weekStartsOn);
  const weekEnd = endOfWeek(today, data.settings.weekStartsOn);
  const base = data.tasks.filter((t) => {
    if (view === "pending" || view === "board") return view === "board" ? true : t.status === "todo";
    if (view === "done") return t.status === "done";
    if (view === "week") return !!t.date && t.date >= weekStart && t.date <= weekEnd;
    return true;
  });
  const filtered = base
    .filter((t) => stages.length === 0 || stages.includes(taskStage(t)))
    .filter((t) => priorities.length === 0 || priorities.includes(t.priority))
    .filter((t) => cats.length === 0 || cats.includes(t.area ?? "none"))
    .filter((t) => matches([t.title, t.description, t.notes, categoryFor(t.area, categories)?.name], query));
  const effectiveSort: SortKey = view === "done" && sort === "date-desc" ? "date-desc" : sort;
  const sorted = sortTasks(filtered, effectiveSort);
  const effectiveGroup: GroupKey = view === "week" && group === "none" ? "day" : group;
  const groups = groupTasks(sorted, effectiveGroup, categories, today);
  const activeFilters = stages.length + priorities.length + cats.length;
  const pending = data.tasks.filter((t) => t.status === "todo");
  const defaultsForNew = (): Partial<Task> => ({
    date: today,
    area: cats.length === 1 && cats[0] !== "none" ? cats[0] : null,
    priority: priorities.length === 1 ? priorities[0] : 0,
  });

  return (
    <SectionPage
      section="vida"
      title="Tareas"
      description={`${pending.length} pendientes · ${pointsOf(pending)} puntos${pending.filter((t) => t.date && t.date < today).length ? ` · ${pending.filter((t) => t.date && t.date < today).length} atrasadas` : ""}`}
      actions={
        <>
          <Button variant="outline" onClick={() => setImportOpen(true)}>
            <ClipboardPaste /> Importar
          </Button>
          <Button onClick={() => openForm({ kind: "task", defaults: defaultsForNew() })}>
            <Plus /> Nueva tarea
          </Button>
        </>
      }
    >
      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center gap-2 border-b border-border px-2 py-2 sm:px-3">
          <div role="tablist" aria-label="Vistas" className="no-scrollbar -mx-2 flex min-w-0 flex-1 basis-full gap-1 overflow-x-auto px-2 sm:mx-0 sm:basis-auto sm:px-0">
            {VIEWS.map((v) => (
              <button
                key={v.key}
                type="button"
                role="tab"
                aria-selected={view === v.key}
                onClick={() => setPrefs({ view: v.key })}
                className={cn(
                  "inline-flex h-8 shrink-0 items-center gap-1.5 rounded-lg px-2.5 text-[13px] font-medium whitespace-nowrap text-muted-foreground transition-colors hover:bg-accent hover:text-foreground [&_svg]:size-3.5",
                  view === v.key && "bg-secondary text-foreground",
                )}
              >
                {v.icon}
                {v.label}
              </button>
            ))}
          </div>
          <div className="flex w-full items-center gap-1 sm:w-auto">
            <div className="relative min-w-0 flex-1 sm:w-44 sm:flex-none">
              <Search className="pointer-events-none absolute top-1/2 left-2.5 size-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar" aria-label="Buscar tareas" className="h-8 pl-8 text-[13px] sm:h-8" />
            </div>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant={activeFilters ? "secondary" : "ghost"} size="sm" aria-label="Filtrar" className={cn("h-8 px-2.5", activeFilters && "text-brand")}>
                  <Filter /> <span className="max-sm:hidden">Filtrar</span>
                  {activeFilters > 0 && <span className="tabular">{activeFilters}</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-[min(92vw,340px)] space-y-3">
                <FilterGroup label="Estado">
                  {STAGES.map((s) => (
                    <Chip key={s} active={stages.includes(s)} onClick={() => setStages((l) => (l.includes(s) ? l.filter((x) => x !== s) : [...l, s]))}>
                      {STAGE_LABEL[s]}
                    </Chip>
                  ))}
                </FilterGroup>
                <FilterGroup label="Prioridad">
                  {PRIORITY_ORDER.map((p) => (
                    <Chip key={p} active={priorities.includes(p)} onClick={() => setPriorities((l) => (l.includes(p) ? l.filter((x) => x !== p) : [...l, p]))}>
                      {PRIORITY_NAME[p]}
                    </Chip>
                  ))}
                </FilterGroup>
                <FilterGroup label="Categoría">
                  {[...categories, { key: "none", name: "Sin categoría", color: "slate" }].map((c) => (
                    <Chip key={c.key} active={cats.includes(c.key)} onClick={() => setCats((l) => (l.includes(c.key) ? l.filter((x) => x !== c.key) : [...l, c.key]))}>
                      {c.name}
                    </Chip>
                  ))}
                </FilterGroup>
                {activeFilters > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setStages([]);
                      setPriorities([]);
                      setCats([]);
                    }}
                  >
                    <X /> Quitar filtros
                  </Button>
                )}
              </PopoverContent>
            </Popover>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" aria-label="Ordenar y agrupar" className="h-8 px-2.5">
                  <ArrowDownUp /> <span className="max-sm:hidden">Ordenar</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-60">
                <DropdownMenuLabel>Ordenar por</DropdownMenuLabel>
                {(Object.keys(SORT_LABEL) as SortKey[]).map((k) => (
                  <DropdownMenuItem key={k} onSelect={() => setPrefs({ sort: k })} className={cn(sort === k && "font-semibold text-foreground")}>
                    {SORT_LABEL[k]}
                  </DropdownMenuItem>
                ))}
                <DropdownMenuSeparator />
                <DropdownMenuLabel className="flex items-center gap-1.5">
                  <Layers className="size-3" /> Agrupar por
                </DropdownMenuLabel>
                {(Object.keys(GROUP_LABEL) as GroupKey[]).map((k) => (
                  <DropdownMenuItem key={k} onSelect={() => setPrefs({ group: k })} className={cn(group === k && "font-semibold text-foreground")}>
                    {GROUP_LABEL[k]}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <Button variant="ghost" size="icon-sm" aria-label="Editar categorías" onClick={() => setCategoriesOpen(true)}>
              <Settings2 />
            </Button>
          </div>
        </div>

        {data.tasks.length === 0 ? (
          <EmptyState
            icon={<ListTodo />}
            title="Tu tracker está vacío"
            description="Crea tu primera tarea o pega una lista desde Notion, Excel o Google Sheets con «Importar»."
            action={
              <>
                <Button onClick={() => openForm({ kind: "task", defaults: defaultsForNew() })}>
                  <Plus /> Nueva tarea
                </Button>
                <Button variant="outline" onClick={() => setImportOpen(true)}>
                  <ClipboardPaste /> Importar
                </Button>
              </>
            }
          />
        ) : view === "board" ? (
          <Board tasks={sorted} categories={categories} onEditCategories={() => setCategoriesOpen(true)} />
        ) : (
          <TrackerTable groups={groups} grouped={effectiveGroup !== "none"} categories={categories} onEditCategories={() => setCategoriesOpen(true)} newDefaults={defaultsForNew()} empty={sorted.length === 0} total={sorted} />
        )}
      </Card>

      {importOpen && <ImportSheet initialText={importText} onClose={() => { setImportOpen(false); setImportText(""); }} />}
      {categoriesOpen && <CategoriesSheet onClose={() => setCategoriesOpen(false)} />}
    </SectionPage>
  );
}

function FilterGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-medium text-muted-foreground">{label}</p>
      <div className="flex flex-wrap gap-1.5">{children}</div>
    </div>
  );
}

// ── Table (desktop) and cards (phone) ────────────────────────────────────────

function NewRow({ defaults }: { defaults: Partial<Task> }) {
  const [title, setTitle] = React.useState("");
  const ref = React.useRef<HTMLInputElement>(null);
  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        if (!title.trim()) return;
        if (await runSave(() => createTask({ ...defaults, title }), "Tarea creada")) {
          setTitle("");
          ref.current?.focus();
        }
      }}
      className="flex items-center gap-2 px-3 py-2 text-muted-foreground"
    >
      <Plus className="size-4 shrink-0" aria-hidden />
      <input
        ref={ref}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Nueva tarea (Enter para crear)"
        aria-label="Nueva tarea"
        className="h-8 min-w-0 flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-subtle"
      />
      {title.trim() && (
        <Button type="submit" size="sm">
          Crear
        </Button>
      )}
    </form>
  );
}

function TrackerTable({
  groups,
  grouped,
  categories,
  onEditCategories,
  newDefaults,
  empty,
  total,
}: {
  groups: Group[];
  grouped: boolean;
  categories: TaskCategory[];
  onEditCategories: () => void;
  newDefaults: Partial<Task>;
  empty: boolean;
  total: Task[];
}) {
  const today = useToday();
  const wide = useMediaQuery("(min-width: 768px)", true);
  if (empty) {
    return (
      <>
        <p className="px-4 py-8 text-center text-[13px] text-muted-foreground">Ninguna tarea coincide con esta vista o filtros.</p>
        <div className="border-t border-border">
          <NewRow defaults={newDefaults} />
        </div>
      </>
    );
  }
  if (!wide) {
    return (
      <div>
        {groups.map((g) => (
          <section key={g.key}>
            {grouped && (
              <div className="flex items-center gap-2 border-b border-border bg-muted/40 px-3 py-2 text-xs">
                {g.label}
                <span className="text-muted-foreground tabular">
                  {g.tasks.length} · {pointsOf(g.tasks)} pts
                </span>
              </div>
            )}
            <ul className="divide-y divide-border">
              {g.tasks.map((t) => (
                <li key={t.id} className="px-3 py-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <TaskTitle task={t} categories={categories} className="flex-1 pt-1" />
                    <RowMenu task={t} />
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-x-1.5 gap-y-1.5 pl-7">
                    <StageMenu task={t} />
                    <PriorityMenu task={t} />
                    <CategoryMenu task={t} categories={categories} onEdit={onEditCategories} />
                    <span className="ml-auto inline-flex items-center gap-1 text-xs whitespace-nowrap text-muted-foreground">
                      <DateInput task={t} today={today} short className="px-1 py-0.5 text-xs" />
                      <span aria-hidden>·</span>
                      <PointsInput task={t} className="w-6 px-0.5 py-0.5 text-xs" />
                      pts
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))}
        <div className="border-t border-border">
          <NewRow defaults={newDefaults} />
        </div>
        <TableFooter tasks={total} />
      </div>
    );
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] table-fixed text-sm">
        <colgroup>
          <col className="w-[132px]" />
          <col />
          <col className="w-[104px]" />
          <col className="w-[168px]" />
          <col className="w-[84px]" />
          <col className="w-[124px]" />
          <col className="w-[44px]" />
        </colgroup>
        <thead>
          <tr className="border-b border-border text-left text-xs text-muted-foreground">
            <th className="px-3 py-2 font-medium">Estado</th>
            <th className="px-3 py-2 font-medium">Tarea</th>
            <th className="px-3 py-2 font-medium">Prioridad</th>
            <th className="px-3 py-2 font-medium">Categoría</th>
            <th className="px-3 py-2 text-right font-medium">Puntos</th>
            <th className="px-3 py-2 font-medium">Fecha</th>
            <th aria-label="Acciones" />
          </tr>
        </thead>
        {groups.map((g) => (
          <tbody key={g.key} className="divide-y divide-border border-b border-border">
            {grouped && (
              <tr className="bg-muted/40">
                <td colSpan={7} className="px-3 py-2 text-xs">
                  <span className="inline-flex items-center gap-2">
                    {g.label}
                    <span className="text-muted-foreground tabular">
                      {g.tasks.length} {g.tasks.length === 1 ? "tarea" : "tareas"} · {pointsOf(g.tasks)} pts
                    </span>
                  </span>
                </td>
              </tr>
            )}
            {g.tasks.map((t) => (
              <tr key={t.id} className="group align-top transition-colors hover:bg-accent/40">
                <td className="px-3 py-2.5">
                  <StageMenu task={t} />
                </td>
                <td className="px-3 py-2">
                  <TaskTitle task={t} categories={categories} />
                </td>
                <td className="px-3 py-2.5">
                  <PriorityMenu task={t} />
                </td>
                <td className="px-3 py-2.5">
                  <CategoryMenu task={t} categories={categories} onEdit={onEditCategories} />
                </td>
                <td className="px-1.5 py-1.5">
                  <PointsInput task={t} />
                </td>
                <td className="px-1.5 py-1.5">
                  <DateInput task={t} today={today} />
                </td>
                <td className="px-1 py-1.5 text-right">
                  <span className="opacity-100 lg:opacity-0 lg:group-hover:opacity-100 lg:focus-within:opacity-100">
                    <RowMenu task={t} />
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        ))}
      </table>
      <NewRow defaults={newDefaults} />
      <TableFooter tasks={total} />
    </div>
  );
}

function TableFooter({ tasks }: { tasks: Task[] }) {
  const done = tasks.filter((t) => t.status === "done");
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
      <span className="tabular">
        {tasks.length} {tasks.length === 1 ? "tarea" : "tareas"} · {pointsOf(tasks)} puntos
      </span>
      {done.length > 0 && done.length < tasks.length && (
        <span className="tabular">
          Completado: {pointsOf(done)} de {pointsOf(tasks)} pts
        </span>
      )}
    </div>
  );
}

// ── Board ────────────────────────────────────────────────────────────────────

function BoardCard({ task, categories, coarse, onEditCategories }: { task: Task; categories: TaskCategory[]; coarse: boolean; onEditCategories: () => void }) {
  const today = useToday();
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({ id: task.id, disabled: coarse });
  return (
    <div ref={setNodeRef} className={cn("space-y-2 rounded-lg border border-border bg-card p-3 shadow-[var(--shadow-card)]", isDragging && "opacity-30")} {...(coarse ? {} : listeners)} {...(coarse ? {} : attributes)}>
      <div className="flex items-start justify-between gap-1">
        <TaskTitle task={task} categories={categories} className="flex-1" />
        <RowMenu task={task} />
      </div>
      <div className="flex flex-wrap items-center gap-1.5">
        {coarse && <StageMenu task={task} />}
        <PriorityMenu task={task} />
        <CategoryMenu task={task} categories={categories} onEdit={onEditCategories} />
      </div>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className={cn("tabular", task.status === "todo" && task.date && task.date < today && "font-medium text-expense")}>{task.date ? formatRelativeDay(task.date, today) : "Sin fecha"}</span>
        {task.points != null && <span className="tabular">{task.points} pts</span>}
      </div>
    </div>
  );
}

function BoardColumn({ stage, tasks, children }: { stage: TaskStage; tasks: Task[]; children: React.ReactNode }) {
  const { setNodeRef, isOver } = useDroppable({ id: stage });
  return (
    <section ref={setNodeRef} aria-label={STAGE_LABEL[stage]} className={cn("flex w-[280px] shrink-0 snap-start flex-col rounded-xl bg-muted/50 p-2 transition-colors sm:w-auto sm:min-w-0 sm:flex-1", isOver && "bg-brand-soft ring-2 ring-brand/40")}>
      <header className="flex items-center justify-between px-1.5 pt-1 pb-2">
        <TonePill color={STAGE_COLOR[stage]}>{STAGE_LABEL[stage]}</TonePill>
        <span className="text-xs text-muted-foreground tabular">
          {tasks.length} · {pointsOf(tasks)} pts
        </span>
      </header>
      <div className="flex min-h-24 flex-col gap-2">{children}</div>
    </section>
  );
}

function Board({ tasks, categories, onEditCategories }: { tasks: Task[]; categories: TaskCategory[]; onEditCategories: () => void }) {
  const coarse = useMediaQuery("(pointer: coarse)");
  const sensors = useSensors(useSensor(MouseSensor, { activationConstraint: { distance: 6 } }), useSensor(KeyboardSensor));
  const [active, setActive] = React.useState<Task | null>(null);
  const byStage = (s: TaskStage) => {
    const list = tasks.filter((t) => taskStage(t) === s);
    return s === "done" ? list.sort((a, b) => (b.completedAt ?? "").localeCompare(a.completedAt ?? "")).slice(0, 20) : list;
  };
  const onEnd = (e: DragEndEvent) => {
    setActive(null);
    const stage = e.over?.id as TaskStage | undefined;
    const task = tasks.find((t) => t.id === e.active.id);
    if (stage && task && taskStage(task) !== stage) void runSave(() => setTaskStage(task.id, stage), `Movida a ${STAGE_LABEL[stage]}`);
  };
  return (
    <DndContext sensors={sensors} onDragStart={(e) => setActive(tasks.find((t) => t.id === e.active.id) ?? null)} onDragEnd={onEnd} onDragCancel={() => setActive(null)}>
      <div className="flex snap-x gap-3 overflow-x-auto p-3">
        {STAGES.map((s) => {
          const list = byStage(s);
          return (
            <BoardColumn key={s} stage={s} tasks={list}>
              {list.map((t) => (
                <BoardCard key={t.id} task={t} categories={categories} coarse={coarse} onEditCategories={onEditCategories} />
              ))}
              {list.length === 0 && <p className="rounded-lg border border-dashed border-border-strong/60 p-3 text-center text-xs text-subtle">{coarse ? "Vacío" : "Arrastra tareas aquí"}</p>}
            </BoardColumn>
          );
        })}
      </div>
      <DragOverlay dropAnimation={{ duration: 180, easing: "cubic-bezier(0.22,1,0.36,1)" }}>
        {active ? (
          <div className="rotate-[1.5deg] rounded-lg border border-border bg-card p-3 shadow-pop">
            <TaskTitle task={active} categories={categories} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
