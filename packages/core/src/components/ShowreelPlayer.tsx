"use client";
import { Pause, Play, Volume2, VolumeX } from "lucide-react";
import { useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { posterSrc, videoMeta, videoSources } from "../content/media";

interface Props {
  slug: string;
  label: string;
  /** Short on-screen label while playing. */
  tag?: string;
  className?: string;
}

/**
 * Hero player: autoplays muted and loops when allowed, with accessible
 * play/pause and sound toggles and a red playhead bar.
 */
export function ShowreelPlayer({ slug, label, tag = "Showreel", className = "" }: Props) {
  const ref = useRef<HTMLVideoElement>(null);
  const bar = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(true);
  const reduced = useReducedMotion();
  const meta = videoMeta(slug);

  useEffect(() => {
    const video = ref.current;
    if (!video) return;
    if (reduced) {
      video.pause();
      return;
    }
    video.muted = true;
    const p = video.play();
    if (p) p.catch(() => setPlaying(false));
  }, [reduced]);

  // Pause when scrolled out of view to free the decoder; resume when back.
  useEffect(() => {
    const video = ref.current;
    if (!video) return;
    const io = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) video.pause();
      else if (video.dataset.wanted === "1") video.play().catch(() => {});
    });
    io.observe(video);
    return () => io.disconnect();
  }, []);

  const toggle = () => {
    const video = ref.current;
    if (!video) return;
    if (video.paused) {
      video.dataset.wanted = "1";
      video.play().catch(() => {});
    } else {
      video.dataset.wanted = "0";
      video.pause();
    }
  };

  const toggleSound = () => {
    const video = ref.current;
    if (!video) return;
    video.muted = !video.muted;
    setMuted(video.muted);
    if (!video.muted && video.paused) {
      video.dataset.wanted = "1";
      video.play().catch(() => {});
    }
  };

  return (
    <figure className={`relative overflow-hidden bg-panel ${className}`} style={{ aspectRatio: `${meta.width} / ${meta.height}` }}>
      <video
        ref={ref}
        className="absolute inset-0 h-full w-full object-cover"
        poster={posterSrc(slug)}
        muted
        loop
        playsInline
        autoPlay={!reduced}
        preload="auto"
        data-wanted={reduced ? "0" : "1"}
        aria-label={label}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onTimeUpdate={(e) => {
          const v = e.currentTarget;
          if (bar.current && v.duration) bar.current.style.transform = `scaleX(${v.currentTime / v.duration})`;
        }}
      >
        {videoSources(slug).map((s) => (
          <source key={s.type} src={s.src} type={s.type} />
        ))}
      </video>
      <div aria-hidden className="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-ink/80 to-transparent" />
      <figcaption className="absolute inset-x-0 bottom-0 flex items-center gap-3 p-3 sm:p-4">
        <button
          type="button"
          onClick={toggle}
          className="press grid size-11 shrink-0 place-items-center rounded-full bg-paper text-ink hover:bg-signal hover:text-paper"
          aria-label={playing ? "Pausar video" : "Reproducir video"}
        >
          {playing ? <Pause size={18} fill="currentColor" /> : <Play size={18} fill="currentColor" className="translate-x-px" />}
        </button>
        <button
          type="button"
          onClick={toggleSound}
          className="press grid size-11 shrink-0 place-items-center rounded-full border border-white/30 bg-ink/40 hover:border-paper"
          aria-label={muted ? "Activar sonido" : "Silenciar"}
          aria-pressed={!muted}
        >
          {muted ? <VolumeX size={18} /> : <Volume2 size={18} />}
        </button>
        <div className="relative h-[2px] flex-1 bg-white/20" aria-hidden>
          <div ref={bar} className="absolute inset-0 origin-left scale-x-0 bg-signal" />
        </div>
        <span className="text-[0.6875rem] font-medium uppercase tracking-[0.08em] text-paper/80">
          {playing ? tag : "En pausa"}
        </span>
      </figcaption>
    </figure>
  );
}
