import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { easeIn, easeOut, kf } from "../lib/anim";

// Envoltorios de transición para usar DENTRO de un <Sequence> (tiempo local de la secuencia).
// Elige los que aparezcan en el catálogo de transiciones de estilo.md y con sus duraciones medidas.

type Dir = "left" | "right" | "up" | "down";
const vec = (d: Dir) => ({ left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] })[d];

/**
 * Empuje / whip con desenfoque de movimiento direccional (filtro SVG).
 * mode "in": entra desde `from` al inicio. mode "out": sale hacia `to` al final (pasa seqDur en segundos).
 */
export const Push: React.FC<{ mode: "in" | "out"; dir?: Dir; dur?: number; seqDur?: number; blurMax?: number; id: string; children: React.ReactNode }> = ({
  mode,
  dir,
  dur = 0.3,
  seqDur = 0,
  blurMax = 60,
  id,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const d = dir ?? (mode === "in" ? "left" : "right");
  const [vx, vy] = vec(d);
  let p: number;
  let blur: number;
  if (mode === "in") {
    p = kf(t, [0, dur], [1, 0], easeOut); // 1 = fuera, 0 = en su sitio
    blur = p * blurMax * Math.min(1, (1 - p) * 4 + 0.2);
  } else {
    p = kf(t, [seqDur - dur, seqDur], [0, 1], easeIn);
    blur = p * blurMax;
  }
  const x = vx * p * width;
  const y = vy * p * height;
  const std = vx !== 0 ? `${blur} 0` : `0 ${blur}`;
  return (
    <AbsoluteFill style={{ translate: `${x}px ${y}px`, filter: blur > 0.5 ? `url(#mb-${id})` : undefined }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id={`mb-${id}`} x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur stdDeviation={std} />
        </filter>
      </svg>
      {children}
    </AbsoluteFill>
  );
};

/** Iris circular de borde suave desde (x, y). */
export const Iris: React.FC<{ x: number; y: number; dur?: number; soft?: number; maxR?: number; children: React.ReactNode }> = ({ x, y, dur = 0.3, soft = 24, maxR = 2400, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const r = kf(frame / fps, [0, dur], [0, maxR], easeIn);
  if (r >= maxR - 1) return <AbsoluteFill>{children}</AbsoluteFill>;
  const mask = `radial-gradient(circle at ${x}px ${y}px, #000 ${r}px, transparent ${r + soft}px)`;
  return <AbsoluteFill style={{ WebkitMaskImage: mask, maskImage: mask }}>{children}</AbsoluteFill>;
};

/** Fundido (cruzado si la secuencia anterior sigue debajo) con desenfoque opcional. */
export const FadeIn: React.FC<{ dur?: number; blur?: number; children: React.ReactNode }> = ({ dur = 0.25, blur = 0, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = kf(frame / fps, [0, dur], [0, 1]);
  return <AbsoluteFill style={{ opacity: p, filter: blur && p < 1 ? `blur(${(1 - p) * blur}px)` : undefined }}>{children}</AbsoluteFill>;
};

/** Destello de color (blanco/negro) al inicio de la secuencia: corte con "flash". */
export const Flash: React.FC<{ color?: string; dur?: number; children: React.ReactNode }> = ({ color = "#fff", dur = 0.2, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const o = kf(frame / fps, [0, dur], [1, 0]);
  return (
    <AbsoluteFill>
      {children}
      {o > 0 && <AbsoluteFill style={{ background: color, opacity: o }} />}
    </AbsoluteFill>
  );
};

/** Zoom de entrada (punch-in / zoom-through): escala desde `from` hasta 1 con desenfoque. */
export const ZoomIn: React.FC<{ from?: number; dur?: number; blur?: number; children: React.ReactNode }> = ({ from = 1.35, dur = 0.35, blur = 14, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = kf(frame / fps, [0, dur], [0, 1]);
  return <AbsoluteFill style={{ scale: `${from + (1 - from) * p}`, filter: p < 1 ? `blur(${(1 - p) * blur}px)` : undefined }}>{children}</AbsoluteFill>;
};

/** Barrido lineal (wipe) con borde suave en la dirección dada. */
export const Wipe: React.FC<{ dir?: Dir; dur?: number; soft?: number; children: React.ReactNode }> = ({ dir = "right", dur = 0.3, soft = 8, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = kf(frame / fps, [0, dur], [0, 100 + soft], easeOut);
  const angle = { right: 90, left: 270, down: 180, up: 0 }[dir];
  const mask = `linear-gradient(${angle}deg, #000 ${p - soft}%, transparent ${p}%)`;
  return <AbsoluteFill style={p >= 100 + soft ? undefined : { WebkitMaskImage: mask, maskImage: mask }}>{children}</AbsoluteFill>;
};
