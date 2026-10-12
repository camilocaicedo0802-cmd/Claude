export type SiteId = "editor" | "disenador";

export type Category =
  | "Motion Graphics"
  | "Video Editing"
  | "Reels & Short Form"
  | "Commercial Ads"
  | "Social Media"
  | "Visual Design"
  | "Campañas con IA";

export type Tool =
  | "After Effects"
  | "Premiere Pro"
  | "Illustrator"
  | "Photoshop"
  | "Canva"
  | "CapCut"
  | "ElevenLabs"
  | "Midjourney"
  | "ChatGPT"
  | "Claude"
  | "Google Ads"
  | "TikTok Ads"
  | "Hootsuite"
  | "Notion";

/** A verified number taken from the portfolio sources. */
export interface Metric {
  value: number;
  label: string;
  /** Where the number comes from and the period it covers. */
  context: string;
  /** Format hint for the counter. */
  format?: "integer" | "compact";
  suffix?: string;
}

export interface ImageAsset {
  /** File name inside media/out/pieces (without extension). */
  file: string;
  alt: string;
  width: number;
  height: number;
}

export interface CaseStudy {
  objective?: string;
  need?: string;
  solution?: string;
  process?: string[];
  resources?: string[];
  result?: string;
}

/** One video inside a chapter. `video` is a slug from media/selection.json. */
export interface VideoItem {
  kind: "video";
  video: string;
  title: string;
  /** Optional detail shown in the motion showcase and the chapter page. */
  description?: string;
  /** Long-form piece (e.g. a full YouTube episode), shown in its own block instead of the reel. */
  longForm?: { platform: string };
}

/** One graphic piece inside a chapter. */
export interface ImageItem {
  kind: "image";
  image: ImageAsset;
  title: string;
  description?: string;
}

export type MediaItem = VideoItem | ImageItem;

/**
 * A chapter is one numbered folder of the portfolio (a client or a body of work).
 * The folder number is the priority: 1 is the most important.
 */
export interface Chapter {
  slug: string;
  number: number;
  title: string;
  /** Client or brand, only when the source names one. */
  client?: string;
  /** Short line shown under the title. */
  context: string;
  categories: Category[];
  description: string;
  role: string;
  tools: Tool[];
  year?: number;
  /** Ordered media. The editor site keeps only the videos. */
  items: MediaItem[];
  caseStudy?: CaseStudy;
  /** Original source reference (Drive folder). */
  source: string;
}

/** A media item with the chapter it belongs to, as shown by cards and the viewer. */
export interface Entry {
  item: MediaItem;
  chapter: Chapter;
  /** Position inside the chapter, 0-based. */
  index: number;
}
