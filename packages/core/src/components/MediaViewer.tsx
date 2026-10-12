"use client";
import { ArrowLeft, ArrowRight, ArrowUpRight, X } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { counts } from "../content/chapters";
import { formatDuration, pieceSrc, posterSrc, videoMeta, videoSources } from "../content/media";
import type { Entry } from "../content/types";
import { pad2 } from "../lib/format";
import { caseHref } from "../lib/paths";
import { pauseAll } from "../lib/playback";
import { lockScroll } from "../lib/scroll";
import { SiteLink } from "./SiteLink";

interface ViewerState {
  list: Entry[];
  index: number;
}

const ViewerContext = createContext<(list: Entry[], index: number) => void>(() => {});

/** Opens the full-screen viewer on `list[index]`; arrows step through the rest of the list. */
export const useOpenViewer = () => useContext(ViewerContext);

/** Full-screen viewer for videos (with sound) and pieces, shared by every section on the page. */
export function ViewerProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ViewerState | null>(null);
  const opener = useRef<HTMLElement | null>(null);
  const open = useCallback((list: Entry[], index: number) => {
    opener.current = document.activeElement as HTMLElement | null;
    pauseAll();
    setState({ list, index: Math.max(0, Math.min(index, list.length - 1)) });
  }, []);
  const close = useCallback(() => {
    setState(null);
    requestAnimationFrame(() => opener.current?.focus());
  }, []);
  const move = useCallback(
    (delta: number) => setState((s) => (s ? { ...s, index: (s.index + delta + s.list.length) % s.list.length } : s)),
    [],
  );

  return (
    <ViewerContext.Provider value={open}>
      {children}
      <AnimatePresence>{state && <ViewerDialog key="viewer" state={state} onClose={close} onMove={move} />}</AnimatePresence>
    </ViewerContext.Provider>
  );
}

function ViewerDialog({ state, onClose, onMove }: { state: ViewerState; onClose: () => void; onMove: (delta: number) => void }) {
  const { item, chapter, index } = state.list[state.index];
  const dialog = useRef<HTMLDivElement>(null);
  const closeBtn = useRef<HTMLButtonElement>(null);
  const touch = useRef<{ x: number; y: number; t: number } | null>(null);
  const reduced = useReducedMotion();
  const multiple = state.list.length > 1;
  const meta = item.kind === "video" ? videoMeta(item.video) : null;
  const { videos, pieces } = counts(chapter);
  const key = item.kind === "video" ? item.video : item.image.file;

  useEffect(() => {
    lockScroll(true);
    closeBtn.current?.focus();
    return () => lockScroll(false);
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (multiple && e.key === "ArrowRight" && !(e.target instanceof HTMLVideoElement)) onMove(1);
      if (multiple && e.key === "ArrowLeft" && !(e.target instanceof HTMLVideoElement)) onMove(-1);
      if (e.key === "Tab" && dialog.current) {
        const focusable = dialog.current.querySelectorAll<HTMLElement>("button, a, video");
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose, onMove, multiple]);

  // Horizontal swipe on the media steps through the list (a quick flick is enough).
  const onTouchStart = (e: React.TouchEvent) => {
    const t = e.touches[0];
    touch.current = { x: t.clientX, y: t.clientY, t: performance.now() };
  };
  const onTouchEnd = (e: React.TouchEvent) => {
    const start = touch.current;
    touch.current = null;
    if (!start || !multiple) return;
    const t = e.changedTouches[0];
    const dx = t.clientX - start.x;
    const dy = t.clientY - start.y;
    const velocity = Math.abs(dx) / (performance.now() - start.t);
    if (Math.abs(dx) > Math.abs(dy) * 1.5 && (Math.abs(dx) > 60 || velocity > 0.4)) onMove(dx < 0 ? 1 : -1);
  };

  const label = `${item.kind === "video" ? "Video" : "Pieza"}: ${item.title}`;
  const description = item.description ?? chapter.description;

  return (
    <motion.div
      className="fixed inset-0 z-[80] bg-ink"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.2 } }}
      transition={{ duration: 0.25 }}
    >
      <motion.div
        ref={dialog}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        className="relative mx-auto flex h-full w-full max-w-[1400px] flex-col overflow-y-auto overscroll-contain md:flex-row md:items-center md:gap-10 md:overflow-hidden md:px-8"
        initial={reduced ? { opacity: 0 } : { opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={reduced ? { opacity: 0 } : { opacity: 0, scale: 0.99, transition: { duration: 0.18 } }}
        transition={{ duration: 0.32, ease: [0.32, 0.72, 0, 1] }}
      >
        <div className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-between gap-4 bg-ink px-[var(--gutter)] md:fixed md:inset-x-0 md:top-0 md:bg-transparent md:px-6">
          <p className="min-w-0 truncate text-sm font-medium text-fog md:pointer-events-none">
            <span className="tabular text-signal">{pad2(chapter.number)}</span> {chapter.title}
          </p>
          <button
            ref={closeBtn}
            type="button"
            onClick={onClose}
            className="press grid size-11 shrink-0 place-items-center rounded-full bg-panel hover:bg-signal"
            aria-label="Cerrar"
          >
            <X size={20} />
          </button>
        </div>

        <div
          className="flex shrink-0 items-center justify-center px-[var(--gutter)] md:h-full md:min-w-0 md:flex-1 md:px-0 md:py-20"
          onTouchStart={onTouchStart}
          onTouchEnd={onTouchEnd}
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={key}
              className="flex max-h-full w-full items-center justify-center"
              initial={reduced ? { opacity: 0 } : { opacity: 0, filter: "blur(4px)" }}
              animate={{ opacity: 1, filter: "blur(0px)" }}
              exit={{ opacity: 0, transition: { duration: 0.12 } }}
              transition={{ duration: 0.22, ease: [0.23, 1, 0.32, 1] }}
            >
              {item.kind === "video" && meta ? (
                <video
                  className="max-h-[62svh] w-auto max-w-full bg-panel md:max-h-[calc(100svh-10rem)]"
                  style={{ aspectRatio: `${meta.width} / ${meta.height}` }}
                  poster={posterSrc(item.video)}
                  controls
                  autoPlay
                  playsInline
                  preload="auto"
                >
                  {videoSources(item.video).map((s) => (
                    <source key={s.type} src={s.src} type={s.type} />
                  ))}
                </video>
              ) : item.kind === "image" ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={pieceSrc(item.image.file)}
                  alt={item.image.alt}
                  width={item.image.width}
                  height={item.image.height}
                  className="max-h-[62svh] w-auto max-w-full object-contain md:max-h-[calc(100svh-10rem)]"
                />
              ) : null}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="w-full min-w-0 px-[var(--gutter)] pb-28 pt-6 md:w-[22rem] md:shrink-0 md:px-0 md:pb-0 md:pt-0">
          <p className="text-sm font-semibold tabular text-signal" aria-live="polite">
            {pad2(index + 1)}
            <span className="font-medium text-smoke"> / {pad2(chapter.items.length)}</span>
          </p>
          <h2 className="mt-3 text-[1.75rem] font-bold leading-tight tracking-[-0.03em] md:text-4xl">{item.title}</h2>
          <p className="mt-2 text-sm text-fog">{chapter.client ? `${chapter.client} · ${chapter.context}` : chapter.context}</p>
          <p className="body-copy mt-5 text-[0.9375rem]">{description}</p>
          <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-4 border-t border-line pt-5 text-sm">
            <div className="col-span-2">
              <dt className="text-smoke">Rol</dt>
              <dd className="mt-1">{chapter.role}</dd>
            </div>
            {meta && (
              <div>
                <dt className="text-smoke">Duración</dt>
                <dd className="mt-1 tabular">{formatDuration(meta.duration)}</dd>
              </div>
            )}
            <div>
              <dt className="text-smoke">En el proyecto</dt>
              <dd className="mt-1">{[videos && `${videos} ${videos === 1 ? "video" : "videos"}`, pieces && `${pieces} ${pieces === 1 ? "pieza" : "piezas"}`].filter(Boolean).join(" · ")}</dd>
            </div>
          </dl>
          <SiteLink
            href={caseHref(chapter.slug)}
            className="press mt-7 inline-flex h-12 items-center gap-2 border border-white/25 px-5 text-[0.8125rem] font-medium uppercase tracking-[0.06em] hover:border-paper"
          >
            Ver proyecto completo <ArrowUpRight aria-hidden size={16} />
          </SiteLink>
        </div>

        {multiple && (
          <div className="fixed inset-x-0 bottom-0 z-10 flex items-center justify-between gap-3 border-t border-line bg-ink px-[var(--gutter)] pb-[max(12px,env(safe-area-inset-bottom))] pt-3 md:inset-x-auto md:bottom-6 md:right-6 md:border-0 md:bg-transparent md:p-0">
            <button type="button" onClick={() => onMove(-1)} className="press grid size-12 place-items-center bg-panel hover:bg-panel-2" aria-label="Anterior">
              <ArrowLeft size={18} />
            </button>
            <span className="text-xs font-medium tabular text-smoke md:hidden">
              {pad2(state.index + 1)} / {pad2(state.list.length)}
            </span>
            <button type="button" onClick={() => onMove(1)} className="press grid size-12 place-items-center bg-panel hover:bg-panel-2" aria-label="Siguiente">
              <ArrowRight size={18} />
            </button>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
