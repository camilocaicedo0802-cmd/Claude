"use client";
import { ArrowUpRight, Images, Play } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { formatDuration, pieceSrc, videoMeta } from "../content/media";
import type { Project } from "../content/types";
import { useFinePointer } from "../lib/media-query";
import { pad2 } from "../lib/format";
import { useOpenPlayer } from "./PlayerModal";
import { VideoPreview } from "./VideoPreview";

interface Props {
  project: Project;
  index: number;
  /** List the player can step through. */
  list: Project[];
  caseBase?: string;
}

export function ProjectCard({ project, index, list, caseBase = "/trabajos" }: Props) {
  const [hover, setHover] = useState(false);
  const fine = useFinePointer();
  const openPlayer = useOpenPlayer();
  const href = `${caseBase}/${project.slug}/`;
  const isVideo = project.media.kind === "video";
  const cover = project.media.kind === "images" ? project.media.images[0] : undefined;
  const meta = project.media.kind === "video" ? videoMeta(project.media.video) : undefined;
  const label = `${isVideo ? "Reproducir" : "Ver"} ${project.title}`;

  const media = (
    <div className="relative overflow-hidden">
      <div className={`transition-transform duration-500 ease-[var(--ease-out)] ${hover ? "scale-[1.025]" : ""}`}>
        {project.media.kind === "video" ? (
          <VideoPreview slug={project.media.video} alt="" active={hover} />
        ) : (
          cover && (
            <div className="relative bg-panel" style={{ aspectRatio: `${cover.width} / ${cover.height}` }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={pieceSrc(cover.file)}
                alt=""
                width={cover.width}
                height={cover.height}
                loading="lazy"
                decoding="async"
                className="absolute inset-0 h-full w-full object-cover"
              />
            </div>
          )
        )}
      </div>
      <div aria-hidden className="pointer-events-none absolute inset-0 ring-1 ring-inset ring-white/[0.06]" />
      <span
        aria-hidden
        className={`absolute left-3 top-3 grid size-10 place-items-center rounded-full bg-ink/70 transition-[background-color,transform] duration-200 ${
          hover ? "scale-105 bg-signal" : ""
        }`}
      >
        {isVideo ? <Play size={15} fill="currentColor" className="translate-x-px" /> : <Images size={16} />}
      </span>
      {meta && (
        <span className="absolute bottom-3 right-3 bg-ink/75 px-2 py-1 text-[0.6875rem] font-medium tabular text-paper/90">
          {formatDuration(meta.duration)}
        </span>
      )}
    </div>
  );

  return (
    <article
      className="group"
      onPointerEnter={() => fine && setHover(true)}
      onPointerLeave={() => setHover(false)}
    >
      {isVideo ? (
        <button
          type="button"
          className="block w-full text-left"
          aria-label={label}
          onClick={() => openPlayer(list, list.indexOf(project))}
          onFocus={() => fine && setHover(true)}
          onBlur={() => setHover(false)}
        >
          {media}
        </button>
      ) : (
        <Link href={href} className="block" aria-label={label}>
          {media}
        </Link>
      )}

      <div className="pt-4">
        <p className="flex items-baseline gap-3 text-[0.75rem] font-medium">
          <span className="text-signal tabular">{pad2(index + 1)}</span>
          <span className="text-smoke">{project.categories.join(" / ")}</span>
          {project.year && <span className="ml-auto text-smoke tabular">{project.year}</span>}
        </p>
        <h3 className="mt-2 text-lg font-semibold leading-snug tracking-[-0.015em] md:text-xl">{project.title}</h3>
        {project.client && <p className="mt-0.5 text-sm text-fog">{project.client}</p>}
        <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-smoke">{project.description}</p>
        {project.tools.length > 0 && <p className="mt-2 text-xs text-fog">{project.tools.join(" + ")}</p>}
        <Link
          href={href}
          className="mt-3 inline-flex items-center gap-1.5 text-[0.8125rem] font-medium text-paper underline decoration-white/25 underline-offset-[6px] transition-colors hover:decoration-signal"
        >
          Explorar proyecto <ArrowUpRight aria-hidden size={14} />
        </Link>
      </div>
    </article>
  );
}
