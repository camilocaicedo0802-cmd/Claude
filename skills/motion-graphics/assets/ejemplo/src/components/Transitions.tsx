import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { easeIn, easeOut, kf } from "../lib/anim";
import { W } from "../theme";

/**
 * Empuje horizontal (whip) de 0.25–0.3 s con desenfoque de movimiento direccional (estilo.md §5).
 * mode "in": entra desde la izquierda al principio de la secuencia.
 * mode "out": sale hacia la derecha al final de la secuencia.
 */
export const Push: React.FC<{ mode: "in" | "out"; dur?: number; seqDur?: number; id: string; children: React.ReactNode }> = ({ mode, dur = 0.3, seqDur = 0, id, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const end = seqDur;
  let x = 0;
  let blur = 0;
  if (mode === "in") {
    const p = kf(t, [0, dur], [0, 1], easeOut);
    x = (p - 1) * W;
    blur = (1 - p) * 60 * Math.min(1, p * 4);
  } else {
    const p = kf(t, [end - dur, end], [0, 1], easeIn);
    x = p * W;
    blur = p * 60;
  }
  return (
    <AbsoluteFill style={{ translate: `${x}px 0px`, filter: blur > 0.5 ? `url(#hblur-${id})` : undefined }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id={`hblur-${id}`} x="-10%" y="0" width="120%" height="100%">
          <feGaussianBlur stdDeviation={`${blur} 0`} />
        </filter>
      </svg>
      {children}
    </AbsoluteFill>
  );
};

/** Iris circular con borde suave: revela el contenido desde (x, y). */
export const Iris: React.FC<{ x: number; y: number; dur?: number; soft?: number; children: React.ReactNode; maxR?: number }> = ({
  x,
  y,
  dur = 0.3,
  soft = 24,
  maxR = 2300,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const r = kf(t, [0, dur], [0, maxR], easeIn);
  const done = r >= maxR - 1;
  const mask = `radial-gradient(circle at ${x}px ${y}px, #000 ${r}px, transparent ${r + soft}px)`;
  return <AbsoluteFill style={done ? undefined : { WebkitMaskImage: mask, maskImage: mask }}>{children}</AbsoluteFill>;
};
