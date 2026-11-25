import { Video } from "@remotion/media";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Escena } from "../plan";
import { clamp, eOut } from "../util";

// B-roll (UGC): corte seco, escala lenta, color natural.
export const BRoll: React.FC<{ e: Extract<Escena, { tipo: "broll" }> }> = ({ e }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const kb = e.kb ?? [1.06, 1.0];
  const s = interpolate(frame, [0, durationInFrames], kb, { ...clamp, easing: eOut });
  return (
    <AbsoluteFill style={{ scale: String(s), backgroundColor: "#000" }}>
      <Video src={staticFile(e.src)} trimBefore={Math.round(e.trim * fps)} muted objectFit="cover" style={{ width: "100%", height: "100%", filter: "contrast(1.05) saturate(1.08) brightness(1.03)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 52%, rgba(0,0,0,0.38) 66%, rgba(0,0,0,0.38) 76%, rgba(0,0,0,0) 90%)" }} />
    </AbsoluteFill>
  );
};

// Píldora de cierre sobre el plano del producto
export const PildoraCierre: React.FC<{ desde: number }> = ({ desde }) => {
  const frame = useCurrentFrame();
  const d = Math.round(desde * 60);
  if (frame < d) return null;
  const p = interpolate(frame, [d, d + 14], [0, 1], { ...clamp, easing: eOut });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 300 }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: p, translate: `0px ${(1 - p) * 30}px` }}>
        <div style={{ fontFamily: "Inter Tight", fontWeight: 700, fontSize: 40, letterSpacing: "0.32em", color: "#2B2B2B", paddingLeft: "0.32em" }}>FARMASI · NUTRIPLUS</div>
        <div style={{ display: "flex", alignItems: "center", gap: 14, background: "#0FB2EF", borderRadius: 999, padding: "10px 36px 14px 18px", rotate: "-2deg", scale: String(0.7 + 0.3 * p), boxShadow: "0 12px 30px rgba(0,60,110,0.35)" }}>
          <Img src={staticFile("iconos/manzana.png")} style={{ width: 70, height: 70 }} />
          <span style={{ fontFamily: "Inter Tight", fontWeight: 700, fontSize: 56, color: "#fff" }}>Gomitas de sidra de manzana</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Imagen de apoyo a pantalla completa con Ken Burns
export const Imagen: React.FC<{ e: Extract<Escena, { tipo: "imagen" }> }> = ({ e }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const kb = e.kb ?? [1.1, 1.0];
  const s = interpolate(frame, [0, durationInFrames], kb, clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <Img src={staticFile(e.src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: e.foco ?? "50% 50%", scale: String(s), filter: "contrast(1.04) saturate(1.06)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 52%, rgba(0,0,0,0.38) 66%, rgba(0,0,0,0.38) 76%, rgba(0,0,0,0) 90%)" }} />
    </AbsoluteFill>
  );
};
