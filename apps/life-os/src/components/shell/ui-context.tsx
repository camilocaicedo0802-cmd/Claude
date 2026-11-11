"use client";

import * as React from "react";
import type { CalendarEvent, Task, TransactionKind, AccountType, CategoryKind } from "@/db/types";
import type { DateStr } from "@/lib/dates";
import { ConfirmDialog } from "@/components/ui/overlays";

export type FormRequest =
  | {
      kind: "transaction";
      id?: string;
      defaults?: { kind?: TransactionKind; clientId?: string | null; jobId?: string | null; categoryId?: string; accountId?: string };
    }
  | { kind: "client"; id?: string }
  | { kind: "job"; id?: string; defaults?: { clientId?: string; dueDate?: DateStr } }
  | { kind: "payment"; id?: string; defaults?: { jobId?: string; clientId?: string } }
  | { kind: "task"; id?: string; defaults?: Partial<Task> }
  | { kind: "event"; id?: string; occurrence?: DateStr; defaults?: Partial<CalendarEvent> }
  | { kind: "habit"; id?: string }
  | { kind: "obligation"; id?: string }
  | { kind: "obligationPayment"; obligationId: string; dueDate: DateStr }
  | { kind: "plannedIncome"; id?: string }
  | { kind: "receiveIncome"; plannedIncomeId: string; dueDate: DateStr }
  | { kind: "account"; id?: string; defaults?: { type?: AccountType } }
  | { kind: "goal"; id?: string }
  | { kind: "contribution"; goalId: string }
  | { kind: "budget"; categoryId?: string }
  | { kind: "category"; id?: string; defaults?: { kind?: CategoryKind } };

export type DetailRequest = { type: "client"; id: string } | { type: "job"; id: string };

export interface ConfirmOptions {
  title: string;
  description?: React.ReactNode;
  confirmLabel?: string;
  destructive?: boolean;
}

interface UIState {
  form: FormRequest | null;
  openForm: (req: FormRequest) => void;
  closeForm: () => void;
  detail: DetailRequest | null;
  openDetail: (req: DetailRequest) => void;
  closeDetail: () => void;
  quickAddOpen: boolean;
  setQuickAddOpen: (v: boolean) => void;
  searchOpen: boolean;
  setSearchOpen: (v: boolean) => void;
  notificationsOpen: boolean;
  setNotificationsOpen: (v: boolean) => void;
  confirm: (opts: ConfirmOptions) => Promise<boolean>;
}

const UIContext = React.createContext<UIState | null>(null);

export function UIProvider({ children }: { children: React.ReactNode }) {
  const [form, setForm] = React.useState<FormRequest | null>(null);
  const [detail, setDetail] = React.useState<DetailRequest | null>(null);
  const [quickAddOpen, setQuickAddOpen] = React.useState(false);
  const [searchOpen, setSearchOpen] = React.useState(false);
  const [notificationsOpen, setNotificationsOpen] = React.useState(false);
  const [confirmState, setConfirmState] = React.useState<(ConfirmOptions & { resolve: (v: boolean) => void }) | null>(null);
  const [confirmOpen, setConfirmOpen] = React.useState(false);

  const confirm = React.useCallback(
    (opts: ConfirmOptions) =>
      new Promise<boolean>((resolve) => {
        setConfirmState({ ...opts, resolve });
        setConfirmOpen(true);
      }),
    [],
  );

  const value = React.useMemo<UIState>(
    () => ({
      form,
      openForm: (req) => {
        setQuickAddOpen(false);
        setForm(req);
      },
      closeForm: () => setForm(null),
      detail,
      openDetail: (req) => setDetail(req),
      closeDetail: () => setDetail(null),
      quickAddOpen,
      setQuickAddOpen,
      searchOpen,
      setSearchOpen,
      notificationsOpen,
      setNotificationsOpen,
      confirm,
    }),
    [form, detail, quickAddOpen, searchOpen, notificationsOpen, confirm],
  );

  return (
    <UIContext.Provider value={value}>
      {children}
      {confirmState && (
        <ConfirmDialog
          open={confirmOpen}
          onOpenChange={(open) => {
            setConfirmOpen(open);
            if (!open) {
              confirmState.resolve(false);
              setTimeout(() => setConfirmState(null), 200);
            }
          }}
          title={confirmState.title}
          description={confirmState.description}
          confirmLabel={confirmState.confirmLabel}
          destructive={confirmState.destructive}
          onConfirm={() => {
            confirmState.resolve(true);
          }}
        />
      )}
    </UIContext.Provider>
  );
}

export function useUI(): UIState {
  const ctx = React.useContext(UIContext);
  if (!ctx) throw new Error("useUI must be used inside UIProvider");
  return ctx;
}
