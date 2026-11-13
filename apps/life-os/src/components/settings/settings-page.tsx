"use client";

import * as React from "react";
import Link from "next/link";
import { CircleCheck, CloudOff, Database, Download, FlaskConical, HardDrive, Keyboard, Moon, Plus, RotateCcw, Smartphone, Sun, SunMoon, Upload } from "lucide-react";
import { toast } from "sonner";
import { useData, useMoney } from "@/hooks/data";
import { readMode } from "@/db/db";
import type { HorizonMode, Settings, ThemePref } from "@/db/types";
import { CURRENCIES, parseMoney } from "@/lib/money";
import { downloadFile, cn } from "@/lib/utils";
import { formatDateLong, instantToDate, todayIn } from "@/lib/dates";
import { Button } from "@/components/ui/button";
import { Field, Input, NativeSelect, SwitchRow } from "@/components/ui/form-controls";
import { Kbd, Segmented } from "@/components/ui/misc";
import { Card, CardHeader, IconBadge, PageHeader } from "@/components/shared/primitives";
import { AmountInput, amountToText } from "@/components/shared/inputs";
import { useUI } from "@/components/shell/ui-context";
import { runSave } from "@/components/forms/form-kit";
import { InstallInstructions, lastBackupAt, markBackupDone, useInstall } from "@/components/shell/pwa";
import { NATURE_LABEL } from "@/components/forms/finance-forms";
import { errorMessage } from "@/services/common";
import { discardDemo, exportBackup, parseBackup, requestPersistentStorage, resetAllData, restoreBackup, switchMode, updateSettings } from "@/services/settings-service";

const TIME_ZONES = ["America/Bogota", "America/Mexico_City", "America/Lima", "America/Santiago", "America/Argentina/Buenos_Aires", "America/Caracas", "America/New_York", "America/Los_Angeles", "Europe/Madrid", "UTC"];

function save(patch: Partial<Settings>, msg = "Ajuste guardado") {
  return runSave(() => updateSettings(patch), msg);
}

export function SettingsPage() {
  const data = useData();
  const money = useMoney();
  const s = data.settings;
  const { openForm, confirm } = useUI();
  const [name, setName] = React.useState(s.userName);
  const [reserve, setReserve] = React.useState(amountToText(s.safetyReserve, s.currency));
  const [persisted, setPersisted] = React.useState<boolean | null>(null);
  const [usage, setUsage] = React.useState<string | null>(null);
  const fileRef = React.useRef<HTMLInputElement>(null);
  const demo = readMode() === "demo";
  const install = useInstall();
  const [lastBackup, setLastBackup] = React.useState<string | null>(null);
  React.useEffect(() => setLastBackup(lastBackupAt()), []);

  React.useEffect(() => {
    navigator.storage?.persisted?.().then(setPersisted).catch(() => setPersisted(null));
    navigator.storage?.estimate?.().then((e) => e.usage !== undefined && setUsage(`${(e.usage / 1024 / 1024).toFixed(1)} MB`)).catch(() => {});
  }, []);

  const exportJSON = async () => {
    try {
      const backup = await exportBackup();
      const filename = `lifeos-respaldo-${todayIn(s.timeZone)}.json`;
      const json = JSON.stringify(backup, null, 2);
      // On phones, the share sheet saves the file to Drive/Files or sends it by WhatsApp or email.
      const file = typeof File !== "undefined" ? new File([json], filename, { type: "application/json" }) : null;
      if (file && window.matchMedia("(pointer: coarse)").matches && navigator.canShare?.({ files: [file] })) {
        try {
          await navigator.share({ files: [file], title: "Respaldo de LIFE OS" });
        } catch (e) {
          if (e instanceof DOMException && e.name === "AbortError") return;
          downloadFile(filename, json, "application/json");
        }
      } else {
        downloadFile(filename, json, "application/json");
      }
      markBackupDone();
      setLastBackup(lastBackupAt());
      toast.success("Respaldo descargado. Guárdalo en Drive o envíatelo por correo.");
    } catch (e) {
      toast.error(errorMessage(e));
    }
  };

  const importJSON = async (file: File) => {
    try {
      const backup = parseBackup(await file.text());
      const counts = Object.entries(backup.tables).reduce((n, [, rows]) => n + (Array.isArray(rows) ? rows.length : 0), 0);
      const ok = await confirm({
        title: "¿Restaurar este respaldo?",
        description: `Se reemplazarán TODOS los datos actuales de ${demo ? "la demo" : "este dispositivo"} por los del archivo (${counts} registros, exportado el ${backup.exportedAt.slice(0, 10)}). Te recomendamos descargar primero un respaldo actual.`,
        confirmLabel: "Restaurar",
        destructive: true,
      });
      if (!ok) return;
      await restoreBackup(backup);
      toast.success("Respaldo restaurado");
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const expenseCats = data.categories.filter((c) => c.kind === "expense");
  const incomeCats = data.categories.filter((c) => c.kind === "income");

  return (
    <div className="mx-auto max-w-3xl space-y-5 lg:space-y-6">
      <PageHeader title="Ajustes" description="Preferencias, cálculo financiero, categorías y respaldo de tus datos." />

      <Card>
        <CardHeader title="Perfil y región" />
        <div className="grid gap-4 px-4 pb-5 sm:grid-cols-2 sm:px-5">
          <Field label="Tu nombre" htmlFor="st-name">
            <Input id="st-name" value={name} onChange={(e) => setName(e.target.value)} onBlur={() => name !== s.userName && save({ userName: name.trim() })} />
          </Field>
          <Field label="Moneda" htmlFor="st-cur" hint="Cambia el formato; no convierte valores ya registrados.">
            <NativeSelect id="st-cur" value={s.currency} onChange={(e) => save({ currency: e.target.value })}>
              {CURRENCIES.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.label} ({c.code})
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Zona horaria" htmlFor="st-tz" hint="Define qué es «hoy» en tu agenda y tus finanzas.">
            <NativeSelect id="st-tz" value={s.timeZone} onChange={(e) => save({ timeZone: e.target.value })}>
              {[...new Set([s.timeZone, ...TIME_ZONES])].map((z) => (
                <option key={z} value={z}>
                  {z.replace(/_/g, " ")}
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Primer día de la semana" htmlFor="st-week">
            <NativeSelect id="st-week" value={String(s.weekStartsOn)} onChange={(e) => save({ weekStartsOn: Number(e.target.value) as 0 | 1 })}>
              <option value="1">Lunes</option>
              <option value="0">Domingo</option>
            </NativeSelect>
          </Field>
          <p className="text-xs text-muted-foreground sm:col-span-2">Idioma: español · Formato de fecha: día/mes/año.</p>
        </div>
      </Card>

      <Card>
        <CardHeader title="Apariencia" />
        <div className="px-4 pb-5 sm:px-5">
          <Segmented<ThemePref>
            ariaLabel="Tema"
            value={s.theme}
            onChange={(t) => save({ theme: t }, t === "dark" ? "Modo oscuro" : t === "light" ? "Modo claro" : "Tema del sistema")}
            options={[
              { value: "system", label: "Sistema", icon: <SunMoon /> },
              { value: "light", label: "Claro", icon: <Sun /> },
              { value: "dark", label: "Oscuro", icon: <Moon /> },
            ]}
          />
        </div>
      </Card>

      <Card id="calculo" className="scroll-mt-20">
        <CardHeader title="Cálculo de «¿Cuánto puedo gastar?»" description="Recomendaciones conservadoras: nunca cuentan dinero que no tienes." />
        <div className="space-y-5 px-4 pb-5 sm:px-5">
          <Field label="Horizonte del cálculo">
            <Segmented<HorizonMode>
              className="w-full"
              size="sm"
              value={s.horizonMode}
              onChange={(m) => save({ horizonMode: m })}
              options={[
                { value: "nextIncome", label: "Próximo ingreso" },
                { value: "endOfMonth", label: "Fin de mes" },
                { value: "days", label: "Días fijos" },
              ]}
            />
          </Field>
          {s.horizonMode === "days" && (
            <Field label="Número de días" htmlFor="st-hdays">
              <Input id="st-hdays" type="number" min={1} max={120} inputMode="numeric" defaultValue={s.horizonDays} onBlur={(e) => save({ horizonDays: Math.max(1, Math.min(120, Number(e.target.value) || 30)) })} className="w-32" />
            </Field>
          )}
          {s.horizonMode === "nextIncome" && !data.plannedIncomes.some((p) => p.confirmed && p.active) && (
            <p className="rounded-lg bg-muted p-3 text-[13px] text-muted-foreground">
              No tienes ingresos confirmados registrados, así que se calcula hasta fin de mes.{" "}
              <button type="button" className="font-medium text-foreground underline underline-offset-2" onClick={() => openForm({ kind: "plannedIncome" })}>
                Registrar mi salario o ingreso fijo
              </button>
            </p>
          )}
          <Field label="Colchón de seguridad" htmlFor="st-reserve" hint="Dinero que nunca se considera disponible para gastar.">
            <AmountInput id="st-reserve" value={reserve} onChange={setReserve} className="max-w-60" />
          </Field>
          <Button variant="outline" size="sm" onClick={() => save({ safetyReserve: parseMoney(reserve) ?? 0 }, `Colchón: ${money(parseMoney(reserve) ?? 0)}`)}>
            Guardar colchón
          </Button>
          <Field label={`Porcentaje del margen sugerido para ocio: ${s.leisureShare} %`} htmlFor="st-leisure" hint="Solo se usa si no tienes presupuestos de ocio o compras personales.">
            <input id="st-leisure" type="range" min={0} max={60} step={5} defaultValue={s.leisureShare} onPointerUp={(e) => save({ leisureShare: Number((e.target as HTMLInputElement).value) })} onKeyUp={(e) => save({ leisureShare: Number((e.target as HTMLInputElement).value) })} className="w-full max-w-sm accent-[var(--brand)]" />
          </Field>
          <SwitchRow id="st-confirmed" label="Contar ingresos confirmados dentro del período" description="Apagado por defecto: lo más prudente es no gastar dinero que aún no llega." checked={s.includeConfirmedIncome} onCheckedChange={(v) => save({ includeConfirmedIncome: v })} />
          <SwitchRow id="st-goals" label="Reservar aportes a metas de ahorro" description="Aparta lo que deberías ahorrar al mes para llegar a tus metas con fecha." checked={s.reserveSavingsGoals} onCheckedChange={(v) => save({ reserveSavingsGoals: v })} />
        </div>
      </Card>

      <Card>
        <CardHeader title="Agenda" />
        <div className="px-4 pb-5 sm:px-5">
          <Field label="Horas disponibles por día" htmlFor="st-hours" hint="Para avisarte cuando planificas más de lo que cabe en tu día.">
            <Input id="st-hours" type="number" min={1} max={16} inputMode="numeric" defaultValue={s.availableHoursPerDay} onBlur={(e) => save({ availableHoursPerDay: Math.max(1, Math.min(16, Number(e.target.value) || 8)) })} className="w-32" />
          </Field>
        </div>
      </Card>

      <Card id="planificador" className="scroll-mt-20">
        <CardHeader title="Planificador y enfoque" description="Así arma el planificador tu día y así funciona el modo enfoque." />
        <div className="grid gap-4 px-4 pb-5 sm:grid-cols-2 sm:px-5">
          <Field label="Mi día empieza" htmlFor="pl-start">
            <Input id="pl-start" type="time" defaultValue={s.planner.dayStart} onBlur={(e) => e.target.value && save({ planner: { ...s.planner, dayStart: e.target.value } })} />
          </Field>
          <Field label="Mi día termina" htmlFor="pl-end">
            <Input id="pl-end" type="time" defaultValue={s.planner.dayEnd} onBlur={(e) => e.target.value && save({ planner: { ...s.planner, dayEnd: e.target.value } })} />
          </Field>
          <Field label="Máxima energía desde" htmlFor="pl-fs" hint="Auto-planificar pone aquí las tareas de prioridad alta.">
            <Input id="pl-fs" type="time" defaultValue={s.planner.focusStart} onBlur={(e) => e.target.value && save({ planner: { ...s.planner, focusStart: e.target.value } })} />
          </Field>
          <Field label="Máxima energía hasta" htmlFor="pl-fe">
            <Input id="pl-fe" type="time" defaultValue={s.planner.focusEnd} onBlur={(e) => e.target.value && save({ planner: { ...s.planner, focusEnd: e.target.value } })} />
          </Field>
          <Field label="Pausa entre bloques" htmlFor="pl-buffer">
            <NativeSelect id="pl-buffer" value={String(s.planner.bufferMin)} onChange={(e) => save({ planner: { ...s.planner, bufferMin: Number(e.target.value) } })}>
              {[0, 5, 10, 15, 20, 30].map((m) => (
                <option key={m} value={m}>
                  {m === 0 ? "Sin pausa" : `${m} min`}
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Duración por defecto de una tarea" htmlFor="pl-default" hint="Para tareas sin duración estimada.">
            <NativeSelect id="pl-default" value={String(s.planner.defaultTaskMin)} onChange={(e) => save({ planner: { ...s.planner, defaultTaskMin: Number(e.target.value) } })}>
              {[15, 30, 45, 60, 90, 120].map((m) => (
                <option key={m} value={m}>
                  {m < 60 ? `${m} min` : `${m / 60} h`}
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Sesión de enfoque" htmlFor="pl-pomo">
            <NativeSelect id="pl-pomo" value={String(s.planner.pomodoroMin)} onChange={(e) => save({ planner: { ...s.planner, pomodoroMin: Number(e.target.value) } })}>
              {[15, 20, 25, 30, 45, 50, 60, 90].map((m) => (
                <option key={m} value={m}>
                  {m} min
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Descanso" htmlFor="pl-break">
            <NativeSelect id="pl-break" value={String(s.planner.breakMin)} onChange={(e) => save({ planner: { ...s.planner, breakMin: Number(e.target.value) } })}>
              {[3, 5, 10, 15, 20].map((m) => (
                <option key={m} value={m}>
                  {m} min
                </option>
              ))}
            </NativeSelect>
          </Field>
        </div>
      </Card>

      <Card>
        <CardHeader title="Notificaciones" description="Se muestran en la campana mientras usas la app. Los avisos push en segundo plano aún no están disponibles." />
        <div className="space-y-3 px-4 pb-5 sm:px-5">
          {(
            [
              ["obligations", "Pagos y obligaciones por vencer"],
              ["budgets", "Presupuestos cerca del límite"],
              ["jobs", "Entregas de trabajos próximas o atrasadas"],
              ["collections", "Cobros vencidos"],
              ["tasks", "Tareas atrasadas"],
            ] as const
          ).map(([key, label]) => (
            <SwitchRow key={key} id={`nt-${key}`} label={label} checked={s.notifications[key]} onCheckedChange={(v) => save({ notifications: { ...s.notifications, [key]: v } })} />
          ))}
          <Field label="Avisar de pagos con anticipación de" htmlFor="nt-lead">
            <NativeSelect id="nt-lead" className="w-40" value={String(s.notifications.obligationLeadDays)} onChange={(e) => save({ notifications: { ...s.notifications, obligationLeadDays: Number(e.target.value) } })}>
              {[1, 2, 3, 5, 7].map((d) => (
                <option key={d} value={d}>
                  {d} {d === 1 ? "día" : "días"}
                </option>
              ))}
            </NativeSelect>
          </Field>
        </div>
      </Card>

      <Card>
        <CardHeader
          title="Categorías"
          description="Toca una categoría para editarla o archivarla."
          action={
            <Button variant="ghost" size="sm" onClick={() => openForm({ kind: "category" })}>
              <Plus /> Nueva
            </Button>
          }
        />
        <div className="space-y-4 px-4 pb-5 sm:px-5">
          {[
            { label: "Gastos", list: expenseCats },
            { label: "Ingresos", list: incomeCats },
          ].map((g) => (
            <div key={g.label}>
              <p className="mb-2 text-xs font-semibold text-muted-foreground">{g.label}</p>
              <div className="grid gap-1.5 sm:grid-cols-2">
                {g.list.map((c) => (
                  <button key={c.id} type="button" onClick={() => openForm({ kind: "category", id: c.id })} className={cn("flex items-center gap-2.5 rounded-lg border border-border px-2.5 py-2 text-left hover:bg-accent", c.archived && "opacity-50")}>
                    <IconBadge icon={c.icon} color={c.color} size="sm" />
                    <span className="min-w-0 flex-1 truncate text-sm">{c.name}</span>
                    {c.nature && <span className="text-xs text-muted-foreground">{NATURE_LABEL[c.nature]}</span>}
                    {c.archived && <span className="text-xs text-muted-foreground">Archivada</span>}
                  </button>
                ))}
              </div>
            </div>
          ))}
          <p className="text-[13px] text-muted-foreground">
            Los límites por categoría se configuran en{" "}
            <Link href="/finanzas/presupuestos/" className="font-medium text-foreground underline underline-offset-2">
              Presupuestos
            </Link>
            .
          </p>
        </div>
      </Card>

      <Card>
        <CardHeader title="App en tu celular" icon={<Smartphone />} />
        <div className="space-y-3 px-4 pb-5 sm:px-5">
          {install.standalone ? (
            <p className="flex items-center gap-2 text-[13px]">
              <CircleCheck className="size-4 text-income" /> Estás usando la app instalada. Funciona sin conexión.
            </p>
          ) : install.canPrompt ? (
            <>
              <p className="text-[13px] text-muted-foreground">Instálala para abrirla desde tu pantalla de inicio, sin barra del navegador y sin conexión.</p>
              <Button variant="brand" onClick={() => install.prompt()}>
                <Download /> Instalar LIFE OS
              </Button>
            </>
          ) : (
            <InstallInstructions ios={install.ios} />
          )}
        </div>
      </Card>

      <Card id="datos" className="scroll-mt-20">
        <CardHeader title="Tus datos" icon={<Database />} />
        <div className="space-y-4 px-4 pb-5 sm:px-5">
          <div className="rounded-lg bg-muted/70 p-3 text-[13px]">
            <p className="flex items-center gap-2 font-medium">
              <HardDrive className="size-4" /> Guardados en este dispositivo (IndexedDB){usage ? ` · ${usage}` : ""}
            </p>
            <p className="mt-1 text-muted-foreground">
              No se envían a ningún servidor. {persisted === true ? "El navegador marcó el almacenamiento como persistente." : "Pide almacenamiento persistente para que el navegador no los borre si le falta espacio."}
            </p>
            {persisted !== true && (
              <Button
                size="sm"
                variant="outline"
                className="mt-2"
                onClick={async () => {
                  const r = await requestPersistentStorage();
                  setPersisted(r);
                  toast[r ? "success" : "info"](r ? "Almacenamiento persistente activado" : "El navegador no lo concedió; descarga respaldos con frecuencia.");
                }}
              >
                Pedir almacenamiento persistente
              </Button>
            )}
          </div>
          <div className="rounded-lg border border-dashed border-border p-3 text-[13px]">
            <p className="flex items-center gap-2 font-medium">
              <CloudOff className="size-4" /> Sincronización entre dispositivos: no disponible todavía
            </p>
            <p className="mt-1 text-muted-foreground">
              Tu celular y tu computador tienen bases separadas. Para llevar tus datos de uno a otro, descarga un respaldo y restáuralo en el otro dispositivo. La sincronización requiere un backend (por ejemplo, Supabase con autenticación y RLS) que aún no está configurado.
            </p>
          </div>
          <p className="text-[13px] text-muted-foreground">
            {lastBackup ? `Último respaldo descargado: ${formatDateLong(instantToDate(lastBackup, s.timeZone))}.` : "Aún no has descargado un respaldo en este dispositivo."} Si pierdes el celular o borras los datos del navegador, solo podrás recuperar lo que esté en un respaldo.
          </p>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={exportJSON}>
              <Download /> Descargar respaldo
            </Button>
            <Button variant="outline" onClick={() => fileRef.current?.click()}>
              <Upload /> Restaurar respaldo
            </Button>
            <Button variant="outline" asChild>
              <Link href="/finanzas/movimientos/">Exportar movimientos (CSV)</Link>
            </Button>
            <input ref={fileRef} type="file" accept="application/json,.json" className="hidden" onChange={(e) => e.target.files?.[0] && importJSON(e.target.files[0])} />
          </div>
          <div className="border-t border-border pt-4">
            {demo ? (
              <div className="flex flex-wrap gap-2">
                <Button onClick={() => switchMode("real")}>Volver a mis datos reales</Button>
                <Button variant="ghost" onClick={() => discardDemo()}>
                  Borrar la demo y salir
                </Button>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-2">
                <Button variant="outline" onClick={() => switchMode("demo").catch((e) => toast.error(errorMessage(e)))}>
                  <FlaskConical /> Explorar modo demo
                </Button>
                <span className="text-xs text-muted-foreground">Datos de ejemplo en un espacio separado; tus registros no se tocan.</span>
              </div>
            )}
          </div>
          <div className="border-t border-border pt-4">
            <Button
              variant="destructive-ghost"
              onClick={async () => {
                const ok = await confirm({
                  title: demo ? "¿Borrar todos los datos de la demo?" : "¿Borrar TODOS tus datos?",
                  description: "Se eliminarán cuentas, movimientos, clientes, tareas, hábitos y ajustes de este dispositivo. No se puede deshacer. Descarga un respaldo antes.",
                  confirmLabel: "Borrar todo",
                  destructive: true,
                });
                if (ok) await runSave(() => resetAllData(), "Datos borrados");
              }}
            >
              <RotateCcw /> Borrar todos los datos
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader title="Atajos de teclado" icon={<Keyboard />} />
        <dl className="grid gap-2 px-4 pb-5 text-[13px] sm:grid-cols-2 sm:px-5">
          {[
            [["⌘", "K"], "Buscar en todo"],
            [["/"], "Buscar"],
            [["N"], "Agregar rápido (gasto, tarea, cliente…)"],
            [["1–8"], "Elegir acción en el menú Agregar"],
            [["G", "F"], "Ir a Finanzas"],
            [["G", "C"], "Ir a Clientes"],
            [["G", "V"], "Ir a Mi Vida"],
            [["G", "A"], "Ir a Ajustes"],
          ].map(([keys, label]) => (
            <div key={label as string} className="flex items-center justify-between gap-3">
              <dt className="text-muted-foreground">{label as string}</dt>
              <dd className="flex gap-1">
                {(keys as string[]).map((k) => (
                  <Kbd key={k}>{k}</Kbd>
                ))}
              </dd>
            </div>
          ))}
        </dl>
      </Card>
    </div>
  );
}
