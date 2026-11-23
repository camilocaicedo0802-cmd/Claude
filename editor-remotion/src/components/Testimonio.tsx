// Prueba social a pantalla completa. Reparto (corrección del cliente): chip «Testimonio» arriba a la izquierda,
// nombre arriba a la derecha, la cara libre en el centro y los subtítulos ABAJO, bajo la barbilla.
// La imagen no se oscurece: solo un velo suave arriba y abajo para que se lean los rótulos.
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
  // Encuadre: 116–122 % pegado abajo, para subir la cara y dejar sitio a los subtítulos; salto en cada corte.
  const cuts = s.cuts.map((c) => c - s.start);
  const z = keys(lt, [
    [0, 1.22],
    [0.7, 1.16],
    [cuts[0] - 0.01, 1.18],
    [cuts[0], 1.22],
    [cuts[1] - 0.01, 1.2],
    [cuts[1], 1.16],
    [s.end - s.start, 1.21],
  ]);
  const vw = W * z;
  const vh = H * z;
  const left = (W - vw) / 2 + 26 * z; // la cara está a la izquierda del plano: se centra un poco
  const top = H - vh;
  const chip = ramp(lt, 0.15, 0.18);
  const name = ramp(lt, 0.4, 0.22, Easing.out(Easing.cubic));
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <Video src={staticFile(s.file)} volume={0.9} style={{ position: "absolute", left, top, width: vw, height: vh, maxWidth: "none", filter: "contrast(1.05) saturate(1.04) brightness(1.03)" }} />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.22) 12%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.55) 74%, rgba(0,0,0,0.78) 100%)" }} />
      {/* Fila superior: chip a la izquierda, nombre a la derecha */}
      <div style={{ position: "absolute", left: 56, top: 238, height: 58, padding: "0 24px", borderRadius: 32, display: "flex", alignItems: "center", gap: 12, background: "rgba(10,10,10,0.7)", border: "1px solid rgba(255,255,255,0.24)", fontFamily: FONT.wide, fontSize: 24, letterSpacing: "0.2em", color: C.white, opacity: chip, translate: `${-14 * (1 - chip)}px 0px` }}>
        <span style={{ width: 12, height: 12, borderRadius: 12, background: C.redDot, boxShadow: "0 0 10px rgba(212,0,42,0.9)" }} />
        TESTIMONIO
      </div>
      <div style={{ position: "absolute", right: 56, top: 226, display: "flex", alignItems: "center", gap: 16, opacity: name, translate: `${16 * (1 - name)}px 0px` }}>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 56, letterSpacing: "-0.04em", lineHeight: 1, color: C.white, textShadow: "0 2px 6px rgba(0,0,0,0.7), 0 4px 22px rgba(0,0,0,0.7)" }}>{nombre}</div>
          <div style={{ marginTop: 6, fontFamily: FONT.wide, fontWeight: 300, fontSize: 24, color: "rgba(255,255,255,0.92)", textShadow: "0 2px 10px rgba(0,0,0,0.85)" }}>{rol}</div>
        </div>
        <span style={{ width: 7, height: 84, borderRadius: 7, background: C.accent, boxShadow: `0 0 16px ${C.accentGlow}` }} />
      </div>
    </AbsoluteFill>
  );
};
