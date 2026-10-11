import React from "react";
import { random } from "remotion";
import { kcolor, kf } from "../lib/anim";
import type { Reveal, TextLook } from "./types";
import { aberrationShadow, cleanWord, lookStyle, wordsIn } from "./util";

/**
 * Subtítulo editorial de DOS NIVELES colocado junto al objeto del que habla la frase:
 *  - guía (rango de palabras) que aparece palabra a palabra, sincronizada con la voz
 *  - palabra(s) clave que entran en el frame exacto en que se pronuncian
 * Todo el aspecto viene de `look` (ver CAPTION_LOOKS en theme.ts), medido en estilo.md.
 */
export type EditorialLook = { guide: TextLook; key: TextLook; keyFrom: string; reveal: Reveal; aberration: number; guideAbove?: boolean };

export const EditorialBlock: React.FC<{
  g: number; // tiempo global (s)
  look: EditorialLook;
  guide?: [number, number];
  keyw: [number, number];
  x: number;
  y: number;
  width?: number;
  align?: "left" | "right" | "center";
  exitAt?: number; // segundo global de salida (desenfoque + subida)
  keySize?: number;
  guideSize?: number;
  jitter?: number; // irregularidad de línea base en la guía (px)
  lower?: boolean;
}> = ({ g, look, guide, keyw, x, y, width = 820, align = "left", exitAt, keySize, guideSize, jitter = 12, lower = true }) => {
  const gw = wordsIn(guide);
  const kw = wordsIn(keyw);
  const first = (gw[0] ?? kw[0]).startMs / 1000;
  if (g < first - 0.05) return null;
  const exitP = exitAt !== undefined ? kf(g, [exitAt, exitAt + 0.28], [0, 1]) : 0;
  if (exitP >= 1) return null;
  const justify = align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";
  const left = align === "right" ? x - width : align === "center" ? x - width / 2 : x;
  const gl = { ...look.guide, size: guideSize ?? look.guide.size };
  const kl = { ...look.key, size: keySize ?? look.key.size };
  const ab = aberrationShadow(look.aberration);

  const guideLine = gw.length > 0 && (
    <div key="g" style={{ display: "flex", flexWrap: "wrap", justifyContent: justify, columnGap: "0.26em", lineHeight: 1.2, ...lookStyle(gl), textShadow: gl.shadow ?? ab }}>
      {gw.map((w) => {
        const dt = g - w.startMs / 1000;
        const txt = cleanWord(w.text, { lower });
        if (dt < 0) return <span key={w.idx} style={{ opacity: 0 }}>{txt}</span>;
        const j = (random(`base-${w.idx}`) - 0.5) * jitter;
        return (
          <span key={w.idx} style={{ display: "inline-block", opacity: kf(dt, [0, 0.2], [0, 1]), filter: `blur(${kf(dt, [0, 0.2], [8, 0])}px)`, translate: `0px ${kf(dt, [0, 0.22], [12, 0]) + j}px` }}>
            {txt}
          </span>
        );
      })}
    </div>
  );

  const keyLine = (
    <div key="k" style={{ display: "flex", flexWrap: "wrap", justifyContent: justify, columnGap: "0.24em", lineHeight: 1.05, marginTop: look.guideAbove === false ? 0 : -gl.size * 0.12, ...lookStyle(kl) }}>
      {kw.map((w) => {
        const dt = g - w.startMs / 1000;
        const txt = cleanWord(w.text, { lower });
        if (dt < 0) return <span key={w.idx} style={{ opacity: 0 }}>{txt}</span>;
        const base: React.CSSProperties = { display: "inline-block", textShadow: kl.shadow ?? ab, background: kl.background, padding: kl.background ? "0 0.15em" : undefined };
        switch (look.reveal) {
          case "wipe": {
            const p = kf(dt, [0, 0.36], [-40, 110]);
            const done = dt > 0.4;
            const m = `linear-gradient(90deg, black ${p}%, transparent ${p + 35}%)`;
            // el padding evita que la máscara recorte ascendentes/descendentes (p, j, g)
            return (
              <span key={w.idx} style={{ ...base, filter: done ? undefined : `blur(${kf(dt, [0, 0.36], [12, 0])}px)`, WebkitMaskImage: done ? undefined : m, maskImage: done ? undefined : m, padding: "0.3em 0.14em 0.42em 0.1em", margin: "-0.3em -0.14em -0.42em -0.1em" }}>
                {txt}
              </span>
            );
          }
          case "pop":
            return <span key={w.idx} style={{ ...base, scale: `${kf(dt, [0, 0.12], [0.6, 1.08]) - kf(dt, [0.12, 0.22], [0, 0.08])}`, opacity: kf(dt, [0, 0.06], [0, 1]) }}>{txt}</span>;
          case "fade":
            return <span key={w.idx} style={{ ...base, opacity: kf(dt, [0, 0.25], [0, 1]) }}>{txt}</span>;
          case "none":
            return <span key={w.idx} style={base}>{txt}</span>;
          case "typewriter": {
            const n = Math.floor(kf(dt, [0, Math.max(0.15, (w.endMs - w.startMs) / 1000)], [0, txt.length]));
            return <span key={w.idx} style={base}>{txt.slice(0, Math.max(1, n))}</span>;
          }
          default: // "rise": sube y pasa de gris a tinta
            return (
              <span key={w.idx} style={{ ...base, opacity: kf(dt, [0, 0.1], [0, 1]), color: kcolor(dt, [0, 0.3], [look.keyFrom, kl.color]), translate: `0px ${kf(dt, [0, 0.35], [35, 0])}px` }}>
                {txt}
              </span>
            );
        }
      })}
    </div>
  );

  return (
    <div style={{ position: "absolute", left, top: y, width, display: "flex", flexDirection: "column", alignItems: justify, opacity: 1 - exitP, filter: exitP > 0 ? `blur(${exitP * 12}px)` : undefined, translate: `0px ${-exitP * 40}px` }}>
      {look.guideAbove === false ? [keyLine, guideLine] : [guideLine, keyLine]}
    </div>
  );
};
