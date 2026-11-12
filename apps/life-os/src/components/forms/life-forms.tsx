"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Copy, Plus, Trash2, X } from "lucide-react";
import { useData, useToday } from "@/hooks/data";
import { createEvent, createHabit, createTask, deleteEvent, deleteHabit, deleteTask, duplicateTask, setTaskStage, updateEvent, updateHabit, updateTask } from "@/services/life-service";
import { STAGE_LABEL, STAGES, taskStage, type TaskStage } from "@/domain/tasks";
import type { EventCategory, FollowUpType, LifeArea, Subtask, TaskPriority } from "@/db/types";
import { EVENT_CATEGORY_LABEL } from "@/domain/agenda";
import { formatDateLong } from "@/lib/dates";
import { PRESET_LABELS, presetToRecurrence, recurrenceToPreset, type RecurrencePreset } from "@/lib/recurrence";
import { uid } from "@/lib/utils";
import { Field, Input, NativeSelect, SwitchRow, Textarea, Checkbox } from "@/components/ui/form-controls";
import { Segmented } from "@/components/ui/misc";
import { Button } from "@/components/ui/button";
import { ColorPicker, DateField, IconPicker, WeekdayPicker } from "@/components/shared/inputs";
import { PALETTE } from "@/components/shared/primitives";
import { useUI } from "@/components/shell/ui-context";
import { Disclosure, FormSheet, runSave, useBusy } from "./form-kit";

const TASK_ICONS = ["clapperboard", "video", "film", "camera", "brush", "image", "laptop", "monitor", "files", "file-text", "folder", "globe", "briefcase", "send", "banknote", "book-open", "lightbulb", "home", "shopping-cart", "dumbbell", "heart", "star", "target", "wrench"];

function useClosable(onDone: () => void) {
  const [open, setOpen] = React.useState(true);
  return { open, close: () => (setOpen(false), setTimeout(onDone, 180)) };
}

export const FOLLOWUP_LABEL: Record<FollowUpType, string> = {
  collect: "Cobrar saldo pendiente",
  proposal: "Enviar propuesta",
  info: "Solicitar información",
  deliver: "Entregar proyecto",
  contact: "Contactar cliente",
  review: "Revisar correcciones",
};

export const TASK_PRIORITY_LABEL: Record<TaskPriority, string> = { 0: "Sin prioridad", 1: "Baja", 2: "Media", 3: "Alta" };

const DURATIONS = [15, 30, 45, 60, 90, 120, 180, 240];

// ── Task ─────────────────────────────────────────────────────────────────────

const taskSchema = z.object({
  title: z.string().trim().min(1, "Escribe la tarea"),
  date: z.string().nullable(),
  time: z.string().optional(),
  durationMin: z.string().optional(),
  priority: z.number(),
  stage: z.enum(["not_started", "in_progress", "done"]),
  points: z.string().refine((v) => v.trim() === "" || (Number.isFinite(Number(v)) && Number(v) >= 0), "Usa un número"),
  icon: z.string(),
  area: z.string().optional(),
  preset: z.string(),
  days: z.array(z.number()),
  clientId: z.string().optional(),
  jobId: z.string().optional(),
  followUp: z.string().optional(),
  description: z.string().optional(),
  notes: z.string().optional(),
});

export function TaskForm({ id, defaults, onDone }: { id?: string; defaults?: Partial<import("@/db/types").Task>; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.tasks.find((t) => t.id === id) : undefined;
  const src = existing ?? defaults;
  const [subtasks, setSubtasks] = React.useState<Subtask[]>(existing?.subtasks ?? []);
  const [newSub, setNewSub] = React.useState("");
  const form = useForm<z.infer<typeof taskSchema>>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: src?.title ?? "",
      date: src?.date === undefined ? today : src.date,
      time: src?.time ?? "",
      durationMin: src?.durationMin ? String(src.durationMin) : "",
      priority: src?.priority ?? 0,
      area: src?.area ?? (src?.clientId ? "clientes" : ""),
      stage: src?.status ? taskStage({ status: src.status, inProgress: src.inProgress }) : "not_started",
      points: src?.points != null ? String(src.points) : "",
      icon: src?.icon ?? "",
      preset: recurrenceToPreset(src?.recurrence),
      days: src?.recurrence?.byWeekday ?? [1, 2, 3, 4, 5],
      clientId: src?.clientId ?? "",
      jobId: src?.jobId ?? "",
      followUp: src?.followUp ?? "",
      description: src?.description ?? "",
      notes: src?.notes ?? "",
    },
  });
  const { register, watch, setValue, handleSubmit, formState } = form;
  const preset = watch("preset") as RecurrencePreset;
  const clientId = watch("clientId");

  const submit = handleSubmit((v) =>
    wrap(async () => {
      const recurrence = presetToRecurrence(v.preset as RecurrencePreset, v.days);
      if (recurrence && !v.date) {
        form.setError("date", { message: "Una tarea que se repite necesita fecha de inicio" });
        return;
      }
      const payload = {
        title: v.title,
        date: v.date,
        time: v.time || null,
        durationMin: v.durationMin ? Number(v.durationMin) : null,
        priority: v.priority as TaskPriority,
        area: (v.area || null) as LifeArea | null,
        points: v.points.trim() === "" ? null : Math.round(Number(v.points)),
        icon: v.icon || null,
        recurrence,
        clientId: v.clientId || null,
        jobId: v.jobId || null,
        followUp: (v.followUp || null) as FollowUpType | null,
        description: v.description?.trim() || undefined,
        notes: v.notes?.trim() || undefined,
        subtasks,
      };
      const stage = v.stage as TaskStage;
      if (existing) {
        const ok = await runSave(async () => {
          await updateTask(existing.id, payload);
          if (stage !== taskStage(existing)) await setTaskStage(existing.id, stage);
        }, "Tarea actualizada");
        if (ok) close();
      } else if (
        await runSave(
          () =>
            createTask({
              ...payload,
              inProgress: stage === "in_progress",
              status: stage === "done" ? "done" : "todo",
              completedAt: stage === "done" ? new Date().toISOString() : null,
            }),
          "Tarea creada",
        )
      )
        close();
    }),
  );

  const jobs = data.jobs.filter((j) => !j.archived && (!clientId || j.clientId === clientId));

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar tarea" : "Nueva tarea"}
      formId="task-form"
      busy={busy}
      extraActions={
        existing && (
          <>
            <Button
              variant="destructive-ghost"
              size="icon-sm"
              aria-label="Eliminar tarea"
              onClick={async () => {
                if (await confirm({ title: "¿Eliminar esta tarea?", confirmLabel: "Eliminar", destructive: true })) {
                  if (await runSave(() => deleteTask(existing.id), "Tarea eliminada")) close();
                }
              }}
            >
              <Trash2 />
            </Button>
            <Button variant="ghost" size="icon-sm" aria-label="Duplicar tarea" onClick={() => runSave(() => duplicateTask(existing.id), "Tarea duplicada").then((ok) => ok && close())}>
              <Copy />
            </Button>
          </>
        )
      }
    >
      <form id="task-form" onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Tarea" htmlFor="task-title" error={formState.errors.title?.message}>
          <Input id="task-title" autoFocus={!existing} autoComplete="off" placeholder="¿Qué tienes que hacer?" {...register("title")} />
        </Field>
        <Field label="Estado">
          <Segmented
            className="w-full"
            size="sm"
            value={watch("stage")}
            onChange={(st) => setValue("stage", st)}
            options={STAGES.map((st) => ({ value: st, label: STAGE_LABEL[st] }))}
          />
        </Field>
        <Field label="Fecha" error={formState.errors.date?.message}>
          <DateField value={watch("date")} onChange={(v) => setValue("date", v)} quick={["today", "tomorrow", "weekend", "nextweek"]} allowEmpty emptyLabel="Algún día" />
        </Field>
        <Field label="Prioridad">
          <Segmented
            className="w-full"
            size="sm"
            value={String(watch("priority"))}
            onChange={(p) => setValue("priority", Number(p))}
            options={[0, 1, 2, 3].map((p) => ({ value: String(p), label: p === 0 ? "Ninguna" : TASK_PRIORITY_LABEL[p as TaskPriority] }))}
          />
        </Field>
        <div className="grid grid-cols-[1fr_6.5rem] gap-4">
          <Field label="Categoría" htmlFor="task-area">
            <NativeSelect id="task-area" {...register("area")}>
              <option value="">Sin categoría</option>
              {data.settings.taskCategories.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.name}
                </option>
              ))}
              {src?.area && !data.settings.taskCategories.some((c) => c.key === src.area) && <option value={src.area}>{src.area}</option>}
            </NativeSelect>
          </Field>
          <Field label="Puntos" htmlFor="task-points" error={formState.errors.points?.message}>
            <Input id="task-points" type="number" min={0} inputMode="numeric" placeholder="—" {...register("points")} />
          </Field>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Hora" htmlFor="task-time" optional hint={watch("time") ? "Aparecerá en el calendario." : undefined}>
            <Input id="task-time" type="time" {...register("time")} />
          </Field>
          <Field label="Duración" htmlFor="task-dur" optional>
            <NativeSelect id="task-dur" {...register("durationMin")}>
              <option value="">Sin estimar</option>
              {DURATIONS.map((d) => (
                <option key={d} value={d}>
                  {d < 60 ? `${d} min` : `${d / 60} h`}
                </option>
              ))}
            </NativeSelect>
          </Field>
        </div>
        <Disclosure label="Repetición, icono, cliente y subtareas" defaultOpen={!!(existing?.recurrence || existing?.clientId || existing?.subtasks.length || defaults?.clientId)}>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Repetir" htmlFor="task-rep">
              <NativeSelect id="task-rep" {...register("preset")}>
                {(["none", "daily", "weekdays", "weekly", "biweekly", "monthly", "custom-days"] as RecurrencePreset[]).map((p) => (
                  <option key={p} value={p}>
                    {PRESET_LABELS[p]}
                  </option>
                ))}
              </NativeSelect>
            </Field>
          </div>
          <Field label="Icono" optional>
            <IconPicker icons={TASK_ICONS} value={watch("icon")} onChange={(i) => setValue("icon", watch("icon") === i ? "" : i)} color={data.settings.taskCategories.find((c) => c.key === watch("area"))?.color ?? "slate"} />
          </Field>
          {preset === "custom-days" && <WeekdayPicker value={watch("days")} onChange={(d) => setValue("days", d)} weekStartsOn={data.settings.weekStartsOn} />}
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Cliente" htmlFor="task-client" optional>
              <NativeSelect
                id="task-client"
                value={clientId}
                onChange={(e) => {
                  setValue("clientId", e.target.value);
                  setValue("jobId", "");
                  if (e.target.value && !watch("area")) setValue("area", "clientes");
                }}
              >
                <option value="">Ninguno</option>
                {data.clients
                  .filter((c) => !c.archived)
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
              </NativeSelect>
            </Field>
            <Field label="Trabajo" htmlFor="task-job" optional>
              <NativeSelect id="task-job" {...register("jobId")}>
                <option value="">Ninguno</option>
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title}
                  </option>
                ))}
              </NativeSelect>
            </Field>
          </div>
          {clientId && (
            <Field label="Tipo de seguimiento" htmlFor="task-fu" optional>
              <NativeSelect id="task-fu" {...register("followUp")}>
                <option value="">No es un seguimiento</option>
                {Object.entries(FOLLOWUP_LABEL).map(([k, l]) => (
                  <option key={k} value={k}>
                    {l}
                  </option>
                ))}
              </NativeSelect>
            </Field>
          )}
          <Field label="Subtareas" optional>
            <ul className="space-y-1.5">
              {subtasks.map((s) => (
                <li key={s.id} className="flex items-center gap-2">
                  <Checkbox checked={s.done} onCheckedChange={() => setSubtasks((list) => list.map((x) => (x.id === s.id ? { ...x, done: !x.done } : x)))} aria-label={s.title} />
                  <span className={s.done ? "flex-1 text-sm text-muted-foreground line-through" : "flex-1 text-sm"}>{s.title}</span>
                  <Button variant="ghost" size="icon-sm" aria-label="Quitar subtarea" onClick={() => setSubtasks((list) => list.filter((x) => x.id !== s.id))}>
                    <X />
                  </Button>
                </li>
              ))}
            </ul>
            <div className="flex gap-2">
              <Input
                value={newSub}
                onChange={(e) => setNewSub(e.target.value)}
                placeholder="Añadir subtarea"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    if (newSub.trim()) {
                      setSubtasks((l) => [...l, { id: uid(), title: newSub.trim(), done: false }]);
                      setNewSub("");
                    }
                  }
                }}
              />
              <Button
                variant="outline"
                size="icon"
                aria-label="Añadir subtarea"
                onClick={() => {
                  if (!newSub.trim()) return;
                  setSubtasks((l) => [...l, { id: uid(), title: newSub.trim(), done: false }]);
                  setNewSub("");
                }}
              >
                <Plus />
              </Button>
            </div>
          </Field>
          <Field label="Descripción" htmlFor="task-desc" optional>
            <Textarea id="task-desc" rows={2} {...register("description")} />
          </Field>
          <Field label="Notas" htmlFor="task-notes" optional>
            <Textarea id="task-notes" rows={2} {...register("notes")} />
          </Field>
        </Disclosure>
      </form>
    </FormSheet>
  );
}

// ── Event ────────────────────────────────────────────────────────────────────

export function EventForm({
  id,
  occurrence,
  defaults,
  onDone,
}: {
  id?: string;
  occurrence?: string;
  defaults?: Partial<import("@/db/types").CalendarEvent>;
  onDone: () => void;
}) {
  const data = useData();
  const today = useToday();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.events.find((e) => e.id === id) : undefined;
  const src = existing ?? defaults;
  const [title, setTitle] = React.useState(src?.title ?? "");
  const [date, setDate] = React.useState<string>(existing?.recurrence && occurrence ? existing.date : src?.date ?? today);
  const [allDay, setAllDay] = React.useState<boolean>(src?.allDay ?? false);
  const [startTime, setStart] = React.useState(src?.startTime ?? "09:00");
  const [endTime, setEnd] = React.useState(src?.endTime ?? "10:00");
  const [category, setCategory] = React.useState<EventCategory>(src?.category ?? "personal");
  const [preset, setPreset] = React.useState<RecurrencePreset>(recurrenceToPreset(src?.recurrence));
  const [days, setDays] = React.useState<number[]>(src?.recurrence?.byWeekday ?? [1, 3, 5]);
  const [location, setLocation] = React.useState(src?.location ?? "");
  const [clientId, setClientId] = React.useState(src?.clientId ?? "");
  const [notes, setNotes] = React.useState(src?.notes ?? "");
  const [error, setError] = React.useState<string | null>(null);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return setError("Escribe el título del evento");
    if (!allDay && endTime && startTime && endTime <= startTime) return setError("La hora de fin debe ser posterior al inicio");
    setError(null);
    void wrap(async () => {
      const payload = {
        title,
        date,
        allDay,
        startTime: allDay ? null : startTime,
        endTime: allDay ? null : endTime || null,
        category,
        recurrence: presetToRecurrence(preset, days),
        location: location.trim() || undefined,
        clientId: clientId || null,
        jobId: src?.jobId ?? null,
        notes: notes.trim() || undefined,
      };
      if (existing) {
        if (await runSave(() => updateEvent(existing.id, payload), "Evento actualizado")) close();
      } else if (await runSave(() => createEvent(payload), "Evento agendado")) close();
    });
  };

  const remove = async () => {
    if (!existing) return;
    if (existing.recurrence && occurrence) {
      const ok = await confirm({
        title: "¿Eliminar solo esta fecha?",
        description: `Se quitará la ocurrencia del ${formatDateLong(occurrence)}. Para borrar toda la serie usa «Eliminar serie».`,
        confirmLabel: "Eliminar esta fecha",
        destructive: true,
      });
      if (ok && (await runSave(() => deleteEvent(existing.id, occurrence), "Fecha eliminada de la serie"))) close();
      return;
    }
    if (await confirm({ title: "¿Eliminar este evento?", confirmLabel: "Eliminar", destructive: true })) {
      if (await runSave(() => deleteEvent(existing.id), "Evento eliminado")) close();
    }
  };

  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar evento" : "Agendar evento"}
      description={existing?.recurrence ? "Los cambios se aplican a toda la serie." : undefined}
      formId="event-form"
      busy={busy}
      extraActions={
        existing && (
          <>
            <Button variant="destructive-ghost" size="sm" onClick={remove}>
              <Trash2 /> {existing.recurrence && occurrence ? "Esta fecha" : "Eliminar"}
            </Button>
            {existing.recurrence && (
              <Button
                variant="ghost"
                size="sm"
                onClick={async () => {
                  if (await confirm({ title: "¿Eliminar toda la serie?", confirmLabel: "Eliminar serie", destructive: true })) {
                    if (await runSave(() => deleteEvent(existing.id), "Serie eliminada")) close();
                  }
                }}
              >
                Eliminar serie
              </Button>
            )}
          </>
        )
      }
    >
      <form id="event-form" onSubmit={submit} className="space-y-4" noValidate>
        {error && <p role="alert" className="text-[13px] text-destructive">{error}</p>}
        <Field label="Título" htmlFor="ev-title">
          <Input id="ev-title" autoFocus={!existing} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ej. Reunión con cliente" />
        </Field>
        <Field label="Fecha">
          <DateField value={date} onChange={(v) => setDate(v ?? today)} quick={["today", "tomorrow"]} />
        </Field>
        <SwitchRow id="ev-allday" label="Todo el día" checked={allDay} onCheckedChange={setAllDay} />
        {!allDay && (
          <div className="grid grid-cols-2 gap-4">
            <Field label="Inicio" htmlFor="ev-start">
              <Input id="ev-start" type="time" value={startTime} onChange={(e) => setStart(e.target.value)} />
            </Field>
            <Field label="Fin" htmlFor="ev-end">
              <Input id="ev-end" type="time" value={endTime} onChange={(e) => setEnd(e.target.value)} />
            </Field>
          </div>
        )}
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Categoría" htmlFor="ev-cat">
            <NativeSelect id="ev-cat" value={category} onChange={(e) => setCategory(e.target.value as EventCategory)}>
              {Object.entries(EVENT_CATEGORY_LABEL).map(([k, l]) => (
                <option key={k} value={k}>
                  {l}
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Repetir" htmlFor="ev-rep">
            <NativeSelect id="ev-rep" value={preset} onChange={(e) => setPreset(e.target.value as RecurrencePreset)}>
              {(["none", "daily", "weekdays", "weekly", "biweekly", "monthly", "yearly", "custom-days"] as RecurrencePreset[]).map((p) => (
                <option key={p} value={p}>
                  {PRESET_LABELS[p]}
                </option>
              ))}
            </NativeSelect>
          </Field>
        </div>
        {preset === "custom-days" && <WeekdayPicker value={days} onChange={setDays} weekStartsOn={data.settings.weekStartsOn} />}
        <Disclosure label="Lugar, cliente y notas" defaultOpen={!!(src?.location || src?.clientId || src?.notes)}>
          <Field label="Lugar" htmlFor="ev-loc" optional>
            <Input id="ev-loc" value={location} onChange={(e) => setLocation(e.target.value)} />
          </Field>
          <Field label="Cliente" htmlFor="ev-client" optional>
            <NativeSelect id="ev-client" value={clientId ?? ""} onChange={(e) => setClientId(e.target.value)}>
              <option value="">Ninguno</option>
              {data.clients
                .filter((c) => !c.archived)
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
            </NativeSelect>
          </Field>
          <Field label="Notas" htmlFor="ev-notes" optional>
            <Textarea id="ev-notes" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </Field>
        </Disclosure>
      </form>
    </FormSheet>
  );
}

// ── Habit ────────────────────────────────────────────────────────────────────

const HABIT_ICONS = ["dumbbell", "book-open", "glass-water", "list-checks", "bed", "piggy-bank", "brain", "pen", "languages", "bike", "apple", "leaf", "moon", "sun", "heart", "pill", "coffee", "music", "droplet", "target", "flame", "mountain", "sparkles", "star"];

export function HabitForm({ id, onDone }: { id?: string; onDone: () => void }) {
  const data = useData();
  const today = useToday();
  const { confirm } = useUI();
  const { open, close } = useClosable(onDone);
  const [busy, wrap] = useBusy();
  const existing = id ? data.habits.find((h) => h.id === id) : undefined;
  const [name, setName] = React.useState(existing?.name ?? "");
  const [icon, setIcon] = React.useState(existing?.icon ?? "sparkles");
  const [color, setColor] = React.useState(existing?.color ?? "iris");
  const [mode, setMode] = React.useState<"daily" | "days">(existing?.schedule.type ?? "daily");
  const [days, setDays] = React.useState<number[]>(existing?.schedule.type === "days" ? existing.schedule.days : [1, 2, 3, 4, 5]);
  const [target, setTarget] = React.useState(String(existing?.target ?? 1));
  const [unit, setUnit] = React.useState(existing?.unit ?? "");
  const [error, setError] = React.useState<string | null>(null);
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return setError("Ponle un nombre al hábito");
    if (mode === "days" && days.length === 0) return setError("Elige al menos un día");
    setError(null);
    void wrap(async () => {
      const payload = {
        name,
        icon,
        color,
        schedule: mode === "daily" ? ({ type: "daily" } as const) : ({ type: "days", days } as const),
        target: Math.max(1, Math.min(50, Number(target) || 1)),
        unit: unit.trim() || undefined,
        startDate: existing?.startDate ?? today,
      };
      if (existing) {
        if (await runSave(() => updateHabit(existing.id, payload), "Hábito actualizado")) close();
      } else if (await runSave(() => createHabit(payload), "Hábito creado")) close();
    });
  };
  return (
    <FormSheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title={existing ? "Editar hábito" : "Nuevo hábito"}
      formId="habit-form"
      busy={busy}
      extraActions={
        existing && (
          <>
            <Button variant="ghost" size="sm" onClick={() => runSave(() => updateHabit(existing.id, { archived: !existing.archived }), existing.archived ? "Hábito restaurado" : "Hábito archivado").then((ok) => ok && close())}>
              {existing.archived ? "Restaurar" : "Archivar"}
            </Button>
            <Button
              variant="destructive-ghost"
              size="icon-sm"
              aria-label="Eliminar hábito"
              onClick={async () => {
                if (await confirm({ title: `¿Eliminar «${existing.name}»?`, description: "Se borrará todo su historial. Si solo quieres pausarlo, archívalo.", confirmLabel: "Eliminar", destructive: true })) {
                  if (await runSave(() => deleteHabit(existing.id), "Hábito eliminado")) close();
                }
              }}
            >
              <Trash2 />
            </Button>
          </>
        )
      }
    >
      <form id="habit-form" onSubmit={submit} className="space-y-4" noValidate>
        {error && <p role="alert" className="text-[13px] text-destructive">{error}</p>}
        <Field label="Hábito" htmlFor="hb-name">
          <Input id="hb-name" autoFocus={!existing} value={name} onChange={(e) => setName(e.target.value)} placeholder="Ej. Leer 20 minutos" />
        </Field>
        <Field label="Frecuencia" hint="Las rachas solo cuentan los días programados: no se rompen en días de descanso.">
          <Segmented className="w-full" value={mode} onChange={setMode} options={[{ value: "daily", label: "Todos los días" }, { value: "days", label: "Días específicos" }]} />
        </Field>
        {mode === "days" && <WeekdayPicker value={days} onChange={setDays} weekStartsOn={data.settings.weekStartsOn} />}
        <div className="grid grid-cols-2 gap-4">
          <Field label="Meta diaria" htmlFor="hb-target" hint="Veces al día">
            <Input id="hb-target" type="number" min={1} max={50} inputMode="numeric" value={target} onChange={(e) => setTarget(e.target.value)} />
          </Field>
          <Field label="Unidad" htmlFor="hb-unit" optional>
            <Input id="hb-unit" value={unit} onChange={(e) => setUnit(e.target.value)} placeholder="vasos, páginas…" />
          </Field>
        </div>
        <Field label="Color">
          <ColorPicker colors={PALETTE} value={color} onChange={setColor} />
        </Field>
        <Field label="Icono">
          <IconPicker icons={HABIT_ICONS} value={icon} onChange={setIcon} color={color} />
        </Field>
      </form>
    </FormSheet>
  );
}
