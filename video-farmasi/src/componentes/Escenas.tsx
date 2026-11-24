import { Video } from "@remotion/media";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Escena } from "../plan";
import { clamp, eOut } from "../util";

// B-roll propio (UGC): corte seco, escala 1,06 → 1,00 en todo el clip, color natural.
export const BRoll: React.FC<{ e: Escena }> = ({ e }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const s = interpolate(frame, [0, durationInFrames], [1.06, 1.0], { ...clamp, easing: eOut });
  return (
    <AbsoluteFill style={{ scale: String(s), backgroundColor: "#000" }}>
      <Video src={staticFile(e.src)} trimBefore={Math.round(e.trim * fps)} muted objectFit="cover" style={{ width: "100%", height: "100%", filter: "contrast(1.05) saturate(1.08) brightness(1.03)" }} />
    </AbsoluteFill>
  );
};
