import React from "react";
import { C } from "../theme";

/** Círculo discontinuo alrededor del objeto protagonista: trazo 7 px, guion 22 / hueco 16, giro lento. */
export const DashedCircle: React.FC<{ cx: number; cy: number; d: number; t: number; appearAt?: number; color?: string; opacity?: number; spread?: number }> = ({
  cx,
  cy,
  d,
  t,
  appearAt = 0,
  color = C.ink,
  opacity = 1,
  spread = 0,
}) => {
  const p = Math.min(Math.max((t - appearAt) / 0.5, 0), 1);
  const e = 1 - Math.pow(1 - p, 3);
  if (p <= 0) return null;
  const r = d / 2;
  const circ = 2 * Math.PI * r;
  return (
    <svg
      width={d + 20}
      height={d + 20}
      style={{ position: "absolute", left: cx - d / 2 - 10, top: cy - d / 2 - 10, overflow: "visible", opacity: opacity * Math.min(1, p * 2) }}
    >
      <circle
        cx={r + 10}
        cy={r + 10}
        r={r * (0.86 + 0.14 * e)}
        fill="none"
        stroke={color}
        strokeWidth={7}
        strokeDasharray={`${22} ${16 + spread}`}
        strokeDashoffset={-(t * 10 * circ) / 360}
        strokeLinecap="butt"
        style={{ filter: "drop-shadow(2px 3px 2px rgba(0,0,0,0.18))" }}
        transform={`rotate(${-90 + (1 - e) * -60} ${r + 10} ${r + 10})`}
      />
    </svg>
  );
};
