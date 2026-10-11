import React from "react";
import { captions } from "../data/captions";
import { kf } from "../lib/anim";
import type { TextLook } from "./types";
import { cleanWord, lookStyle } from "./util";

/**
 * Subtítulo "palabra a palabra" centrado (estilo TikTok / Hormozi / podcast clips):
 * muestra la palabra (o grupo de `group` palabras) que se está diciendo, con pop de escala.
 * `highlight`: índices de palabras que van en color de acento (y opcionalmente más grandes).
 */
export const WordPop: React.FC<{
  g: number;
  look: TextLook;
  y: number; // centro vertical en px
  group?: number; // palabras visibles a la vez (1–3 típico)
  highlight?: number[];
  accent?: string;
  accentScale?: number;
  range?: [number, number]; // limitar a un tramo de palabras
  maxWidth?: number;
  popScale?: number;
}> = ({ g, look, y, group = 1, highlight = [], accent = "#FFD400", accentScale = 1.15, range, maxWidth = 900, popScale = 1.25 }) => {
  const ms = g * 1000;
  const [a, b] = range ?? [0, captions.length - 1];
  let cur = -1;
  for (let i = a; i <= b; i++) {
    if (captions[i].startMs <= ms) cur = i;
  }
  if (cur < 0) return null;
  const c = captions[cur];
  const next = captions[cur + 1];
  if (ms > c.endMs + 400 && (!next || next.startMs > ms + 50)) return null; // silencio largo: ocultar
  const start = cur - ((cur - a) % group);
  const ids = Array.from({ length: group }, (_, k) => start + k).filter((i) => i <= b && i <= cur);
  const dt = g - captions[cur].startMs / 1000;
  const s = kf(dt, [0, 0.08], [1 / popScale, 1.04]) - kf(dt, [0.08, 0.16], [0, 0.04]);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: y, translate: "0 -50%", display: "flex", justifyContent: "center" }}>
      <div style={{ maxWidth, display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: "0.25em", textAlign: "center", lineHeight: 1.05, scale: `${s}`, ...lookStyle(look) }}>
        {ids.map((i) => {
          const hl = highlight.includes(i);
          return (
            <span key={i} style={{ display: "inline-block", color: hl ? accent : look.color, scale: hl ? `${accentScale}` : undefined, background: look.background, padding: look.background ? "0.05em 0.2em" : undefined, borderRadius: look.background ? "0.15em" : undefined }}>
              {cleanWord(captions[i].text, { keepPunct: false })}
            </span>
          );
        })}
      </div>
    </div>
  );
};
