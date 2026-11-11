"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Archive, Trash2 } from "lucide-react";
import { useData, useMoney, useToday } from "@/hooks/data";
import {
  addContribution,
  createAccount,
  createCategory,
  createGoal,
  createObligation,
  createPlannedIncome,
  deleteBudget,
  deleteGoal,
  deleteObligation,
  deleteOrArchiveAccount,
  deletePlannedIncome,
  payObligation,
  receivePlannedIncome,
  setBudget,
  settleOccurrence,
  skipPlannedIncome,
  updateAccount,
  updateCategory,
  updateGoal,
  updateObligation,
  updatePlannedIncome,
} from "@/services/finance-service";
import type { AccountType, CategoryKind, ExpenseNature, ObligationType } from "@/db/types";
import { accountBalances, obligationOccurrences, plannedIncomeOccurrences } from "@/domain/finance";
import { formatDateLong } from "@/lib/dates";
import { parseMoney } from "@/lib/money";
import { PRESET_LABELS, presetToRecurrence, recurrenceToPreset, type RecurrencePreset } from "@/lib/recurrence";
import { Field, Input, NativeSelect, SwitchRow, Textarea } from "@/components/ui/form-controls";
import { Segmented } from "@/components/ui/misc";
import { Button } from "@/components/ui/button";
import { AccountSelect, AmountInput, ColorPicker, DateField, IconPicker, amountToText } from "@/components/shared/inputs";
import { ICON_CHOICES, PALETTE } from "@/components/shared/primitives";
import { useUI } from "@/components/shell/ui-context";
import { FormSheet, lastAccount, rememberAccount, runSave, useBusy } from "./form-kit";

const amountRule = z.string().refine((s) => (parseMoney(s) ?? 0) > 0, "Ingresa un valor mayor que cero");
const amountOrZero = z.string().refine((s) => s.trim() === "" || parseMoney(s) !== null, "Valor no válido");

function useClosable(onDone: () => void) {
  const [open, setOpen] = React.useState(true);
  return {
    open,
    close: () => {
      setOpen(false);
      setTimeout(onDone, 180);
    },
  };
}

// ── Account ──────────────────────────────────────────────────────────────────

export const ACCOUNT_TYPE_LABEL: Record<AccountType, string> = {
  cash: "Efectivo",
  bank: "Cuenta bancaria",
  wallet: "Billetera digital",
  savings: "Cuenta de ahorro",
  credit: "Tarjeta de crédito",
  other: "Otra cuenta",
};

const accountSchema = z.object({
  name: z.string().trim().min(1, "Ponle un nombre"),
  type: z.enum(["cash", "bank", "wallet", "savings", "credit", "other"]),
  balance: amountOrZero,
  creditLimit: amountOrZero,
  spendable: z.boolean(),
  color: z.string(),
});

export function AccountForm({ id, defaultType, onDone }: { id?: string; defaultType?: AccountType; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.accounts.find((a) => a.id === id) : undefined;
  const balances = React.useMemo(() => accountBalances(data.accounts, data.transactions), [data.accounts, data.transactions]);
  const current = existing ? balances.get(existing.id) ?? 0 : 0;
  const type0 = existing?.type ?? defaultType ?? "bank";
  const form = useForm<z.infer<typeof accountSchema>>({
    resolver: zodResolver(accountSchema),
    defaultValues: {
      name: existing?.name ?? "",
      type: type0,
      balance: existing ? amountToText(type0 === "credit" ? Math.max(0, -current) : current, data.settings.currency) : "",
      creditLimit: existing?.creditLimit ? amountToText(existing.creditLimit, data.settings.currency) : "",
      spendable: existing?.spendable ?? !(type0 === "savings" || type0 === "credit"),
      color: existing?.color ?? "iris",
    },
  });
  const { watch, setValue, register, handleSubmit, formState } = form;
  const type = watch("type");

  const submit = handleSubmit((v) =>
    wrap(async () => {
      const entered = parseMoney(v.balance) ?? 0;
      const desired = v.type === "credit" ? -Math.abs(entered) : entered;
      const payload = {
        name: v.name,
        type: v.type,
        spendable: v.type === "credit" ? false : v.spendable,
        color: v.color,
        creditLimit: v.type === "credit" ? parseMoney(v.creditLimit) : null,
      };
      if (existing) {
        // Editing the balance adjusts the opening balance so history stays intact.
        const openingBalance = existing.openingBalance + (desired - current);
        if (await runSave(() => updateAccount(existing.id, { ...payload, openingBalance }), "Cuenta actualizada")) close();
      } else if (await runSave(() => createAccount({ ...payload, openingBalance: desired, openingDate: today }), "Cuenta creada")) close();
    }),
  );

  const remove = async () => {
    if (!existing) return;
    const ok = await confirm({
      title: `¿Eliminar «${existing.name}»?`,
      description: "Si la cuenta tiene movimientos se archivará para conservar el historial.",
      confirmLabel: "Eliminar",
      destructive: true,
    });
    if (!ok) return;
    let result = "deleted" as "deleted" | "archived";
    if (await runSave(async () => void (result = await deleteOrArchiveAccount(existing.id)))) {
      const { toast } = await import("sonner");
      toast.success(result === "archived" ? "Cuenta archivada (tenía movimientos)" : "Cuenta eliminada");
      close();
    }
  };

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar cuenta" : "Nueva cuenta"}
      formId="account-form"
      busy={busy}
      extraActions={
        existing && (
          <Button variant="destructive-ghost" size="sm" onClick={remove}>
            <Trash2 /> Eliminar
          </Button>
        )
      }
    >
      <form id="account-form" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Tipo" htmlFor="acc-type">
          <NativeSelect
            id="acc-type"
            value={type}
            onChange={(e) => {
              const t = e.target.value as AccountType;
              setValue("type", t);
              setValue("spendable", !(t === "savings" || t === "credit"));
            }}
          >
            {Object.entries(ACCOUNT_TYPE_LABEL).map(([k, label]) => (
              <option key={k} value={k}>
                {label}
              </option>
            ))}
          </NativeSelect>
        </Field>
        <Field label="Nombre" htmlFor="acc-name" error={formState.errors.name?.message}>
          <Input id="acc-name" autoFocus={!existing} placeholder={type === "credit" ? "Ej. Visa Bancolombia" : "Ej. Cuenta de ahorros Davivienda"} {...register("name")} />
        </Field>
        <Field
          label={type === "credit" ? "Deuda actual" : "Saldo actual"}
          htmlFor="acc-balance"
          error={formState.errors.balance?.message}
          hint={
            type === "credit"
              ? "Lo que debes hoy en la tarjeta. El cupo nunca se cuenta como dinero disponible."
              : existing
                ? "Si cambias el saldo se registra como ajuste del saldo inicial; tus movimientos no cambian."
                : "El dinero que tienes hoy en esta cuenta."
          }
        >
          <AmountInput id="acc-balance" value={watch("balance")} onChange={(v) => setValue("balance", v)} />
        </Field>
        {type === "credit" && (
          <Field label="Cupo total" htmlFor="acc-limit" optional>
            <AmountInput id="acc-limit" value={watch("creditLimit")} onChange={(v) => setValue("creditLimit", v)} />
          </Field>
        )}
        {type !== "credit" && (
          <SwitchRow
            id="acc-spendable"
            label="Disponible para el gasto diario"
            description="Apágalo para dinero apartado (ahorros): seguirá en tu saldo real, pero no en tu margen para gastar."
            checked={watch("spendable")}
            onCheckedChange={(v) => setValue("spendable", v)}
          />
        )}
        <Field label="Color">
          <ColorPicker colors={PALETTE} value={watch("color")} onChange={(c) => setValue("color", c)} />
        </Field>
      </form>
    </FormSheet>
  );
}

// ── Obligation ───────────────────────────────────────────────────────────────

export const OBLIGATION_TYPE_LABEL: Record<ObligationType, string> = {
  rent: "Arriendo",
  utilities: "Servicios",
  loan: "Préstamo",
  card: "Tarjeta de crédito",
  subscription: "Suscripción",
  installment: "Cuota",
  supplier: "Pago a proveedor",
  tax: "Impuesto",
  other: "Otro compromiso",
};

const OBLIGATION_CATEGORY: Partial<Record<ObligationType, string>> = {
  rent: "housing",
  utilities: "utilities",
  loan: "debts",
  subscription: "subscriptions",
  installment: "debts",
};

const obligationSchema = z.object({
  name: z.string().trim().min(1, "Ponle un nombre"),
  type: z.enum(["rent", "utilities", "loan", "card", "subscription", "installment", "supplier", "tax", "other"]),
  amount: amountRule,
  startDate: z.string().min(10, "Elige la fecha"),
  preset: z.string(),
  count: z.string().optional(),
  accountId: z.string().optional(),
  cardAccountId: z.string().optional(),
  categoryId: z.string().optional(),
  notes: z.string().optional(),
});

export function ObligationForm({ id, onDone }: { id?: string; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.obligations.find((o) => o.id === id) : undefined;
  const form = useForm<z.infer<typeof obligationSchema>>({
    resolver: zodResolver(obligationSchema),
    defaultValues: {
      name: existing?.name ?? "",
      type: existing?.type ?? "rent",
      amount: existing ? amountToText(existing.amount, data.settings.currency) : "",
      startDate: existing?.startDate ?? today,
      preset: recurrenceToPreset(existing?.recurrence ?? (existing ? null : { freq: "monthly", interval: 1 })),
      count: existing?.recurrence?.count ? String(existing.recurrence.count) : "",
      accountId: existing?.accountId ?? data.accounts.find((a) => a.type === "bank" && !a.archived)?.id ?? "",
      cardAccountId: existing?.cardAccountId ?? "",
      categoryId: existing?.categoryId ?? data.categories.find((c) => c.systemKey === "housing")?.id ?? "",
      notes: existing?.notes ?? "",
    },
  });
  const { watch, setValue, register, handleSubmit, formState } = form;
  const type = watch("type");
  const preset = watch("preset") as RecurrencePreset;

  const submit = handleSubmit((v) =>
    wrap(async () => {
      const base = presetToRecurrence(v.preset as RecurrencePreset);
      const count = v.count ? Math.max(1, Number(v.count)) : null;
      const recurrence = base ? { ...base, count } : null;
      const payload = {
        name: v.name,
        type: v.type,
        amount: parseMoney(v.amount)!,
        startDate: v.startDate,
        recurrence,
        accountId: v.accountId || null,
        cardAccountId: v.type === "card" ? v.cardAccountId || null : null,
        categoryId: v.type === "card" ? null : v.categoryId || null,
        notes: v.notes,
      };
      if (existing) {
        if (await runSave(() => updateObligation(existing.id, payload), "Obligación actualizada")) close();
      } else if (await runSave(() => createObligation(payload), "Obligación creada")) close();
    }),
  );

  const remove = async () => {
    if (!existing) return;
    const ok = await confirm({
      title: `¿Eliminar «${existing.name}»?`,
      description: "Dejará de aparecer en tus proyecciones y agenda. Los pagos ya registrados se conservan como gastos normales.",
      confirmLabel: "Eliminar",
      destructive: true,
    });
    if (ok && (await runSave(() => deleteObligation(existing.id), "Obligación eliminada"))) close();
  };

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar obligación" : "Nueva obligación"}
      description="Compromisos de pago: se reservan en tus proyecciones, pero no se descuentan del saldo real hasta que los pagues."
      formId="obligation-form"
      busy={busy}
      extraActions={
        existing && (
          <>
            <Button variant="destructive-ghost" size="sm" onClick={remove}>
              <Trash2 /> Eliminar
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => runSave(() => updateObligation(existing.id, { active: !existing.active }), existing.active ? "Obligación pausada" : "Obligación reactivada").then((ok) => ok && close())}
            >
              <Archive /> {existing.active ? "Pausar" : "Reactivar"}
            </Button>
          </>
        )
      }
    >
      <form id="obligation-form" onSubmit={submit} className="space-y-4" noValidate>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Tipo" htmlFor="ob-type">
            <NativeSelect
              id="ob-type"
              value={type}
              onChange={(e) => {
                const t = e.target.value as ObligationType;
                setValue("type", t);
                const key = OBLIGATION_CATEGORY[t];
                const cat = key && data.categories.find((c) => c.systemKey === key);
                if (cat) setValue("categoryId", cat.id);
                if (t === "subscription" || t === "rent" || t === "utilities" || t === "card") setValue("preset", "monthly");
              }}
            >
              {Object.entries(OBLIGATION_TYPE_LABEL).map(([k, label]) => (
                <option key={k} value={k}>
                  {label}
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Nombre" htmlFor="ob-name" error={formState.errors.name?.message}>
            <Input id="ob-name" autoFocus={!existing} placeholder="Ej. Arriendo apartamento" {...register("name")} />
          </Field>
        </div>
        <Field label={preset === "none" ? "Valor" : "Valor de cada pago"} htmlFor="ob-amount" error={formState.errors.amount?.message}>
          <AmountInput id="ob-amount" large value={watch("amount")} onChange={(v) => setValue("amount", v)} />
        </Field>
        <Field label={existing ? "Primer vencimiento" : "Próximo vencimiento"} error={formState.errors.startDate?.message} hint="Si ya pasó y no lo has pagado, aparecerá como vencido.">
          <DateField value={watch("startDate")} onChange={(v) => setValue("startDate", v ?? today)} quick={["today", "tomorrow", "nextweek"]} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Periodicidad" htmlFor="ob-freq">
            <NativeSelect id="ob-freq" {...register("preset")}>
              {(["none", "weekly", "biweekly", "monthly", "quarterly", "yearly"] as RecurrencePreset[]).map((p) => (
                <option key={p} value={p}>
                  {p === "none" ? "Una sola vez" : PRESET_LABELS[p]}
                </option>
              ))}
            </NativeSelect>
          </Field>
          {preset !== "none" && (
            <Field label="Número de pagos" htmlFor="ob-count" optional hint="Para cuotas o préstamos con fin.">
              <Input id="ob-count" type="number" min={1} inputMode="numeric" placeholder="Sin fin" {...register("count")} />
            </Field>
          )}
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Se paga desde" htmlFor="ob-account" optional>
            <AccountSelect id="ob-account" allowNone noneLabel="Elegir al pagar" value={watch("accountId")} onChange={(v) => setValue("accountId", v ?? "")} filter={(a) => a.type !== "credit" || type !== "card"} />
          </Field>
          {type === "card" ? (
            <Field label="Tarjeta que pagas" htmlFor="ob-card" hint="El pago será una transferencia a la tarjeta: tus compras no se cuentan dos veces.">
              <AccountSelect id="ob-card" allowNone noneLabel="Sin vincular" value={watch("cardAccountId")} onChange={(v) => setValue("cardAccountId", v ?? "")} filter={(a) => a.type === "credit"} />
            </Field>
          ) : (
            <Field label="Categoría del gasto" htmlFor="ob-cat">
              <NativeSelect id="ob-cat" {...register("categoryId")}>
                {data.categories
                  .filter((c) => c.kind === "expense" && !c.archived)
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
              </NativeSelect>
            </Field>
          )}
        </div>
        <Field label="Notas" htmlFor="ob-notes" optional>
          <Textarea id="ob-notes" rows={2} placeholder="Referencia de pago, número de contrato…" {...register("notes")} />
        </Field>
      </form>
    </FormSheet>
  );
}

// ── Pay an obligation occurrence ─────────────────────────────────────────────

export function ObligationPaymentForm({ obligationId, dueDate, onDone }: { obligationId: string; dueDate: string; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const obligation = data.obligations.find((o) => o.id === obligationId);
  const occurrence = React.useMemo(
    () => (obligation ? obligationOccurrences([obligation], data.transactions, dueDate, dueDate, today, { includeInactive: true })[0] : undefined),
    [obligation, data.transactions, dueDate, today],
  );
  const [amount, setAmount] = React.useState(() => amountToText(occurrence?.remaining || obligation?.amount || 0, data.settings.currency));
  const [date, setDate] = React.useState(today);
  const [accountId, setAccountId] = React.useState<string>(obligation?.accountId ?? lastAccount("expense") ?? data.accounts.find((a) => a.spendable && !a.archived)?.id ?? "");
  const [error, setError] = React.useState<string | null>(null);
  if (!obligation || !occurrence) return null;

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseMoney(amount);
    if (!value || value <= 0) return setError("Ingresa un valor mayor que cero");
    if (!accountId) return setError("Elige la cuenta desde la que pagaste");
    void wrap(async () => {
      rememberAccount("expense", accountId);
      const ok = await runSave(
        () => payObligation({ obligationId, dueDate, amount: value, date, accountId }),
        value >= occurrence.remaining ? `${obligation.name} quedó pagada` : `Abono de ${money(value)} registrado`,
      );
      if (ok) close();
    });
  };

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={`Pagar: ${obligation.name}`}
      description={`Vence el ${formatDateLong(dueDate)} · pendiente ${money(occurrence.remaining)}`}
      formId="pay-obligation"
      busy={busy}
      submitLabel="Registrar pago"
      layout="center"
      extraActions={
        <Button
          variant="ghost"
          size="sm"
          onClick={() => runSave(() => settleOccurrence(obligationId, dueDate, "paid-outside"), "Marcada como pagada").then((ok) => ok && close())}
        >
          Ya la pagué antes
        </Button>
      }
    >
      <form id="pay-obligation" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Valor pagado" htmlFor="pay-amount" error={error ?? undefined} hint={occurrence.paid > 0 ? `Ya abonaste ${money(occurrence.paid)} a esta cuota.` : "Puedes registrar un pago parcial."}>
          <AmountInput id="pay-amount" large autoFocus value={amount} onChange={setAmount} />
        </Field>
        <Field label="Pagado con" htmlFor="pay-account">
          <AccountSelect id="pay-account" value={accountId} onChange={(v) => setAccountId(v ?? "")} />
        </Field>
        <Field label="Fecha del pago">
          <DateField value={date} onChange={(v) => setDate(v ?? today)} quick={["today", "yesterday"]} />
        </Field>
        <button
          type="button"
          className="text-[13px] text-muted-foreground underline underline-offset-4 hover:text-foreground"
          onClick={() => runSave(() => settleOccurrence(obligationId, dueDate, "skipped"), "Este pago se omitió").then((ok) => ok && close())}
        >
          Omitir este vencimiento (no aplica este período)
        </button>
      </form>
    </FormSheet>
  );
}

// ── Planned income ───────────────────────────────────────────────────────────

const plannedSchema = z.object({
  name: z.string().trim().min(1, "Ponle un nombre"),
  amount: amountRule,
  startDate: z.string().min(10),
  preset: z.string(),
  confirmed: z.boolean(),
  accountId: z.string().optional(),
  categoryId: z.string().optional(),
});

export function PlannedIncomeForm({ id, onDone }: { id?: string; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.plannedIncomes.find((p) => p.id === id) : undefined;
  const form = useForm<z.infer<typeof plannedSchema>>({
    resolver: zodResolver(plannedSchema),
    defaultValues: {
      name: existing?.name ?? "",
      amount: existing ? amountToText(existing.amount, data.settings.currency) : "",
      startDate: existing?.startDate ?? today,
      preset: recurrenceToPreset(existing?.recurrence ?? (existing ? null : { freq: "monthly", interval: 1 })),
      confirmed: existing?.confirmed ?? true,
      accountId: existing?.accountId ?? "",
      categoryId: existing?.categoryId ?? data.categories.find((c) => c.systemKey === "salary")?.id ?? "",
    },
  });
  const { watch, setValue, register, handleSubmit, formState } = form;
  const submit = handleSubmit((v) =>
    wrap(async () => {
      const payload = {
        name: v.name,
        amount: parseMoney(v.amount)!,
        startDate: v.startDate,
        recurrence: presetToRecurrence(v.preset as RecurrencePreset),
        confirmed: v.confirmed,
        accountId: v.accountId || null,
        categoryId: v.categoryId || null,
      };
      if (existing) {
        if (await runSave(() => updatePlannedIncome(existing.id, payload), "Ingreso previsto actualizado")) close();
      } else if (await runSave(() => createPlannedIncome(payload), "Ingreso previsto creado")) close();
    }),
  );
  const remove = async () => {
    if (!existing) return;
    if (await confirm({ title: `¿Eliminar «${existing.name}»?`, confirmLabel: "Eliminar", destructive: true })) {
      if (await runSave(() => deletePlannedIncome(existing.id), "Ingreso previsto eliminado")) close();
    }
  };
  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar ingreso previsto" : "Nuevo ingreso previsto"}
      description="Salario, honorarios fijos u otros ingresos esperados. Nunca se suman a tu dinero disponible hasta que los recibas."
      formId="planned-form"
      busy={busy}
      extraActions={existing && <Button variant="destructive-ghost" size="sm" onClick={remove}><Trash2 /> Eliminar</Button>}
    >
      <form id="planned-form" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Nombre" htmlFor="pi-name" error={formState.errors.name?.message}>
          <Input id="pi-name" autoFocus={!existing} placeholder="Ej. Salario" {...register("name")} />
        </Field>
        <Field label="Valor" htmlFor="pi-amount" error={formState.errors.amount?.message}>
          <AmountInput id="pi-amount" large value={watch("amount")} onChange={(v) => setValue("amount", v)} />
        </Field>
        <Field label="Próxima fecha">
          <DateField value={watch("startDate")} onChange={(v) => setValue("startDate", v ?? today)} quick={["today", "tomorrow", "nextweek"]} />
        </Field>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Periodicidad" htmlFor="pi-freq">
            <NativeSelect id="pi-freq" {...register("preset")}>
              {(["none", "weekly", "biweekly", "monthly", "quarterly", "yearly"] as RecurrencePreset[]).map((p) => (
                <option key={p} value={p}>
                  {p === "none" ? "Una sola vez" : PRESET_LABELS[p]}
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Cuenta donde llega" htmlFor="pi-acc" optional>
            <AccountSelect id="pi-acc" allowNone noneLabel="Elegir al recibir" value={watch("accountId")} onChange={(v) => setValue("accountId", v ?? "")} filter={(a) => a.type !== "credit"} />
          </Field>
        </div>
        <SwitchRow
          id="pi-confirmed"
          label="Ingreso confirmado"
          description="Confirmado = seguro (salario, contrato firmado). Marca como no confirmado lo que todavía es incierto."
          checked={watch("confirmed")}
          onCheckedChange={(v) => setValue("confirmed", v)}
        />
      </form>
    </FormSheet>
  );
}

export function ReceiveIncomeForm({ plannedIncomeId, dueDate, onDone }: { plannedIncomeId: string; dueDate: string; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const planned = data.plannedIncomes.find((p) => p.id === plannedIncomeId);
  const occ = React.useMemo(
    () => (planned ? plannedIncomeOccurrences([planned], data.transactions, dueDate, dueDate, today)[0] : undefined),
    [planned, data.transactions, dueDate, today],
  );
  const [amount, setAmount] = React.useState(() => amountToText(occ?.remaining || planned?.amount || 0, data.settings.currency));
  const [date, setDate] = React.useState(today);
  const [accountId, setAccountId] = React.useState(planned?.accountId ?? lastAccount("income") ?? "");
  const [error, setError] = React.useState<string | null>(null);
  if (!planned || !occ) return null;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseMoney(amount);
    if (!value) return setError("Ingresa un valor mayor que cero");
    if (!accountId) return setError("Elige la cuenta donde lo recibiste");
    void wrap(async () => {
      rememberAccount("income", accountId);
      if (await runSave(() => receivePlannedIncome({ plannedIncomeId, dueDate, amount: value, date, accountId }), `Ingreso de ${money(value)} registrado`)) close();
    });
  };
  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={`Recibir: ${planned.name}`}
      description={`Previsto para el ${formatDateLong(dueDate)}`}
      formId="receive-form"
      busy={busy}
      submitLabel="Registrar ingreso"
      layout="center"
      extraActions={
        <Button variant="ghost" size="sm" onClick={() => runSave(() => skipPlannedIncome(plannedIncomeId, dueDate, true), "Ingreso omitido").then((ok) => ok && close())}>
          No llegó / omitir
        </Button>
      }
    >
      <form id="receive-form" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Valor recibido" htmlFor="rc-amount" error={error ?? undefined}>
          <AmountInput id="rc-amount" large autoFocus value={amount} onChange={setAmount} />
        </Field>
        <Field label="Cuenta" htmlFor="rc-acc">
          <AccountSelect id="rc-acc" value={accountId} onChange={(v) => setAccountId(v ?? "")} filter={(a) => a.type !== "credit"} />
        </Field>
        <Field label="Fecha">
          <DateField value={date} onChange={(v) => setDate(v ?? today)} quick={["today", "yesterday"]} />
        </Field>
      </form>
    </FormSheet>
  );
}

// ── Budget ───────────────────────────────────────────────────────────────────

export function BudgetForm({ categoryId, onDone }: { categoryId?: string; onDone: () => void }) {
  const data = useData();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = categoryId ? data.budgets.find((b) => b.categoryId === categoryId) : undefined;
  const expenseCats = data.categories.filter((c) => c.kind === "expense" && !c.archived);
  const [cat, setCat] = React.useState(categoryId ?? expenseCats.find((c) => !data.budgets.some((b) => b.categoryId === c.id))?.id ?? expenseCats[0]?.id ?? "");
  const [amount, setAmount] = React.useState(existing ? amountToText(existing.amount, data.settings.currency) : "");
  const [error, setError] = React.useState<string | null>(null);
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseMoney(amount);
    if (!value || value <= 0) return setError("Ingresa un valor mayor que cero");
    void wrap(async () => {
      if (await runSave(() => setBudget(cat, value), "Presupuesto guardado")) close();
    });
  };
  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar presupuesto" : "Nuevo presupuesto"}
      description="Límite mensual por categoría. Se reinicia cada mes."
      formId="budget-form"
      busy={busy}
      layout="center"
      extraActions={
        existing && (
          <Button variant="destructive-ghost" size="sm" onClick={() => runSave(() => deleteBudget(existing.id), "Presupuesto eliminado").then((ok) => ok && close())}>
            <Trash2 /> Quitar
          </Button>
        )
      }
    >
      <form id="budget-form" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Categoría" htmlFor="bd-cat">
          <NativeSelect id="bd-cat" value={cat} onChange={(e) => setCat(e.target.value)} disabled={!!existing}>
            {expenseCats.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
                {data.budgets.some((b) => b.categoryId === c.id) && c.id !== categoryId ? " (ya tiene)" : ""}
              </option>
            ))}
          </NativeSelect>
        </Field>
        <Field label="Límite mensual" htmlFor="bd-amount" error={error ?? undefined}>
          <AmountInput id="bd-amount" large autoFocus value={amount} onChange={setAmount} />
        </Field>
      </form>
    </FormSheet>
  );
}

// ── Category ─────────────────────────────────────────────────────────────────

export const NATURE_LABEL: Record<ExpenseNature, string> = { fixed: "Fijo", variable: "Variable", discretionary: "Discrecional" };

export function CategoryForm({ id, defaultKind, onDone }: { id?: string; defaultKind?: CategoryKind; onDone: () => void }) {
  const data = useData();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.categories.find((c) => c.id === id) : undefined;
  const [kind, setKind] = React.useState<CategoryKind>(existing?.kind ?? defaultKind ?? "expense");
  const [name, setName] = React.useState(existing?.name ?? "");
  const [nature, setNature] = React.useState<ExpenseNature>(existing?.nature ?? "variable");
  const [icon, setIcon] = React.useState(existing?.icon ?? "sparkles");
  const [color, setColor] = React.useState(existing?.color ?? "iris");
  const [error, setError] = React.useState<string | null>(null);
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return setError("Ponle un nombre");
    void wrap(async () => {
      if (existing) {
        if (await runSave(() => updateCategory(existing.id, { name: name.trim(), nature, icon, color }), "Categoría actualizada")) close();
      } else if (await runSave(() => createCategory({ name, kind, nature, icon, color }), "Categoría creada")) close();
    });
  };
  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar categoría" : "Nueva categoría"}
      formId="category-form"
      busy={busy}
      extraActions={
        existing && (
          <Button variant="ghost" size="sm" onClick={() => runSave(() => updateCategory(existing.id, { archived: !existing.archived }), existing.archived ? "Categoría restaurada" : "Categoría archivada").then((ok) => ok && close())}>
            <Archive /> {existing.archived ? "Restaurar" : "Archivar"}
          </Button>
        )
      }
    >
      <form id="category-form" onSubmit={submit} className="space-y-4" noValidate>
        {!existing && (
          <Segmented
            className="w-full"
            value={kind}
            onChange={setKind}
            options={[
              { value: "expense", label: "Gasto" },
              { value: "income", label: "Ingreso" },
            ]}
          />
        )}
        <Field label="Nombre" htmlFor="cat-name" error={error ?? undefined}>
          <Input id="cat-name" autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder="Ej. Mascotas" />
        </Field>
        {kind === "expense" && (
          <Field label="Tipo de gasto" hint="Fijos y variables son esenciales; los discrecionales alimentan tu margen de ocio.">
            <Segmented
              className="w-full"
              value={nature}
              onChange={setNature}
              options={(["fixed", "variable", "discretionary"] as ExpenseNature[]).map((n) => ({ value: n, label: NATURE_LABEL[n] }))}
            />
          </Field>
        )}
        <Field label="Color">
          <ColorPicker colors={PALETTE} value={color} onChange={setColor} />
        </Field>
        <Field label="Icono">
          <IconPicker icons={ICON_CHOICES} value={icon} onChange={setIcon} color={color} />
        </Field>
      </form>
    </FormSheet>
  );
}

// ── Savings goals ────────────────────────────────────────────────────────────

export function GoalForm({ id, onDone }: { id?: string; onDone: () => void }) {
  const data = useData();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.goals.find((g) => g.id === id) : undefined;
  const [name, setName] = React.useState(existing?.name ?? "");
  const [target, setTarget] = React.useState(existing ? amountToText(existing.target, data.settings.currency) : "");
  const [initial, setInitial] = React.useState("");
  const [targetDate, setTargetDate] = React.useState<string | null>(existing?.targetDate ?? null);
  const [isEmergency, setEmergency] = React.useState(existing?.isEmergencyFund ?? false);
  const [accountId, setAccountId] = React.useState<string | null>(existing?.accountId ?? data.accounts.find((a) => a.type === "savings" && !a.archived)?.id ?? null);
  const [color, setColor] = React.useState(existing?.color ?? "emerald");
  const [error, setError] = React.useState<string | null>(null);
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const t = parseMoney(target);
    if (!name.trim()) return setError("Ponle un nombre a la meta");
    if (!t || t <= 0) return setError("Define el valor de la meta");
    void wrap(async () => {
      const payload = { name, target: t, targetDate, isEmergencyFund: isEmergency, accountId, color };
      if (existing) {
        if (await runSave(() => updateGoal(existing.id, payload), "Meta actualizada")) close();
      } else if (await runSave(() => createGoal(payload, parseMoney(initial) ?? 0), "Meta creada")) close();
    });
  };
  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar meta" : "Nueva meta de ahorro"}
      formId="goal-form"
      busy={busy}
      extraActions={
        existing && (
          <Button
            variant="destructive-ghost"
            size="sm"
            onClick={async () => {
              if (await confirm({ title: `¿Eliminar la meta «${existing.name}»?`, description: "Se borrarán sus aportes registrados.", confirmLabel: "Eliminar", destructive: true })) {
                if (await runSave(() => deleteGoal(existing.id), "Meta eliminada")) close();
              }
            }}
          >
            <Trash2 /> Eliminar
          </Button>
        )
      }
    >
      <form id="goal-form" onSubmit={submit} className="space-y-4" noValidate>
        {error && <p className="text-[13px] text-destructive">{error}</p>}
        <Field label="Nombre" htmlFor="goal-name">
          <Input id="goal-name" autoFocus={!existing} value={name} onChange={(e) => setName(e.target.value)} placeholder="Ej. Fondo de emergencia" />
        </Field>
        <Field label="Meta" htmlFor="goal-target">
          <AmountInput id="goal-target" large value={target} onChange={setTarget} />
        </Field>
        {!existing && (
          <Field label="Ya tengo ahorrado" htmlFor="goal-initial" optional>
            <AmountInput id="goal-initial" value={initial} onChange={setInitial} />
          </Field>
        )}
        <Field label="Fecha objetivo" optional hint="Con fecha, calculamos cuánto apartar al mes y lo reservamos en tu margen de gasto.">
          <DateField value={targetDate} onChange={setTargetDate} quick={[]} allowEmpty emptyLabel="Sin fecha" />
        </Field>
        <Field label="¿Dónde guardas este dinero?" htmlFor="goal-acc" hint="Si está en una cuenta de ahorro (no disponible para gastar), ya queda protegido.">
          <AccountSelect id="goal-acc" allowNone noneLabel="En mis cuentas de uso diario" value={accountId} onChange={setAccountId} filter={(a) => a.type !== "credit"} />
        </Field>
        <SwitchRow id="goal-emergency" label="Es mi fondo de emergencia" checked={isEmergency} onCheckedChange={setEmergency} />
        <Field label="Color">
          <ColorPicker colors={PALETTE} value={color} onChange={setColor} />
        </Field>
      </form>
    </FormSheet>
  );
}

export function ContributionForm({ goalId, onDone }: { goalId: string; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const goal = data.goals.find((g) => g.id === goalId);
  const [mode, setMode] = React.useState<"add" | "withdraw">("add");
  const [amount, setAmount] = React.useState("");
  const [date, setDate] = React.useState(today);
  const [note, setNote] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  if (!goal) return null;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const v = parseMoney(amount);
    if (!v || v <= 0) return setError("Ingresa un valor mayor que cero");
    void wrap(async () => {
      if (await runSave(() => addContribution({ goalId, amount: mode === "add" ? v : -v, date, note }), mode === "add" ? `Aporte de ${money(v)} a ${goal.name}` : `Retiro de ${money(v)} registrado`)) close();
    });
  };
  return (
    <FormSheet open={open} onOpenChange={(v) => !v && close()} title={goal.name} description="Registra cuánto apartaste o retiraste." formId="contrib-form" busy={busy} layout="center" submitLabel={mode === "add" ? "Aportar" : "Retirar"}>
      <form id="contrib-form" onSubmit={submit} className="space-y-4" noValidate>
        <Segmented className="w-full" value={mode} onChange={setMode} options={[{ value: "add", label: "Aporte" }, { value: "withdraw", label: "Retiro" }]} />
        <Field label="Valor" htmlFor="ct-amount" error={error ?? undefined}>
          <AmountInput id="ct-amount" large autoFocus value={amount} onChange={setAmount} />
        </Field>
        <Field label="Fecha">
          <DateField value={date} onChange={(v) => setDate(v ?? today)} quick={["today", "yesterday"]} />
        </Field>
        <Field label="Nota" htmlFor="ct-note" optional>
          <Input id="ct-note" value={note} onChange={(e) => setNote(e.target.value)} />
        </Field>
      </form>
    </FormSheet>
  );
}
