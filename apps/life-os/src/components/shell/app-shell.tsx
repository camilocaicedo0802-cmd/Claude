"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Toaster } from "sonner";
import { FlaskConical, HardDrive, Plus, Search, Settings } from "lucide-react";
import { DataProvider, useAlerts, useData, useDBStatus, useJobViews, useNow } from "@/hooks/data";
import { readMode } from "@/db/db";
import { pendingObligations } from "@/domain/finance";
import { dailyBrief } from "@/domain/insights";
import { addDays, formatDateLong, greetingFor } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Kbd } from "@/components/ui/misc";
import { TooltipProvider, Tooltip } from "@/components/ui/overlays";
import { PageSkeleton } from "@/components/shared/primitives";
import { FormHost } from "@/components/forms/form-host";
import { DetailHost } from "@/components/clients/detail-sheets";
import { discardDemo, switchMode, THEME_STORAGE_KEY } from "@/services/settings-service";
import { NAV, sectionFor } from "./nav";
import { NotificationCenter } from "./notifications";
import { Onboarding } from "./onboarding";
import { QuickAdd } from "./quick-add";
import { SearchCommand } from "./search-command";
import { UIProvider, useUI } from "./ui-context";
import { useIsDesktop } from "@/hooks/use-media";
import { ServiceWorkerRegistrar } from "./pwa";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <DataProvider>
      <UIProvider>
        <TooltipProvider delayDuration={300}>
          <AppShell>{children}</AppShell>
        </TooltipProvider>
      </UIProvider>
    </DataProvider>
  );
}

function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <svg viewBox="0 0 24 24" className="size-6" aria-hidden>
        <rect x="1" y="1" width="22" height="22" rx="6.5" className="fill-foreground" />
        <rect x="6" y="6.5" width="12" height="2.6" rx="1.3" className="fill-background" />
        <rect x="6" y="10.7" width="8.5" height="2.6" rx="1.3" className="fill-background opacity-75" />
        <rect x="6" y="14.9" width="5" height="2.6" rx="1.3" className="fill-brand" />
      </svg>
      <span className="text-[15px] font-semibold tracking-tight">LIFE OS</span>
    </span>
  );
}

function ThemeSync() {
  const data = useData();
  const theme = data.settings.theme;
  React.useEffect(() => {
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      /* ignore */
    }
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      const dark = theme === "dark" || (theme === "system" && mq.matches);
      document.documentElement.classList.toggle("dark", dark);
      document.querySelector('meta[name="theme-color"]')?.setAttribute("content", dark ? "#161513" : "#faf9f7");
    };
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, [theme]);
  return null;
}

function Shortcuts() {
  const router = useRouter();
  const { setSearchOpen, setQuickAddOpen, form, detail } = useUI();
  React.useEffect(() => {
    let pendingG = false;
    let gTimer: number | undefined;
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const typing = target && (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen(true);
        return;
      }
      if (typing || e.metaKey || e.ctrlKey || e.altKey || form || detail) return;
      if (document.querySelector("[role=dialog]")) return;
      const k = e.key.toLowerCase();
      if (pendingG) {
        pendingG = false;
        const to = k === "f" ? "/finanzas/" : k === "c" ? "/clientes/" : k === "v" ? "/vida/" : k === "a" ? "/ajustes/" : null;
        if (to) {
          e.preventDefault();
          router.push(to);
        }
        return;
      }
      if (k === "/") {
        e.preventDefault();
        setSearchOpen(true);
      } else if (k === "n") {
        e.preventDefault();
        setQuickAddOpen(true);
      } else if (k === "g") {
        pendingG = true;
        window.clearTimeout(gTimer);
        gTimer = window.setTimeout(() => (pendingG = false), 900);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [router, setSearchOpen, setQuickAddOpen, form, detail]);
  return null;
}

/** Opens a record when the URL carries ?trabajo=… or ?cliente=… (links from notifications). */
function DeepLinks() {
  const pathname = usePathname();
  const { openDetail } = useUI();
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const job = params.get("trabajo");
    const client = params.get("cliente");
    if (job) openDetail({ type: "job", id: job });
    else if (client) openDetail({ type: "client", id: client });
    if (job || client) window.history.replaceState(null, "", window.location.pathname);
  }, [pathname, openDetail]);
  return null;
}

function useBrief() {
  const data = useData();
  const now = useNow();
  const views = useJobViews();
  return React.useMemo(() => {
    const obligations = pendingObligations(data.obligations, data.transactions, addDays(now.date, 3), now.date);
    return dailyBrief({ today: now.date, tasks: data.tasks, jobViews: views, obligations });
  }, [data.obligations, data.transactions, data.tasks, views, now.date]);
}

function Sidebar() {
  const pathname = usePathname();
  const current = sectionFor(pathname);
  const { unread } = useAlerts();
  const demo = readMode() === "demo";
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[232px] flex-col border-r border-border bg-sidebar lg:flex">
      <div className="flex h-14 items-center px-4">
        <Link href="/vida/" className="rounded-md outline-none focus-visible:ring-2 focus-visible:ring-ring">
          <Logo />
        </Link>
      </div>
      <nav aria-label="Principal" className="flex-1 space-y-1 overflow-y-auto px-2.5 py-2">
        {NAV.map((s) => {
          const active = current?.key === s.key;
          const count = unread.filter((a) => a.area === s.key).length;
          return (
            <div key={s.key}>
              <Link
                href={s.href}
                aria-current={active ? "true" : undefined}
                className={cn(
                  "flex h-9 items-center gap-2.5 rounded-lg px-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground",
                  active && "bg-card text-foreground shadow-[0_0_0_1px_var(--border)] hover:bg-card",
                )}
              >
                <s.icon className={cn("size-[18px]", active && "text-brand")} />
                <span className="flex-1">{s.label}</span>
                {count > 0 && <span className="rounded-full bg-expense-soft px-1.5 text-[11px] font-semibold text-expense tabular">{count}</span>}
              </Link>
              {active && (
                <ul className="mt-1 mb-2 ml-[19px] space-y-0.5 border-l border-border pl-2.5">
                  {s.items.map((i) => {
                    const on = i.exact ? pathname.replace(/\/$/, "") === i.href.replace(/\/$/, "") : pathname.startsWith(i.href.replace(/\/$/, ""));
                    return (
                      <li key={i.href}>
                        <Link
                          href={i.href}
                          aria-current={on ? "page" : undefined}
                          className={cn("flex h-8 items-center rounded-md px-2 text-[13px] text-muted-foreground transition-colors hover:text-foreground", on && "font-medium text-foreground")}
                        >
                          {i.label}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })}
      </nav>
      <div className="space-y-1 border-t border-border p-2.5">
        {demo && (
          <div className="mb-2 rounded-lg bg-warning-soft p-2.5 text-xs text-warning">
            <p className="flex items-center gap-1.5 font-semibold">
              <FlaskConical className="size-3.5" /> Modo demo
            </p>
            <p className="mt-0.5">Datos de ejemplo, separados de los tuyos.</p>
          </div>
        )}
        <Link
          href="/ajustes/"
          className={cn("flex h-9 items-center gap-2.5 rounded-lg px-2.5 text-sm text-muted-foreground hover:bg-accent hover:text-foreground", pathname.startsWith("/ajustes") && "bg-card text-foreground")}
        >
          <Settings className="size-[18px]" /> Ajustes
        </Link>
        <p className="flex items-center gap-1.5 px-2.5 pt-1 text-[11px] text-subtle">
          <HardDrive className="size-3" /> Guardado en este dispositivo
        </p>
      </div>
    </aside>
  );
}

function Header() {
  const now = useNow();
  const data = useData();
  const brief = useBrief();
  const { setSearchOpen, setQuickAddOpen } = useUI();
  const desktop = useIsDesktop();
  const name = data.settings.userName.trim().split(" ")[0];
  return (
    <header className="sticky top-0 z-20 border-b border-border/70 bg-background/85 pt-safe backdrop-blur-md supports-[backdrop-filter]:bg-background/70">
      <div className="mx-auto flex h-14 max-w-[1240px] items-center gap-3 px-4 sm:px-6 lg:h-16">
        <Link href="/vida/" className="lg:hidden" aria-label="LIFE OS, ir a Mi día">
          <svg viewBox="0 0 24 24" className="size-7" aria-hidden>
            <rect x="1" y="1" width="22" height="22" rx="6.5" className="fill-foreground" />
            <rect x="6" y="6.5" width="12" height="2.6" rx="1.3" className="fill-background" />
            <rect x="6" y="10.7" width="8.5" height="2.6" rx="1.3" className="fill-background opacity-75" />
            <rect x="6" y="14.9" width="5" height="2.6" rx="1.3" className="fill-brand" />
          </svg>
        </Link>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] text-muted-foreground first-letter:uppercase max-lg:text-xs">{formatDateLong(now.date)}</p>
          <p className="truncate text-sm font-semibold lg:text-[15px]">
            {greetingFor(now.hour)}
            {name ? `, ${name}` : ""}
            {brief && (
              <Link href="/vida/" className="ml-2 font-normal text-muted-foreground hover:text-foreground max-xl:hidden">
                {brief}
              </Link>
            )}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setSearchOpen(true)}
          className="hidden h-9 w-60 items-center gap-2 rounded-lg border border-border bg-card px-3 text-[13px] text-subtle transition-colors hover:border-border-strong hover:text-muted-foreground md:flex"
        >
          <Search className="size-4" />
          <span className="flex-1 text-left">Buscar…</span>
          <Kbd>⌘K</Kbd>
        </button>
        <Button variant="ghost" size="icon" aria-label="Buscar" onClick={() => setSearchOpen(true)} className="md:hidden">
          <Search />
        </Button>
        <NotificationCenter />
        <Tooltip content="Ajustes">
          <Button variant="ghost" size="icon" asChild className="max-lg:hidden">
            <Link href="/ajustes/" aria-label="Ajustes">
              <Settings />
            </Link>
          </Button>
        </Tooltip>
        <Button variant="ghost" size="icon" asChild className="lg:hidden">
          <Link href="/ajustes/" aria-label="Ajustes">
            <Settings />
          </Link>
        </Button>
        {desktop && (
          <QuickAdd
            trigger={
              <Button onClick={() => setQuickAddOpen(true)}>
                <Plus /> Agregar
              </Button>
            }
          />
        )}
      </div>
    </header>
  );
}

function BottomNav() {
  const pathname = usePathname();
  const current = sectionFor(pathname);
  const { setQuickAddOpen } = useUI();
  const desktop = useIsDesktop();
  return (
    <>
      <div className="fixed right-4 bottom-[calc(4.25rem+env(safe-area-inset-bottom))] z-30 lg:hidden">
        {!desktop && <QuickAdd />}
        <button
          type="button"
          aria-label="Agregar"
          onClick={() => setQuickAddOpen(true)}
          className="press flex size-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-pop outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        >
          <Plus className="size-6" />
        </button>
      </div>
      <nav aria-label="Principal" className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-background/92 pb-safe backdrop-blur-md lg:hidden">
        <ul className="mx-auto grid h-16 max-w-md grid-cols-3">
          {NAV.map((s) => {
            const active = current?.key === s.key;
            return (
              <li key={s.key}>
                <Link
                  href={s.href}
                  aria-current={active ? "page" : undefined}
                  className={cn("flex h-full flex-col items-center justify-center gap-1 text-[11px] font-medium text-muted-foreground transition-colors", active && "text-foreground")}
                >
                  <span className={cn("flex h-7 w-12 items-center justify-center rounded-full transition-colors", active && "bg-brand-soft text-brand")}>
                    <s.icon className="size-5" />
                  </span>
                  {s.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </>
  );
}

function DemoBanner() {
  if (readMode() !== "demo") return null;
  return (
    <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 border-b border-warning/30 bg-warning-soft px-4 py-2 text-center text-[13px] text-warning lg:hidden">
      <span className="inline-flex items-center gap-1.5 font-semibold">
        <FlaskConical className="size-3.5" /> Modo demo
      </span>
      <span>Estás viendo datos de ejemplo.</span>
      <button type="button" className="font-semibold underline underline-offset-2" onClick={() => switchMode("real")}>
        Volver a mis datos
      </button>
    </div>
  );
}

function ReadyShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <ThemeSync />
      <Shortcuts />
      <DeepLinks />
      <Sidebar />
      <div className="lg:pl-[232px]">
        <DemoBanner />
        <Header />
        <main id="contenido" className="mx-auto max-w-[1240px] px-4 pt-5 pb-[calc(6.5rem+env(safe-area-inset-bottom))] sm:px-6 lg:pt-7 lg:pb-16">
          {children}
        </main>
      </div>
      <BottomNav />
      <FormHost />
      <DetailHost />
      <SearchCommand />
      <Onboarding />
    </>
  );
}

function AppShell({ children }: { children: React.ReactNode }) {
  const { status, error } = useDBStatus();
  if (status === "error") {
    return (
      <div className="mx-auto flex min-h-dvh max-w-md flex-col items-center justify-center px-6 text-center">
        <Logo className="mb-6" />
        <h1 className="text-lg font-semibold">No se pudo abrir tu base de datos local</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          El navegador bloqueó el almacenamiento (por ejemplo, en modo incógnito estricto) o no hay espacio. Abre LIFE OS en una ventana normal o libera espacio e inténtalo de nuevo.
        </p>
        {error && <p className="mt-3 rounded-lg bg-muted px-3 py-2 font-mono text-xs text-muted-foreground">{error}</p>}
        <div className="mt-5 flex gap-2">
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
          {readMode() === "demo" && (
            <Button variant="outline" onClick={() => discardDemo()}>
              Salir del modo demo
            </Button>
          )}
        </div>
      </div>
    );
  }
  return (
    <>
      <ServiceWorkerRegistrar />
      {status === "ready" ? (
        <ReadyShell>{children}</ReadyShell>
      ) : (
        <div className="lg:pl-[232px]">
          <div className="fixed inset-y-0 left-0 hidden w-[232px] border-r border-border bg-sidebar p-4 lg:block">
            <Logo />
          </div>
          <div className="h-14 border-b border-border lg:h-16" />
          <main className="mx-auto max-w-[1240px] px-4 pt-5 sm:px-6 lg:pt-7">
            <PageSkeleton />
          </main>
        </div>
      )}
      <Toaster
        position="bottom-center"
        offset={{ bottom: 88 }}
        mobileOffset={{ bottom: 92 }}
        toastOptions={{
          classNames: {
            toast: "!rounded-xl !border-border !bg-popover !text-popover-foreground !shadow-pop !font-sans",
            description: "!text-muted-foreground",
            actionButton: "!bg-primary !text-primary-foreground !rounded-md",
          },
        }}
      />
    </>
  );
}
