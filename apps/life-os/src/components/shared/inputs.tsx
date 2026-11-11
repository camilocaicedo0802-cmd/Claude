"use client";

import * as React from "react";
import { useData, useToday } from "@/hooks/data";
import { addDays, formatDateShort, WEEKDAY_LETTER, orderedWeekdays, type DateStr } from "@/lib/dates";
import { currencyDecimals, moneyToInput, parseMoney, type Minor } from "@/lib/money";
import { cn } from "@/lib/utils";
import { Chip } from "@/components/ui/misc";
import { Input, NativeSelect } from "@/components/ui/form-controls";
import type { Account, CategoryKind } from "@/db/types";
import { DynamicIcon, toneStyle } from "./primitives";

/** Formats thousands as you type (COP: "1.250.000"); keeps a comma for decimals in other currencies. */
export function formatAmountTyping(raw: string, currency: string): string {
  const decimals = currencyDecimals(currency);
  let cleaned = raw.replace(/[^\d,]/g, "");
  if (decimals === 0) cleaned = cleaned.replace(/,/g, "");
  const [int, ...rest] = cleaned.split(",");
  const intDigits = int.replace(/^0+(?=\d)/, "");
  const grouped = intDigits.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  if (rest.length === 0) return grouped;
  return `${grouped || "0"},${rest.join("").slice(0, decimals)}`;
}

export function AmountInput({
  value,
  onChange,
  id,
  autoFocus,
  className,
  large,
  ariaInvalid,
  placeholder = "0",
}: {
  value: string;
  onChange: (v: string) => void;
  id?: string;
  autoFocus?: boolean;
  className?: string;
  large?: boolean;
  ariaInvalid?: boolean;
  placeholder?: string;
}) {
  const data = useData();
  const currency = data.settings.currency;
  return (
    <div className={cn("relative", className)}>
      <span
        className={cn(
          "pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-muted-foreground",
          large ? "text-xl font-medium" : "text-sm",
        )}
      >
        $
      </span>
      <Input
        id={id}
        inputMode={currencyDecimals(currency) ? "decimal" : "numeric"}
        autoComplete="off"
        autoFocus={autoFocus}
        aria-invalid={ariaInvalid || undefined}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(formatAmountTyping(e.target.value, currency))}
        className={cn("tabular pl-7", large && "h-14 pl-8 text-[28px] font-semibold tracking-tight sm:h-14")}
      />
    </div>
  );
}

export function amountFrom(text: string): Minor | null {
  return parseMoney(text);
}

export function amountToText(m: Minor | null | undefined, currency = "COP") {
  return moneyToInput(m, currency);
}

/** Native date input plus quick picks (Hoy, Mañana…). */
export function DateField({
  value,
  onChange,
  id,
  quick = ["today", "tomorrow"],
  allowEmpty,
  emptyLabel = "Sin fecha",
}: {
  value: DateStr | null | undefined;
  onChange: (v: DateStr | null) => void;
  id?: string;
  quick?: Array<"today" | "tomorrow" | "yesterday" | "nextweek" | "weekend">;
  allowEmpty?: boolean;
  emptyLabel?: string;
}) {
  const today = useToday();
  const options: Record<string, { label: string; date: DateStr }> = {
    yesterday: { label: "Ayer", date: addDays(today, -1) },
    today: { label: "Hoy", date: today },
    tomorrow: { label: "Mañana", date: addDays(today, 1) },
    nextweek: { label: "En una semana", date: addDays(today, 7) },
    weekend: { label: "Sábado", date: addDays(today, (6 - new Date(`${today}T12:00:00`).getDay() + 7) % 7 || 7) },
  };
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-1.5">
        {quick.map((q) => (
          <Chip key={q} active={value === options[q].date} onClick={() => onChange(options[q].date)}>
            {options[q].label}
          </Chip>
        ))}
        {allowEmpty && (
          <Chip active={!value} onClick={() => onChange(null)}>
            {emptyLabel}
          </Chip>
        )}
      </div>
      <Input id={id} type="date" value={value ?? ""} onChange={(e) => onChange(e.target.value || null)} className="tabular" />
      {value && !quick.some((q) => options[q].date === value) && (
        <span className="sr-only">{formatDateShort(value)}</span>
      )}
    </div>
  );
}

export function AccountSelect({
  value,
  onChange,
  id,
  allowNone,
  noneLabel = "Sin cuenta",
  exclude,
  filter,
}: {
  value: string | null | undefined;
  onChange: (v: string | null) => void;
  id?: string;
  allowNone?: boolean;
  noneLabel?: string;
  exclude?: string | null;
  filter?: (a: Account) => boolean;
}) {
  const data = useData();
  const accounts = data.accounts.filter((a) => !a.archived && a.id !== exclude && (!filter || filter(a)));
  return (
    <NativeSelect id={id} value={value ?? ""} onChange={(e) => onChange(e.target.value || null)}>
      {(allowNone || !value) && <option value="">{allowNone ? noneLabel : "Elige una cuenta"}</option>}
      {accounts.map((a) => (
        <option key={a.id} value={a.id}>
          {a.name}
          {a.type === "credit" ? " (tarjeta)" : ""}
        </option>
      ))}
    </NativeSelect>
  );
}

/** Category chips: one tap to choose. */
export function CategoryPicker({
  kind,
  value,
  onChange,
  id,
}: {
  kind: CategoryKind;
  value: string | null | undefined;
  onChange: (v: string) => void;
  id?: string;
}) {
  const data = useData();
  const cats = data.categories.filter((c) => c.kind === kind && !c.archived);
  return (
    <div id={id} role="radiogroup" aria-label="Categoría" className="grid grid-cols-3 gap-1.5 sm:grid-cols-4">
      {cats.map((c) => {
        const active = c.id === value;
        return (
          <button
            key={c.id}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(c.id)}
            style={toneStyle(c.color)}
            className={cn(
              "press flex min-h-[60px] flex-col items-center justify-center gap-1 rounded-lg border px-1 py-2 text-center text-[11.5px] leading-tight font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring",
              active ? "tone-border tone-soft border-2" : "border-border bg-card text-muted-foreground hover:border-border-strong hover:text-foreground",
            )}
          >
            <span className={cn("[&_svg]:size-4", active ? "" : "tone-text")}>
              <DynamicIcon name={c.icon} />
            </span>
            <span className="line-clamp-2">{c.name}</span>
          </button>
        );
      })}
    </div>
  );
}

export function WeekdayPicker({ value, onChange, weekStartsOn }: { value: number[]; onChange: (v: number[]) => void; weekStartsOn: number }) {
  const names = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
  return (
    <div className="flex gap-1.5" role="group" aria-label="Días de la semana">
      {orderedWeekdays(weekStartsOn).map((d) => {
        const on = value.includes(d);
        return (
          <button
            key={d}
            type="button"
            aria-pressed={on}
            aria-label={names[d]}
            onClick={() => onChange(on ? value.filter((x) => x !== d) : [...value, d].sort())}
            className={cn(
              "press flex size-9 items-center justify-center rounded-full border text-[13px] font-semibold transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring",
              on ? "border-foreground bg-foreground text-background" : "border-border bg-card text-muted-foreground hover:text-foreground",
            )}
          >
            {WEEKDAY_LETTER[d]}
          </button>
        );
      })}
    </div>
  );
}

export function ColorPicker({ value, onChange, colors }: { value: string; onChange: (v: string) => void; colors: readonly string[] }) {
  return (
    <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Color">
      {colors.map((c) => (
        <button
          key={c}
          type="button"
          role="radio"
          aria-checked={value === c}
          aria-label={c}
          onClick={() => onChange(c)}
          style={toneStyle(c)}
          className={cn(
            "size-7 rounded-full tone-dot outline-none ring-offset-2 ring-offset-popover transition-shadow focus-visible:ring-2 focus-visible:ring-ring",
            value === c && "ring-2 ring-foreground",
          )}
        />
      ))}
    </div>
  );
}

export function IconPicker({ value, onChange, icons, color }: { value: string; onChange: (v: string) => void; icons: string[]; color: string }) {
  return (
    <div className="grid grid-cols-8 gap-1.5" role="radiogroup" aria-label="Icono">
      {icons.map((i) => (
        <button
          key={i}
          type="button"
          role="radio"
          aria-checked={value === i}
          aria-label={i}
          onClick={() => onChange(i)}
          style={toneStyle(color)}
          className={cn(
            "flex aspect-square items-center justify-center rounded-lg border outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring [&_svg]:size-4",
            value === i ? "tone-soft tone-border border-2" : "border-border text-muted-foreground hover:text-foreground",
          )}
        >
          <DynamicIcon name={i} />
        </button>
      ))}
    </div>
  );
}
