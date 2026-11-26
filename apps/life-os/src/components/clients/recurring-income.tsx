"use client";

import * as React from "react";
import { Pencil } from "lucide-react";
import type { PlannedIncome } from "@/db/types";
import type { Occurrence, RecurringIncomeView } from "@/domain/finance";
import { useMoney, useToday } from "@/hooks/data";
import { formatDateShort, formatRelativeDay, type DateStr } from "@/lib/dates";
import { describeRecurrence } from "@/lib/recurrence";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/misc";
import { Button } from "@/components/ui/button";
import { Money } from "@/components/shared/primitives";
import { useUI } from "@/components/shell/ui-context";

/** Status of one pay period, in the words of a salary: received, late, skipped, upcoming. */
export function PeriodBadge({ occ, today, className }: { occ: Occurrence<PlannedIncome>; today: DateStr; className?: string }) {
  const [tone, label] = periodState(occ, today);
  return (
    <Badge tone={tone} className={className}>
      {label}
    </Badge>
  );
}

function periodState(occ: Occurrence<PlannedIncome>, today: DateStr): [React.ComponentProps<typeof Badge>["tone"], string] {
  switch (occ.status) {
    case "settled":
      return ["neutral", "Omitido"];
    case "paid":
      return ["income", "Recibido"];
    case "overdue":
      return ["expense", occ.paid > 0 ? "Incompleto" : "Sin registrar"];
    case "partial":
      return ["warning", "Parcial"];
    default:
      return occ.dueDate === today ? ["brand", "Hoy"] : ["outline", "Próximo"];
  }
}

/** One pay period row: date, status, value and the action to register it. */
export function PeriodRow({
  occ,
  title,
  subtitle,
  onTitleClick,
  className,
}: {
  occ: Occurrence<PlannedIncome>;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  onTitleClick?: () => void;
  className?: string;
}) {
  const today = useToday();
  const { openForm } = useUI();
  const due = occ.dueDate < today ? formatDateShort(occ.dueDate) : formatRelativeDay(occ.dueDate, today);
  const info = (
    <>
      {title && <span className="block truncate text-sm font-medium">{title}</span>}
      <span className={cn("block truncate", title ? "text-xs text-muted-foreground" : "text-sm")}>
        {subtitle ? <>{subtitle} · </> : null}
        {due}
      </span>
    </>
  );
  return (
    <li className={cn("flex items-center gap-3 px-3 py-2.5", className)}>
      {onTitleClick ? (
        <button type="button" onClick={onTitleClick} className="min-w-0 flex-1 text-left">
          {info}
        </button>
      ) : (
        <div className="min-w-0 flex-1">{info}</div>
      )}
      <div className="flex shrink-0 flex-col items-end gap-1">
        <Money amount={occ.remaining > 0 ? occ.remaining : occ.status === "paid" ? occ.paid : occ.amount} tone={occ.status === "paid" ? "income" : undefined} className={cn("text-sm font-semibold", occ.status === "settled" && "text-muted-foreground line-through")} />
        <PeriodBadge occ={occ} today={today} />
      </div>
      {occ.remaining > 0 ? (
        <Button
          size="sm"
          variant={occ.status === "overdue" || occ.dueDate === today ? "income" : "outline"}
          aria-label={`Registrar el pago del ${formatDateShort(occ.dueDate)}`}
          onClick={() => openForm({ kind: "receiveIncome", plannedIncomeId: occ.source.id, dueDate: occ.dueDate })}
        >
          Recibir
        </Button>
      ) : (
        <span className="w-[74px] shrink-0" aria-hidden />
      )}
    </li>
  );
}

/** A salary or fixed payment agreement inside the client sheet. */
export function ClientIncomeCard({ view }: { view: RecurringIncomeView }) {
  const today = useToday();
  const money = useMoney();
  const { openForm } = useUI();
  const { income, next, recent, overdue } = view;
  // What needs action first (late periods, then the next payday), then the history.
  const late = recent.filter((o) => o.status === "overdue").reverse();
  const periods = [...late, ...(next ? [next] : []), ...recent.filter((o) => o.status !== "overdue")];
  const olderOverdue = overdue.filter((o) => !recent.some((r) => r.key === o.key));
  const edit = () => openForm({ kind: "plannedIncome", id: income.id });
  return (
    <div className="overflow-hidden rounded-xl border border-border">
      <div className="flex items-start gap-3 px-4 pt-3.5 pb-3">
        <button type="button" onClick={edit} className="min-w-0 flex-1 text-left">
          <span className="block truncate text-sm font-semibold">{income.name}</span>
          <span className="block text-xs text-muted-foreground">
            {describeRecurrence(income.recurrence)}
            {income.recurrence?.until ? ` · hasta el ${formatDateShort(income.recurrence.until)}` : ""}
            {income.confirmed ? "" : " · por confirmar"}
          </span>
        </button>
        <div className="text-right">
          <Money amount={income.amount} className="block text-[17px] leading-tight font-semibold" />
          <span className="text-xs text-muted-foreground">{income.recurrence ? "por pago" : "una vez"}</span>
        </div>
        <Button variant="ghost" size="icon-sm" aria-label={`Editar ${income.name}`} className="-mr-1.5" onClick={edit}>
          <Pencil />
        </Button>
      </div>
      <dl className="grid grid-cols-2 gap-3 border-t border-border bg-muted/40 px-4 py-2.5 text-[13px]">
        <div className="min-w-0">
          <dt className="text-xs text-muted-foreground">Próximo pago</dt>
          <dd className="truncate font-medium">{next ? formatRelativeDay(next.dueDate, today) : view.ended ? "Terminado" : "—"}</dd>
        </div>
        <div className="min-w-0">
          <dt className="text-xs text-muted-foreground">Recibido en {today.slice(0, 4)}</dt>
          <dd className="tabular font-medium text-income">{money(view.receivedYear)}</dd>
        </div>
        {view.monthly > 0 && view.income.recurrence?.freq !== "monthly" && (
          <div className="col-span-2 text-xs text-muted-foreground">Equivale a unos {money(view.monthly)} al mes.</div>
        )}
      </dl>
      {periods.length > 0 && (
        <ul className="divide-y divide-border border-t border-border">
          {periods.map((o) => (
            <PeriodRow key={o.key} occ={o} />
          ))}
        </ul>
      )}
      {olderOverdue.length > 0 && (
        <p className="border-t border-border px-4 py-2 text-xs text-expense">
          {olderOverdue.length === 1 ? "Hay 1 pago anterior sin registrar" : `Hay ${olderOverdue.length} pagos anteriores sin registrar`} (desde el {formatDateShort(olderOverdue[0].dueDate)}). Están en Cobros.
        </p>
      )}
    </div>
  );
}
