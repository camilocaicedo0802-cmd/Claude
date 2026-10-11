import React from "react";
import { AbsoluteFill, Img, random, staticFile, useCurrentFrame } from "remotion";

/** Grano de película animado: cambia cada frame (estilo.md §7). */
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.16 }) => {
  const frame = useCurrentFrame();
  const i = frame % 8;
  const ox = Math.floor(random(`gx-${frame}`) * 40);
  const oy = Math.floor(random(`gy-${frame}`) * 40);
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "overlay", opacity, overflow: "hidden" }}>
      <Img src={staticFile(`fx/grain_${i}.png`)} style={{ position: "absolute", left: -ox, top: -oy, width: 1080 + 40, height: 1920 + 40 }} />
    </AbsoluteFill>
  );
};

/** Viñeta suave (12–15 % en esquinas). */
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.2 }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: `radial-gradient(ellipse 75% 62% at 50% 48%, rgba(0,0,0,0) 58%, rgba(0,0,0,${strength}) 100%)`,
    }}
  />
);

/** Halo negro difuminado detrás de objetos sobre fondo oscuro. */
export const Halo: React.FC<{ cx: number; cy: number; w: number; h: number; opacity?: number }> = ({ cx, cy, w, h, opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      left: cx - w / 2,
      top: cy - h / 2,
      width: w,
      height: h,
      borderRadius: "50%",
      background: "rgba(0,0,0,0.95)",
      filter: "blur(60px)",
      opacity,
    }}
  />
);
