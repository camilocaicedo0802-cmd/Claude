"use client";
import { ArrowLeft, ArrowRight, ArrowUpRight } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { LongForm, isLongForm } from "../components/LongForm";
import { MediaCard } from "../components/MediaCard";
import { useOpenViewer } from "../components/MediaViewer";
import { RedRule, Reveal } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import { SiteLink } from "../components/SiteLink";
import { counts, entriesOf } from "../content/chapters";
import type { Chapter } from "../content/types";
import { pad2 } from "../lib/format";
import { caseHref } from "../lib/paths";

interface Props {
  chapters: Chapter[];
  heading?: ReactNode[];
  intro: string;
  id?: string;
  /** Extra index entries that live elsewhere on the page (e.g. chapter 01 in the motion section). */
  leading?: { href: string; number: number; title: string }[];
}

const anchor = (slug: string) => `capitulo-${slug}`;

export const countLabel = (c: Chapter) => {
  const { videos, pieces } = counts(c);
  return [videos && `${videos} ${videos === 1 ? "video" : "videos"}`, pieces && `${pieces} ${pieces === 1 ? "pieza" : "piezas"}`].filter(Boolean).join(" · ");
};

/**
 * Selected Works as numbered chapters, one per portfolio folder and in its priority order.
 * Each chapter is a horizontal reel of its videos and pieces, so long chapters stay compact on phones.
 */
export function Chapters({ chapters, heading, intro, id = "trabajos", leading = [] }: Props) {
  const [active, setActive] = useState<string | null>(null);
  const index = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) setActive(e.target.id);
      },
      { rootMargin: "-35% 0px -55% 0px" },
    );
    for (const c of chapters) {
      const el = document.getElementById(anchor(c.slug));
      if (el) io.observe(el);
    }
    return () => io.disconnect();
  }, [chapters]);

  // Keep the active chip visible inside the index strip.
  useEffect(() => {
    const strip = index.current;
    const chip = active && strip?.querySelector<HTMLElement>(`[data-target="${active}"]`);
    if (strip && chip) strip.scrollTo({ left: chip.offsetLeft - 16, behavior: "smooth" });
  }, [active]);

  return (
    <section id={id} aria-labelledby={`${id}-title`} className="py-16 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <div className="grid gap-6 md:grid-cols-12">
          <SectionHeading
            id={`${id}-title`}
            lines={heading ?? [<span key="h">Selected <span className="em text-signal">Works.</span></span>]}
            className="md:col-span-7"
          />
          <Reveal className="md:col-span-4 md:col-start-9 md:self-end">
            <p className="body-copy">{intro}</p>
          </Reveal>
        </div>
      </div>

      <nav aria-label="Proyectos" className="sticky top-[var(--nav-h)] z-20 mt-10 border-y border-line bg-ink md:mt-14">
        <div ref={index} className="shell flex gap-1 overflow-x-auto py-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {[...leading, ...chapters.map((c) => ({ href: `#${anchor(c.slug)}`, number: c.number, title: c.title }))].map((c) => {
            const on = active === c.href.slice(1);
            return (
              <a
                key={c.href}
                href={c.href}
                data-target={c.href.slice(1)}
                aria-current={on ? "true" : undefined}
                className={`flex h-10 shrink-0 items-center gap-2 whitespace-nowrap px-3 text-[0.8125rem] font-medium transition-colors duration-200 ${
                  on ? "bg-signal text-paper" : "text-fog hover:bg-panel hover:text-paper"
                }`}
              >
                <span className={`tabular text-[0.6875rem] ${on ? "text-paper/85" : "text-signal"}`}>{pad2(c.number)}</span>
                {c.title}
              </a>
            );
          })}
        </div>
      </nav>

      <div className="mt-6 md:mt-10">
        {chapters.map((c) => (
          <ChapterReel key={c.slug} chapter={c} />
        ))}
      </div>
    </section>
  );
}

function ChapterReel({ chapter }: { chapter: Chapter }) {
  const rail = useRef<HTMLDivElement>(null);
  const [edges, setEdges] = useState({ start: true, end: false });
  const openViewer = useOpenViewer();
  const entries = entriesOf(chapter);
  // Long-form videos get their own block under the reel; the viewer still steps through the whole chapter.
  const reel = entries.filter((e) => !isLongForm(e));
  const long = entries.filter(isLongForm);

  const update = () => {
    const el = rail.current;
    if (!el) return;
    setEdges({ start: el.scrollLeft < 8, end: el.scrollLeft + el.clientWidth > el.scrollWidth - 8 });
  };
  useEffect(update, []);

  const scrollBy = (dir: 1 | -1) => {
    const el = rail.current;
    if (el) el.scrollBy({ left: dir * el.clientWidth * 0.8, behavior: "smooth" });
  };

  return (
    <article id={anchor(chapter.slug)} aria-labelledby={`${anchor(chapter.slug)}-title`} className="scroll-mt-[calc(var(--nav-h)+4rem)] border-b border-line py-12 md:py-16">
      <div className="shell grid gap-5 md:grid-cols-12 md:gap-6">
        <div className="md:col-span-5">
          <p className="flex items-baseline gap-3 text-sm font-medium text-smoke">
            <span className="text-[2.5rem] font-bold leading-none tracking-[-0.04em] tabular text-signal md:text-[3.5rem]">{pad2(chapter.number)}</span>
            <span>{countLabel(chapter)}</span>
          </p>
          <h3 id={`${anchor(chapter.slug)}-title`} className="mt-4 text-[clamp(1.75rem,3.2vw,2.75rem)] font-bold leading-[1.05] tracking-[-0.03em]">
            {chapter.title}
          </h3>
          <p className="mt-2 text-fog">{chapter.context}</p>
        </div>
        <div className="flex min-w-0 flex-col gap-5 md:col-span-6 md:col-start-7">
          <p className="body-copy line-clamp-4 md:line-clamp-none">{chapter.description}</p>
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
            <SiteLink
              href={caseHref(chapter.slug)}
              className="inline-flex items-center gap-1.5 text-[0.8125rem] font-medium uppercase tracking-[0.06em] text-paper underline decoration-signal underline-offset-[6px] hover:decoration-paper"
            >
              Ver proyecto completo <ArrowUpRight aria-hidden size={15} />
            </SiteLink>
            {reel.length > 2 && (
              <div className="ml-auto hidden gap-2 md:flex">
                <button type="button" onClick={() => scrollBy(-1)} disabled={edges.start} className="press grid size-11 place-items-center bg-panel hover:bg-panel-2 disabled:opacity-30" aria-label={`Anteriores de ${chapter.title}`}>
                  <ArrowLeft size={18} />
                </button>
                <button type="button" onClick={() => scrollBy(1)} disabled={edges.end} className="press grid size-11 place-items-center bg-panel hover:bg-panel-2 disabled:opacity-30" aria-label={`Siguientes de ${chapter.title}`}>
                  <ArrowRight size={18} />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div
        ref={rail}
        onScroll={update}
        className="rail mt-8 flex snap-x snap-mandatory items-start gap-3 overflow-x-auto pb-2 [scrollbar-width:none] md:mt-10 md:gap-4 [&::-webkit-scrollbar]:hidden"
        aria-label={`${chapter.title}: ${countLabel(chapter)}. Desliza para ver más.`}
        role="region"
      >
        {reel.map((e) => (
          <MediaCard key={e.index} entry={e} layout="rail" sizes="(min-width: 768px) 360px, 60vw" onOpen={() => openViewer(entries, e.index)} />
        ))}
      </div>

      {long.map((e) => (
        <LongForm key={e.index} entry={e} onOpen={() => openViewer(entries, e.index)} className="mt-10 md:mt-14" />
      ))}
    </article>
  );
}
