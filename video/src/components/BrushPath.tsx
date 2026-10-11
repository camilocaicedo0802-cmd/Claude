import React from "react";
import { evolvePath } from "@remotion/paths";

/**
 * Trazo curvo tipo pincel (estilo.md §5): línea negra gruesa con bordes suaves y sombra,
 * que serpentea entre objetos y se dibuja según avanza la cámara.
 */
export const BrushPath: React.FC<{ d: string; progress: number; width?: number; color?: string; id: string; opacity?: number; plain?: boolean }> = ({
  d,
  progress,
  width = 22,
  color = "#161616",
  id,
  opacity = 1,
  plain = false,
}) => {
  if (progress <= 0) return null;
  const ev = evolvePath(Math.min(progress, 1), d);
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity }} width={1} height={1}>
      <defs>
        <filter id={`soft-${id}`} x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="1.4" />
        </filter>
        <filter id={`shadow-${id}`} x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="9" />
        </filter>
      </defs>
      {!plain && <path d={d} fill="none" stroke="rgba(0,0,0,0.32)" strokeWidth={width * 1.1} strokeLinecap="round" transform="translate(14 18)" filter={`url(#shadow-${id})`} strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} />}
      <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" filter={`url(#soft-${id})`} strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} />
      {!plain && <path d={d} fill="none" stroke="rgba(255,255,255,0.13)" strokeWidth={width * 0.22} strokeLinecap="round" transform="translate(-3 -4)" filter={`url(#soft-${id})`} strokeDasharray={ev.strokeDasharray} strokeDashoffset={ev.strokeDashoffset} />}
    </svg>
  );
};
