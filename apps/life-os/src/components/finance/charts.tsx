"use client";

import * as React from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useMoney } from "@/hooks/data";
import { formatDayMonth, formatMonthShort, formatDateShort, type DateStr } from "@/lib/dates";
import type { Minor } from "@/lib/money";
import { cn } from "@/lib/utils";
import { ArrowDown, ArrowUp } from "lucide-react";
import { DynamicIcon, toneStyle } from "@/components/shared/primitives";

const axisTick = { fontSize: 11, fill: "var(--muted-foreground)" };

function TooltipBox({ title, rows }: { title: string; rows: Array<{ label: string; value: string; color?: string; dashed?: boolean }> }) {
  return (
    <div className="min-w-40 rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-pop">
      <p className="mb-1 font-medium text-foreground first-letter:uppercase">{title}</p>
      {rows.map((r) => (
        <p key={r.label} className="flex items-center justify-between gap-4 py-0.5">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            {r.color && <span className={cn("inline-block h-0.5 w-3 rounded-full", r.dashed && "border-t-2 border-dashed bg-transparent")} style={r.dashed ? { borderColor: r.color } : { background: r.color }} />}
            {r.label}
          </span>
          <span className="tabular font-medium text-foreground">{r.value}</span>
        </p>
      ))}
    </div>
  );
}

function Legend({ items }: { items: Array<{ label: string; color: string; dashed?: boolean }> }) {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
      {items.map((i) => (
        <li key={i.label} className="flex items-center gap-1.5">
          <span className={cn("inline-block h-2 w-3 rounded-[3px]", i.dashed && "h-0 rounded-none border-t-2 border-dashed")} style={i.dashed ? { borderColor: i.color } : { background: i.color }} aria-hidden />
          {i.label}
        </li>
      ))}
    </ul>
  );
}

const compactAxis = (fmt: (m: Minor, o?: { compact?: boolean }) => string) => (v: number) => fmt(v, { compact: true });

// ── Income vs expenses per month ─────────────────────────────────────────────

export function IncomeExpenseChart({ data }: { data: Array<{ month: string; income: Minor; expense: Minor }> }) {
  const money = useMoney();
  return (
    <div className="space-y-3">
      <Legend
        items={[
          { label: "Ingresos", color: "var(--chart-in)" },
          { label: "Gastos", color: "var(--chart-out)" },
        ]}
      />
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={2} barCategoryGap="28%" margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
            <XAxis dataKey="month" tickFormatter={(m: string) => formatMonthShort(`${m}-01`)} tick={axisTick} tickLine={false} axisLine={false} />
            <YAxis tickFormatter={compactAxis(money)} tick={axisTick} tickLine={false} axisLine={false} width={64} />
            <Tooltip
              cursor={{ fill: "var(--accent)" }}
              content={({ active, payload, label }) =>
                active && payload?.length ? (
                  <TooltipBox
                    title={formatMonthShort(`${label}-01`) + " " + String(label).slice(0, 4)}
                    rows={[
                      { label: "Ingresos", value: money(Number(payload[0]?.payload.income)), color: "var(--chart-in)" },
                      { label: "Gastos", value: money(Number(payload[0]?.payload.expense)), color: "var(--chart-out)" },
                      { label: "Neto", value: money(Number(payload[0]?.payload.income) - Number(payload[0]?.payload.expense), { signed: true }) },
                    ]}
                  />
                ) : null
              }
            />
            <Bar dataKey="income" name="Ingresos" fill="var(--chart-in)" radius={[4, 4, 0, 0]} maxBarSize={28} />
            <Bar dataKey="expense" name="Gastos" fill="var(--chart-out)" radius={[4, 4, 0, 0]} maxBarSize={28} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ── Daily spending ───────────────────────────────────────────────────────────

export function DailySpendChart({ data, average }: { data: Array<{ date: DateStr; amount: Minor }>; average?: Minor }) {
  const money = useMoney();
  return (
    <div className="h-52">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 4, left: 4, bottom: 0 }} barCategoryGap={data.length > 40 ? 1 : "18%"}>
          <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
          <XAxis dataKey="date" tickFormatter={(d: string) => formatDayMonth(d)} tick={axisTick} tickLine={false} axisLine={false} minTickGap={24} />
          <YAxis tickFormatter={compactAxis(money)} tick={axisTick} tickLine={false} axisLine={false} width={64} />
          {average !== undefined && average > 0 && (
            <ReferenceLine y={average} stroke="var(--chart-neutral)" strokeDasharray="4 4" label={{ value: "Promedio", position: "insideTopRight", fontSize: 11, fill: "var(--muted-foreground)" }} />
          )}
          <Tooltip
            cursor={{ fill: "var(--accent)" }}
            content={({ active, payload }) =>
              active && payload?.length ? (
                <TooltipBox title={formatDateShort(String(payload[0].payload.date))} rows={[{ label: "Gastado", value: money(Number(payload[0].payload.amount)), color: "var(--chart-1)" }]} />
              ) : null
            }
          />
          <Bar dataKey="amount" fill="var(--chart-1)" radius={[4, 4, 0, 0]} maxBarSize={22} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// ── Cash-flow projection ─────────────────────────────────────────────────────

export function CashflowChart({ data }: { data: Array<{ date: DateStr; conservative: Minor; withConfirmed: Minor; optimistic: Minor }> }) {
  const money = useMoney();
  const showOptimistic = data.some((d) => d.optimistic !== d.withConfirmed);
  const showConfirmed = data.some((d) => d.withConfirmed !== d.conservative);
  const legend = [
    { label: "Solo lo que tienes", color: "var(--chart-1)" },
    ...(showConfirmed ? [{ label: "+ ingresos confirmados", color: "var(--chart-2)" }] : []),
    ...(showOptimistic ? [{ label: "+ ingresos inciertos", color: "var(--chart-neutral)", dashed: true }] : []),
  ];
  return (
    <div className="space-y-3">
      {legend.length > 1 && <Legend items={legend} />}
      <div className="h-60">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: 4, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
            <XAxis dataKey="date" tickFormatter={(d: string) => formatDayMonth(d)} tick={axisTick} tickLine={false} axisLine={false} minTickGap={28} />
            <YAxis tickFormatter={compactAxis(money)} tick={axisTick} tickLine={false} axisLine={false} width={64} />
            <ReferenceLine y={0} stroke="var(--expense)" strokeOpacity={0.6} />
            <Tooltip
              cursor={{ stroke: "var(--border-strong)" }}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const p = payload[0].payload as { date: string; conservative: number; withConfirmed: number; optimistic: number };
                return (
                  <TooltipBox
                    title={formatDateShort(p.date)}
                    rows={[
                      { label: "Solo lo que tienes", value: money(p.conservative), color: "var(--chart-1)" },
                      ...(showConfirmed ? [{ label: "+ confirmados", value: money(p.withConfirmed), color: "var(--chart-2)" }] : []),
                      ...(showOptimistic ? [{ label: "+ inciertos", value: money(p.optimistic), color: "var(--chart-neutral)", dashed: true }] : []),
                    ]}
                  />
                );
              }}
            />
            {showOptimistic && <Line type="stepAfter" dataKey="optimistic" stroke="var(--chart-neutral)" strokeWidth={2} strokeDasharray="5 4" dot={false} activeDot={{ r: 4 }} />}
            {showConfirmed && <Line type="stepAfter" dataKey="withConfirmed" stroke="var(--chart-2)" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />}
            <Line type="stepAfter" dataKey="conservative" stroke="var(--chart-1)" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ── Category bars (HTML) ─────────────────────────────────────────────────────

export function CategoryBars({
  rows,
  total,
  onSelect,
  limit = 8,
}: {
  rows: Array<{ id: string; name: string; icon: string; color: string; amount: Minor; previous?: Minor }>;
  total: Minor;
  onSelect?: (id: string) => void;
  limit?: number;
}) {
  const money = useMoney();
  const max = Math.max(1, ...rows.map((r) => r.amount));
  return (
    <ul className="space-y-2.5">
      {rows.slice(0, limit).map((r) => {
        const pct = total > 0 ? (r.amount / total) * 100 : 0;
        const change = r.previous !== undefined && r.previous > 0 ? ((r.amount - r.previous) / r.previous) * 100 : null;
        const Body = (
          <>
            <div className="flex items-center gap-2 text-[13px]">
              <span style={toneStyle(r.color)} className="tone-text [&_svg]:size-3.5">
                <DynamicIcon name={r.icon} />
              </span>
              <span className="min-w-0 flex-1 truncate">{r.name}</span>
              {change !== null && Math.abs(change) >= 10 && (
                <span className={cn("inline-flex items-center gap-0.5 text-xs tabular", change > 0 ? "text-expense" : "text-income")} aria-label={change > 0 ? "Aumentó" : "Disminuyó"}>
                  {change > 0 ? <ArrowUp className="size-3" /> : <ArrowDown className="size-3" />}
                  {Math.abs(Math.round(change))} %
                </span>
              )}
              <span className="tabular font-medium">{money(r.amount)}</span>
              <span className="w-10 text-right text-xs text-muted-foreground tabular">{Math.round(pct)} %</span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full bg-muted">
              <div className="h-full rounded-full bg-chart-1" style={{ width: `${(r.amount / max) * 100}%` }} />
            </div>
          </>
        );
        return (
          <li key={r.id}>
            {onSelect ? (
              <button type="button" className="block w-full rounded-md text-left outline-none focus-visible:ring-2 focus-visible:ring-ring" onClick={() => onSelect(r.id)}>
                {Body}
              </button>
            ) : (
              Body
            )}
          </li>
        );
      })}
    </ul>
  );
}
