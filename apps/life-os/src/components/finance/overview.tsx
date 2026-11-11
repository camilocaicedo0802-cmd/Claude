"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowDownLeft, ArrowRight, ArrowUpRight, CalendarClock, CreditCard, Landmark, PiggyBank, Plus, Receipt, Target } from "lucide-react";
import { useCapacity, useCategoryMap, useData, useMoney, useToday } from "@/hooks/data";
import { budgetStatuses, expensesByCategory, pendingObligations, periodTotals } from "@/domain/finance";
import { addDays, endOfMonth, endOfWeek, startOfMonth } from "@/lib/dates";
import { sumMinor } from "@/lib/money";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/misc";
import { Card, CardHeader, EmptyState, MetricCard, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { SpendCapacityCard } from "./spend-card";
import { ObligationOccurrenceRow, TransactionRow } from "./rows";
import { CategoryBars } from "./charts";

export function FinanceOverview() {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const c = useCapacity();
  const cats = useCategoryMap();
  const { openForm } = useUI();

  const monthFrom = startOfMonth(today);
  const monthTo = endOfMonth(today);
  const month = periodTotals(data.transactions, monthFrom, monthTo);
  const pendingMonth = pendingObligations(data.obligations, data.transactions, monthTo, today);
  const committedMonth = sumMinor(pendingMonth.map((o) => o.remaining));
  const upcoming = pendingObligations(data.obligations, data.transactions, addDays(today, 30), today);
  const weekEnd = endOfWeek(today, data.settings.weekStartsOn);
  const groups = [
    { label: "Vencidas", items: upcoming.filter((o) => o.dueDate < today) },
    { label: "Esta semana", items: upcoming.filter((o) => o.dueDate >= today && o.dueDate <= weekEnd) },
    { label: "Próximos 7 días", items: upcoming.filter((o) => o.dueDate > weekEnd && o.dueDate <= addDays(today, 7)) },
    { label: "Más adelante (30 días)", items: upcoming.filter((o) => o.dueDate > addDays(today, 7) && o.dueDate > weekEnd) },
  ].filter((g) => g.items.length);
  const budgets = budgetStatuses(data.budgets, data.categories, data.transactions, today, today).slice(0, 5);
  const recent = [...data.transactions].sort((a, b) => b.date.localeCompare(a.date) || b.createdAt.localeCompare(a.createdAt)).slice(0, 7);
  const byCat = expensesByCategory(data.transactions, monthFrom, monthTo);
  const catRows = [...byCat.entries()]
    .map(([id, amount]) => {
      const cat = cats.get(id);
      return { id, amount, name: cat?.name ?? "Sin categoría", icon: cat?.icon ?? "circle-dashed", color: cat?.color ?? "slate" };
    })
    .sort((a, b) => b.amount - a.amount);
  const liquidAccounts = data.accounts.filter((a) => !a.archived && a.type !== "credit");

  return (
    <SectionPage
      section="finanzas"
      title="Finanzas"
      description="Tu dinero real, lo que debes y cuánto puedes gastar sin comprometer tus pagos."
      actions={
        <>
          <Button variant="outline" onClick={() => openForm({ kind: "transaction", defaults: { kind: "income" } })}>
            <ArrowDownLeft className="text-income" /> Ingreso
          </Button>
          <Button onClick={() => openForm({ kind: "transaction", defaults: { kind: "expense" } })}>
            <ArrowUpRight /> Registrar gasto
          </Button>
        </>
      }
    >
      <div className="grid gap-4 lg:grid-cols-3">
        <SpendCapacityCard className="lg:col-span-2" />
        <Card className="p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-[13px] font-medium text-muted-foreground">Saldo real</h2>
            <Link href="/finanzas/cuentas/" className="text-xs font-medium text-muted-foreground hover:text-foreground">
              Cuentas
            </Link>
          </div>
          <Money amount={c.realBalance} className={cn("mt-1 block text-[30px] leading-9 font-semibold tracking-tight", c.realBalance < 0 && "text-expense")} />
          <p className="text-xs text-muted-foreground">Efectivo y cuentas, sin cupos de crédito.</p>
          {liquidAccounts.length === 0 ? (
            <Button variant="outline" size="sm" className="mt-4" onClick={() => openForm({ kind: "account" })}>
              <Plus /> Agregar cuenta
            </Button>
          ) : (
            <dl className="mt-4 space-y-2 text-[13px]">
              <div className="flex justify-between gap-2">
                <dt className="flex items-center gap-1.5 text-muted-foreground">
                  <Landmark className="size-3.5" /> Para gastar
                </dt>
                <dd className="tabular font-medium">{money(c.balances.spendable)}</dd>
              </div>
              {c.balances.protectedSavings !== 0 && (
                <div className="flex justify-between gap-2">
                  <dt className="flex items-center gap-1.5 text-muted-foreground">
                    <PiggyBank className="size-3.5" /> Ahorros apartados
                  </dt>
                  <dd className="tabular font-medium">{money(c.balances.protectedSavings)}</dd>
                </div>
              )}
              {c.balances.creditDebt > 0 && (
                <div className="flex justify-between gap-2">
                  <dt className="flex items-center gap-1.5 text-muted-foreground">
                    <CreditCard className="size-3.5" /> Deuda en tarjetas
                  </dt>
                  <dd className="tabular font-medium text-expense">{money(-c.balances.creditDebt)}</dd>
                </div>
              )}
              <div className="mt-3 border-t border-border pt-3">
                <div className="flex justify-between gap-2">
                  <dt className="text-muted-foreground">Comprometido ({c.horizon.days} d)</dt>
                  <dd className="tabular font-medium">{money(c.committed)}</dd>
                </div>
                <div className="mt-2 flex justify-between gap-2">
                  <dt className="text-muted-foreground">Ingresos confirmados</dt>
                  <dd className="tabular font-medium text-income">{money(c.income.confirmed)}</dd>
                </div>
                <div className="mt-2 flex justify-between gap-2">
                  <dt className="text-muted-foreground">Ingresos inciertos</dt>
                  <dd className="tabular text-muted-foreground">{money(c.income.uncertain)}</dd>
                </div>
              </div>
            </dl>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard label="Ingresos del mes" value={<Money amount={month.income} />} hint="Dinero recibido, no facturado" icon={<ArrowDownLeft />} tone="income" href="/finanzas/movimientos/?tipo=income" />
        <MetricCard label="Gastos del mes" value={<Money amount={month.expense} />} hint={`Neto ${money(month.net, { signed: true })}`} icon={<ArrowUpRight />} tone="expense" href="/finanzas/movimientos/?tipo=expense" />
        <MetricCard label="Compromisos pendientes" value={<Money amount={committedMonth} />} hint={`${pendingMonth.length} pago(s) hasta fin de mes`} icon={<CalendarClock />} tone="warning" href="/finanzas/obligaciones/" />
        <MetricCard
          label="Proyección fin de mes"
          value={<Money amount={c.monthEnd.projected} className={c.monthEnd.projected < 0 ? "text-expense" : ""} />}
          hint="Estimado: saldo − pagos − esenciales + confirmados"
          icon={<Target />}
          tone="brand"
          href="/finanzas/analisis/"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader
            title="Próximos pagos"
            description="30 días. No se descuentan de tu saldo hasta pagarlos."
            action={
              <Button variant="ghost" size="sm" asChild>
                <Link href="/finanzas/obligaciones/">
                  Ver todos <ArrowRight />
                </Link>
              </Button>
            }
          />
          {groups.length === 0 ? (
            <EmptyState
              compact
              icon={<CalendarClock />}
              title="Sin pagos próximos"
              description="Registra arriendo, servicios, cuotas o suscripciones para reservarlos en tus proyecciones."
              action={
                <Button size="sm" variant="outline" onClick={() => openForm({ kind: "obligation" })}>
                  <Plus /> Nueva obligación
                </Button>
              }
            />
          ) : (
            <div className="px-2 pb-3 sm:px-3">
              {groups.map((g) => (
                <div key={g.label} className="mt-1">
                  <p className={cn("px-2 pt-2 text-xs font-semibold", g.label === "Vencidas" ? "text-expense" : "text-muted-foreground")}>
                    {g.label} · {money(sumMinor(g.items.map((i) => i.remaining)))}
                  </p>
                  <ul>
                    {g.items.slice(0, 5).map((o) => (
                      <ObligationOccurrenceRow key={o.key} occ={o} compact />
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <CardHeader
            title="Presupuestos del mes"
            action={
              <Button variant="ghost" size="sm" asChild>
                <Link href="/finanzas/presupuestos/">
                  Ver todos <ArrowRight />
                </Link>
              </Button>
            }
          />
          {budgets.length === 0 ? (
            <EmptyState
              compact
              icon={<Target />}
              title="Sin presupuestos"
              description="Define cuánto quieres gastar al mes en alimentación, transporte u ocio y te avisaremos al acercarte al límite."
              action={
                <Button size="sm" variant="outline" onClick={() => openForm({ kind: "budget" })}>
                  <Plus /> Crear presupuesto
                </Button>
              }
            />
          ) : (
            <ul className="space-y-4 px-4 pt-2 pb-5 sm:px-5">
              {budgets.map((b) => (
                <li key={b.budget.id}>
                  <button type="button" className="block w-full text-left" onClick={() => openForm({ kind: "budget", categoryId: b.budget.categoryId })}>
                    <div className="flex items-baseline justify-between gap-2 text-[13px]">
                      <span className="font-medium">{b.category?.name}</span>
                      <span className="text-muted-foreground tabular">
                        <span className={cn("font-medium", b.state === "over" ? "text-expense" : b.state === "near" ? "text-warning" : "text-foreground")}>{money(b.spent)}</span> de {money(b.budget.amount)}
                      </span>
                    </div>
                    <Progress className="mt-1.5" value={b.percent} tone={b.state === "over" ? "expense" : b.state === "near" ? "warning" : "income"} label={`${b.category?.name}: ${Math.round(b.percent)} %`} />
                    <p className="mt-1 text-xs text-muted-foreground">
                      {b.remaining >= 0 ? `Quedan ${money(b.remaining)}` : `Excedido por ${money(-b.remaining)}`}
                      {b.state !== "over" && b.projected > b.budget.amount && " · a este ritmo te pasarás"}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
        <Card>
          <CardHeader
            title="Movimientos recientes"
            action={
              <Button variant="ghost" size="sm" asChild>
                <Link href="/finanzas/movimientos/">
                  Historial <ArrowRight />
                </Link>
              </Button>
            }
          />
          {recent.length === 0 ? (
            <EmptyState compact icon={<Receipt />} title="Sin movimientos" description="Registra tu primer gasto con el botón «+»: valor, categoría y listo." />
          ) : (
            <ul className="px-2 pb-2 sm:px-3">
              {recent.map((t) => (
                <TransactionRow key={t.id} tx={t} showDate />
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <CardHeader
            title="¿En qué se va el dinero?"
            description="Gastos de este mes por categoría"
            action={
              <Button variant="ghost" size="sm" asChild>
                <Link href="/finanzas/analisis/">
                  Análisis <ArrowRight />
                </Link>
              </Button>
            }
          />
          <div className="px-4 pt-2 pb-5 sm:px-5">
            {catRows.length === 0 ? <p className="py-6 text-center text-[13px] text-muted-foreground">Aún no hay gastos este mes.</p> : <CategoryBars rows={catRows} total={month.expense} limit={6} />}
          </div>
        </Card>
      </div>
    </SectionPage>
  );
}
