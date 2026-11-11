"use client";

import * as React from "react";
import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  MouseSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { ArrowDown, ArrowUp, Columns3, FileStack, GripVertical, List, Plus, Search, Settings2, Trash2 } from "lucide-react";
import { useData, useJobViews, useMoney, useToday } from "@/hooks/data";
import { useMediaQuery } from "@/hooks/use-media";
import type { JobStatusKind } from "@/db/types";
import { PRIORITY_LABEL, type JobView } from "@/domain/clients";
import { matches, cn } from "@/lib/utils";
import { parseMoney } from "@/lib/money";
import { Button } from "@/components/ui/button";
import { Field, Input, NativeSelect, Textarea } from "@/components/ui/form-controls";
import { Chip, Segmented } from "@/components/ui/misc";
import { Sheet } from "@/components/ui/overlays";
import { Card, EmptyState, Money } from "@/components/shared/primitives";
import { AmountInput, ColorPicker, amountToText } from "@/components/shared/inputs";
import { PALETTE } from "@/components/shared/primitives";
import { SectionPage } from "@/components/shared/section-page";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { deleteJobStatus, deleteTemplate, reorderJobStatuses, saveJobStatus, saveTemplate, setJobStatus } from "@/services/clients-service";
import { DueLabel, JobCard, PaymentBadge, PriorityFlag, StatusBadge } from "./bits";

type JobFilter = "all" | "pendientes" | "proximos" | "atrasados" | "terminados" | "cobro";
const FILTER_LABEL: Record<JobFilter, string> = {
  all: "Todos",
  pendientes: "Pendientes",
  proximos: "Próximos a vencer",
  atrasados: "Atrasados",
  terminados: "Terminados",
  cobro: "Con saldo por cobrar",
};

const PRIORITY_RANK = { urgent: 0, high: 1, medium: 2, low: 3 };

export function JobsPage() {
  const data = useData();
  const views = useJobViews();
  const { openForm, openDetail } = useUI();
  const coarse = useMediaQuery("(pointer: coarse)");
  const [view, setView] = React.useState<"board" | "list">("board");
  const [filter, setFilter] = React.useState<JobFilter>("all");
  const [query, setQuery] = React.useState("");
  const [clientId, setClientId] = React.useState("");
  const [sort, setSort] = React.useState<"due" | "priority" | "recent">("due");
  const [showArchived, setShowArchived] = React.useState(false);
  const [config, setConfig] = React.useState<"statuses" | "templates" | null>(null);

  React.useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const f = p.get("filtro") as JobFilter | null;
    if (f && f in FILTER_LABEL) setFilter(f);
    if (window.matchMedia("(max-width: 640px)").matches) setView("list");
  }, []);

  const filtered = views
    .filter((v) => (showArchived ? v.job.archived : !v.job.archived))
    .filter((v) => !clientId || v.job.clientId === clientId)
    .filter((v) => matches([v.job.title, v.client?.name, v.client?.company, v.job.description, ...v.job.tags], query))
    .filter((v) => {
      switch (filter) {
        case "pendientes":
          return v.isOpen;
        case "proximos":
          return v.isOpen && v.daysToDue !== null && v.daysToDue <= 3;
        case "atrasados":
          return v.isOverdue;
        case "terminados":
          return v.kind === "done" || v.kind === "delivered";
        case "cobro":
          return v.finance.balance > 0 && v.kind !== "cancelled";
        default:
          return true;
      }
    })
    .sort((a, b) => {
      if (sort === "priority") return PRIORITY_RANK[a.job.priority] - PRIORITY_RANK[b.job.priority];
      if (sort === "recent") return b.job.updatedAt.localeCompare(a.job.updatedAt);
      return (a.job.dueDate ?? "9999").localeCompare(b.job.dueDate ?? "9999");
    });

  return (
    <SectionPage
      section="clientes"
      title="Trabajos"
      description="Estado de producción y estado de cobro, por separado."
      actions={
        <>
          <Button variant="outline" size="icon" aria-label="Plantillas de trabajo" onClick={() => setConfig("templates")}>
            <FileStack />
          </Button>
          <Button variant="outline" size="icon" aria-label="Configurar estados" onClick={() => setConfig("statuses")}>
            <Settings2 />
          </Button>
          <Button onClick={() => openForm({ kind: "job" })}>
            <Plus /> Trabajo
          </Button>
        </>
      }
    >
      <div className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Segmented
            ariaLabel="Vista"
            value={view}
            onChange={setView}
            options={[
              { value: "board", label: "Tablero", icon: <Columns3 /> },
              { value: "list", label: "Lista", icon: <List /> },
            ]}
          />
          <div className="relative min-w-0 flex-1 basis-56">
            <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar trabajo o cliente" className="pl-9" aria-label="Buscar trabajos" />
          </div>
          <NativeSelect aria-label="Cliente" className="w-full sm:w-48" value={clientId} onChange={(e) => setClientId(e.target.value)}>
            <option value="">Todos los clientes</option>
            {data.clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </NativeSelect>
          <NativeSelect aria-label="Ordenar" className="w-full sm:w-44" value={sort} onChange={(e) => setSort(e.target.value as typeof sort)}>
            <option value="due">Por fecha límite</option>
            <option value="priority">Por prioridad</option>
            <option value="recent">Recientes</option>
          </NativeSelect>
        </div>
        <div className="no-scrollbar -mx-4 flex gap-1.5 overflow-x-auto px-4 sm:mx-0 sm:flex-wrap sm:px-0">
          {(Object.keys(FILTER_LABEL) as JobFilter[]).map((f) => (
            <Chip key={f} active={filter === f} onClick={() => setFilter(f)}>
              {FILTER_LABEL[f]}
            </Chip>
          ))}
          <Chip active={showArchived} onClick={() => setShowArchived((v) => !v)}>
            Archivados
          </Chip>
        </div>
      </div>

      {data.jobs.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Columns3 />}
            title="Tu tablero está vacío"
            description="Crea un trabajo con su cliente, precio, fecha de entrega y anticipo. La fecha aparecerá en tu agenda y el saldo en tus cobros."
            action={
              <Button onClick={() => openForm({ kind: "job" })}>
                <Plus /> Crear trabajo
              </Button>
            }
          />
        </Card>
      ) : view === "board" ? (
        <Board views={filtered} coarse={coarse} onOpen={(id) => openDetail({ type: "job", id })} />
      ) : (
        <JobList views={filtered} onOpen={(id) => openDetail({ type: "job", id })} />
      )}

      {config === "statuses" && <StatusesSheet onClose={() => setConfig(null)} />}
      {config === "templates" && <TemplatesSheet onClose={() => setConfig(null)} />}
    </SectionPage>
  );
}

// ── Board ────────────────────────────────────────────────────────────────────

function DraggableCard({ view, onOpen, coarse }: { view: JobView; onOpen: () => void; coarse: boolean }) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({ id: view.job.id, disabled: coarse });
  const data = useData();
  return (
    <div ref={setNodeRef} className={cn("relative", isDragging && "opacity-30")}>
      <JobCard
        view={view}
        onOpen={onOpen}
        dragHandle={
          coarse ? (
            <div className="border-t border-border px-3 py-2">
              <NativeSelect
                aria-label={`Mover ${view.job.title}`}
                value={view.job.statusId}
                onChange={(e) => runSave(() => setJobStatus(view.job.id, e.target.value))}
                className="[&_select]:h-8 [&_select]:text-xs"
              >
                {data.jobStatuses.map((s) => (
                  <option key={s.id} value={s.id}>
                    Mover a: {s.name}
                  </option>
                ))}
              </NativeSelect>
            </div>
          ) : (
            <button
              type="button"
              aria-label={`Arrastrar ${view.job.title}`}
              className="absolute top-2 right-1.5 flex size-7 cursor-grab items-center justify-center rounded-md text-subtle opacity-0 transition-opacity group-hover:opacity-100 hover:bg-accent focus-visible:opacity-100 active:cursor-grabbing"
              {...listeners}
              {...attributes}
            >
              <GripVertical className="size-4" />
            </button>
          )
        }
      />
    </div>
  );
}

function Column({ statusId, children, count, total, name, color }: { statusId: string; children: React.ReactNode; count: number; total: number; name: string; color: string }) {
  const { setNodeRef, isOver } = useDroppable({ id: statusId });
  const money = useMoney();
  return (
    <section
      ref={setNodeRef}
      aria-label={name}
      className={cn("flex w-[272px] shrink-0 snap-start flex-col rounded-xl bg-muted/60 p-2 transition-colors", isOver && "bg-brand-soft ring-2 ring-brand/40")}
    >
      <header className="flex items-center justify-between gap-2 px-1.5 pt-1 pb-2">
        <StatusBadge status={{ id: statusId, name, color, kind: "new", order: 0 }} />
        <span className="text-xs text-muted-foreground tabular">
          {count}
          {total > 0 ? ` · ${money(total, { compact: true })}` : ""}
        </span>
      </header>
      <div className="flex min-h-24 flex-1 flex-col gap-2">{children}</div>
    </section>
  );
}

function Board({ views, coarse, onOpen }: { views: JobView[]; coarse: boolean; onOpen: (id: string) => void }) {
  const data = useData();
  const sensors = useSensors(useSensor(MouseSensor, { activationConstraint: { distance: 6 } }), useSensor(KeyboardSensor));
  const [active, setActive] = React.useState<JobView | null>(null);
  const onStart = (e: DragStartEvent) => setActive(views.find((v) => v.job.id === e.active.id) ?? null);
  const onEnd = (e: DragEndEvent) => {
    setActive(null);
    const statusId = e.over?.id as string | undefined;
    const jobId = e.active.id as string;
    if (!statusId) return;
    const job = data.jobs.find((j) => j.id === jobId);
    if (job && job.statusId !== statusId) {
      const s = data.jobStatuses.find((x) => x.id === statusId);
      void runSave(() => setJobStatus(jobId, statusId), `Movido a ${s?.name}`);
    }
  };
  return (
    <DndContext sensors={sensors} onDragStart={onStart} onDragEnd={onEnd} onDragCancel={() => setActive(null)}>
      <div className="-mx-4 flex snap-x gap-3 overflow-x-auto px-4 pb-3 sm:mx-0 sm:px-0">
        {data.jobStatuses.map((s) => {
          const col = views.filter((v) => v.job.statusId === s.id);
          return (
            <Column key={s.id} statusId={s.id} name={s.name} color={s.color} count={col.length} total={col.reduce((sum, v) => sum + v.finance.balance, 0)}>
              {col.map((v) => (
                <DraggableCard key={v.job.id} view={v} coarse={coarse} onOpen={() => onOpen(v.job.id)} />
              ))}
              {col.length === 0 && <p className="rounded-lg border border-dashed border-border-strong/60 p-3 text-center text-xs text-subtle">{coarse ? "Sin trabajos" : "Arrastra trabajos aquí"}</p>}
            </Column>
          );
        })}
      </div>
      <DragOverlay dropAnimation={{ duration: 180, easing: "cubic-bezier(0.22,1,0.36,1)" }}>
        {active ? <JobCard view={active} onOpen={() => {}} className="rotate-[1.5deg] shadow-pop" /> : null}
      </DragOverlay>
    </DndContext>
  );
}

function JobList({ views, onOpen }: { views: JobView[]; onOpen: (id: string) => void }) {
  const data = useData();
  if (views.length === 0) return <Card><EmptyState compact title="Ningún trabajo coincide" description="Cambia los filtros o la búsqueda." /></Card>;
  return (
    <Card>
      <ul className="divide-y divide-border">
        {views.map((v) => (
          <li key={v.job.id} className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:gap-4">
            <button type="button" className="min-w-0 flex-1 text-left" onClick={() => onOpen(v.job.id)}>
              <span className="block truncate text-xs text-muted-foreground">{v.client?.name}</span>
              <span className="block truncate text-sm font-medium">{v.job.title}</span>
              <span className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1">
                <DueLabel view={v} />
                <PriorityFlag priority={v.job.priority} />
                {v.job.priority === "low" || v.job.priority === "medium" ? <span className="text-xs text-subtle">Prioridad {PRIORITY_LABEL[v.job.priority].toLowerCase()}</span> : null}
              </span>
            </button>
            <div className="flex items-center justify-between gap-3 sm:justify-end">
              <div className="flex flex-col items-start gap-1 sm:items-end">
                <PaymentBadge state={v.finance.state} />
                {v.finance.balance > 0 && v.kind !== "cancelled" && <Money amount={v.finance.balance} className="text-xs font-medium" />}
              </div>
              <NativeSelect aria-label={`Estado de ${v.job.title}`} className="w-44" value={v.job.statusId} onChange={(e) => runSave(() => setJobStatus(v.job.id, e.target.value), "Estado actualizado")}>
                {data.jobStatuses.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </NativeSelect>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}

// ── Configuration sheets ─────────────────────────────────────────────────────

const KIND_LABEL: Record<JobStatusKind, string> = {
  new: "Nuevo",
  todo: "Por iniciar",
  doing: "En proceso",
  review: "En revisión",
  done: "Terminado",
  delivered: "Entregado",
  cancelled: "Cancelado",
};

function StatusesSheet({ onClose }: { onClose: () => void }) {
  const data = useData();
  const { confirm } = useUI();
  const [open, setOpen] = React.useState(true);
  const [name, setName] = React.useState("");
  const [kind, setKind] = React.useState<JobStatusKind>("doing");
  const close = () => (setOpen(false), setTimeout(onClose, 180));
  const ids = data.jobStatuses.map((s) => s.id);
  const move = (i: number, d: -1 | 1) => {
    const next = [...ids];
    [next[i], next[i + d]] = [next[i + d], next[i]];
    void runSave(() => reorderJobStatuses(next));
  };
  return (
    <Sheet open={open} onOpenChange={(v) => !v && close()} title="Estados de producción" description="Personaliza las columnas del tablero. Cada estado indica qué significa (abierto, terminado, entregado…) para calcular pendientes.">
      <ul className="space-y-2">
        {data.jobStatuses.map((s, i) => (
          <li key={s.id} className="rounded-lg border border-border p-3">
            <div className="flex items-center gap-2">
              <Input aria-label="Nombre del estado" defaultValue={s.name} onBlur={(e) => e.target.value.trim() && e.target.value !== s.name && runSave(() => saveJobStatus({ ...s, name: e.target.value }), "Estado renombrado")} />
              <Button variant="ghost" size="icon-sm" aria-label="Subir" disabled={i === 0} onClick={() => move(i, -1)}>
                <ArrowUp />
              </Button>
              <Button variant="ghost" size="icon-sm" aria-label="Bajar" disabled={i === ids.length - 1} onClick={() => move(i, 1)}>
                <ArrowDown />
              </Button>
              <Button
                variant="destructive-ghost"
                size="icon-sm"
                aria-label="Eliminar estado"
                onClick={async () => {
                  if (await confirm({ title: `¿Eliminar el estado «${s.name}»?`, confirmLabel: "Eliminar", destructive: true })) void runSave(() => deleteJobStatus(s.id), "Estado eliminado");
                }}
              >
                <Trash2 />
              </Button>
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-3">
              <NativeSelect aria-label="Significado" className="w-40" value={s.kind} onChange={(e) => runSave(() => saveJobStatus({ ...s, kind: e.target.value as JobStatusKind }))}>
                {Object.entries(KIND_LABEL).map(([k, l]) => (
                  <option key={k} value={k}>
                    Cuenta como: {l}
                  </option>
                ))}
              </NativeSelect>
              <ColorPicker colors={PALETTE} value={s.color} onChange={(c) => runSave(() => saveJobStatus({ ...s, color: c }))} />
            </div>
          </li>
        ))}
      </ul>
      <form
        className="mt-4 space-y-2 rounded-lg bg-muted/60 p-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (!name.trim()) return;
          void runSave(() => saveJobStatus({ name, kind, color: "slate" }), "Estado agregado").then((ok) => ok && setName(""));
        }}
      >
        <p className="text-[13px] font-medium">Nuevo estado</p>
        <div className="flex gap-2">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ej. Esperando material" aria-label="Nombre del nuevo estado" />
          <NativeSelect aria-label="Significado" className="w-36 shrink-0" value={kind} onChange={(e) => setKind(e.target.value as JobStatusKind)}>
            {Object.entries(KIND_LABEL).map(([k, l]) => (
              <option key={k} value={k}>
                {l}
              </option>
            ))}
          </NativeSelect>
          <Button type="submit" size="icon" aria-label="Agregar estado">
            <Plus />
          </Button>
        </div>
      </form>
    </Sheet>
  );
}

function TemplatesSheet({ onClose }: { onClose: () => void }) {
  const data = useData();
  const money = useMoney();
  const { openForm } = useUI();
  const [open, setOpen] = React.useState(true);
  const [editing, setEditing] = React.useState<string | "new" | null>(null);
  const [form, setForm] = React.useState({ name: "", description: "", price: "", durationDays: "" });
  const close = () => (setOpen(false), setTimeout(onClose, 180));
  const edit = (id: string | "new") => {
    const t = id === "new" ? undefined : data.jobTemplates.find((x) => x.id === id);
    setForm({ name: t?.name ?? "", description: t?.description ?? "", price: t ? amountToText(t.price, data.settings.currency) : "", durationDays: t?.durationDays ? String(t.durationDays) : "" });
    setEditing(id);
  };
  return (
    <Sheet open={open} onOpenChange={(v) => !v && close()} title="Plantillas de trabajos" description="Trabajos frecuentes con su precio y duración. Úsalas al crear un trabajo.">
      {editing ? (
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            void runSave(
              () =>
                saveTemplate({
                  id: editing === "new" ? undefined : editing,
                  name: form.name,
                  description: form.description || undefined,
                  price: parseMoney(form.price) ?? 0,
                  durationDays: form.durationDays ? Number(form.durationDays) : null,
                  priority: "medium",
                }),
              "Plantilla guardada",
            ).then((ok) => ok && setEditing(null));
          }}
        >
          <Field label="Nombre" htmlFor="tp-name">
            <Input id="tp-name" autoFocus value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Ej. Reel para redes" />
          </Field>
          <Field label="Precio habitual" htmlFor="tp-price">
            <AmountInput id="tp-price" value={form.price} onChange={(v) => setForm({ ...form, price: v })} />
          </Field>
          <Field label="Días de entrega" htmlFor="tp-days" optional>
            <Input id="tp-days" type="number" min={0} inputMode="numeric" value={form.durationDays} onChange={(e) => setForm({ ...form, durationDays: e.target.value })} />
          </Field>
          <Field label="Descripción" htmlFor="tp-desc" optional>
            <Textarea id="tp-desc" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </Field>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setEditing(null)}>
              Cancelar
            </Button>
            <Button type="submit">Guardar plantilla</Button>
          </div>
        </form>
      ) : (
        <div className="space-y-3">
          {data.jobTemplates.length === 0 && <p className="text-[13px] text-muted-foreground">Aún no tienes plantillas.</p>}
          <ul className="space-y-2">
            {data.jobTemplates.map((t) => (
              <li key={t.id} className="flex items-center gap-2 rounded-lg border border-border p-3">
                <button type="button" className="min-w-0 flex-1 text-left" onClick={() => edit(t.id)}>
                  <span className="block truncate text-sm font-medium">{t.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {money(t.price)}
                    {t.durationDays ? ` · ${t.durationDays} días` : ""}
                  </span>
                </button>
                <Button size="sm" variant="outline" onClick={() => { close(); setTimeout(() => openForm({ kind: "job" }), 220); }}>
                  Usar
                </Button>
                <Button variant="destructive-ghost" size="icon-sm" aria-label="Eliminar plantilla" onClick={() => runSave(() => deleteTemplate(t.id), "Plantilla eliminada")}>
                  <Trash2 />
                </Button>
              </li>
            ))}
          </ul>
          <Button variant="outline" onClick={() => edit("new")}>
            <Plus /> Nueva plantilla
          </Button>
        </div>
      )}
    </Sheet>
  );
}

