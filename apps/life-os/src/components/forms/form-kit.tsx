"use client";

import * as React from "react";
import { toast } from "sonner";
import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, type SheetLayout } from "@/components/ui/overlays";
import { errorMessage } from "@/services/common";

export function FormSheet({
  open,
  onOpenChange,
  title,
  description,
  formId,
  submitLabel = "Guardar",
  busy,
  children,
  extraActions,
  layout = "panel",
  submitDisabled,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  title: string;
  description?: React.ReactNode;
  formId: string;
  submitLabel?: string;
  busy?: boolean;
  children: React.ReactNode;
  extraActions?: React.ReactNode;
  layout?: SheetLayout;
  submitDisabled?: boolean;
}) {
  return (
    <Sheet
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      description={description}
      layout={layout}
      footer={
        <>
          {extraActions && <div className="mr-auto flex items-center gap-1">{extraActions}</div>}
          <Button variant="ghost" onClick={() => onOpenChange(false)} className="max-sm:hidden">
            Cancelar
          </Button>
          <Button type="submit" form={formId} disabled={busy || submitDisabled} size="lg" className="max-sm:flex-1 sm:h-9 sm:px-4 sm:text-sm">
            {submitLabel}
          </Button>
        </>
      }
    >
      {children}
    </Sheet>
  );
}

/** Runs a save action with toast feedback. Returns true on success. */
export async function runSave(action: () => Promise<unknown>, success?: string, undo?: () => Promise<unknown>): Promise<boolean> {
  try {
    await action();
    if (success) {
      toast.success(success, undo ? { action: { label: "Deshacer", onClick: () => void undo().catch(() => toast.error("No se pudo deshacer")) } } : undefined);
    }
    return true;
  } catch (e) {
    toast.error(errorMessage(e));
    return false;
  }
}

export function useBusy() {
  const [busy, setBusy] = React.useState(false);
  const wrap = React.useCallback(async <T,>(fn: () => Promise<T>) => {
    setBusy(true);
    try {
      return await fn();
    } finally {
      setBusy(false);
    }
  }, []);
  return [busy, wrap] as const;
}

const LAST_ACCOUNT_KEY = "lifeos:last-account";

export function rememberAccount(kind: string, id: string | null | undefined) {
  if (!id) return;
  try {
    localStorage.setItem(`${LAST_ACCOUNT_KEY}:${kind}`, id);
  } catch {
    /* ignore */
  }
}

export function lastAccount(kind: string): string | null {
  try {
    return localStorage.getItem(`${LAST_ACCOUNT_KEY}:${kind}`);
  } catch {
    return null;
  }
}

export function Disclosure({ label, children, defaultOpen = false }: { label: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = React.useState(defaultOpen);
  return (
    <div className="rounded-lg border border-dashed border-border">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-3 py-2.5 text-[13px] font-medium text-muted-foreground hover:text-foreground"
      >
        {label}
        <ChevronDown aria-hidden className={`size-4 transition-transform duration-200 ${open ? "rotate-180" : ""}`} />
      </button>
      {open && <div className="space-y-4 border-t border-dashed border-border px-3 pt-3 pb-3">{children}</div>}
    </div>
  );
}
