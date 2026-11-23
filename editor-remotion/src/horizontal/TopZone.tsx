// Zona superior de la opción B: titular de capítulo tecleado y palabra clave gigante que asoma detrás de la ventana.
import React from "react";
import { AbsoluteFill, Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { ramp } from "../anim";
import { BehindBlockT, Words } from "../components/Captions";
import { C, FONT, W } from "../theme";
import { HEAD_TOP, WIN, keywordPx, winY } from "./layout";

// ───────────────────────── Titular de capítulo ─────────────────────────
export type HeadlineT = { start: number; end: number; eyebrow: string; text: string; typed?: boolean };
export const TYPE_CPS = 20; // 1 letra cada 3 fotogramas

export const Headline: React.FC<{ h: HeadlineT }> = ({ h }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < h.start || t >= h.end) return null;
  const typedMode = h.typed !== false;
  const inP = ramp(t, h.start, typedMode ? 0.2 : 0.3);
  const outP = 1 - ramp(t, h.end - 0.15, 0.15);
  const n = typedMode ? Math.max(0, Math.min(h.text.length, Math.floor((t - h.start - 0.12) * TYPE_CPS))) : h.text.length;
  const typing = n < h.text.length;
  const caretOn = typedMode && t < h.start + 0.12 + h.text.length / TYPE_CPS + 1.4 && (typing || Math.floor((t - h.start) * 2.5) % 2 === 0);
  return (
    <div style={{ position: "absolute", left: 0, top: HEAD_TOP, width: W, textAlign: "center", opacity: inP * outP, translate: typedMode ? undefined : `0px ${10 * (1 - inP)}px` }}>
      <div style={{ display: "inline-flex", alignItems: "center", gap: 14, fontFamily: FONT.wide, fontWeight: 400, fontSize: 25, letterSpacing: "0.24em", color: "rgba(255,255,255,0.72)", textTransform: "uppercase" }}>
        <span style={{ width: 11, height: 11, borderRadius: 11, background: C.accent, boxShadow: `0 0 14px ${C.accentGlow}` }} />
        {h.eyebrow}
      </div>
      <div style={{ marginTop: 16, fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 86, letterSpacing: "-0.045em", lineHeight: 1, color: C.white, whiteSpace: "nowrap" }}>
        {h.text.slice(0, n)}
        <span style={{ display: "inline-block", width: 5, height: 70, marginLeft: 6, verticalAlign: "-6px", background: C.accent, opacity: caretOn ? 1 : 0 }} />
        <span style={{ opacity: 0 }}>{h.text.slice(n)}</span>
      </div>
    </div>
  );
};

// ───────────────────────── Palabra clave gigante (detrás de la ventana y de la cabeza) ─────────────────────────
const ACCENT: [number, number, number] = [255, 222, 33];
const mixWhite = (p: number) => `rgb(${ACCENT.map((c) => Math.round(c + (255 - c) * p)).join(",")})`;
const TUCK = 0.035; // la base de la palabra se mete un 3,5 % de su tamaño por detrás del borde superior de la ventana
// Métricas de Inter Tight 700 con interlineado 0,86: línea base y altura de mayúscula respecto a la caja.
const BASELINE = 0.794;
const CAP_TOP = 0.067;

export const KeywordTop: React.FC<{ block: BehindBlockT }> = ({ block }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < block.start || t >= block.end) return null;
  const text = block.big.map((w) => w.text).join(" ");
  const px = keywordPx(text);
  const top = winY(t) + (TUCK - BASELINE) * px;
  const life = Math.min(1, (t - block.start) / Math.max(0.4, block.end - block.start));
  // Salida: se hunde detrás de la ventana mientras esta vuelve a subir.
  const out = ramp(t, block.end - 0.2, 0.18, Easing.in(Easing.quad));
  return (
    <AbsoluteFill style={{ pointerEvents: "none", fontFamily: FONT.grotesk }}>
      <div style={{ position: "absolute", left: 0, top, width: W, textAlign: "center", fontSize: px, fontWeight: 700, letterSpacing: "-0.05em", lineHeight: 0.86, whiteSpace: "nowrap", opacity: 1 - out, translate: `0px ${46 * out}px` }}>
        <span style={{ position: "relative", display: "inline-block", scale: String(1 + 0.035 * life), transformOrigin: "50% 100%" }}>
          {/* fila pequeña, alineada con el borde izquierdo de la palabra */}
          <span style={{ position: "absolute", left: 6, bottom: (0.86 - CAP_TOP) * px + 12, fontSize: 54, fontWeight: 600, letterSpacing: "-0.035em", lineHeight: 1.05 }}>
            <Words words={block.small} size="S" t={t} />
          </span>
          {block.big.map((w, j) => {
            // La palabra sube desde detrás de la ventana: 280 ms.
            const p = ramp(t, w.t, 0.28, Easing.out(Easing.cubic));
            const flash = 1 - ramp(t, w.t + 0.05, 0.25, Easing.out(Easing.quad));
            return (
              <span
                key={j}
                style={{
                  display: "inline-block",
                  marginLeft: j === 0 ? 0 : "0.2em",
                  opacity: t < w.t ? 0 : Math.min(1, 0.2 + p),
                  translate: `0px ${110 * (1 - p)}px`,
                  scale: String(1.12 - 0.12 * p),
                  transformOrigin: "50% 100%",
                  filter: p < 1 ? `blur(${12 * (1 - p)}px)` : undefined,
                  color: mixWhite(flash * 0.8),
                  textShadow: `0 0 ${30 + 50 * flash}px rgba(255,222,33,${0.45 + 0.35 * flash}), 0 0 90px rgba(255,222,33,0.18)`,
                }}
              >
                {w.text}
              </span>
            );
          })}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ───────────────────────── Visor REC sobre la ventana ─────────────────────────
export const RecWindow: React.FC<{ t: number; at: number; end: number }> = ({ t, at, end }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.12);
  const inset = 26;
  const arm = 62;
  const line = "3px solid rgba(255,255,255,0.92)";
  const corner = (sx: number, sy: number): React.CSSProperties => ({
    position: "absolute",
    left: sx < 0 ? inset : undefined,
    right: sx > 0 ? inset : undefined,
    top: sy < 0 ? inset : undefined,
    bottom: sy > 0 ? inset : undefined,
    width: arm,
    height: arm * 0.9,
    borderLeft: sx < 0 ? line : undefined,
    borderRight: sx > 0 ? line : undefined,
    borderTop: sy < 0 ? line : undefined,
    borderBottom: sy > 0 ? line : undefined,
  });
  const blink = Math.floor((t - at) * 2) % 2 === 0;
  return (
    <div style={{ position: "absolute", left: WIN.x, top: winY(t), width: WIN.w, height: WIN.h, opacity: p, scale: String(1.04 - 0.04 * p) }}>
      <div style={corner(-1, -1)} />
      <div style={corner(1, -1)} />
      <div style={corner(-1, 1)} />
      <div style={corner(1, 1)} />
      <div style={{ position: "absolute", left: inset + 26, top: inset + 20, display: "flex", alignItems: "center", gap: 12, fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 30, color: C.white, letterSpacing: "0.02em" }}>
        <span style={{ width: 15, height: 15, borderRadius: 15, background: C.redDot, opacity: blink ? 1 : 0.25, boxShadow: "0 0 12px rgba(212,0,42,0.9)" }} />
        REC
      </div>
      <div style={{ position: "absolute", right: inset + 30, bottom: inset + 22, width: 26, height: 26 }}>
        <div style={{ position: "absolute", left: 12, top: 0, width: 2, height: 26, background: "rgba(255,255,255,0.85)" }} />
        <div style={{ position: "absolute", left: 0, top: 12, width: 26, height: 2, background: "rgba(255,255,255,0.85)" }} />
      </div>
    </div>
  );
};

// ───────────────────────── Flecha larga que barre la zona inferior («que el conflicto avance») ─────────────────────────
export const SweepArrow: React.FC<{ t: number; at: number; end: number; cy: number }> = ({ t, at, end, cy }) => {
  if (t < at || t >= end) return null;
  const p = ramp(t, at, 0.45, Easing.out(Easing.cubic));
  const head = ramp(t, at + 0.26, 0.16, Easing.out(Easing.back(2)));
  const x0 = 200;
  const x1 = 872;
  const y1 = cy - 34;
  return (
    <svg width={W} height={1920} viewBox={`0 0 ${W} 1920`} style={{ position: "absolute", left: 0, top: 0, overflow: "visible", filter: `drop-shadow(0 0 12px ${C.accentGlow}) drop-shadow(0 0 30px rgba(255,222,33,0.3))` }}>
      <path d={`M ${x0} ${cy + 34} C ${x0 + 230} ${cy + 46}, ${x1 - 260} ${cy + 18}, ${x1} ${y1}`} fill="none" stroke={C.accent} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
      <g transform={`translate(${x1} ${y1}) rotate(-14) scale(${head})`} opacity={head > 0 ? 1 : 0}>
        <path d="M -58 -44 L 6 0 L -58 44" fill="none" stroke={C.accent} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
      </g>
    </svg>
  );
};
