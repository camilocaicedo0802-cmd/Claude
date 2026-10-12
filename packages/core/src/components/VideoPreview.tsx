"use client";
import { useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { posterSrc, previewSources, videoMeta } from "../content/media";
import { playExclusive, release } from "../lib/playback";

interface Props {
  slug: string;
  alt: string;
  /** Force playback (sticky player, active carousel slide). */
  active?: boolean;
  className?: string;
  /** Fill the parent instead of sizing by the clip's own aspect ratio. */
  fill?: boolean;
  eager?: boolean;
}

/**
 * Poster first; the 6 s muted preview is only fetched the first time it should play.
 * Only one preview plays on the page at a time.
 */
export function VideoPreview({ slug, alt, active = false, className = "", fill = false, eager = false }: Props) {
  const ref = useRef<HTMLVideoElement>(null);
  const [requested, setRequested] = useState(false);
  const [visible, setVisible] = useState(false);
  const reduced = useReducedMotion();
  const meta = videoMeta(slug);
  const shouldPlay = active && !reduced;

  useEffect(() => {
    if (shouldPlay) setRequested(true);
  }, [shouldPlay]);

  useEffect(() => {
    const video = ref.current;
    if (!video || !requested) return;
    if (shouldPlay) playExclusive(video);
    else release(video);
  }, [shouldPlay, requested]);

  return (
    <div
      className={`relative overflow-hidden bg-panel ${fill ? "h-full w-full" : ""} ${className}`}
      style={fill ? undefined : { aspectRatio: `${meta.width} / ${meta.height}` }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={posterSrc(slug)}
        alt={alt}
        width={meta.width}
        height={meta.height}
        loading={eager ? "eager" : "lazy"}
        decoding="async"
        className="absolute inset-0 h-full w-full object-cover"
      />
      {requested && (
        <video
          ref={ref}
          muted
          loop
          playsInline
          preload="auto"
          aria-hidden
          tabIndex={-1}
          onPlaying={() => setVisible(true)}
          onPause={() => setVisible(false)}
          className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-300 ${
            visible && shouldPlay ? "opacity-100" : "opacity-0"
          }`}
        >
          {previewSources(slug).map((s) => (
            <source key={s.type} src={s.src} type={s.type} />
          ))}
        </video>
      )}
    </div>
  );
}
