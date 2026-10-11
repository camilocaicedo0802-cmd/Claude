import React from "react";
import { AbsoluteFill, Img, interpolate, random, staticFile, useCurrentFrame } from "remotion";

/** Grano de película animado (texturas de make_grain.py en public/fx). Ajusta opacity al grano medido. */
export const Grain: React.FC<{ opacity?: number; blend?: React.CSSProperties["mixBlendMode"] }> = ({ opacity = 0.16, blend = "overlay" }) => {
  const frame = useCurrentFrame();
  const ox = Math.floor(random(`gx-${frame}`) * 40);
  const oy = Math.floor(random(`gy-${frame}`) * 40);
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: blend, opacity, overflow: "hidden" }}>
      <Img src={staticFile(`fx/grain_${frame % 8}.png`)} style={{ position: "absolute", left: -ox, top: -oy, width: "calc(100% + 40px)", height: "calc(100% + 40px)" }} />
    </AbsoluteFill>
  );
};

/** Viñeta: strength = oscurecimiento en esquinas (0.12–0.2 típico). */
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.14 }) => (
  <AbsoluteFill style={{ pointerEvents: "none", background: `radial-gradient(ellipse 75% 62% at 50% 48%, rgba(0,0,0,0) 58%, rgba(0,0,0,${strength}) 100%)` }} />
);

/** Halo difuminado detrás de un objeto (negro sobre oscuro, o de color para "glow"). */
export const Halo: React.FC<{ cx: number; cy: number; w: number; h: number; color?: string; blur?: number; opacity?: number }> = ({ cx, cy, w, h, color = "rgba(0,0,0,0.95)", blur = 60, opacity = 1 }) => (
  <div style={{ position: "absolute", left: cx - w / 2, top: cy - h / 2, width: w, height: h, borderRadius: "50%", background: color, filter: `blur(${blur}px)`, opacity }} />
);

/** Etalonaje global aproximado: tinte de color + contraste/saturación vía CSS sobre una capa. */
export const ColorGrade: React.FC<{ tint?: string; tintOpacity?: number; blend?: React.CSSProperties["mixBlendMode"] }> = ({ tint = "#ff8a3d", tintOpacity = 0.08, blend = "soft-light" }) => (
  <AbsoluteFill style={{ pointerEvents: "none", background: tint, opacity: tintOpacity, mixBlendMode: blend }} />
);

/** Fuga de luz suave que cruza el cuadro (para referencias cálidas/cinemáticas). */
export const LightLeak: React.FC<{ from: number; dur: number; color?: string }> = ({ from, dur, color = "255,170,90" }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [from, from + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (p <= 0 || p >= 1) return null;
  const o = Math.sin(p * Math.PI);
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        mixBlendMode: "screen",
        opacity: o * 0.85,
        background: `radial-gradient(ellipse 60% 45% at ${-20 + p * 140}% ${30 + p * 30}%, rgba(${color},0.9) 0%, rgba(${color},0) 70%)`,
      }}
    />
  );
};

/** Barras/letterbox o marco (algunas referencias encuadran el vídeo). */
export const Letterbox: React.FC<{ size: number; color?: string }> = ({ size, color = "#000" }) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: size, background: color }} />
    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: size, background: color }} />
  </AbsoluteFill>
);
