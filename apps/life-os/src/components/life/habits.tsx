"use client";

import * as React from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Archive, Flame, Pencil, Plus, Sparkles, Trophy } from "lucide-react";
import { useData, useToday } from "@/hooks/data";
import type { Habit } from "@/db/types";
import { bestStreak, completionRate, currentStreak, isDone, isScheduled, logsIndex, scheduleLabel, weeklyTrend } from "@/domain/habits";
import { addDays, formatDateShort, formatDayMonth, orderedWeekdays, startOfWeek, WEEKDAY_LETTER, type DateStr } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, DynamicIcon, EmptyState, toneStyle } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { toggleHabit } from "@/services/life-service";
import { HabitCheckRow } from "./bits";

const WEEKS = 12;

export function HabitsPage() {
  const data = useData();
  const today = useToday();
  const { openForm } = useUI();
  const [showArchived, setShowArchived] = React.useState(false);
  const index = React.useMemo(() => logsIndex(data.habitLogs), [data.habitLogs]);
  const habits = data.habits.filter((h) => (showArchived ? h.archived : !h.archived));
  const scheduledToday = habits.filter((h) => !h.archived && isScheduled(h, today));
  const doneToday = scheduledToday.filter((h) => isDone(h, index, today)).length;
  const trend = React.useMemo(() => weeklyTrend(data.habits.filter((h) => !h.archived), index, today, data.settings.weekStartsOn, 8), [data.habits, index, today, data.settings.weekStartsOn]);
  const archivedCount = data.habits.filter((h) => h.archived).length;

  return (
    <SectionPage
      section="vida"
      title="Hábitos"
      description="Las rachas solo cuentan los días programados: descansar no te penaliza."
      actions={
        <Button onClick={() => openForm({ kind: "habit" })}>
          <Plus /> Hábito
        </Button>
      }
    >
      {data.habits.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Sparkles />}
            title="Empieza con un hábito pequeño"
            description="Hacer ejercicio de lunes a viernes, leer 20 minutos, tomar 8 vasos de agua… Márcalo con un toque cada día."
            action={
              <Button onClick={() => openForm({ kind: "habit" })}>
                <Plus /> Crear hábito
              </Button>
            }
          />
        </Card>
      ) : (
        <>
          <div className="grid gap-4 lg:grid-cols-[1fr_1.2fr]">
            <Card>
              <CardHeader title="Hoy" description={scheduledToday.length ? `${doneToday} de ${scheduledToday.length} completados` : "Nada programado hoy"} />
              <div className="space-y-2 px-3 pb-4 sm:px-4">
                {scheduledToday.length === 0 ? <p className="text-[13px] text-muted-foreground">Hoy es día de descanso para todos tus hábitos.</p> : scheduledToday.map((h) => <HabitCheckRow key={h.id} habit={h} date={today} />)}
              </div>
            </Card>
            <Card>
              <CardHeader title="Tendencia semanal" description="% de cumplimiento en días programados" />
              <div className="h-48 px-2 pb-3 sm:px-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trend.map((t) => ({ ...t, value: t.rate === null ? 0 : Math.round(t.rate) }))} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
                    <XAxis dataKey="weekStart" tickFormatter={(d: string) => formatDayMonth(d)} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} />
                    <YAxis domain={[0, 100]} ticks={[0, 50, 100]} tickFormatter={(v: number) => `${v}%`} tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} />
                    <Tooltip
                      cursor={{ fill: "var(--accent)" }}
                      content={({ active, payload }) =>
                        active && payload?.length ? (
                          <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-pop">
                            <p className="font-medium">Semana del {formatDateShort(String(payload[0].payload.weekStart))}</p>
                            <p className="text-muted-foreground">
                              {payload[0].payload.done} de {payload[0].payload.scheduled} · <span className="font-medium text-foreground">{payload[0].payload.value} %</span>
                            </p>
                          </div>
                        ) : null
                      }
                    />
                    <Bar dataKey="value" fill="var(--chart-1)" radius={[4, 4, 0, 0]} maxBarSize={30} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {habits.map((h) => (
              <HabitCard key={h.id} habit={h} />
            ))}
          </div>
          {archivedCount > 0 && (
            <div className="flex justify-center">
              <Button variant="ghost" size="sm" onClick={() => setShowArchived((v) => !v)}>
                <Archive /> {showArchived ? "Ver activos" : `Ver ${archivedCount} archivado(s)`}
              </Button>
            </div>
          )}
        </>
      )}
    </SectionPage>
  );
}

function HabitCard({ habit }: { habit: Habit }) {
  const data = useData();
  const today = useToday();
  const { openForm } = useUI();
  const index = React.useMemo(() => logsIndex(data.habitLogs), [data.habitLogs]);
  const streak = currentStreak(habit, index, today);
  const best = bestStreak(habit, index, today);
  const rate30 = completionRate(habit, index, addDays(today, -29), today);
  const ws = data.settings.weekStartsOn;
  const gridStart = addDays(startOfWeek(today, ws), -7 * (WEEKS - 1));
  const weeks = Array.from({ length: WEEKS }, (_, w) => Array.from({ length: 7 }, (_, d) => addDays(gridStart, w * 7 + d)));
  const cell = (d: DateStr) => {
    if (d > today) return "future";
    if (!isScheduled(habit, d)) return "off";
    return isDone(habit, index, d) ? "done" : d === today ? "pending" : "missed";
  };
  return (
    <Card className="p-4 sm:p-5" style={toneStyle(habit.color)}>
      <div className="flex items-start gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl tone-soft [&_svg]:size-5">
          <DynamicIcon name={habit.icon} />
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-[15px] font-semibold">{habit.name}</h3>
          <p className="text-xs text-muted-foreground">
            {scheduleLabel(habit)}
            {habit.target > 1 ? ` · ${habit.target} ${habit.unit ?? "veces"} al día` : ""}
          </p>
        </div>
        <Button variant="ghost" size="icon-sm" aria-label={`Editar ${habit.name}`} onClick={() => openForm({ kind: "habit", id: habit.id })}>
          <Pencil />
        </Button>
      </div>
      <dl className="mt-4 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-muted/60 py-2">
          <dt className="flex items-center justify-center gap-1 text-[11px] text-muted-foreground">
            <Flame className="size-3" /> Racha
          </dt>
          <dd className="text-lg font-semibold tabular">{streak}</dd>
        </div>
        <div className="rounded-lg bg-muted/60 py-2">
          <dt className="flex items-center justify-center gap-1 text-[11px] text-muted-foreground">
            <Trophy className="size-3" /> Mejor
          </dt>
          <dd className="text-lg font-semibold tabular">{best}</dd>
        </div>
        <div className="rounded-lg bg-muted/60 py-2">
          <dt className="text-[11px] text-muted-foreground">30 días</dt>
          <dd className="text-lg font-semibold tabular">{rate30.rate === null ? "—" : `${Math.round(rate30.rate)} %`}</dd>
        </div>
      </dl>
      <div className="mt-4 overflow-x-auto">
        <div className="inline-grid gap-[3px]" style={{ gridTemplateColumns: `14px repeat(${WEEKS}, 14px)`, gridTemplateRows: "repeat(7, 14px)", gridAutoFlow: "column" }} role="grid" aria-label={`Calendario de cumplimiento de ${habit.name}, últimas ${WEEKS} semanas`}>
          {orderedWeekdays(ws).map((d) => (
            <span key={`l${d}`} className="flex items-center justify-center text-[9px] text-subtle" aria-hidden>
              {WEEKDAY_LETTER[d]}
            </span>
          ))}
          {weeks.flat().map((d) => {
            const s = cell(d);
            return (
              <button
                key={d}
                type="button"
                disabled={s === "future" || s === "off"}
                onClick={() => runSave(() => toggleHabit(habit, d))}
                title={`${formatDateShort(d)}: ${s === "done" ? "cumplido" : s === "off" ? "no programado" : s === "future" ? "" : "sin cumplir"}`}
                aria-label={`${formatDateShort(d)}: ${s === "done" ? "cumplido" : s === "off" ? "no programado" : "sin cumplir"}`}
                className={cn(
                  "size-[14px] rounded-[3px] outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  s === "done" && "tone-dot",
                  s === "missed" && "bg-border",
                  s === "pending" && "border border-dashed border-[var(--tone)] bg-transparent",
                  s === "off" && "bg-transparent [background-image:repeating-linear-gradient(135deg,var(--border)_0_1px,transparent_1px_4px)]",
                  s === "future" && "bg-transparent",
                )}
              />
            );
          })}
        </div>
      </div>
      <p className="mt-2 text-[11px] text-subtle">Toca un día pasado para corregirlo. Las rayas son días no programados.</p>
    </Card>
  );
}
