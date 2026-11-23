// Subtítulos al estilo de la referencia (estilo.md §2): bloque de hasta 3–4 filas pegadas, palabras pequeñas
// blancas, una palabra clave grande en lima con resplandor, cada palabra entra en el instante en que se dice.
import React from "react";
import { AbsoluteFill, Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { ramp } from "../anim";
import { C, FONT } from "../theme";

export type CapWord = { t: number; text: string; color?: "lime" | "white" | "grey" };
export type CapRow = {
  size: "S" | "M" | "L";
  align?: "left" | "right" | "center";
  words: CapWord[];
  strikeAt?: number; // tachado rojo a mano (segundo absoluto)
  px?: number; // tamaño forzado
};
export type CapBlock = { start: number; end: number; cy: number; rows: CapRow[]; maxW?: number; scale?: number };

const SHADOW = "0 2px 4px rgba(0,0,0,0.55), 0 4px 24px rgba(0,0,0,0.6)";
const GLOW = `0 0 28px ${C.limeGlow}, 0 0 60px rgba(223,255,79,0.22), 0 4px 24px rgba(0,0,0,0.6)`;

const sizeOf = (row: CapRow, maxW: number, scale: number) => {
  if (row.px) return row.px;
  if (row.size === "S") return 48 * scale;
  if (row.size === "M") return 88 * scale;
  const chars = row.words.map((w) => w.text).join(" ").length;
  return Math.max(92, Math.min(185 * scale, maxW / (0.535 * chars)));
};

const Word: React.FC<{ w: CapWord; row: CapRow; t: number; first: boolean }> = ({ w, row, t, first }) => {
  const color = w.color === "grey" ? C.grey : w.color === "lime" || (row.size === "L" && w.color !== "white") ? C.lime : C.white;
  const lime = color === C.lime;
  let style: React.CSSProperties;
  if (row.size === "L") {
    // 130 ms: escala 1,08→1, opacidad 50→100 %, desenfoque 8→0; el resplandor acaba de encenderse 100 ms después.
    const p = ramp(t, w.t, 0.13);
    const g = ramp(t, w.t + 0.08, 0.15);
    style = {
      opacity: t < w.t ? 0 : 0.5 + 0.5 * p,
      scale: String(1.08 - 0.08 * p),
      filter: p < 1 ? `blur(${8 * (1 - p)}px)` : undefined,
      textShadow: lime ? `0 0 ${28 * g}px rgba(223,255,79,${0.55 * g}), 0 0 60px rgba(223,255,79,${0.22 * g}), 0 4px 24px rgba(0,0,0,0.6)` : SHADOW,
    };
  } else if (row.size === "M") {
    // Barrido de izquierda a derecha en 130 ms.
    const p = ramp(t, w.t, 0.13, Easing.out(Easing.quad));
    style = {
      opacity: t < w.t ? 0 : 0.35 + 0.65 * p,
      clipPath: p < 1 ? `inset(-20% ${100 * (1 - p)}% -20% -5%)` : undefined,
      textShadow: lime ? GLOW : SHADOW,
    };
  } else {
    // Fundido + desenfoque 6→0 en 100 ms, sin desplazamiento.
    const p = ramp(t, w.t, 0.1, Easing.out(Easing.quad));
    style = {
      opacity: t < w.t ? 0 : p * (w.color === "grey" ? 0.75 : 1),
      filter: p < 1 ? `blur(${6 * (1 - p)}px)` : undefined,
      textShadow: SHADOW,
    };
  }
  return (
    <span style={{ display: "inline-block", color, marginLeft: first ? 0 : "0.22em", transformOrigin: "50% 60%", ...style }}>
      {w.text}
    </span>
  );
};

const Strike: React.FC<{ t: number; at: number }> = ({ t, at }) => {
  // Trazo rojo a mano, ≈15 px, ligeramente inclinado; se dibuja de izquierda a derecha en 400 ms.
  const p = ramp(t, at, 0.4, Easing.inOut(Easing.quad));
  if (t < at) return null;
  return (
    <svg viewBox="0 0 1000 200" preserveAspectRatio="none" style={{ position: "absolute", left: "-6%", top: "8%", width: "112%", height: "84%", overflow: "visible", pointerEvents: "none" }}>
      <path
        d="M 6 128 C 150 96, 300 118, 470 92 S 800 58, 994 74"
        fill="none"
        stroke={C.red}
        strokeWidth={17}
        strokeLinecap="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - p}
        style={{ filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.5))" }}
      />
    </svg>
  );
};

export const CaptionBlock: React.FC<{ block: CapBlock }> = ({ block }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < block.start || t >= block.end) return null;
  const maxW = block.maxW ?? 880;
  const scale = block.scale ?? 1;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: block.cy,
          translate: "-50% -50%",
          display: "flex",
          flexDirection: "column",
          width: "max-content",
          fontFamily: FONT.grotesk,
        }}
      >
        {block.rows.map((row, i) => {
          const px = sizeOf(row, maxW, scale);
          const big = row.size === "L";
          return (
            <div
              key={i}
              style={{
                position: "relative",
                alignSelf: row.align === "right" ? "flex-end" : row.align === "center" ? "center" : "flex-start",
                fontSize: px,
                fontWeight: row.size === "S" ? 600 : 700,
                letterSpacing: row.size === "S" ? "-0.035em" : "-0.045em",
                lineHeight: big ? 0.9 : row.size === "M" ? 0.98 : 1.08,
                whiteSpace: "nowrap",
                paddingLeft: row.size === "S" && row.align !== "right" && row.align !== "center" ? px * 0.35 : 0,
                paddingRight: row.size === "S" && row.align === "right" ? px * 0.25 : 0,
                marginTop: i === 0 ? 0 : big ? -px * 0.02 : row.size === "M" ? px * 0.02 : px * 0.06,
              }}
            >
              {row.words.map((w, j) => (
                <Word key={j} w={w} row={row} t={t} first={j === 0} />
              ))}
              {row.strikeAt !== undefined ? <Strike t={t} at={row.strikeAt} /> : null}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
