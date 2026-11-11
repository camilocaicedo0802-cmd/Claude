"use client";

import * as React from "react";
import {
  ArrowDownLeft,
  ArrowLeftRight,
  ArrowUpRight,
  BriefcaseBusiness,
  CalendarPlus,
  CalendarClock,
  HandCoins,
  ListTodo,
  Repeat,
  UserPlus,
  type LucideIcon,
} from "lucide-react";
import { useIsDesktop } from "@/hooks/use-media";
import { cn } from "@/lib/utils";
import { Popover, PopoverContent, PopoverTrigger, Sheet } from "@/components/ui/overlays";
import { Kbd } from "@/components/ui/misc";
import { useUI, type FormRequest } from "./ui-context";

interface QuickAction {
  key: string;
  label: string;
  hint: string;
  icon: LucideIcon;
  tone: string;
  request: FormRequest;
}

export const QUICK_ACTIONS: QuickAction[] = [
  { key: "1", label: "Gasto", hint: "Finanzas", icon: ArrowUpRight, tone: "text-expense bg-expense-soft", request: { kind: "transaction", defaults: { kind: "expense" } } },
  { key: "2", label: "Ingreso", hint: "Finanzas", icon: ArrowDownLeft, tone: "text-income bg-income-soft", request: { kind: "transaction", defaults: { kind: "income" } } },
  { key: "3", label: "Tarea", hint: "Mi Vida", icon: ListTodo, tone: "text-brand bg-brand-soft", request: { kind: "task" } },
  { key: "4", label: "Pago de cliente", hint: "Clientes", icon: HandCoins, tone: "text-income bg-income-soft", request: { kind: "payment" } },
  { key: "5", label: "Trabajo", hint: "Clientes", icon: BriefcaseBusiness, tone: "text-info bg-info-soft", request: { kind: "job" } },
  { key: "6", label: "Cliente", hint: "Clientes", icon: UserPlus, tone: "text-info bg-info-soft", request: { kind: "client" } },
  { key: "7", label: "Evento", hint: "Mi Vida", icon: CalendarPlus, tone: "text-brand bg-brand-soft", request: { kind: "event" } },
  { key: "8", label: "Hábito", hint: "Mi Vida", icon: Repeat, tone: "text-warning bg-warning-soft", request: { kind: "habit" } },
];

const SECONDARY: QuickAction[] = [
  { key: "", label: "Transferencia", hint: "", icon: ArrowLeftRight, tone: "", request: { kind: "transaction", defaults: { kind: "transfer" } } },
  { key: "", label: "Obligación de pago", hint: "", icon: CalendarClock, tone: "", request: { kind: "obligation" } },
];

function ActionGrid({ onPick, showKeys }: { onPick: (r: FormRequest) => void; showKeys: boolean }) {
  return (
    <div>
      <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-4 lg:grid-cols-2">
        {QUICK_ACTIONS.map((a) => (
          <button
            key={a.label}
            type="button"
            onClick={() => onPick(a.request)}
            className="press group flex items-center gap-3 rounded-xl border border-border bg-card p-3 text-left outline-none hover:border-border-strong hover:bg-accent/50 focus-visible:ring-2 focus-visible:ring-ring max-sm:min-h-[60px] lg:p-2.5"
          >
            <span className={cn("flex size-9 shrink-0 items-center justify-center rounded-lg [&_svg]:size-[18px]", a.tone)}>
              <a.icon />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-medium">{a.label}</span>
              <span className="block text-xs text-muted-foreground">{a.hint}</span>
            </span>
            {showKeys && <Kbd className="max-lg:hidden">{a.key}</Kbd>}
          </button>
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5 border-t border-border pt-2">
        {SECONDARY.map((a) => (
          <button
            key={a.label}
            type="button"
            onClick={() => onPick(a.request)}
            className="inline-flex h-9 items-center gap-2 rounded-lg px-2.5 text-[13px] font-medium text-muted-foreground hover:bg-accent hover:text-foreground [&_svg]:size-4"
          >
            <a.icon /> {a.label}
          </button>
        ))}
      </div>
    </div>
  );
}

/** Universal "+" action: popover on desktop, bottom sheet on phones. */
export function QuickAdd({ trigger }: { trigger?: React.ReactNode }) {
  const { quickAddOpen, setQuickAddOpen, openForm } = useUI();
  const desktop = useIsDesktop();

  React.useEffect(() => {
    if (!quickAddOpen || !desktop) return;
    const onKey = (e: KeyboardEvent) => {
      const a = QUICK_ACTIONS.find((x) => x.key === e.key);
      if (a) {
        e.preventDefault();
        openForm(a.request);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [quickAddOpen, desktop, openForm]);

  if (desktop) {
    return (
      <Popover open={quickAddOpen} onOpenChange={setQuickAddOpen}>
        <PopoverTrigger asChild>{trigger}</PopoverTrigger>
        <PopoverContent className="w-[420px] p-2" align="end">
          <p className="px-1 pt-1 pb-2 text-xs font-medium text-muted-foreground">
            Agregar rápido · <Kbd>N</Kbd> abre este menú
          </p>
          <ActionGrid onPick={openForm} showKeys />
        </PopoverContent>
      </Popover>
    );
  }
  return (
    <>
      {trigger && <span onClick={() => setQuickAddOpen(true)}>{trigger}</span>}
      <Sheet open={quickAddOpen} onOpenChange={setQuickAddOpen} title="¿Qué quieres agregar?" layout="center">
        <ActionGrid onPick={openForm} showKeys={false} />
      </Sheet>
    </>
  );
}
