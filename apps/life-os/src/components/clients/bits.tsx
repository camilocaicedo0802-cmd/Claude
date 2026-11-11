"use client";

import * as React from "react";
import { CalendarClock, Flag } from "lucide-react";
import { cn } from "@/lib/utils";
import type { JobStatus, Priority } from "@/db/types";
import { PAYMENT_STATE_LABEL, PRIORITY_LABEL, type JobView, type PaymentState } from "@/domain/clients";
import { formatRelativeDay } from "@/lib/dates";
import { Badge } from "@/components/ui/misc";
import { ColorDot, Money, toneStyle } from "@/components/shared/primitives";
import { useToday } from "@/hooks/data";

export function StatusBadge({ status, className }: { status: JobStatus | undefined; className?: string }) {
  if (!status) return null;
  return (
    <span style={toneStyle(status.color)} className={cn("inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium tone-soft whitespace-nowrap", className)}>
      <span className="size-1.5 rounded-full tone-dot" aria-hidden />
      {status.name}
    </span>
  );
}

const PAYMENT_TONE: Record<PaymentState, "neutral" | "income" | "warning" | "expense" | "info"> = {
  unbilled: "neutral",
  unpaid: "neutral",
  partial: "info",
  paid: "income",
  overdue: "expense",
};

export function PaymentBadge({ state, className }: { state: PaymentState; className?: string }) {
  return (
    <Badge tone={PAYMENT_TONE[state]} className={className}>
      {PAYMENT_STATE_LABEL[state]}
    </Badge>
  );
}

export function PriorityFlag({ priority, className }: { priority: Priority; className?: string }) {
  if (priority === "low" || priority === "medium") return null;
  return (
    <span className={cn("inline-flex items-center gap-1 text-xs font-medium", priority === "urgent" ? "text-expense" : "text-warning", className)}>
      <Flag className="size-3" aria-hidden />
      {PRIORITY_LABEL[priority]}
    </span>
  );
}

export function DueLabel({ view, className }: { view: JobView; className?: string }) {
  const today = useToday();
  if (!view.job.dueDate) return <span className={cn("text-xs text-subtle", className)}>Sin fecha</span>;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs tabular",
        view.isOverdue ? "font-medium text-expense" : view.dueSoon ? "font-medium text-warning" : "text-muted-foreground",
        className,
      )}
    >
      <CalendarClock className="size-3" aria-hidden />
      {view.isOpen ? formatRelativeDay(view.job.dueDate, today) : formatRelativeDay(view.job.dueDate, today)}
      {view.isOverdue && " · atrasado"}
    </span>
  );
}

/** Compact job card used in the Kanban, lists and the client sheet. */
export function JobCard({ view, onOpen, showClient = true, className, dragHandle }: { view: JobView; onOpen: () => void; showClient?: boolean; className?: string; dragHandle?: React.ReactNode }) {
  return (
    <div className={cn("group relative rounded-lg border border-border bg-card shadow-[var(--shadow-card)] transition-colors hover:border-border-strong", className)}>
      <button type="button" onClick={onOpen} className="block w-full rounded-lg p-3 text-left outline-none focus-visible:ring-2 focus-visible:ring-ring">
        {showClient && <div className="truncate text-xs font-medium text-muted-foreground">{view.client?.name ?? "Sin cliente"}</div>}
        <div className="mt-0.5 line-clamp-2 text-sm leading-snug font-medium">{view.job.title}</div>
        <div className="mt-2.5 flex flex-wrap items-center gap-x-2.5 gap-y-1.5">
          <DueLabel view={view} />
          <PriorityFlag priority={view.job.priority} />
        </div>
        <div className="mt-2 flex items-center justify-between gap-2">
          <PaymentBadge state={view.finance.state} />
          {view.finance.balance > 0 && view.kind !== "cancelled" && (
            <span className="text-xs text-muted-foreground">
              Debe <Money amount={view.finance.balance} className="font-medium text-foreground" />
            </span>
          )}
        </div>
      </button>
      {dragHandle}
    </div>
  );
}

export function StatusDot({ color }: { color: string }) {
  return <ColorDot color={color} />;
}
