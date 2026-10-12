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

export type ProjectMedia =
  | { kind: "video"; video: string }
  | { kind: "images"; images: ImageAsset[] };

export interface CaseStudy {
  objective?: string;
  need?: string;
  solution?: string;
  process?: string[];
  resources?: string[];
  result?: string;
}

export interface Project {
  slug: string;
  title: string;
  /** Client or brand, only when the source names one. */
  client?: string;
  /** Short line shown under the title, e.g. "Agencia Mente Nueva Marketing". */
  context?: string;
  categories: Category[];
  description: string;
  media: ProjectMedia;
  /** Optional cover image for image projects or override poster for video. */
  cover?: ImageAsset;
  role: string;
  tools: Tool[];
  year?: number;
  metrics?: Metric[];
  /** Lower number = more visible. */
  priority: number;
  /** Which websites show this project. */
  sites: SiteId[];
  /** Original source reference (Drive file id or Canva page). */
  source: string;
  caseStudy?: CaseStudy;
}
