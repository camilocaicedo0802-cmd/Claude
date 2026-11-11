"use client";

import * as React from "react";
import {
  BriefcaseBusiness,
  CalendarClock,
  CalendarDays,
  CalendarPlus,
  Check,
  Copy,
  Flag,
  HandCoins,
  ListTodo,
  MoreHorizontal,
  Pencil,
  Repeat,
  Star,
  Trash2,
  TrendingUp,
  Users,
} from "lucide-react";
import { useData, useMoney, useToday } from "@/hooks/data";
import type { Habit, Task } from "@/db/types";
import type { AgendaItem } from "@/domain/agenda";
import { isDone, isScheduled, logKey } from "@/domain/habits";
import { addDays, formatDuration, formatRelativeDay, formatTime, type DateStr } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/overlays";
import { DynamicIcon, toneStyle } from "@/components/shared/primitives";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { FOLLOWUP_LABEL } from "@/components/forms/life-forms";
import { deleteTask, duplicateTask, postponeTask, rescheduleTask, setDayPriorities, setTaskDone, toggleHabit } from "@/services/life-service";

export function CheckCircle({ done, onToggle, label, priority }: { done: boolean; onToggle: () => void; label: string; priority?: number }) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={done}
      aria-label={label}
      onClick={(e) => {
        e.stopPropagation();
        onToggle();
      }}
      className={cn(
        "press relative flex size-[22px] shrink-0 items-center justify-center rounded-full border-2 outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        done ? "border-income bg-income text-white dark:text-background" : priority === 3 ? "border-expense/70 hover:bg-expense-soft" : priority === 2 ? "border-warning/80 hover:bg-warning-soft" : "border-border-strong hover:border-income hover:bg-income-soft",
      )}
    >
      {done && <Check className="size-3.5 animate-check" strokeWidth={3} />}
      <span className="absolute -inset-2.5" aria-hidden />
    </button>
  );
}

export function TaskItem({ task, showDate = true, onPriorityToggle, isPriority, className }: { task: Task; showDate?: boolean; onPriorityToggle?: () => void; isPriority?: boolean; className?: string }) {
  const data = useData();
  const today = useToday();
  const { openForm, confirm } = useUI();
  const done = task.status === "done";
  const overdue = !done && task.date && task.date < today;
  const client = task.clientId ? data.clients.find((c) => c.id === task.clientId) : undefined;
  const subDone = task.subtasks.filter((s) => s.done).length;
  const meta = [
    showDate && task.date ? formatRelativeDay(task.date, today) : null,
    task.time ? formatTime(task.time) : null,
    task.durationMin ? formatDuration(task.durationMin) : null,
  ].filter(Boolean);
  return (
    <div className={cn("group flex items-start gap-3 rounded-lg px-2 py-2.5 transition-colors hover:bg-accent/60", className)}>
      <div className="pt-0.5">
        <CheckCircle
          done={done}
          priority={task.priority}
          label={done ? `Marcar «${task.title}» como pendiente` : `Completar «${task.title}»`}
          onToggle={() =>
            void runSave(async () => {
              const next = await setTaskDone(task.id, !done);
              return next;
            }, !done ? (task.recurrence ? "Hecho · se programó la siguiente" : "Tarea completada") : undefined, !done ? () => setTaskDone(task.id, false) : undefined)
          }
        />
      </div>
      <button type="button" className="min-w-0 flex-1 text-left outline-none" onClick={() => openForm({ kind: "task", id: task.id })}>
        <span className={cn("block text-sm leading-snug", done ? "text-muted-foreground line-through decoration-border-strong" : "font-medium")}>{task.title}</span>
        <span className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-muted-foreground">
          {meta.length > 0 && <span className={cn(overdue && "font-medium text-expense")}>{meta.join(" · ")}</span>}
          {task.recurrence && <Repeat className="size-3" aria-label="Se repite" />}
          {client && (
            <span className="inline-flex items-center gap-1">
              <Users className="size-3" /> {client.name}
            </span>
          )}
          {task.followUp && <span className="text-info">{FOLLOWUP_LABEL[task.followUp]}</span>}
          {task.subtasks.length > 0 && (
            <span>
              {subDone}/{task.subtasks.length} subtareas
            </span>
          )}
          {task.priority === 3 && !done && (
            <span className="inline-flex items-center gap-0.5 text-expense">
              <Flag className="size-3" /> Alta
            </span>
          )}
        </span>
      </button>
      {!done && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon-sm" aria-label={`Acciones de «${task.title}»`} className="text-muted-foreground opacity-100 lg:opacity-0 lg:group-hover:opacity-100 lg:focus-visible:opacity-100 lg:data-[state=open]:opacity-100">
              <MoreHorizontal />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>Reprogramar</DropdownMenuLabel>
            <DropdownMenuItem onSelect={() => runSave(() => rescheduleTask(task.id, today), "Movida a hoy")}>
              <CalendarDays /> Hoy
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => runSave(() => postponeTask(task.id, 1, today), "Pospuesta para mañana")}>
              <CalendarClock /> Posponer a mañana
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => runSave(() => rescheduleTask(task.id, addDays(today, 7)), "Movida a la próxima semana")}>
              <CalendarPlus /> En una semana
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => runSave(() => rescheduleTask(task.id, null), "Movida a «Algún día»")}>
              <ListTodo /> Algún día (sin fecha)
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {onPriorityToggle && (
              <DropdownMenuItem onSelect={onPriorityToggle}>
                <Star /> {isPriority ? "Quitar de prioridades" : "Marcar como prioridad del día"}
              </DropdownMenuItem>
            )}
            <DropdownMenuItem onSelect={() => openForm({ kind: "task", id: task.id })}>
              <Pencil /> Editar
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => runSave(() => duplicateTask(task.id), "Tarea duplicada")}>
              <Copy /> Duplicar
            </DropdownMenuItem>
            <DropdownMenuItem
              destructive
              onSelect={async () => {
                if (await confirm({ title: "¿Eliminar esta tarea?", confirmLabel: "Eliminar", destructive: true })) void runSave(() => deleteTask(task.id), "Tarea eliminada");
              }}
            >
              <Trash2 /> Eliminar
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  );
}

const KIND_ICON = {
  event: CalendarDays,
  task: ListTodo,
  delivery: BriefcaseBusiness,
  obligation: CalendarClock,
  income: TrendingUp,
  collection: HandCoins,
};

/** Opens whatever an agenda item points at, without leaving the page. */
export function useAgendaOpener() {
  const { openForm, openDetail } = useUI();
  return React.useCallback(
    (item: AgendaItem) => {
      if (item.ref.type === "event") openForm({ kind: "event", id: item.ref.id, occurrence: item.ref.date });
      else if (item.ref.type === "task") openForm({ kind: "task", id: item.ref.id });
      else if (item.ref.type === "job") openDetail({ type: "job", id: item.ref.id });
      else if (item.ref.type === "obligation") openForm({ kind: "obligationPayment", obligationId: item.ref.id, dueDate: item.ref.date! });
      else if (item.ref.type === "plannedIncome") openForm({ kind: "receiveIncome", plannedIncomeId: item.ref.id, dueDate: item.ref.date! });
    },
    [openForm, openDetail],
  );
}

export function AgendaRow({ item, showDate, compact }: { item: AgendaItem; showDate?: boolean; compact?: boolean }) {
  const today = useToday();
  const money = useMoney();
  const open = useAgendaOpener();
  const Icon = KIND_ICON[item.kind];
  return (
    <button
      type="button"
      onClick={() => open(item)}
      className={cn("flex w-full items-start gap-3 rounded-lg px-2 py-2 text-left transition-colors outline-none hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring", item.done && "opacity-55", item.projected && "opacity-70")}
    >
      {!compact && (
        <span className="w-[72px] shrink-0 pt-0.5 text-right text-xs whitespace-nowrap text-muted-foreground tabular">
          {item.time ? formatTime(item.time) : showDate ? formatRelativeDay(item.date, today) : "Todo el día"}
        </span>
      )}
      <span style={toneStyle(item.color)} className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-md tone-soft [&_svg]:size-3">
        <Icon />
      </span>
      <span className="min-w-0 flex-1">
        <span className={cn("block truncate", compact ? "text-xs" : "text-sm", item.done ? "line-through" : "font-medium", item.overdue && "text-expense")}>{item.title}</span>
        {compact && item.time && <span className="block text-[11px] text-muted-foreground tabular">{formatTime(item.time)}</span>}
        {!compact && (item.subtitle || item.endTime || item.amount !== undefined || item.projected) && (
          <span className="block truncate text-xs text-muted-foreground">
            {[
              item.endTime && item.time ? `hasta ${formatTime(item.endTime)}` : null,
              item.amount !== undefined ? money(item.amount) : null,
              item.subtitle,
              item.projected ? "Se repite" : null,
              item.overdue ? "Atrasado" : null,
            ]
              .filter(Boolean)
              .join(" · ")}
          </span>
        )}
      </span>
    </button>
  );
}

export function HabitCheckRow({ habit, date }: { habit: Habit; date: DateStr }) {
  const data = useData();
  const log = data.habitLogs.find((l) => l.id === logKey(habit.id, date));
  const count = log?.count ?? 0;
  const target = Math.max(1, habit.target);
  const index = React.useMemo(() => new Map(data.habitLogs.map((l) => [l.id, l])), [data.habitLogs]);
  const done = isDone(habit, index, date);
  if (!isScheduled(habit, date)) return null;
  return (
    <button
      type="button"
      aria-pressed={done}
      onClick={() => runSave(() => toggleHabit(habit, date))}
      style={toneStyle(habit.color)}
      className={cn(
        "press flex w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring",
        done ? "tone-border tone-soft" : "border-border bg-card hover:border-border-strong",
      )}
    >
      <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-lg [&_svg]:size-4", done ? "tone-dot text-white dark:text-background" : "tone-soft")}>
        {done ? <Check className="animate-check" strokeWidth={3} /> : <DynamicIcon name={habit.icon} />}
      </span>
      <span className="min-w-0 flex-1">
        <span className={cn("block truncate text-sm font-medium", done && "text-foreground")}>{habit.name}</span>
        {target > 1 && (
          <span className="block text-xs text-muted-foreground tabular">
            {count}/{target} {habit.unit ?? "veces"}
          </span>
        )}
      </span>
      {target > 1 && (
        <span className="flex gap-0.5" aria-hidden>
          {Array.from({ length: Math.min(target, 10) }, (_, i) => (
            <span key={i} className={cn("h-3 w-1.5 rounded-full", i < count ? "tone-dot" : "bg-border")} />
          ))}
        </span>
      )}
    </button>
  );
}

export function usePriorityToggle(date: DateStr) {
  const data = useData();
  const plan = data.dayPlans.find((p) => p.date === date);
  const priorities = plan?.priorities ?? [];
  return {
    priorities,
    toggle: (taskId: string) => {
      if (priorities.includes(taskId)) return runSave(() => setDayPriorities(date, priorities.filter((p) => p !== taskId)));
      if (priorities.length >= 3) {
        void import("sonner").then(({ toast }) => toast.info("Ya tienes tres prioridades. Quita una para elegir otra."));
        return Promise.resolve(false);
      }
      return runSave(() => setDayPriorities(date, [...priorities, taskId]), "Agregada a tus prioridades del día");
    },
  };
}

