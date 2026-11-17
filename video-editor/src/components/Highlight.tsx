import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import { CUTS, EDL, Highlight as H, rand, Segment, segmentAt } from "../edl";
import { CAP, SF } from "../fonts";
import { SegmentFrame } from "./SegmentVideo";

const W = 1080;
const H_ = 1920;
const LINE = 0.92; // interlineado de la palabra grande (estilo.md)
const TRACK = -0.055; // interletraje en em (medido sobre "CLIENTES")

/** Definiciones SVG compartidas: texturas duotono de la referencia. */
export const TextureDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <defs>
      {/* Rojo: vídeo posterizado a dos rojos medidos en la referencia (#D70000 / #FD4040) */}
      <filter id="duoRed" colorInterpolationFilters="sRGB">
        <feColorMatrix type="matrix" values="0.2126 0.7152 0.0722 0 0 0.2126 0.7152 0.0722 0 0 0.2126 0.7152 0.0722 0 0 0 0 0 1 0" />
        <feComponentTransfer>
          <feFuncR type="discrete" tableValues="0.843 0.843 0.992" />
          <feFuncG type="discrete" tableValues="0 0 0.251" />
          <feFuncB type="discrete" tableValues="0 0 0.251" />
        </feComponentTransfer>
      </filter>
      {/* Blanco: vídeo en grises claros (como "GRABAR") */}
      <filter id="duoWhite" colorInterpolationFilters="sRGB">
        <feColorMatrix type="matrix" values="0.2126 0.7152 0.0722 0 0 0.2126 0.7152 0.0722 0 0 0.2126 0.7152 0.0722 0 0 0 0 0 1 0" />
        <feComponentTransfer>
          <feFuncR type="linear" slope="0.62" intercept="0.4" />
          <feFuncG type="linear" slope="0.62" intercept="0.4" />
          <feFuncB type="linear" slope="0.62" intercept="0.4" />
        </feComponentTransfer>
      </filter>
    </defs>
  </svg>
);

const fit = (lines: string[], size: number) => {
  // ancho aproximado de SF Pro Display Black en mayúsculas (0,64 em por carácter con el tracking)
  const longest = Math.max(...lines.map((l) => l.length));
  const est = longest * size * 0.64;
  return est > 1000 ? (size * 1000) / est : size;
};

/** Texto grande con textura de vídeo y glitch por franjas. */
const BigWord: React.FC<{ h: H; seg: Segment; start: number; id: string }> = ({ h, seg, start, id }) => {
  const frame = useCurrentFrame();
  const g = start + frame; // fotograma global
  const lines = h.big.split("\n");
  const size = fit(lines, h.layout.size);
  const anchor = h.layout.align === "left" ? "start" : h.layout.align === "right" ? "end" : "middle";
  const top = h.layout.bigY;
  const bottom = top + size * (CAP + (lines.length - 1) * LINE) + size * 0.12;
  const since = g - h.bFrom;
  if (since < 0) return null;

  // entrada: rojo = aparición seca con escala 1,10 -> 1; blanco = zoom-blur 1,25 -> 1 y desenfoque 20 -> 0
  const isWhite = h.style === "white";
  const inDur = isWhite ? 4 : 3;
  const scale = interpolate(since, [0, inDur], [isWhite ? 1.25 : 1.1, 1], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const blur = isWhite ? interpolate(since, [0, inDur], [20, 0], { extrapolateRight: "clamp" }) : 0;
  const fadeOut = CUTS.has(h.to) ? 1 : interpolate(g, [h.to - 6, h.to], [1, 0.3], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const opacity = Math.min(interpolate(since, [0, 1], [0.4, 1], { extrapolateRight: "clamp" }), fadeOut);

  // glitch: cada 3 fotogramas cambian los cortes y desplazamientos de 3 franjas
  const epoch = Math.floor(since / 3);
  const strong = since < 3;
  const r1 = top + (bottom - top) * (0.2 + 0.25 * rand(epoch * 7 + h.bFrom));
  const r2 = top + (bottom - top) * (0.55 + 0.3 * rand(epoch * 13 + h.bFrom));
  const bands: [number, number][] = [
    [0, r1],
    [r1, r2],
    [r2, H_],
  ];
  const dx = bands.map((_, i) => {
    const on = rand(epoch * 31 + i * 5 + h.bFrom) < (strong ? 0.7 : 0.22);
    const mag = (strong ? 8 : 3) + rand(epoch * 17 + i) * (strong ? 10 : 6);
    return on ? (rand(epoch * 3 + i * 11) < 0.5 ? -mag : mag) : 0;
  });

  const texture = (
    <AbsoluteFill style={{ clipPath: `url(#${id})` }}>
      <AbsoluteFill style={{ backgroundColor: isWhite ? "#FFFFFF" : "#E10000" }} />
      <AbsoluteFill
        style={{
          filter: `url(#${isWhite ? "duoWhite" : "duoRed"})`,
          opacity: isWhite ? 0.92 : 0.88,
          translate: "-28px 16px",
          scale: "1.05",
        }}
      >
        <SegmentFrame seg={seg} kind="base" offset={h.bFrom - seg.from_} />
      </AbsoluteFill>
    </AbsoluteFill>
  );

  return (
    <AbsoluteFill
      style={{
        opacity,
        scale: String(scale),
        transformOrigin: `${h.layout.x}px ${(top + bottom) / 2}px`,
        // las blancas llevan una sombra suave para leerse sobre paredes claras
        filter:
          [blur > 0.2 ? `blur(${blur}px)` : "", isWhite ? "drop-shadow(0 8px 26px rgba(0,0,0,0.38))" : ""].join(" ").trim() ||
          undefined,
      }}
    >
      <svg width={W} height={H_} style={{ position: "absolute", left: 0, top: 0 }}>
        <defs>
          <clipPath id={id} clipPathUnits="userSpaceOnUse">
            <text
              textAnchor={anchor}
              style={{ fontFamily: SF, fontWeight: 900, fontSize: size, letterSpacing: `${TRACK}em` }}
            >
              {lines.map((l, i) => (
                <tspan key={i} x={h.layout.x} y={top + size * CAP + i * size * LINE}>
                  {l}
                </tspan>
              ))}
            </text>
          </clipPath>
        </defs>
      </svg>
      {bands.map(([a, b], i) => (
        <AbsoluteFill key={i} style={{ clipPath: `inset(${a}px 0px ${H_ - b}px 0px)`, translate: `${dx[i]}px 0px` }}>
          {texture}
        </AbsoluteFill>
      ))}
    </AbsoluteFill>
  );
};

/** Texto pequeño (kicker) tecleado letra a letra. */
const Kicker: React.FC<{ h: H; start: number }> = ({ h, start }) => {
  const frame = useCurrentFrame();
  const g = start + frame;
  if (!h.kicker || h.kFrom === null || g < h.kFrom) return null;
  const n = Math.min(h.kicker.length, g - h.kFrom + 1);
  const size = Math.max(54, Math.min(104, h.layout.size * 0.42));
  const fadeOut = CUTS.has(h.to) ? 1 : interpolate(g, [h.to - 6, h.to], [1, 0.3], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const align = h.layout.align;
  return (
    <div
      style={{
        position: "absolute",
        top: h.layout.kickerY - size * 0.95,
        left: align === "left" ? h.layout.x + 8 : undefined,
        right: align === "right" ? W - h.layout.x + 8 : undefined,
        width: align === "center" ? W : undefined,
        textAlign: align,
        fontFamily: SF,
        fontWeight: 300,
        fontStyle: h.kickerItalic ? "italic" : "normal",
        fontSize: size,
        lineHeight: 1,
        color: "#FFFFFF",
        letterSpacing: "0.01em",
        whiteSpace: "pre",
        textShadow: "0 2px 10px rgba(0,0,0,0.35)",
        opacity: fadeOut,
      }}
    >
      {/* la parte aún no tecleada ocupa su sitio pero es invisible: el bloque no se recoloca */}
      {h.kicker.slice(0, n)}
      <span style={{ opacity: 0 }}>{h.kicker.slice(n)}</span>
    </div>
  );
};

export const HighlightItem: React.FC<{ h: H; index: number; part: "big" | "kicker" }> = ({ h, index, part }) => {
  const start = Math.min(h.kFrom ?? h.bFrom, h.bFrom);
  const seg = segmentAt(h.bFrom);
  if (!seg) return null;
  return (
    <Sequence from={start} durationInFrames={h.to - start} name={`${part === "big" ? "Palabra" : "Kicker"} ${h.big.replace("\n", " ")}`}>
      {part === "big" ? <BigWord h={h} seg={seg} start={start} id={`hl-clip-${index}`} /> : <Kicker h={h} start={start} />}
    </Sequence>
  );
};

/**
 * Capas de destacados. "behind": palabras grandes que van detrás de la persona.
 * "front": palabras grandes delante + todos los kickers (siempre delante).
 */
export const HighlightsLayer: React.FC<{ layer: "behind" | "front" }> = ({ layer }) => (
  <>
    {EDL.highlights.map((h, i) => (
      <React.Fragment key={i}>
        {h.behind === (layer === "behind") ? <HighlightItem h={h} index={i} part="big" /> : null}
        {layer === "front" && h.kicker ? <HighlightItem h={h} index={i} part="kicker" /> : null}
      </React.Fragment>
    ))}
  </>
);
