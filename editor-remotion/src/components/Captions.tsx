// Subtítulos al estilo de la referencia (estilo.md §2): bloque compacto con palabras pequeñas blancas encajadas
// sobre una palabra clave grande con resplandor. Cada palabra entra en el instante en que se dice.
// v2 (corrección del cliente: «más dinámicos»): la palabra clave entra con golpe de escala y destello,
// las pequeñas suben, el bloque respira, y hay una variante que va DETRÁS del sujeto (BehindBlock).
import React from "react";
import { AbsoluteFill, Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { keys, lerp, ramp } from "../anim";
import { C, FONT, W } from "../theme";

export type CapWord = { t: number; text: string; color?: "accent" | "white" | "grey" };
export type CapRow = {
  size: "S" | "M" | "L";
  align?: "left" | "right" | "center";
  words: CapWord[];
  right?: CapWord[]; // segundo grupo en la misma fila, pegado a la derecha («If the … have to»)
  strikeAt?: number; // tachado rojo a mano (segundo absoluto)
  px?: number; // tamaño forzado
};
export type CapBlock = { start: number; end: number; cy: number; rows: CapRow[]; maxW?: number; scale?: number };

const SHADOW = "0 2px 6px rgba(0,0,0,0.6), 0 6px 30px rgba(0,0,0,0.65)";

const mix = (a: [number, number, number], b: [number, number, number], p: number) => `rgb(${Math.round(lerp(a[0], b[0], p))},${Math.round(lerp(a[1], b[1], p))},${Math.round(lerp(a[2], b[2], p))})`;
const ACCENT: [number, number, number] = [255, 222, 33];
const WHITE: [number, number, number] = [255, 255, 255];

export const keywordSize = (text: string, maxW: number, max: number) => Math.max(92, Math.min(max, maxW / (0.535 * text.length)));

const sizeOf = (row: CapRow, maxW: number, scale: number) => {
  if (row.px) return row.px;
  if (row.size === "S") return 50 * scale;
  if (row.size === "M") return 92 * scale;
  return keywordSize(row.words.map((w) => w.text).join(" "), maxW, 190 * scale);
};

/** Estilo de entrada de una palabra según su nivel. */
export const wordStyle = (w: CapWord, size: CapRow["size"], t: number): React.CSSProperties => {
  const accent = w.color === "accent" || (size === "L" && w.color !== "white" && w.color !== "grey");
  if (t < w.t) return { opacity: 0 };
  if (size === "L") {
    // 220 ms: golpe de escala 1,28→0,97→1 con desenfoque, destello blanco→amarillo y resplandor que se asienta.
    const s = keys(t, [
      [w.t, 1.28],
      [w.t + 0.13, 0.97],
      [w.t + 0.22, 1.0],
    ]);
    const p = ramp(t, w.t, 0.13);
    const flash = 1 - ramp(t, w.t + 0.03, 0.2, Easing.out(Easing.quad));
    const glow = 28 + 46 * flash;
    return {
      opacity: Math.min(1, 0.25 + 0.75 * ramp(t, w.t, 0.08)),
      scale: String(s),
      filter: p < 1 ? `blur(${12 * (1 - p)}px)` : undefined,
      color: accent ? mix(ACCENT, WHITE, flash * 0.85) : C.white,
      textShadow: accent ? `0 0 ${glow}px rgba(255,222,33,${0.55 + 0.35 * flash}), 0 0 70px rgba(255,222,33,0.22), 0 4px 24px rgba(0,0,0,0.65)` : SHADOW,
    };
  }
  if (size === "M") {
    // Barrido de izquierda a derecha con empuje lateral, 160 ms.
    const p = ramp(t, w.t, 0.16, Easing.out(Easing.cubic));
    return {
      opacity: 0.3 + 0.7 * p,
      translate: `${-26 * (1 - p)}px 0px`,
      clipPath: p < 1 ? `inset(-25% ${100 * (1 - p)}% -25% -8%)` : undefined,
      color: accent ? C.accent : w.color === "grey" ? C.grey : C.white,
      textShadow: accent ? `0 0 26px ${C.accentGlow}, 0 4px 24px rgba(0,0,0,0.65)` : SHADOW,
    };
  }
  // Pequeñas: suben 12 px con fundido y desenfoque, 120 ms.
  const p = ramp(t, w.t, 0.12, Easing.out(Easing.cubic));
  return {
    opacity: p * (w.color === "grey" ? 0.75 : 1),
    translate: `0px ${12 * (1 - p)}px`,
    filter: p < 1 ? `blur(${6 * (1 - p)}px)` : undefined,
    color: accent ? C.accent : w.color === "grey" ? C.grey : C.white,
    textShadow: SHADOW,
  };
};

const Words: React.FC<{ words: CapWord[]; size: CapRow["size"]; t: number }> = ({ words, size, t }) => (
  <span style={{ display: "inline-block", whiteSpace: "nowrap" }}>
    {words.map((w, j) => (
      <span key={j} style={{ display: "inline-block", marginLeft: j === 0 ? 0 : "0.22em", transformOrigin: "50% 62%", ...wordStyle(w, size, t) }}>
        {w.text}
      </span>
    ))}
  </span>
);

const Strike: React.FC<{ t: number; at: number }> = ({ t, at }) => {
  // Trazo rojo a mano, ≈15 px, ligeramente inclinado; se dibuja de izquierda a derecha en 400 ms.
  const p = ramp(t, at, 0.4, Easing.inOut(Easing.quad));
  if (t < at) return null;
  return (
    <svg viewBox="0 0 1000 200" preserveAspectRatio="none" style={{ position: "absolute", left: "-6%", top: "8%", width: "112%", height: "84%", overflow: "visible", pointerEvents: "none" }}>
      <path d="M 6 128 C 150 96, 300 118, 470 92 S 800 58, 994 74" fill="none" stroke={C.red} strokeWidth={17} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} style={{ filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.5))" }} />
    </svg>
  );
};

export const CaptionBlock: React.FC<{ block: CapBlock }> = ({ block }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < block.start || t >= block.end) return null;
  const maxW = block.maxW ?? 900;
  const scale = block.scale ?? 1;
  // El bloque «respira»: crece un 3,5 % mientras está en pantalla.
  const life = Math.min(1, (t - block.start) / Math.max(0.4, block.end - block.start));
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: "50%", top: block.cy, translate: "-50% -50%", scale: String(1 + 0.035 * life), display: "flex", flexDirection: "column", width: "max-content", fontFamily: FONT.grotesk }}>
        {block.rows.map((row, i) => {
          const px = sizeOf(row, maxW, scale);
          const big = row.size === "L";
          const prevBig = i > 0 && block.rows[i - 1].size === "L";
          const nextBig = i < block.rows.length - 1 && block.rows[i + 1].size === "L";
          return (
            <div
              key={i}
              style={{
                position: "relative",
                zIndex: big ? 1 : 2, // las pequeñas montan sobre la palabra clave
                display: "flex",
                justifyContent: row.right ? "space-between" : row.align === "right" ? "flex-end" : row.align === "center" ? "center" : "flex-start",
                alignSelf: row.right ? "stretch" : row.align === "right" ? "flex-end" : row.align === "center" ? "center" : "flex-start",
                gap: 30,
                fontSize: px,
                fontWeight: row.size === "S" ? 600 : 700,
                letterSpacing: row.size === "S" ? "-0.035em" : "-0.045em",
                lineHeight: big ? 0.9 : row.size === "M" ? 0.98 : 1.05,
                whiteSpace: "nowrap",
                paddingLeft: !big && row.align !== "right" && row.align !== "center" ? px * 0.3 : 0,
                paddingRight: !big && (row.align === "right" || row.right) ? px * 0.3 : 0,
                // Encaje de la referencia: la fila pequeña pisa el borde de la palabra clave.
                marginBottom: !big && nextBig ? -px * (row.size === "S" ? 0.2 : 0.08) : 0,
                marginTop: i === 0 ? 0 : big ? 0 : prevBig ? -px * (row.size === "S" ? 0.28 : 0.1) : px * 0.04,
              }}
            >
              <Words words={row.words} size={row.size} t={t} />
              {row.right ? <Words words={row.right} size={row.size} t={t} /> : null}
              {row.strikeAt !== undefined ? <Strike t={t} at={row.strikeAt} /> : null}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ───────────────────────── Texto detrás del sujeto ─────────────────────────
// Va entre el vídeo base y la capa del sujeto recortado: la cabeza tapa parte de la palabra gigante.
export type BehindBlockT = {
  seg: string; // toma (para saber qué recorte del sujeto va encima)
  start: number;
  end: number;
  top: number; // borde superior de la palabra gigante
  small: CapWord[]; // fila pequeña, arriba a la izquierda
  big: CapWord[]; // palabra gigante
  under?: CapWord[]; // fila mediana, abajo a la derecha
  px?: number;
};

export const BehindBlock: React.FC<{ block: BehindBlockT }> = ({ block }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < block.start || t >= block.end) return null;
  const text = block.big.map((w) => w.text).join(" ");
  const px = block.px ?? Math.min(400, (W - 130) / (0.535 * text.length));
  const life = Math.min(1, (t - block.start) / Math.max(0.4, block.end - block.start));
  return (
    <AbsoluteFill style={{ pointerEvents: "none", fontFamily: FONT.grotesk }}>
      {/* velo oscuro para que la palabra se lea sobre la pared */}
      <div style={{ position: "absolute", left: 0, top: 0, width: W, height: block.top + px * 1.6, background: "linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.34) 60%, rgba(0,0,0,0) 100%)" }} />
      <div style={{ position: "absolute", left: 56, top: block.top - 66, fontSize: 54, fontWeight: 600, letterSpacing: "-0.035em", whiteSpace: "nowrap" }}>
        <Words words={block.small} size="S" t={t} />
      </div>
      <div style={{ position: "absolute", left: 0, top: block.top, width: W, textAlign: "center", fontSize: px, fontWeight: 700, letterSpacing: "-0.05em", lineHeight: 0.86, whiteSpace: "nowrap", translate: `0px ${-14 * life}px`, scale: String(1 + 0.04 * life) }}>
        {block.big.map((w, j) => {
          // La palabra gigante sube desde detrás de la cabeza: 280 ms.
          const p = ramp(t, w.t, 0.28, Easing.out(Easing.cubic));
          const flash = 1 - ramp(t, w.t + 0.05, 0.25, Easing.out(Easing.quad));
          return (
            <span
              key={j}
              style={{
                display: "inline-block",
                marginLeft: j === 0 ? 0 : "0.2em",
                opacity: t < w.t ? 0 : Math.min(1, 0.2 + p),
                translate: `0px ${90 * (1 - p)}px`,
                scale: String(1.14 - 0.14 * p),
                filter: p < 1 ? `blur(${14 * (1 - p)}px)` : undefined,
                color: mix(ACCENT, WHITE, flash * 0.8),
                textShadow: `0 0 ${34 + 50 * flash}px rgba(255,222,33,${0.5 + 0.35 * flash}), 0 0 90px rgba(255,222,33,0.2)`,
              }}
            >
              {w.text}
            </span>
          );
        })}
      </div>
      {block.under ? (
        <div style={{ position: "absolute", right: 56, top: block.top + px * 0.84, fontSize: Math.min(104, px * 0.36), fontWeight: 700, letterSpacing: "-0.045em", whiteSpace: "nowrap" }}>
          <Words words={block.under} size="M" t={t} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
