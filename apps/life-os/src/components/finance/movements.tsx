"use client";

import * as React from "react";
import { Download, Plus, Receipt, Search, X } from "lucide-react";
import { useAccountMap, useCategoryMap, useData, useMoney, useToday } from "@/hooks/data";
import type { TransactionKind } from "@/db/types";
import { addDays, endOfMonth, formatDateLong, formatDateNumeric, startOfMonth, addMonthKey, type DateStr } from "@/lib/dates";
import { sumMinor, toMajor } from "@/lib/money";
import { downloadFile, matches, toCSV } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input, NativeSelect } from "@/components/ui/form-controls";
import { Chip } from "@/components/ui/misc";
import { Card, EmptyState, Money } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { TransactionRow } from "./rows";

type Range = "month" | "last-month" | "30" | "90" | "year" | "all" | "custom";

export function rangeBounds(range: Range, today: DateStr, custom: { from: string; to: string }): { from: DateStr; to: DateStr } {
  switch (range) {
    case "month":
      return { from: startOfMonth(today), to: endOfMonth(today) };
    case "last-month": {
      const k = addMonthKey(today.slice(0, 7), -1);
      return { from: `${k}-01`, to: endOfMonth(`${k}-01`) };
    }
    case "30":
      return { from: addDays(today, -29), to: today };
    case "90":
      return { from: addDays(today, -89), to: today };
    case "year":
      return { from: `${today.slice(0, 4)}-01-01`, to: `${today.slice(0, 4)}-12-31` };
    case "all":
      return { from: "1900-01-01", to: "2999-12-31" };
    case "custom":
      return { from: custom.from || "1900-01-01", to: custom.to || "2999-12-31" };
  }
}

export const RANGE_LABEL: Record<Range, string> = {
  month: "Este mes",
  "last-month": "Mes pasado",
  "30": "30 días",
  "90": "90 días",
  year: "Este año",
  all: "Todo",
  custom: "Personalizado",
};

const PAGE = 60;

export function MovementsPage() {
  const data = useData();
  const today = useToday();
  const money = useMoney();
  const cats = useCategoryMap();
  const accounts = useAccountMap();
  const { openForm } = useUI();
  const [query, setQuery] = React.useState("");
  const [kind, setKind] = React.useState<"all" | TransactionKind>("all");
  const [categoryId, setCategoryId] = React.useState("");
  const [accountId, setAccountId] = React.useState("");
  const [range, setRange] = React.useState<Range>("month");
  const [custom, setCustom] = React.useState({ from: "", to: "" });
  const [limit, setLimit] = React.useState(PAGE);

  React.useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const t = p.get("tipo");
    if (t === "income" || t === "expense" || t === "transfer") setKind(t);
    const c = p.get("categoria");
    if (c) setCategoryId(c);
  }, []);

  const { from, to } = rangeBounds(range, today, custom);
  const filtered = React.useMemo(() => {
    return data.transactions
      .filter((t) => t.date >= from && t.date <= to)
      .filter((t) => kind === "all" || t.kind === kind)
      .filter((t) => !categoryId || t.categoryId === categoryId)
      .filter((t) => !accountId || t.accountId === accountId || t.toAccountId === accountId)
      .filter((t) =>
        matches([t.description, cats.get(t.categoryId ?? "")?.name, accounts.get(t.accountId)?.name, data.clients.find((c) => c.id === t.clientId)?.name, String(toMajor(t.amount))], query),
      )
      .sort((a, b) => b.date.localeCompare(a.date) || (b.time ?? "").localeCompare(a.time ?? "") || b.createdAt.localeCompare(a.createdAt));
  }, [data.transactions, data.clients, from, to, kind, categoryId, accountId, query, cats, accounts]);

  React.useEffect(() => setLimit(PAGE), [from, to, kind, categoryId, accountId, query]);

  const income = sumMinor(filtered.filter((t) => t.kind === "income").map((t) => t.amount));
  const expense = sumMinor(filtered.filter((t) => t.kind === "expense").map((t) => t.amount));
  const visible = filtered.slice(0, limit);
  const days = new Map<DateStr, typeof visible>();
  for (const t of visible) {
    const list = days.get(t.date);
    if (list) list.push(t);
    else days.set(t.date, [t]);
  }

  const exportCSV = () => {
    const rows: Array<Array<string | number | null>> = [["Fecha", "Hora", "Tipo", "Categoría", "Descripción", "Cuenta", "Cuenta destino", "Cliente", "Valor"]];
    for (const t of filtered) {
      rows.push([
        formatDateNumeric(t.date),
        t.time ?? "",
        t.kind === "income" ? "Ingreso" : t.kind === "expense" ? "Gasto" : "Transferencia",
        cats.get(t.categoryId ?? "")?.name ?? "",
        t.description ?? "",
        accounts.get(t.accountId)?.name ?? "",
        t.toAccountId ? accounts.get(t.toAccountId)?.name ?? "" : "",
        data.clients.find((c) => c.id === t.clientId)?.name ?? "",
        (t.kind === "expense" ? -1 : 1) * toMajor(t.amount),
      ]);
    }
    downloadFile(`movimientos-${from === "1900-01-01" ? "todos" : from}-${to === "2999-12-31" ? today : to}.csv`, toCSV(rows), "text/csv;charset=utf-8");
  };

  const hasFilters = query || kind !== "all" || categoryId || accountId;

  return (
    <SectionPage
      section="finanzas"
      title="Movimientos"
      description="Historial completo con búsqueda, filtros y exportación."
      actions={
        <>
          <Button variant="outline" onClick={exportCSV} disabled={filtered.length === 0}>
            <Download /> Exportar CSV
          </Button>
          <Button onClick={() => openForm({ kind: "transaction" })}>
            <Plus /> Movimiento
          </Button>
        </>
      }
    >
      <Card className="space-y-3 p-3 sm:p-4">
        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar por descripción, categoría, cuenta, cliente o valor" className="pl-9" aria-label="Buscar movimientos" />
        </div>
        <div className="no-scrollbar -mx-3 flex gap-1.5 overflow-x-auto px-3 sm:mx-0 sm:flex-wrap sm:px-0">
          {(Object.keys(RANGE_LABEL) as Range[]).map((r) => (
            <Chip key={r} active={range === r} onClick={() => setRange(r)}>
              {RANGE_LABEL[r]}
            </Chip>
          ))}
        </div>
        {range === "custom" && (
          <div className="grid grid-cols-2 gap-2">
            <Input type="date" aria-label="Desde" value={custom.from} onChange={(e) => setCustom((c) => ({ ...c, from: e.target.value }))} />
            <Input type="date" aria-label="Hasta" value={custom.to} onChange={(e) => setCustom((c) => ({ ...c, to: e.target.value }))} />
          </div>
        )}
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          <NativeSelect aria-label="Tipo" value={kind} onChange={(e) => setKind(e.target.value as typeof kind)}>
            <option value="all">Todos los tipos</option>
            <option value="expense">Gastos</option>
            <option value="income">Ingresos</option>
            <option value="transfer">Transferencias</option>
          </NativeSelect>
          <NativeSelect aria-label="Categoría" value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">Todas las categorías</option>
            {data.categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.kind === "income" ? "Ingreso · " : ""}
                {c.name}
              </option>
            ))}
          </NativeSelect>
          <NativeSelect aria-label="Cuenta" value={accountId} onChange={(e) => setAccountId(e.target.value)}>
            <option value="">Todas las cuentas</option>
            {data.accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </NativeSelect>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border pt-3 text-[13px]">
          <p className="text-muted-foreground">
            {filtered.length} {filtered.length === 1 ? "movimiento" : "movimientos"} · Ingresos <Money amount={income} tone="income" className="font-medium" /> · Gastos <Money amount={expense} className="font-medium text-foreground" /> · Neto{" "}
            <Money amount={income - expense} signed tone="auto" className="font-medium" />
          </p>
          {hasFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setQuery("");
                setKind("all");
                setCategoryId("");
                setAccountId("");
              }}
            >
              <X /> Limpiar filtros
            </Button>
          )}
        </div>
      </Card>

      {filtered.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Receipt />}
            title={data.transactions.length === 0 ? "Aún no hay movimientos" : "Nada coincide con los filtros"}
            description={data.transactions.length === 0 ? "Registra un gasto o ingreso; también se crean solos cuando registras pagos de clientes con cuenta receptora." : "Prueba con otro período o limpia los filtros."}
            action={
              data.transactions.length === 0 ? (
                <Button onClick={() => openForm({ kind: "transaction" })}>
                  <Plus /> Registrar movimiento
                </Button>
              ) : undefined
            }
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {[...days.entries()].map(([date, list]) => {
            const net = sumMinor(list.map((t) => (t.kind === "income" ? t.amount : t.kind === "expense" ? -t.amount : 0)));
            return (
              <section key={date}>
                <div className="sticky top-14 z-10 -mx-1 flex items-baseline justify-between bg-background/90 px-1 py-1.5 backdrop-blur lg:top-16">
                  <h3 className="text-[13px] font-semibold first-letter:uppercase">{date === today ? "Hoy" : formatDateLong(date)}</h3>
                  <Money amount={net} signed tone="muted" className="text-xs" />
                </div>
                <Card>
                  <ul className="px-2 py-1">
                    {list.map((t) => (
                      <TransactionRow key={t.id} tx={t} />
                    ))}
                  </ul>
                </Card>
              </section>
            );
          })}
          {filtered.length > limit && (
            <div className="flex justify-center">
              <Button variant="outline" onClick={() => setLimit((l) => l + PAGE)}>
                Ver más ({filtered.length - limit} restantes)
              </Button>
            </div>
          )}
          <p className="text-center text-xs text-muted-foreground">Total del período: {money(income - expense, { signed: true })}</p>
        </div>
      )}
    </SectionPage>
  );
}
