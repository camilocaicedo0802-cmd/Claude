import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { kf, springy } from "../lib/anim";

/**
 * Metraje principal (persona a cámara, pantalla, etc.) con "zoom punches": saltos de encuadre
 * en instantes concretos, típicos de talking-heads editados (alternar 1.0 / 1.15 / 1.3 en cada corte o frase).
 * Pasa el vídeo YA cortado (scripts/jumpcut.py quita silencios) y transcribe ESE archivo para que
 * los subtítulos y los punches compartan línea de tiempo.
 */
export type Punch = { t: number; scale: number; x?: number; y?: number; smooth?: boolean };

export const ARoll: React.FC<{ src: string; punches?: Punch[]; volume?: number; fit?: "cover" | "contain"; trimBefore?: number }> = ({ src, punches = [], volume = 1, fit = "cover", trimBefore = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  // punch activo = el último cuyo t <= ahora
  let cur: Punch = { t: 0, scale: 1, x: 50, y: 40 };
  let prev: Punch = cur;
  for (const p of punches) {
    if (p.t <= t) {
      prev = cur;
      cur = p;
    }
  }
  const k = cur.smooth ? kf(t, [cur.t, cur.t + 0.35], [0, 1]) : springy(t, cur.t, 0.12, 0);
  const scale = prev.scale + (cur.scale - prev.scale) * Math.min(1, k);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ scale: `${scale}`, transformOrigin: `${cur.x ?? 50}% ${cur.y ?? 40}%` }}>
        <Video src={src.startsWith("http") ? src : staticFile(src)} trimBefore={Math.round(trimBefore * fps)} volume={volume} objectFit={fit} style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
