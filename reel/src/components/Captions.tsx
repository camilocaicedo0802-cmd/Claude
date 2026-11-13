import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { BEBAS, C, GLOW, GRADIENT, OUTFIT, W } from "../theme";
import { BLOCKS, Block } from "../timeline";
import { Word, clamp01, easeOut, measure, prog, word } from "../util";

const SMALL = 50; // px, palabras de contexto (estilo.md §2: 44–60 px)
const SMALL_SHADOW = "0 2px 14px rgba(0,0,0,0.55)";

const cleanText = (w: Word) => w.text.replace(/[,.;:]+$/, "");
const upperFirst = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

/** Palabra pequeña: fade + subida 20 px + blur 6→0 en 5 fotogramas, justo cuando se pronuncia. */
const SmallWord: React.FC<{ w: Word; t: number; font?: string; size?: number }> = ({ w, t, font, size }) => {
  const p = prog(t, w.start - 0.03, 5 / 30);
  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: font ?? OUTFIT,
        fontWeight: 500,
        fontSize: size ?? SMALL,
        color: C.white,
        letterSpacing: "-0.02em",
        opacity: p,
        translate: `0px ${20 * (1 - p)}px`,
        filter: p < 1 ? `blur(${6 * (1 - p)}px)` : undefined,
        textShadow: SMALL_SHADOW,
        whiteSpace: "pre",
      }}
    >
      {cleanText(w)}
    </span>
  );
};

const KineticBlock: React.FC<{ b: Block; t: number; next?: Block }> = ({ b, t, next }) => {
  const all: Word[] = [];
  for (let i = b.w[0]; i <= b.w[1]; i++) {
    if (b.skip?.includes(i)) continue;
    try {
      all.push(word(i));
    } catch {
      /* palabra eliminada en el montaje */
    }
  }
  const hlSet = new Set(b.hl);
  const hlWords = all.filter((w) => hlSet.has(w.i));
  const firstHl = Math.min(...b.hl);
  const lastHl = Math.max(...b.hl);
  const before = all.filter((w) => w.i < firstHl);
  const after = all.filter((w) => w.i > lastHl);

  const start = all[0].start - 0.05;
  const naturalEnd = Math.max(...all.map((w) => w.end)) + 0.5;
  const end = b.end ?? Math.min(naturalEnd, next ? next.w && word(next.w[0]).start - 0.02 : naturalEnd);
  if (t < start || t > end) return null;

  const style = b.style ?? "yellow";
  const isTitle = style === "title";
  const hlStart = hlWords[0].start - 0.02;

  // --- Palabra destacada: tamaño ajustado al ancho objetivo (650–760 px) ---
  const hlRaw = hlWords.map(cleanText).join(" ");
  const hlText = b.hlText ?? (isTitle ? hlRaw.toUpperCase() : upperFirst(hlRaw));
  const fontFamily = isTitle ? BEBAS : OUTFIT;
  const weight = isTitle ? 400 : 700;
  const spacing = isTitle ? 0.01 : -0.04;
  const target = b.hlWidth ?? (isTitle ? 900 : 740);
  const ref = measure(hlText, `${weight} 100px ${fontFamily}`, spacing) || 1;
  const maxHl = b.maxHl ?? (isTitle ? 300 : 250);
  const hlSize = Math.max(isTitle ? 140 : 110, Math.min(maxHl, (100 * target) / ref));
  const hlWidth = (ref * hlSize) / 100;

  const p = prog(t, hlStart, 7 / 30);
  const exit = clamp01((t - (end - 0.14)) / 0.14);
  const life = clamp01((t - start) / Math.max(0.3, end - start));

  // Título condensado: aparece letra a letra (máquina de escribir).
  const typed = isTitle
    ? hlText.slice(0, Math.max(0, Math.floor(clamp01((t - hlStart) / Math.min(0.6, Math.max(0.25, hlText.length * 0.04))) * hlText.length + 0.001)))
    : hlText;

  const gradient = style === "lime" ? GRADIENT.lime : style === "white" ? GRADIENT.white : GRADIENT.yellow;
  const glow = style === "lime" ? GLOW.lime : style === "white" ? GLOW.white : GLOW.yellow;

  // Línea superior: palabras repartidas a izquierda y derecha (como "Discipline ··· is the").
  const half = Math.ceil(before.length / 2);
  const left = before.length >= 2 ? before.slice(0, half) : before;
  const right = before.length >= 2 ? before.slice(half) : [];
  const lineWidth = Math.max(hlWidth, 560);

  return (
    <div
      style={{
        position: "absolute",
        left: (b.x ?? 0.5) * W,
        top: (b.y ?? 0.6) * 1920,
        translate: "-50% -50%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        opacity: 1 - exit,
        filter: exit > 0 ? `blur(${8 * exit}px)` : undefined,
        scale: String(1 + 0.03 * life),
      }}
    >
      {before.length > 0 && (
        <div
          style={{
            minWidth: lineWidth,
            maxWidth: 1000,
            columnGap: 34,
            display: "flex",
            justifyContent: right.length ? "space-between" : "center",
            alignItems: "flex-end",
            marginBottom: isTitle ? -6 : -Math.round(hlSize * 0.12),
            paddingLeft: 8,
            paddingRight: 8,
          }}
        >
          <div style={{ display: "flex", gap: 14 }}>
            {left.map((w) => (
              <SmallWord key={w.i} w={w} t={t} />
            ))}
          </div>
          {right.length > 0 && (
            <div style={{ display: "flex", gap: 14, paddingTop: 18 }}>
              {right.map((w) => (
                <SmallWord key={w.i} w={w} t={t} />
              ))}
            </div>
          )}
        </div>
      )}
      <div
        style={{
          fontFamily,
          fontWeight: weight,
          fontSize: hlSize,
          lineHeight: isTitle ? 0.92 : 1.02,
          letterSpacing: `${spacing}em`,
          whiteSpace: "nowrap",
          opacity: p,
          translate: `0px ${60 * (1 - p)}px`,
          scale: String(0.85 + 0.15 * p),
          ...(isTitle
            ? {
                color: "#F5F5F5",
                textShadow: "0 0 30px rgba(255,255,255,0.25), 0 6px 26px rgba(0,0,0,0.45)",
                filter: p < 1 ? `blur(${10 * (1 - p)}px)` : undefined,
              }
            : {
                backgroundImage: gradient,
                WebkitBackgroundClip: "text",
                backgroundClip: "text",
                color: "transparent",
                filter: `${p < 1 ? `blur(${12 * (1 - p)}px) ` : ""}${glow}`,
                paddingBottom: Math.round(hlSize * 0.08),
              }),
        }}
      >
        {isTitle ? (
          <>
            {typed}
            <span style={{ opacity: 0 }}>{hlText.slice(typed.length)}</span>
          </>
        ) : (
          hlText
        )}
      </div>
      {after.length > 0 && (
        <div
          style={{
            minWidth: lineWidth,
            display: "flex",
            justifyContent: "flex-end",
            gap: 12,
            marginTop: isTitle ? 4 : -Math.round(hlSize * 0.1),
            paddingRight: 8,
          }}
        >
          {after.map((w) => (
            <SmallWord key={w.i} w={w} t={t} size={isTitle ? 44 : 46} />
          ))}
        </div>
      )}
      {b.strikeAt !== undefined && t >= b.strikeAt && (
        <Strike t={t} t0={b.strikeAt} width={hlWidth} hlSize={hlSize} />
      )}
    </div>
  );
};

/** Tachado rojo a mano alzada (marcador), dibujado de izquierda a derecha en 6 fotogramas. */
const Strike: React.FC<{ t: number; t0: number; width: number; hlSize: number }> = ({ t, t0, width, hlSize }) => {
  const p = prog(t, t0, 6 / 30, easeOut);
  const w = width + 40;
  const y = hlSize * 0.5;
  const d = `M 6 ${y + 10} C ${w * 0.3} ${y - 6}, ${w * 0.6} ${y + 14}, ${w - 6} ${y - 4}`;
  return (
    <svg
      width={w}
      height={hlSize}
      style={{ position: "absolute", left: "50%", bottom: hlSize * 0.12, translate: "-50% 0", overflow: "visible" }}
    >
      <path
        d={d}
        stroke={C.red}
        strokeWidth={14}
        strokeLinecap="round"
        fill="none"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - p}
        style={{ filter: "drop-shadow(0 0 14px rgba(254,67,72,0.6))" }}
      />
    </svg>
  );
};

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <>
      {BLOCKS.map((b, i) => (
        <KineticBlock key={b.id} b={b} t={t} next={BLOCKS[i + 1]} />
      ))}
    </>
  );
};
