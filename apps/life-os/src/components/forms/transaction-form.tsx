"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { ArrowDownLeft, ArrowLeftRight, ArrowUpRight, Link2, Trash2 } from "lucide-react";
import { useData, useToday, useMoney } from "@/hooks/data";
import { createTransaction, deleteTransaction, updateTransaction } from "@/services/finance-service";
import type { Transaction, TransactionKind } from "@/db/types";
import { parseMoney } from "@/lib/money";
import { formatDateShort } from "@/lib/dates";
import { Field, Input, NativeSelect, Checkbox } from "@/components/ui/form-controls";
import { Segmented } from "@/components/ui/misc";
import { Button } from "@/components/ui/button";
import { AccountSelect, AmountInput, CategoryPicker, DateField, amountToText } from "@/components/shared/inputs";
import { useUI } from "@/components/shell/ui-context";
import { Disclosure, FormSheet, lastAccount, rememberAccount, runSave, useBusy } from "./form-kit";

const schema = z
  .object({
    kind: z.enum(["income", "expense", "transfer"]),
    amount: z.string().refine((s) => (parseMoney(s) ?? 0) > 0, "Ingresa un valor mayor que cero"),
    date: z.string().min(10, "Elige la fecha"),
    time: z.string().optional(),
    accountId: z.string().min(1, "Elige una cuenta"),
    toAccountId: z.string().optional(),
    categoryId: z.string().optional(),
    description: z.string().max(140).optional(),
    clientId: z.string().optional(),
    jobId: z.string().optional(),
    recurring: z.boolean(),
  })
  .refine((v) => v.kind !== "transfer" || (v.toAccountId && v.toAccountId !== v.accountId), {
    path: ["toAccountId"],
    message: "Elige una cuenta de destino distinta",
  });

type Values = z.infer<typeof schema>;

const KIND_LABEL: Record<TransactionKind, string> = { expense: "gasto", income: "ingreso", transfer: "transferencia" };

export function TransactionForm({
  id,
  defaults,
  onDone,
}: {
  id?: string;
  defaults?: { kind?: TransactionKind; clientId?: string | null; jobId?: string | null; categoryId?: string; accountId?: string };
  onDone: () => void;
}) {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { confirm } = useUI();
  const existing = id ? data.transactions.find((t) => t.id === id) : undefined;
  const [busy, wrap] = useBusy();
  const [open, setOpen] = React.useState(true);
  const close = () => {
    setOpen(false);
    setTimeout(onDone, 180);
  };

  const initialKind = existing?.kind ?? defaults?.kind ?? "expense";
  const fallbackAccount =
    (lastAccount(initialKind) && data.accounts.some((a) => a.id === lastAccount(initialKind) && !a.archived) ? lastAccount(initialKind) : null) ??
    data.accounts.find((a) => !a.archived && a.type !== "credit" && a.spendable)?.id ??
    "";

  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: {
      kind: initialKind,
      amount: existing ? amountToText(existing.amount, data.settings.currency) : "",
      date: existing?.date ?? today,
      time: existing?.time ?? "",
      accountId: existing?.accountId ?? defaults?.accountId ?? fallbackAccount,
      toAccountId: existing?.toAccountId ?? "",
      categoryId: existing?.categoryId ?? defaults?.categoryId ?? "",
      description: existing?.description ?? "",
      clientId: existing?.clientId ?? defaults?.clientId ?? "",
      jobId: existing?.jobId ?? defaults?.jobId ?? "",
      recurring: existing?.recurring ?? false,
    },
  });
  const { register, watch, setValue, handleSubmit, formState } = form;
  const kind = watch("kind");
  const clientId = watch("clientId");
  const linked = existing?.clientPaymentId ? "client" : existing?.obligationId ? "obligation" : existing?.plannedIncomeId ? "planned" : null;
  const noAccounts = data.accounts.filter((a) => !a.archived).length === 0;

  const onSubmit = handleSubmit((v) =>
    wrap(async () => {
      const fallbackCat = data.categories.find((c) => c.systemKey === (v.kind === "income" ? "other-income" : "other-expense"))?.id ?? null;
      const payload = {
        kind: v.kind,
        amount: parseMoney(v.amount)!,
        date: v.date,
        time: v.time || null,
        accountId: v.accountId,
        toAccountId: v.kind === "transfer" ? v.toAccountId || null : null,
        categoryId: v.kind === "transfer" ? null : v.categoryId || fallbackCat,
        description: v.description,
        clientId: v.clientId || null,
        jobId: v.jobId || null,
        recurring: v.recurring,
      };
      rememberAccount(v.kind, v.accountId);
      if (existing) {
        const ok = await runSave(() => updateTransaction(existing.id, payload), "Movimiento actualizado");
        if (ok) close();
      } else {
        let createdId = "";
        const ok = await runSave(
          async () => {
            createdId = await createTransaction(payload);
          },
          `${KIND_LABEL[v.kind][0].toUpperCase()}${KIND_LABEL[v.kind].slice(1)} de ${money(payload.amount)} registrado`,
          () => deleteTransaction(createdId),
        );
        if (ok) close();
      }
    }),
  );

  const remove = async () => {
    if (!existing) return;
    const ok = await confirm({
      title: "¿Eliminar este movimiento?",
      description:
        linked === "client"
          ? "Este ingreso es el pago de un cliente. Al eliminarlo también se anulará el pago y el saldo del trabajo volverá a quedar pendiente."
          : linked === "obligation"
            ? "Es el pago de una obligación: la cuota volverá a aparecer como pendiente."
            : "El saldo de la cuenta se recalculará. Esta acción no se puede deshacer.",
      confirmLabel: "Eliminar",
      destructive: true,
    });
    if (!ok) return;
    if (await runSave(() => deleteTransaction(existing.id), "Movimiento eliminado")) close();
  };

  const jobs = data.jobs.filter((j) => !j.archived && (!clientId || j.clientId === clientId));
  const errors = formState.errors;

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar movimiento" : `Registrar ${KIND_LABEL[kind]}`}
      formId="transaction-form"
      busy={busy}
      submitLabel={existing ? "Guardar cambios" : "Registrar"}
      submitDisabled={noAccounts}
      extraActions={
        existing && (
          <Button variant="destructive-ghost" size="sm" onClick={remove}>
            <Trash2 /> Eliminar
          </Button>
        )
      }
    >
      <form id="transaction-form" onSubmit={onSubmit} className="space-y-5" noValidate>
        {linked && (
          <p className="flex items-start gap-2 rounded-lg bg-info-soft px-3 py-2 text-[13px] text-info">
            <Link2 className="mt-0.5 size-4 shrink-0" />
            {linked === "client"
              ? "Vinculado a un pago de cliente: los cambios de valor, fecha o cuenta también actualizan el pago."
              : linked === "obligation"
                ? `Pago de una obligación (cuota del ${formatDateShort(existing!.occurrenceDate!)}).`
                : "Recibo de un ingreso previsto."}
          </p>
        )}
        {!existing && (
          <Segmented
            ariaLabel="Tipo de movimiento"
            className="w-full"
            value={kind}
            onChange={(k) => {
              setValue("kind", k);
              setValue("categoryId", "");
              const remembered = lastAccount(k);
              if (remembered && data.accounts.some((a) => a.id === remembered && !a.archived)) setValue("accountId", remembered);
            }}
            options={[
              { value: "expense", label: "Gasto", icon: <ArrowUpRight /> },
              { value: "income", label: "Ingreso", icon: <ArrowDownLeft /> },
              { value: "transfer", label: "Transferencia", icon: <ArrowLeftRight /> },
            ]}
          />
        )}
        {noAccounts && (
          <p className="rounded-lg bg-warning-soft px-3 py-2 text-[13px] text-warning">Primero crea una cuenta en Finanzas › Cuentas para registrar movimientos.</p>
        )}
        <Field label="Valor" htmlFor="tx-amount" error={errors.amount?.message}>
          <AmountInput
            id="tx-amount"
            large
            autoFocus={!existing}
            value={watch("amount")}
            onChange={(v) => setValue("amount", v, { shouldValidate: formState.isSubmitted })}
            ariaInvalid={!!errors.amount}
          />
        </Field>

        {kind !== "transfer" && (
          <Field label="Categoría" optional hint={!watch("categoryId") ? "Si no eliges, queda en «Otros»." : undefined}>
            <CategoryPicker kind={kind} value={watch("categoryId")} onChange={(v) => setValue("categoryId", v)} />
          </Field>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label={kind === "transfer" ? "Desde" : kind === "income" ? "Cuenta que recibe" : "Pagado con"} htmlFor="tx-account" error={errors.accountId?.message}>
            <AccountSelect id="tx-account" value={watch("accountId")} onChange={(v) => setValue("accountId", v ?? "")} />
          </Field>
          {kind === "transfer" && (
            <Field label="Hacia" htmlFor="tx-to" error={errors.toAccountId?.message}>
              <AccountSelect id="tx-to" value={watch("toAccountId")} exclude={watch("accountId")} onChange={(v) => setValue("toAccountId", v ?? "")} />
            </Field>
          )}
        </div>

        <Field label="Fecha" error={errors.date?.message}>
          <DateField value={watch("date")} onChange={(v) => setValue("date", v ?? today)} quick={["today", "yesterday"]} />
        </Field>

        <Field label="Descripción" htmlFor="tx-desc" optional>
          <Input id="tx-desc" placeholder={kind === "expense" ? "Ej. Mercado de la semana" : kind === "income" ? "Ej. Pago de proyecto" : "Ej. Recarga Nequi"} {...register("description")} />
        </Field>

        <Disclosure label="Más opciones" defaultOpen={!!(existing?.clientId || existing?.time || existing?.recurring || defaults?.clientId)}>
          <Field label="Hora" htmlFor="tx-time" optional>
            <Input id="tx-time" type="time" {...register("time")} />
          </Field>
          {kind !== "transfer" && (
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Cliente" htmlFor="tx-client" optional>
                <NativeSelect id="tx-client" {...register("clientId")} onChange={(e) => { setValue("clientId", e.target.value); setValue("jobId", ""); }}>
                  <option value="">Ninguno</option>
                  {data.clients.filter((c) => !c.archived).map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </NativeSelect>
              </Field>
              <Field label="Trabajo o proyecto" htmlFor="tx-job" optional>
                <NativeSelect id="tx-job" {...register("jobId")}>
                  <option value="">Ninguno</option>
                  {jobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.title}
                    </option>
                  ))}
                </NativeSelect>
              </Field>
            </div>
          )}
          {kind === "expense" && (
            <label className="flex items-start gap-2.5 text-sm">
              <Checkbox checked={watch("recurring")} onCheckedChange={(v) => setValue("recurring", v === true)} className="mt-0.5" />
              <span>
                Es un gasto recurrente
                <span className="block text-xs text-muted-foreground">Para que se descuente de tus proyecciones, créalo también como obligación.</span>
              </span>
            </label>
          )}
        </Disclosure>
      </form>
    </FormSheet>
  );
}

export type { Transaction };
