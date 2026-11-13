"use client";

import * as React from "react";
import { Dialog as DialogPrimitive } from "radix-ui";
import { CheckCheck, CircleStop, Coffee, Pause, Play, Plus, Timer, X, Zap } from "lucide-react";
import { toast } from "sonner";
import { useData, useToday } from "@/hooks/data";
import { formatDuration, instantToDate } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { recordFocusSession } from "@/services/planner-service";
import { setTaskDone } from "@/services/life-service";

const STORAGE_KEY = "lifeos:focus";

export interface FocusState {
  title: string;
  taskId?: string | null;
  mode: "focus" | "break";
  plannedMin: number;
  startedAt: number;
  pausedAt: number | null;
  pausedMs: number;
}

interface Finished {
  mode: "focus" | "break";
  title: string;
  taskId?: string | null;
  minutes: number;
}

interface FocusContextValue {
  state: FocusState | null;
  remainingMs: number;
  elapsedMs: number;
  viewOpen: boolean;
  setViewOpen: (v: boolean) => void;
  finished: Finished | null;
  start: (opts: { title: string; taskId?: string | null; minutes?: number; mode?: "focus" | "break" }) => void;
  pause: () => void;
  resume: () => void;
  addMinutes: (m: number) => void;
  stop: (opts?: { completeTask?: boolean }) => Promise<void>;
  dismissFinished: () => void;
}

const FocusContext = React.createContext<FocusContextValue | null>(null);

function load(): FocusState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as FocusState) : null;
  } catch {
    return null;
  }
}

function persist(s: FocusState | null) {
  try {
    if (s) localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* storage unavailable: the timer still runs for this session */
  }
}

function elapsedOf(s: FocusState, now = Date.now()) {
  return (s.pausedAt ?? now) - s.startedAt - s.pausedMs;
}

let audioCtx: AudioContext | null = null;
function prepareAudio() {
  try {
    const Ctx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    audioCtx ??= new Ctx();
    if (audioCtx.state === "suspended") void audioCtx.resume();
  } catch {
    audioCtx = null;
  }
}

function chime() {
  if (!audioCtx) return;
  const now = audioCtx.currentTime;
  [660, 880, 990].forEach((freq, i) => {
    const osc = audioCtx!.createOscillator();
    const gain = audioCtx!.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.0001, now + i * 0.18);
    gain.gain.exponentialRampToValueAtTime(0.18, now + i * 0.18 + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.18 + 0.5);
    osc.connect(gain).connect(audioCtx!.destination);
    osc.start(now + i * 0.18);
    osc.stop(now + i * 0.18 + 0.55);
  });
}

async function systemNotify(title: string, body: string) {
  try {
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    const reg = await navigator.serviceWorker?.getRegistration();
    if (reg) await reg.showNotification(title, { body, icon: "icon-192.png", tag: "lifeos-focus" });
    else new Notification(title, { body });
  } catch {
    /* notifications are best effort */
  }
}

export function FocusProvider({ children }: { children: React.ReactNode }) {
  const data = useData();
  const [state, setState] = React.useState<FocusState | null>(null);
  const [now, setNow] = React.useState(() => Date.now());
  const [viewOpen, setViewOpen] = React.useState(false);
  const [finished, setFinished] = React.useState<Finished | null>(null);
  const finishing = React.useRef(false);
  const tz = data.settings.timeZone;

  React.useEffect(() => setState(load()), []);

  const update = React.useCallback((s: FocusState | null) => {
    setState(s);
    persist(s);
  }, []);

  const complete = React.useCallback(
    async (s: FocusState, completed: boolean, minutes: number) => {
      if (finishing.current) return;
      finishing.current = true;
      try {
        update(null);
        if (s.mode === "focus" && minutes >= 1) {
          const endedAt = new Date(s.startedAt + s.pausedMs + minutes * 60_000).toISOString();
          await recordFocusSession({
            date: instantToDate(new Date(s.startedAt).toISOString(), tz),
            startedAt: new Date(s.startedAt).toISOString(),
            endedAt,
            minutes,
            title: s.title,
            taskId: s.taskId ?? null,
            completed,
          });
        }
        if (completed) {
          setFinished({ mode: s.mode, title: s.title, taskId: s.taskId, minutes });
          setViewOpen(true);
          chime();
          navigator.vibrate?.([220, 120, 220]);
          void systemNotify(s.mode === "focus" ? "Sesión de enfoque terminada" : "Fin del descanso", s.mode === "focus" ? `${minutes} min en «${s.title}». Tómate un respiro.` : "Volvamos al trabajo.");
        }
      } finally {
        finishing.current = false;
      }
    },
    [update, tz],
  );

  // Tick while running. Time is derived from the wall clock, so it survives reloads and background tabs.
  React.useEffect(() => {
    if (!state || state.pausedAt) return;
    const tick = () => {
      const t = Date.now();
      setNow(t);
      if (elapsedOf(state, t) >= state.plannedMin * 60_000) void complete(state, true, state.plannedMin);
    };
    tick();
    const id = window.setInterval(tick, 1000);
    const onVisible = () => document.visibilityState === "visible" && tick();
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.clearInterval(id);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [state, complete]);

  const value = React.useMemo<FocusContextValue>(() => {
    const elapsed = state ? Math.max(0, elapsedOf(state, now)) : 0;
    return {
      state,
      elapsedMs: elapsed,
      remainingMs: state ? Math.max(0, state.plannedMin * 60_000 - elapsed) : 0,
      viewOpen,
      setViewOpen,
      finished,
      dismissFinished: () => setFinished(null),
      start: ({ title, taskId, minutes, mode = "focus" }) => {
        prepareAudio();
        if ("Notification" in window && Notification.permission === "default") void Notification.requestPermission().catch(() => {});
        const planned = minutes ?? (mode === "focus" ? data.settings.planner.pomodoroMin : data.settings.planner.breakMin);
        setFinished(null);
        setNow(Date.now());
        update({ title, taskId: taskId ?? null, mode, plannedMin: planned, startedAt: Date.now(), pausedAt: null, pausedMs: 0 });
        if (mode === "focus") toast(`Enfoque de ${planned} min: ${title}`, { icon: <Zap className="size-4" /> });
      },
      pause: () => state && !state.pausedAt && update({ ...state, pausedAt: Date.now() }),
      resume: () => state?.pausedAt && update({ ...state, pausedMs: state.pausedMs + (Date.now() - state.pausedAt), pausedAt: null }),
      addMinutes: (m) => state && update({ ...state, plannedMin: state.plannedMin + m }),
      stop: async ({ completeTask } = {}) => {
        if (!state) return;
        const minutes = Math.floor(elapsedOf(state) / 60_000);
        await complete(state, false, minutes);
        if (completeTask && state.taskId) await setTaskDone(state.taskId, true);
        if (state.mode === "focus") toast.success(minutes >= 1 ? `${formatDuration(minutes)} de enfoque registrados` : "Sesión cancelada (menos de un minuto)");
        setViewOpen(false);
      },
    };
  }, [state, now, viewOpen, finished, update, complete, data.settings.planner.pomodoroMin, data.settings.planner.breakMin]);

  return <FocusContext.Provider value={value}>{children}</FocusContext.Provider>;
}

export function useFocus() {
  const ctx = React.useContext(FocusContext);
  if (!ctx) throw new Error("useFocus must be used inside FocusProvider");
  return ctx;
}

const mmss = (ms: number) => {
  const total = Math.ceil(ms / 1000);
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
};

/** Small floating pill while a session runs; tapping it opens the full focus view. */
export function FocusBar() {
  const f = useFocus();
  if (!f.state) return null;
  const paused = !!f.state.pausedAt;
  return (
    <div className="fixed bottom-[calc(4.5rem+env(safe-area-inset-bottom))] left-4 z-30 max-w-[calc(100%-6.5rem)] lg:bottom-5 lg:left-[252px] lg:max-w-sm">
      <div className="flex items-center gap-1 rounded-full border border-border bg-popover py-1 pr-1 pl-3 shadow-pop">
        <button type="button" onClick={() => f.setViewOpen(true)} className="flex min-w-0 items-center gap-2 py-1 text-left" aria-label="Abrir modo enfoque">
          <span className={cn("size-2 shrink-0 rounded-full", f.state.mode === "focus" ? "bg-brand" : "bg-income", !paused && "animate-pulse")} aria-hidden />
          <span className="text-sm font-semibold tabular">{mmss(f.remainingMs)}</span>
          <span className="min-w-0 truncate text-[13px] text-muted-foreground">{f.state.mode === "focus" ? f.state.title : "Descanso"}</span>
        </button>
        <Button variant="ghost" size="icon-sm" className="rounded-full" aria-label={paused ? "Reanudar" : "Pausar"} onClick={paused ? f.resume : f.pause}>
          {paused ? <Play /> : <Pause />}
        </Button>
      </div>
    </div>
  );
}

/** Full-screen focus view with the countdown ring and the end-of-session choices. */
export function FocusView() {
  const f = useFocus();
  const data = useData();
  const today = useToday();
  const todayMin = data.focusSessions.filter((s) => s.date === today).reduce((sum, s) => sum + s.minutes, 0);
  const todayCount = data.focusSessions.filter((s) => s.date === today).length;
  const s = f.state;
  const total = s ? s.plannedMin * 60_000 : 1;
  const progress = s ? 1 - f.remainingMs / total : 0;
  const R = 112;
  const C = 2 * Math.PI * R;
  const task = (s?.taskId ?? f.finished?.taskId) ? data.tasks.find((t) => t.id === (s?.taskId ?? f.finished?.taskId)) : undefined;
  const planner = data.settings.planner;

  return (
    <DialogPrimitive.Root open={f.viewOpen} onOpenChange={(v) => { f.setViewOpen(v); if (!v) f.dismissFinished(); }}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-background/90 backdrop-blur-md data-[state=open]:animate-in data-[state=open]:fade-in data-[state=closed]:animate-out data-[state=closed]:fade-out" />
        <DialogPrimitive.Content className="fixed inset-0 z-50 flex flex-col items-center justify-center px-6 pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)] outline-none data-[state=open]:animate-in data-[state=open]:fade-in data-[state=open]:zoom-in-[0.98]">
          <DialogPrimitive.Title className="sr-only">Modo enfoque</DialogPrimitive.Title>
          <DialogPrimitive.Description className="sr-only">Temporizador de enfoque</DialogPrimitive.Description>
          <DialogPrimitive.Close asChild>
            <Button variant="ghost" size="icon" className="absolute top-[max(1rem,env(safe-area-inset-top))] right-4" aria-label="Cerrar (el temporizador sigue)">
              <X />
            </Button>
          </DialogPrimitive.Close>

          {s ? (
            <>
              <p className={cn("text-[13px] font-semibold tracking-wide uppercase", s.mode === "focus" ? "text-brand" : "text-income")}>{s.mode === "focus" ? "Enfoque" : "Descanso"}</p>
              <p className="mt-1 max-w-md text-center text-lg font-semibold text-balance">{s.mode === "focus" ? s.title : "Respira, estírate, toma agua"}</p>
              <div className="relative my-8 size-64">
                <svg viewBox="0 0 256 256" className="size-full -rotate-90" aria-hidden>
                  <circle cx="128" cy="128" r={R} fill="none" stroke="var(--muted)" strokeWidth="10" />
                  <circle
                    cx="128"
                    cy="128"
                    r={R}
                    fill="none"
                    stroke={s.mode === "focus" ? "var(--brand)" : "var(--income)"}
                    strokeWidth="10"
                    strokeLinecap="round"
                    strokeDasharray={C}
                    strokeDashoffset={C * (1 - progress)}
                    style={{ transition: "stroke-dashoffset 1s linear" }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-[56px] leading-none font-semibold tracking-tight tabular" role="timer" aria-live="off">
                    {mmss(f.remainingMs)}
                  </span>
                  <span className="mt-2 text-xs text-muted-foreground">{s.pausedAt ? "En pausa" : `de ${s.plannedMin} min`}</span>
                </div>
              </div>
              <div className="flex flex-wrap items-center justify-center gap-2">
                <Button size="lg" onClick={s.pausedAt ? f.resume : f.pause}>
                  {s.pausedAt ? <Play /> : <Pause />} {s.pausedAt ? "Reanudar" : "Pausar"}
                </Button>
                <Button size="lg" variant="outline" onClick={() => f.addMinutes(5)}>
                  <Plus /> 5 min
                </Button>
                <Button size="lg" variant="ghost" onClick={() => f.stop()}>
                  <CircleStop /> Terminar
                </Button>
              </div>
              {task && task.status === "todo" && s.mode === "focus" && (
                <Button variant="link" className="mt-4" onClick={() => f.stop({ completeTask: true })}>
                  <CheckCheck /> Terminé la tarea
                </Button>
              )}
            </>
          ) : f.finished ? (
            <div className="flex max-w-sm flex-col items-center text-center">
              <span className={cn("flex size-16 items-center justify-center rounded-2xl", f.finished.mode === "focus" ? "bg-brand-soft text-brand" : "bg-income-soft text-income")}>
                {f.finished.mode === "focus" ? <CheckCheck className="size-7" /> : <Zap className="size-7" />}
              </span>
              <p className="mt-4 text-xl font-semibold">{f.finished.mode === "focus" ? "¡Sesión completada!" : "Descanso terminado"}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {f.finished.mode === "focus" ? `${f.finished.minutes} min en «${f.finished.title}».` : "¿Seguimos con otra sesión?"}
              </p>
              <div className="mt-6 grid w-full gap-2">
                {f.finished.mode === "focus" && (
                  <Button size="lg" variant="income" onClick={() => f.start({ title: "Descanso", mode: "break", taskId: f.finished?.taskId })}>
                    <Coffee /> Descanso de {planner.breakMin} min
                  </Button>
                )}
                <Button size="lg" onClick={() => f.start({ title: f.finished!.mode === "focus" ? f.finished!.title : task?.title ?? "Enfoque", taskId: f.finished!.taskId })}>
                  <Timer /> Otra sesión de {planner.pomodoroMin} min
                </Button>
                {task && task.status === "todo" && (
                  <Button
                    size="lg"
                    variant="outline"
                    onClick={async () => {
                      await setTaskDone(task.id, true);
                      toast.success("Tarea completada");
                      f.dismissFinished();
                      f.setViewOpen(false);
                    }}
                  >
                    <CheckCheck /> Marcar «{task.title}» como completada
                  </Button>
                )}
              </div>
            </div>
          ) : null}

          <p className="absolute bottom-[max(1.5rem,env(safe-area-inset-bottom))] text-xs text-muted-foreground tabular">
            Hoy: {todayCount} {todayCount === 1 ? "sesión" : "sesiones"} · {formatDuration(todayMin || 0)} de enfoque
          </p>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
