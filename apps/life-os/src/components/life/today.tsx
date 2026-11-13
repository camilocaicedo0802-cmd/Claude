"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, CalendarCheck2, CalendarPlus, Lightbulb, Plus, Repeat, Sparkles, Star, X } from "lucide-react";
import { toast } from "sonner";
import { useData, useJobViews, useNow } from "@/hooks/data";
import { buildAgenda, occupiedMinutes } from "@/domain/agenda";
import { pendingObligations } from "@/domain/finance";
import { dailyBrief, productivityInsights } from "@/domain/insights";
import { isScheduled } from "@/domain/habits";
import { addDays, formatDateLong, formatDuration, type DateStr } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/form-controls";
import { Chip, Progress } from "@/components/ui/misc";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/overlays";
import { Card, CardHeader, EmptyState } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { createTask, rescheduleTask, setDayPriorities } from "@/services/life-service";
import { AgendaRow, CheckCircle, HabitCheckRow, TaskItem, usePriorityToggle } from "./bits";
import { setTaskDone } from "@/services/life-service";
import { InstallBanner } from "@/components/shell/pwa";
import { dayCapacity, dayItems, nowAndNext, planCandidates, toTime } from "@/domain/planner";
import { categoryFor } from "@/domain/tasks";
import { formatTime, timeToMinutes } from "@/lib/dates";
import { CalendarClock, Play, Wand2 } from "lucide-react";
import { useFocus } from "./focus";

/** Compact "Ahora / Siguiente" with a shortcut to the day planner. */
function PlanMyDayCard() {
  const data = useData();
  const now = useNow();
  const focus = useFocus();
  const planner = data.settings.planner;
  const items = React.useMemo(
    () => dayItems(now.date, data.tasks, data.events, planner, (k) => categoryFor(k, data.settings.taskCategories)?.color ?? "slate"),
    [now.date, data.tasks, data.events, planner, data.settings.taskCategories],
  );
  const nowMin = timeToMinutes(now.time);
  const { now: current, next } = nowAndNext(items, nowMin);
  const unplanned = planCandidates(data.tasks, now.date, now.date).length;
  const cap = dayCapacity(items, planner);
  return (
    <Card className="flex flex-wrap items-center gap-3 p-4">
      <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
        <CalendarClock className="size-4" />
      </span>
      <div className="min-w-0 flex-1 basis-[calc(100%-3rem)] sm:basis-0">
        <p className="truncate text-[15px] font-semibold">
          {current ? `Ahora: ${current.title}` : next ? `Siguiente: ${next.title} a las ${formatTime(toTime(next.start))}` : items.length ? "Lo programado de hoy ya pasó" : "Tu día aún no tiene cronograma"}
        </p>
        <p className="truncate text-[13px] text-muted-foreground">
          {current && next ? `Luego: ${next.title} a las ${formatTime(toTime(next.start))} · ` : ""}
          {unplanned ? `${unplanned} ${unplanned === 1 ? "tarea" : "tareas"} sin hora · ` : ""}
          {Math.round(cap.free / 60)} h libres
        </p>
      </div>
      <div className="flex w-full gap-2 pl-12 sm:w-auto sm:pl-0">
        {current && !focus.state && (
          <Button size="sm" variant="outline" onClick={() => focus.start({ title: current.title, taskId: current.kind === "task" ? current.id : null })}>
            <Play /> Enfoque
          </Button>
        )}
        <Button size="sm" asChild>
          <Link href="/vida/planificar/">
            <Wand2 /> Planificar mi día
          </Link>
        </Button>
      </div>
    </Card>
  );
}

export function QuickCapture({ defaultDate, placeholder = "Anota algo pendiente y pulsa Enter" }: { defaultDate: DateStr | null; placeholder?: string }) {
  const now = useNow();
  const [title, setTitle] = React.useState("");
  const [date, setDate] = React.useState<DateStr | null>(defaultDate);
  const inputRef = React.useRef<HTMLInputElement>(null);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const t = title.trim();
    if (!t) return;
    const ok = await runSave(() => createTask({ title: t, date }), date === now.date ? "Agregada a hoy" : date ? "Tarea agendada" : "Guardada en «Algún día»");
    if (ok) {
      setTitle("");
      inputRef.current?.focus();
    }
  };
  return (
    <form onSubmit={submit} className="rounded-xl border border-border bg-card p-2 shadow-[var(--shadow-card)] focus-within:border-ring/60">
      <div className="flex items-center gap-2">
        <Plus className="ml-1.5 size-4 shrink-0 text-muted-foreground" aria-hidden />
        <input
          ref={inputRef}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder={placeholder}
          aria-label="Captura rápida de tarea"
          className="h-9 min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-subtle"
        />
        <Button type="submit" size="sm" disabled={!title.trim()}>
          Agregar
        </Button>
      </div>
      {title.trim() && (
        <div className="mt-2 flex flex-wrap gap-1.5 border-t border-border px-1 pt-2">
          <Chip active={date === now.date} onClick={() => setDate(now.date)}>
            Hoy
          </Chip>
          <Chip active={date === addDays(now.date, 1)} onClick={() => setDate(addDays(now.date, 1))}>
            Mañana
          </Chip>
          <Chip active={date === null} onClick={() => setDate(null)}>
            Algún día
          </Chip>
        </div>
      )}
    </form>
  );
}

export function TodayPage() {
  const data = useData();
  const now = useNow();
  const today = now.date;
  const views = useJobViews();
  const { openForm } = useUI();
  const { priorities, toggle } = usePriorityToggle(today);

  const todays = data.tasks.filter((t) => t.date === today).sort((a, b) => Number(a.status === "done") - Number(b.status === "done") || b.priority - a.priority || (a.time ?? "99").localeCompare(b.time ?? "99"));
  const overdue = data.tasks.filter((t) => t.status === "todo" && t.date && t.date < today).sort((a, b) => a.date!.localeCompare(b.date!));
  const doneToday = todays.filter((t) => t.status === "done").length;
  const priorityTasks = priorities.map((id) => data.tasks.find((t) => t.id === id)).filter(Boolean) as typeof data.tasks;
  const candidates = data.tasks.filter((t) => t.status === "todo" && !priorities.includes(t.id) && (t.date === today || (t.date && t.date < today)));

  const agenda = React.useMemo(
    () =>
      buildAgenda({
        from: today,
        to: today,
        today,
        events: data.events,
        tasks: data.tasks.filter((t) => t.time || t.recurrence),
        jobViews: views,
        obligations: data.obligations,
        plannedIncomes: data.plannedIncomes,
        transactions: data.transactions,
        clients: data.clients,
      }),
    [data, views, today],
  );
  const upcoming = React.useMemo(
    () =>
      buildAgenda({
        from: addDays(today, 1),
        to: addDays(today, 7),
        today,
        events: [],
        tasks: data.tasks.filter((t) => t.status === "todo" && t.followUp),
        jobViews: views,
        obligations: data.obligations,
        plannedIncomes: data.plannedIncomes,
        transactions: data.transactions,
        clients: data.clients,
      }).filter((i) => !i.done && !i.projected),
    [data, views, today],
  );
  const overdueItems = React.useMemo(() => {
    const deliveries = views.filter((v) => v.isOverdue && !v.job.archived);
    const obligations = pendingObligations(data.obligations, data.transactions, addDays(today, -1), today);
    return { deliveries, obligations };
  }, [views, data.obligations, data.transactions, today]);

  const habits = data.habits.filter((h) => !h.archived && isScheduled(h, today));
  const brief = dailyBrief({ today, tasks: data.tasks, jobViews: views, obligations: pendingObligations(data.obligations, data.transactions, addDays(today, 3), today) });
  const insights = productivityInsights({
    today,
    tasks: data.tasks,
    todayAgenda: [...agenda, ...todays.filter((t) => !t.time && t.status === "todo").map((t) => ({ key: t.id, kind: "task" as const, date: today, title: t.title, color: "slate", durationMin: t.durationMin ?? 0, ref: { type: "task" as const, id: t.id } }))],
    jobViews: views,
    habits: data.habits,
    habitLogs: data.habitLogs,
    availableHoursPerDay: data.settings.availableHoursPerDay,
  });
  const busy = occupiedMinutes([...agenda.filter((i) => i.kind === "event"), ...todays.filter((t) => t.status === "todo").map((t) => ({ key: t.id, kind: "task" as const, date: today, title: t.title, color: "slate", durationMin: t.durationMin ?? 0, ref: { type: "task" as const, id: t.id } }))]);
  const progress = todays.length ? (doneToday / todays.length) * 100 : 0;

  return (
    <SectionPage
      section="vida"
      title="Mi día"
      description={<span className="first-letter:uppercase">{formatDateLong(today)}</span>}
      actions={
        <>
          <Button variant="outline" onClick={() => openForm({ kind: "event", defaults: { date: today } })}>
            <CalendarPlus /> Evento
          </Button>
          <Button onClick={() => openForm({ kind: "task", defaults: { date: today } })}>
            <Plus /> Tarea
          </Button>
        </>
      }
    >
      <InstallBanner />
      <PlanMyDayCard />
      <Card className="p-4 sm:p-5">
        <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
          <div className="min-w-0 flex-1">
            <p className="text-[15px] font-medium leading-snug">{brief ?? "No tienes entregas, pagos ni tareas urgentes. Buen momento para adelantar lo importante."}</p>
            {busy > 0 && (
              <p className="mt-1 text-[13px] text-muted-foreground">
                Tiempo planificado hoy: {formatDuration(busy)} de {data.settings.availableHoursPerDay} h disponibles.
              </p>
            )}
          </div>
          <div className="w-full sm:w-64">
            {todays.length === 0 ? (
              <p className="text-[13px] text-muted-foreground">Sin tareas para hoy todavía.</p>
            ) : (
              <>
                <div className="flex items-baseline justify-between text-[13px]">
                  <span className="text-muted-foreground">Progreso del día</span>
                  <span className="font-medium tabular">
                    {doneToday} de {todays.length} tareas
                  </span>
                </div>
                <Progress className="mt-2 h-2" value={progress} tone="income" label="Progreso del día" />
              </>
            )}
          </div>
        </div>
        {insights.length > 0 && (
          <ul className="mt-4 grid gap-2 border-t border-border pt-4 sm:grid-cols-2">
            {insights.map((i) => (
              <li key={i.key}>
                <Link href={i.href ?? "#"} className={cn("flex items-start gap-2 rounded-lg p-2 text-[13px] hover:bg-accent", i.tone === "warning" ? "text-warning" : i.tone === "positive" ? "text-income" : "text-muted-foreground")}>
                  <Lightbulb className="mt-0.5 size-3.5 shrink-0" />
                  <span>{i.text}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <div className="grid gap-4 lg:grid-cols-[1.25fr_1fr]">
        <div className="space-y-4">
          <Card>
            <CardHeader title="Mis tres prioridades" description="Lo que haría que hoy valiera la pena" icon={<Star />} />
            <ol className="space-y-1.5 px-3 pb-4 sm:px-4">
              {[0, 1, 2].map((slot) => {
                const t = priorityTasks[slot];
                if (t) {
                  return (
                    <li key={slot} className="flex items-center gap-3 rounded-lg border border-border bg-background/60 px-3 py-2.5">
                      <span className="w-4 text-sm font-semibold text-brand tabular">{slot + 1}</span>
                      <CheckCircle done={t.status === "done"} priority={t.priority} label={`Completar «${t.title}»`} onToggle={() => runSave(() => setTaskDone(t.id, t.status !== "done"), t.status !== "done" ? "Prioridad cumplida" : undefined)} />
                      <button type="button" className={cn("min-w-0 flex-1 truncate text-left text-sm font-medium", t.status === "done" && "text-muted-foreground line-through")} onClick={() => openForm({ kind: "task", id: t.id })}>
                        {t.title}
                      </button>
                      <Button variant="ghost" size="icon-sm" aria-label="Quitar de prioridades" onClick={() => runSave(() => setDayPriorities(today, priorities.filter((p) => p !== t.id)))}>
                        <X />
                      </Button>
                    </li>
                  );
                }
                return (
                  <li key={slot}>
                    <PriorityPicker slot={slot} candidates={candidates} onPick={(id) => toggle(id)} onCreate={async (title) => {
                      const id = await createTask({ title, date: today, priority: 3 });
                      await setDayPriorities(today, [...priorities, id]);
                    }} />
                  </li>
                );
              })}
            </ol>
          </Card>

          <Card>
            <CardHeader
              title="Tareas de hoy"
              description={todays.length ? `${todays.length - doneToday} pendientes` : undefined}
              action={
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/vida/tareas/">
                    Todas <ArrowRight />
                  </Link>
                </Button>
              }
            />
            <div className="space-y-3 px-2 pb-3 sm:px-3">
              <QuickCapture defaultDate={today} />
              {overdue.length > 0 && (
                <div className="rounded-lg border border-expense/25 bg-expense-soft/50 p-1">
                  <div className="flex items-center justify-between gap-2 px-2 pt-1.5">
                    <p className="text-xs font-semibold text-expense">Atrasadas ({overdue.length})</p>
                    <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => runSave(async () => { for (const t of overdue) await rescheduleTask(t.id, today); }, "Atrasadas movidas a hoy")}>
                      Mover todo a hoy
                    </Button>
                  </div>
                  {overdue.slice(0, 5).map((t) => (
                    <TaskItem key={t.id} task={t} onPriorityToggle={() => toggle(t.id)} isPriority={priorities.includes(t.id)} />
                  ))}
                  {overdue.length > 5 && (
                    <Link href="/vida/tareas/?vista=vencidas" className="block px-2 pb-1.5 text-xs font-medium text-expense hover:underline">
                      Ver las {overdue.length} atrasadas
                    </Link>
                  )}
                </div>
              )}
              {todays.length === 0 ? (
                <EmptyState compact icon={<CalendarCheck2 />} title="Nada programado para hoy" description="Escribe arriba lo primero que tienes que hacer, o trae tareas de «Algún día»." />
              ) : (
                <div>
                  {todays.map((t) => (
                    <TaskItem key={t.id} task={t} showDate={false} onPriorityToggle={() => toggle(t.id)} isPriority={priorities.includes(t.id)} />
                  ))}
                </div>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader
              title="Agenda de hoy"
              action={
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/vida/calendario/">
                    Calendario <ArrowRight />
                  </Link>
                </Button>
              }
            />
            <div className="px-2 pb-3 sm:px-3">
              {agenda.length === 0 && overdueItems.deliveries.length === 0 && overdueItems.obligations.length === 0 ? (
                <p className="px-2 pb-2 text-[13px] text-muted-foreground">Sin compromisos con hora para hoy.</p>
              ) : (
                <>
                  {overdueItems.deliveries.map((v) => (
                    <AgendaRow key={v.job.id} item={{ key: v.job.id, kind: "delivery", date: v.job.dueDate!, title: `Entrega atrasada: ${v.job.title}`, subtitle: v.client?.name, color: "rose", overdue: true, ref: { type: "job", id: v.job.id } }} showDate />
                  ))}
                  {overdueItems.obligations.map((o) => (
                    <AgendaRow key={o.key} item={{ key: o.key, kind: "obligation", date: o.dueDate, title: `Pago vencido: ${o.source.name}`, color: "rose", amount: o.remaining, overdue: true, ref: { type: "obligation", id: o.source.id, date: o.dueDate } }} showDate />
                  ))}
                  {agenda.map((i) => (
                    <AgendaRow key={i.key} item={i} />
                  ))}
                </>
              )}
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Hábitos de hoy"
              icon={<Repeat />}
              action={
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/vida/habitos/">
                    Ver <ArrowRight />
                  </Link>
                </Button>
              }
            />
            <div className="space-y-2 px-3 pb-4 sm:px-4">
              {data.habits.filter((h) => !h.archived).length === 0 ? (
                <EmptyState
                  compact
                  icon={<Sparkles />}
                  title="Sin hábitos"
                  description="Ejercicio, lectura, agua… marca cada uno con un toque."
                  action={
                    <Button size="sm" variant="outline" onClick={() => openForm({ kind: "habit" })}>
                      <Plus /> Crear hábito
                    </Button>
                  }
                />
              ) : habits.length === 0 ? (
                <p className="text-[13px] text-muted-foreground">Hoy no tienes hábitos programados. Día de descanso.</p>
              ) : (
                habits.map((h) => <HabitCheckRow key={h.id} habit={h} date={today} />)
              )}
            </div>
          </Card>

          <Card>
            <CardHeader title="Próximos vencimientos" description="7 días: entregas, pagos, cobros y seguimientos" />
            <div className="px-2 pb-3 sm:px-3">
              {upcoming.length === 0 ? <p className="px-2 pb-2 text-[13px] text-muted-foreground">Nada vence en la próxima semana.</p> : upcoming.slice(0, 8).map((i) => <AgendaRow key={i.key} item={i} showDate />)}
            </div>
          </Card>
        </div>
      </div>
    </SectionPage>
  );
}

function PriorityPicker({ slot, candidates, onPick, onCreate }: { slot: number; candidates: Array<{ id: string; title: string }>; onPick: (id: string) => void; onCreate: (title: string) => Promise<void> }) {
  const [open, setOpen] = React.useState(false);
  const [title, setTitle] = React.useState("");
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button type="button" className="flex w-full items-center gap-3 rounded-lg border border-dashed border-border-strong px-3 py-2.5 text-left text-sm text-muted-foreground transition-colors hover:border-brand/50 hover:bg-brand-soft/40 hover:text-foreground">
          <span className="w-4 font-semibold tabular">{slot + 1}</span>
          Elegir prioridad
        </button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-[min(92vw,360px)] p-2">
        <form
          className="flex gap-2 p-1"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!title.trim()) return;
            try {
              await onCreate(title.trim());
              setTitle("");
              setOpen(false);
            } catch {
              toast.error("No se pudo crear la tarea");
            }
          }}
        >
          <Input autoFocus value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Nueva prioridad…" aria-label="Nueva prioridad" />
          <Button type="submit" size="icon" aria-label="Crear prioridad">
            <Plus />
          </Button>
        </form>
        {candidates.length > 0 && (
          <>
            <p className="px-2 pt-2 pb-1 text-xs font-medium text-muted-foreground">O elige de tus tareas</p>
            <ul className="max-h-60 overflow-y-auto">
              {candidates.map((t) => (
                <li key={t.id}>
                  <button
                    type="button"
                    className="w-full truncate rounded-md px-2 py-2 text-left text-sm hover:bg-accent"
                    onClick={() => {
                      onPick(t.id);
                      setOpen(false);
                    }}
                  >
                    {t.title}
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}
      </PopoverContent>
    </Popover>
  );
}
