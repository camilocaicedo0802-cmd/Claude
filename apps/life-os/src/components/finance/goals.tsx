"use client";

import * as React from "react";
import { PiggyBank, Plus, ShieldCheck } from "lucide-react";
import { useCapacity, useData, useMoney, useToday } from "@/hooks/data";
import { goalProgress, monthlyNeeded, periodTotals, isEssential } from "@/domain/finance";
import { addDays, formatDateLong, formatRelativeDay } from "@/lib/dates";
import { divideFloor } from "@/lib/money";
import { Button } from "@/components/ui/button";
import { Badge, Progress } from "@/components/ui/misc";
import { Card, EmptyState, Money, toneStyle } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";

export function GoalsPage() {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const capacity = useCapacity();
  const { openForm } = useUI();
  const goals = data.goals.filter((g) => !g.archived).sort((a, b) => Number(b.isEmergencyFund) - Number(a.isEmergencyFund));

  // Monthly essential spending over the last 90 days, used to express the emergency fund in months.
  const from = addDays(today, -89);
  const cats = new Map(data.categories.map((c) => [c.id, c]));
  const essential90 = data.transactions
    .filter((t) => t.kind === "expense" && t.date >= from && t.date <= today && isEssential(cats.get(t.categoryId ?? "")))
    .reduce((s, t) => s + t.amount, 0);
  const firstTx = data.transactions.reduce<string | null>((m, t) => (!m || t.date < m ? t.date : m), null);
  const months = firstTx ? Math.max(1, Math.min(3, (Date.parse(today) - Date.parse(firstTx > from ? firstTx : from)) / (30.44 * 86_400_000))) : 0;
  const essentialMonthly = months >= 0.5 ? divideFloor(essential90, months) : 0;
  void periodTotals;

  return (
    <SectionPage
      section="finanzas"
      title="Metas de ahorro"
      description="Aparta dinero con intención. Lo apartado se protege en el cálculo de cuánto puedes gastar."
      actions={
        <Button onClick={() => openForm({ kind: "goal" })}>
          <Plus /> Meta
        </Button>
      }
    >
      {goals.length === 0 ? (
        <Card>
          <EmptyState
            icon={<PiggyBank />}
            title="Sin metas todavía"
            description="Empieza por un fondo de emergencia (3 a 6 meses de gastos esenciales) y agrega metas con fecha: calculamos cuánto apartar cada mes."
            action={
              <Button onClick={() => openForm({ kind: "goal" })}>
                <Plus /> Crear meta
              </Button>
            }
          />
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {goals.map((g) => {
            const p = goalProgress(g, data.contributions);
            const monthly = monthlyNeeded(g, p.saved, today);
            const contributions = data.contributions.filter((c) => c.goalId === g.id).sort((a, b) => b.date.localeCompare(a.date));
            const account = data.accounts.find((a) => a.id === g.accountId);
            return (
              <Card key={g.id} className="p-5" style={toneStyle(g.color)}>
                <div className="flex items-start justify-between gap-3">
                  <button type="button" className="min-w-0 text-left" onClick={() => openForm({ kind: "goal", id: g.id })}>
                    <h2 className="flex items-center gap-2 text-[15px] font-semibold">
                      {g.isEmergencyFund && <ShieldCheck className="size-4 tone-text" />}
                      {g.name}
                    </h2>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {g.targetDate ? `Meta al ${formatDateLong(g.targetDate)}` : "Sin fecha objetivo"}
                      {account ? ` · en ${account.name}` : " · en cuentas de uso diario"}
                    </p>
                  </button>
                  {p.saved >= g.target && <Badge tone="income">Lograda</Badge>}
                </div>
                <div className="mt-4 flex items-baseline justify-between gap-2">
                  <Money amount={p.saved} className="text-2xl font-semibold tracking-tight" />
                  <span className="text-[13px] text-muted-foreground tabular">de {money(g.target)}</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted" role="progressbar" aria-valuenow={Math.round(p.percent)} aria-valuemin={0} aria-valuemax={100} aria-label={`Progreso de ${g.name}`}>
                  <div className="h-full rounded-full tone-dot transition-[width] duration-500" style={{ width: `${p.percent}%` }} />
                </div>
                <p className="mt-2 text-[13px] text-muted-foreground">
                  {Math.round(p.percent)} % · faltan {money(p.remaining)}
                  {monthly ? ` · aparta ${money(monthly)} al mes para llegar a tiempo` : ""}
                </p>
                {g.isEmergencyFund && essentialMonthly > 0 && (
                  <p className="mt-2 rounded-lg bg-muted p-2.5 text-[13px]">
                    Cubre <span className="font-semibold">{(p.saved / essentialMonthly).toFixed(1)} meses</span> de tus gastos esenciales ({money(essentialMonthly)}/mes según tu historial).
                  </p>
                )}
                <div className="mt-4 flex gap-2">
                  <Button size="sm" onClick={() => openForm({ kind: "contribution", goalId: g.id })}>
                    <Plus /> Aportar
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => openForm({ kind: "goal", id: g.id })}>
                    Editar
                  </Button>
                </div>
                {contributions.length > 0 && (
                  <ul className="mt-4 space-y-1 border-t border-border pt-3 text-[13px]">
                    {contributions.slice(0, 4).map((c) => (
                      <li key={c.id} className="flex justify-between gap-2">
                        <span className="text-muted-foreground">
                          {formatRelativeDay(c.date, today)}
                          {c.note ? ` · ${c.note}` : ""}
                        </span>
                        <Money amount={c.amount} signed tone={c.amount < 0 ? "expense" : "income"} />
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            );
          })}
        </div>
      )}
      {capacity.reserves.goalsPlanned > 0 && (
        <p className="text-center text-[13px] text-muted-foreground">
          Se reservan {money(capacity.reserves.goalsPlanned)} para aportes planificados en el cálculo de gasto ({capacity.horizon.days} días). Puedes desactivarlo en Ajustes.
        </p>
      )}
    </SectionPage>
  );
}
