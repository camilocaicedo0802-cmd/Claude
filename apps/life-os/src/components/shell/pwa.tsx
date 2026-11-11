"use client";

import * as React from "react";
import { Download, EllipsisVertical, Share, Smartphone, X } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { requestPersistentStorage } from "@/services/settings-service";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
const DISMISS_KEY = "lifeos:install-dismissed";
export const LAST_BACKUP_KEY = "lifeos:last-backup";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

// The install prompt event can fire before any component mounts: keep it at module level.
let deferredPrompt: BeforeInstallPromptEvent | null = null;
const listeners = new Set<() => void>();
const notify = () => listeners.forEach((l) => l());

if (typeof window !== "undefined") {
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e as BeforeInstallPromptEvent;
    notify();
  });
  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    notify();
    toast.success("LIFE OS quedó instalada en tu pantalla de inicio");
  });
}

export function isStandalone(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(display-mode: standalone)").matches || (navigator as Navigator & { standalone?: boolean }).standalone === true;
}

/** iOS has no install prompt: the user installs from the Share sheet, so the copy differs. */
function isIOS(): boolean {
  if (typeof navigator === "undefined") return false;
  return /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

export function useInstall() {
  const [, force] = React.useReducer((x: number) => x + 1, 0);
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => {
    setMounted(true);
    listeners.add(force);
    return () => {
      listeners.delete(force);
    };
  }, []);
  return {
    ready: mounted,
    standalone: mounted && isStandalone(),
    ios: mounted && isIOS(),
    canPrompt: mounted && !!deferredPrompt,
    prompt: async () => {
      if (!deferredPrompt) return false;
      await deferredPrompt.prompt();
      const choice = await deferredPrompt.userChoice;
      deferredPrompt = null;
      notify();
      return choice.outcome === "accepted";
    },
  };
}

/** Registers the offline service worker (production builds only) and announces updates. */
export function ServiceWorkerRegistrar() {
  React.useEffect(() => {
    if (process.env.NODE_ENV !== "production" || !("serviceWorker" in navigator)) return;
    const hadController = !!navigator.serviceWorker.controller;
    let refreshing = false;
    const onChange = () => {
      if (!hadController || refreshing) return;
      refreshing = true;
      toast("Hay una versión nueva de LIFE OS", {
        duration: Infinity,
        action: { label: "Actualizar", onClick: () => window.location.reload() },
      });
    };
    navigator.serviceWorker.addEventListener("controllerchange", onChange);
    navigator.serviceWorker.register(`${BASE}/sw.js`, { scope: `${BASE}/` }).catch((e) => console.warn("Service worker no registrado", e));
    // Installed apps keep their data; ask the browser not to evict it under storage pressure.
    if (isStandalone()) void requestPersistentStorage();
    return () => navigator.serviceWorker.removeEventListener("controllerchange", onChange);
  }, []);
  return null;
}

export function InstallInstructions({ ios }: { ios: boolean }) {
  return ios ? (
    <ol className="space-y-1 text-[13px] text-muted-foreground">
      <li>
        1. Abre esta página en <span className="font-medium text-foreground">Safari</span>.
      </li>
      <li className="flex flex-wrap items-center gap-1">
        2. Toca <Share className="inline size-3.5" aria-label="Compartir" /> <span className="font-medium text-foreground">Compartir</span> y luego
        <span className="font-medium text-foreground">«Agregar a pantalla de inicio»</span>.
      </li>
      <li>3. Desde entonces, abre LIFE OS solo con su ícono: la app instalada guarda sus datos aparte de Safari.</li>
    </ol>
  ) : (
    <p className="text-[13px] text-muted-foreground">
      En el menú del navegador <EllipsisVertical className="inline size-3.5" aria-label="Menú" /> elige <span className="font-medium text-foreground">«Instalar app»</span> o <span className="font-medium text-foreground">«Agregar a pantalla de inicio»</span>. Después ábrela siempre desde su ícono.
    </p>
  );
}

/** Dismissible card on phones that are not running the installed app. */
export function InstallBanner() {
  const install = useInstall();
  const [dismissed, setDismissed] = React.useState(true);
  React.useEffect(() => {
    try {
      setDismissed(localStorage.getItem(DISMISS_KEY) === "1");
    } catch {
      setDismissed(false);
    }
  }, []);
  if (!install.ready || install.standalone || dismissed) return null;
  if (!window.matchMedia("(pointer: coarse)").matches) return null;
  const dismiss = () => {
    setDismissed(true);
    try {
      localStorage.setItem(DISMISS_KEY, "1");
    } catch {
      /* ignore */
    }
  };
  return (
    <div className="flex items-start gap-3 rounded-xl border border-brand/25 bg-brand-soft/60 p-4">
      <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand text-brand-foreground">
        <Smartphone className="size-4" />
      </span>
      <div className="min-w-0 flex-1 space-y-2">
        <p className="text-sm font-semibold">Instala LIFE OS en tu celular</p>
        {install.canPrompt ? (
          <>
            <p className="text-[13px] text-muted-foreground">Se abre como una app, sin barra del navegador, y funciona sin conexión.</p>
            <Button size="sm" variant="brand" onClick={() => install.prompt().then((ok) => ok && dismiss())}>
              <Download /> Instalar
            </Button>
          </>
        ) : (
          <InstallInstructions ios={install.ios} />
        )}
      </div>
      <Button variant="ghost" size="icon-sm" aria-label="Ocultar" onClick={dismiss} className="-mt-1 -mr-1">
        <X />
      </Button>
    </div>
  );
}

export function markBackupDone() {
  try {
    localStorage.setItem(LAST_BACKUP_KEY, new Date().toISOString());
  } catch {
    /* ignore */
  }
}

export function lastBackupAt(): string | null {
  try {
    return localStorage.getItem(LAST_BACKUP_KEY);
  } catch {
    return null;
  }
}
