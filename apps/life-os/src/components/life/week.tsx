"use client";

import * as React from "react";
import { DndContext, KeyboardSensor, MouseSensor, useDraggable, useDroppable, useSensor, useSensors, type DragEndEvent } from "@dnd-kit/core";
import { CheckCheck, ChevronLeft, ChevronRight, ClipboardCheck, GripVertical, Plus, Star } from "lucide-react";
import { useData, useJobViews, useToday } from "@/hooks/data";
import { useMediaQuery } from "@/hooks/use-media";
import { buildAgenda, eventDuration } from "@/domain/agenda";
import { isDone, isScheduled, logsIndex } from "@/domain/habits";
import { addDays, eachDay, endOfWeek, formatDateLong, formatDayMonth, formatDuration, startOfWeek, WEEKDAY_SHORT, weekday, type DateStr } from "@/lib/dates";
import { occurrencesBetween } from "@/lib/recurrence";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Field, Input, NativeSelect, Textarea } from "@/components/ui/form-controls";
import { Progress } from "@/components/ui/misc";
import { Card, CardHeader } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { rescheduleTask, saveWeekPlan } from "@/services/life-service";
import { AgendaRow, CheckCircle } from "./bits";
import { setTaskDone } from "@/services/life-service";
import type { Task } from "@/db/types";

export function WeekPage() {
  const data = useData();
  const today = useToday();
  const views = useJobViews();
  const coarse = useMediaQuery("(pointer: coarse)");
  const { openForm } = useUI();
  const ws = data.settings.weekStartsOn;
  const [weekStart, setWeekStart] = React.useState(() => startOfWeek(today, ws));
  const weekEnd = endOfWeek(weekStart, ws);
  const days = eachDay(weekStart, weekEnd);
  const plan = data.weekPlans.find((p) => p.weekStart === weekStart);
  const sensors = useSensors(useSensor(MouseSensor, { activationConstraint: { distance: 6 } }), useSensor(KeyboardSensor));

  const agenda = React.useMemo(
    () =>
      buildAgenda({
        from: weekStart,
        to: weekEnd,
        today,
        events: data.events,
        tasks: [],
        jobViews: views,
        obligations: data.obligations,
        plannedIncomes: data.plannedIncomes,
        transactions: data.transactions,
        clients: data.clients,
      }),
    [data, views, weekStart, weekEnd, today],
  );
  const tasksByDay = (d: DateStr) => data.tasks.filter((t) => t.date === d).sort((a, b) => Number(a.status === "done") - Number(b.status === "done") || b.priority - a.priority);
  const hoursAvail = data.settings.availableHoursPerDay * 60;
  const index = React.useMemo(() => logsIndex(data.habitLogs), [data.habitLogs]);

  const busyFor = (d: DateStr) => {
    const taskMin = tasksByDay(d)
      .filter((t) => t.status === "todo")
      .reduce((s, t) => s + (t.durationMin ?? 0), 0);
    const eventMin = data.events.reduce((s, e) => s + (occurrencesBetween(e.date, e.recurrence, d, d).length && !e.exceptions?.includes(d) ? eventDuration(e) : 0), 0);
    return taskMin + eventMin;
  };

  const onDragEnd = (e: DragEndEvent) => {
    const taskId = e.active.id as string;
    const date = e.over?.id as string | undefined;
    if (!date) return;
    const task = data.tasks.find((t) => t.id === taskId);
    if (task && task.date !== date) void runSave(() => rescheduleTask(taskId, date), `Movida al ${formatDateLong(date)}`);
  };

  const weekTasks = data.tasks.filter((t) => t.date && t.date >= weekStart && t.date <= weekEnd);
  const completed = weekTasks.filter((t) => t.status === "done");
  const pending = weekTasks.filter((t) => t.status === "todo");
  const deliveries = views.filter((v) => v.isOpen && v.job.dueDate && v.job.dueDate >= weekStart && v.job.dueDate <= addDays(weekEnd, 7) && !v.job.archived);
  const habitStats = (() => {
    let s = 0;
    let dn = 0;
    for (const h of data.habits.filter((x) => !x.archived)) {
      for (const d of days) {
        if (d > today || !isScheduled(h, d)) continue;
        s++;
        if (isDone(h, index, d)) dn++;
      }
    }
    return { s, dn };
  })();
  const totalBusy = days.reduce((s, d) => s + busyFor(d), 0);

  const [priorities, setPriorities] = React.useState<string[]>(plan?.priorities ?? ["", "", ""]);
  const [review, setReview] = React.useState(plan?.review ?? { completed: "", pending: "", next: "" });
  React.useEffect(() => {
    setPriorities([...(plan?.priorities ?? []), "", "", ""].slice(0, 3));
    setReview(plan?.review ?? { completed: "", pending: "", next: "" });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weekStart, plan?.weekStart]);

  return (
    <SectionPage
      section="vida"
      title="Semana"
      description="Planifica tu semana, mueve tareas entre días y cierra con una revisión."
      actions={
        <Button onClick={() => openForm({ kind: "task", defaults: { date: today >= weekStart && today <= weekEnd ? today : weekStart } })}>
          <Plus /> Tarea
        </Button>
      }
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm" onClick={() => setWeekStart(startOfWeek(today, ws))}>
            Esta semana
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Semana anterior" onClick={() => setWeekStart(addDays(weekStart, -7))}>
            <ChevronLeft />
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Semana siguiente" onClick={() => setWeekStart(addDays(weekStart, 7))}>
            <ChevronRight />
          </Button>
          <h2 className="ml-1 text-sm font-semibold sm:text-[15px]">
            {formatDayMonth(weekStart)} – {formatDayMonth(weekEnd)}
          </h2>
        </div>
        <p className="text-[13px] text-muted-foreground">
          {formatDuration(totalBusy)} planificadas de {data.settings.availableHoursPerDay * 7} h disponibles
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_1.4fr]">
        <Card>
          <CardHeader title="Prioridades de la semana" icon={<Star />} />
          <form
            className="space-y-2 px-4 pb-4 sm:px-5"
            onSubmit={(e) => {
              e.preventDefault();
              void runSave(() => saveWeekPlan(weekStart, { priorities: priorities.map((p) => p.trim()).filter(Boolean) }), "Prioridades guardadas");
            }}
          >
            {[0, 1, 2].map((i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="w-4 text-sm font-semibold text-brand tabular">{i + 1}</span>
                <Input
                  value={priorities[i] ?? ""}
                  onChange={(e) => setPriorities((p) => p.map((x, j) => (j === i ? e.target.value : x)))}
                  onBlur={() => saveWeekPlan(weekStart, { priorities: priorities.map((p) => p.trim()).filter(Boolean) })}
                  placeholder={i === 0 ? "Lo más importante de esta semana" : "Otra prioridad"}
                  aria-label={`Prioridad ${i + 1} de la semana`}
                />
              </div>
            ))}
          </form>
        </Card>
        <Card>
          <CardHeader title="Entregas y pagos de la semana" description="Trabajos de clientes y obligaciones" />
          <div className="max-h-64 overflow-y-auto px-2 pb-3 sm:px-3">
            {agenda.filter((i) => i.kind !== "event").length === 0 && deliveries.length === 0 ? (
              <p className="px-2 pb-2 text-[13px] text-muted-foreground">Sin entregas ni pagos esta semana.</p>
            ) : (
              agenda.filter((i) => i.kind !== "event").map((i) => <AgendaRow key={i.key} item={i} showDate />)
            )}
          </div>
        </Card>
      </div>

      <DndContext sensors={sensors} onDragEnd={onDragEnd}>
        <div className="grid gap-3 md:grid-cols-2 xl:-mx-1 xl:grid-cols-[repeat(7,minmax(160px,1fr))] xl:gap-2 xl:overflow-x-auto xl:px-1 xl:pb-1">
          {days.map((d) => (
            <DayColumn key={d} date={d} today={today} tasks={tasksByDay(d)} events={agenda.filter((i) => i.date === d && i.kind === "event")} other={agenda.filter((i) => i.date === d && i.kind !== "event")} busy={busyFor(d)} available={hoursAvail} coarse={coarse} days={days} />
          ))}
        </div>
      </DndContext>

      <Card>
        <CardHeader title="Revisión semanal" description="Cinco minutos para cerrar la semana y preparar la siguiente" icon={<ClipboardCheck />} />
        <div className="grid gap-4 px-4 pb-5 sm:px-5 lg:grid-cols-3">
          <div className="space-y-2">
            <Field label="¿Qué completé?">
              <Textarea rows={4} value={review.completed} onChange={(e) => setReview({ ...review, completed: e.target.value })} placeholder="Logros de la semana" />
            </Field>
            <p className="text-xs text-muted-foreground">
              Datos: {completed.length} tareas completadas{habitStats.s ? ` · hábitos ${habitStats.dn}/${habitStats.s}` : ""}.
            </p>
            {completed.length > 0 && (
              <Button variant="ghost" size="sm" onClick={() => setReview({ ...review, completed: [review.completed, ...completed.map((t) => `• ${t.title}`)].filter(Boolean).join("\n") })}>
                <CheckCheck /> Insertar tareas completadas
              </Button>
            )}
          </div>
          <div className="space-y-2">
            <Field label="¿Qué quedó pendiente?">
              <Textarea rows={4} value={review.pending} onChange={(e) => setReview({ ...review, pending: e.target.value })} placeholder="Lo que se movió o quedó sin hacer" />
            </Field>
            <p className="text-xs text-muted-foreground">{pending.length} tareas pendientes en esta semana.</p>
            {pending.length > 0 && (
              <Button variant="ghost" size="sm" onClick={() => setReview({ ...review, pending: [review.pending, ...pending.map((t) => `• ${t.title}`)].filter(Boolean).join("\n") })}>
                Insertar pendientes
              </Button>
            )}
          </div>
          <div className="space-y-2">
            <Field label="¿Qué necesito priorizar la próxima semana?">
              <Textarea rows={4} value={review.next} onChange={(e) => setReview({ ...review, next: e.target.value })} placeholder="Tus focos para la siguiente semana" />
            </Field>
            {deliveries.length > 0 && <p className="text-xs text-muted-foreground">Próximas entregas: {deliveries.slice(0, 3).map((v) => v.job.title).join(", ")}.</p>}
          </div>
        </div>
        <div className="flex items-center justify-end gap-2 border-t border-border px-4 py-3 sm:px-5">
          {plan?.reviewedAt && <span className="mr-auto text-xs text-muted-foreground">Guardada</span>}
          <Button
            onClick={async () => {
              await runSave(() => saveWeekPlan(weekStart, { review, reviewedAt: new Date().toISOString() }), "Revisión guardada");
              const next = addDays(weekStart, 7);
              const lines = review.next.split("\n").map((l) => l.replace(/^[•\-\s]+/, "").trim()).filter(Boolean).slice(0, 3);
              if (lines.length && !data.weekPlans.find((p) => p.weekStart === next)?.priorities.length) await saveWeekPlan(next, { priorities: lines });
            }}
          >
            Guardar revisión
          </Button>
        </div>
      </Card>
    </SectionPage>
  );
}

function DraggableTask({ task, coarse, days }: { task: Task; coarse: boolean; days: DateStr[] }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id: task.id, disabled: coarse || task.status === "done" });
  const { openForm } = useUI();
  const done = task.status === "done";
  return (
    <div
      ref={setNodeRef}
      style={transform ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)` } : undefined}
      className={cn("group relative flex items-start gap-2 rounded-lg border border-border bg-card px-2 py-2 text-[13px]", isDragging && "z-30 shadow-pop")}
    >
      <CheckCircle done={done} priority={task.priority} label={`Completar «${task.title}»`} onToggle={() => runSave(() => setTaskDone(task.id, !done))} />
      <button type="button" className="min-w-0 flex-1 text-left" onClick={() => openForm({ kind: "task", id: task.id })}>
        <span className={cn("line-clamp-3 leading-snug", done ? "text-muted-foreground line-through" : "font-medium")} title={task.title}>{task.title}</span>
        {task.durationMin ? <span className="text-[11px] text-muted-foreground">{formatDuration(task.durationMin)}</span> : null}
      </button>
      {!coarse && !done && (
        <button type="button" aria-label={`Mover «${task.title}» a otro día`} className="cursor-grab text-subtle opacity-0 group-hover:opacity-100 focus-visible:opacity-100 active:cursor-grabbing" {...listeners} {...attributes}>
          <GripVertical className="size-4" />
        </button>
      )}
      {coarse && !done && (
        <NativeSelect aria-label={`Mover «${task.title}»`} className="w-[76px] shrink-0 [&_select]:h-7 [&_select]:px-1.5 [&_select]:pr-6 [&_select]:text-[11px]" value={task.date ?? ""} onChange={(e) => runSave(() => rescheduleTask(task.id, e.target.value), "Tarea movida")}>
          {days.map((d) => (
            <option key={d} value={d}>
              {WEEKDAY_SHORT[weekday(d)]}
            </option>
          ))}
          <option value={addDays(days[6], 1)}>Sig. sem.</option>
        </NativeSelect>
      )}
    </div>
  );
}

function DayColumn({
  date,
  today,
  tasks,
  events,
  other,
  busy,
  available,
  coarse,
  days,
}: {
  date: DateStr;
  today: DateStr;
  tasks: Task[];
  events: ReturnType<typeof buildAgenda>;
  other: ReturnType<typeof buildAgenda>;
  busy: number;
  available: number;
  coarse: boolean;
  days: DateStr[];
}) {
  const { setNodeRef, isOver } = useDroppable({ id: date });
  const { openForm } = useUI();
  const over = busy > available;
  return (
    <section ref={setNodeRef} aria-label={formatDateLong(date)} className={cn("flex min-h-40 flex-col rounded-xl border border-border bg-muted/40 p-2 transition-colors", date === today && "border-brand/40 bg-brand-soft/30", isOver && "ring-2 ring-brand/50")}>
      <header className="flex items-start justify-between gap-1 px-1 pb-2">
        <div>
          <p className={cn("text-[13px] font-semibold first-letter:uppercase", date === today && "text-brand")}>
            {WEEKDAY_SHORT[weekday(date)]} {Number(date.slice(8))}
          </p>
          <p className={cn("text-[11px] tabular", over ? "font-medium text-expense" : "text-muted-foreground")}>
            {busy ? `${formatDuration(busy)} de ${Math.round(available / 60)} h` : "Libre"}
            {over ? " · sobrecargado" : ""}
          </p>
          {busy > 0 && !over && <p className="text-[11px] text-muted-foreground tabular">~{formatDuration(Math.max(0, available - busy))} libres</p>}
        </div>
        <Button variant="ghost" size="icon-sm" aria-label={`Agregar tarea el ${formatDateLong(date)}`} onClick={() => openForm({ kind: "task", defaults: { date } })}>
          <Plus />
        </Button>
      </header>
      {busy > 0 && <Progress value={(busy / Math.max(1, available)) * 100} tone={over ? "expense" : busy / available > 0.8 ? "warning" : "brand"} className="mb-2 h-1" label="Tiempo ocupado" />}
      <div className="flex flex-1 flex-col gap-1.5">
        {other.map((i) => (
          <AgendaRow key={i.key} item={i} compact />
        ))}
        {events.map((i) => (
          <AgendaRow key={i.key} item={i} compact />
        ))}
        {tasks.map((t) => (
          <DraggableTask key={t.id} task={t} coarse={coarse} days={days} />
        ))}
        {tasks.length === 0 && events.length === 0 && other.length === 0 && <p className="px-1 py-2 text-[11px] text-subtle">{coarse ? "Libre" : "Arrastra tareas aquí"}</p>}
      </div>
    </section>
  );
}
