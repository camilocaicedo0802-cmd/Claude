"use client";
import { ArrowUpRight } from "lucide-react";
import type { ReactNode } from "react";
import { RedRule, Reveal } from "../components/Reveal";
import { SectionHeading } from "../components/SectionHeading";
import { SiteLink } from "../components/SiteLink";
import { pieceSrc } from "../content/media";
import type { ImageAsset, Project } from "../content/types";
import { pad2 } from "../lib/format";
import { caseHref } from "../lib/paths";

interface Tile {
  project: Project;
  /** How many images of the project to lay side by side inside the tile. */
  show: number;
  span: string;
}

interface Props {
  tiles: Tile[];
  heading: ReactNode[];
  intro: string;
}

/** Gallery wall: real pieces matted on charcoal panels, same height per row, never cropped. */
export function FeaturedPieces({ tiles, heading, intro }: Props) {
  return (
    <section id="piezas" aria-labelledby="piezas-title" className="py-24 md:py-36">
      <div className="shell">
        <RedRule className="mb-10 md:mb-14" />
        <div className="grid gap-6 md:grid-cols-12">
          <SectionHeading id="piezas-title" lines={heading} className="md:col-span-7" />
          <Reveal className="md:col-span-4 md:col-start-9 md:self-end">
            <p className="body-copy">{intro}</p>
          </Reveal>
        </div>
        <div className="mt-12 grid gap-4 md:mt-16 md:grid-cols-12 md:gap-6">
          {tiles.map((t, i) => (
            <Reveal key={t.project.slug} variant="wipe" delay={(i % 2) * 0.08} className={t.span}>
              <PieceTile tile={t} index={i} />
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

function PieceTile({ tile, index }: { tile: Tile; index: number }) {
  const { project } = tile;
  const images: ImageAsset[] = project.media.kind === "images" ? project.media.images.slice(0, tile.show) : [];
  return (
    <SiteLink href={caseHref(project.slug)} className="group block" aria-label={`Ver proyecto ${project.title}`}>
      <div className="relative flex aspect-[4/5] items-center justify-center gap-3 overflow-hidden bg-panel p-5 transition-colors duration-300 group-hover:bg-panel-2 sm:aspect-[4/3] sm:p-8 md:aspect-auto md:h-[clamp(320px,36vw,540px)] md:gap-4 md:p-10">
        {images.map((im) => (
          <div key={im.file} className="min-w-0" style={{ flex: `${im.width / im.height} 1 0%` }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={pieceSrc(im.file)}
              alt={im.alt}
              width={im.width}
              height={im.height}
              loading="lazy"
              decoding="async"
              className="mx-auto h-auto max-h-[100%] w-full object-contain shadow-[0_18px_40px_rgba(0,0,0,0.45)] transition-transform duration-500 ease-[var(--ease-out)] group-hover:scale-[1.02]"
            />
          </div>
        ))}
        <span className="absolute right-4 top-4 grid size-10 place-items-center rounded-full bg-ink/70 opacity-0 transition-opacity duration-200 group-hover:opacity-100 group-focus-visible:opacity-100">
          <ArrowUpRight aria-hidden size={18} />
        </span>
      </div>
      <div className="mt-4 flex items-baseline gap-3">
        <span className="text-sm font-semibold text-signal tabular">{pad2(index + 1)}</span>
        <div>
          <h3 className="text-lg font-semibold tracking-[-0.015em] md:text-xl">{project.title}</h3>
          <p className="text-sm text-fog">{[project.client, project.context].filter(Boolean).join(" · ")}</p>
        </div>
      </div>
    </SiteLink>
  );
}

/** Two real pieces floating behind the hero video (desktop only). */
export function HeroPieces({ pieces }: { pieces: ImageAsset[] }) {
  const [a, b] = pieces;
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 hidden lg:block">
      {a && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={pieceSrc(a.file)}
          alt=""
          className="absolute -left-[46%] top-[6%] w-[52%] opacity-90 shadow-[0_24px_60px_rgba(0,0,0,0.6)]"
        />
      )}
      {b && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={pieceSrc(b.file)}
          alt=""
          className="absolute -left-[30%] bottom-[4%] w-[44%] opacity-90 shadow-[0_24px_60px_rgba(0,0,0,0.6)]"
        />
      )}
    </div>
  );
}
