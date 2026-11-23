// Prueba social a pantalla completa (corrección del cliente): el vídeo vertical del alumno ocupa todo el lienzo,
// con chip «Testimonio» y rótulo de nombre. Los subtítulos van arriba, sobre la pared (la cara queda en el centro).
import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { keys, ramp } from "../anim";
import { C, FONT, H, W } from "../theme";
import { Segment } from "../timeline";

export const Testimonio: React.FC<{ s: Segment; nombre: string; rol: string }> = ({ s, nombre, rol }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lt = frame / fps; // tiempo local
  // Encuadre: 114 % y desplazado hacia arriba para subir la cara; salto de zoom en cada corte de silencio.
  const cuts = s.cuts.map((c) => c - s.start);
  const z = keys(lt, [
    [0, 1.24],
    [0.7, 1.12],
    [cuts[0] - 0.01, 1.15],
    [cuts[0], 1.22],
    [cuts[1] - 0.01, 1.27],
    [cuts[1], 1.13],
    [s.end - s.start, 1.2],
  ]);
  const vw = W * z;
  const vh = H * z;
  const left = (W - vw) / 2 - 10 * z;
  const top = H - vh; // pegado abajo: la cara sube
  const chip = ramp(lt, 0.15, 0.18);
  const name = ramp(lt, 0.4, 0.22, Easing.out(Easing.cubic));
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <Video src={staticFile(s.file)} volume={0.9} style={{ position: "absolute", left, top, width: vw, height: vh, maxWidth: "none", filter: "contrast(1.1) saturate(0.92) brightness(0.9)" }} />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,0.72) 0%, rgba(0,0,0,0.5) 24%, rgba(0,0,0,0.12) 40%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.66) 100%)" }} />
      <div style={{ position: "absolute", left: 56, top: 236, height: 58, padding: "0 24px", borderRadius: 32, display: "flex", alignItems: "center", gap: 12, background: "rgba(10,10,10,0.72)", border: "1px solid rgba(255,255,255,0.22)", fontFamily: FONT.wide, fontSize: 24, letterSpacing: "0.2em", color: C.white, opacity: chip, translate: `${-14 * (1 - chip)}px 0px` }}>
        <span style={{ width: 12, height: 12, borderRadius: 12, background: C.redDot, boxShadow: "0 0 10px rgba(212,0,42,0.9)" }} />
        TESTIMONIO
      </div>
      <div style={{ position: "absolute", left: 60, top: 1392, opacity: name, translate: `0px ${18 * (1 - name)}px` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ width: 7, height: 74, borderRadius: 7, background: C.accent, boxShadow: `0 0 16px ${C.accentGlow}` }} />
          <div>
            <div style={{ fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 66, letterSpacing: "-0.04em", lineHeight: 1, color: C.white, textShadow: "0 4px 18px rgba(0,0,0,0.8)" }}>{nombre}</div>
            <div style={{ marginTop: 8, fontFamily: FONT.wide, fontWeight: 300, fontSize: 28, color: "rgba(255,255,255,0.86)", textShadow: "0 2px 10px rgba(0,0,0,0.8)" }}>{rol}</div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
