"use client";
import { Play } from "lucide-react";
import { formatDuration, videoMeta } from "../content/media";
import type { Entry } from "../content/types";
import { MediaCard } from "./MediaCard";

/** A chapter's long-form video (e.g. a full YouTube episode): its own block with label, title and a wide card. */
export function LongForm({ entry, onOpen, className = "" }: { entry: Entry; onOpen: () => void; className?: string }) {
  const { item } = entry;
  if (item.kind !== "video") return null;
  const meta = videoMeta(item.video);
  return (
    // grid-cols-1 (minmax(0, 1fr)) keeps the one-line caption from widening the column on phones.
    <div className={`shell grid grid-cols-1 items-center gap-6 md:grid-cols-12 ${className}`}>
      <div className="min-w-0 md:col-span-4">
        <p className="flex flex-wrap items-center gap-3 text-[0.75rem] font-semibold uppercase tracking-[0.08em]">
          <span className="inline-flex items-center gap-1.5 bg-signal px-2 py-1 text-paper">
            <Play aria-hidden size={11} fill="currentColor" /> {item.longForm?.platform}
          </span>
          <span className="tabular text-smoke">Formato largo · {formatDuration(meta.duration)}</span>
        </p>
        <h4 className="mt-4 text-balance text-[clamp(1.35rem,2.2vw,1.9rem)] font-bold leading-tight tracking-[-0.02em]">{item.title}</h4>
        {item.description && <p className="body-copy mt-3">{item.description}</p>}
      </div>
      <div className="min-w-0 md:col-span-8">
        <MediaCard entry={entry} sizes="(min-width: 768px) 60vw, 100vw" onOpen={onOpen} />
      </div>
    </div>
  );
}

export const isLongForm = (e: Entry) => e.item.kind === "video" && Boolean(e.item.longForm);
