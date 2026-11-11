"use client";

import * as React from "react";
import { ArrowLeftRight, Check, Link2, MoreHorizontal, Pencil, Repeat, SkipForward } from "lucide-react";
import { useAccountMap, useCategoryMap, useData, useMoney, useToday } from "@/hooks/data";
import type { Obligation, PlannedIncome, Transaction } from "@/db/types";
import type { Occurrence } from "@/domain/finance";
import { formatRelativeDay, formatTime } from "@/lib/dates";
import { describeRecurrence } from "@/lib/recurrence";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/misc";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/overlays";
import { IconBadge, Money } from "@/components/shared/primitives";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { settleOccurrence, skipPlannedIncome } from "@/services/finance-service";

export function TransactionRow({ tx, showDate }: { tx: Transaction; showDate?: boolean }) {
  const cats = useCategoryMap();
  const accounts = useAccountMap();
  const data = useData();
  const today = useToday();
  const { openForm } = useUI();
  const cat = tx.categoryId ? cats.get(tx.categoryId) : undefined;
  const account = accounts.get(tx.accountId);
  const to = tx.toAccountId ? accounts.get(tx.toAccountId) : undefined;
  const client = tx.clientId ? data.clients.find((c) => c.id === tx.clientId) : undefined;
  const linked = tx.clientPaymentId || tx.obligationId || tx.plannedIncomeId;
  const title = tx.description || cat?.name || (tx.kind === "transfer" ? "Transferencia" : "Movimiento");
  return (
    <li className="list-none">
      <button
        type="button"
        onClick={() => openForm({ kind: "transaction", id: tx.id })}
        className="flex w-full min-w-0 items-center gap-3 rounded-lg px-2 py-2.5 text-left transition-colors outline-none hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring"
      >
        {tx.kind === "transfer" ? (
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-secondary text-muted-foreground">
            <ArrowLeftRight className="size-4" />
          </span>
        ) : (
          <IconBadge icon={cat?.icon ?? "circle-dashed"} color={cat?.color ?? "slate"} />
        )}
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-1.5">
            <span className="truncate text-sm font-medium">{title}</span>
            {linked && <Link2 className="size-3 shrink-0 text-info" aria-label="Vinculado" />}
            {tx.recurring && <Repeat className="size-3 shrink-0 text-muted-foreground" aria-label="Recurrente" />}
          </span>
          <span className="block truncate text-xs text-muted-foreground">
            {[
              showDate ? formatRelativeDay(tx.date, today) : tx.time ? formatTime(tx.time) : null,
              tx.kind === "transfer" ? `${account?.name ?? "?"} → ${to?.name ?? "?"}` : account?.name,
              client?.name,
              tx.description && cat ? cat.name : null,
            ]
              .filter(Boolean)
              .join(" · ")}
          </span>
        </span>
        <Money
          amount={tx.kind === "expense" ? -tx.amount : tx.amount}
          signed={tx.kind === "income"}
          tone={tx.kind === "income" ? "income" : tx.kind === "transfer" ? "muted" : undefined}
          className="text-sm font-semibold"
        />
      </button>
    </li>
  );
}

const STATUS_BADGE = {
  overdue: { tone: "expense" as const, label: "Vencida" },
  partial: { tone: "info" as const, label: "Abonada" },
  pending: { tone: "neutral" as const, label: "Pendiente" },
  paid: { tone: "income" as const, label: "Pagada" },
  settled: { tone: "outline" as const, label: "Resuelta" },
};

export function ObligationOccurrenceRow({ occ, compact }: { occ: Occurrence<Obligation>; compact?: boolean }) {
  const today = useToday();
  const money = useMoney();
  const { openForm } = useUI();
  const o = occ.source;
  const badge = STATUS_BADGE[occ.status];
  return (
    <li className="flex items-center gap-3 px-2 py-2.5">
      <div className={cn("flex w-11 shrink-0 flex-col items-center rounded-lg border py-1 text-center leading-none", occ.status === "overdue" ? "border-expense/40 text-expense" : "border-border")}>
        <span className="text-[10px] font-medium uppercase text-muted-foreground">{new Intl.DateTimeFormat("es-CO", { month: "short", timeZone: "UTC" }).format(new Date(`${occ.dueDate}T12:00:00Z`)).replace(".", "")}</span>
        <span className="mt-0.5 text-base font-semibold tabular">{Number(occ.dueDate.slice(8))}</span>
      </div>
      <button type="button" className="min-w-0 flex-1 text-left" onClick={() => openForm({ kind: "obligation", id: o.id })}>
        <span className="block truncate text-sm font-medium">{o.name}</span>
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className={cn(occ.status === "overdue" && "text-expense")}>{formatRelativeDay(occ.dueDate, today)}</span>
          {!compact && o.recurrence && <span>· {describeRecurrence(o.recurrence)}</span>}
          {occ.paid > 0 && occ.remaining > 0 && <span>· abonado {money(occ.paid)}</span>}
        </span>
      </button>
      <div className="flex shrink-0 flex-col items-end gap-1">
        <Money amount={occ.remaining > 0 ? occ.remaining : occ.amount} className="text-sm font-semibold" />
        {!compact && <Badge tone={badge.tone}>{badge.label}</Badge>}
      </div>
      {occ.remaining > 0 ? (
        <div className="flex shrink-0 items-center">
          <Button size="sm" variant="outline" onClick={() => openForm({ kind: "obligationPayment", obligationId: o.id, dueDate: occ.dueDate })}>
            Pagar
          </Button>
          {!compact && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon-sm" aria-label="Más acciones">
                  <MoreHorizontal />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onSelect={() => runSave(() => settleOccurrence(o.id, occ.dueDate, "paid-outside"), "Marcada como pagada")}>
                  <Check /> Ya la pagué (sin movimiento)
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => runSave(() => settleOccurrence(o.id, occ.dueDate, "skipped"), "Vencimiento omitido")}>
                  <SkipForward /> Omitir este vencimiento
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => openForm({ kind: "obligation", id: o.id })}>
                  <Pencil /> Editar obligación
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      ) : occ.settlement ? (
        <Button variant="ghost" size="sm" onClick={() => runSave(() => settleOccurrence(o.id, occ.dueDate, null), "Vencimiento restaurado")}>
          Deshacer
        </Button>
      ) : (
        <span className="flex size-8 items-center justify-center text-income">
          <Check className="size-4" />
        </span>
      )}
    </li>
  );
}

export function PlannedIncomeRow({ occ }: { occ: Occurrence<PlannedIncome> }) {
  const today = useToday();
  const { openForm } = useUI();
  const p = occ.source;
  return (
    <li className="flex items-center gap-3 px-2 py-2.5">
      <button type="button" className="min-w-0 flex-1 text-left" onClick={() => openForm({ kind: "plannedIncome", id: p.id })}>
        <span className="flex items-center gap-2">
          <span className="truncate text-sm font-medium">{p.name}</span>
          <Badge tone={p.confirmed ? "income" : "warning"}>{p.confirmed ? "Confirmado" : "Por confirmar"}</Badge>
        </span>
        <span className="text-xs text-muted-foreground">
          {formatRelativeDay(occ.dueDate, today)}
          {p.recurrence ? ` · ${describeRecurrence(p.recurrence)}` : ""}
        </span>
      </button>
      <Money amount={occ.remaining > 0 ? occ.remaining : occ.amount} tone="income" className="text-sm font-semibold" />
      {occ.remaining > 0 ? (
        <div className="flex items-center">
          <Button size="sm" variant="outline" onClick={() => openForm({ kind: "receiveIncome", plannedIncomeId: p.id, dueDate: occ.dueDate })}>
            Recibir
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon-sm" aria-label="Más acciones">
                <MoreHorizontal />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onSelect={() => runSave(() => skipPlannedIncome(p.id, occ.dueDate, true), "Ingreso omitido")}>
                <SkipForward /> No llegó / omitir
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => openForm({ kind: "plannedIncome", id: p.id })}>
                <Pencil /> Editar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      ) : (
        <span className="flex size-8 items-center justify-center text-income">
          <Check className="size-4" />
        </span>
      )}
    </li>
  );
}
