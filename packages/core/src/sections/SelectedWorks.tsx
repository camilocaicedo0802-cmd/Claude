"use client";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { ProjectCard } from "../components/ProjectCard";
import { RedRule } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import { videoMeta } from "../content/media";
import type { Category, Project } from "../content/types";
import { useMediaQuery } from "../lib/media-query";

interface Props {
  projects: Project[];
  filters: Category[];
  heading?: ReactNode[];
  id?: string;
}

const ALL = "Todos";

/** Height of a card relative to its width, used to balance the columns. */
function relativeHeight(p: Project) {
  if (p.media.kind === "video") {
    const m = videoMeta(p.media.video);
    return m.height / m.width + 0.55;
  }
  const c = p.media.images[0];
  return c.height / c.width + 0.55;
}

/** Distribute items into N columns, each item going to the currently shortest column. */
function toColumns<T>(items: T[], count: number, height: (item: T) => number) {
  const cols: T[][] = Array.from({ length: count }, () => []);
  const heights = new Array(count).fill(0);
  for (const item of items) {
    const i = heights.indexOf(Math.min(...heights));
    cols[i].push(item);
    heights[i] += height(item);
  }
  return cols;
}

export function SelectedWorks({ projects, filters, heading, id = "trabajos" }: Props) {
  const [filter, setFilter] = useState<string>(ALL);
  const reduced = useReducedMotion();
  const xl = useMediaQuery("(min-width: 1280px)");
  const lg = useMediaQuery("(min-width: 1024px)");
  const columnCount = xl ? 4 : lg ? 3 : 2;

  // Only show filters backed by at least one project.
  const available = filters.filter((f) => projects.some((p) => p.categories.includes(f)));
  const visible = useMemo(
    () => (filter === ALL ? projects : projects.filter((p) => p.categories.includes(filter as Category))),
    [filter, projects],
  );
  const columns = useMemo(() => toColumns(visible, columnCount, relativeHeight), [visible, columnCount]);

  return (
    <section id={id} aria-labelledby={`${id}-title`} className="py-24 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <SectionHeading
          id={`${id}-title`}
          lines={heading ?? [<span key="h">Selected <span className="em text-signal">Works.</span></span>]}
        />

        <div className="sticky top-[var(--nav-h)] z-20 -mx-[var(--gutter)] mt-10 bg-ink/95 px-[var(--gutter)] py-3 md:mt-14">
          <div role="group" aria-label="Filtrar proyectos" className="flex gap-2 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {[ALL, ...available].map((f) => {
              const count = f === ALL ? projects.length : projects.filter((p) => p.categories.includes(f as Category)).length;
              const on = filter === f;
              return (
                <button
                  key={f}
                  type="button"
                  aria-pressed={on}
                  onClick={() => setFilter(f)}
                  className={`press relative flex h-10 shrink-0 items-center gap-2 px-4 text-[0.8125rem] font-medium ${
                    on ? "text-paper" : "bg-panel text-fog hover:bg-panel-2 hover:text-paper"
                  }`}
                >
                  {on && (
                    <motion.span
                      layoutId={`${id}-filter`}
                      className="absolute inset-0 bg-signal"
                      transition={{ type: "spring", duration: 0.35, bounce: 0 }}
                    />
                  )}
                  <span className="relative">{f}</span>
                  <span className={`relative tabular text-[0.6875rem] ${on ? "text-paper/85" : "text-fog"}`}>{count}</span>
                </button>
              );
            })}
          </div>
        </div>

        <p className="sr-only" aria-live="polite">
          {visible.length} proyectos{filter === ALL ? "" : ` en ${filter}`}
        </p>

        <div className="mt-8 grid gap-x-4 gap-y-0 md:mt-10 md:gap-x-6" style={{ gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))` }}>
          {columns.map((col, c) => (
            <div key={c} className="flex flex-col gap-10 md:gap-14">
              <AnimatePresence mode="popLayout" initial={false}>
                {col.map((p) => (
                  <motion.div
                    key={p.slug}
                    layout={!reduced}
                    initial={reduced ? { opacity: 0 } : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, transition: { duration: 0.15 } }}
                    transition={{ duration: 0.45, ease: [0.23, 1, 0.32, 1] }}
                  >
                    <ProjectCard project={p} index={projects.indexOf(p)} list={visible} />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
