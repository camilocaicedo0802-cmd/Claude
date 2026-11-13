import type { Caption } from "@remotion/captions";
import React from "react";
import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { blurIn, blurOut, clamp, easeInOut, easeOut, keyframes } from "../anim";
import { BRAND, BRAND_SANS, BRAND_SCRIPT, BRAND_SERIF, C, LAYOUT, SANS, TEXT_SHADOW } from "../theme";

/* ------------------------------------------------------------------------ */
/* Texto tecleado: las letras aparecen una a una (acompaña al SFX de typing). */
/* El texto que falta se reserva invisible para que el bloque no se mueva.    */
/* ------------------------------------------------------------------------ */

export const Typed: React.FC<{ readonly text: string; readonly at: number; readonly framesPerChar: number }> = ({
  text,
  at,
  framesPerChar,
}) => {
  const frame = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor((frame - at) / framesPerChar) + 1));
  if (frame < at) return <span style={{ opacity: 0 }}>{text}</span>;
  return (
    <>
      <span>{text.slice(0, n)}</span>
      <span style={{ opacity: 0 }}>{text.slice(n)}</span>
    </>
  );
};

/* ------------------------------------------------------------------------ */
/* Texto del hook: palabras en cascada (referente "Ranking de redflags…").    */
/* ------------------------------------------------------------------------ */

type CascadeProps = {
  readonly name: string;
  readonly from: number;
  readonly durationInFrames: number;
  readonly children: React.ReactNode;
};

/** Grupo de palabras con salida común (blur + fundido de 6 fotogramas). */
export const Cascade: React.FC<CascadeProps> = ({ name, from, durationInFrames, children }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames}>
    <CascadeExit durationInFrames={durationInFrames}>{children}</CascadeExit>
  </Sequence>
);

const CascadeExit: React.FC<{ readonly durationInFrames: number; readonly children: React.ReactNode }> = ({
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const out = blurOut(frame, durationInFrames);
  return <AbsoluteFill style={{ opacity: out.opacity, filter: `blur(${out.blur}px)` }}>{children}</AbsoluteFill>;
};

type WordFont = "sans" | "brand" | "script";

type WordProps = {
  readonly at: number;
  readonly x: number;
  readonly y: number;
  readonly size: number;
  readonly children: string;
  /** sans = Inter Display (base); brand = Black Mango; script = Jimmy Script. */
  readonly font?: WordFont;
  readonly weight?: number;
  readonly color?: string;
  readonly align?: "left" | "center";
  /** Si se indica, la palabra se teclea a este ritmo (fotogramas por letra). */
  readonly typing?: number;
};

const FAMILY: Record<WordFont, string> = { sans: SANS, brand: BRAND_SERIF, script: BRAND_SCRIPT };

/** Palabra que entra con fundido + desenfoque en 4 fotogramas (o tecleada) y se queda. */
export const Word: React.FC<WordProps> = ({
  at,
  x,
  y,
  size,
  children,
  font = "sans",
  weight = 700,
  color = C.white,
  align = "left",
  typing,
}) => {
  const frame = useCurrentFrame();
  const accent = font !== "sans";
  const a = typing ? { opacity: frame >= at ? 1 : 0, filter: "none" } : blurIn(frame, at, 4, 12);
  const rise = typing ? 0 : interpolate(frame, [at, at + 4], [accent ? 24 : 12, 0], { ...clamp, easing: easeOut });
  const sc = accent && !typing ? interpolate(frame, [at, at + 4], [0.9, 1], { ...clamp, easing: easeOut }) : 1;
  return (
    <div
      style={{
        position: "absolute",
        left: align === "center" ? 0 : x,
        width: align === "center" ? 1080 : undefined,
        textAlign: align,
        top: y,
        fontFamily: FAMILY[font],
        fontWeight: accent ? 400 : weight,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: font === "sans" ? "-0.04em" : font === "brand" ? "-0.01em" : "0em",
        color,
        whiteSpace: "nowrap",
        textShadow: accent ? "0 2px 4px rgba(0,0,0,0.28), 0 0 26px rgba(0,0,0,0.42)" : TEXT_SHADOW,
        WebkitTextStroke: font === "brand" ? `1.5px ${color}` : undefined,
        opacity: a.opacity,
        filter: a.filter,
        translate: `0px ${rise}px`,
        scale: String(sc),
        transformOrigin: align === "center" ? "center center" : "left center",
      }}
    >
      {typing ? <Typed text={children} at={at} framesPerChar={typing} /> : children}
    </div>
  );
};

/* ------------------------------------------------------------------------ */
/* Ítem numerado (referente "1. Mal aliento").                               */
/* ------------------------------------------------------------------------ */

type ItemLine = { readonly text: string; readonly at: number };

type NumberedItemProps = {
  readonly name: string;
  readonly from: number;
  readonly durationInFrames: number;
  readonly num: string;
  readonly lines: ReadonlyArray<ItemLine>;
  /** Borde izquierdo final del bloque. */
  readonly left: number;
  readonly top?: number;
};

export const NumberedItem: React.FC<NumberedItemProps> = ({ name, from, durationInFrames, ...rest }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames}>
    <NumberedItemInner durationInFrames={durationInFrames} {...rest} />
  </Sequence>
);

const NumberedItemInner: React.FC<Omit<NumberedItemProps, "name" | "from">> = ({
  durationInFrames,
  num,
  lines,
  left,
  top = LAYOUT.blockTop,
}) => {
  const frame = useCurrentFrame();
  const out = blurOut(frame, durationInFrames);
  const numW = 120;
  // f0: el número aparece en seco centrado; f2→f8 se desliza a su sitio.
  const slide = interpolate(frame, [2, 8], [540 - (left + numW / 2), 0], { ...clamp, easing: easeOut });
  const pop = interpolate(frame, [0, 3], [1.15, 1], { ...clamp, easing: easeOut });
  return (
    <AbsoluteFill style={{ opacity: out.opacity, filter: `blur(${out.blur}px)` }}>
      <div style={{ position: "absolute", left, top, display: "flex", alignItems: "center", gap: 22 }}>
        <div style={{ width: numW, display: "flex", justifyContent: "flex-end", translate: `${slide}px 0px`, scale: String(pop) }}>
          <span
            style={{
              fontFamily: SANS,
              fontWeight: 900,
              fontSize: 104,
              lineHeight: 1,
              letterSpacing: "-0.04em",
              color: C.white,
              textShadow: TEXT_SHADOW,
            }}
          >
            {num}
          </span>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          {lines.map((l) => {
            const a = blurIn(frame, l.at, 5, 12);
            const dx = interpolate(frame, [l.at, l.at + 5], [20, 0], { ...clamp, easing: easeOut });
            return (
              <div
                key={l.text}
                style={{
                  fontFamily: SANS,
                  fontWeight: 500,
                  fontSize: 64,
                  lineHeight: 1,
                  letterSpacing: "-0.04em",
                  color: C.white,
                  whiteSpace: "nowrap",
                  textShadow: TEXT_SHADOW,
                  opacity: a.opacity,
                  filter: a.filter,
                  translate: `${dx}px 0px`,
                }}
              >
                {l.text}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------------ */
/* Subtítulos: bloques de 1–4 palabras, cambio en seco (estilo.md §3).        */
/* ------------------------------------------------------------------------ */

export const Subtitles: React.FC<{ readonly name: string; readonly captions: Caption[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // +0.5 ms: evita que un bloque siga visible el fotograma en que empieza el siguiente.
  const ms = (frame / fps) * 1000 + 0.5;
  const pages: Caption[][] = [];
  let cur: Caption[] = [];
  for (const c of captions) {
    cur.push(c);
    if (c.pageBreakAfter) {
      pages.push(cur);
      cur = [];
    }
  }
  if (cur.length) pages.push(cur);
  const page = pages.find((p) => ms >= p[0].startMs && ms < p[p.length - 1].endMs);
  if (!page) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        width: 960,
        top: LAYOUT.subtitleCenterY - 34,
        textAlign: "center",
        fontFamily: SANS,
        fontWeight: 500,
        fontSize: 54,
        lineHeight: 1.15,
        letterSpacing: "-0.04em",
        color: C.white,
        textShadow: "0 2px 8px rgba(0,0,0,0.25)",
      }}
    >
      {page.map((w) => w.text).join("").trim()}
    </div>
  );
};

/* ------------------------------------------------------------------------ */
/* Barra 1–10 (objeto del referente) con la escala beige → marrón de marca.   */
/* ------------------------------------------------------------------------ */

type BarProps = {
  readonly name: string;
  readonly from: number;
  readonly durationInFrames: number;
  /** [fotograma, índice] del puntero, relativo al inicio de la barra. */
  readonly pointer: ReadonlyArray<readonly [number, number]>;
  readonly y?: number;
};

const Pill: React.FC<{ readonly width: number; readonly height: number; readonly y: number }> = ({ width, height, y }) => (
  <div
    style={{
      position: "absolute",
      left: 540 - width / 2,
      top: y - height / 2,
      width,
      height,
      borderRadius: height / 2,
      backgroundColor: "rgba(255,255,255,0.22)",
      border: "2px solid rgba(255,255,255,0.42)",
      backdropFilter: "blur(12px)",
      boxShadow: "0 6px 24px rgba(0,0,0,0.12)",
    }}
  />
);

const Pointer: React.FC<{ readonly x: number; readonly y: number }> = ({ x, y }) => (
  <svg
    width={26}
    height={20}
    viewBox="0 0 26 20"
    style={{ position: "absolute", left: x - 13, top: y, overflow: "visible", filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.3))" }}
  >
    <path d="M2 2 L24 2 L13 18 Z" fill="white" stroke="white" strokeWidth={3} strokeLinejoin="round" />
  </svg>
);

export const RatingBar: React.FC<BarProps> = ({ name, from, durationInFrames, ...rest }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames}>
    <RatingBarInner durationInFrames={durationInFrames} {...rest} />
  </Sequence>
);

const RatingBarInner: React.FC<Omit<BarProps, "name" | "from">> = ({ durationInFrames, pointer, y = LAYOUT.barCenterY }) => {
  const frame = useCurrentFrame();
  const a = blurIn(frame, 0, 6, 8);
  const out = blurOut(frame, durationInFrames);
  const pitch = 77;
  const d = 56;
  const x0 = 540 - (9 * pitch) / 2;
  const idx = keyframes(frame, pointer, easeInOut);
  return (
    <AbsoluteFill style={{ opacity: a.opacity * out.opacity, filter: `${a.filter} blur(${out.blur}px)` }}>
      <Pill width={795} height={74} y={y} />
      {C.scale.map((col, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: x0 + i * pitch - d / 2,
            top: y - d / 2,
            width: d,
            height: d,
            borderRadius: d / 2,
            backgroundColor: col,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: SANS,
            fontWeight: 600,
            fontSize: 24,
            color: C.scaleText[i],
            letterSpacing: "-0.02em",
            boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.08)",
          }}
        >
          {i + 1}
        </div>
      ))}
      <Pointer x={x0 + idx * pitch} y={y - 74 / 2 - 26} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------------ */
/* Calendario: misma píldora del referente con los días de la semana.        */
/* ------------------------------------------------------------------------ */

type CalendarProps = BarProps & {
  readonly eventIndex: number;
  readonly targetIndex: number;
  /** Fotograma (relativo) en que el puntero llega al día objetivo. */
  readonly arriveAt: number;
};

export const CalendarBar: React.FC<CalendarProps> = ({ name, from, durationInFrames, ...rest }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames}>
    <CalendarInner durationInFrames={durationInFrames} {...rest} />
  </Sequence>
);

const DAYS = ["M", "T", "W", "T", "F", "S", "S"];

const CalendarInner: React.FC<Omit<CalendarProps, "name" | "from">> = ({
  durationInFrames,
  pointer,
  eventIndex,
  targetIndex,
  arriveAt,
  y = LAYOUT.barCenterY,
}) => {
  const frame = useCurrentFrame();
  const a = blurIn(frame, 0, 6, 8);
  const out = blurOut(frame, durationInFrames);
  const pitch = 104;
  const d = 78;
  const x0 = 540 - (6 * pitch) / 2;
  const idx = keyframes(frame, pointer, easeInOut);
  const hit = interpolate(frame, [arriveAt, arriveAt + 3, arriveAt + 7], [1, 1.16, 1], clamp);
  const fillP = interpolate(frame, [arriveAt, arriveAt + 3], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: a.opacity * out.opacity, filter: `${a.filter} blur(${out.blur}px)` }}>
      <Pill width={790} height={100} y={y} />
      {DAYS.map((day, i) => {
        const isTarget = i === targetIndex;
        const isEvent = i === eventIndex;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x0 + i * pitch - d / 2,
              top: y - d / 2,
              width: d,
              height: d,
              borderRadius: d / 2,
              backgroundColor: isTarget ? `rgba(163,185,136,${fillP})` : isEvent ? "rgba(228,198,168,0.9)" : "rgba(255,255,255,0.18)",
              border: isEvent ? `3px solid ${BRAND.beige}` : "2px solid rgba(255,255,255,0.35)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: SANS,
              fontWeight: 600,
              fontSize: 34,
              letterSpacing: "-0.02em",
              color: (isTarget && fillP > 0.5) || isEvent ? BRAND.navy : "white",
              scale: String(isTarget ? hit : 1),
            }}
          >
            {day}
          </div>
        );
      })}
      <div
        style={{
          position: "absolute",
          left: x0 + eventIndex * pitch - 70,
          width: 140,
          top: y + 62,
          textAlign: "center",
          fontFamily: SANS,
          fontWeight: 500,
          fontSize: 28,
          letterSpacing: "-0.02em",
          color: "white",
          textShadow: TEXT_SHADOW,
          opacity: interpolate(frame, [8, 14], [0, 1], clamp),
        }}
      >
        event
      </div>
      <Pointer x={x0 + idx * pitch} y={y - 100 / 2 - 26} />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------------ */
/* Halo de color en los bordes (referente) con colores de marca.             */
/* ------------------------------------------------------------------------ */

type GlowProps = {
  readonly name: string;
  readonly from: number;
  readonly durationInFrames: number;
  readonly rgb: string;
  readonly peak?: number;
  /** screen = halo luminoso; normal = viñeta de color (para tonos oscuros). */
  readonly blend?: "screen" | "normal";
};

export const GlowEdges: React.FC<GlowProps> = ({ name, from, durationInFrames, ...rest }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames}>
    <GlowInner durationInFrames={durationInFrames} {...rest} />
  </Sequence>
);

const GlowInner: React.FC<Omit<GlowProps, "name" | "from">> = ({ durationInFrames, rgb, peak = 0.55, blend = "screen" }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 4, durationInFrames - 10, durationInFrames], [0, peak, peak, 0], clamp);
  return (
    <AbsoluteFill
      style={{
        opacity: o,
        boxShadow: `inset 0 0 260px 70px rgba(${rgb},0.95)`,
        background: `radial-gradient(ellipse 75% 60% at 50% 45%, rgba(${rgb},0) 55%, rgba(${rgb},0.35) 100%)`,
        mixBlendMode: blend,
      }}
    />
  );
};

/* ------------------------------------------------------------------------ */
/* Cierre con la identidad del manual: panel salvia + logotipo blanco.       */
/* ------------------------------------------------------------------------ */

export const EndCard: React.FC<{ readonly durationInFrames: number }> = ({ durationInFrames }) => {
  const frame = useCurrentFrame();
  const panelIn = interpolate(frame, [0, 8], [0, 1], { ...clamp, easing: easeOut });
  const logoIn = interpolate(frame, [4, 18], [0, 1], { ...clamp, easing: easeOut });
  const line = blurIn(frame, 12, 6, 10);
  const fadeToBlack = interpolate(frame, [durationInFrames - 21, durationInFrames], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: panelIn }}>
      <AbsoluteFill
        style={{
          backgroundColor: BRAND.sage,
          backgroundImage: "radial-gradient(ellipse 80% 55% at 50% 45%, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 70%)",
        }}
      />
      <Img
        src={staticFile("brand/slate_logo_white.svg")}
        style={{
          position: "absolute",
          width: 560,
          left: 260,
          top: 790,
          opacity: logoIn,
          scale: String(interpolate(logoIn, [0, 1], [0.94, 1])),
          filter: `blur(${interpolate(logoIn, [0, 1], [10, 0])}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 1030,
          left: 0,
          width: 1080,
          textAlign: "center",
          fontFamily: BRAND_SANS,
          fontSize: 40,
          letterSpacing: "0.32em",
          color: "white",
          opacity: line.opacity,
          filter: line.filter,
        }}
      >
        TULSA, OK
      </div>
      <AbsoluteFill style={{ backgroundColor: "black", opacity: fadeToBlack }} />
    </AbsoluteFill>
  );
};
