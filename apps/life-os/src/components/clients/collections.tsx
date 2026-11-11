"use client";

import * as React from "react";
import { BellRing, HandCoins, Link2, MessageCircle, Plus } from "lucide-react";
import { useData, useJobViews, useMoney, useToday } from "@/hooks/data";
import { PAYMENT_KIND_LABEL, summarizeClients, totalReceivables } from "@/domain/clients";
import { addDays, endOfMonth, formatRelativeDay, startOfMonth } from "@/lib/dates";
import { sumMinor } from "@/lib/money";
import { cn, whatsappLink } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Chip } from "@/components/ui/misc";
import { Card, CardHeader, EmptyState, MetricCard, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { createTask } from "@/services/life-service";
import { PaymentBadge } from "./bits";

export function CollectionsPage() {
  const data = useData();
  const views = useJobViews();
  const today = useToday();
  const money = useMoney();
  const { openForm, openDetail } = useUI();
  const [filter, setFilter] = React.useState<"all" | "vencidos" | "proximos">("all");
  React.useEffect(() => {
    if (new URLSearchParams(window.location.search).get("filtro") === "vencidos") setFilter("vencidos");
  }, []);

  const receivables = views
    .filter((v) => v.finance.balance > 0 && v.kind !== "cancelled")
    .filter((v) => (filter === "vencidos" ? v.finance.state === "overdue" : filter === "proximos" ? !!v.job.paymentDueDate && v.job.paymentDueDate >= today && v.job.paymentDueDate <= addDays(today, 7) : true))
    .sort((a, b) => Number(b.finance.state === "overdue") - Number(a.finance.state === "overdue") || (a.job.paymentDueDate ?? "9999").localeCompare(b.job.paymentDueDate ?? "9999"));
  const monthFrom = startOfMonth(today);
  const monthTo = endOfMonth(today);
  const collectedMonth = sumMinor(data.clientPayments.filter((p) => p.date >= monthFrom && p.date <= monthTo).map((p) => p.amount));
  const billedMonth = sumMinor(views.filter((v) => v.kind !== "cancelled" && v.job.requestedAt >= monthFrom && v.job.requestedAt <= monthTo).map((v) => v.job.price));
  const overdueTotal = sumMinor(views.filter((v) => v.finance.state === "overdue").map((v) => v.finance.balance));
  const payments = [...data.clientPayments].sort((a, b) => b.date.localeCompare(a.date) || b.createdAt.localeCompare(a.createdAt)).slice(0, 15);
  const byClient = summarizeClients(data.clients, views)
    .filter((s) => s.billed > 0 || s.collected > 0)
    .sort((a, b) => b.billed - a.billed);
  const jobById = new Map(data.jobs.map((j) => [j.id, j]));
  const clientById = new Map(data.clients.map((c) => [c.id, c]));

  const remind = (jobId: string) => {
    const v = views.find((x) => x.job.id === jobId);
    if (!v) return;
    void runSave(
      () => createTask({ title: `Cobrar saldo: ${v.job.title}`, date: today, clientId: v.job.clientId, jobId: v.job.id, followUp: "collect", area: "clientes", priority: 2 }),
      "Recordatorio de cobro agregado a tu día",
    );
  };

  return (
    <SectionPage
      section="clientes"
      title="Cobros"
      description="Lo que te deben es una cuenta por cobrar: solo se vuelve dinero cuando registras el pago."
      actions={
        <Button onClick={() => openForm({ kind: "payment" })}>
          <HandCoins /> Registrar pago
        </Button>
      }
    >
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard label="Por cobrar" value={<Money amount={totalReceivables(views)} />} hint="Saldo pendiente total" />
        <MetricCard label="Vencido" value={<Money amount={overdueTotal} className={overdueTotal ? "text-expense" : ""} />} hint="Fecha de cobro pasada" />
        <MetricCard label="Facturado este mes" value={<Money amount={billedMonth} />} hint="Trabajos solicitados este mes" />
        <MetricCard label="Cobrado este mes" value={<Money amount={collectedMonth} tone="income" />} hint="Pagos recibidos" />
      </div>

      <div className="flex gap-1.5">
        <Chip active={filter === "all"} onClick={() => setFilter("all")}>
          Todos
        </Chip>
        <Chip active={filter === "vencidos"} onClick={() => setFilter("vencidos")}>
          Vencidos
        </Chip>
        <Chip active={filter === "proximos"} onClick={() => setFilter("proximos")}>
          Próximos 7 días
        </Chip>
      </div>

      <Card>
        <CardHeader title="Cuentas por cobrar" description={`${receivables.length} trabajo(s) con saldo`} />
        {receivables.length === 0 ? (
          <EmptyState compact icon={<HandCoins />} title={filter === "all" ? "Nadie te debe dinero" : "Nada en este filtro"} description="Cuando un trabajo tenga saldo pendiente aparecerá aquí con su fecha de cobro." />
        ) : (
          <ul className="divide-y divide-border">
            {receivables.map((v) => {
              const client = v.client;
              const msg = `Hola ${client?.name.split(" ")[0] ?? ""}, te escribo para recordarte el saldo pendiente de ${money(v.finance.balance)} por "${v.job.title}". ¡Gracias!`;
              return (
                <li key={v.job.id} className="flex flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:px-5">
                  <button type="button" className="min-w-0 flex-1 text-left" onClick={() => openDetail({ type: "job", id: v.job.id })}>
                    <span className="block truncate text-sm font-medium">{client?.name ?? "Cliente"}</span>
                    <span className="block truncate text-xs text-muted-foreground">
                      {v.job.title} · pagado {money(v.finance.paid)} de {money(v.job.price)}
                    </span>
                    <span className={cn("mt-0.5 block text-xs", v.finance.state === "overdue" ? "font-medium text-expense" : "text-muted-foreground")}>
                      {v.job.paymentDueDate ? `Cobro ${formatRelativeDay(v.job.paymentDueDate, today).toLowerCase()}` : "Sin fecha de cobro"}
                    </span>
                  </button>
                  <div className="flex items-center justify-between gap-2 sm:justify-end">
                    <div className="flex flex-col items-start sm:items-end">
                      <Money amount={v.finance.balance} className="text-[15px] font-semibold" />
                      <PaymentBadge state={v.finance.state} />
                    </div>
                    <div className="flex items-center gap-1">
                      {client?.whatsapp && (
                        <Button variant="ghost" size="icon-sm" asChild aria-label="Recordar por WhatsApp">
                          <a href={whatsappLink(client.whatsapp, msg)} target="_blank" rel="noreferrer">
                            <MessageCircle />
                          </a>
                        </Button>
                      )}
                      <Button variant="ghost" size="icon-sm" aria-label="Crear recordatorio de cobro" onClick={() => remind(v.job.id)}>
                        <BellRing />
                      </Button>
                      <Button size="sm" variant="income" onClick={() => openForm({ kind: "payment", defaults: { jobId: v.job.id } })}>
                        Cobrar
                      </Button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader title="Pagos recibidos" description="Con cuenta receptora se reflejan en Finanzas (sin duplicar)" />
          {payments.length === 0 ? (
            <EmptyState
              compact
              title="Sin pagos registrados"
              action={
                <Button size="sm" variant="outline" onClick={() => openForm({ kind: "payment" })}>
                  <Plus /> Registrar pago
                </Button>
              }
            />
          ) : (
            <ul className="px-2 pb-2 sm:px-3">
              {payments.map((p) => (
                <li key={p.id}>
                  <button type="button" onClick={() => openForm({ kind: "payment", id: p.id })} className="flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left hover:bg-accent">
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">{clientById.get(p.clientId)?.name}</span>
                      <span className="flex items-center gap-1.5 truncate text-xs text-muted-foreground">
                        {PAYMENT_KIND_LABEL[p.kind]} · {jobById.get(p.jobId)?.title} · {formatRelativeDay(p.date, today)}
                        {p.transactionId && <Link2 className="size-3 shrink-0 text-info" aria-label="Registrado en Finanzas" />}
                      </span>
                    </span>
                    <Money amount={p.amount} tone="income" className="text-sm font-semibold" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <CardHeader title="Ingresos por cliente" description="Facturado (acordado) frente a cobrado" />
          {byClient.length === 0 ? (
            <p className="px-5 pb-5 text-[13px] text-muted-foreground">Sin datos todavía.</p>
          ) : (
            <div className="overflow-x-auto px-4 pb-4 sm:px-5">
              <table className="w-full min-w-[360px] text-[13px]">
                <thead>
                  <tr className="text-left text-xs text-muted-foreground">
                    <th className="py-2 font-medium">Cliente</th>
                    <th className="py-2 text-right font-medium">Facturado</th>
                    <th className="py-2 text-right font-medium">Cobrado</th>
                    <th className="py-2 text-right font-medium">Pendiente</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {byClient.map((s) => (
                    <tr key={s.client.id} className="cursor-pointer hover:bg-accent/50" onClick={() => openDetail({ type: "client", id: s.client.id })}>
                      <td className="max-w-40 truncate py-2">{s.client.name}</td>
                      <td className="py-2 text-right tabular">{money(s.billed)}</td>
                      <td className="py-2 text-right tabular text-income">{money(s.collected)}</td>
                      <td className={cn("py-2 text-right tabular", s.balance > 0 && "font-medium")}>{money(s.balance)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </SectionPage>
  );
}
