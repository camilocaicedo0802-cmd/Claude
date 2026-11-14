// Tipos compartidos por todos los videos (motor de edición).
export type Segment = {take: string; idx: number; srcIn: number; srcOut: number; start: number};
export type Word = {text: string; s: number; e: number; seg: number; take: string};
export type Framing = {scale: [number, number]; zoom?: {from: number; to: number; s: number; e: number}};

export type TitleWord = {text: string; at: number};
export type TitleLine = {words: TitleWord[]; color: 'white' | 'purple' | 'chrome'; size: number; upper?: boolean; dx?: number};
export type TitleDef = {
  id: string;
  start: number;
  end: number;
  /** centro vertical en px; 'head' = anclado a la cabeza del plano (solapa `overlap` px detrás de él) */
  y: number | 'head';
  overlap?: number;
  lines: TitleLine[];
  /** en escena: sigue el zoom de cámara y va DETRÁS de la persona */
  scene?: boolean;
  tilt?: number;
  covers: number[];
  /** letras lisas (blanco / morado sin brillo, cromado ni volumen) */
  plain?: boolean;
};

export type BrollDef = {src: string; start: number; end: number; trim?: number; bw?: boolean; zoom?: [number, number]};
export type CardDef = {src: string; start: number; end: number; trim?: number; y: number; width: number; aspect: number; bw?: boolean; rotate?: number};
export type Sfx = {src: string; at: number; vol: number; dur?: number; trim?: number};

export type Spec = {
  id: string;
  clipPrefix: string; // p. ej. 'v9' → clips/v9_<toma>.mp4
  segments: Segment[];
  words: Word[];
  faces: Record<number, [number, number, number, number]>;
  framing: Record<number, Framing>;
  titles: TitleDef[];
  noSubs: [number, number][];
  broll: BrollDef[];
  cards: CardDef[];
  defocus: [number, number][];
  flashes: number[];
  whips: number[];
  pulses: number[];
  music: {src: string; volume: number; stopFrom?: number; stopTo?: number; fadeOutAt: number};
  sfx: Sfx[];
  total: number; // segundos
  end?: {start: number; words: {t: string; at: number}[]};
};
