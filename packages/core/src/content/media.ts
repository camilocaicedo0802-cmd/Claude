import manifest from "../../../../media/out/manifest.json";

export interface VideoMeta {
  width: number;
  height: number;
  duration: number;
  audio: boolean;
  /** True when a full-length WebM fallback exists. */
  webm?: boolean;
  bytes: number;
  previewBytes: number;
}

const videos = manifest as Record<string, VideoMeta>;

/** Base URL for media. Point NEXT_PUBLIC_MEDIA_BASE to a CDN to serve videos from there. */
export const MEDIA_BASE = (process.env.NEXT_PUBLIC_MEDIA_BASE ?? "/media").replace(/\/$/, "");

export function videoMeta(slug: string): VideoMeta {
  const meta = videos[slug];
  if (!meta) throw new Error(`Unknown video "${slug}". Add it to media/selection.json and run npm run media:build.`);
  return meta;
}

export const videoSrc = (slug: string) => `${MEDIA_BASE}/videos/${slug}.mp4`;
export const previewSrc = (slug: string) => `${MEDIA_BASE}/previews/${slug}.mp4`;

/** MP4 (H.264) first, VP9 WebM as fallback for browsers built without H.264. */
export const videoSources = (slug: string) => [
  { src: `${MEDIA_BASE}/videos/${slug}.mp4`, type: "video/mp4" },
  ...(videos[slug]?.webm ? [{ src: `${MEDIA_BASE}/videos/${slug}.webm`, type: "video/webm" }] : []),
];
export const previewSources = (slug: string) => [
  { src: `${MEDIA_BASE}/previews/${slug}.mp4`, type: "video/mp4" },
  { src: `${MEDIA_BASE}/previews/${slug}.webm`, type: "video/webm" },
];
export const posterSrc = (slug: string) => `${MEDIA_BASE}/posters/${slug}.webp`;
export const pieceSrc = (file: string) => `${MEDIA_BASE}/pieces/${file}.webp`;

export function aspectOf(slug: string) {
  const { width, height } = videoMeta(slug);
  return width / height;
}

export function orientationOf(slug: string): "vertical" | "horizontal" | "square" {
  const ratio = aspectOf(slug);
  if (ratio < 0.9) return "vertical";
  if (ratio > 1.1) return "horizontal";
  return "square";
}

export function formatDuration(seconds: number) {
  const s = Math.round(seconds);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
