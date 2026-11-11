"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

export const badgeVariants = cva(
  "inline-flex max-w-full shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap [&_svg]:size-3",
  {
    variants: {
      tone: {
        neutral: "bg-secondary text-muted-foreground",
        brand: "bg-brand-soft text-brand",
        income: "bg-income-soft text-income",
        expense: "bg-expense-soft text-expense",
        warning: "bg-warning-soft text-warning",
        info: "bg-info-soft text-info",
        outline: "border border-border text-muted-foreground",
      },
    },
    defaultVariants: { tone: "neutral" },
  },
);

export function Badge({ className, tone, ...props }: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ tone }), className)} {...props} />;
}

export function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("animate-pulse rounded-lg bg-muted", className)} {...props} />;
}

export type ProgressTone = "brand" | "income" | "warning" | "expense" | "neutral";

export function Progress({
  value,
  tone = "brand",
  className,
  label,
}: {
  value: number;
  tone?: ProgressTone;
  className?: string;
  label?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value));
  const color = {
    brand: "bg-brand",
    income: "bg-income",
    warning: "bg-warning",
    expense: "bg-expense",
    neutral: "bg-foreground/60",
  }[tone];
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(clamped)}
      aria-label={label}
      className={cn("h-1.5 w-full overflow-hidden rounded-full bg-muted", className)}
    >
      <div className={cn("h-full rounded-full transition-[width] duration-500 ease-[var(--ease-out)]", color)} style={{ width: `${clamped}%` }} />
    </div>
  );
}

/** Segmented control (single choice). Keyboard: arrows move, like a radio group. */
export function Segmented<T extends string>({
  value,
  onChange,
  options,
  className,
  size = "md",
  ariaLabel,
}: {
  value: T;
  onChange: (v: T) => void;
  options: Array<{ value: T; label: React.ReactNode; icon?: React.ReactNode }>;
  className?: string;
  size?: "sm" | "md";
  ariaLabel?: string;
}) {
  const refs = React.useRef<Array<HTMLButtonElement | null>>([]);
  return (
    <div role="radiogroup" aria-label={ariaLabel} className={cn("inline-flex rounded-lg bg-secondary p-0.5", className)}>
      {options.map((o, i) => {
        const active = o.value === value;
        return (
          <button
            key={o.value}
            ref={(el) => {
              refs.current[i] = el;
            }}
            type="button"
            role="radio"
            aria-checked={active}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(o.value)}
            onKeyDown={(e) => {
              if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
                e.preventDefault();
                const next = (i + (e.key === "ArrowRight" ? 1 : -1) + options.length) % options.length;
                onChange(options[next].value);
                refs.current[next]?.focus();
              }
            }}
            className={cn(
              "inline-flex flex-1 items-center justify-center gap-1.5 rounded-md font-medium whitespace-nowrap text-muted-foreground transition-[color,background-color,box-shadow] duration-150 outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring [&_svg]:size-3.5",
              size === "sm" ? "h-7 px-2.5 text-xs" : "h-8 px-3 text-[13px]",
              active && "bg-card text-foreground shadow-[0_1px_2px_oklch(0.2_0.01_75/0.12)] dark:bg-accent",
            )}
          >
            {o.icon}
            {o.label}
          </button>
        );
      })}
    </div>
  );
}

export function Separator({ className }: { className?: string }) {
  return <div role="separator" className={cn("h-px w-full bg-border", className)} />;
}

export function Kbd({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <kbd className={cn("inline-flex h-5 min-w-5 items-center justify-center rounded border border-border bg-card px-1 font-sans text-[11px] text-muted-foreground", className)}>
      {children}
    </kbd>
  );
}

/** Chip-style toggle used for quick picks (dates, categories, weekdays). */
export function Chip({
  active,
  className,
  ...props
}: React.ComponentProps<"button"> & { active?: boolean }) {
  return (
    <button
      type="button"
      aria-pressed={active}
      className={cn(
        "press inline-flex h-8 shrink-0 items-center gap-1.5 rounded-full border px-3 text-[13px] font-medium whitespace-nowrap transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring [&_svg]:size-3.5",
        active ? "border-foreground bg-foreground text-background" : "border-border bg-card text-muted-foreground hover:border-border-strong hover:text-foreground",
        className,
      )}
      {...props}
    />
  );
}
