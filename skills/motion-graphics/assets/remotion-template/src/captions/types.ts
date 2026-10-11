export type TextLook = {
  font: string;
  weight: number;
  size: number;
  color: string;
  tracking: string;
  uppercase: boolean;
  stroke?: string; // p. ej. "6px #000" (contorno, típico de subtítulos tipo meme/TikTok)
  shadow?: string; // CSS text-shadow
  background?: string; // caja detrás del texto (color)
};
export type Reveal = "rise" | "wipe" | "pop" | "fade" | "typewriter" | "none";
