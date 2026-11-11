"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";
import { useData, useMoney, useToday } from "@/hooks/data";
import {
  addClientPayment,
  createClient,
  createJob,
  deleteClientPayment,
  updateClient,
  updateClientPayment,
  updateJob,
  deleteJob,
} from "@/services/clients-service";
import { DomainError, errorMessage } from "@/services/common";
import type { ClientPayment, ClientStatus, Priority } from "@/db/types";
import { CLIENT_STATUS_LABEL, PAYMENT_KIND_LABEL, PRIORITY_LABEL, jobFinance, paymentsByJob } from "@/domain/clients";
import { addDays } from "@/lib/dates";
import { parseMoney } from "@/lib/money";
import { Field, Input, NativeSelect, Textarea, Checkbox } from "@/components/ui/form-controls";
import { Segmented } from "@/components/ui/misc";
import { Button } from "@/components/ui/button";
import { AccountSelect, AmountInput, DateField, amountToText } from "@/components/shared/inputs";
import { useUI } from "@/components/shell/ui-context";
import { Disclosure, FormSheet, lastAccount, rememberAccount, runSave, useBusy } from "./form-kit";

function useClosable(onDone: () => void) {
  const [open, setOpen] = React.useState(true);
  return { open, close: () => (setOpen(false), setTimeout(onDone, 180)) };
}

const parseTags = (s: string) =>
  [...new Set(s.split(",").map((t) => t.trim()).filter(Boolean))].slice(0, 12);

// ── Client ───────────────────────────────────────────────────────────────────

const clientSchema = z.object({
  name: z.string().trim().min(1, "Escribe el nombre del cliente"),
  company: z.string().optional(),
  phone: z.string().optional(),
  whatsapp: z.string().optional(),
  sameWhatsapp: z.boolean(),
  email: z.union([z.literal(""), z.string().email("Correo no válido")]).optional(),
  serviceType: z.string().optional(),
  status: z.enum(["lead", "active", "paused", "inactive"]),
  tags: z.string().optional(),
  notes: z.string().optional(),
});

export function ClientForm({ id, onDone }: { id?: string; onDone: () => void }) {
  const data = useData();
  const { openDetail } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.clients.find((c) => c.id === id) : undefined;
  const services = [...new Set(data.clients.map((c) => c.serviceType).filter(Boolean))] as string[];
  const form = useForm<z.infer<typeof clientSchema>>({
    resolver: zodResolver(clientSchema),
    defaultValues: {
      name: existing?.name ?? "",
      company: existing?.company ?? "",
      phone: existing?.phone ?? "",
      whatsapp: existing?.whatsapp ?? "",
      sameWhatsapp: existing ? !existing.whatsapp || existing.whatsapp === existing.phone : true,
      email: existing?.email ?? "",
      serviceType: existing?.serviceType ?? "",
      status: existing?.status ?? "active",
      tags: existing?.tags.join(", ") ?? "",
      notes: existing?.notes ?? "",
    },
  });
  const { register, handleSubmit, watch, setValue, formState } = form;
  const submit = handleSubmit((v) =>
    wrap(async () => {
      const payload = {
        name: v.name,
        company: v.company?.trim() || undefined,
        phone: v.phone?.trim() || undefined,
        whatsapp: (v.sameWhatsapp ? v.phone : v.whatsapp)?.trim() || undefined,
        email: v.email?.trim() || undefined,
        serviceType: v.serviceType?.trim() || undefined,
        status: v.status as ClientStatus,
        tags: parseTags(v.tags ?? ""),
        notes: v.notes?.trim() || undefined,
      };
      if (existing) {
        if (await runSave(() => updateClient(existing.id, payload), "Cliente actualizado")) close();
      } else {
        let newId = "";
        if (await runSave(async () => void (newId = await createClient(payload)), `${payload.name} agregado`)) {
          close();
          setTimeout(() => openDetail({ type: "client", id: newId }), 220);
        }
      }
    }),
  );
  return (
    <FormSheet open={open} onOpenChange={(v) => !v && close()} title={existing ? "Editar cliente" : "Nuevo cliente"} formId="client-form" busy={busy}>
      <form id="client-form" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Nombre" htmlFor="cl-name" error={formState.errors.name?.message}>
          <Input id="cl-name" autoFocus={!existing} autoComplete="off" placeholder="Ej. Laura Gómez" {...register("name")} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Empresa" htmlFor="cl-company" optional>
            <Input id="cl-company" {...register("company")} />
          </Field>
          <Field label="Tipo de servicio" htmlFor="cl-service" optional>
            <Input id="cl-service" list="service-types" placeholder="Ej. Edición de video" {...register("serviceType")} />
            <datalist id="service-types">
              {services.map((s) => (
                <option key={s} value={s} />
              ))}
            </datalist>
          </Field>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Teléfono" htmlFor="cl-phone" optional>
            <Input id="cl-phone" type="tel" inputMode="tel" autoComplete="off" {...register("phone")} />
          </Field>
          <Field label="Correo" htmlFor="cl-email" optional error={formState.errors.email?.message}>
            <Input id="cl-email" type="email" inputMode="email" autoComplete="off" {...register("email")} />
          </Field>
        </div>
        <label className="flex items-center gap-2.5 text-sm">
          <Checkbox checked={watch("sameWhatsapp")} onCheckedChange={(v) => setValue("sameWhatsapp", v === true)} />
          El WhatsApp es el mismo teléfono
        </label>
        {!watch("sameWhatsapp") && (
          <Field label="WhatsApp" htmlFor="cl-wa">
            <Input id="cl-wa" type="tel" inputMode="tel" {...register("whatsapp")} />
          </Field>
        )}
        <Field label="Estado de la relación">
          <Segmented
            className="w-full"
            size="sm"
            value={watch("status")}
            onChange={(s) => setValue("status", s)}
            options={(Object.keys(CLIENT_STATUS_LABEL) as ClientStatus[]).map((s) => ({ value: s, label: CLIENT_STATUS_LABEL[s] }))}
          />
        </Field>
        <Field label="Etiquetas" htmlFor="cl-tags" optional hint="Separadas por comas: recurrente, referido…">
          <Input id="cl-tags" {...register("tags")} />
        </Field>
        <Field label="Notas importantes" htmlFor="cl-notes" optional>
          <Textarea id="cl-notes" rows={3} {...register("notes")} />
        </Field>
      </form>
    </FormSheet>
  );
}

// ── Job ──────────────────────────────────────────────────────────────────────

const jobSchema = z.object({
  clientId: z.string(),
  newClientName: z.string().optional(),
  title: z.string().trim().min(1, "Describe el trabajo"),
  description: z.string().optional(),
  requestedAt: z.string().min(10),
  dueDate: z.string().nullable(),
  price: z.string().refine((s) => s.trim() === "" || (parseMoney(s) ?? -1) >= 0, "Precio no válido"),
  priority: z.enum(["low", "medium", "high", "urgent"]),
  statusId: z.string().min(1),
  paymentDueDate: z.string().nullable(),
  advance: z.string().optional(),
  advanceAccountId: z.string().optional(),
  notes: z.string().optional(),
  tags: z.string().optional(),
});

export function JobForm({ id, defaults, onDone }: { id?: string; defaults?: { clientId?: string; dueDate?: string }; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { openDetail, confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.jobs.find((j) => j.id === id) : undefined;
  const clients = data.clients.filter((c) => !c.archived || c.id === existing?.clientId);
  const form = useForm<z.infer<typeof jobSchema>>({
    resolver: zodResolver(jobSchema),
    defaultValues: {
      clientId: existing?.clientId ?? defaults?.clientId ?? (clients.length ? clients[0].id : "__new"),
      newClientName: "",
      title: existing?.title ?? "",
      description: existing?.description ?? "",
      requestedAt: existing?.requestedAt ?? today,
      dueDate: existing?.dueDate ?? defaults?.dueDate ?? null,
      price: existing ? amountToText(existing.price, data.settings.currency) : "",
      priority: existing?.priority ?? "medium",
      statusId: existing?.statusId ?? data.jobStatuses[0]?.id ?? "",
      paymentDueDate: existing?.paymentDueDate ?? null,
      advance: "",
      advanceAccountId: lastAccount("income") ?? data.accounts.find((a) => a.type === "bank" && !a.archived)?.id ?? "",
      notes: existing?.notes ?? "",
      tags: existing?.tags.join(", ") ?? "",
    },
  });
  const { register, handleSubmit, watch, setValue, formState, setError } = form;
  const clientId = watch("clientId");

  const applyTemplate = (templateId: string) => {
    const t = data.jobTemplates.find((x) => x.id === templateId);
    if (!t) return;
    setValue("title", t.name);
    setValue("description", t.description ?? "");
    setValue("price", amountToText(t.price, data.settings.currency));
    setValue("priority", t.priority);
    if (t.durationDays) setValue("dueDate", addDays(today, t.durationDays));
  };

  const submit = handleSubmit((v) =>
    wrap(async () => {
      let cid = v.clientId;
      if (cid === "__new") {
        if (!v.newClientName?.trim()) {
          setError("newClientName", { message: "Escribe el nombre del cliente" });
          return;
        }
      }
      const price = parseMoney(v.price) ?? 0;
      const advance = parseMoney(v.advance ?? "") ?? 0;
      if (advance > price) {
        setError("advance", { message: "El anticipo no puede superar el precio" });
        return;
      }
      const payload = {
        title: v.title,
        description: v.description?.trim() || undefined,
        requestedAt: v.requestedAt,
        dueDate: v.dueDate || null,
        price,
        priority: v.priority as Priority,
        statusId: v.statusId,
        paymentDueDate: v.paymentDueDate || null,
        notes: v.notes?.trim() || undefined,
        tags: parseTags(v.tags ?? ""),
      };
      if (existing) {
        if (await runSave(() => updateJob(existing.id, { ...payload, clientId: cid }), "Trabajo actualizado")) close();
        return;
      }
      let jobId = "";
      const ok = await runSave(async () => {
        if (cid === "__new") cid = await createClient({ name: v.newClientName!.trim(), status: "active", tags: [] });
        if (advance > 0 && v.advanceAccountId) rememberAccount("income", v.advanceAccountId);
        jobId = await createJob(
          { ...payload, clientId: cid },
          advance > 0 ? { amount: advance, date: today, accountId: v.advanceAccountId || null } : undefined,
        );
      }, advance > 0 ? `Trabajo creado con anticipo de ${money(advance)}` : "Trabajo creado");
      if (ok) {
        close();
        setTimeout(() => openDetail({ type: "job", id: jobId }), 220);
      }
    }),
  );

  const remove = async () => {
    if (!existing) return;
    const payments = data.clientPayments.filter((p) => p.jobId === existing.id);
    const ok = await confirm({
      title: `¿Eliminar «${existing.title}»?`,
      description: payments.length
        ? `Tiene ${payments.length} pago(s) registrados. Se anularán y sus ingresos vinculados se eliminarán de Finanzas. Si solo quieres sacarlo de la vista, archívalo.`
        : "Esta acción no se puede deshacer. Si solo quieres sacarlo de la vista, archívalo.",
      confirmLabel: "Eliminar",
      destructive: true,
    });
    if (ok && (await runSave(() => deleteJob(existing.id), "Trabajo eliminado"))) close();
  };

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar trabajo" : "Nuevo trabajo"}
      formId="job-form"
      busy={busy}
      extraActions={
        existing && (
          <Button variant="destructive-ghost" size="sm" onClick={remove}>
            <Trash2 /> Eliminar
          </Button>
        )
      }
    >
      <form id="job-form" onSubmit={submit} className="space-y-4" noValidate>
        {!existing && data.jobTemplates.length > 0 && (
          <Field label="Usar plantilla" htmlFor="job-template" optional>
            <NativeSelect id="job-template" defaultValue="" onChange={(e) => applyTemplate(e.target.value)}>
              <option value="">Sin plantilla</option>
              {data.jobTemplates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </NativeSelect>
          </Field>
        )}
        <Field label="Cliente" htmlFor="job-client">
          <NativeSelect id="job-client" {...register("clientId")}>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
                {c.company ? ` · ${c.company}` : ""}
              </option>
            ))}
            <option value="__new">+ Cliente nuevo…</option>
          </NativeSelect>
        </Field>
        {clientId === "__new" && (
          <Field label="Nombre del cliente nuevo" htmlFor="job-newclient" error={formState.errors.newClientName?.message}>
            <Input id="job-newclient" autoFocus {...register("newClientName")} />
          </Field>
        )}
        <Field label="Trabajo" htmlFor="job-title" error={formState.errors.title?.message}>
          <Input id="job-title" autoFocus={!existing && clientId !== "__new"} placeholder="Ej. Video institucional" {...register("title")} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Precio acordado" htmlFor="job-price" error={formState.errors.price?.message}>
            <AmountInput id="job-price" value={watch("price")} onChange={(v) => setValue("price", v)} />
          </Field>
          <Field label="Estado" htmlFor="job-status">
            <NativeSelect id="job-status" {...register("statusId")}>
              {data.jobStatuses.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </NativeSelect>
          </Field>
        </div>
        <Field label="Fecha de entrega" optional hint="Aparecerá en tu agenda y planificación semanal.">
          <DateField value={watch("dueDate")} onChange={(v) => setValue("dueDate", v)} quick={["tomorrow", "nextweek"]} allowEmpty />
        </Field>
        <Field label="Prioridad">
          <Segmented
            className="w-full"
            size="sm"
            value={watch("priority")}
            onChange={(p) => setValue("priority", p)}
            options={(Object.keys(PRIORITY_LABEL) as Priority[]).map((p) => ({ value: p, label: PRIORITY_LABEL[p] }))}
          />
        </Field>
        {!existing && (
          <div className="space-y-3 rounded-lg bg-muted/60 p-3">
            <Field label="Anticipo recibido" htmlFor="job-advance" optional error={formState.errors.advance?.message}>
              <AmountInput id="job-advance" value={watch("advance") ?? ""} onChange={(v) => setValue("advance", v)} />
            </Field>
            {(parseMoney(watch("advance") ?? "") ?? 0) > 0 && (
              <Field label="Cuenta donde lo recibiste" htmlFor="job-adv-acc" hint="Con cuenta se registra como ingreso real en Finanzas. Sin cuenta, solo como pago del cliente.">
                <AccountSelect id="job-adv-acc" allowNone noneLabel="No registrar en Finanzas" value={watch("advanceAccountId")} onChange={(v) => setValue("advanceAccountId", v ?? "")} filter={(a) => a.type !== "credit"} />
              </Field>
            )}
          </div>
        )}
        <Disclosure label="Más detalles" defaultOpen={!!(existing?.description || existing?.paymentDueDate || existing?.notes)}>
          <Field label="Descripción" htmlFor="job-desc" optional>
            <Textarea id="job-desc" rows={3} {...register("description")} />
          </Field>
          <Field label="Fecha de cobro del saldo" optional hint="Cuando pase esta fecha sin pago completo, se marcará como cobro vencido.">
            <DateField value={watch("paymentDueDate")} onChange={(v) => setValue("paymentDueDate", v)} quick={["nextweek"]} allowEmpty />
          </Field>
          <Field label="Fecha de solicitud">
            <Input type="date" {...register("requestedAt")} />
          </Field>
          <Field label="Etiquetas" htmlFor="job-tags" optional>
            <Input id="job-tags" placeholder="urgente, video…" {...register("tags")} />
          </Field>
          <Field label="Notas" htmlFor="job-notes" optional>
            <Textarea id="job-notes" rows={2} {...register("notes")} />
          </Field>
        </Disclosure>
      </form>
    </FormSheet>
  );
}

// ── Payment ──────────────────────────────────────────────────────────────────

export function PaymentForm({ id, defaults, onDone }: { id?: string; defaults?: { jobId?: string; clientId?: string }; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.clientPayments.find((p) => p.id === id) : undefined;
  const byJob = React.useMemo(() => paymentsByJob(data.clientPayments), [data.clientPayments]);
  const candidates = data.jobs
    .filter((j) => !j.archived && (!defaults?.clientId || j.clientId === defaults.clientId))
    .map((j) => ({ job: j, finance: jobFinance(j, byJob.get(j.id) ?? [], today) }))
    .filter((x) => x.finance.balance > 0 || x.job.id === existing?.jobId || x.job.id === defaults?.jobId);
  const [jobId, setJobId] = React.useState(existing?.jobId ?? defaults?.jobId ?? candidates[0]?.job.id ?? "");
  const selected = candidates.find((c) => c.job.id === jobId) ?? (jobId ? { job: data.jobs.find((j) => j.id === jobId)!, finance: jobFinance(data.jobs.find((j) => j.id === jobId)!, byJob.get(jobId) ?? [], today) } : undefined);
  const balance = selected ? selected.finance.balance + (existing ? existing.amount : 0) : 0;
  const [amount, setAmount] = React.useState(existing ? amountToText(existing.amount, data.settings.currency) : balance ? amountToText(balance, data.settings.currency) : "");
  const [date, setDate] = React.useState(existing?.date ?? today);
  const [accountId, setAccountId] = React.useState<string | null>(existing ? existing.accountId ?? null : lastAccount("income") ?? data.accounts.find((a) => a.type === "bank" && !a.archived)?.id ?? null);
  const [note, setNote] = React.useState(existing?.note ?? "");
  const [error, setError] = React.useState<string | null>(null);
  const clientName = (cid: string) => data.clients.find((c) => c.id === cid)?.name ?? "";

  React.useEffect(() => {
    if (existing || !selected) return;
    setAmount(selected.finance.balance ? amountToText(selected.finance.balance, data.settings.currency) : "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  if (candidates.length === 0 && !existing) {
    return (
      <FormSheet open={open} onOpenChange={(v) => !v && close()} title="Registrar pago" formId="payment-form" submitDisabled layout="center">
        <p className="py-4 text-sm text-muted-foreground">No hay trabajos con saldo pendiente. Crea un trabajo con su precio para registrar pagos.</p>
      </FormSheet>
    );
  }

  const value = parseMoney(amount) ?? 0;
  const kind: ClientPayment["kind"] = existing?.kind ?? (selected && selected.finance.paid === 0 && value < balance ? "advance" : value >= balance ? "final" : "partial");

  const save = async (adjustPrice = false): Promise<void> => {
    if (existing) {
      if (await runSave(() => updateClientPayment(existing.id, { amount: value, date, accountId, note }), "Pago actualizado")) close();
      return;
    }
    try {
      await addClientPayment({ jobId, amount: value, date, kind, accountId, note, adjustPrice });
      if (accountId) rememberAccount("income", accountId);
      toast.success(accountId ? `Pago de ${money(value)} registrado e ingresado en Finanzas` : `Pago de ${money(value)} registrado`);
      close();
    } catch (e) {
      if (e instanceof DomainError && e.code === "overpayment") {
        const excess = Number(e.data?.excess ?? 0);
        const ok = await confirm({
          title: "El pago supera el saldo pendiente",
          description: `Excede el precio acordado por ${money(excess)}. ¿Quieres ajustar el precio del trabajo a ${money((selected?.job.price ?? 0) + excess)} y registrar el pago completo?`,
          confirmLabel: "Ajustar precio y registrar",
        });
        if (ok) return save(true);
        return;
      }
      toast.error(errorMessage(e));
    }
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobId) return setError("Elige el trabajo");
    if (value <= 0) return setError("Ingresa un valor mayor que cero");
    setError(null);
    void wrap(() => save());
  };

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar pago" : "Registrar pago de cliente"}
      formId="payment-form"
      busy={busy}
      submitLabel={existing ? "Guardar cambios" : "Registrar pago"}
      extraActions={
        existing && (
          <Button
            variant="destructive-ghost"
            size="sm"
            onClick={async () => {
              const ok = await confirm({
                title: "¿Anular este pago?",
                description: existing.transactionId ? "También se eliminará el ingreso vinculado en Finanzas y el saldo volverá a quedar pendiente." : "El saldo del trabajo volverá a quedar pendiente.",
                confirmLabel: "Anular pago",
                destructive: true,
              });
              if (ok && (await runSave(() => deleteClientPayment(existing.id), "Pago anulado"))) close();
            }}
          >
            <Trash2 /> Anular
          </Button>
        )
      }
    >
      <form id="payment-form" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Trabajo" htmlFor="pm-job">
          <NativeSelect id="pm-job" value={jobId} onChange={(e) => setJobId(e.target.value)} disabled={!!existing}>
            {candidates.map(({ job, finance }) => (
              <option key={job.id} value={job.id}>
                {clientName(job.clientId)} · {job.title} ({money(finance.balance)} pendiente)
              </option>
            ))}
          </NativeSelect>
        </Field>
        <Field
          label="Valor recibido"
          htmlFor="pm-amount"
          error={error ?? undefined}
          hint={selected ? `Precio ${money(selected.job.price)} · pagado ${money(selected.finance.paid - (existing?.amount ?? 0))} · pendiente ${money(balance)}` : undefined}
        >
          <AmountInput id="pm-amount" large autoFocus value={amount} onChange={setAmount} />
        </Field>
        {!existing && value > 0 && (
          <p className="text-[13px] text-muted-foreground">
            Se registrará como <span className="font-medium text-foreground">{PAYMENT_KIND_LABEL[kind].toLowerCase()}</span>
            {value < balance ? ` · quedarán ${money(balance - value)} por cobrar.` : "."}
          </p>
        )}
        <Field label="Cuenta receptora" htmlFor="pm-acc" hint={accountId ? "Se creará un ingreso vinculado en Finanzas (sin duplicados)." : "Solo quedará en el historial del cliente; no suma a tu saldo."}>
          <AccountSelect id="pm-acc" allowNone noneLabel="No registrar en Finanzas" value={accountId} onChange={setAccountId} filter={(a) => a.type !== "credit"} />
        </Field>
        <Field label="Fecha">
          <DateField value={date} onChange={(v) => setDate(v ?? today)} quick={["today", "yesterday"]} />
        </Field>
        <Field label="Nota" htmlFor="pm-note" optional>
          <Input id="pm-note" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Ej. Transferencia Bancolombia" />
        </Field>
      </form>
    </FormSheet>
  );
}
