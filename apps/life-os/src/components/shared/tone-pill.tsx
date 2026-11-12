import * as React from "react";
import { cn } from "@/lib/utils";
import { toneStyle } from "./primitives";

/** Notion-style coloured label used for statuses, priorities and categories. */
export function TonePill({ color, children, dot = true, className }: { color: string; children: React.ReactNode; dot?: boolean; className?: string }) {
  return (
    <span style={toneStyle(color)} className={cn("inline-flex max-w-full items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium whitespace-nowrap tone-soft", className)}>
      {dot && <span className="size-1.5 shrink-0 rounded-full tone-dot" aria-hidden />}
      <span className="truncate">{children}</span>
    </span>
  );
}
