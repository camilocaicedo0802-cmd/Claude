"use client";

import * as React from "react";
import { ClipboardPaste, Info } from "lucide-react";
import { toast } from "sonner";
import { useData, useToday } from "@/hooks/data";
import { categoryFor, parseTaskImport, PRIORITY_COLOR, PRIORITY_NAME, STAGE_COLOR, STAGE_LABEL } from "@/domain/tasks";
import { formatDateNumeric } from "@/lib/dates";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/form-controls";
import { Sheet } from "@/components/ui/overlays";
import { DynamicIcon, ICON_CHOICES, toneStyle } from "@/components/shared/primitives";
import { errorMessage } from "@/services/common";
import { importTasks } from "@/services/life-service";
import { TonePill } from "@/components/shared/tone-pill";

export function ImportSheet({ initialText = "", onClose }: { initialText?: string; onClose: () => void }) {
  const data = useData();
  const today = useToday();
  const [open, setOpen] = React.useState(true);
  const [text, setText] = React.useState(initialText);
  const [busy, setBusy] = React.useState(false);
  const close = () => {
    setOpen(false);
    setTimeout(onClose, 180);
  };
  const parsed = React.useMemo(() => parseTaskImport(text, data.settings.taskCategories, ICON_CHOICES, today), [text, data.settings.taskCategories, today]);
  const allCategories = [...data.settings.taskCategories, ...parsed.newCategories];

  const paste = async () => {
    try {
      const clip = await navigator.clipboard.readText();
      if (clip.trim()) setText(clip);
      else toast.info("El portapapeles está vacío");
    } catch {
      toast.info("Tu navegador no permite leer el portapapeles: mantén pulsado el cuadro de texto y elige «Pegar».");
    }
  };

  const submit = async () => {
    if (parsed.rows.length === 0) return;
    setBusy(true);
    try {
      const { created, skipped } = await importTasks(parsed.rows, parsed.newCategories);
      toast.success(
        created === 0 ? "Esas tareas ya estaban en tu lista" : `${created} ${created === 1 ? "tarea agregada" : "tareas agregadas"}${skipped ? ` · ${skipped} ya existían` : ""}`,
      );
      close();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Sheet
      open={open}
      onOpenChange={(v) => !v && close()}
      title="Importar tareas"
      description="Pega filas copiadas de Notion, Excel o Google Sheets, o escribe una tarea por línea."
      wide
      footer={
        <>
          <Button variant="ghost" onClick={close} className="max-sm:hidden">
            Cancelar
          </Button>
          <Button size="lg" className="max-sm:flex-1 sm:h-9 sm:px-4 sm:text-sm" disabled={busy || parsed.rows.length === 0} onClick={submit}>
            {parsed.rows.length ? `Agregar ${parsed.rows.length} ${parsed.rows.length === 1 ? "tarea" : "tareas"}` : "Agregar"}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" size="sm" onClick={paste}>
            <ClipboardPaste /> Pegar del portapapeles
          </Button>
          {text && (
            <Button variant="ghost" size="sm" onClick={() => setText("")}>
              Limpiar
            </Button>
          )}
        </div>
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          aria-label="Tareas a importar"
          placeholder={"Sin empezar\tVideos ALI\tAlta\tTrabajo\t5\t11/11/2026\nEn curso\tActualizar portafolio\tMedia\tProyecto personal\t3\t20/11/2026"}
          className="font-mono text-xs leading-relaxed"
        />
        <p className="flex gap-2 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" />
          Columnas en este orden (o con encabezados en cualquier orden): Estado, Tarea, Prioridad, Categoría, Puntos, Fecha. Separadas por tabulación, punto y coma o coma. Si pegas la misma lista dos veces, no se duplica.
        </p>

        {parsed.rows.length > 0 && (
          <div>
            <p className="mb-2 text-[13px] font-semibold">
              Vista previa · {parsed.rows.length} {parsed.rows.length === 1 ? "tarea" : "tareas"}
              {parsed.newCategories.length > 0 && <span className="font-normal text-muted-foreground"> · categorías nuevas: {parsed.newCategories.map((c) => c.name).join(", ")}</span>}
            </p>
            <ul className="divide-y divide-border rounded-lg border border-border">
              {parsed.rows.map((r) => {
                const cat = categoryFor(r.category, allCategories);
                return (
                  <li key={r.line} className="space-y-1.5 px-3 py-2.5">
                    <div className="flex items-center gap-2">
                      <span style={toneStyle(cat?.color ?? "slate")} className="flex size-5 shrink-0 items-center justify-center rounded tone-soft [&_svg]:size-3.5">
                        <DynamicIcon name={r.icon ?? "list-checks"} />
                      </span>
                      <span className="min-w-0 truncate text-sm font-medium">{r.title}</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5 pl-7 text-xs text-muted-foreground">
                      <TonePill color={STAGE_COLOR[r.stage]}>{STAGE_LABEL[r.stage]}</TonePill>
                      {r.priority > 0 && (
                        <TonePill color={PRIORITY_COLOR[r.priority]} dot={false}>
                          {PRIORITY_NAME[r.priority]}
                        </TonePill>
                      )}
                      {cat && (
                        <TonePill color={cat.color} dot={false}>
                          {cat.name}
                        </TonePill>
                      )}
                      {r.points !== null && <span className="tabular">{r.points} pts</span>}
                      <span className="tabular">{r.date ? formatDateNumeric(r.date) : "Sin fecha"}</span>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
        {parsed.skipped.length > 0 && (
          <p className="text-xs text-warning">
            {parsed.skipped.length} {parsed.skipped.length === 1 ? "línea ignorada" : "líneas ignoradas"} (sin nombre de tarea): {parsed.skipped.map((s) => s.line).join(", ")}.
          </p>
        )}
      </div>
    </Sheet>
  );
}
