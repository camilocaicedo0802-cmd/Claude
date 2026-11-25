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
    </AbsoluteFill>
  );
};
