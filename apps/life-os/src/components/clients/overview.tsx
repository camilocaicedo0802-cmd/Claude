"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { AlarmClock, BriefcaseBusiness, CircleCheck, HandCoins, Plus, Search, TriangleAlert, UserPlus, Users } from "lucide-react";
import { useData, useJobViews, useMoney, useToday } from "@/hooks/data";
import { CLIENT_STATUS_LABEL, summarizeClients, totalReceivables, type ClientSummary } from "@/domain/clients";
import { diffDays, endOfMonth, formatRelativeDay, startOfMonth } from "@/lib/dates";
import { sumMinor } from "@/lib/money";
import { cn, matches } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input, NativeSelect } from "@/components/ui/form-controls";
import { Badge, Chip } from "@/components/ui/misc";
import { Card, CardHeader, EmptyState, MetricCard, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { PaymentBadge } from "./bits";

type ClientFilter = "all" | "active" | "lead" | "paused" | "inactive" | "balance" | "archived";
const FILTER_LABEL: Record<ClientFilter, string> = { all: "Todos", active: "Activos", lead: "Prospectos", paused: "En pausa", inactive: "Inactivos", balance: "Con saldo", archived: "Archivados" };

export function ClientsOverview() {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const views = useJobViews();
  const router = useRouter();
  const { openForm, openDetail } = useUI();
  const [query, setQuery] = React.useState("");
  const [filter, setFilter] = React.useState<ClientFilter>("all");
  const [sort, setSort] = React.useState<"activity" | "name" | "balance" | "billed">("activity");
  const listRef = React.useRef<HTMLDivElement>(null);

  const summaries = React.useMemo(() => summarizeClients(data.clients, views), [data.clients, views]);
  const live = views.filter((v) => !v.job.archived);
  const pending = live.filter((v) => v.isOpen);
  const dueSoon = pending.filter((v) => v.daysToDue !== null && v.daysToDue <= 3);
  const finished = live.filter((v) => v.kind === "done" || v.kind === "delivered");
  const receivable = totalReceivables(views);
  const overdue = views.filter((v) => v.finance.state === "overdue");
  const monthFrom = startOfMonth(today);
  const collectedMonth = sumMinor(data.clientPayments.filter((p) => p.date >= monthFrom && p.date <= endOfMonth(today)).map((p) => p.amount));
  const activeClients = data.clients.filter((c) => !c.archived && c.status === "active").length;

  // Clients that need a follow-up: overdue follow-up tasks, overdue collections, or owing money with no activity in 14 days.
  const attention = React.useMemo(() => {
    const out: Array<{ s: ClientSummary; reason: string; tone: "expense" | "warning" }> = [];
    for (const s of summaries) {
      if (s.client.archived) continue;
      const overdueFollow = data.tasks.find((t) => t.clientId === s.client.id && t.status === "todo" && t.date && t.date < today);
      const lateJob = s.jobs.find((j) => j.isOverdue && !j.job.archived);
      if (lateJob) out.push({ s, reason: `Entrega atrasada: ${lateJob.job.title}`, tone: "expense" });
      else if (s.overdue > 0) out.push({ s, reason: `Cobro vencido de ${money(s.overdue)}`, tone: "expense" });
      else if (overdueFollow) out.push({ s, reason: `Seguimiento pendiente: ${overdueFollow.title}`, tone: "warning" });
      else if (s.balance > 0 && diffDays(s.lastActivity.slice(0, 10), today) > 14) out.push({ s, reason: `Debe ${money(s.balance)} y no hay actividad hace más de 2 semanas`, tone: "warning" });
    }
    return out.slice(0, 6);
  }, [summaries, data.tasks, today, money]);

  const list = summaries
    .filter((s) => (filter === "archived" ? s.client.archived : !s.client.archived))
    .filter((s) => (filter === "all" || filter === "archived" ? true : filter === "balance" ? s.balance > 0 : s.client.status === filter))
    .filter((s) => matches([s.client.name, s.client.company, s.client.serviceType, s.client.email, s.client.phone, ...s.client.tags], query))
    .sort((a, b) =>
      sort === "name"
        ? a.client.name.localeCompare(b.client.name)
        : sort === "balance"
          ? b.balance - a.balance
          : sort === "billed"
            ? b.billed - a.billed
            : b.lastActivity.localeCompare(a.lastActivity),
    );
  const top = summaries.filter((s) => s.billed > 0).sort((a, b) => b.billed - a.billed).slice(0, 5);
  const maxBilled = Math.max(1, ...top.map((t) => t.billed));

  const focusList = (f: ClientFilter) => {
    setFilter(f);
    listRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <SectionPage
      section="clientes"
      title="Clientes"
      description="Quién te debe, qué tienes que entregar y a quién hacerle seguimiento."
      actions={
        <>
          <Button variant="outline" onClick={() => openForm({ kind: "client" })}>
            <UserPlus /> Cliente
          </Button>
          <Button onClick={() => openForm({ kind: "job" })}>
            <Plus /> Trabajo
          </Button>
        </>
      }
    >
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        <MetricCard emphasis label="Por cobrar" value={<Money amount={receivable} />} hint="Cuentas por cobrar · no es saldo líquido" icon={<HandCoins />} tone="brand" href="/clientes/cobros/" />
        <MetricCard
          emphasis
          label="Pagos vencidos"
          value={<Money amount={sumMinor(overdue.map((v) => v.finance.balance))} className={overdue.length ? "text-expense" : ""} />}
          hint={`${overdue.length} trabajo(s) con fecha de cobro pasada`}
          icon={<TriangleAlert />}
          tone="expense"
          href="/clientes/cobros/?filtro=vencidos"
        />
        <MetricCard emphasis label="Cobrado este mes" value={<Money amount={collectedMonth} />} hint="Pagos de clientes recibidos" icon={<CircleCheck />} tone="income" href="/clientes/cobros/" className="col-span-2 lg:col-span-1" />
      </div>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <MetricCard label="Clientes activos" value={activeClients} icon={<Users />} onClick={() => focusList("active")} />
        <MetricCard label="Trabajos pendientes" value={pending.length} hint="Nuevos, por iniciar, en proceso o revisión" icon={<BriefcaseBusiness />} href="/clientes/trabajos/?filtro=pendientes" />
        <MetricCard label="Próximos a vencer" value={<span className={dueSoon.length ? "text-warning" : ""}>{dueSoon.length}</span>} hint="Entrega en 3 días o atrasados" icon={<AlarmClock />} tone="warning" href="/clientes/trabajos/?filtro=proximos" />
        <MetricCard label="Terminados" value={finished.length} hint="Terminados o entregados" icon={<CircleCheck />} href="/clientes/trabajos/?filtro=terminados" />
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardHeader title="Necesitan atención" description="Atrasos, cobros vencidos y seguimientos" />
          {attention.length === 0 ? (
            <p className="px-5 pb-5 text-[13px] text-muted-foreground">Nada urgente con tus clientes. Buen trabajo.</p>
          ) : (
            <ul className="px-2 pb-2 sm:px-3">
              {attention.map(({ s, reason, tone }) => (
                <li key={s.client.id}>
                  <button type="button" onClick={() => openDetail({ type: "client", id: s.client.id })} className="flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left hover:bg-accent">
                    <span className={cn("size-2 shrink-0 rounded-full", tone === "expense" ? "bg-expense" : "bg-warning")} aria-hidden />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">{s.client.name}</span>
                      <span className="block truncate text-xs text-muted-foreground">{reason}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <CardHeader title="Mayor facturación" description="Total acordado en trabajos (sin cancelados)" />
          {top.length === 0 ? (
            <p className="px-5 pb-5 text-[13px] text-muted-foreground">Aparecerá cuando registres trabajos con precio.</p>
          ) : (
            <ul className="space-y-3 px-4 pb-5 sm:px-5">
              {top.map((t) => (
                <li key={t.client.id}>
                  <button type="button" className="block w-full text-left" onClick={() => openDetail({ type: "client", id: t.client.id })}>
                    <div className="flex items-baseline justify-between gap-2 text-[13px]">
                      <span className="truncate font-medium">{t.client.name}</span>
                      <span className="tabular">
                        {money(t.billed)} <span className="text-xs text-muted-foreground">· cobrado {Math.round((t.collected / Math.max(1, t.billed)) * 100)} %</span>
                      </span>
                    </div>
                    <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-muted">
                      <div className="flex h-full" style={{ width: `${(t.billed / maxBilled) * 100}%` }}>
                        <div className="h-full bg-income" style={{ width: `${(t.collected / Math.max(1, t.billed)) * 100}%` }} />
                        <div className="h-full flex-1 bg-chart-1/40" />
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div ref={listRef} className="scroll-mt-20 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-[15px] font-semibold">Directorio</h2>
          <NativeSelect aria-label="Ordenar" className="w-48" value={sort} onChange={(e) => setSort(e.target.value as typeof sort)}>
            <option value="activity">Actividad reciente</option>
            <option value="name">Nombre</option>
            <option value="balance">Saldo pendiente</option>
            <option value="billed">Facturación</option>
          </NativeSelect>
        </div>
        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar por nombre, empresa, servicio o etiqueta" className="pl-9" aria-label="Buscar clientes" />
        </div>
        <div className="no-scrollbar -mx-4 flex gap-1.5 overflow-x-auto px-4 sm:mx-0 sm:flex-wrap sm:px-0">
          {(Object.keys(FILTER_LABEL) as ClientFilter[]).map((f) => (
            <Chip key={f} active={filter === f} onClick={() => setFilter(f)}>
              {FILTER_LABEL[f]}
            </Chip>
          ))}
        </div>
        {list.length === 0 ? (
          <Card>
            <EmptyState
              icon={<Users />}
              title={data.clients.length === 0 ? "Aún no tienes clientes" : "Ningún cliente coincide"}
              description={data.clients.length === 0 ? "Agrega a quienes te compran o contratan. Luego crea sus trabajos con precio, fecha de entrega y anticipo." : "Cambia el filtro o la búsqueda."}
              action={
                data.clients.length === 0 ? (
                  <Button onClick={() => openForm({ kind: "client" })}>
                    <UserPlus /> Agregar cliente
                  </Button>
                ) : undefined
              }
            />
          </Card>
        ) : (
          <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
            {list.map((s) => {
              const worst = s.jobs.find((j) => j.finance.state === "overdue") ?? s.jobs.find((j) => j.finance.balance > 0);
              const nextDue = s.jobs.filter((j) => j.isOpen && j.job.dueDate).sort((a, b) => a.job.dueDate!.localeCompare(b.job.dueDate!))[0];
              return (
                <button
                  key={s.client.id}
                  type="button"
                  onClick={() => openDetail({ type: "client", id: s.client.id })}
                  className="press flex flex-col rounded-xl border border-border bg-card p-4 text-left shadow-[var(--shadow-card)] transition-colors hover:border-border-strong"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold">{s.client.name}</p>
                      <p className="truncate text-xs text-muted-foreground">{[s.client.company, s.client.serviceType].filter(Boolean).join(" · ") || "Sin detalles"}</p>
                    </div>
                    <Badge tone={s.client.status === "active" ? "income" : s.client.status === "lead" ? "brand" : "neutral"}>{CLIENT_STATUS_LABEL[s.client.status]}</Badge>
                  </div>
                  <div className="mt-3 flex items-end justify-between gap-2 text-[13px]">
                    <div className="text-muted-foreground">
                      {s.openJobs} {s.openJobs === 1 ? "trabajo abierto" : "trabajos abiertos"}
                      {nextDue && <span className="block text-xs">Próxima entrega {formatRelativeDay(nextDue.job.dueDate!, today).toLowerCase()}</span>}
                    </div>
                    {s.balance > 0 ? (
                      <div className="text-right">
                        <Money amount={s.balance} className="block font-semibold" />
                        {worst && <PaymentBadge state={worst.finance.state} className="mt-1" />}
                      </div>
                    ) : (
                      <span className="text-xs text-subtle">Al día</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
      <Button variant="link" className="mx-auto block" onClick={() => router.push("/clientes/trabajos/")}>
        Ver tablero de trabajos
      </Button>
    </SectionPage>
  );
}
