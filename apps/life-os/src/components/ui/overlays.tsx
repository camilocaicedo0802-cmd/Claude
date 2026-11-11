"use client";

import * as React from "react";
import { AlertDialog as AlertPrimitive, Dialog as DialogPrimitive, DropdownMenu as MenuPrimitive, Popover as PopoverPrimitive, Tooltip as TooltipPrimitive } from "radix-ui";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

// ── Sheet: bottom sheet on phones, side panel or centered dialog on desktop ──

export type SheetLayout = "panel" | "center";

export function Sheet({
  open,
  onOpenChange,
  title,
  description,
  children,
  footer,
  layout = "panel",
  className,
  wide,
  headerExtra,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: React.ReactNode;
  description?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  layout?: SheetLayout;
  className?: string;
  wide?: boolean;
  headerExtra?: React.ReactNode;
}) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-[oklch(0.15_0.01_75/0.32)] backdrop-blur-[2px] data-[state=open]:animate-in data-[state=open]:fade-in data-[state=closed]:animate-out data-[state=closed]:fade-out dark:bg-black/55" />
        <DialogPrimitive.Content
          aria-describedby={description ? undefined : undefined}
          className={cn(
            "fixed z-50 flex flex-col bg-popover text-popover-foreground shadow-pop outline-none",
            // phones: bottom sheet
            "inset-x-0 bottom-0 max-h-[92dvh] rounded-t-2xl border-t border-border duration-300 ease-[var(--ease-out)] data-[state=open]:animate-in data-[state=open]:slide-in-from-bottom data-[state=closed]:animate-out data-[state=closed]:slide-out-to-bottom data-[state=closed]:duration-200",
            layout === "panel" &&
              "lg:inset-x-auto lg:top-2 lg:right-2 lg:bottom-2 lg:max-h-none lg:rounded-xl lg:border lg:data-[state=open]:slide-in-from-right-8 lg:data-[state=open]:slide-in-from-bottom-0 lg:data-[state=open]:fade-in lg:data-[state=closed]:slide-out-to-right-8 lg:data-[state=closed]:slide-out-to-bottom-0 lg:data-[state=closed]:fade-out",
            layout === "panel" && (wide ? "lg:w-[560px]" : "lg:w-[460px]"),
            layout === "center" &&
              "lg:inset-x-auto lg:top-[10vh] lg:bottom-auto lg:left-1/2 lg:max-h-[80vh] lg:w-[520px] lg:-translate-x-1/2 lg:rounded-xl lg:border lg:data-[state=open]:slide-in-from-bottom-2 lg:data-[state=open]:fade-in lg:data-[state=open]:zoom-in-[0.98] lg:data-[state=closed]:slide-out-to-bottom-0 lg:data-[state=closed]:fade-out",
            className,
          )}
        >
          <div className="mx-auto mt-2 h-1 w-9 shrink-0 rounded-full bg-border-strong lg:hidden" aria-hidden />
          <header className="flex shrink-0 items-start gap-3 px-5 pt-3 pb-3 lg:pt-5">
            <div className="min-w-0 flex-1">
              <DialogPrimitive.Title className="text-[17px] leading-snug font-semibold tracking-tight">{title}</DialogPrimitive.Title>
              {description ? (
                <DialogPrimitive.Description className="mt-0.5 text-[13px] text-muted-foreground">{description}</DialogPrimitive.Description>
              ) : (
                <DialogPrimitive.Description className="sr-only">{typeof title === "string" ? title : "Detalle"}</DialogPrimitive.Description>
              )}
            </div>
            {headerExtra}
            <DialogPrimitive.Close asChild>
              <Button variant="ghost" size="icon-sm" aria-label="Cerrar" className="-mt-1 -mr-2 text-muted-foreground">
                <X />
              </Button>
            </DialogPrimitive.Close>
          </header>
          <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-5 pb-5">{children}</div>
          {footer && (
            <footer className="flex shrink-0 items-center justify-end gap-2 border-t border-border px-5 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
              {footer}
            </footer>
          )}
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

// ── Confirm dialog ───────────────────────────────────────────────────────────

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  destructive,
  onConfirm,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: React.ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  onConfirm: () => void | Promise<void>;
}) {
  const [busy, setBusy] = React.useState(false);
  return (
    <AlertPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <AlertPrimitive.Portal>
        <AlertPrimitive.Overlay className="fixed inset-0 z-[60] bg-black/40 data-[state=open]:animate-in data-[state=open]:fade-in data-[state=closed]:animate-out data-[state=closed]:fade-out" />
        <AlertPrimitive.Content className="fixed top-1/2 left-1/2 z-[60] w-[calc(100%-2rem)] max-w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-popover p-5 shadow-pop data-[state=open]:animate-in data-[state=open]:fade-in data-[state=open]:zoom-in-[0.97] data-[state=closed]:animate-out data-[state=closed]:fade-out">
          <AlertPrimitive.Title className="text-base font-semibold">{title}</AlertPrimitive.Title>
          {description ? (
            <AlertPrimitive.Description className="mt-2 text-sm text-muted-foreground">{description}</AlertPrimitive.Description>
          ) : (
            <AlertPrimitive.Description className="sr-only">{title}</AlertPrimitive.Description>
          )}
          <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <AlertPrimitive.Cancel asChild>
              <Button variant="outline">{cancelLabel}</Button>
            </AlertPrimitive.Cancel>
            <Button
              variant={destructive ? "destructive" : "default"}
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                try {
                  await onConfirm();
                  onOpenChange(false);
                } finally {
                  setBusy(false);
                }
              }}
            >
              {confirmLabel}
            </Button>
          </div>
        </AlertPrimitive.Content>
      </AlertPrimitive.Portal>
    </AlertPrimitive.Root>
  );
}

// ── Dropdown menu ────────────────────────────────────────────────────────────

export const DropdownMenu = MenuPrimitive.Root;
export const DropdownMenuTrigger = MenuPrimitive.Trigger;

export function DropdownMenuContent({ className, align = "end", sideOffset = 6, ...props }: React.ComponentProps<typeof MenuPrimitive.Content>) {
  return (
    <MenuPrimitive.Portal>
      <MenuPrimitive.Content
        align={align}
        sideOffset={sideOffset}
        className={cn(
          "z-50 min-w-48 overflow-hidden rounded-xl border border-border bg-popover p-1 text-popover-foreground shadow-pop data-[state=open]:animate-in data-[state=open]:fade-in data-[state=open]:zoom-in-[0.97] data-[state=closed]:animate-out data-[state=closed]:fade-out",
          className,
        )}
        {...props}
      />
    </MenuPrimitive.Portal>
  );
}

export function DropdownMenuItem({ className, destructive, ...props }: React.ComponentProps<typeof MenuPrimitive.Item> & { destructive?: boolean }) {
  return (
    <MenuPrimitive.Item
      className={cn(
        "relative flex cursor-pointer items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm outline-none select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 data-[highlighted]:bg-accent [&_svg]:size-4 [&_svg]:text-muted-foreground",
        destructive && "text-destructive data-[highlighted]:bg-expense-soft [&_svg]:text-destructive",
        className,
      )}
      {...props}
    />
  );
}

export function DropdownMenuSeparator({ className, ...props }: React.ComponentProps<typeof MenuPrimitive.Separator>) {
  return <MenuPrimitive.Separator className={cn("-mx-1 my-1 h-px bg-border", className)} {...props} />;
}

export function DropdownMenuLabel({ className, ...props }: React.ComponentProps<typeof MenuPrimitive.Label>) {
  return <MenuPrimitive.Label className={cn("px-2.5 pt-1.5 pb-1 text-xs font-medium text-muted-foreground", className)} {...props} />;
}

// ── Popover ──────────────────────────────────────────────────────────────────

export const Popover = PopoverPrimitive.Root;
export const PopoverTrigger = PopoverPrimitive.Trigger;
export const PopoverAnchor = PopoverPrimitive.Anchor;

export function PopoverContent({ className, align = "end", sideOffset = 8, ...props }: React.ComponentProps<typeof PopoverPrimitive.Content>) {
  return (
    <PopoverPrimitive.Portal>
      <PopoverPrimitive.Content
        align={align}
        sideOffset={sideOffset}
        collisionPadding={12}
        className={cn(
          "z-50 rounded-xl border border-border bg-popover p-3 text-popover-foreground shadow-pop outline-none data-[state=open]:animate-in data-[state=open]:fade-in data-[state=open]:zoom-in-[0.97] data-[state=closed]:animate-out data-[state=closed]:fade-out",
          className,
        )}
        {...props}
      />
    </PopoverPrimitive.Portal>
  );
}

// ── Tooltip ──────────────────────────────────────────────────────────────────

export const TooltipProvider = TooltipPrimitive.Provider;

export function Tooltip({ content, children, side = "bottom" }: { content: React.ReactNode; children: React.ReactNode; side?: "top" | "bottom" | "left" | "right" }) {
  return (
    <TooltipPrimitive.Root delayDuration={350}>
      <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
      <TooltipPrimitive.Portal>
        <TooltipPrimitive.Content
          side={side}
          sideOffset={6}
          className="z-[70] rounded-md bg-primary px-2 py-1 text-xs text-primary-foreground shadow-pop data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in data-[state=closed]:animate-out data-[state=closed]:fade-out"
        >
          {content}
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Portal>
    </TooltipPrimitive.Root>
  );
}
