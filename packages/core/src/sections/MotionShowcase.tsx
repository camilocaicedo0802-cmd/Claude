"use client";
import { ArrowUpRight, Play } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { useOpenViewer } from "../components/MediaViewer";
import { RedRule, Reveal } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import { VideoPreview } from "../components/VideoPreview";
import { formatDuration, videoMeta } from "../content/media";
import { entriesOf } from "../content/chapters";
import type { Chapter, Entry } from "../content/types";
import { pad2 } from "../lib/format";
import { useMediaQuery } from "../lib/media-query";

interface Props {
  /** Chapter 01: its videos fill the reel. */
  chapter: Chapter;
  heading: ReactNode[];
  intro: string;
  id?: string;
}

/**
 * Section 02. Desktop: a sticky monitor on the left plays the piece whose row
 * crosses the middle of the screen, morphing its frame to each clip's aspect ratio.
 * Phones: a swipeable strip with the active slide playing.
 */
export function MotionShowcase({ chapter, heading, intro, id = "motion" }: Props) {
  const videos = entriesOf(chapter).filter((e) => e.item.kind === "video");
  const desktop = useMediaQuery("(min-width: 1024px)");
  return (
    <section id={id} aria-labelledby={`${id}-title`} className="relative py-16 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <div className="grid gap-6 md:grid-cols-12">
          <SectionHeading id={`${id}-title`} lines={heading} className="md:col-span-7" />
          <Reveal className="md:col-span-4 md:col-start-9 md:self-end">
            <p className="body-copy">{intro}</p>
          </Reveal>
        </div>
      </div>
      {desktop ? <StickyReel entries={videos} /> : <SwipeReel entries={videos} />}
    </section>
  );
}

function StickyReel({ entries }: { entries: Entry[] }) {
  const [active, setActive] = useState(0);
  const [inSection, setInSection] = useState(false);
  const rows = useRef<(HTMLLIElement | null)[]>([]);
  const wrap = useRef<HTMLDivElement>(null);
  const openViewer = useOpenViewer();
  const reduced = useReducedMotion();

  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) setActive(Number((e.target as HTMLElement).dataset.index));
      },
      { rootMargin: "-45% 0px -45% 0px" },
    );
    rows.current.forEach((r) => r && io.observe(r));
    const sectionIo = new IntersectionObserver(([e]) => setInSection(e.isIntersecting), { threshold: 0.05 });
    if (wrap.current) sectionIo.observe(wrap.current);
    return () => {
      io.disconnect();
      sectionIo.disconnect();
    };
  }, [entries.length]);

  const current = entries[active].item;
  const slug = current.kind === "video" ? current.video : "";
  const meta = videoMeta(slug);
  const ratio = meta.width / meta.height;

  return (
    <div ref={wrap} className="shell mt-16 grid grid-cols-12 gap-6">
      <div className="col-span-5">
        <div className="sticky top-[calc(var(--nav-h)+4vh)] flex h-[calc(100svh-var(--nav-h)-8vh)] items-center justify-center">
          <motion.button
            type="button"
            layout={!reduced}
            transition={{ duration: 0.5, ease: [0.77, 0, 0.175, 1] }}
            onClick={() => openViewer(entries, active)}
            aria-label={`Reproducir ${current.title} con sonido`}
            className="group relative block max-h-full overflow-hidden"
            style={{ aspectRatio: ratio, height: ratio < 1 ? "100%" : "auto", width: ratio < 1 ? "auto" : "100%" }}
          >
            {entries.map(({ item }, i) =>
              item.kind === "video" ? (
                <div
                  key={item.video}
                  className={`absolute inset-0 transition-opacity duration-500 ${i === active ? "opacity-100" : "opacity-0"}`}
                  aria-hidden={i !== active}
                >
                  {Math.abs(i - active) <= 1 && (
                    <VideoPreview slug={item.video} alt="" active={inSection && i === active} fill eager={i === 0} />
                  )}
                </div>
              ) : null,
            )}
            <span className="absolute bottom-4 left-4 flex items-center gap-2 bg-ink/75 px-3 py-2 text-[0.75rem] font-medium uppercase tracking-[0.06em] transition-colors group-hover:bg-signal">
              <Play aria-hidden size={13} fill="currentColor" /> Ver con sonido
            </span>
            <span className="absolute bottom-4 right-4 bg-ink/75 px-2 py-1 text-[0.6875rem] tabular text-paper/90">
              {formatDuration(meta.duration)}
            </span>
          </motion.button>
        </div>
      </div>

      <ol className="col-span-6 col-start-7">
        {entries.map(({ item, chapter }, i) => (
          <li
            key={i}
            ref={(el) => {
              rows.current[i] = el;
            }}
            data-index={i}
            className="flex min-h-[62svh] flex-col justify-center border-t border-line py-12 first:border-t-0"
          >
            <div>
              <p className="flex items-center gap-4 text-sm font-semibold">
                <span className={`tabular text-2xl transition-colors duration-500 ${i === active ? "text-signal" : "text-smoke"}`}>{pad2(i + 1)}</span>
                <span className="text-smoke font-medium">{chapter.categories.join(" / ")}</span>
              </p>
              <h3
                className={`mt-5 text-[clamp(2rem,3.4vw,3.5rem)] font-bold leading-[1.02] tracking-[-0.03em] transition-colors duration-500 ${
                  i === active ? "text-paper" : "text-white/50"
                }`}
              >
                {item.title}
              </h3>
              <p className="mt-3 text-fog">{chapter.context}</p>
              <p className="body-copy mt-6">{item.description ?? chapter.description}</p>
              <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm">
                <span className="text-smoke">
                  Rol: <span className="text-paper">{chapter.role}</span>
                </span>
                {chapter.tools.length > 0 && (
                  <span className="text-smoke">
                    Herramientas: <span className="text-paper">{chapter.tools.join(", ")}</span>
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={() => openViewer(entries, i)}
                className="press mt-8 inline-flex h-12 items-center gap-2 border border-white/25 px-5 text-[0.8125rem] font-medium uppercase tracking-[0.06em] hover:border-paper"
              >
                Reproducir <ArrowUpRight aria-hidden size={15} />
              </button>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

function SwipeReel({ entries }: { entries: Entry[] }) {
  const [active, setActive] = useState(0);
  const strip = useRef<HTMLUListElement>(null);
  const [inView, setInView] = useState(false);
  const openViewer = useOpenViewer();

  useEffect(() => {
    const root = strip.current;
    if (!root) return;
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) setActive(Number((e.target as HTMLElement).dataset.index));
      },
      { root, threshold: 0.6 },
    );
    root.querySelectorAll("li").forEach((li) => io.observe(li));
    const viewIo = new IntersectionObserver(([e]) => setInView(e.isIntersecting), { threshold: 0.5 });
    viewIo.observe(root);
    return () => {
      io.disconnect();
      viewIo.disconnect();
    };
  }, []);

  return (
    <div className="mt-10">
      <ul
        ref={strip}
        className="flex snap-x snap-mandatory gap-3 overflow-x-auto px-[var(--gutter)] pb-4 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        aria-label="Proyectos de motion graphics, desliza para ver más"
      >
        {entries.map(({ item, chapter }, i) => {
          const slug = item.kind === "video" ? item.video : "";
          const vertical = videoMeta(slug).height > videoMeta(slug).width;
          return (
            <li key={slug} data-index={i} className={`shrink-0 snap-center ${vertical ? "w-[72vw] max-w-[340px]" : "w-[86vw] max-w-[560px] self-center"}`}>
              <button type="button" onClick={() => openViewer(entries, i)} className="block w-full text-left" aria-label={`Reproducir ${item.title}`}>
                <VideoPreview slug={slug} alt="" active={inView && i === active} eager={i < 2} />
              </button>
              <p className="mt-3 flex items-baseline gap-3 text-sm">
                <span className="font-semibold text-signal tabular">{pad2(i + 1)}</span>
                <span className="font-semibold">{item.title}</span>
              </p>
              <p className="mt-1 text-xs text-smoke">{chapter.title}</p>
            </li>
          );
        })}
      </ul>
      <div className="shell mt-2 flex items-center gap-3" aria-hidden>
        {entries.map((e, i) => (
          <span key={i} className={`h-[2px] flex-1 transition-colors duration-300 ${i === active ? "bg-signal" : "bg-white/15"}`} />
        ))}
      </div>
    </div>
  );
}
