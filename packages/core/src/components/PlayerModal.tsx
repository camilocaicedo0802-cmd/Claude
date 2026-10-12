"use client";
import { ArrowLeft, ArrowRight, ArrowUpRight, X } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import Link from "next/link";
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { formatDuration, posterSrc, videoMeta, videoSources } from "../content/media";
import type { Project } from "../content/types";
import { pauseAll } from "../lib/playback";
import { lockScroll } from "../lib/scroll";

interface PlayerState {
  list: Project[];
  index: number;
}

const PlayerContext = createContext<(list: Project[], index: number) => void>(() => {});

export const useOpenPlayer = () => useContext(PlayerContext);

/** Full-screen player for video projects, shared by every grid on the page. */
export function PlayerProvider({ children, caseBase = "/trabajos" }: { children: ReactNode; caseBase?: string }) {
  const [state, setState] = useState<PlayerState | null>(null);
  const opener = useRef<HTMLElement | null>(null);
  const open = useCallback((list: Project[], index: number) => {
    opener.current = document.activeElement as HTMLElement | null;
    pauseAll();
    const videos = list.filter((p) => p.media.kind === "video");
    setState({ list: videos, index: Math.max(0, videos.indexOf(list[index])) });
  }, []);
  const close = useCallback(() => {
    setState(null);
    requestAnimationFrame(() => opener.current?.focus());
  }, []);

  return (
    <PlayerContext.Provider value={open}>
      {children}
      <AnimatePresence>
        {state && (
          <PlayerDialog
            key="player"
            state={state}
            caseBase={caseBase}
            onClose={close}
            onMove={(delta) => setState((s) => (s ? { ...s, index: (s.index + delta + s.list.length) % s.list.length } : s))}
          />
        )}
      </AnimatePresence>
    </PlayerContext.Provider>
  );
}

function PlayerDialog({
  state,
  onClose,
  onMove,
  caseBase,
}: {
  state: PlayerState;
  onClose: () => void;
  onMove: (delta: number) => void;
  caseBase: string;
}) {
  const project = state.list[state.index];
  const slug = project.media.kind === "video" ? project.media.video : "";
  const meta = useMemo(() => videoMeta(slug), [slug]);
  const dialog = useRef<HTMLDivElement>(null);
  const closeBtn = useRef<HTMLButtonElement>(null);
  const reduced = useReducedMotion();
  const vertical = meta.height > meta.width;
  const multiple = state.list.length > 1;

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

  return (
    <motion.div
      className="fixed inset-0 z-[80] flex items-stretch justify-center bg-ink md:items-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.2 } }}
      transition={{ duration: 0.25 }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        ref={dialog}
        role="dialog"
        aria-modal="true"
        aria-label={`Video: ${project.title}`}
        className="relative flex h-full w-full flex-col gap-5 overflow-y-auto px-[var(--gutter)] pb-8 pt-16 md:h-auto md:max-h-[92svh] md:max-w-[1280px] md:flex-row md:items-center md:gap-10 md:overflow-visible md:p-8"
        initial={reduced ? { opacity: 0 } : { opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={reduced ? { opacity: 0 } : { opacity: 0, scale: 0.98, transition: { duration: 0.18 } }}
        transition={{ duration: 0.32, ease: [0.32, 0.72, 0, 1] }}
      >
        <button
          ref={closeBtn}
          type="button"
          onClick={onClose}
          className="press fixed right-3 top-3 z-10 grid size-11 place-items-center rounded-full bg-panel hover:bg-signal md:right-6 md:top-6"
          aria-label="Cerrar video"
        >
          <X size={20} />
        </button>

        <div className={`mx-auto flex w-full shrink-0 justify-center ${vertical ? "md:w-auto" : "md:w-[64%]"}`}>
          <video
            key={slug}
            className="max-h-[72svh] w-auto max-w-full bg-ink md:max-h-[84svh]"
            style={{ aspectRatio: `${meta.width} / ${meta.height}` }}
            poster={posterSrc(slug)}
            controls
            autoPlay
            playsInline
            preload="auto"
          >
            {videoSources(slug).map((s) => (
              <source key={s.type} src={s.src} type={s.type} />
            ))}
          </video>
        </div>

        <div className="w-full min-w-0 md:max-w-sm">
          <p className="text-sm font-semibold text-signal tabular">
            {String(state.index + 1).padStart(2, "0")}
            <span className="text-smoke"> / {String(state.list.length).padStart(2, "0")}</span>
          </p>
          <h2 className="mt-3 text-3xl font-bold leading-tight tracking-[-0.03em] md:text-4xl">{project.title}</h2>
          {(project.client || project.context) && (
            <p className="mt-2 text-sm text-fog">{[project.client, project.context].filter(Boolean).join(" · ")}</p>
          )}
          <p className="body-copy mt-5 text-[0.9375rem]">{project.description}</p>
          <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-4 border-t border-line pt-5 text-sm">
            <div>
              <dt className="text-smoke">Rol</dt>
              <dd className="mt-1">{project.role}</dd>
            </div>
            <div>
              <dt className="text-smoke">Duración</dt>
              <dd className="mt-1 tabular">{formatDuration(meta.duration)}</dd>
            </div>
            {project.tools.length > 0 && (
              <div className="col-span-2">
                <dt className="text-smoke">Herramientas</dt>
                <dd className="mt-1">{project.tools.join(", ")}</dd>
              </div>
            )}
          </dl>
          <div className="mt-7 flex items-center gap-3">
            <Link
              href={`${caseBase}/${project.slug}/`}
              className="press inline-flex h-12 items-center gap-2 border border-white/25 px-5 text-[0.8125rem] font-medium uppercase tracking-[0.06em] hover:border-paper"
            >
              Ver caso <ArrowUpRight aria-hidden size={16} />
            </Link>
            {multiple && (
              <div className="ml-auto flex gap-2">
                <button type="button" onClick={() => onMove(-1)} className="press grid size-12 place-items-center bg-panel hover:bg-panel-2" aria-label="Video anterior">
                  <ArrowLeft size={18} />
                </button>
                <button type="button" onClick={() => onMove(1)} className="press grid size-12 place-items-center bg-panel hover:bg-panel-2" aria-label="Video siguiente">
                  <ArrowRight size={18} />
                </button>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
