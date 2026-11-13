"use client";

import * as React from "react";
import Link from "next/link";
import { DndContext, DragOverlay, MouseSensor, useDraggable, useDroppable, useSensor, useSensors, type DragEndEvent, type DragStartEvent } from "@dnd-kit/core";
import {
  ArrowRight,
  CalendarCheck,
  CalendarPlus,
  Check,
  ChevronLeft,
  ChevronRight,
  Clock,
  GripVertical,
  LayoutTemplate,
  Lightbulb,
  ListTodo,
  Moon,
  MoreHorizontal,
  Pencil,
  Play,
  Sparkles,
  Timer,
  Trash2,
  Wand2,
} from "lucide-react";
import { toast } from "sonner";
import { useData, useNow } from "@/hooks/data";
import { useIsDesktop } from "@/hooks/use-media";
import type { CalendarEvent, DayTemplateBlock, EventCategory, Task } from "@/db/types";
import { SUGGESTED_TEMPLATE } from "@/db/defaults";
import { categoryFor, PRIORITY_COLOR, PRIORITY_NAME } from "@/domain/tasks";
import { EVENT_CATEGORY_LABEL } from "@/domain/agenda";
import {
  autoPlan,
  dayCapacity,
  dayItems,
  freeSlots,
  mergeIntervals,
  nowAndNext,
  planCandidates,
  snap,
  taskMinutes,
  toTime,
  type AutoPlanResult,
  type PlanItem,
} from "@/domain/planner";
import { addDays, formatDateLong, formatDuration, formatRelativeDay, formatTime, instantToDate, timeToMinutes, type DateStr } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Field, Input, NativeSelect } from "@/components/ui/form-controls";
import { Chip, Progress, Segmented } from "@/components/ui/misc";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger, Sheet } from "@/components/ui/overlays";
import { Card, CardHeader, DynamicIcon, EmptyState, toneStyle } from "@/components/shared/primitives";
import { TonePill } from "@/components/shared/tone-pill";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { deleteEvent, setTaskDone } from "@/services/life-service";
import {
  applyDayTemplate,
  applyPlan,
  clearDayBlocks,
  createBlock,
  deleteDayTemplate,
  moveEventTime,
  moveTasksTo,
  resizeEvent,
  restoreTasks,
  saveDayTemplate,
  scheduleTask,
  unscheduleTask,
} from "@/services/planner-service";
import { useFocus } from "./focus";

const BLOCK_PRESETS: Array<{ title: string; category: EventCategory; minutes: number }> = [
  { title: "Trabajo profundo", category: "trabajo", minutes: 90 },
  { title: "Correos y mensajes", category: "trabajo", minutes: 30 },
  { title: "Reunión", category: "clientes", minutes: 60 },
  { title: "Almuerzo", category: "personal", minutes: 60 },
  { title: "Descanso", category: "personal", minutes: 15 },
  { title: "Ejercicio", category: "salud", minutes: 60 },
  { title: "Estudio", category: "estudio", minutes: 60 },
  { title: "Desplazamiento", category: "otro", minutes: 30 },
];

const DURATIONS = [15, 30, 45, 60, 90, 120, 180];

function usePlannerData(date: DateStr) {
  const data = useData();
  const cats = data.settings.taskCategories;
  const planner = data.settings.planner;
  const colorOf = React.useCallback((key?: string | null) => categoryFor(key, cats)?.color ?? "slate", [cats]);
  const items = React.useMemo(() => dayItems(date, data.tasks, data.events, planner, colorOf), [date, data.tasks, data.events, planner, colorOf]);
  return { data, planner, items, colorOf };
}

// ── Page ─────────────────────────────────────────────────────────────────────

export function PlannerPage() {
  const now = useNow();
  const today = now.date;
  const desktop = useIsDesktop();
  const [date, setDate] = React.useState<DateStr>(today);
  React.useEffect(() => {
    const d = new URLSearchParams(window.location.search).get("fecha");
    if (d && /^\d{4}-\d{2}-\d{2}$/.test(d)) setDate(d);
  }, []);
  const { data, planner, items, colorOf } = usePlannerData(date);
  const focus = useFocus();
  const isToday = date === today;
  const nowMin = timeToMinutes(now.time);
  const candidates = planCandidates(data.tasks, date, today);
  const someday = data.tasks.filter((t) => t.status === "todo" && !t.date);
  const capacity = dayCapacity(items, planner);
  const pendingMin = candidates.reduce((s, t) => s + taskMinutes(t, planner), 0);
  const focusToday = data.focusSessions.filter((s) => s.date === date).reduce((s, x) => s + x.minutes, 0);
  const { now: current, next } = isToday ? nowAndNext(items, nowMin) : { now: null, next: null };
  const [slot, setSlot] = React.useState<{ start: number; task?: Task } | null>(null);
  const [plan, setPlan] = React.useState<AutoPlanResult | null>(null);
  const [templatesOpen, setTemplatesOpen] = React.useState(false);
  const [closeOpen, setCloseOpen] = React.useState(false);
  const [mobileTab, setMobileTab] = React.useState<"horario" | "pendientes">("horario");

  const busy = items.filter((i) => !i.done).map((i) => ({ start: i.start, end: i.end }));
  const runAutoPlan = () => {
    const r = autoPlan({ date, candidates, busy, settings: planner, nowMin: isToday ? nowMin : null });
    if (r.placed.length === 0 && r.unplaced.length === 0) return toast.info("No hay tareas pendientes para ubicar en este día.");
    setPlan(r);
  };

  const suggestions = React.useMemo(() => {
    const out: string[] = [];
    const focusStart = timeToMinutes(planner.focusStart);
    const focusEnd = timeToMinutes(planner.focusEnd);
    const freeFocus = freeSlots(busy, isToday ? Math.max(focusStart, nowMin) : focusStart, focusEnd, 30).reduce((s, x) => s + x.end - x.start, 0);
    const topTask = [...candidates].sort((a, b) => b.priority - a.priority)[0];
    if (freeFocus >= 60 && topTask && topTask.priority >= 2) {
      out.push(`Tu horario de máxima energía (${formatTime(planner.focusStart)}–${formatTime(planner.focusEnd)}) tiene ${formatDuration(freeFocus)} libres: úsalo para «${topTask.title}».`);
    }
    if (pendingMin > capacity.free && candidates.length) {
      out.push(`Tienes ${formatDuration(pendingMin)} de tareas por ubicar y solo ${formatDuration(capacity.free)} libres: decide qué pasa a otro día.`);
    }
    // Breaks (descanso, almuerzo, pausa…) count as rest, not as work.
    const isRest = (title: string) => /descanso|almuerzo|pausa|comida|siesta|break/i.test(title);
    const work = items.filter((i) => !i.done && !isRest(i.title));
    const blocks = mergeIntervals(work.map((b) => ({ start: b.start, end: b.end + 10 })));
    const marathon = blocks.find((b) => b.end - 10 - b.start > 180);
    if (marathon) out.push(`Tienes más de 3 horas seguidas sin pausa entre ${formatTime(toTime(marathon.start))} y ${formatTime(toTime(marathon.end - 10))}: agrega un descanso corto.`);
    const sorted = [...items].filter((i) => !i.done).sort((a, b) => a.start - b.start);
    const overlap = sorted.find((it, idx) => idx > 0 && it.start < sorted[idx - 1].end);
    if (overlap) out.push(`«${overlap.title}» se cruza con otro bloque a las ${formatTime(toTime(overlap.start))}.`);
    if (isToday && items.length === 0) out.push("Aún no has planificado el día: usa «Auto-planificar» o aplica una plantilla.");
    return out.slice(0, 3);
  }, [busy, candidates, capacity.free, isToday, items, nowMin, pendingMin, planner]);

  return (
    <SectionPage
      section="vida"
      title="Planificador"
      description="Arma el cronograma del día con tus tareas, eventos y bloques de tiempo."
      actions={
        <>
          <Button variant="outline" onClick={() => setTemplatesOpen(true)}>
            <LayoutTemplate /> Plantillas
          </Button>
          <Button onClick={runAutoPlan}>
            <Wand2 /> Auto-planificar
          </Button>
        </>
      }
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1">
          <Button variant={isToday ? "secondary" : "outline"} size="sm" onClick={() => setDate(today)}>
            Hoy
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Día anterior" onClick={() => setDate(addDays(date, -1))}>
            <ChevronLeft />
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Día siguiente" onClick={() => setDate(addDays(date, 1))}>
            <ChevronRight />
          </Button>
          <h2 className="ml-1 text-sm font-semibold first-letter:uppercase sm:text-[15px]">{isToday ? `Hoy, ${formatDateLong(date)}` : formatDateLong(date)}</h2>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={() => focus.start({ title: "Enfoque libre" })} disabled={!!focus.state}>
            <Timer /> Enfoque libre
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setCloseOpen(true)}>
            <Moon /> Cerrar el día
          </Button>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="p-4 xl:col-span-2">
          {isToday ? (
            <div className="flex items-start gap-3">
              <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
                <Clock className="size-4" />
              </span>
              <div className="min-w-0 flex-1">
                {current ? (
                  <>
                    <p className="text-xs font-medium text-muted-foreground">Ahora · hasta {formatTime(toTime(current.end))}</p>
                    <p className="truncate text-[15px] font-semibold">{current.title}</p>
                    <Progress className="mt-2" value={((nowMin - current.start) / Math.max(1, current.end - current.start)) * 100} label="Avance del bloque actual" />
                  </>
                ) : (
                  <>
                    <p className="text-xs font-medium text-muted-foreground">Ahora</p>
                    <p className="text-[15px] font-semibold">Tiempo libre</p>
                  </>
                )}
                <p className="mt-2 truncate text-[13px] text-muted-foreground">
                  {next ? `Siguiente: ${next.title} a las ${formatTime(toTime(next.start))}` : "No hay nada más programado hoy."}
                </p>
              </div>
              {current && !focus.state && (
                <Button size="sm" variant="outline" onClick={() => focus.start({ title: current.title, taskId: current.kind === "task" ? current.id : null, minutes: Math.min(planner.pomodoroMin, Math.max(5, current.end - nowMin)) })}>
                  <Play /> Enfoque
                </Button>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <span className="flex size-9 items-center justify-center rounded-lg bg-secondary text-muted-foreground">
                <CalendarCheck className="size-4" />
              </span>
              <div>
                <p className="text-[15px] font-semibold">{formatRelativeDay(date, today)}</p>
                <p className="text-[13px] text-muted-foreground">{items.length ? `${items.length} elementos programados` : "Nada programado todavía"}</p>
              </div>
            </div>
          )}
        </Card>
        <Card className="p-4">
          <p className="text-xs font-medium text-muted-foreground">Planificado</p>
          <p className={cn("mt-1 text-lg font-semibold tabular", capacity.overbooked && "text-expense")}>
            {formatDuration(capacity.planned)} <span className="text-xs font-normal text-muted-foreground">de {formatDuration(capacity.window)}</span>
          </p>
          <Progress className="mt-2" value={(capacity.planned / Math.max(1, capacity.window)) * 100} tone={capacity.overbooked ? "expense" : capacity.planned / capacity.window > 0.85 ? "warning" : "brand"} label="Tiempo planificado del día" />
          <p className="mt-1.5 text-xs text-muted-foreground">
            {formatDuration(capacity.free)} libres · {formatTime(planner.dayStart)}–{formatTime(planner.dayEnd)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs font-medium text-muted-foreground">Por ubicar · Enfoque</p>
          <p className="mt-1 text-lg font-semibold tabular">
            {candidates.length} <span className="text-xs font-normal text-muted-foreground">tareas · {formatDuration(pendingMin)}</span>
          </p>
          <p className="mt-2 text-xs text-muted-foreground tabular">
            <Timer className="mr-1 inline size-3" />
            {formatDuration(focusToday)} de enfoque {isToday ? "hoy" : "ese día"}
          </p>
        </Card>
      </div>

      {suggestions.length > 0 && (
        <ul className="space-y-1.5">
          {suggestions.map((s) => (
            <li key={s} className="flex items-start gap-2 rounded-lg bg-warning-soft/60 px-3 py-2 text-[13px] text-warning">
              <Lightbulb className="mt-0.5 size-3.5 shrink-0" /> {s}
            </li>
          ))}
        </ul>
      )}

      {desktop ? (
        <DesktopPlanner date={date} items={items} candidates={candidates} someday={someday} nowMin={isToday ? nowMin : null} onSlot={(start, task) => setSlot({ start, task })} colorOf={colorOf} />
      ) : (
        <div className="space-y-3">
          <Segmented
            className="w-full"
            value={mobileTab}
            onChange={setMobileTab}
            options={[
              { value: "horario", label: "Cronograma" },
              { value: "pendientes", label: `Por planificar (${candidates.length})` },
            ]}
          />
          {mobileTab === "horario" ? (
            <MobileSchedule date={date} items={items} nowMin={isToday ? nowMin : null} onSlot={(start) => setSlot({ start })} />
          ) : (
            <Card>
              <CandidateList candidates={candidates} someday={someday} onSchedule={(t) => setSlot({ start: firstFit(t, busy, planner, isToday ? nowMin : null), task: t })} />
            </Card>
          )}
        </div>
      )}

      {slot && <SlotSheet date={date} start={slot.start} task={slot.task} candidates={candidates} onClose={() => setSlot(null)} />}
      {plan && <AutoPlanSheet date={date} plan={plan} onClose={() => setPlan(null)} />}
      {templatesOpen && <TemplatesSheet date={date} items={items} onClose={() => setTemplatesOpen(false)} />}
      {closeOpen && <CloseDaySheet date={date} onClose={() => setCloseOpen(false)} onPlanTomorrow={() => setDate(addDays(date, 1))} />}
    </SectionPage>
  );
}

function firstFit(task: Task, busy: Array<{ start: number; end: number }>, planner: { dayStart: string; dayEnd: string; bufferMin: number; defaultTaskMin: number }, nowMin: number | null) {
  const from = Math.max(timeToMinutes(planner.dayStart), nowMin === null ? 0 : snap(nowMin + 7, 15));
  const padded = busy.map((b) => ({ start: b.start - planner.bufferMin, end: b.end + planner.bufferMin }));
  const slotFound = freeSlots(padded, from, timeToMinutes(planner.dayEnd), 5).find((s) => s.end - s.start >= taskMinutes(task, planner));
  return slotFound ? snap(slotFound.start, 5) : from;
}

// ── Item actions ─────────────────────────────────────────────────────────────

function ItemMenu({ item, date }: { item: PlanItem; date: DateStr }) {
  const { openForm, confirm } = useUI();
  const focus = useFocus();
  const length = item.end - item.start;
  const setLength = (m: number) =>
    item.kind === "task" ? runSave(() => scheduleTask(item.id, date, toTime(item.start), m)) : runSave(() => resizeEvent(item.id, m));
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label={`Acciones de «${item.title}»`} className="size-7 shrink-0">
          <MoreHorizontal />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        {!focus.state && (
          <DropdownMenuItem onSelect={() => focus.start({ title: item.title, taskId: item.kind === "task" ? item.id : null })}>
            <Play /> Iniciar enfoque
          </DropdownMenuItem>
        )}
        {item.kind === "task" && (
          <DropdownMenuItem onSelect={() => runSave(() => setTaskDone(item.id, !item.done), item.done ? undefined : "Tarea completada")}>
            <Check /> {item.done ? "Marcar pendiente" : "Completar"}
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuLabel>Duración ({formatDuration(length)})</DropdownMenuLabel>
        <div className="flex flex-wrap gap-1 px-2 pb-2">
          {[15, 30, 45, 60, 90, 120].map((m) => (
            <button key={m} type="button" onClick={() => setLength(m)} className={cn("rounded-md border px-2 py-1 text-xs", m === length ? "border-foreground bg-foreground text-background" : "border-border hover:bg-accent")}>
              {m < 60 ? `${m}m` : `${m / 60}h`}
            </button>
          ))}
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={() => (item.kind === "task" ? openForm({ kind: "task", id: item.id }) : openForm({ kind: "event", id: item.id, occurrence: date }))}>
          <Pencil /> Editar
        </DropdownMenuItem>
        {item.kind === "task" ? (
          <>
            <DropdownMenuItem onSelect={() => runSave(() => unscheduleTask(item.id), "Quitada del cronograma")}>
              <ListTodo /> Quitar del cronograma
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => runSave(() => moveTasksTo([item.id], addDays(date, 1)), "Movida a mañana")}>
              <CalendarPlus /> Mover a mañana
            </DropdownMenuItem>
          </>
        ) : (
          <DropdownMenuItem
            destructive
            onSelect={async () => {
              if (await confirm({ title: `¿Eliminar «${item.title}»${item.recurring ? " solo de este día" : ""}?`, confirmLabel: "Eliminar", destructive: true }))
                void runSave(() => deleteEvent(item.id, item.recurring ? date : undefined), "Eliminado del cronograma");
            }}
          >
            <Trash2 /> Eliminar
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function KindIcon({ item }: { item: PlanItem }) {
  if (item.kind === "task") return <ListTodo className="size-3" aria-label="Tarea" />;
  if (item.kind === "block") return <Timer className="size-3" aria-label="Bloque" />;
  return <CalendarCheck className="size-3" aria-label="Evento" />;
}

// ── Desktop: draggable timeline ──────────────────────────────────────────────

const PX_PER_MIN = 1.1;

function DesktopPlanner({
  date,
  items,
  candidates,
  someday,
  nowMin,
  onSlot,
  colorOf,
}: {
  date: DateStr;
  items: PlanItem[];
  candidates: Task[];
  someday: Task[];
  nowMin: number | null;
  onSlot: (start: number, task?: Task) => void;
  colorOf: (k?: string | null) => string;
}) {
  const data = useData();
  const planner = data.settings.planner;
  const sensors = useSensors(useSensor(MouseSensor, { activationConstraint: { distance: 6 } }));
  const columnRef = React.useRef<HTMLDivElement>(null);
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = React.useState<{ title: string } | null>(null);
  const first = Math.min(timeToMinutes(planner.dayStart), ...items.map((i) => i.start));
  const last = Math.max(timeToMinutes(planner.dayEnd), ...items.map((i) => i.end));
  const rangeStart = Math.max(0, Math.floor(first / 60) * 60);
  const rangeEnd = Math.min(24 * 60, Math.ceil(last / 60) * 60);
  const hours = Array.from({ length: (rangeEnd - rangeStart) / 60 }, (_, i) => rangeStart / 60 + i);
  const lanes = layoutLanes(items);
  const focusStart = timeToMinutes(planner.focusStart);
  const focusEnd = timeToMinutes(planner.focusEnd);

  React.useEffect(() => {
    const target = nowMin ?? timeToMinutes(planner.dayStart);
    scrollRef.current?.scrollTo({ top: Math.max(0, (target - rangeStart - 60) * PX_PER_MIN) });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [date]);

  const minutesAtY = (clientY: number) => {
    const rect = columnRef.current!.getBoundingClientRect();
    return Math.max(rangeStart, Math.min(rangeEnd - 15, snap(rangeStart + (clientY - rect.top) / PX_PER_MIN, 15)));
  };

  const onStart = (e: DragStartEvent) => {
    const d = e.active.data.current as { title: string } | undefined;
    setDragging(d ? { title: d.title } : null);
  };
  const onEnd = (e: DragEndEvent) => {
    setDragging(null);
    const payload = e.active.data.current as { type: "candidate"; task: Task } | { type: "item"; item: PlanItem } | undefined;
    if (!payload || e.over?.id !== "timeline") return;
    if (payload.type === "candidate") {
      const pointer = (e.activatorEvent as PointerEvent).clientY + e.delta.y;
      const start = minutesAtY(pointer);
      void runSave(() => scheduleTask(payload.task.id, date, toTime(start), taskMinutes(payload.task, planner)), `Programada a las ${formatTime(toTime(start))}`);
    } else {
      const it = payload.item;
      const start = Math.max(0, snap(it.start + e.delta.y / PX_PER_MIN, 15));
      if (start === it.start) return;
      if (it.kind === "task") void runSave(() => scheduleTask(it.id, date, toTime(start)), `Movida a las ${formatTime(toTime(start))}`);
      else void runSave(() => moveEventTime(it.id, toTime(start)), `Movido a las ${formatTime(toTime(start))}`);
    }
  };

  return (
    <DndContext sensors={sensors} onDragStart={onStart} onDragEnd={onEnd} onDragCancel={() => setDragging(null)}>
      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <Card className="flex max-h-[calc(100vh-15rem)] min-h-80 flex-col">
          <CardHeader title="Por planificar" description="Arrastra una tarea al cronograma o toca «Programar»." />
          <div className="min-h-0 flex-1 overflow-y-auto pb-2">
            <CandidateList candidates={candidates} someday={someday} draggable onSchedule={(t) => onSlot(-1, t)} colorOf={colorOf} />
          </div>
        </Card>
        <Card className="overflow-hidden">
          <div ref={scrollRef} className="max-h-[calc(100vh-15rem)] min-h-80 overflow-y-auto">
            <div className="grid" style={{ gridTemplateColumns: "74px 1fr" }}>
              <div>
                {hours.map((h) => (
                  <div key={h} className="relative pr-2 text-right text-[11px] whitespace-nowrap text-muted-foreground tabular" style={{ height: 60 * PX_PER_MIN }}>
                    <span className="relative -top-1.5">{formatTime(`${String(h).padStart(2, "0")}:00`)}</span>
                  </div>
                ))}
              </div>
              <TimelineColumn columnRef={columnRef} height={(rangeEnd - rangeStart) * PX_PER_MIN} onEmptyClick={(clientY) => onSlot(minutesAtY(clientY))}>
                {hours.map((h) => (
                  <div key={h} className="pointer-events-none border-b border-border/60" style={{ height: 60 * PX_PER_MIN }} />
                ))}
                {focusEnd > focusStart && (
                  <div
                    className="pointer-events-none absolute right-0 left-0 border-l-2 border-brand/40 bg-brand-soft/25"
                    style={{ top: (focusStart - rangeStart) * PX_PER_MIN, height: (focusEnd - focusStart) * PX_PER_MIN }}
                    aria-hidden
                  >
                    <span className="absolute top-1 right-2 text-[10px] font-medium text-brand/80">Máxima energía</span>
                  </div>
                )}
                {nowMin !== null && nowMin >= rangeStart && nowMin <= rangeEnd && (
                  <div className="pointer-events-none absolute right-0 left-0 z-20 h-px bg-expense" style={{ top: (nowMin - rangeStart) * PX_PER_MIN }}>
                    <span className="absolute -top-1 -left-1 size-2 rounded-full bg-expense" />
                  </div>
                )}
                {lanes.map(({ item, lane, count }) => (
                  <TimelineItem key={item.key} item={item} date={date} lane={lane} count={count} top={(item.start - rangeStart) * PX_PER_MIN} height={Math.max(22, (item.end - item.start) * PX_PER_MIN - 2)} />
                ))}
              </TimelineColumn>
            </div>
          </div>
        </Card>
      </div>
      <DragOverlay dropAnimation={{ duration: 160, easing: "cubic-bezier(0.22,1,0.36,1)" }}>
        {dragging ? <div className="rounded-lg border border-border bg-popover px-3 py-2 text-sm font-medium shadow-pop">{dragging.title}</div> : null}
      </DragOverlay>
    </DndContext>
  );
}

function TimelineColumn({ children, columnRef, height, onEmptyClick }: { children: React.ReactNode; columnRef: React.RefObject<HTMLDivElement | null>; height: number; onEmptyClick: (clientY: number) => void }) {
  const { setNodeRef, isOver } = useDroppable({ id: "timeline" });
  return (
    <div
      ref={(el) => {
        setNodeRef(el);
        columnRef.current = el;
      }}
      role="button"
      tabIndex={-1}
      aria-label="Cronograma: haz clic en un espacio libre para agregar algo"
      onClick={(e) => {
        if (e.target === e.currentTarget) onEmptyClick(e.clientY);
      }}
      className={cn("relative cursor-copy border-l border-border transition-colors", isOver && "bg-brand-soft/30")}
      style={{ height }}
    >
      {children}
    </div>
  );
}

function layoutLanes(items: PlanItem[]) {
  const sorted = [...items].sort((a, b) => a.start - b.start);
  const out: Array<{ item: PlanItem; lane: number; count: number }> = [];
  let group: Array<{ item: PlanItem; lane: number }> = [];
  let groupEnd = -1;
  const flush = () => {
    const count = Math.max(1, ...group.map((g) => g.lane + 1));
    for (const g of group) out.push({ ...g, count });
    group = [];
  };
  for (const it of sorted) {
    if (it.start >= groupEnd && group.length) flush();
    const used = new Set(group.filter((g) => g.item.end > it.start).map((g) => g.lane));
    let lane = 0;
    while (used.has(lane)) lane++;
    group.push({ item: it, lane });
    groupEnd = Math.max(groupEnd, it.end);
  }
  if (group.length) flush();
  return out;
}

function TimelineItem({ item, date, lane, count, top, height }: { item: PlanItem; date: DateStr; lane: number; count: number; top: number; height: number }) {
  const movable = !item.recurring && !item.done;
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id: item.key, data: { type: "item", item, title: item.title }, disabled: !movable });
  const style: React.CSSProperties = {
    ...toneStyle(item.color),
    top,
    height,
    left: `calc(${(lane / count) * 100}% + 4px)`,
    width: `calc(${100 / count}% - 8px)`,
    transform: transform ? `translate3d(0, ${transform.y}px, 0)` : undefined,
  };
  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "group absolute z-10 flex overflow-hidden rounded-lg text-left tone-soft ring-1 ring-card",
        item.kind === "block" && "border border-dashed tone-border",
        item.done && "opacity-55",
        isDragging && "z-30 shadow-pop",
      )}
    >
      {movable && (
        <button type="button" aria-label={`Mover «${item.title}»`} className="flex w-4 shrink-0 cursor-grab items-start justify-center pt-1.5 opacity-50 hover:opacity-100 active:cursor-grabbing" {...listeners} {...attributes}>
          <GripVertical className="size-3" />
        </button>
      )}
      <div className={cn("min-w-0 flex-1 py-1 pr-1", !movable && "pl-2")}>
        <p className={cn("flex items-center gap-1 truncate text-[12.5px] leading-tight font-semibold", item.done && "line-through")}>
          <KindIcon item={item} /> <span className="truncate">{item.title}</span>
        </p>
        {height > 34 && (
          <p className="truncate text-[11px] opacity-80 tabular">
            {formatTime(toTime(item.start))} – {formatTime(toTime(item.end))}
          </p>
        )}
      </div>
      <div className="opacity-100 lg:opacity-0 lg:group-hover:opacity-100 lg:focus-within:opacity-100">
        <ItemMenu item={item} date={date} />
      </div>
    </div>
  );
}

// ── Candidates ───────────────────────────────────────────────────────────────

function CandidateRow({ task, draggable, onSchedule, colorOf }: { task: Task; draggable?: boolean; onSchedule: () => void; colorOf?: (k?: string | null) => string }) {
  const data = useData();
  const now = useNow();
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({ id: `cand:${task.id}`, data: { type: "candidate", task, title: task.title }, disabled: !draggable });
  const color = colorOf?.(task.area) ?? categoryFor(task.area, data.settings.taskCategories)?.color ?? "slate";
  const mins = taskMinutes(task, data.settings.planner);
  return (
    <li ref={setNodeRef} className={cn("flex items-center gap-2 px-3 py-2", isDragging && "opacity-40")}>
      {draggable && (
        <button type="button" aria-label={`Arrastrar «${task.title}»`} className="cursor-grab text-subtle hover:text-foreground active:cursor-grabbing" {...listeners} {...attributes}>
          <GripVertical className="size-4" />
        </button>
      )}
      <span style={toneStyle(color)} className="flex size-6 shrink-0 items-center justify-center rounded-md tone-soft [&_svg]:size-3.5">
        <DynamicIcon name={task.icon ?? "list-checks"} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">{task.title}</p>
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          {task.priority > 0 && (
            <TonePill color={PRIORITY_COLOR[task.priority]} dot={false} className="px-1.5 py-0 text-[11px]">
              {PRIORITY_NAME[task.priority]}
            </TonePill>
          )}
          <span className="tabular">{formatDuration(mins)}</span>
          {!task.date ? <span>· algún día</span> : task.date < now.date ? <span className="text-expense">· atrasada</span> : null}
        </p>
      </div>
      <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={onSchedule}>
        Programar
      </Button>
    </li>
  );
}

function CandidateList({ candidates, someday, draggable, onSchedule, colorOf }: { candidates: Task[]; someday: Task[]; draggable?: boolean; onSchedule: (t: Task) => void; colorOf?: (k?: string | null) => string }) {
  const [showSomeday, setShowSomeday] = React.useState(false);
  const ranked = [...candidates].sort((a, b) => b.priority - a.priority || (a.date ?? "").localeCompare(b.date ?? ""));
  return (
    <div>
      {ranked.length === 0 ? (
        <EmptyState compact icon={<Sparkles />} title="Nada por ubicar" description="Todas las tareas de este día ya tienen hora. Usa «Algún día» o crea una tarea." />
      ) : (
        <ul className="divide-y divide-border">
          {ranked.map((t) => (
            <CandidateRow key={t.id} task={t} draggable={draggable} onSchedule={() => onSchedule(t)} colorOf={colorOf} />
          ))}
        </ul>
      )}
      {someday.length > 0 && (
        <div className="border-t border-border">
          <button type="button" onClick={() => setShowSomeday((v) => !v)} className="w-full px-3 py-2.5 text-left text-xs font-semibold text-muted-foreground hover:text-foreground">
            {showSomeday ? "Ocultar" : "Ver"} «Algún día» ({someday.length})
          </button>
          {showSomeday && (
            <ul className="divide-y divide-border">
              {someday.map((t) => (
                <CandidateRow key={t.id} task={t} draggable={draggable} onSchedule={() => onSchedule(t)} colorOf={colorOf} />
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

// ── Mobile: schedule list with free gaps ─────────────────────────────────────

function MobileSchedule({ date, items, nowMin, onSlot }: { date: DateStr; items: PlanItem[]; nowMin: number | null; onSlot: (start: number) => void }) {
  const data = useData();
  const focus = useFocus();
  const planner = data.settings.planner;
  const from = Math.max(timeToMinutes(planner.dayStart), nowMin === null ? 0 : snap(nowMin, 15));
  const to = timeToMinutes(planner.dayEnd);
  const gaps = freeSlots(items.filter((i) => !i.done), from, to, 20);
  const rows: Array<{ type: "item"; item: PlanItem } | { type: "gap"; start: number; end: number }> = [
    ...items.map((item) => ({ type: "item" as const, item })),
    ...gaps.map((g) => ({ type: "gap" as const, start: g.start, end: g.end })),
  ].sort((a, b) => (a.type === "item" ? a.item.start : a.start) - (b.type === "item" ? b.item.start : b.start));

  if (rows.length === 0) {
    return (
      <Card>
        <EmptyState compact icon={<CalendarCheck />} title="Día libre" description="Toca «Auto-planificar», aplica una plantilla o agrega un bloque." action={<Button size="sm" variant="outline" onClick={() => onSlot(from)}>Agregar algo</Button>} />
      </Card>
    );
  }
  return (
    <Card>
      <ol className="divide-y divide-border">
        {rows.map((r) =>
          r.type === "gap" ? (
            <li key={`gap-${r.start}`}>
              <button type="button" onClick={() => onSlot(r.start)} className="flex w-full items-center gap-3 px-3 py-2.5 text-left hover:bg-accent/50">
                <span className="w-[68px] shrink-0 text-right text-xs text-subtle tabular">{formatTime(toTime(r.start))}</span>
                <span className="flex-1 rounded-md border border-dashed border-border-strong/70 px-2.5 py-1.5 text-[13px] text-muted-foreground">
                  Libre · {formatDuration(r.end - r.start)} <span className="font-medium text-brand">· Usar</span>
                </span>
              </button>
            </li>
          ) : (
            <li key={r.item.key} className={cn("flex items-center gap-3 px-3 py-2.5", r.item.done && "opacity-55", nowMin !== null && r.item.start <= nowMin && nowMin < r.item.end && "bg-brand-soft/40")}>
              <span className="w-[68px] shrink-0 text-right text-xs leading-tight text-muted-foreground tabular">
                {formatTime(toTime(r.item.start))}
                <span className="block text-[11px] text-subtle">{formatDuration(r.item.end - r.item.start)}</span>
              </span>
              <span style={toneStyle(r.item.color)} className={cn("size-2.5 shrink-0 rounded-full tone-dot", r.item.kind === "block" && "opacity-60")} aria-hidden />
              <div className="min-w-0 flex-1">
                <p className={cn("truncate text-sm font-medium", r.item.done && "line-through")}>{r.item.title}</p>
                <p className="flex items-center gap-1 text-xs text-muted-foreground">
                  <KindIcon item={r.item} /> {r.item.kind === "task" ? "Tarea" : r.item.kind === "block" ? "Bloque" : "Evento"}
                </p>
              </div>
              {r.item.kind === "task" && !r.item.done && (
                <Button variant="ghost" size="icon-sm" aria-label={`Completar «${r.item.title}»`} onClick={() => runSave(() => setTaskDone(r.item.id, true), "Tarea completada")}>
                  <Check />
                </Button>
              )}
              {!focus.state && !r.item.done && (
                <Button variant="ghost" size="icon-sm" aria-label={`Iniciar enfoque en «${r.item.title}»`} onClick={() => focus.start({ title: r.item.title, taskId: r.item.kind === "task" ? r.item.id : null })}>
                  <Play />
                </Button>
              )}
              <ItemMenu item={r.item} date={date} />
            </li>
          ),
        )}
      </ol>
    </Card>
  );
}

// ── Sheets ───────────────────────────────────────────────────────────────────

function useClosable(onClose: () => void) {
  const [open, setOpen] = React.useState(true);
  return { open, close: () => (setOpen(false), setTimeout(onClose, 180)) };
}

/** "¿Qué harás a las 10:00?" — schedule a task or add a time block at a time. */
function SlotSheet({ date, start: initialStart, task, candidates, onClose }: { date: DateStr; start: number; task?: Task; candidates: Task[]; onClose: () => void }) {
  const { planner, items } = usePlannerData(date);
  const now = useNow();
  const { open, close } = useClosable(onClose);
  const busy = items.filter((i) => !i.done);
  const defaultStart = initialStart >= 0 ? initialStart : task ? firstFit(task, busy, planner, date === now.date ? timeToMinutes(now.time) : null) : timeToMinutes(planner.dayStart);
  const [tab, setTab] = React.useState<"task" | "block">(task ? "task" : candidates.length ? "task" : "block");
  const [start, setStart] = React.useState(toTime(defaultStart));
  const [duration, setDuration] = React.useState(task ? taskMinutes(task, planner) : 60);
  const [title, setTitle] = React.useState("");
  const [category, setCategory] = React.useState<EventCategory>("trabajo");
  const startMin = timeToMinutes(start);
  const conflicts = busy.filter((i) => i.start < startMin + duration && startMin < i.end && i.id !== task?.id);

  const scheduleOne = (t: Task, mins: number) =>
    runSave(() => scheduleTask(t.id, date, start, mins), `«${t.title}» a las ${formatTime(start)}`).then((ok) => ok && close());

  return (
    <Sheet open={open} onOpenChange={(v) => !v && close()} title={task ? `Programar: ${task.title}` : `¿Qué harás a las ${formatTime(start)}?`} layout="center">
      <div className="space-y-4">
        {!task && (
          <Segmented
            className="w-full"
            value={tab}
            onChange={setTab}
            options={[
              { value: "task", label: "Una tarea" },
              { value: "block", label: "Bloque de tiempo" },
            ]}
          />
        )}
        <div className="grid grid-cols-[1fr_auto] items-end gap-3">
          <Field label="Hora de inicio" htmlFor="slot-start">
            <Input id="slot-start" type="time" step={300} value={start} onChange={(e) => e.target.value && setStart(e.target.value)} />
          </Field>
          <p className="pb-2.5 text-[13px] text-muted-foreground tabular">hasta {formatTime(toTime(startMin + duration))}</p>
        </div>
        {(task || tab === "block") && (
          <Field label="Duración">
            <div className="flex flex-wrap gap-1.5">
              {DURATIONS.map((m) => (
                <Chip key={m} active={duration === m} onClick={() => setDuration(m)}>
                  {m < 60 ? `${m} min` : `${m / 60} h`}
                </Chip>
              ))}
            </div>
          </Field>
        )}
        {conflicts.length > 0 && <p className="rounded-lg bg-warning-soft px-3 py-2 text-[13px] text-warning">Se cruza con «{conflicts[0].title}». Puedes dejarlo así o cambiar la hora.</p>}

        {task ? (
          <Button className="w-full" size="lg" onClick={() => scheduleOne(task, duration)}>
            <CalendarPlus /> Programar a las {formatTime(start)}
          </Button>
        ) : tab === "task" ? (
          candidates.length === 0 ? (
            <p className="text-[13px] text-muted-foreground">No hay tareas pendientes para este día. Crea una tarea o agrega un bloque.</p>
          ) : (
            <ul className="max-h-72 divide-y divide-border overflow-y-auto rounded-lg border border-border">
              {[...candidates]
                .sort((a, b) => b.priority - a.priority)
                .map((t) => (
                  <li key={t.id}>
                    <button type="button" onClick={() => scheduleOne(t, taskMinutes(t, planner))} className="flex w-full items-center gap-2 px-3 py-2.5 text-left hover:bg-accent">
                      <span className="min-w-0 flex-1 truncate text-sm font-medium">{t.title}</span>
                      <span className="text-xs text-muted-foreground tabular">{formatDuration(taskMinutes(t, planner))}</span>
                    </button>
                  </li>
                ))}
            </ul>
          )
        ) : (
          <>
            <div className="flex flex-wrap gap-1.5">
              {BLOCK_PRESETS.map((p) => (
                <Chip
                  key={p.title}
                  active={title === p.title}
                  onClick={() => {
                    setTitle(p.title);
                    setCategory(p.category);
                    setDuration(p.minutes);
                  }}
                >
                  {p.title}
                </Chip>
              ))}
            </div>
            <div className="grid gap-3 sm:grid-cols-[1fr_10rem]">
              <Field label="Nombre del bloque" htmlFor="slot-title">
                <Input id="slot-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ej. Editar videos de clientes" />
              </Field>
              <Field label="Categoría" htmlFor="slot-cat">
                <NativeSelect id="slot-cat" value={category} onChange={(e) => setCategory(e.target.value as EventCategory)}>
                  {Object.entries(EVENT_CATEGORY_LABEL).map(([k, l]) => (
                    <option key={k} value={k}>
                      {l}
                    </option>
                  ))}
                </NativeSelect>
              </Field>
            </div>
            <Button
              className="w-full"
              size="lg"
              disabled={!title.trim()}
              onClick={() => runSave(() => createBlock({ date, title, start, end: toTime(startMin + duration), category }), "Bloque agregado").then((ok) => ok && close())}
            >
              <Timer /> Agregar bloque
            </Button>
          </>
        )}
      </div>
    </Sheet>
  );
}

function AutoPlanSheet({ date, plan, onClose }: { date: DateStr; plan: AutoPlanResult; onClose: () => void }) {
  const { open, close } = useClosable(onClose);
  return (
    <Sheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title="Plan sugerido"
      description="Prioridad alta primero y en tus horas de máxima energía; respeta tus eventos y deja pausas entre bloques."
      layout="center"
      footer={
        <>
          <Button variant="ghost" onClick={close} className="max-sm:hidden">
            Cancelar
          </Button>
          <Button
            size="lg"
            className="max-sm:flex-1 sm:h-9 sm:px-4 sm:text-sm"
            disabled={plan.placed.length === 0}
            onClick={async () => {
              try {
                const previous = await applyPlan(date, plan.placed);
                toast.success(`${plan.placed.length} ${plan.placed.length === 1 ? "tarea programada" : "tareas programadas"}`, {
                  action: { label: "Deshacer", onClick: () => void restoreTasks(previous) },
                });
                close();
              } catch {
                toast.error("No se pudo aplicar el plan");
              }
            }}
          >
            <Wand2 /> Aplicar plan
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {plan.placed.length > 0 && (
          <ol className="divide-y divide-border rounded-lg border border-border">
            {plan.placed.map((p) => (
              <li key={p.taskId} className="flex items-center gap-3 px-3 py-2.5">
                <span className="w-[92px] shrink-0 text-xs text-muted-foreground tabular">
                  {formatTime(toTime(p.start))}–{formatTime(toTime(p.end))}
                </span>
                <span className="min-w-0 flex-1 truncate text-sm font-medium">{p.title}</span>
                {p.inFocusWindow && <TonePill color="iris">Energía alta</TonePill>}
              </li>
            ))}
          </ol>
        )}
        {plan.unplaced.length > 0 && (
          <div className="rounded-lg bg-warning-soft p-3 text-[13px] text-warning">
            <p className="font-semibold">No caben hoy ({plan.unplaced.length}):</p>
            <p className="mt-1">{plan.unplaced.map((u) => `${u.title} (${formatDuration(u.minutes)})`).join(" · ")}</p>
            <p className="mt-1 text-xs">Muévelas a otro día o acorta su duración.</p>
          </div>
        )}
        <p className="text-xs text-muted-foreground">Quedarían {formatDuration(plan.freeAfter)} libres. Las tareas sin duración estimada usan la duración por defecto de Ajustes.</p>
      </div>
    </Sheet>
  );
}

function TemplatesSheet({ date, items, onClose }: { date: DateStr; items: PlanItem[]; onClose: () => void }) {
  const data = useData();
  const { confirm } = useUI();
  const { open, close } = useClosable(onClose);
  const [name, setName] = React.useState("");
  const templates = data.settings.dayTemplates.length ? data.settings.dayTemplates : [SUGGESTED_TEMPLATE];
  const blocks = items.filter((i) => i.kind === "block" && !i.recurring);
  const eventsById = new Map(data.events.map((e) => [e.id, e] as [string, CalendarEvent]));
  const toTemplateBlocks = (): DayTemplateBlock[] =>
    blocks.map((b) => ({ title: b.title, start: toTime(b.start), end: toTime(b.end), category: eventsById.get(b.id)?.category ?? "otro" }));

  return (
    <Sheet open={open} onOpenChange={(v) => !v && close()} title="Plantillas de día" description="Tu rutina ideal en bloques: aplícala a cualquier día con un toque.">
      <div className="space-y-5">
        <ul className="space-y-2">
          {templates.map((t) => (
            <li key={t.id} className="rounded-xl border border-border p-3">
              <div className="flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">
                    {t.name} {t.id === SUGGESTED_TEMPLATE.id && <span className="text-xs font-normal text-muted-foreground">(sugerida)</span>}
                  </p>
                  <p className="text-xs text-muted-foreground">{t.blocks.length} bloques</p>
                </div>
                <div className="flex items-center gap-1">
                  <Button size="sm" onClick={() => runSave(async () => {
                    const n = await applyDayTemplate(t, date);
                    toast.success(n ? `${n} bloques agregados` : "Esos bloques ya estaban en el día");
                  }).then((ok) => ok && close())}>
                    Aplicar
                  </Button>
                  {t.id !== SUGGESTED_TEMPLATE.id && (
                    <Button
                      variant="destructive-ghost"
                      size="icon-sm"
                      aria-label={`Eliminar plantilla ${t.name}`}
                      onClick={async () => {
                        if (await confirm({ title: `¿Eliminar la plantilla «${t.name}»?`, confirmLabel: "Eliminar", destructive: true })) void runSave(() => deleteDayTemplate(t.id), "Plantilla eliminada");
                      }}
                    >
                      <Trash2 />
                    </Button>
                  )}
                </div>
              </div>
              <ol className="mt-2 space-y-0.5 text-xs text-muted-foreground">
                {t.blocks.map((b, i) => (
                  <li key={i} className="flex gap-2 tabular">
                    <span className="w-24 shrink-0">
                      {b.start}–{b.end}
                    </span>
                    <span className="truncate">{b.title}</span>
                  </li>
                ))}
              </ol>
            </li>
          ))}
        </ul>

        <div className="space-y-2 rounded-xl bg-muted/60 p-3">
          <p className="text-[13px] font-semibold">Guardar este día como plantilla</p>
          {blocks.length === 0 ? (
            <p className="text-xs text-muted-foreground">Primero agrega bloques de tiempo a este día (toca un espacio libre del cronograma).</p>
          ) : (
            <form
              className="flex gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                void runSave(() => saveDayTemplate(name, toTemplateBlocks()), "Plantilla guardada").then((ok) => ok && setName(""));
              }}
            >
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder={`Ej. Lunes de producción (${blocks.length} bloques)`} aria-label="Nombre de la plantilla" />
              <Button type="submit" disabled={!name.trim()}>
                Guardar
              </Button>
            </form>
          )}
        </div>
        {blocks.length > 0 && (
          <Button
            variant="ghost"
            className="text-muted-foreground"
            onClick={async () => {
              if (await confirm({ title: "¿Quitar los bloques de este día?", description: "Se eliminan los bloques de tiempo (no las tareas ni los eventos).", confirmLabel: "Quitar bloques", destructive: true }))
                void runSave(() => clearDayBlocks(date), "Bloques quitados");
            }}
          >
            <Trash2 /> Quitar los bloques de este día
          </Button>
        )}
      </div>
    </Sheet>
  );
}

function CloseDaySheet({ date, onClose, onPlanTomorrow }: { date: DateStr; onClose: () => void; onPlanTomorrow: () => void }) {
  const data = useData();
  const { open, close } = useClosable(onClose);
  const tz = data.settings.timeZone;
  const done = data.tasks.filter((t) => t.status === "done" && t.completedAt && instantToDate(t.completedAt, tz) === date);
  const pending = data.tasks.filter((t) => t.status === "todo" && t.date && t.date <= date);
  const [selected, setSelected] = React.useState<string[]>(() => pending.map((t) => t.id));
  const focusMin = data.focusSessions.filter((s) => s.date === date).reduce((s, x) => s + x.minutes, 0);
  const points = done.reduce((s, t) => s + (t.points ?? 0), 0);
  const tomorrow = addDays(date, 1);

  return (
    <Sheet open={open} onOpenChange={(v) => !v && close()} title="Cerrar el día" description="Revisa lo logrado y pasa lo pendiente a mañana en un toque." layout="center">
      <div className="space-y-5">
        <dl className="grid grid-cols-3 gap-2 text-center">
          {[
            { label: "Completadas", value: String(done.length) },
            { label: "Puntos", value: String(points) },
            { label: "Enfoque", value: formatDuration(focusMin) },
          ].map((m) => (
            <div key={m.label} className="rounded-lg bg-muted/60 py-3">
              <dt className="text-[11px] text-muted-foreground">{m.label}</dt>
              <dd className="mt-0.5 text-lg font-semibold tabular">{m.value}</dd>
            </div>
          ))}
        </dl>
        {pending.length === 0 ? (
          <p className="flex items-center gap-2 rounded-lg bg-income-soft px-3 py-2.5 text-[13px] text-income">
            <Check className="size-4" /> No quedan tareas pendientes de este día.
          </p>
        ) : (
          <div>
            <div className="mb-2 flex items-center justify-between">
              <p className="text-[13px] font-semibold">Quedaron pendientes ({pending.length})</p>
              <button type="button" className="text-xs font-medium text-muted-foreground hover:text-foreground" onClick={() => setSelected(selected.length === pending.length ? [] : pending.map((t) => t.id))}>
                {selected.length === pending.length ? "Ninguna" : "Todas"}
              </button>
            </div>
            <ul className="max-h-60 divide-y divide-border overflow-y-auto rounded-lg border border-border">
              {pending.map((t) => (
                <li key={t.id}>
                  <label className="flex cursor-pointer items-center gap-2.5 px-3 py-2 text-sm">
                    <input type="checkbox" className="size-4 accent-[var(--brand)]" checked={selected.includes(t.id)} onChange={() => setSelected((s) => (s.includes(t.id) ? s.filter((x) => x !== t.id) : [...s, t.id]))} />
                    <span className="min-w-0 flex-1 truncate">{t.title}</span>
                    {t.date && t.date < date && <span className="text-xs text-expense">atrasada</span>}
                  </label>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="grid gap-2 sm:grid-cols-2">
          <Button
            size="lg"
            disabled={selected.length === 0}
            onClick={() => runSave(() => moveTasksTo(selected, tomorrow), `${selected.length} ${selected.length === 1 ? "tarea movida" : "tareas movidas"} a mañana`).then((ok) => ok && close())}
          >
            <ArrowRight /> Mover {selected.length || ""} a mañana
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => {
              close();
              onPlanTomorrow();
            }}
          >
            <CalendarPlus /> Planificar mañana
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          ¿Quieres revisar la semana completa?{" "}
          <Link href="/vida/semana/" className="font-medium text-foreground underline underline-offset-2">
            Ir a la revisión semanal
          </Link>
        </p>
      </div>
    </Sheet>
  );
}
