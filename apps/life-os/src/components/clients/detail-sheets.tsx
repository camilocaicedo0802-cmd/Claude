"use client";

import * as React from "react";
import {
  Archive,
  ArchiveRestore,
  CalendarPlus,
  Check,
  HandCoins,
  Link2,
  ListPlus,
  Mail,
  MessageCircle,
  Pencil,
  Phone,
  Plus,
  StickyNote,
} from "lucide-react";
import { useData, useJobViews, useMoney, useToday } from "@/hooks/data";
import { useUI } from "@/components/shell/ui-context";
import { Sheet } from "@/components/ui/overlays";
import { Button } from "@/components/ui/button";
import { Badge, Progress } from "@/components/ui/misc";
import { Input, NativeSelect } from "@/components/ui/form-controls";
import { Money, SectionTitle } from "@/components/shared/primitives";
import { runSave } from "@/components/forms/form-kit";
import { addClientNote, setJobStatus, updateClient, updateJob } from "@/services/clients-service";
import { setTaskDone } from "@/services/life-service";
import { CLIENT_STATUS_LABEL, PAYMENT_KIND_LABEL, summarizeClients } from "@/domain/clients";
import { formatDateNumeric, formatDateShort, formatRelativeDay, instantToDate } from "@/lib/dates";
import { cn, whatsappLink } from "@/lib/utils";
import { DueLabel, JobCard, PaymentBadge, PriorityFlag, StatusBadge } from "./bits";
import { FOLLOWUP_LABEL } from "@/components/forms/life-forms";

export function DetailHost() {
  const { detail, closeDetail } = useUI();
  const [open, setOpen] = React.useState(false);
  const [current, setCurrent] = React.useState(detail);
  React.useEffect(() => {
    if (detail) {
      setCurrent(detail);
      setOpen(true);
    } else setOpen(false);
  }, [detail]);
  if (!current) return null;
  const onOpenChange = (v: boolean) => {
    if (!v) {
      setOpen(false);
      setTimeout(closeDetail, 180);
    }
  };
  return current.type === "client" ? (
    <ClientSheet id={current.id} open={open} onOpenChange={onOpenChange} />
  ) : (
    <JobSheet id={current.id} open={open} onOpenChange={onOpenChange} />
  );
}

function ActivityList({ items }: { items: Array<{ id: string; at: string; message: string; type: string }> }) {
  const tz = useData().settings.timeZone;
  if (items.length === 0) return <p className="text-[13px] text-muted-foreground">Sin actividad todavía.</p>;
  return (
    <ol className="relative space-y-3 border-l border-border pl-4">
      {items.map((a) => (
        <li key={a.id} className="relative">
          <span className={cn("absolute top-1.5 -left-[21px] size-2 rounded-full border-2 border-popover", a.type === "payment" ? "bg-income" : a.type === "note" ? "bg-brand" : "bg-border-strong")} aria-hidden />
          <p className={cn("text-[13px]", a.type === "note" && "whitespace-pre-wrap")}>{a.message}</p>
          <p className="text-xs text-subtle tabular">{formatDateNumeric(instantToDate(a.at, tz))}</p>
        </li>
      ))}
    </ol>
  );
}

// ── Job sheet ────────────────────────────────────────────────────────────────

function JobSheet({ id, open, onOpenChange }: { id: string; open: boolean; onOpenChange: (v: boolean) => void }) {
  const data = useData();
  const views = useJobViews();
  const today = useToday();
  const money = useMoney();
  const { openForm, openDetail } = useUI();
  const view = views.find((v) => v.job.id === id);
  if (!view) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange} title="Trabajo no encontrado">
        <p className="text-sm text-muted-foreground">Este trabajo ya no existe.</p>
      </Sheet>
    );
  }
  const { job, finance } = view;
  const tasks = data.tasks.filter((t) => t.jobId === job.id).sort((a, b) => (a.status === b.status ? (a.date ?? "9").localeCompare(b.date ?? "9") : a.status === "todo" ? -1 : 1));
  const activity = data.activities.filter((a) => a.jobId === job.id).slice(0, 12);
  const paidPct = job.price > 0 ? (finance.paid / job.price) * 100 : 0;

  return (
    <Sheet
      open={open}
      onOpenChange={onOpenChange}
      wide
      title={job.title}
      description={
        <button type="button" className="hover:text-foreground hover:underline" onClick={() => openDetail({ type: "client", id: job.clientId })}>
          {view.client?.name ?? "Cliente"}
          {view.client?.company ? ` · ${view.client.company}` : ""}
        </button>
      }
      headerExtra={
        <Button variant="ghost" size="icon-sm" aria-label="Editar trabajo" className="-mt-1" onClick={() => openForm({ kind: "job", id: job.id })}>
          <Pencil />
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex flex-wrap items-center gap-2">
          <NativeSelect
            aria-label="Estado de producción"
            className="w-[200px]"
            value={job.statusId}
            onChange={(e) => runSave(() => setJobStatus(job.id, e.target.value), "Estado actualizado")}
          >
            {data.jobStatuses.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </NativeSelect>
          <PriorityFlag priority={job.priority} />
          {job.archived && <Badge tone="outline">Archivado</Badge>}
        </div>

        <section className="rounded-xl border border-border p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-[13px] text-muted-foreground">Saldo pendiente</div>
              <Money amount={finance.balance} className="mt-0.5 block text-2xl font-semibold tracking-tight" />
            </div>
            <PaymentBadge state={finance.state} />
          </div>
          <Progress value={paidPct} tone="income" className="mt-3" label="Porcentaje cobrado" />
          <dl className="mt-3 grid grid-cols-2 gap-2 text-[13px]">
            <div>
              <dt className="text-muted-foreground">Precio acordado</dt>
              <dd className="tabular font-medium">{money(job.price)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Cobrado</dt>
              <dd className="tabular font-medium text-income">{money(finance.paid)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Entrega</dt>
              <dd>
                <DueLabel view={view} />
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Fecha de cobro</dt>
              <dd className={cn("text-xs", finance.state === "overdue" && "font-medium text-expense")}>
                {job.paymentDueDate ? formatRelativeDay(job.paymentDueDate, today) : "Sin definir"}
              </dd>
            </div>
          </dl>
          {finance.balance > 0 && view.kind !== "cancelled" && (
            <Button className="mt-4 w-full" variant="income" onClick={() => openForm({ kind: "payment", defaults: { jobId: job.id } })}>
              <HandCoins /> Registrar pago
            </Button>
          )}
        </section>

        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" onClick={() => openForm({ kind: "task", defaults: { clientId: job.clientId, jobId: job.id, area: "clientes", title: "" } })}>
            <ListPlus /> Crear tarea
          </Button>
          <Button variant="outline" onClick={() => openForm({ kind: "event", defaults: { clientId: job.clientId, jobId: job.id, category: "clientes", title: `${job.title}` } })}>
            <CalendarPlus /> Agendar
          </Button>
        </div>

        <section>
          <SectionTitle>Pagos</SectionTitle>
          {finance.payments.length === 0 ? (
            <p className="text-[13px] text-muted-foreground">Aún no hay pagos registrados.</p>
          ) : (
            <ul className="divide-y divide-border rounded-lg border border-border">
              {finance.payments.map((p) => (
                <li key={p.id}>
                  <button type="button" onClick={() => openForm({ kind: "payment", id: p.id })} className="flex w-full items-center gap-3 px-3 py-2.5 text-left hover:bg-accent">
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium">{PAYMENT_KIND_LABEL[p.kind]}</div>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        {formatDateShort(p.date)}
                        {p.transactionId ? (
                          <span className="inline-flex items-center gap-1 text-info">
                            <Link2 className="size-3" /> en Finanzas
                          </span>
                        ) : (
                          <span>· sin cuenta receptora</span>
                        )}
                      </div>
                    </div>
                    <Money amount={p.amount} tone="income" className="text-sm font-medium" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <SectionTitle
            action={
              <Button variant="ghost" size="sm" onClick={() => openForm({ kind: "task", defaults: { clientId: job.clientId, jobId: job.id, area: "clientes" } })}>
                <Plus /> Tarea
              </Button>
            }
          >
            Tareas del trabajo
          </SectionTitle>
          {tasks.length === 0 ? (
            <p className="text-[13px] text-muted-foreground">Divide el trabajo en tareas para verlas en tu día.</p>
          ) : (
            <ul className="space-y-1">
              {tasks.map((t) => (
                <li key={t.id} className="flex items-center gap-2.5 rounded-lg px-1 py-1.5 hover:bg-accent">
                  <button
                    type="button"
                    aria-label={t.status === "done" ? "Marcar como pendiente" : "Completar"}
                    onClick={() => runSave(() => setTaskDone(t.id, t.status !== "done"))}
                    className={cn("flex size-5 shrink-0 items-center justify-center rounded-full border-2", t.status === "done" ? "border-income bg-income text-white" : "border-border-strong hover:border-income")}
                  >
                    {t.status === "done" && <Check className="size-3" strokeWidth={3} />}
                  </button>
                  <button type="button" className="min-w-0 flex-1 text-left" onClick={() => openForm({ kind: "task", id: t.id })}>
                    <span className={cn("block truncate text-sm", t.status === "done" && "text-muted-foreground line-through")}>{t.title}</span>
                    {t.date && <span className="text-xs text-muted-foreground">{formatRelativeDay(t.date, today)}</span>}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        {(job.description || job.notes) && (
          <section className="space-y-2">
            <SectionTitle>Descripción y notas</SectionTitle>
            {job.description && <p className="text-sm whitespace-pre-wrap">{job.description}</p>}
            {job.notes && <p className="rounded-lg bg-muted p-3 text-[13px] whitespace-pre-wrap">{job.notes}</p>}
          </section>
        )}

        <section>
          <SectionTitle>Historial</SectionTitle>
          <ActivityList items={activity} />
        </section>

        <Button variant="ghost" className="w-full text-muted-foreground" onClick={() => runSave(() => updateJob(job.id, { archived: !job.archived }), job.archived ? "Trabajo restaurado" : "Trabajo archivado")}>
          {job.archived ? <ArchiveRestore /> : <Archive />}
          {job.archived ? "Restaurar trabajo" : "Archivar trabajo (se conserva su historial)"}
        </Button>
      </div>
    </Sheet>
  );
}

// ── Client sheet ─────────────────────────────────────────────────────────────

function ClientSheet({ id, open, onOpenChange }: { id: string; open: boolean; onOpenChange: (v: boolean) => void }) {
  const data = useData();
  const views = useJobViews();
  const money = useMoney();
  const today = useToday();
  const { openForm, openDetail } = useUI();
  const [note, setNote] = React.useState("");
  const client = data.clients.find((c) => c.id === id);
  const summary = React.useMemo(() => (client ? summarizeClients([client], views)[0] : undefined), [client, views]);
  if (!client || !summary) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange} title="Cliente no encontrado">
        <p className="text-sm text-muted-foreground">Este cliente ya no existe.</p>
      </Sheet>
    );
  }
  const jobs = summary.jobs.sort((a, b) => Number(b.isOpen) - Number(a.isOpen) || (a.job.dueDate ?? "9").localeCompare(b.job.dueDate ?? "9"));
  const payments = data.clientPayments.filter((p) => p.clientId === id).sort((a, b) => b.date.localeCompare(a.date));
  const followUps = data.tasks.filter((t) => t.clientId === id && t.status === "todo");
  const activity = data.activities.filter((a) => a.clientId === id).slice(0, 20);
  const jobTitle = (jobId: string) => data.jobs.find((j) => j.id === jobId)?.title ?? "";

  return (
    <Sheet
      open={open}
      onOpenChange={onOpenChange}
      wide
      title={client.name}
      description={[client.company, client.serviceType].filter(Boolean).join(" · ") || undefined}
      headerExtra={
        <Button variant="ghost" size="icon-sm" aria-label="Editar cliente" className="-mt-1" onClick={() => openForm({ kind: "client", id: client.id })}>
          <Pencil />
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone={client.status === "active" ? "income" : client.status === "lead" ? "brand" : "neutral"}>{CLIENT_STATUS_LABEL[client.status]}</Badge>
          {client.archived && <Badge tone="outline">Archivado</Badge>}
          {client.tags.map((t) => (
            <Badge key={t} tone="outline">
              {t}
            </Badge>
          ))}
        </div>

        {(client.phone || client.whatsapp || client.email) && (
          <div className="grid grid-cols-3 gap-2">
            <Button variant="outline" asChild disabled={!client.phone}>
              <a href={client.phone ? `tel:${client.phone}` : undefined} aria-disabled={!client.phone}>
                <Phone /> Llamar
              </a>
            </Button>
            <Button variant="outline" asChild>
              <a href={client.whatsapp ? whatsappLink(client.whatsapp) : undefined} target="_blank" rel="noreferrer" aria-disabled={!client.whatsapp}>
                <MessageCircle /> WhatsApp
              </a>
            </Button>
            <Button variant="outline" asChild>
              <a href={client.email ? `mailto:${client.email}` : undefined} aria-disabled={!client.email}>
                <Mail /> Correo
              </a>
            </Button>
          </div>
        )}

        <dl className="grid grid-cols-3 gap-2">
          {[
            { label: "Facturado", value: summary.billed, cls: "" },
            { label: "Cobrado", value: summary.collected, cls: "text-income" },
            { label: "Por cobrar", value: summary.balance, cls: summary.overdue > 0 ? "text-expense" : "" },
          ].map((m) => (
            <div key={m.label} className="rounded-lg border border-border p-3">
              <dt className="text-xs text-muted-foreground">{m.label}</dt>
              <dd className={cn("mt-0.5 tabular text-[15px] font-semibold", m.cls)}>{money(m.value, { compact: m.value >= 100_000_000_00 })}</dd>
            </div>
          ))}
        </dl>
        {summary.overdue > 0 && <p className="-mt-3 text-xs text-expense">{money(summary.overdue)} con fecha de cobro vencida.</p>}

        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          <Button onClick={() => openForm({ kind: "job", defaults: { clientId: client.id } })}>
            <Plus /> Trabajo
          </Button>
          <Button variant="outline" onClick={() => openForm({ kind: "payment", defaults: { clientId: client.id } })} disabled={summary.balance <= 0}>
            <HandCoins /> Pago
          </Button>
          <Button variant="outline" className="col-span-2 sm:col-span-1" onClick={() => openForm({ kind: "task", defaults: { clientId: client.id, area: "clientes", followUp: "contact", title: `Contactar a ${client.name}` } })}>
            <CalendarPlus /> Seguimiento
          </Button>
        </div>

        <section>
          <SectionTitle>Trabajos ({jobs.length})</SectionTitle>
          {jobs.length === 0 ? (
            <p className="text-[13px] text-muted-foreground">Sin trabajos todavía.</p>
          ) : (
            <div className="grid gap-2 sm:grid-cols-2">
              {jobs.map((v) => (
                <div key={v.job.id} className="relative">
                  <JobCard view={v} showClient={false} onOpen={() => openDetail({ type: "job", id: v.job.id })} />
                  <StatusBadge status={v.status} className="absolute top-2.5 right-2.5" />
                </div>
              ))}
            </div>
          )}
        </section>

        {followUps.length > 0 && (
          <section>
            <SectionTitle>Seguimientos pendientes</SectionTitle>
            <ul className="space-y-1">
              {followUps.map((t) => (
                <li key={t.id}>
                  <button type="button" onClick={() => openForm({ kind: "task", id: t.id })} className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-accent">
                    <span className="min-w-0 flex-1 truncate text-sm">{t.title}</span>
                    <span className="text-xs text-muted-foreground">{t.followUp ? FOLLOWUP_LABEL[t.followUp] : ""}</span>
                    {t.date && <span className={cn("text-xs tabular", t.date < today ? "text-expense" : "text-muted-foreground")}>{formatRelativeDay(t.date, today)}</span>}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        <section>
          <SectionTitle>Historial de pagos</SectionTitle>
          {payments.length === 0 ? (
            <p className="text-[13px] text-muted-foreground">Sin pagos registrados.</p>
          ) : (
            <ul className="divide-y divide-border rounded-lg border border-border">
              {payments.map((p) => (
                <li key={p.id}>
                  <button type="button" onClick={() => openForm({ kind: "payment", id: p.id })} className="flex w-full items-center gap-3 px-3 py-2 text-left hover:bg-accent">
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm">{jobTitle(p.jobId)}</div>
                      <div className="text-xs text-muted-foreground">
                        {PAYMENT_KIND_LABEL[p.kind]} · {formatDateShort(p.date)}
                      </div>
                    </div>
                    <Money amount={p.amount} tone="income" className="text-sm font-medium" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        {client.notes && (
          <section>
            <SectionTitle>Notas importantes</SectionTitle>
            <p className="rounded-lg bg-muted p-3 text-[13px] whitespace-pre-wrap">{client.notes}</p>
          </section>
        )}

        <section>
          <SectionTitle>Actividad</SectionTitle>
          <form
            className="mb-4 flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              if (!note.trim()) return;
              void runSave(() => addClientNote(client.id, note), "Nota agregada").then((ok) => ok && setNote(""));
            }}
          >
            <Input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Escribe una nota rápida…" aria-label="Nueva nota" />
            <Button type="submit" variant="outline" size="icon" aria-label="Agregar nota">
              <StickyNote />
            </Button>
          </form>
          <ActivityList items={activity} />
        </section>

        <Button
          variant="ghost"
          className="w-full text-muted-foreground"
          onClick={() => runSave(() => updateClient(client.id, { archived: !client.archived, status: client.archived ? client.status : "inactive" }), client.archived ? "Cliente restaurado" : "Cliente archivado")}
        >
          {client.archived ? <ArchiveRestore /> : <Archive />}
          {client.archived ? "Restaurar cliente" : "Archivar cliente (conserva trabajos y pagos)"}
        </Button>
      </div>
    </Sheet>
  );
}
