import type React from "react";
import { captions } from "../data/captions";
import type { TextLook } from "./types";

export const wordsIn = (r?: [number, number]) => (r ? captions.slice(r[0], r[1] + 1).map((c, i) => ({ ...c, idx: r[0] + i })) : []);

/** Limpia puntuación final para el render (la referencia decide si se muestra). */
export const cleanWord = (s: string, opts: { keepPunct?: boolean; lower?: boolean } = {}) => {
  let w = s.trim();
  if (!opts.keepPunct) w = w.replace(/[.,;:!?¡¿…]/g, "");
  return opts.lower ? w.toLowerCase() : w;
};

export const lookStyle = (l: TextLook): React.CSSProperties => ({
  fontFamily: l.font,
  fontWeight: l.weight,
  fontSize: l.size,
  color: l.color,
  letterSpacing: l.tracking,
  textTransform: l.uppercase ? "uppercase" : "none",
  WebkitTextStroke: l.stroke,
  paintOrder: l.stroke ? "stroke fill" : undefined,
  textShadow: l.shadow,
});

export const aberrationShadow = (k: number) => (k > 0 ? `-${k * 4}px 0 rgba(0,170,255,${k}), ${k * 4}px 0 rgba(255,110,30,${k})` : undefined);
