"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Download } from "lucide-react";
import { useCapacity, useCategoryMap, useData, useFinanceInput, useMoney, useReceivablesByDate, useToday } from "@/hooks/data";
import { cashflowProjection, dailyExpenses, expensesByCategory, periodTotals } from "@/domain/finance";
import { addDays, addMonthKey, diffDays, eachDay, endOfMonth, endOfWeek, formatDateLong, formatMonthYear, startOfMonth, startOfWeek } from "@/lib/dates";
import { divideFloor, sumMinor, toMajor } from "@/lib/money";
import { cn, downloadFile, toCSV } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Chip, Segmented } from "@/components/ui/misc";
import { Card, CardHeader, MetricCard, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { CashflowChart, CategoryBars, DailySpendChart, IncomeExpenseChart } from "./charts";
import { RANGE_LABEL, rangeBounds } from "./movements";

type Range = "month" | "last-month" | "30" | "90" | "year";

export function AnalysisPage() {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const cats = useCategoryMap();
  const router = useRouter();
  const input = useFinanceInput();
  const capacity = useCapacity();
  const receivables = useReceivablesByDate();
  const [range, setRange] = React.useState<Range>("30");
  const [horizon, setHorizon] = React.useState<"30" | "60" | "90">("30");
  const { from, to: rawTo } = rangeBounds(range, today, { from: "", to: "" });
  const to = rawTo > today ? today : rawTo;

  const txs = data.transactions;
  const spentToday = periodTotals(txs, today, today).expense;
  const spentYesterday = periodTotals(txs, addDays(today, -1), addDays(today, -1)).expense;
  const weekFrom = startOfWeek(today, data.settings.weekStartsOn);
  const spentWeek = periodTotals(txs, weekFrom, today).expense;
  const spentMonth = periodTotals(txs, startOfMonth(today), today).expense;
  const rangeTotals = periodTotals(txs, from, to);
  const rangeDays = Math.max(1, diffDays(from, to) + 1);
  const firstTx = txs.reduce<string | null>((m, t) => (!m || t.date < m ? t.date : m), null);
  const effectiveDays = firstTx && firstTx > from ? Math.max(1, diffDays(firstTx, to) + 1) : rangeDays;
  const dailyAvg = divideFloor(rangeTotals.expense, effectiveDays);

  const daily = dailyExpenses(txs, from, to);
  const dailySeries = eachDay(from, to).map((d) => ({ date: d, amount: daily.get(d) ?? 0 }));
  const topDays = [...daily.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);

  const byCat = expensesByCategory(txs, from, to);
  const prevFrom = addDays(from, -rangeDays);
  const prevTo = addDays(from, -1);
  const prevByCat = expensesByCategory(txs, prevFrom, prevTo);
  const catRows = [...byCat.entries()]
    .map(([id, amount]) => {
      const c = cats.get(id);
      return { id, amount, previous: prevByCat.get(id) ?? 0, name: c?.name ?? "Sin categoría", icon: c?.icon ?? "circle-dashed", color: c?.color ?? "slate" };
    })
    .sort((a, b) => b.amount - a.amount);

  const months = Array.from({ length: 6 }, (_, i) => addMonthKey(today.slice(0, 7), i - 5));
  const monthly = months.map((m) => {
    const t = periodTotals(txs, `${m}-01`, endOfMonth(`${m}-01`));
    return { month: m, income: t.income, expense: t.expense };
  });

  // Month-over-month comparison per category (this month vs previous month, same number of days).
  const thisMonthFrom = startOfMonth(today);
  const elapsed = diffDays(thisMonthFrom, today);
  const lastMonthFrom = `${addMonthKey(today.slice(0, 7), -1)}-01`;
  const lastMonthSameDay = addDays(lastMonthFrom, Math.min(elapsed, diffDays(lastMonthFrom, endOfMonth(lastMonthFrom))));
  const cur = expensesByCategory(txs, thisMonthFrom, today);
  const prev = expensesByCategory(txs, lastMonthFrom, lastMonthSameDay);
  const comparison = [...new Set([...cur.keys(), ...prev.keys()])]
    .map((id) => ({ id, name: cats.get(id)?.name ?? "Sin categoría", cur: cur.get(id) ?? 0, prev: prev.get(id) ?? 0 }))
    .map((r) => ({ ...r, diff: r.cur - r.prev, pct: r.prev > 0 ? ((r.cur - r.prev) / r.prev) * 100 : null }))
    .sort((a, b) => b.diff - a.diff);
  const rising = comparison.filter((r) => r.diff > 0 && (r.pct === null || r.pct >= 15)).slice(0, 3);

  const essentialsDaily = capacity.horizon.days > 0 ? divideFloor(capacity.essentials.total, capacity.horizon.days) : 0;
  const projection = cashflowProjection(input, Number(horizon), essentialsDaily, receivables);
  const minPoint = projection.reduce((m, p) => (p.conservative < m.conservative ? p : m), projection[0]);

  const exportReport = () => {
    const rows: Array<Array<string | number>> = [["Reporte LIFE OS", `${from} a ${to}`], [], ["Indicador", "Valor"]];
    rows.push(["Ingresos", toMajor(rangeTotals.income)], ["Gastos", toMajor(rangeTotals.expense)], ["Neto", toMajor(rangeTotals.net)], ["Gasto diario promedio", toMajor(dailyAvg)], []);
    rows.push(["Categoría", "Gasto", "% del total", "Período anterior"]);
    for (const r of catRows) rows.push([r.name, toMajor(r.amount), Math.round((r.amount / Math.max(1, rangeTotals.expense)) * 1000) / 10, toMajor(r.previous)]);
    rows.push([], ["Mes", "Ingresos", "Gastos"]);
    for (const m of monthly) rows.push([m.month, toMajor(m.income), toMajor(m.expense)]);
    downloadFile(`reporte-${from}-${to}.csv`, toCSV(rows), "text/csv;charset=utf-8");
  };

  return (
    <SectionPage
      section="finanzas"
      title="Análisis"
      description="Patrones de gasto, comparaciones y proyección de flujo de caja."
      actions={
        <Button variant="outline" onClick={exportReport}>
          <Download /> Exportar reporte
        </Button>
      }
    >
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">
        <MetricCard label="Hoy" value={<Money amount={spentToday} />} hint="Gastado" />
        <MetricCard label="Ayer" value={<Money amount={spentYesterday} />} hint="Gastado" />
        <MetricCard label="Promedio diario" value={<Money amount={dailyAvg} />} hint={RANGE_LABEL[range]} />
        <MetricCard label="Esta semana" value={<Money amount={spentWeek} />} hint="Acumulado" />
        <MetricCard label="Este mes" value={<Money amount={spentMonth} />} hint="Acumulado" className="col-span-2 md:col-span-1" />
      </div>

      <div className="no-scrollbar -mx-4 flex gap-1.5 overflow-x-auto px-4 sm:mx-0 sm:px-0">
        {(["30", "month", "last-month", "90", "year"] as Range[]).map((r) => (
          <Chip key={r} active={range === r} onClick={() => setRange(r)}>
            {RANGE_LABEL[r]}
          </Chip>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
        <Card>
          <CardHeader title="Gasto diario" description={`${RANGE_LABEL[range]} · total ${money(rangeTotals.expense)}`} />
          <div className="px-2 pb-4 sm:px-4">
            {rangeTotals.expense === 0 ? <p className="py-16 text-center text-[13px] text-muted-foreground">Sin gastos en este período.</p> : <DailySpendChart data={dailySeries} average={dailyAvg} />}
          </div>
        </Card>
        <Card>
          <CardHeader title="Días con mayor gasto" />
          <ol className="space-y-1 px-4 pb-4 sm:px-5">
            {topDays.length === 0 && <li className="text-[13px] text-muted-foreground">Sin datos.</li>}
            {topDays.map(([d, amount], i) => (
              <li key={d}>
                <button type="button" onClick={() => router.push(`/finanzas/movimientos/`)} className="flex w-full items-center gap-3 rounded-lg py-1.5 text-left text-[13px] hover:bg-accent">
                  <span className="w-4 text-xs text-subtle tabular">{i + 1}</span>
                  <span className="min-w-0 flex-1 truncate first-letter:uppercase">{formatDateLong(d)}</span>
                  <Money amount={amount} className="font-medium" />
                </button>
              </li>
            ))}
          </ol>
          {rising.length > 0 && (
            <div className="mx-4 mb-4 rounded-lg bg-warning-soft p-3 text-[13px] text-warning sm:mx-5">
              <p className="font-semibold">Gastos en aumento este mes</p>
              <ul className="mt-1 space-y-0.5">
                {rising.map((r) => (
                  <li key={r.id}>
                    {r.name}: {money(r.cur)} vs {money(r.prev)} a esta altura del mes pasado
                    {r.pct !== null ? ` (+${Math.round(r.pct)} %)` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title="Distribución por categoría" description={`Comparado con los ${rangeDays} días anteriores`} />
          <div className="px-4 pb-5 sm:px-5">
            {catRows.length === 0 ? (
              <p className="py-8 text-center text-[13px] text-muted-foreground">Sin gastos en este período.</p>
            ) : (
              <CategoryBars rows={catRows} total={rangeTotals.expense} limit={10} onSelect={(id) => router.push(`/finanzas/movimientos/?categoria=${id}`)} />
            )}
          </div>
        </Card>
        <Card>
          <CardHeader title="Ingresos frente a gastos" description="Últimos 6 meses" />
          <div className="px-2 pb-4 sm:px-4">
            <IncomeExpenseChart data={monthly} />
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader
          title="Proyección de flujo de caja"
          description="Saldo disponible día a día restando pagos programados y gastos esenciales estimados."
          action={
            <Segmented
              size="sm"
              ariaLabel="Horizonte"
              value={horizon}
              onChange={setHorizon}
              options={[
                { value: "30", label: "30 d" },
                { value: "60", label: "60 d" },
                { value: "90", label: "90 d" },
              ]}
            />
          }
        />
        <div className="px-2 pb-4 sm:px-4">
          {capacity.status === "no-accounts" ? (
            <p className="py-12 text-center text-[13px] text-muted-foreground">Registra tus cuentas para proyectar tu flujo de caja.</p>
          ) : (
            <>
              <CashflowChart data={projection} />
              {minPoint && (
                <p className={cn("mt-3 px-2 text-[13px]", minPoint.conservative < 0 ? "text-expense" : "text-muted-foreground")}>
                  {minPoint.conservative < 0
                    ? `Sin contar ingresos, tu saldo quedaría negativo hacia el ${formatDateLong(minPoint.date)} (${money(minPoint.conservative)}).`
                    : `Punto más bajo sin contar ingresos: ${money(minPoint.conservative)} el ${formatDateLong(minPoint.date)}.`}{" "}
                  Esencial estimado: {money(essentialsDaily)}/día.
                </p>
              )}
            </>
          )}
        </div>
      </Card>

      <Card>
        <CardHeader title="Comparación mensual" description={`${formatMonthYear(today)} vs el mismo número de días del mes anterior`} />
        {comparison.length === 0 ? (
          <p className="px-5 pb-5 text-[13px] text-muted-foreground">Sin gastos para comparar.</p>
        ) : (
          <div className="overflow-x-auto px-4 pb-4 sm:px-5">
            <table className="w-full min-w-[420px] text-[13px]">
              <thead>
                <tr className="text-left text-xs text-muted-foreground">
                  <th className="py-2 font-medium">Categoría</th>
                  <th className="py-2 text-right font-medium">Mes pasado</th>
                  <th className="py-2 text-right font-medium">Este mes</th>
                  <th className="py-2 text-right font-medium">Cambio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {comparison.map((r) => (
                  <tr key={r.id}>
                    <td className="py-2">{r.name}</td>
                    <td className="py-2 text-right tabular text-muted-foreground">{money(r.prev)}</td>
                    <td className="py-2 text-right tabular font-medium">{money(r.cur)}</td>
                    <td className={cn("py-2 text-right tabular", r.diff > 0 ? "text-expense" : r.diff < 0 ? "text-income" : "text-muted-foreground")}>
                      {r.diff === 0 ? "—" : `${r.diff > 0 ? "+" : "−"}${money(Math.abs(r.diff))}`}
                      {r.pct !== null && r.diff !== 0 ? ` (${r.pct > 0 ? "+" : ""}${Math.round(r.pct)} %)` : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t border-border font-semibold">
                  <td className="py-2">Total</td>
                  <td className="py-2 text-right tabular">{money(sumMinor(comparison.map((r) => r.prev)))}</td>
                  <td className="py-2 text-right tabular">{money(sumMinor(comparison.map((r) => r.cur)))}</td>
                  <td className="py-2" />
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </Card>
      <p className="text-center text-xs text-muted-foreground">Semana actual: {weekFrom} a {endOfWeek(today, data.settings.weekStartsOn)}</p>
    </SectionPage>
  );
}
