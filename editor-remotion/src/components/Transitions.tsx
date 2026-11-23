// Transiciones de la referencia (estilo.md §5): barras verticales + destello, glitch RGB y desenfoque.
import React from "react";
import { AbsoluteFill, Easing } from "remotion";
import { keys, ramp, rnd } from "../anim";
import { H, W } from "../theme";

/** ≈50 barras blancas verticales (barra 11 px, hueco 10 px): suben en 133 ms hasta casi blanco y bajan en 150 ms. */
export const BarsFlash: React.FC<{ t: number; peak: number }> = ({ t, peak }) => {
  const a = keys(t, [
    [peak - 0.133, 0],
    [peak, 1],
    [peak + 0.15, 0],
  ], Easing.inOut(Easing.quad));
  if (a <= 0) return null;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ backgroundColor: `rgba(255,255,255,${0.86 * a * a})` }} />
      <AbsoluteFill
        style={{
          opacity: Math.min(1, a * 1.25),
          backgroundImage: "repeating-linear-gradient(90deg, rgba(255,255,255,0.95) 0px, rgba(255,255,255,0.95) 11px, rgba(255,255,255,0) 11px, rgba(255,255,255,0) 21px)",
        }}
      />
    </AbsoluteFill>
  );
};
export const barsBlur = (t: number, peak: number) => keys(t, [[peak - 0.12, 0], [peak, 16], [peak + 0.2, 0]]);

/** Glitch de 167 ms: franjas desplazadas, separación RGB simulada y bajada de brillo; termina en corte seco. */
export const Glitch: React.FC<{ t: number; at: number }> = ({ t, at }) => {
  const dur = 0.167;
  if (t < at || t >= at + dur) return null;
  const k = Math.floor((t - at) * 60);
  const bands = [0, 1, 2, 3, 4, 5, 6].map((i) => ({
    top: rnd(k * 7 + i) * H,
    h: 6 + rnd(k * 13 + i * 3) * 46,
    dx: (rnd(k * 17 + i * 5) - 0.5) * 60,
    c: i % 2 === 0 ? "rgba(255,0,60,0.2)" : "rgba(0,255,220,0.18)",
  }));
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ backgroundColor: "rgba(0,0,0,0.32)" }} />
      {bands.map((b, i) => (
        <div key={i} style={{ position: "absolute", left: b.dx, top: b.top, width: W, height: b.h, background: b.c, mixBlendMode: "screen" }} />
      ))}
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(255,255,255,0.07) 0px, rgba(255,255,255,0.07) 2px, rgba(0,0,0,0) 2px, rgba(0,0,0,0) 6px)" }} />
    </AbsoluteFill>
  );
};
export const glitchShift = (t: number, at: number) => {
  if (t < at || t >= at + 0.167) return 0;
  const k = Math.floor((t - at) * 60);
  return (rnd(k * 3.3) - 0.5) * 30;
};

/** Desenfoque 0→20 px→0 en 167 ms (la «foto» del gancho). */
export const blurPulse = (t: number, at: number) => keys(t, [[at, 0], [at + 0.07, 20], [at + 0.167, 0]]);
export { ramp };
