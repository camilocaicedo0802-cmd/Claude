import type { Caption } from "@remotion/captions";
import React from "react";
import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { blurIn, blurOut, clamp, easeInOut, easeOut, keyframes } from "../anim";
import { C, LAYOUT, SANS, SERIF, TEXT_SHADOW } from "../theme";

/* ------------------------------------------------------------------------ */
/* Iconos de línea (sustituyen a los emojis: el cliente no quiere emojis).   */
/* ------------------------------------------------------------------------ */

export type IconKind = "pin" | "sparkle" | "leaf" | "ornament" | "champagne" | "calendar";

const ICONS: Record<IconKind, { paths: string[]; circles?: Array<[number, number, number]> }> = {
  pin: {
    paths: ["M50 94 C38 78 20 60 20 40 A30 30 0 0 1 80 40 C80 60 62 78 50 94 Z"],
    circles: [[50, 40, 11]],
  },
  sparkle: {
    paths: [
      "M46 10 C49 38 57 46 86 50 C57 54 49 62 46 90 C43 62 35 54 6 50 C35 46 43 38 46 10 Z",
      "M82 8 C83 17 86 20 95 21 C86 22 83 25 82 34 C81 25 78 22 69 21 C78 20 81 17 82 8 Z",
    ],
  },
  leaf: {
    paths: [
      "M50 88 C26 76 14 52 22 22 C36 30 46 22 50 8 C54 22 64 30 78 22 C86 52 74 76 50 88 Z",
      "M50 96 L50 30",
      "M50 66 L34 50",
      "M50 54 L66 40",
    ],
  },
  ornament: {
    paths: ["M42 24 L58 24 L58 32 L42 32 Z", "M50 24 C46 14 56 10 56 18", "M23 56 C40 66 60 66 77 56", "M25 70 C40 78 60 78 75 70"],
    circles: [[50, 60, 28]],
  },
  champagne: {
    paths: [
      "M18 22 L40 18 L42 50 C42 58 33 60 31 53 Z",
      "M36 57 L40 82",
      "M30 84 L48 81",
      "M82 22 L60 18 L58 50 C58 58 67 60 69 53 Z",
      "M64 57 L60 82",
      "M70 84 L52 81",
      "M50 4 L50 11",
      "M42 8 L39 4",
      "M58 8 L61 4",
    ],
  },
  calendar: {
    paths: ["M16 22 L84 22 L84 86 L16 86 Z", "M16 40 L84 40", "M33 12 L33 30", "M67 12 L67 30", "M30 56 L36 56", "M47 56 L53 56", "M64 56 L70 56", "M30 70 L36 70", "M47 70 L53 70"],
  },
};

type LineIconProps = {
  readonly kind: IconKind;
  readonly size: number;
  readonly color?: string;
  /** Fotograma (relativo al padre) en que empieza a dibujarse. */
  readonly at: number;
  readonly drawFrames?: number;
  readonly strokeWidth?: number;
  readonly fill?: boolean;
  readonly style?: React.CSSProperties;
};

export const LineIcon: React.FC<LineIconProps> = ({
  kind,
  size,
  color = C.white,
  at,
  drawFrames = 12,
  strokeWidth = 4,
  fill = false,
  style,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + drawFrames], [0, 1], { ...clamp, easing: easeOut });
  const pop = interpolate(frame, [at, at + 3, at + 6], [0, 1.12, 1], clamp);
  const icon = ICONS[kind];
  const common = {
    pathLength: 1,
    fill: fill ? color : "none",
    fillOpacity: fill ? p : 0,
    stroke: color,
    strokeWidth,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeDasharray: 1,
    strokeDashoffset: 1 - p,
  };
  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      style={{ overflow: "visible", scale: String(fill ? pop : 1), filter: "drop-shadow(0 2px 8px rgba(0,0,0,0.25))", ...style }}
    >
      {icon.paths.map((d) => (
        <path key={d} d={d} {...common} />
      ))}
      {icon.circles?.map(([cx, cy, r]) => <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r={r} {...common} fill="none" />)}
    </svg>
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

type WordProps = {
  readonly at: number;
  readonly x: number;
  readonly y: number;
  readonly size: number;
  readonly children: React.ReactNode;
  readonly serif?: boolean;
  readonly weight?: number;
  readonly color?: string;
  readonly align?: "left" | "center";
};

/** Palabra que entra con fundido + desenfoque en 4 fotogramas y se queda. */
export const Word: React.FC<WordProps> = ({ at, x, y, size, children, serif = false, weight = 700, color = C.white, align = "left" }) => {
  const frame = useCurrentFrame();
  const a = blurIn(frame, at, 4, 12);
  const rise = interpolate(frame, [at, at + 4], [serif ? 24 : 12, 0], { ...clamp, easing: easeOut });
  const sc = serif ? interpolate(frame, [at, at + 4], [0.9, 1], { ...clamp, easing: easeOut }) : 1;
  return (
    <div
      style={{
        position: "absolute",
        left: align === "center" ? 0 : x,
        width: align === "center" ? 1080 : undefined,
        textAlign: align,
        top: y,
        fontFamily: serif ? SERIF : SANS,
        fontStyle: serif ? "italic" : "normal",
        fontWeight: serif ? 400 : weight,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: serif ? "-0.01em" : "-0.04em",
        color,
        whiteSpace: "nowrap",
        textShadow: TEXT_SHADOW,
        opacity: a.opacity,
        filter: a.filter,
        translate: `0px ${rise}px`,
        scale: String(sc),
        transformOrigin: "left center",
      }}
    >
      {children}
    </div>
  );
};

/** Icono suelto colocado en coordenadas absolutas dentro de una cascada. */
export const PlacedIcon: React.FC<LineIconProps & { readonly x: number; readonly y: number }> = ({ x, y, ...icon }) => (
  <div style={{ position: "absolute", left: x, top: y }}>
    <LineIcon {...icon} />
  </div>
);

/* ------------------------------------------------------------------------ */
/* Ítem numerado (referente "1. Mal aliento").                               */
/* ------------------------------------------------------------------------ */

type ItemLine = { readonly text: string; readonly at: number };

type NumberedItemProps = {
  readonly name: string;
  readonly from: number;
  readonly durationInFrames: number;
  /** "1." … o null para usar un icono en lugar del número. */
  readonly num: string | null;
  readonly lines: ReadonlyArray<ItemLine>;
  readonly icon?: { readonly kind: IconKind; readonly at: number };
  readonly leadIcon?: IconKind;
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
  icon,
  leadIcon,
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
        <div
          style={{
            width: numW,
            display: "flex",
            justifyContent: "flex-end",
            translate: `${slide}px 0px`,
            scale: String(pop),
          }}
        >
          {num ? (
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
          ) : leadIcon ? (
            <LineIcon kind={leadIcon} size={96} at={0} drawFrames={10} strokeWidth={5} />
          ) : null}
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
        {icon ? <LineIcon kind={icon.kind} size={92} at={icon.at} strokeWidth={4.5} style={{ marginLeft: 8 }} /> : null}
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
/* Barra de valoración 1–10 (objeto recurrente del referente).               */
/* ------------------------------------------------------------------------ */

type BarProps = {
  readonly name: string;
  readonly from: number;
  readonly durationInFrames: number;
  /** [fotograma, índice] del puntero, relativo al inicio de la barra. */
  readonly pointer: ReadonlyArray<readonly [number, number]>;
  readonly y?: number;
};

const Pill: React.FC<{ readonly width: number; readonly height: number; readonly y: number; readonly children: React.ReactNode }> = ({
  width,
  height,
  y,
  children,
}) => (
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
  >
    {children}
  </div>
);

const Pointer: React.FC<{ readonly x: number; readonly y: number }> = ({ x, y }) => (
  <svg width={26} height={20} viewBox="0 0 26 20" style={{ position: "absolute", left: x - 13, top: y, overflow: "visible", filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.3))" }}>
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
  const pillW = 795;
  const pitch = 77;
  const d = 56;
  const x0 = 540 - (9 * pitch) / 2;
  const idx = keyframes(frame, pointer, easeInOut);
  return (
    <AbsoluteFill style={{ opacity: a.opacity * out.opacity, filter: `${a.filter} blur(${out.blur}px)` }}>
      <Pill width={pillW} height={74} y={y}>
        <></>
      </Pill>
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
            color: "white",
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
      <Pill width={790} height={100} y={y}>
        <></>
      </Pill>
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
              backgroundColor: isTarget ? `rgba(252,242,16,${fillP})` : "rgba(255,255,255,0.18)",
              border: isEvent ? "3px solid rgba(255,255,255,0.95)" : "2px solid rgba(255,255,255,0.35)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: SANS,
              fontWeight: 600,
              fontSize: 34,
              letterSpacing: "-0.02em",
              color: isTarget && fillP > 0.5 ? "#1C1A14" : "white",
              scale: String(isTarget ? hit : 1),
            }}
          >
            {day}
          </div>
        );
      })}
      <div style={{ position: "absolute", left: x0 + eventIndex * pitch - 20, top: y + 58 }}>
        <LineIcon kind="sparkle" size={40} color={C.yellow} at={8} fill strokeWidth={3} />
      </div>
      <div
        style={{
          position: "absolute",
          left: x0 + eventIndex * pitch - 60,
          width: 120,
          top: y + 100,
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
/* Halo de color en los bordes + punch-in (referente: nota 10 → rojo).       */
/* ------------------------------------------------------------------------ */

type GlowProps = {
  readonly name: string;
  readonly from: number;
  readonly durationInFrames: number;
  readonly rgb: string;
  readonly peak?: number;
};

export const GlowEdges: React.FC<GlowProps> = ({ name, from, durationInFrames, ...rest }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames}>
    <GlowInner durationInFrames={durationInFrames} {...rest} />
  </Sequence>
);

const GlowInner: React.FC<{ readonly durationInFrames: number; readonly rgb: string; readonly peak?: number }> = ({
  durationInFrames,
  rgb,
  peak = 0.55,
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 4, durationInFrames - 10, durationInFrames], [0, peak, peak, 0], clamp);
  return (
    <AbsoluteFill
      style={{
        opacity: o,
        boxShadow: `inset 0 0 260px 70px rgba(${rgb},0.95)`,
        background: `radial-gradient(ellipse 75% 60% at 50% 45%, rgba(${rgb},0) 55%, rgba(${rgb},0.35) 100%)`,
        mixBlendMode: "screen",
      }}
    />
  );
};

/* ------------------------------------------------------------------------ */
/* Cierre con logotipo (manual de marca).                                     */
/* ------------------------------------------------------------------------ */

export const EndCardOverlay: React.FC<{ readonly durationInFrames: number }> = ({ durationInFrames }) => {
  const frame = useCurrentFrame();
  const logoIn = interpolate(frame, [2, 16], [0, 1], { ...clamp, easing: easeOut });
  const fadeToBlack = interpolate(frame, [durationInFrames - 21, durationInFrames], [0, 1], clamp);
  const line = blurIn(frame, 10, 6, 10);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: "rgba(28,24,18,0.34)" }} />
      <Img
        src={staticFile("brand/slate_logo_white.svg")}
        style={{
          position: "absolute",
          width: 560,
          left: 260,
          top: 760,
          opacity: logoIn,
          scale: String(interpolate(logoIn, [0, 1], [0.94, 1])),
          filter: `blur(${interpolate(logoIn, [0, 1], [10, 0])}px) drop-shadow(0 4px 18px rgba(0,0,0,0.25))`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 1010,
          left: 0,
          width: 1080,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: 14,
          opacity: line.opacity,
          filter: line.filter,
        }}
      >
        <LineIcon kind="pin" size={50} at={10} strokeWidth={6} />
        <span style={{ fontFamily: SANS, fontWeight: 500, fontSize: 50, letterSpacing: "-0.03em", color: "white", textShadow: TEXT_SHADOW }}>
          Tulsa, OK
        </span>
      </div>
      <AbsoluteFill style={{ backgroundColor: "black", opacity: fadeToBlack }} />
    </AbsoluteFill>
  );
};

export { easeInOut };
