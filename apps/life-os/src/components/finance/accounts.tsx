"use client";

import * as React from "react";
import { ArrowLeftRight, CreditCard, Landmark, Pencil, Plus, Wallet } from "lucide-react";
import { useCapacity, useData, useMoney } from "@/hooks/data";
import type { Account } from "@/db/types";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge, Progress } from "@/components/ui/misc";
import { Card, CardHeader, EmptyState, IconBadge, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { ACCOUNT_TYPE_LABEL } from "@/components/forms/finance-forms";

const TYPE_ICON: Record<Account["type"], string> = { cash: "banknote", bank: "building", wallet: "smartphone", savings: "piggy-bank", credit: "credit-card", other: "wallet" };

export function AccountsPage() {
  const data = useData();
  const money = useMoney();
  const c = useCapacity();
  const { openForm } = useUI();
  const [showArchived, setShowArchived] = React.useState(false);
  const balances = c.balances.byAccount;
  const liquid = data.accounts.filter((a) => a.type !== "credit" && (showArchived || !a.archived));
  const cards = data.accounts.filter((a) => a.type === "credit" && (showArchived || !a.archived));
  const archivedCount = data.accounts.filter((a) => a.archived).length;

  return (
    <SectionPage
      section="finanzas"
      title="Cuentas"
      description="Cada cuenta con su propio saldo. Las tarjetas se manejan aparte: su cupo nunca es dinero disponible."
      actions={
        <>
          <Button variant="outline" onClick={() => openForm({ kind: "transaction", defaults: { kind: "transfer" } })} disabled={data.accounts.filter((a) => !a.archived).length < 2}>
            <ArrowLeftRight /> Transferir
          </Button>
          <Button onClick={() => openForm({ kind: "account" })}>
            <Plus /> Cuenta
          </Button>
        </>
      }
    >
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Card className="p-4">
          <p className="text-[13px] text-muted-foreground">Saldo real total</p>
          <Money amount={c.balances.liquid} className="mt-1 block text-xl font-semibold" />
        </Card>
        <Card className="p-4">
          <p className="text-[13px] text-muted-foreground">Disponible para gastar</p>
          <Money amount={c.balances.spendable} className="mt-1 block text-xl font-semibold" />
        </Card>
        <Card className="p-4">
          <p className="text-[13px] text-muted-foreground">Ahorros apartados</p>
          <Money amount={c.balances.protectedSavings} className="mt-1 block text-xl font-semibold" />
        </Card>
        <Card className="p-4">
          <p className="text-[13px] text-muted-foreground">Deuda en tarjetas</p>
          <Money amount={c.balances.creditDebt} className={cn("mt-1 block text-xl font-semibold", c.balances.creditDebt > 0 && "text-expense")} />
        </Card>
      </div>

      <Card>
        <CardHeader title="Dinero" description="Efectivo, bancos, billeteras y ahorros" icon={<Wallet />} />
        {liquid.length === 0 ? (
          <EmptyState
            compact
            icon={<Landmark />}
            title="Sin cuentas"
            description="Crea tus cuentas con el saldo que tienen hoy. A partir de ahí, cada movimiento actualiza su saldo."
            action={
              <Button onClick={() => openForm({ kind: "account" })}>
                <Plus /> Crear cuenta
              </Button>
            }
          />
        ) : (
          <ul className="divide-y divide-border px-2 pb-2 sm:px-3">
            {liquid.map((a) => {
              const bal = balances.get(a.id) ?? 0;
              return (
                <li key={a.id}>
                  <button type="button" onClick={() => openForm({ kind: "account", id: a.id })} className="flex w-full items-center gap-3 rounded-lg px-2 py-3 text-left hover:bg-accent">
                    <IconBadge icon={TYPE_ICON[a.type]} color={a.color} />
                    <span className="min-w-0 flex-1">
                      <span className="flex items-center gap-2">
                        <span className="truncate text-sm font-medium">{a.name}</span>
                        {a.archived && <Badge tone="outline">Archivada</Badge>}
                        {!a.spendable && !a.archived && <Badge tone="income">Apartada</Badge>}
                      </span>
                      <span className="text-xs text-muted-foreground">{ACCOUNT_TYPE_LABEL[a.type]}</span>
                    </span>
                    <Money amount={bal} className={cn("text-[15px] font-semibold", bal < 0 && "text-expense")} />
                    <Pencil className="size-3.5 text-subtle" aria-hidden />
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </Card>

      <Card>
        <CardHeader
          title="Tarjetas de crédito"
          description="Las compras con tarjeta son gastos; pagar la tarjeta es una transferencia (no se cuenta dos veces)."
          icon={<CreditCard />}
          action={
            <Button variant="ghost" size="sm" onClick={() => openForm({ kind: "account", defaults: { type: "credit" } })}>
              <Plus /> Tarjeta
            </Button>
          }
        />
        {cards.length === 0 ? (
          <p className="px-5 pb-5 text-[13px] text-muted-foreground">No tienes tarjetas registradas.</p>
        ) : (
          <ul className="space-y-3 px-4 pb-5 sm:px-5">
            {cards.map((a) => {
              const debt = Math.max(0, -(balances.get(a.id) ?? 0));
              const used = a.creditLimit ? (debt / a.creditLimit) * 100 : 0;
              const scheduled = data.obligations.some((o) => o.active && o.type === "card" && o.cardAccountId === a.id);
              return (
                <li key={a.id} className="rounded-lg border border-border p-3">
                  <div className="flex items-center gap-3">
                    <IconBadge icon="credit-card" color={a.color} size="sm" />
                    <button type="button" className="min-w-0 flex-1 text-left" onClick={() => openForm({ kind: "account", id: a.id })}>
                      <span className="block truncate text-sm font-medium">{a.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {a.creditLimit ? `Cupo disponible ${money(Math.max(0, a.creditLimit - debt))} (no es dinero tuyo)` : "Sin cupo registrado"}
                      </span>
                    </button>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Debes</p>
                      <Money amount={debt} className={cn("text-[15px] font-semibold", debt > 0 && "text-expense")} />
                    </div>
                  </div>
                  {a.creditLimit ? <Progress className="mt-3" value={used} tone={used > 70 ? "expense" : used > 40 ? "warning" : "neutral"} label="Uso del cupo" /> : null}
                  <div className="mt-3 flex flex-wrap gap-2">
                    {debt > 0 && (
                      <Button size="sm" variant="outline" onClick={() => openForm({ kind: "transaction", defaults: { kind: "transfer" } })}>
                        Pagar tarjeta
                      </Button>
                    )}
                    {!scheduled && debt > 0 && (
                      <Button size="sm" variant="ghost" onClick={() => openForm({ kind: "obligation" })}>
                        Programar el pago
                      </Button>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </Card>
      {archivedCount > 0 && (
        <div className="flex justify-center">
          <Button variant="ghost" size="sm" onClick={() => setShowArchived((v) => !v)}>
            {showArchived ? "Ocultar archivadas" : `Ver ${archivedCount} archivada(s)`}
          </Button>
        </div>
      )}
    </SectionPage>
  );
}
