"use client";

import * as React from "react";
import { Dialog as DialogPrimitive } from "radix-ui";
import { ArrowLeft, ArrowRight, FlaskConical, Plus, X } from "lucide-react";
import { toast } from "sonner";
import { useData, useToday } from "@/hooks/data";
import { readMode } from "@/db/db";
import type { AccountType } from "@/db/types";
import { addMonths, daysInMonth } from "@/lib/dates";
import { CURRENCIES, parseMoney } from "@/lib/money";
import { cn, uid } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Field, Input, NativeSelect } from "@/components/ui/form-controls";
import { AmountInput } from "@/components/shared/inputs";
import { createAccount, createObligation } from "@/services/finance-service";
import { createClient } from "@/services/clients-service";
import { createTask } from "@/services/life-service";
import { switchMode, updateSettings } from "@/services/settings-service";
import { errorMessage } from "@/services/common";

const TIME_ZONES = ["America/Bogota", "America/Mexico_City", "America/Lima", "America/Santiago", "America/Argentina/Buenos_Aires", "America/New_York", "Europe/Madrid", "UTC"];

interface AccountRow { id: string; name: string; type: AccountType; amount: string }
interface FixedRow { id: string; name: string; amount: string; day: string }

const STEPS = ["Bienvenida", "Tu dinero", "Gastos fijos", "Para empezar"];

export function Onboarding() {
  const data = useData();
  const today = useToday();
  const show = !data.settings.onboardingCompleted && readMode() === "real";
  const [open, setOpen] = React.useState(show);
  const [step, setStep] = React.useState(0);
  const [busy, setBusy] = React.useState(false);
  const [name, setName] = React.useState(data.settings.userName);
  const [currency, setCurrency] = React.useState(data.settings.currency);
  const [timeZone, setTimeZone] = React.useState(data.settings.timeZone);
  const [accounts, setAccounts] = React.useState<AccountRow[]>([
    { id: uid(), name: "Efectivo", type: "cash", amount: "" },
    { id: uid(), name: "Cuenta bancaria", type: "bank", amount: "" },
  ]);
  const [fixed, setFixed] = React.useState<FixedRow[]>([
    { id: uid(), name: "Arriendo", amount: "", day: "5" },
    { id: uid(), name: "Servicios públicos", amount: "", day: "15" },
  ]);
  const [clientName, setClientName] = React.useState("");
  const [taskTitle, setTaskTitle] = React.useState("");

  React.useEffect(() => setOpen(show), [show]);

  const finish = async (skip = false) => {
    setBusy(true);
    try {
      await updateSettings({ userName: name.trim(), currency, timeZone, onboardingCompleted: true });
      if (!skip) {
        const housing = data.categories.find((c) => c.systemKey === "housing")?.id ?? null;
        const utilities = data.categories.find((c) => c.systemKey === "utilities")?.id ?? null;
        let firstBank: string | null = null;
        for (const a of accounts) {
          const amount = parseMoney(a.amount);
          if (!a.name.trim() || amount === null) continue;
          const accId = await createAccount({ name: a.name, type: a.type, openingBalance: amount, openingDate: today, spendable: a.type !== "savings", color: a.type === "cash" ? "amber" : a.type === "savings" ? "emerald" : "iris" });
          if (!firstBank && a.type !== "cash") firstBank = accId;
        }
        for (const f of fixed) {
          const amount = parseMoney(f.amount);
          const day = Math.min(31, Math.max(1, Number(f.day) || 1));
          if (!f.name.trim() || !amount) continue;
          const thisMonth = `${today.slice(0, 7)}-${String(Math.min(day, daysInMonth(today))).padStart(2, "0")}`;
          const start = thisMonth >= today ? thisMonth : addMonths(`${today.slice(0, 7)}-01`, 1, day);
          await createObligation({
            name: f.name,
            type: /arriendo|alquiler/i.test(f.name) ? "rent" : /servicio|luz|agua|gas|internet/i.test(f.name) ? "utilities" : "other",
            amount,
            startDate: start,
            recurrence: { freq: "monthly", interval: 1 },
            accountId: firstBank,
            categoryId: /arriendo|alquiler/i.test(f.name) ? housing : utilities,
          });
        }
        if (clientName.trim()) await createClient({ name: clientName.trim(), status: "active", tags: [] });
        if (taskTitle.trim()) await createTask({ title: taskTitle.trim(), date: today });
        toast.success("¡Listo! Tu LIFE OS está configurado.");
      }
      setOpen(false);
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <DialogPrimitive.Root open={open} onOpenChange={(v) => !v && void finish(true)}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=open]:fade-in" />
        <DialogPrimitive.Content className="fixed inset-0 z-50 flex flex-col bg-popover outline-none data-[state=open]:animate-in data-[state=open]:fade-in sm:inset-auto sm:top-1/2 sm:left-1/2 sm:max-h-[88vh] sm:w-[560px] sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl sm:border sm:border-border sm:shadow-pop">
          <div className="flex items-center justify-between px-5 pt-[max(1rem,env(safe-area-inset-top))] pb-2 sm:pt-5">
            <ol className="flex items-center gap-1.5" aria-label="Pasos">
              {STEPS.map((s, i) => (
                <li key={s} aria-current={i === step ? "step" : undefined} className={cn("h-1.5 rounded-full transition-all duration-300", i === step ? "w-6 bg-foreground" : i < step ? "w-1.5 bg-foreground/50" : "w-1.5 bg-border-strong")}>
                  <span className="sr-only">{s}</span>
                </li>
              ))}
            </ol>
            <Button variant="ghost" size="sm" onClick={() => void finish(true)} disabled={busy}>
              Omitir
            </Button>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto px-5 pt-3 pb-6">
            {step === 0 && (
              <div className="space-y-5">
                <div>
                  <DialogPrimitive.Title className="text-2xl font-semibold tracking-tight">Bienvenido a LIFE OS</DialogPrimitive.Title>
                  <DialogPrimitive.Description className="mt-2 text-sm text-muted-foreground">
                    Tu dinero, tus clientes y tu tiempo en un solo lugar. Configurémoslo en un minuto; puedes cambiar todo después en Ajustes.
                  </DialogPrimitive.Description>
                </div>
                <Field label="¿Cómo te llamas?" htmlFor="ob-name" optional>
                  <Input id="ob-name" autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder="Tu nombre" />
                </Field>
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label="Moneda" htmlFor="ob-currency">
                    <NativeSelect id="ob-currency" value={currency} onChange={(e) => setCurrency(e.target.value)}>
                      {CURRENCIES.map((c) => (
                        <option key={c.code} value={c.code}>
                          {c.label} ({c.code})
                        </option>
                      ))}
                    </NativeSelect>
                  </Field>
                  <Field label="Zona horaria" htmlFor="ob-tz">
                    <NativeSelect id="ob-tz" value={timeZone} onChange={(e) => setTimeZone(e.target.value)}>
                      {TIME_ZONES.map((z) => (
                        <option key={z} value={z}>
                          {z.replace(/_/g, " ")}
                        </option>
                      ))}
                    </NativeSelect>
                  </Field>
                </div>
                <div className="rounded-xl border border-dashed border-border p-4">
                  <p className="text-sm font-medium">¿Prefieres explorar primero?</p>
                  <p className="mt-1 text-[13px] text-muted-foreground">El modo demo usa datos de ejemplo en un espacio separado. Tus registros reales nunca se mezclan con él.</p>
                  <Button variant="outline" size="sm" className="mt-3" onClick={() => switchMode("demo").catch((e) => toast.error(errorMessage(e)))}>
                    <FlaskConical /> Ver con datos de demostración
                  </Button>
                </div>
              </div>
            )}
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <DialogPrimitive.Title className="text-xl font-semibold tracking-tight">¿Cuánto dinero tienes hoy?</DialogPrimitive.Title>
                  <DialogPrimitive.Description className="mt-1.5 text-sm text-muted-foreground">Registra tus cuentas y su saldo actual. Las tarjetas de crédito puedes agregarlas después: su cupo nunca cuenta como dinero.</DialogPrimitive.Description>
                </div>
                {accounts.map((a, i) => (
                  <div key={a.id} className="grid grid-cols-[1fr_auto] gap-2 rounded-xl border border-border p-3 sm:grid-cols-[1.2fr_0.9fr_1fr_auto] sm:items-end">
                    <Field label="Nombre" htmlFor={`ac-n-${a.id}`} className="max-sm:col-span-2">
                      <Input id={`ac-n-${a.id}`} value={a.name} onChange={(e) => setAccounts((l) => l.map((x, j) => (j === i ? { ...x, name: e.target.value } : x)))} />
                    </Field>
                    <Field label="Tipo" htmlFor={`ac-t-${a.id}`}>
                      <NativeSelect id={`ac-t-${a.id}`} value={a.type} onChange={(e) => setAccounts((l) => l.map((x, j) => (j === i ? { ...x, type: e.target.value as AccountType } : x)))}>
                        <option value="cash">Efectivo</option>
                        <option value="bank">Banco</option>
                        <option value="wallet">Billetera digital</option>
                        <option value="savings">Ahorro</option>
                        <option value="other">Otra</option>
                      </NativeSelect>
                    </Field>
                    <Field label="Saldo" htmlFor={`ac-a-${a.id}`} className="max-sm:col-start-1">
                      <AmountInput id={`ac-a-${a.id}`} value={a.amount} onChange={(v) => setAccounts((l) => l.map((x, j) => (j === i ? { ...x, amount: v } : x)))} />
                    </Field>
                    <Button variant="ghost" size="icon" aria-label="Quitar cuenta" onClick={() => setAccounts((l) => l.filter((x) => x.id !== a.id))} className="max-sm:row-start-3 max-sm:self-end">
                      <X />
                    </Button>
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={() => setAccounts((l) => [...l, { id: uid(), name: "", type: "wallet", amount: "" }])}>
                  <Plus /> Otra cuenta
                </Button>
              </div>
            )}
            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <DialogPrimitive.Title className="text-xl font-semibold tracking-tight">Tus gastos fijos del mes</DialogPrimitive.Title>
                  <DialogPrimitive.Description className="mt-1.5 text-sm text-muted-foreground">Arriendo, servicios, cuotas… Se reservan en tus proyecciones y aparecen en tu agenda antes de vencer.</DialogPrimitive.Description>
                </div>
                {fixed.map((f, i) => (
                  <div key={f.id} className="grid grid-cols-[1fr_5rem_auto] gap-2 rounded-xl border border-border p-3 sm:grid-cols-[1.3fr_1fr_5rem_auto] sm:items-end">
                    <Field label="Nombre" htmlFor={`fx-n-${f.id}`} className="max-sm:col-span-3">
                      <Input id={`fx-n-${f.id}`} value={f.name} onChange={(e) => setFixed((l) => l.map((x, j) => (j === i ? { ...x, name: e.target.value } : x)))} />
                    </Field>
                    <Field label="Valor" htmlFor={`fx-a-${f.id}`}>
                      <AmountInput id={`fx-a-${f.id}`} value={f.amount} onChange={(v) => setFixed((l) => l.map((x, j) => (j === i ? { ...x, amount: v } : x)))} />
                    </Field>
                    <Field label="Día" htmlFor={`fx-d-${f.id}`}>
                      <Input id={`fx-d-${f.id}`} type="number" min={1} max={31} inputMode="numeric" value={f.day} onChange={(e) => setFixed((l) => l.map((x, j) => (j === i ? { ...x, day: e.target.value } : x)))} />
                    </Field>
                    <Button variant="ghost" size="icon" aria-label="Quitar gasto fijo" onClick={() => setFixed((l) => l.filter((x) => x.id !== f.id))}>
                      <X />
                    </Button>
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={() => setFixed((l) => [...l, { id: uid(), name: "", amount: "", day: "1" }])}>
                  <Plus /> Otro gasto fijo
                </Button>
              </div>
            )}
            {step === 3 && (
              <div className="space-y-5">
                <div>
                  <DialogPrimitive.Title className="text-xl font-semibold tracking-tight">Un primer paso</DialogPrimitive.Title>
                  <DialogPrimitive.Description className="mt-1.5 text-sm text-muted-foreground">Opcional: agrega tu primer cliente o lo primero que tienes que hacer hoy.</DialogPrimitive.Description>
                </div>
                <Field label="Primer cliente" htmlFor="ob-client" optional>
                  <Input id="ob-client" value={clientName} onChange={(e) => setClientName(e.target.value)} placeholder="Nombre del cliente" />
                </Field>
                <Field label="Una tarea para hoy" htmlFor="ob-task" optional>
                  <Input id="ob-task" value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} placeholder="Ej. Revisar correos de clientes" />
                </Field>
                <p className="rounded-lg bg-muted p-3 text-[13px] text-muted-foreground">
                  Tus datos se guardan en este dispositivo. Para pasarlos a otro equipo usa Ajustes › Respaldo.
                </p>
              </div>
            )}
          </div>
          <div className="flex items-center justify-between gap-2 border-t border-border px-5 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
            <Button variant="ghost" onClick={() => setStep((s) => Math.max(0, s - 1))} disabled={step === 0 || busy}>
              <ArrowLeft /> Atrás
            </Button>
            {step < STEPS.length - 1 ? (
              <Button onClick={() => setStep((s) => s + 1)}>
                Continuar <ArrowRight />
              </Button>
            ) : (
              <Button onClick={() => void finish(false)} disabled={busy}>
                Empezar a usar LIFE OS
              </Button>
            )}
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
