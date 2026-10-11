import React from "react";
import { staticFile } from "remotion";
import { IMG, type ImgName } from "./Cutout";

/** Recorte que se desintegra con una máscara de ruido (feTurbulence) cuyo umbral avanza con `progress`. */
export const DissolveCutout: React.FC<{ name: ImgName; cx: number; cy: number; width: number; progress: number; rotate?: number; id: string }> = ({
  name,
  cx,
  cy,
  width,
  progress,
  rotate = 0,
  id,
}) => {
  const [nw, nh] = IMG[name];
  const w = width;
  const h = (w * nh) / nw;
  if (progress >= 1) return null;
  const k = 9;
  const thr = 0.18 + progress * 0.72; // el ruido de turbulencia cae mayormente en [0.2, 0.8]
  const b = 0.5 - k * thr;
  return (
    <svg
      width={w}
      height={h}
      style={{ position: "absolute", left: cx - w / 2, top: cy - h / 2, overflow: "visible", rotate: `${rotate}deg`, filter: "drop-shadow(20px 24px 22px rgba(0,0,0,0.45))" }}
    >
      <defs>
        <filter id={`n-${id}`} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="3" seed="4" />
          <feColorMatrix type="matrix" values={`${k} 0 0 0 ${b}  ${k} 0 0 0 ${b}  ${k} 0 0 0 ${b}  0 0 0 0 1`} />
        </filter>
        <mask id={`m-${id}`} maskUnits="userSpaceOnUse" x="0" y="0" width={w} height={h}>
          <rect x="0" y="0" width={w} height={h} fill="white" filter={progress > 0 ? `url(#n-${id})` : undefined} />
        </mask>
      </defs>
      <image href={staticFile(`img/${name}.png`)} x="0" y="0" width={w} height={h} mask={`url(#m-${id})`} />
    </svg>
  );
};
