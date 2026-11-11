"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import { Dialog as DialogPrimitive } from "radix-ui";
import { ArrowRight, BriefcaseBusiness, CalendarDays, CalendarClock, ListTodo, Receipt, Search, Settings, User } from "lucide-react";
import { useData, useMoney } from "@/hooks/data";
import { formatDateShort } from "@/lib/dates";
import { normalize } from "@/lib/utils";
import { NAV } from "./nav";
import { QUICK_ACTIONS } from "./quick-add";
import { useUI } from "./ui-context";

function Item({ value, keywords, onSelect, icon, children, meta }: { value: string; keywords?: string[]; onSelect: () => void; icon: React.ReactNode; children: React.ReactNode; meta?: React.ReactNode }) {
  return (
    <Command.Item
      value={value}
      keywords={keywords}
      onSelect={onSelect}
      className="flex cursor-pointer items-center gap-3 rounded-lg px-2.5 py-2 text-sm outline-none select-none data-[selected=true]:bg-accent [&>svg]:size-4 [&>svg]:shrink-0 [&>svg]:text-muted-foreground"
    >
      {icon}
      <span className="min-w-0 flex-1 truncate">{children}</span>
      {meta && <span className="shrink-0 text-xs text-muted-foreground tabular">{meta}</span>}
    </Command.Item>
  );
}

function Group({ heading, children }: { heading: string; children: React.ReactNode }) {
  return (
    <Command.Group heading={heading} className="mb-1 [&_[cmdk-group-heading]]:px-2.5 [&_[cmdk-group-heading]]:pt-2 [&_[cmdk-group-heading]]:pb-1 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground">
      {children}
    </Command.Group>
  );
}

export function SearchCommand() {
  const { searchOpen, setSearchOpen, openForm, openDetail } = useUI();
  const data = useData();
  const money = useMoney();
  const router = useRouter();
  const [query, setQuery] = React.useState("");
  const cats = React.useMemo(() => new Map(data.categories.map((c) => [c.id, c.name])), [data.categories]);
  const clientName = React.useMemo(() => new Map(data.clients.map((c) => [c.id, c.name])), [data.clients]);
  const recentTx = React.useMemo(
    () => [...data.transactions].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 300),
    [data.transactions],
  );
  const run = (fn: () => void) => {
    setSearchOpen(false);
    setQuery("");
    setTimeout(fn, 10);
  };
  const showData = query.trim().length > 0;

  return (
    <DialogPrimitive.Root open={searchOpen} onOpenChange={(v) => { setSearchOpen(v); if (!v) setQuery(""); }}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/35 data-[state=open]:animate-in data-[state=open]:fade-in data-[state=closed]:animate-out data-[state=closed]:fade-out" />
        <DialogPrimitive.Content className="fixed top-3 left-1/2 z-50 w-[calc(100%-1.5rem)] max-w-[600px] -translate-x-1/2 overflow-hidden rounded-xl border border-border bg-popover shadow-pop data-[state=open]:animate-in data-[state=open]:fade-in data-[state=open]:slide-in-from-top-2 data-[state=closed]:animate-out data-[state=closed]:fade-out sm:top-[12vh]">
          <DialogPrimitive.Title className="sr-only">Buscar</DialogPrimitive.Title>
          <DialogPrimitive.Description className="sr-only">Busca clientes, trabajos, tareas y movimientos, o ejecuta una acción.</DialogPrimitive.Description>
          <Command
            label="Búsqueda global"
            loop
            filter={(value, search, keywords) => {
              const terms = normalize(search).split(/\s+/).filter(Boolean);
              const hay = normalize(`${value} ${(keywords ?? []).join(" ")}`);
              return terms.every((t) => hay.includes(t)) ? 1 : 0;
            }}
          >
            <div className="flex items-center gap-2 border-b border-border px-3">
              <Search className="size-4 shrink-0 text-muted-foreground" />
              <Command.Input
                value={query}
                onValueChange={setQuery}
                placeholder="Buscar clientes, trabajos, tareas, movimientos…"
                className="h-12 w-full bg-transparent text-[15px] outline-none placeholder:text-subtle"
              />
            </div>
            <Command.List className="max-h-[min(60vh,440px)] overflow-y-auto overscroll-contain p-1.5">
              <Command.Empty className="px-3 py-8 text-center text-sm text-muted-foreground">Sin resultados para «{query}».</Command.Empty>
              <Group heading="Crear">
                {QUICK_ACTIONS.map((a) => (
                  <Item key={a.label} value={`crear ${a.label}`} keywords={["nuevo", "agregar", "registrar"]} onSelect={() => run(() => openForm(a.request))} icon={<a.icon />}>
                    Nuevo: {a.label.toLowerCase()}
                  </Item>
                ))}
              </Group>
              <Group heading="Ir a">
                {NAV.flatMap((s) =>
                  s.items.map((i) => (
                    <Item key={i.href} value={`ir ${s.label} ${i.label}`} onSelect={() => run(() => router.push(i.href))} icon={<ArrowRight />}>
                      {s.label} › {i.label}
                    </Item>
                  )),
                )}
                <Item value="ir ajustes configuración" onSelect={() => run(() => router.push("/ajustes/"))} icon={<Settings />}>
                  Ajustes
                </Item>
              </Group>
              {showData && (
                <>
                  <Group heading="Clientes">
                    {data.clients.map((c) => (
                      <Item key={c.id} value={`cliente ${c.name} ${c.company ?? ""} ${c.id}`} keywords={[c.serviceType ?? "", ...c.tags]} onSelect={() => run(() => openDetail({ type: "client", id: c.id }))} icon={<User />} meta={c.archived ? "Archivado" : c.company}>
                        {c.name}
                      </Item>
                    ))}
                  </Group>
                  <Group heading="Trabajos">
                    {data.jobs.map((j) => (
                      <Item key={j.id} value={`trabajo ${j.title} ${clientName.get(j.clientId) ?? ""} ${j.id}`} onSelect={() => run(() => openDetail({ type: "job", id: j.id }))} icon={<BriefcaseBusiness />} meta={clientName.get(j.clientId)}>
                        {j.title}
                      </Item>
                    ))}
                  </Group>
                  <Group heading="Tareas">
                    {data.tasks.map((t) => (
                      <Item key={t.id} value={`tarea ${t.title} ${t.id}`} onSelect={() => run(() => openForm({ kind: "task", id: t.id }))} icon={<ListTodo />} meta={t.status === "done" ? "Hecha" : t.date ? formatDateShort(t.date) : "Sin fecha"}>
                        {t.title}
                      </Item>
                    ))}
                  </Group>
                  <Group heading="Eventos">
                    {data.events.map((e) => (
                      <Item key={e.id} value={`evento ${e.title} ${e.id}`} onSelect={() => run(() => openForm({ kind: "event", id: e.id }))} icon={<CalendarDays />} meta={formatDateShort(e.date)}>
                        {e.title}
                      </Item>
                    ))}
                  </Group>
                  <Group heading="Obligaciones">
                    {data.obligations.map((o) => (
                      <Item key={o.id} value={`obligación pago ${o.name} ${o.id}`} onSelect={() => run(() => openForm({ kind: "obligation", id: o.id }))} icon={<CalendarClock />} meta={money(o.amount)}>
                        {o.name}
                      </Item>
                    ))}
                  </Group>
                  <Group heading="Movimientos recientes">
                    {recentTx.map((t) => (
                      <Item
                        key={t.id}
                        value={`movimiento ${t.description ?? ""} ${cats.get(t.categoryId ?? "") ?? ""} ${t.id}`}
                        onSelect={() => run(() => openForm({ kind: "transaction", id: t.id }))}
                        icon={<Receipt />}
                        meta={`${t.kind === "expense" ? "−" : t.kind === "income" ? "+" : ""}${money(t.amount)} · ${formatDateShort(t.date)}`}
                      >
                        {t.description || cats.get(t.categoryId ?? "") || "Movimiento"}
                      </Item>
                    ))}
                  </Group>
                </>
              )}
            </Command.List>
          </Command>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
