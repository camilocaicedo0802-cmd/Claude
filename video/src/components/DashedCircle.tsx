import React from "react";
import { C } from "../theme";

/**
 * Círculo discontinuo alrededor del objeto protagonista: trazo 7 px, guion 22 / hueco 16 (idéntico en todas las escenas),
 * giro lento. v2: se DIBUJA progresivamente (máscara que recorre la circunferencia) en `drawDur` segundos.
 */
export const DashedCircle: React.FC<{
  cx: number;
  cy: number;
  d: number;
  t: number;
  appearAt?: number;
  drawDur?: number;
  color?: string;
  opacity?: number;
  spread?: number;
  id?: string;
}> = ({ cx, cy, d, t, appearAt = 0, drawDur = 0.8, color = C.ink, opacity = 1, spread = 0, id = "dc" }) => {
  const p = Math.min(Math.max((t - appearAt) / drawDur, 0), 1);
  if (p <= 0 || opacity <= 0) return null;
  const e = 1 - Math.pow(1 - p, 3); // desaceleración suave
  const r = d / 2;
  const c = r + 10;
  const circ = 2 * Math.PI * r;
  return (
    <svg width={d + 20} height={d + 20} style={{ position: "absolute", left: cx - c, top: cy - c, overflow: "visible", opacity }}>
      <defs>
        <mask id={`draw-${id}`} maskUnits="userSpaceOnUse" x={-20} y={-20} width={d + 60} height={d + 60}>
          <circle cx={c} cy={c} r={r} fill="none" stroke="white" strokeWidth={24} strokeDasharray={`${e * circ} ${circ}`} transform={`rotate(-90 ${c} ${c})`} />
        </mask>
      </defs>
      <g mask={p < 1 ? `url(#draw-${id})` : undefined}>
        <circle
          cx={c}
          cy={c}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={7}
          strokeDasharray={`22 ${16 + spread}`}
          strokeDashoffset={-(t * 10 * circ) / 360}
          style={{ filter: "drop-shadow(2px 3px 2px rgba(0,0,0,0.18))" }}
          transform={`rotate(-90 ${c} ${c})`}
        />
      </g>
    </svg>
  );
};
