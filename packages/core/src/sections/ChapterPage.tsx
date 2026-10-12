"use client";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { useMemo } from "react";
import { LongForm, isLongForm } from "../components/LongForm";
import { MediaCard } from "../components/MediaCard";
import { useOpenViewer } from "../components/MediaViewer";
import { Reveal } from "../components/Reveal";
import { RevealText } from "../components/RevealText";
import { SiteLink } from "../components/SiteLink";
import { entriesOf } from "../content/chapters";
import { pieceSmallSrc, posterSrc, videoMeta } from "../content/media";
import type { Chapter, Entry, MediaItem } from "../content/types";
import { pad2 } from "../lib/format";
import { useMediaQuery } from "../lib/media-query";
import { caseHref, homeHref } from "../lib/paths";
import { countLabel } from "./Chapters";

interface Props {
  chapter: Chapter;
  prev: Chapter;
  next: Chapter;
}

/** Cover image of a chapter: its first item. */
export const coverSrc = (item: MediaItem) => (item.kind === "video" ? posterSrc(item.video) : pieceSmallSrc(item.image.file));

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Reveal className="border-t border-line py-8 md:py-10">
      {/* Reveal animates an inner layer, so the grid lives inside it. */}
      <div className="grid gap-3 md:grid-cols-12 md:gap-6">
        <h2 className="text-sm font-semibold text-signal md:col-span-3">{title}</h2>
        <div className="text-lg leading-relaxed text-paper md:col-span-8 md:col-start-5">{children}</div>
      </div>
    </Reveal>
  );
}

const heightOf = (e: Entry) => {
  if (e.item.kind === "video") {
    const m = videoMeta(e.item.video);
    return m.height / m.width + 0.2;
  }
  return e.item.image.height / e.item.image.width + 0.2;
};

/** Distribute items into columns, each to the currently shortest one, so reading order stays left to right. */
function toColumns(items: Entry[], count: number) {
  const cols: { entry: Entry; at: number }[][] = Array.from({ length: count }, () => []);
  const heights = new Array(count).fill(0);
  items.forEach((entry) => {
    const i = heights.indexOf(Math.min(...heights));
    cols[i].push({ entry, at: entry.index });
    heights[i] += heightOf(entry);
  });
  return cols;
}

/** Full chapter: every video and piece of one portfolio folder, with context and links to the neighbours. */
export function ChapterPage({ chapter, prev, next }: Props) {
  const openViewer = useOpenViewer();
  const entries = entriesOf(chapter);
  const grid = entries.filter((e) => !isLongForm(e));
  const long = entries.filter(isLongForm);
  const xl = useMediaQuery("(min-width: 1280px)");
  const md = useMediaQuery("(min-width: 768px)");
  const count = Math.min(grid.length, xl ? 4 : md ? 3 : 2);
  const columns = useMemo(() => toColumns(grid, count), [grid, count]);
  const cs = chapter.caseStudy ?? {};

  return (
    <article className="pt-[var(--nav-h)]">
      <div className="shell pb-10 pt-10 md:pb-14 md:pt-16">
        <SiteLink href={homeHref("#trabajos")} className="inline-flex items-center gap-2 text-sm text-fog hover:text-paper">
          <ArrowLeft aria-hidden size={16} /> Todos los proyectos
        </SiteLink>
        <p className="mt-10 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-sm font-medium">
          <span className="text-signal tabular">{pad2(chapter.number)}</span>
          <span className="text-smoke">{chapter.categories.join(" / ")}</span>
        </p>
        <RevealText as="h1" immediate className="display mt-5 max-w-[16ch]" lines={[chapter.title]} />
        <p className="mt-5 text-lg text-fog">{chapter.context}</p>

        <Reveal className="mt-10 md:mt-14">
          <div className="grid gap-8 md:grid-cols-12 md:gap-6">
            <p className="text-lg leading-relaxed md:col-span-7 md:text-2xl">{chapter.description}</p>
            <dl className="grid grid-cols-2 content-start gap-6 text-sm md:col-span-4 md:col-start-9">
              {chapter.client && (
                <div>
                  <dt className="text-smoke">Cliente</dt>
                  <dd className="mt-1">{chapter.client}</dd>
                </div>
              )}
              <div>
                <dt className="text-smoke">Contenido</dt>
                <dd className="mt-1">{countLabel(chapter)}</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-smoke">Mi rol</dt>
                <dd className="mt-1">{chapter.role}</dd>
              </div>
              {chapter.tools.length > 0 && (
                <div>
                  <dt className="text-smoke">Herramientas</dt>
                  <dd className="mt-1">{chapter.tools.join(", ")}</dd>
                </div>
              )}
              {chapter.year && (
                <div>
                  <dt className="text-smoke">Año</dt>
                  <dd className="mt-1 tabular">{chapter.year}</dd>
                </div>
              )}
            </dl>
          </div>
        </Reveal>
      </div>

      <div className="shell">
        <div className="grid items-start gap-3 md:gap-5" style={{ gridTemplateColumns: `repeat(${count}, minmax(0, 1fr))` }}>
          {columns.map((col, c) => (
            <div key={c} className="flex flex-col gap-7 md:gap-10">
              {col.map(({ entry, at }) => (
                <MediaCard
                  key={at}
                  entry={entry}
                  sizes="(min-width: 1280px) 25vw, (min-width: 768px) 33vw, 50vw"
                  onOpen={() => openViewer(entries, at)}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {long.map((e) => (
        <LongForm key={e.index} entry={e} onOpen={() => openViewer(entries, e.index)} className="mt-14 md:mt-20" />
      ))}

      {(cs.objective || cs.solution || cs.process) && (
        <div className="shell mt-16 md:mt-24">
          {cs.objective && <Block title="Objetivo">{cs.objective}</Block>}
          {cs.need && <Block title="Necesidad del cliente">{cs.need}</Block>}
          {cs.solution && <Block title="Solución creativa">{cs.solution}</Block>}
          {cs.process && cs.process.length > 0 && (
            <Block title="Proceso">
              <ol className="space-y-3">
                {cs.process.map((step, i) => (
                  <li key={step} className="flex gap-4">
                    <span className="text-sm font-semibold text-signal tabular">{pad2(i + 1)}</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </Block>
          )}
          {cs.resources && cs.resources.length > 0 && <Block title="Recursos utilizados">{cs.resources.join(", ")}</Block>}
          {cs.result && <Block title="Resultado final">{cs.result}</Block>}
        </div>
      )}

      <nav aria-label="Más proyectos" className="shell mt-16 grid gap-px border-y border-line bg-line md:mt-24 md:grid-cols-2">
        {[
          { c: prev, label: "Anterior", icon: <ArrowLeft aria-hidden size={18} /> },
          { c: next, label: "Siguiente", icon: <ArrowRight aria-hidden size={18} /> },
        ].map(({ c, label, icon }) => (
          <SiteLink key={label} href={caseHref(c.slug)} className={`group flex items-center gap-5 bg-ink py-8 md:px-6 ${label === "Siguiente" ? "md:flex-row-reverse md:text-right" : ""}`}>
            <span className="w-16 shrink-0 overflow-hidden bg-panel">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={coverSrc(c.items[0])} alt="" loading="lazy" className="aspect-[4/5] w-full object-cover transition-transform duration-500 group-hover:scale-105" />
            </span>
            <span className="min-w-0">
              <span className="flex items-center gap-2 text-sm text-smoke md:inline-flex">
                {icon} {label} · <span className="tabular text-signal">{pad2(c.number)}</span>
              </span>
              <span className="mt-1 block truncate text-xl font-semibold tracking-[-0.02em] group-hover:text-signal md:text-2xl">{c.title}</span>
            </span>
          </SiteLink>
        ))}
      </nav>
    </article>
  );
}
