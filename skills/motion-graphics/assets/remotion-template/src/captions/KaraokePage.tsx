import React, { useMemo } from "react";
import { createTikTokStyleCaptions } from "@remotion/captions";
import { captions } from "../data/captions";
import { kf } from "../lib/anim";
import type { TextLook } from "./types";
import { cleanWord, lookStyle } from "./util";

/**
 * Subtítulo por "páginas" (frase de 2–6 palabras) con la palabra activa resaltada
 * (color, caja o subrayado). Típico de vídeos con persona a cámara y documentales cortos.
 * `combineMs`: cuánto agrupar (ms). Ajústalo para igualar "palabras por bloque" de la referencia.
 */
export const KaraokePage: React.FC<{
  g: number;
  look: TextLook;
  y: number;
  combineMs?: number;
  active?: { mode: "color" | "box" | "underline"; color: string; textColor?: string };
  inactiveOpacity?: number;
  maxWidth?: number;
  enter?: "pop" | "rise" | "none";
}> = ({ g, look, y, combineMs = 1200, active = { mode: "color", color: "#FFD400" }, inactiveOpacity = 1, maxWidth = 880, enter = "pop" }) => {
  const { pages } = useMemo(() => createTikTokStyleCaptions({ captions, combineTokensWithinMilliseconds: combineMs }), [combineMs]);
  const ms = g * 1000;
  const page = pages.find((p, i) => ms >= p.startMs && ms < (pages[i + 1]?.startMs ?? p.startMs + p.durationMs + 300));
  if (!page) return null;
  const dt = (ms - page.startMs) / 1000;
  const e = enter === "pop" ? { scale: `${kf(dt, [0, 0.12], [0.85, 1])}` } : enter === "rise" ? { translate: `0px ${kf(dt, [0, 0.2], [30, 0])}px`, opacity: kf(dt, [0, 0.15], [0, 1]) } : {};
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: y, translate: "0 -50%", display: "flex", justifyContent: "center" }}>
      <div style={{ maxWidth, display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: "0.28em", rowGap: "0.1em", textAlign: "center", lineHeight: 1.1, ...lookStyle(look), ...e }}>
        {page.tokens.map((t, i) => {
          const on = ms >= t.fromMs && ms < t.toMs;
          const said = ms >= t.fromMs;
          const st: React.CSSProperties = { display: "inline-block", opacity: said ? 1 : inactiveOpacity };
          if (on && active.mode === "color") st.color = active.color;
          if (on && active.mode === "box") Object.assign(st, { background: active.color, color: active.textColor ?? look.color, borderRadius: "0.18em", padding: "0 0.18em", margin: "0 -0.18em" });
          if (on && active.mode === "underline") Object.assign(st, { textDecoration: `underline ${active.color}`, textDecorationThickness: "0.12em", textUnderlineOffset: "0.12em" });
          return (
            <span key={i} style={st}>
              {cleanWord(t.text, { keepPunct: false })}
            </span>
          );
        })}
      </div>
    </div>
  );
};
