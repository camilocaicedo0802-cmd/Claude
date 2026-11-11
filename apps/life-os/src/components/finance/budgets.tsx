"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight, Plus, Target } from "lucide-react";
import { useCategoryMap, useData, useMoney, useToday } from "@/hooks/data";
import { budgetStatuses, expensesByCategory } from "@/domain/finance";
import { addMonthKey, daysInMonth, diffDays, endOfMonth, formatMonthYear, startOfMonth } from "@/lib/dates";
import { sumMinor } from "@/lib/money";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge, Progress } from "@/components/ui/misc";
import { Card, CardHeader, EmptyState, IconBadge, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { NATURE_LABEL } from "@/components/forms/finance-forms";

export function BudgetsPage() {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const cats = useCategoryMap();
  const { openForm } = useUI();
  const [month, setMonth] = React.useState(today.slice(0, 7));
  const anchor = `${month}-01`;
  const statuses = budgetStatuses(data.budgets, data.categories, data.transactions, anchor, today);
  const spentBy = expensesByCategory(data.transactions, startOfMonth(anchor), endOfMonth(anchor));
  const unbudgeted = [...spentBy.entries()].filter(([id]) => !data.budgets.some((b) => b.categoryId === id)).sort((a, b) => b[1] - a[1]);
  const totalBudget = sumMinor(statuses.map((s) => s.budget.amount));
  const totalSpent = sumMinor(statuses.map((s) => s.spent));
  const isCurrent = month === today.slice(0, 7);
  const elapsedPct = isCurrent ? ((diffDays(anchor, today) + 1) / daysInMonth(anchor)) * 100 : month < today.slice(0, 7) ? 100 : 0;

  return (
    <SectionPage
      section="finanzas"
      title="Presupuestos"
      description="Límites mensuales por categoría. Te avisamos al 80 % y al superarlos."
      actions={
        <Button onClick={() => openForm({ kind: "budget" })}>
          <Plus /> Presupuesto
        </Button>
      }
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon-sm" aria-label="Mes anterior" onClick={() => setMonth(addMonthKey(month, -1))}>
            <ChevronLeft />
          </Button>
          <h2 className="min-w-36 text-center text-sm font-semibold first-letter:uppercase">{formatMonthYear(anchor)}</h2>
          <Button variant="ghost" size="icon-sm" aria-label="Mes siguiente" onClick={() => setMonth(addMonthKey(month, 1))}>
            <ChevronRight />
          </Button>
          {!isCurrent && (
            <Button variant="ghost" size="sm" onClick={() => setMonth(today.slice(0, 7))}>
              Hoy
            </Button>
          )}
        </div>
        {statuses.length > 0 && (
          <p className="text-[13px] text-muted-foreground">
            Gastado <span className="font-medium text-foreground tabular">{money(totalSpent)}</span> de <span className="tabular">{money(totalBudget)}</span>
            {isCurrent && ` · ha pasado el ${Math.round(elapsedPct)} % del mes`}
          </p>
        )}
      </div>

      {statuses.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Target />}
            title="Aún no tienes presupuestos"
            description="Ej.: Alimentación $600.000, Transporte $250.000, Ocio $200.000. Los presupuestos de gastos esenciales también mejoran el cálculo de «¿Cuánto puedo gastar?»."
            action={
              <Button onClick={() => openForm({ kind: "budget" })}>
                <Plus /> Crear el primero
              </Button>
            }
          />
        </Card>
      ) : (
        <Card>
          <ul className="divide-y divide-border">
            {statuses.map((s) => {
              const cat = s.category;
              return (
                <li key={s.budget.id}>
                  <button type="button" onClick={() => openForm({ kind: "budget", categoryId: s.budget.categoryId })} className="block w-full px-4 py-4 text-left hover:bg-accent/40 sm:px-5">
                    <div className="flex items-center gap-3">
                      <IconBadge icon={cat?.icon ?? "circle-dashed"} color={cat?.color ?? "slate"} size="sm" />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="truncate text-sm font-medium">{cat?.name}</span>
                          {cat?.nature && <span className="text-xs text-subtle">{NATURE_LABEL[cat.nature]}</span>}
                        </div>
                      </div>
                      {s.state !== "ok" && <Badge tone={s.state === "over" ? "expense" : "warning"}>{s.state === "over" ? "Excedido" : "Cerca del límite"}</Badge>}
                    </div>
                    <div className="relative mt-3">
                      <Progress value={s.percent} tone={s.state === "over" ? "expense" : s.state === "near" ? "warning" : "income"} className="h-2" label={`${cat?.name}: ${Math.round(s.percent)} % usado`} />
                      {isCurrent && <span className="absolute -top-1 h-4 w-px bg-foreground/40" style={{ left: `${elapsedPct}%` }} aria-hidden title="Día del mes" />}
                    </div>
                    <div className="mt-2 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 text-[13px]">
                      <span className="tabular">
                        <span className={cn("font-semibold", s.state === "over" && "text-expense")}>{money(s.spent)}</span>
                        <span className="text-muted-foreground"> de {money(s.budget.amount)} · {Math.round(s.percent)} %</span>
                      </span>
                      <span className={cn("tabular", s.remaining < 0 ? "text-expense" : "text-muted-foreground")}>
                        {s.remaining >= 0 ? `Quedan ${money(s.remaining)}` : `Te pasaste ${money(-s.remaining)}`}
                        {isCurrent && s.remaining > 0 && s.projected > s.budget.amount && ` · a este ritmo cerrarías en ${money(s.projected)}`}
                      </span>
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        </Card>
      )}

      {unbudgeted.length > 0 && (
        <Card>
          <CardHeader title="Gastos sin presupuesto" description="Categorías con gasto este mes que no tienen límite" />
          <ul className="divide-y divide-border px-2 pb-2 sm:px-3">
            {unbudgeted.map(([id, amount]) => {
              const cat = cats.get(id);
              return (
                <li key={id} className="flex items-center gap-3 px-2 py-2.5">
                  <IconBadge icon={cat?.icon ?? "circle-dashed"} color={cat?.color ?? "slate"} size="sm" />
                  <span className="min-w-0 flex-1 truncate text-sm">{cat?.name ?? "Sin categoría"}</span>
                  <Money amount={amount} className="text-sm font-medium" />
                  {cat && (
                    <Button variant="ghost" size="sm" onClick={() => openForm({ kind: "budget", categoryId: id })}>
                      Limitar
                    </Button>
                  )}
                </li>
              );
            })}
          </ul>
        </Card>
      )}
    </SectionPage>
  );
}
