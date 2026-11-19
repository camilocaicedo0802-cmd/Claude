import raw from "./data/edl.json";

export type ZoomKey = { f: number; s: number; ox: number; oy: number };
/** Toma en la línea de tiempo: sale del clip `clip` a partir de su fotograma `clipStart`. */
export type Segment = {
  id: string;
  clip: string;
  file: string;
  fg: string;
  wav: string;
  clipStart: number;
  from_: number;
  dur: number;
  zoom: ZoomKey[];
};
export type Shot = { file: string; from_: number; dur: number; label: string };
export type Highlight = {
  kicker: string | null;
  big: string;
  kFrom: number | null;
  bFrom: number;
  to: number;
  style: "red" | "white";
  behind: boolean;
  kickerItalic: boolean;
  layout: { align: "left" | "center" | "right"; x: number; kickerY: number; bigY: number; size: number };
};
export type SubBlock = { words: { text: string; f: number }[]; start: number; end: number };
export type Card = { file: string; from_: number; to: number; x: number; y: number; w: number; h: number; rot: number; label: string };
export type Transition = { at: number; kind: "blur" | "leak"; out: number; inn: number };
export type Sfx = { file: string; from_: number; db: number };

export type Edl = {
  fps: number;
  total: number;
  segments: Segment[];
  montage: Shot[];
  vo: { file: string; from_: number; src: number };
  highlights: Highlight[];
  subtitles: SubBlock[];
  cards: Card[];
  neon: { pops: number[]; collapse: number; end: number; y: number };
  transitions: Transition[];
  sfx: Sfx[];
  music: { file: string; songStart: number; keys: { f: number; db: number }[] };
};

export const EDL = raw as unknown as Edl;

/** Fotogramas en los que hay un corte de plano (para no hacer fundidos de salida encima). */
export const CUTS = new Set<number>([
  ...EDL.segments.map((s) => s.from_ + s.dur),
  ...EDL.montage.map((m) => m.from_ + m.dur),
]);

export const segmentAt = (frame: number): Segment | undefined =>
  EDL.segments.find((s) => frame >= s.from_ && frame < s.from_ + s.dur);

export const dbToGain = (db: number) => Math.pow(10, db / 20);

/** Interpola escala y origen del reencuadre de un segmento en su fotograma local. */
export const zoomAt = (seg: Segment, local: number) => {
  const k = seg.zoom;
  if (local <= k[0].f) return k[0];
  for (let i = 0; i < k.length - 1; i++) {
    const a = k[i];
    const b = k[i + 1];
    if (local >= a.f && local <= b.f) {
      const t = b.f === a.f ? 1 : (local - a.f) / (b.f - a.f);
      return { f: local, s: a.s + (b.s - a.s) * t, ox: a.ox + (b.ox - a.ox) * t, oy: a.oy + (b.oy - a.oy) * t };
    }
  }
  return k[k.length - 1];
};

/** Pseudoaleatorio determinista (mismo resultado en cada render). */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};
