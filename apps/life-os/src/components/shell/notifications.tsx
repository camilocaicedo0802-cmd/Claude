"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Bell, BellOff, CheckCheck, CircleAlert, Info, TriangleAlert, X } from "lucide-react";
import { useAlerts, useData } from "@/hooks/data";
import { useIsDesktop } from "@/hooks/use-media";
import { db } from "@/db/db";
import { nowISO } from "@/lib/dates";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger, Sheet } from "@/components/ui/overlays";
import type { Alert } from "@/domain/alerts";
import { useUI } from "./ui-context";

const AREA_LABEL = { finanzas: "Finanzas", clientes: "Clientes", vida: "Mi Vida" };

function AlertList({ alerts, dismissed, onGo }: { alerts: Alert[]; dismissed: Set<string>; onGo: (a: Alert) => void }) {
  if (alerts.length === 0) {
    return (
      <div className="flex flex-col items-center px-4 py-8 text-center">
        <BellOff className="size-5 text-muted-foreground" />
        <p className="mt-2 text-sm font-medium">Todo en orden</p>
        <p className="mt-1 text-xs text-muted-foreground">Aquí verás pagos por vencer, entregas, cobros atrasados y presupuestos al límite.</p>
      </div>
    );
  }
  return (
    <ul className="space-y-1">
      {alerts.map((a) => {
        const Icon = a.severity === "critical" ? CircleAlert : a.severity === "warning" ? TriangleAlert : Info;
        const seen = dismissed.has(a.key);
        return (
          <li key={a.key} className="group relative">
            <button
              type="button"
              onClick={() => onGo(a)}
              className={cn("flex w-full items-start gap-3 rounded-lg p-2.5 pr-9 text-left hover:bg-accent", seen && "opacity-60")}
            >
              <Icon
                className={cn(
                  "mt-0.5 size-4 shrink-0",
                  a.severity === "critical" ? "text-expense" : a.severity === "warning" ? "text-warning" : "text-info",
                )}
              />
              <span className="min-w-0">
                <span className="block text-[13px] leading-snug font-medium">{a.title}</span>
                <span className="mt-0.5 block text-xs text-muted-foreground">
                  {AREA_LABEL[a.area]} · {a.description}
                </span>
              </span>
            </button>
            {!seen && (
              <button
                type="button"
                aria-label="Marcar como vista"
                onClick={() => db().alertState.put({ key: a.key, dismissedAt: nowISO() })}
                className="absolute top-2 right-2 flex size-7 items-center justify-center rounded-md text-muted-foreground opacity-100 hover:bg-background hover:text-foreground lg:opacity-0 lg:group-hover:opacity-100 lg:focus-visible:opacity-100"
              >
                <X className="size-3.5" />
              </button>
            )}
          </li>
        );
      })}
    </ul>
  );
}

export function NotificationCenter() {
  const { all, unread } = useAlerts();
  const data = useData();
  const router = useRouter();
  const desktop = useIsDesktop();
  const { notificationsOpen, setNotificationsOpen } = useUI();
  const dismissed = React.useMemo(() => new Set(data.alertState.map((a) => a.key)), [data.alertState]);
  const go = (a: Alert) => {
    setNotificationsOpen(false);
    void db().alertState.put({ key: a.key, dismissedAt: nowISO() });
    router.push(a.href);
  };
  const markAll = () => db().alertState.bulkPut(unread.map((a) => ({ key: a.key, dismissedAt: nowISO() })));
  const trigger = (
    <Button variant="ghost" size="icon" aria-label={unread.length ? `Notificaciones (${unread.length} sin ver)` : "Notificaciones"} className="relative">
      <Bell />
      {unread.length > 0 && (
        <span className="absolute top-1 right-1 flex min-w-4 items-center justify-center rounded-full bg-expense px-1 text-[10px] leading-4 font-semibold text-white tabular ring-2 ring-background">
          {unread.length > 9 ? "9+" : unread.length}
        </span>
      )}
    </Button>
  );
  const header = (
    <div className="flex items-center justify-between px-1 pb-2">
      <p className="text-sm font-semibold">Notificaciones</p>
      {unread.length > 0 && (
        <Button variant="ghost" size="sm" onClick={markAll}>
          <CheckCheck /> Marcar vistas
        </Button>
      )}
    </div>
  );
  if (desktop) {
    return (
      <Popover open={notificationsOpen} onOpenChange={setNotificationsOpen}>
        <PopoverTrigger asChild>{trigger}</PopoverTrigger>
        <PopoverContent className="w-[380px] p-2">
          {header}
          <div className="max-h-[60vh] overflow-y-auto">
            <AlertList alerts={all} dismissed={dismissed} onGo={go} />
          </div>
        </PopoverContent>
      </Popover>
    );
  }
  return (
    <>
      <span onClick={() => setNotificationsOpen(true)}>{trigger}</span>
      <Sheet open={notificationsOpen} onOpenChange={setNotificationsOpen} title="Notificaciones" headerExtra={unread.length > 0 ? <Button variant="ghost" size="sm" onClick={markAll}><CheckCheck /> Vistas</Button> : undefined}>
        <AlertList alerts={all} dismissed={dismissed} onGo={go} />
      </Sheet>
    </>
  );
}
