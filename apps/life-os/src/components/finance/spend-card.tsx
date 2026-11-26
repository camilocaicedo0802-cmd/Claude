"use client";

import * as React from "react";
import Link from "next/link";
import { ChevronDown, CircleAlert, CircleCheck, Info, PiggyBank, Settings2 } from "lucide-react";
import { useCapacity, useData, useMoney } from "@/hooks/data";
import { formatDayMonth } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Card } from "@/components/shared/primitives";
import { Button } from "@/components/ui/button";
import { useUI } from "@/components/shell/ui-context";

/** "¿Cuánto puedo gastar?" — the decision card. Conservative and transparent by design. */
export function SpendCapacityCard({ className }: { className?: string }) {
  const c = useCapacity();
  const data = useData();
  const money = useMoney();
  const { openForm } = useUI();
  const [open, setOpen] = React.useState(false);
  const horizonLabel =
    c.horizon.reason === "nextIncome" && c.horizon.nextIncome
      ? `hasta tu próximo ingreso (${c.horizon.nextIncome.name}, ${formatDayMonth(c.horizon.nextIncome.date)})`
      : c.horizon.reason === "days"
        ? `en los próximos ${c.horizon.days} días`
        : `hasta fin de mes`;

  if (c.status === "no-accounts") {
    return (
      <Card className={cn("p-5", className)}>
        <h2 className="text-[15px] font-semibold">¿Cuánto puedo gastar?</h2>
        <p className="mt-2 max-w-prose text-sm text-muted-foreground">
          Para recomendarte cuánto gastar necesito saber cuánto dinero tienes. Registra tus cuentas (efectivo, banco o billeteras) con su saldo actual.
        </p>
        <Button className="mt-4" onClick={() => openForm({ kind: "account" })}>
          Registrar mi primera cuenta
        </Button>
      </Card>
    );
  }

  const negative = c.status === "negative";
  const rows: Array<{ label: string; value: number; tone?: "minus" | "plus" | "total"; hint?: string }> = [
    { label: "Dinero disponible para gastar", value: c.startingBalance, hint: c.balances.protectedSavings ? `No incluye ${money(c.balances.protectedSavings)} en ahorros apartados.` : undefined },
    { label: "Obligaciones por pagar", value: -c.obligations.total, tone: "minus", hint: c.obligations.items.length ? `${c.obligations.items.length} pago(s) ${horizonLabel}${c.obligations.overdue ? `, incluye ${money(c.obligations.overdue)} vencido` : ""}.` : undefined },
    {
      label: "Gastos esenciales estimados",
      value: -c.essentials.total,
      tone: "minus",
      hint: c.essentials.lines.length ? c.essentials.lines.map((l) => `${l.name} ${money(l.amount)}${l.method === "history" ? " (historial)" : ""}`).join(" · ") : undefined,
    },
    ...(c.reserves.safety ? [{ label: "Colchón de seguridad", value: -c.reserves.safety, tone: "minus" as const }] : []),
    ...(c.reserves.goalsSetAside ? [{ label: "Dinero apartado para metas", value: -c.reserves.goalsSetAside, tone: "minus" as const }] : []),
    ...(c.reserves.goalsPlanned ? [{ label: "Aportes planificados a metas", value: -c.reserves.goalsPlanned, tone: "minus" as const }] : []),
    ...(c.income.confirmedIncluded ? [{ label: "Ingresos confirmados del período", value: c.income.confirmed, tone: "plus" as const }] : []),
    { label: "Margen libre proyectado", value: c.free, tone: "total" },
  ];

  return (
    <Card className={cn("overflow-hidden", className)}>
      <div className="flex items-start justify-between gap-3 px-5 pt-5">
        <div>
          <h2 className="text-[15px] font-semibold">¿Cuánto puedo gastar?</h2>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Calculado {horizonLabel} · {c.horizon.days} {c.horizon.days === 1 ? "día" : "días"}
          </p>
        </div>
        <Button variant="ghost" size="icon-sm" asChild aria-label="Configurar el cálculo">
          <Link href="/ajustes/#calculo">
            <Settings2 />
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 px-5 pt-4 pb-5 sm:grid-cols-[1.25fr_1fr_1fr] sm:gap-0 sm:divide-x sm:divide-border">
        <div className="sm:pr-5">
          <p className="text-[13px] font-medium text-muted-foreground">Disponible hoy</p>
          <p className={cn("mt-1 tabular text-[34px] leading-none font-semibold tracking-tight", negative ? "text-expense" : "text-foreground")}>{money(c.availableToday)}</p>
          <p className="mt-2 text-xs text-muted-foreground">
            {c.todaySpentDiscretionary > 0
              ? `Ya gastaste ${money(c.todaySpentDiscretionary)} en no esenciales hoy · ritmo ${money(c.dailyAllowance)}/día`
              : `Para gastos no esenciales · ritmo ${money(c.dailyAllowance)}/día`}
          </p>
        </div>
        <div className="sm:px-5">
          <p className="text-[13px] font-medium text-muted-foreground">Esta semana</p>
          <p className="mt-1 tabular text-xl font-semibold">{money(c.week.available)}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {c.week.days} {c.week.days === 1 ? "día restante" : "días restantes"} sin comprometer pagos
          </p>
        </div>
        <div className="sm:pl-5">
          <p className="text-[13px] font-medium text-muted-foreground">Para ocio</p>
          <p className="mt-1 tabular text-xl font-semibold">{money(c.leisure.available)}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {c.leisure.method === "budget" ? "Según lo que queda de tus presupuestos de ocio y compras" : `${c.leisure.share} % de tu margen libre (sin presupuesto de ocio)`}
          </p>
        </div>
      </div>

      {c.savings.share > 0 && <SavingsTip c={c} accounts={data.accounts} />}

      <div className={cn("border-t border-border px-5 py-4 text-sm", negative ? "bg-expense-soft" : "bg-muted/50")}>
        <p className={cn("flex gap-2 leading-relaxed", negative && "text-expense")}>
          {negative && <CircleAlert className="mt-0.5 size-4 shrink-0" />}
          {c.summary}
        </p>
        {c.warnings.filter((w) => !negative || !w.startsWith("Te faltarían")).map((w) => (
          <p key={w} className="mt-2 flex gap-2 text-[13px] text-warning">
            <CircleAlert className="mt-0.5 size-3.5 shrink-0" /> {w}
          </p>
        ))}
        {c.missing.map((m) => (
          <p key={m} className="mt-2 flex gap-2 text-[13px] text-muted-foreground">
            <Info className="mt-0.5 size-3.5 shrink-0" /> {m}
          </p>
        ))}
        <button
          type="button"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
          className="mt-3 inline-flex items-center gap-1 text-[13px] font-medium text-muted-foreground hover:text-foreground"
        >
          {open ? "Ocultar el cálculo" : "Ver cómo se calcula"}
          <ChevronDown className={cn("size-4 transition-transform", open && "rotate-180")} />
        </button>
        {open && (
          <div className="mt-3 animate-rise">
            <dl className="divide-y divide-border rounded-lg border border-border bg-card">
              {rows.map((r) => (
                <div key={r.label} className={cn("px-3 py-2.5", r.tone === "total" && "bg-muted/60")}>
                  <div className="flex items-baseline justify-between gap-3">
                    <dt className={cn("text-[13px]", r.tone === "total" ? "font-semibold" : "text-muted-foreground")}>{r.label}</dt>
                    <dd className={cn("tabular text-sm font-medium", r.tone === "total" && (r.value < 0 ? "text-expense" : "font-semibold"))}>
                      {r.tone === "minus" ? `− ${money(Math.abs(r.value))}` : r.tone === "plus" ? `+ ${money(r.value)}` : money(r.value)}
                    </dd>
                  </div>
                  {r.hint && <p className="mt-0.5 text-xs text-subtle">{r.hint}</p>}
                </div>
              ))}
            </dl>
            <ul className="mt-3 space-y-1.5 text-xs text-muted-foreground">
              {c.notes.map((n) => (
                <li key={n} className="flex gap-1.5">
                  <Info className="mt-0.5 size-3 shrink-0" /> {n}
                </li>
              ))}
              <li className="flex gap-1.5">
                <Info className="mt-0.5 size-3 shrink-0" /> Las obligaciones futuras no se descuentan de tu saldo real hasta que las pagas; aquí solo se reservan.
              </li>
              {c.savings.share > 0 && c.savings.base > 0 && (
                <li className="flex gap-1.5">
                  <Info className="mt-0.5 size-3 shrink-0" />
                  Ahorro sugerido: {c.savings.share} % de {money(c.savings.base)}, lo libre de este período (desde el {formatDayMonth(c.savings.since)})
                  {c.savings.saved > 0 ? `, incluidos ${money(c.savings.saved)} que ya apartaste` : ""}. Se cuenta como apartado lo que pasas a una cuenta de ahorro o a una meta.
                </li>
              )}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
}

type Capacity = ReturnType<typeof useCapacity>;

/** Savings recommendation: a share of what is free this pay period, with a one-tap transfer to savings. */
function SavingsTip({ c, accounts }: { c: Capacity; accounts: ReturnType<typeof useData>["accounts"] }) {
  const money = useMoney();
  const { openForm } = useUI();
  const { suggested, target, saved, share } = c.savings;
  const until = formatDayMonth(c.horizon.end);
  const savingsAccount =
    accounts.find((a) => !a.archived && a.type === "savings" && !a.spendable) ?? accounts.find((a) => !a.archived && a.type !== "credit" && !a.spendable);
  const fromAccount = accounts
    .filter((a) => !a.archived && a.type !== "credit" && a.spendable)
    .sort((a, b) => (c.balances.byAccount.get(b.id) ?? 0) - (c.balances.byAccount.get(a.id) ?? 0))[0];
  const done = suggested === 0 && target > 0 && saved >= target;

  const setAside = () => {
    if (!savingsAccount) {
      openForm({ kind: "account", defaults: { type: "savings" } });
      return;
    }
    openForm({
      kind: "transaction",
      defaults: { kind: "transfer", amount: suggested, accountId: fromAccount?.id, toAccountId: savingsAccount.id, description: "Ahorro" },
    });
  };

  return (
    <div className="px-5 pb-5">
      <div className="flex flex-col gap-3 rounded-xl border border-border bg-card p-4 sm:flex-row sm:items-center">
        <div className="flex min-w-0 flex-1 items-start gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-income-soft text-income [&_svg]:size-[18px]" aria-hidden>
            {done ? <CircleCheck /> : <PiggyBank />}
          </span>
          <div className="min-w-0">
            <p className="text-[13px] font-medium text-muted-foreground">Recomendación de ahorro</p>
            {done ? (
              <>
                <p className="mt-0.5 text-[15px] font-semibold">Ya apartaste {money(saved)} este período</p>
                <p className="mt-0.5 text-xs text-muted-foreground">Cumpliste tu {share} %. Lo que queda libre es para gastar con tranquilidad.</p>
              </>
            ) : suggested > 0 ? (
              <>
                <p className="mt-0.5 text-[15px] font-semibold">
                  Aparta <span className="tabular text-income">{money(suggested)}</span>
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {saved > 0
                    ? `Ya apartaste ${money(saved)}; esto completa el ${share} % de lo libre de este período. `
                    : `Es el ${share} % de tu margen libre hasta el ${until}. `}
                  Después te quedan {money(Math.max(0, c.free - suggested))} libres.
                </p>
              </>
            ) : (
              <>
                <p className="mt-0.5 text-[15px] font-semibold">Hoy no hay margen para ahorrar</p>
                <p className="mt-0.5 text-xs text-muted-foreground">Primero cubre lo comprometido. Cuando tengas margen libre te diré cuánto apartar ({share} %).</p>
              </>
            )}
          </div>
        </div>
        {suggested > 0 && (
          <Button size="sm" variant="income" className="shrink-0 max-sm:w-full" onClick={setAside}>
            {savingsAccount ? "Apartar ahora" : "Crear cuenta de ahorro"}
          </Button>
        )}
      </div>
    </div>
  );
}
