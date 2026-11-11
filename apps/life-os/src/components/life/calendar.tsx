"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { useData, useJobViews, useNow, useToday } from "@/hooks/data";
import { buildAgenda, EVENT_CATEGORY_LABEL, EVENT_COLORS, type AgendaItem } from "@/domain/agenda";
import {
  addDays,
  addMonthKey,
  eachDay,
  endOfMonth,
  endOfWeek,
  formatDateLong,
  formatDayMonth,
  formatMonthYear,
  minutesToTime,
  orderedWeekdays,
  startOfWeek,
  timeToMinutes,
  WEEKDAY_SHORT,
  weekday,
  type DateStr,
} from "@/lib/dates";
import { cn } from "@/lib/utils";
import { useIsDesktop } from "@/hooks/use-media";
import { Button } from "@/components/ui/button";
import { Segmented } from "@/components/ui/misc";
import { Card, toneStyle } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { AgendaRow, useAgendaOpener } from "./bits";

type View = "month" | "week" | "day";
const START_HOUR = 6;
const END_HOUR = 23;
const HOUR_PX = 52;

function useAgendaRange(from: DateStr, to: DateStr) {
  const data = useData();
  const today = useToday();
  const views = useJobViews();
  return React.useMemo(
    () =>
      buildAgenda({
        from,
        to,
        today,
        events: data.events,
        tasks: data.tasks,
        jobViews: views,
        obligations: data.obligations,
        plannedIncomes: data.plannedIncomes,
        transactions: data.transactions,
        clients: data.clients,
      }),
    [data, views, from, to, today],
  );
}

export function CalendarPage() {
  const data = useData();
  const today = useToday();
  const desktop = useIsDesktop();
  const { openForm } = useUI();
  const [view, setView] = React.useState<View>("week");
  const [cursor, setCursor] = React.useState<DateStr>(today);
  const ws = data.settings.weekStartsOn;

  const range =
    view === "month"
      ? { from: startOfWeek(`${cursor.slice(0, 7)}-01`, ws), to: endOfWeek(endOfMonth(cursor), ws) }
      : view === "week"
        ? { from: startOfWeek(cursor, ws), to: endOfWeek(cursor, ws) }
        : { from: cursor, to: cursor };
  const items = useAgendaRange(range.from, range.to);

  const move = (dir: -1 | 1) => {
    if (view === "month") setCursor(`${addMonthKey(cursor.slice(0, 7), dir)}-01`);
    else if (view === "week") setCursor(addDays(cursor, 7 * dir));
    else setCursor(addDays(cursor, dir));
  };
  const title = view === "month" ? formatMonthYear(cursor) : view === "week" ? `${formatDayMonth(range.from)} – ${formatDayMonth(range.to)}` : formatDateLong(cursor);

  return (
    <SectionPage
      section="vida"
      title="Calendario"
      description="Eventos, tareas con hora, entregas de clientes y pagos en un solo lugar."
      actions={
        <Button onClick={() => openForm({ kind: "event", defaults: { date: view === "day" ? cursor : today } })}>
          <Plus /> Evento
        </Button>
      }
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm" onClick={() => setCursor(today)}>
            Hoy
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Anterior" onClick={() => move(-1)}>
            <ChevronLeft />
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Siguiente" onClick={() => move(1)}>
            <ChevronRight />
          </Button>
          <h2 className="ml-1 text-sm font-semibold first-letter:uppercase sm:text-[15px]">{title}</h2>
        </div>
        <Segmented
          ariaLabel="Vista del calendario"
          size="sm"
          value={view}
          onChange={setView}
          options={[
            { value: "day", label: "Día" },
            { value: "week", label: "Semana" },
            { value: "month", label: "Mes" },
          ]}
        />
      </div>

      {view === "month" ? (
        <MonthView month={cursor.slice(0, 7)} from={range.from} to={range.to} items={items} onPickDay={(d) => { setCursor(d); setView("day"); }} />
      ) : view === "week" ? (
        desktop ? (
          <TimeGrid days={eachDay(range.from, range.to)} items={items} />
        ) : (
          <WeekList days={eachDay(range.from, range.to)} items={items} onPickDay={(d) => { setCursor(d); setView("day"); }} />
        )
      ) : (
        <TimeGrid days={[cursor]} items={items} />
      )}

      <ul className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-muted-foreground" aria-label="Colores">
        {Object.entries(EVENT_COLORS).map(([k, c]) => (
          <li key={k} className="flex items-center gap-1.5">
            <span className="size-2 rounded-full tone-dot" style={toneStyle(c)} /> {EVENT_CATEGORY_LABEL[k as keyof typeof EVENT_CATEGORY_LABEL]}
          </li>
        ))}
        <li className="flex items-center gap-1.5">
          <span className="size-2 rounded-full tone-dot" style={toneStyle("amber")} /> Pagos
        </li>
        <li className="flex items-center gap-1.5">
          <span className="size-2 rounded-full tone-dot" style={toneStyle("emerald")} /> Ingresos y cobros
        </li>
      </ul>
    </SectionPage>
  );
}

function Pill({ item, onClick }: { item: AgendaItem; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      style={toneStyle(item.color)}
      className={cn("block w-full truncate rounded px-1.5 py-0.5 text-left text-[11px] leading-4 font-medium tone-soft", item.done && "line-through opacity-60", item.projected && "opacity-60", item.kind === "task" && "bg-transparent text-muted-foreground")}
      title={item.title}
    >
      {item.time && <span className="tabular">{item.time} </span>}
      {item.title}
    </button>
  );
}

function MonthView({ month, from, to, items, onPickDay }: { month: string; from: DateStr; to: DateStr; items: AgendaItem[]; onPickDay: (d: DateStr) => void }) {
  const data = useData();
  const today = useToday();
  const open = useAgendaOpener();
  const { openForm } = useUI();
  const days = eachDay(from, to);
  return (
    <Card className="overflow-hidden">
      <div className="grid grid-cols-7 border-b border-border bg-muted/50">
        {orderedWeekdays(data.settings.weekStartsOn).map((d) => (
          <div key={d} className="py-2 text-center text-[11px] font-medium text-muted-foreground">
            {WEEKDAY_SHORT[d]}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7">
        {days.map((d) => {
          const list = items.filter((i) => i.date === d);
          const inMonth = d.startsWith(month);
          const busy = list.filter((i) => !i.done).length;
          return (
            <div
              key={d}
              role="button"
              tabIndex={0}
              aria-label={`${formatDateLong(d)}: ${busy} elementos`}
              onClick={() => onPickDay(d)}
              onKeyDown={(e) => e.key === "Enter" && onPickDay(d)}
              onDoubleClick={() => openForm({ kind: "event", defaults: { date: d } })}
              className={cn(
                "group min-h-[72px] cursor-pointer border-r border-b border-border p-1 outline-none hover:bg-accent/40 focus-visible:bg-accent/60 sm:min-h-[112px] sm:p-1.5 [&:nth-child(7n)]:border-r-0",
                !inMonth && "bg-muted/30",
              )}
            >
              <div className="mb-1 flex items-center justify-between">
                <span className={cn("flex size-6 items-center justify-center rounded-full text-xs tabular", d === today ? "bg-brand font-semibold text-brand-foreground" : inMonth ? "" : "text-subtle")}>{Number(d.slice(8))}</span>
                {busy > 0 && <span className="text-[10px] text-muted-foreground tabular sm:hidden">{busy}</span>}
              </div>
              <div className="hidden space-y-0.5 sm:block">
                {list.slice(0, 3).map((i) => (
                  <Pill key={i.key} item={i} onClick={() => open(i)} />
                ))}
                {list.length > 3 && <p className="px-1.5 text-[11px] text-muted-foreground">+{list.length - 3} más</p>}
              </div>
              {busy > 0 && (
                <div className="flex flex-wrap gap-0.5 sm:hidden" aria-hidden>
                  {list.slice(0, 4).map((i) => (
                    <span key={i.key} className="size-1.5 rounded-full tone-dot" style={toneStyle(i.color)} />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

function WeekList({ days, items, onPickDay }: { days: DateStr[]; items: AgendaItem[]; onPickDay: (d: DateStr) => void }) {
  const today = useToday();
  const { openForm } = useUI();
  return (
    <div className="space-y-3">
      {days.map((d) => {
        const list = items.filter((i) => i.date === d);
        return (
          <Card key={d} className={cn(d === today && "ring-1 ring-brand/40")}>
            <div className="flex items-center justify-between px-4 pt-3">
              <button type="button" onClick={() => onPickDay(d)} className={cn("text-[13px] font-semibold first-letter:uppercase", d === today && "text-brand")}>
                {d === today ? "Hoy · " : ""}
                {formatDateLong(d)}
              </button>
              <Button variant="ghost" size="icon-sm" aria-label="Agregar evento este día" onClick={() => openForm({ kind: "event", defaults: { date: d } })}>
                <Plus />
              </Button>
            </div>
            <div className="px-2 pb-2">{list.length === 0 ? <p className="px-2 pb-2 text-xs text-subtle">Libre</p> : list.map((i) => <AgendaRow key={i.key} item={i} />)}</div>
          </Card>
        );
      })}
    </div>
  );
}

/** Lays out overlapping timed items in side-by-side lanes. */
function layoutDay(items: AgendaItem[]) {
  const timed = items
    .filter((i) => i.time)
    .map((i) => {
      const start = timeToMinutes(i.time!);
      const end = i.endTime ? timeToMinutes(i.endTime) : start + Math.max(30, i.durationMin || 30);
      return { item: i, start, end: Math.max(end, start + 20) };
    })
    .sort((a, b) => a.start - b.start);
  const lanes: number[] = [];
  const placed = timed.map((t) => {
    let lane = lanes.findIndex((endAt) => endAt <= t.start);
    if (lane === -1) {
      lane = lanes.length;
      lanes.push(t.end);
    } else lanes[lane] = t.end;
    return { ...t, lane };
  });
  return { placed, laneCount: Math.max(1, lanes.length) };
}

function TimeGrid({ days, items }: { days: DateStr[]; items: AgendaItem[] }) {
  const today = useToday();
  const open = useAgendaOpener();
  const { openForm } = useUI();
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const hours = Array.from({ length: END_HOUR - START_HOUR + 1 }, (_, i) => START_HOUR + i);
  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: (8 - START_HOUR) * HOUR_PX });
  }, []);
  const now = useNow();
  const nowMinutes = timeToMinutes(now.time);
  const single = days.length === 1;
  return (
    <Card className="overflow-hidden">
      <div className="grid border-b border-border" style={{ gridTemplateColumns: `56px repeat(${days.length}, minmax(0, 1fr))` }}>
        <div />
        {days.map((d) => (
          <div key={d} className={cn("border-l border-border px-2 py-2 text-center", d === today && "bg-brand-soft/50")}>
            <div className="text-[11px] font-medium text-muted-foreground uppercase">{WEEKDAY_SHORT[weekday(d)]}</div>
            <div className={cn("text-lg leading-6 font-semibold tabular", d === today && "text-brand")}>{Number(d.slice(8))}</div>
          </div>
        ))}
      </div>
      {/* All-day lane: deliveries, payments, untimed tasks and all-day events. */}
      <div className="grid border-b border-border bg-muted/30" style={{ gridTemplateColumns: `56px repeat(${days.length}, minmax(0, 1fr))` }}>
        <div className="px-1.5 py-1.5 text-right text-[10px] leading-tight text-muted-foreground">Todo el día</div>
        {days.map((d) => {
          const list = items.filter((i) => i.date === d && !i.time);
          return (
            <div key={d} className={cn("min-h-8 space-y-0.5 border-l border-border p-1", single && "space-y-1 p-2")}>
              {single ? list.map((i) => <AgendaRow key={i.key} item={i} />) : list.slice(0, 4).map((i) => <Pill key={i.key} item={i} onClick={() => open(i)} />)}
              {!single && list.length > 4 && <p className="px-1 text-[10px] text-muted-foreground">+{list.length - 4}</p>}
            </div>
          );
        })}
      </div>
      <div ref={scrollRef} className="relative max-h-[60vh] overflow-y-auto">
        <div className="grid" style={{ gridTemplateColumns: `56px repeat(${days.length}, minmax(0, 1fr))` }}>
          <div>
            {hours.map((h) => (
              <div key={h} className="relative pr-2 text-right text-[10px] text-muted-foreground tabular" style={{ height: HOUR_PX }}>
                <span className="relative -top-1.5">{`${String(h).padStart(2, "0")}:00`}</span>
              </div>
            ))}
          </div>
          {days.map((d) => {
            const { placed, laneCount } = layoutDay(items.filter((i) => i.date === d));
            return (
              <div
                key={d}
                className="relative border-l border-border"
                style={{ height: hours.length * HOUR_PX }}
                onClick={(e) => {
                  const rect = (e.currentTarget as HTMLDivElement).getBoundingClientRect();
                  const minutes = START_HOUR * 60 + Math.floor(((e.clientY - rect.top) / HOUR_PX) * 2) * 30;
                  openForm({ kind: "event", defaults: { date: d, startTime: minutesToTime(minutes), endTime: minutesToTime(minutes + 60), allDay: false } });
                }}
              >
                {hours.map((h) => (
                  <div key={h} className="pointer-events-none border-b border-border/60" style={{ height: HOUR_PX }} />
                ))}
                {d === today && nowMinutes >= START_HOUR * 60 && nowMinutes <= (END_HOUR + 1) * 60 && (
                  <div className="pointer-events-none absolute right-0 left-0 z-10 h-px bg-expense" style={{ top: ((nowMinutes - START_HOUR * 60) / 60) * HOUR_PX }}>
                    <span className="absolute -top-1 -left-1 size-2 rounded-full bg-expense" />
                  </div>
                )}
                {placed.map(({ item, start, end, lane }) => {
                  const top = Math.max(0, ((start - START_HOUR * 60) / 60) * HOUR_PX);
                  const height = Math.max(20, ((end - start) / 60) * HOUR_PX - 2);
                  return (
                    <button
                      key={item.key}
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        open(item);
                      }}
                      style={{ ...toneStyle(item.color), top, height, left: `calc(${(lane / laneCount) * 100}% + 2px)`, width: `calc(${100 / laneCount}% - 4px)` }}
                      className={cn(
                        "absolute z-[5] flex flex-col items-stretch justify-start overflow-hidden rounded-md px-1.5 py-1 text-left text-[11px] leading-tight tone-soft ring-1 ring-card",
                        item.done && "opacity-50",
                        item.projected && "opacity-60",
                      )}
                    >
                      <span className={cn("block truncate font-semibold", item.done && "line-through")}>{item.title}</span>
                      {height > 30 && <span className="block truncate opacity-80 tabular">{item.time}{item.endTime ? `–${item.endTime}` : ""}</span>}
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
