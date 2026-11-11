"use client";

import * as React from "react";
import { CalendarClock, ChevronLeft, ChevronRight, LayoutList, CalendarDays, Plus, Repeat, TrendingUp } from "lucide-react";
import { useData, useMoney, useToday } from "@/hooks/data";
import { obligationOccurrences, pendingObligations, plannedIncomeOccurrences } from "@/domain/finance";
import { addDays, addMonthKey, eachDay, endOfMonth, endOfWeek, formatMonthYear, orderedWeekdays, startOfMonth, startOfWeek, WEEKDAY_SHORT } from "@/lib/dates";
import { sumMinor } from "@/lib/money";
import { describeRecurrence, nextOccurrence } from "@/lib/recurrence";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge, Segmented } from "@/components/ui/misc";
import { Card, CardHeader, EmptyState, MetricCard, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { OBLIGATION_TYPE_LABEL } from "@/components/forms/finance-forms";
import { ObligationOccurrenceRow, PlannedIncomeRow } from "./rows";

export function ObligationsPage() {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { openForm } = useUI();
  const [view, setView] = React.useState<"list" | "calendar">("list");
  const [month, setMonth] = React.useState(today.slice(0, 7));

  const weekEnd = endOfWeek(today, data.settings.weekStartsOn);
  const monthEnd = endOfMonth(today);
  const pending = pendingObligations(data.obligations, data.transactions, addDays(today, 60), today);
  const overdue = pending.filter((o) => o.dueDate < today);
  const thisWeek = pending.filter((o) => o.dueDate >= today && o.dueDate <= weekEnd);
  const next7 = pending.filter((o) => o.dueDate >= today && o.dueDate <= addDays(today, 7));
  const restMonth = pending.filter((o) => o.dueDate >= today && o.dueDate <= monthEnd);
  const later = pending.filter((o) => o.dueDate > weekEnd);
  const incomes = plannedIncomeOccurrences(data.plannedIncomes, data.transactions, addDays(today, -7), addDays(today, 60), today).filter((o) => o.remaining > 0 || o.dueDate >= today);
  const subscriptions = data.obligations.filter((o) => o.active && o.type === "subscription");
  const monthlySubs = sumMinor(
    subscriptions.map((o) => {
      const r = o.recurrence;
      if (!r) return 0;
      if (r.freq === "monthly") return Math.round(o.amount / r.interval);
      if (r.freq === "yearly") return Math.round(o.amount / (12 * r.interval));
      if (r.freq === "weekly") return Math.round((o.amount * 52) / 12 / r.interval);
      return o.amount * 30;
    }),
  );

  return (
    <SectionPage
      section="finanzas"
      title="Pagos y obligaciones"
      description="Lo que debes pagar y lo que esperas recibir. Se reserva en tus proyecciones sin tocar tu saldo real."
      actions={
        <>
          <Button variant="outline" onClick={() => openForm({ kind: "plannedIncome" })}>
            <TrendingUp /> Ingreso previsto
          </Button>
          <Button onClick={() => openForm({ kind: "obligation" })}>
            <Plus /> Obligación
          </Button>
        </>
      }
    >
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard label="Vencidas" value={<Money amount={sumMinor(overdue.map((o) => o.remaining))} className={overdue.length ? "text-expense" : ""} />} hint={`${overdue.length} sin pagar`} />
        <MetricCard label="Esta semana" value={<Money amount={sumMinor(thisWeek.map((o) => o.remaining))} />} hint={`${thisWeek.length} pago(s)`} />
        <MetricCard label="Próximos 7 días" value={<Money amount={sumMinor(next7.map((o) => o.remaining))} />} hint={`${next7.length} pago(s)`} />
        <MetricCard label="Resto del mes" value={<Money amount={sumMinor(restMonth.map((o) => o.remaining))} />} hint={`${restMonth.length} pago(s) hasta fin de mes`} />
      </div>

      <div className="flex items-center justify-between gap-2">
        <Segmented
          ariaLabel="Vista"
          value={view}
          onChange={setView}
          options={[
            { value: "list", label: "Lista", icon: <LayoutList /> },
            { value: "calendar", label: "Calendario", icon: <CalendarDays /> },
          ]}
        />
      </div>

      {view === "list" ? (
        <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <Card>
            <CardHeader title="Por pagar" description="Próximos 60 días, incluye vencidas" />
            {pending.length === 0 ? (
              <EmptyState
                compact
                icon={<CalendarClock />}
                title="No tienes pagos pendientes"
                description="Agrega arriendo, servicios, préstamos, tarjetas, suscripciones o cualquier compromiso. Admite pagos parciales y recurrencia."
                action={
                  <Button size="sm" onClick={() => openForm({ kind: "obligation" })}>
                    <Plus /> Nueva obligación
                  </Button>
                }
              />
            ) : (
              <div className="px-1 pb-2 sm:px-2">
                {[
                  { label: "Vencidas", items: overdue },
                  { label: "Esta semana", items: thisWeek },
                  { label: "Después", items: later },
                ]
                  .filter((g) => g.items.length)
                  .map((g) => (
                    <div key={g.label}>
                      <p className={cn("px-3 pt-3 text-xs font-semibold", g.label === "Vencidas" ? "text-expense" : "text-muted-foreground")}>
                        {g.label} · {money(sumMinor(g.items.map((i) => i.remaining)))}
                      </p>
                      <ul>
                        {g.items.map((o) => (
                          <ObligationOccurrenceRow key={o.key} occ={o} />
                        ))}
                      </ul>
                    </div>
                  ))}
              </div>
            )}
          </Card>
          <div className="space-y-4">
            <Card>
              <CardHeader
                title="Ingresos previstos"
                description="Nunca cuentan como disponibles hasta recibirlos"
                action={
                  <Button variant="ghost" size="sm" onClick={() => openForm({ kind: "plannedIncome" })}>
                    <Plus /> Nuevo
                  </Button>
                }
              />
              {incomes.length === 0 ? (
                <p className="px-5 pb-5 text-[13px] text-muted-foreground">Registra tu salario u otros ingresos fijos: así el cálculo de gasto sabe cuándo llega tu próximo ingreso.</p>
              ) : (
                <ul className="px-1 pb-2 sm:px-2">
                  {incomes.slice(0, 6).map((o) => (
                    <PlannedIncomeRow key={o.key} occ={o} />
                  ))}
                </ul>
              )}
            </Card>
            <Card>
              <CardHeader title="Suscripciones" description={subscriptions.length ? `${money(monthlySubs)} al mes en total` : undefined} icon={<Repeat />} />
              {subscriptions.length === 0 ? (
                <p className="px-5 pb-5 text-[13px] text-muted-foreground">Registra tus suscripciones como obligaciones de tipo «Suscripción» para ver cuánto suman.</p>
              ) : (
                <ul className="px-3 pb-3">
                  {subscriptions.map((o) => (
                    <li key={o.id}>
                      <button type="button" onClick={() => openForm({ kind: "obligation", id: o.id })} className="flex w-full items-center justify-between gap-2 rounded-lg px-2 py-2 text-left text-sm hover:bg-accent">
                        <span className="truncate">{o.name}</span>
                        <span className="text-xs text-muted-foreground">{describeRecurrence(o.recurrence)}</span>
                        <Money amount={o.amount} className="font-medium" />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </div>
      ) : (
        <PaymentsCalendar month={month} setMonth={setMonth} />
      )}

      <Card>
        <CardHeader title="Obligaciones registradas" description="Cada obligación recurrente es un solo registro; sus vencimientos se calculan sin duplicados." />
        {data.obligations.length === 0 ? (
          <p className="px-5 pb-5 text-[13px] text-muted-foreground">Aún no hay obligaciones.</p>
        ) : (
          <ul className="divide-y divide-border px-2 pb-2 sm:px-3">
            {data.obligations
              .slice()
              .sort((a, b) => Number(b.active) - Number(a.active) || a.name.localeCompare(b.name))
              .map((o) => {
                const next = nextOccurrence(o.startDate, o.recurrence, today);
                const account = data.accounts.find((a) => a.id === o.accountId);
                return (
                  <li key={o.id}>
                    <button type="button" onClick={() => openForm({ kind: "obligation", id: o.id })} className={cn("flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left hover:bg-accent", !o.active && "opacity-60")}>
                      <span className="min-w-0 flex-1">
                        <span className="flex items-center gap-2">
                          <span className="truncate text-sm font-medium">{o.name}</span>
                          {!o.active && <Badge tone="outline">Pausada</Badge>}
                        </span>
                        <span className="block truncate text-xs text-muted-foreground">
                          {OBLIGATION_TYPE_LABEL[o.type]} · {o.recurrence ? describeRecurrence(o.recurrence) : "Una vez"}
                          {next ? ` · próximo ${next.slice(8)}/${next.slice(5, 7)}` : " · finalizada"}
                          {account ? ` · desde ${account.name}` : ""}
                        </span>
                      </span>
                      <Money amount={o.amount} className="text-sm font-semibold" />
                    </button>
                  </li>
                );
              })}
          </ul>
        )}
      </Card>
    </SectionPage>
  );
}

function PaymentsCalendar({ month, setMonth }: { month: string; setMonth: (m: string) => void }) {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { openForm } = useUI();
  const ws = data.settings.weekStartsOn;
  const from = startOfWeek(`${month}-01`, ws);
  const to = endOfWeek(endOfMonth(`${month}-01`), ws);
  const occ = obligationOccurrences(data.obligations, data.transactions, from, to, today).filter((o) => o.status !== "settled");
  const inc = plannedIncomeOccurrences(data.plannedIncomes, data.transactions, from, to, today);
  const days = eachDay(from, to);
  const monthOut = sumMinor(occ.filter((o) => o.dueDate.startsWith(month)).map((o) => o.amount));
  const monthIn = sumMinor(inc.filter((o) => o.dueDate.startsWith(month)).map((o) => o.amount));
  return (
    <Card className="p-3 sm:p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon-sm" aria-label="Mes anterior" onClick={() => setMonth(addMonthKey(month, -1))}>
            <ChevronLeft />
          </Button>
          <h3 className="min-w-36 text-center text-sm font-semibold first-letter:uppercase">{formatMonthYear(`${month}-01`)}</h3>
          <Button variant="ghost" size="icon-sm" aria-label="Mes siguiente" onClick={() => setMonth(addMonthKey(month, 1))}>
            <ChevronRight />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          Pagos <span className="font-medium text-foreground tabular">{money(monthOut)}</span> · Ingresos previstos <span className="font-medium text-income tabular">{money(monthIn)}</span>
        </p>
      </div>
      <div className="grid grid-cols-7 gap-px overflow-hidden rounded-lg border border-border bg-border">
        {orderedWeekdays(ws).map((d) => (
          <div key={d} className="bg-muted/60 py-1.5 text-center text-[11px] font-medium text-muted-foreground">
            {WEEKDAY_SHORT[d]}
          </div>
        ))}
        {days.map((d) => {
          const out = occ.filter((o) => o.dueDate === d);
          const ins = inc.filter((o) => o.dueDate === d);
          const inMonth = d.startsWith(month);
          return (
            <div key={d} className={cn("min-h-16 bg-card p-1 sm:min-h-24 sm:p-1.5", !inMonth && "bg-muted/30 text-subtle")}>
              <div className={cn("mb-1 flex size-6 items-center justify-center rounded-full text-xs tabular", d === today && "bg-brand font-semibold text-brand-foreground")}>{Number(d.slice(8))}</div>
              <div className="space-y-0.5">
                {out.map((o) => (
                  <button
                    key={o.key}
                    type="button"
                    onClick={() => (o.remaining > 0 ? openForm({ kind: "obligationPayment", obligationId: o.source.id, dueDate: o.dueDate }) : openForm({ kind: "obligation", id: o.source.id }))}
                    title={`${o.source.name}: ${money(o.amount)}`}
                    className={cn(
                      "block w-full truncate rounded px-1 py-0.5 text-left text-[10.5px] leading-tight font-medium sm:text-[11px]",
                      o.remaining === 0 ? "bg-muted text-muted-foreground line-through" : o.status === "overdue" ? "bg-expense-soft text-expense" : "bg-warning-soft text-warning",
                    )}
                  >
                    <span className="max-sm:hidden">{o.source.name} · </span>
                    {money(o.remaining || o.amount, { compact: true })}
                  </button>
                ))}
                {ins.map((o) => (
                  <button key={o.key} type="button" onClick={() => openForm({ kind: "receiveIncome", plannedIncomeId: o.source.id, dueDate: o.dueDate })} className="block w-full truncate rounded bg-income-soft px-1 py-0.5 text-left text-[10.5px] leading-tight font-medium text-income sm:text-[11px]">
                    <span className="max-sm:hidden">{o.source.name} · </span>+{money(o.amount, { compact: true })}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
