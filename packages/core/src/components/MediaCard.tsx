"use client";
import { Expand, Play } from "lucide-react";
import { useState } from "react";
import { formatDuration, pieceSmallSrc, pieceSrcSet, videoMeta } from "../content/media";
import type { Entry } from "../content/types";
import { pad2 } from "../lib/format";
import { useFinePointer } from "../lib/media-query";
import { VideoPreview } from "./VideoPreview";

interface Props {
  entry: Entry;
  onOpen: () => void;
  /**
   * "rail": fixed height set by --rail-h, width from the aspect ratio (capped on phones).
   * "grid": full column width, natural height.
   */
  layout?: "rail" | "grid";
  sizes?: string;
}

/** One video or piece. Videos show their poster and play a muted preview on hover; tapping opens the viewer. */
export function MediaCard({ entry, onOpen, layout = "grid", sizes = "(min-width: 1024px) 25vw, 50vw" }: Props) {
  const { item, chapter, index } = entry;
  const [hover, setHover] = useState(false);
  const fine = useFinePointer();
  const isVideo = item.kind === "video";
  const meta = isVideo ? videoMeta(item.video) : null;
  const ratio = isVideo ? meta!.width / meta!.height : item.image.width / item.image.height;
  const label = `${isVideo ? "Reproducir" : "Ver"} ${item.title}`;

  // Buttons shrink to fit their content, so the grid layout sets the width explicitly.
  const frame =
    layout === "rail"
      ? { aspectRatio: `${ratio}`, height: `min(var(--rail-h), calc(var(--rail-max-w) / ${ratio.toFixed(4)}))` }
      : { aspectRatio: `${ratio}` };

  return (
    <figure className={layout === "rail" ? "shrink-0 snap-start" : "w-full"}>
      <button
        type="button"
        onClick={onOpen}
        onPointerEnter={() => fine && setHover(true)}
        onPointerLeave={() => setHover(false)}
        onFocus={() => fine && setHover(true)}
        onBlur={() => setHover(false)}
        aria-label={label}
        className={`group relative block overflow-hidden bg-panel text-left ${layout === "grid" ? "w-full" : ""}`}
        style={frame}
      >
        <div className={`h-full w-full transition-transform duration-500 ease-[var(--ease-out)] ${hover ? "scale-[1.03]" : ""}`}>
          {isVideo ? (
            <VideoPreview slug={item.video} alt="" active={hover} fill />
          ) : (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={pieceSmallSrc(item.image.file)}
              srcSet={pieceSrcSet(item.image.file)}
              sizes={sizes}
              alt={item.image.alt}
              width={item.image.width}
              height={item.image.height}
              loading="lazy"
              decoding="async"
              className="h-full w-full object-cover"
            />
          )}
        </div>
        {isVideo ? (
          <>
            <span className="absolute left-3 top-3 grid size-9 place-items-center rounded-full bg-ink/70 text-paper transition-colors group-hover:bg-signal">
              <Play aria-hidden size={14} fill="currentColor" />
            </span>
            <span className="absolute bottom-3 right-3 bg-ink/75 px-2 py-1 text-[0.6875rem] tabular text-paper/90">{formatDuration(meta!.duration)}</span>
          </>
        ) : (
          <span className="absolute right-3 top-3 grid size-9 place-items-center rounded-full bg-ink/70 text-paper opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
            <Expand aria-hidden size={14} />
          </span>
        )}
      </button>
      <figcaption className="mt-3 flex items-baseline gap-2 text-[0.8125rem] leading-snug" style={layout === "rail" ? { maxWidth: `min(var(--rail-max-w), calc(var(--rail-h) * ${ratio.toFixed(4)}))` } : undefined}>
        <span className="shrink-0 font-semibold tabular text-signal">
          {pad2(chapter.number)}.{pad2(index + 1)}
        </span>
        <span className="min-w-0 truncate text-fog">{item.title}</span>
      </figcaption>
    </figure>
  );
}
