import React from "react";
import { AbsoluteFill } from "remotion";
import { EditorialBlock } from "../captions/EditorialBlock";
import { KaraokePage } from "../captions/KaraokePage";
import { WordPop } from "../captions/WordPop";
import { BrushPath } from "../components/BrushPath";
import { Camera } from "../components/Camera";
import { DashedCircle } from "../components/DashedCircle";
import { Phone } from "../components/Phone";
import { easeInOut, kf, kfs, springy } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C, CAPTION_LOOKS, F } from "../theme";

/**
 * Escena de demostración de la plantilla (no es un estilo a copiar): cámara que viaja por un "mundo",
 * objeto con círculo discontinuo, trazo de pincel y los tres sistemas de subtítulos.
 * `variant` permite previsualizar cada sistema: "editorial" | "wordpop" | "karaoke".
 */
export const ExampleScene: React.FC<{ start?: number; variant?: "editorial" | "wordpop" | "karaoke" }> = ({ start = 0, variant = "editorial" }) => {
  const { t, g } = useSceneTime(start);
  const cy = kfs(t, [0, 1.2, 2.6], [960, 960, 1250]);
  const pop = springy(t, 0.1, 0.5, 0.08);
  return (
    <AbsoluteFill style={{ backgroundColor: variant === "editorial" ? C.bgLight : C.bgDark }}>
      <Camera cx={540} cy={cy} scale={kf(t, [0, 3], [1, 1.06], easeInOut)}>
        <BrushPath id="ex" d="M 1100 -100 C 900 300, 1080 600, 900 900 S 300 1300, 400 1900" progress={kf(t, [0.2, 2.8], [0, 1], easeInOut)} color={variant === "editorial" ? "#161616" : "#e8e8e8"} />
        <DashedCircle cx={540} cy={1050} d={640} t={t} appearAt={0.1} color={variant === "editorial" ? C.ink : C.inkOnDark} />
        <Phone cx={540} cy={1050} w={300} scale={pop} rotate={(1 - pop) * 12}>
          <div style={{ position: "absolute", top: 80, width: "100%", textAlign: "center", fontFamily: F.primary, fontWeight: 800, fontSize: 64, color: "#eee" }}>23:47</div>
        </Phone>
        {variant === "editorial" && <EditorialBlock g={g} look={CAPTION_LOOKS.editorialLight} guide={[0, 2]} keyw={[3, 3]} x={140} y={330} />}
      </Camera>
      {variant === "wordpop" && (
        <WordPop g={g} y={1500} group={1} highlight={[3, 5]} look={{ font: F.primary, weight: 900, size: 120, color: "#fff", tracking: "-0.02em", uppercase: true, stroke: "10px #000" }} />
      )}
      {variant === "karaoke" && (
        <KaraokePage g={g} y={1550} look={{ font: F.primary, weight: 800, size: 78, color: "#fff", tracking: "-0.01em", uppercase: false, shadow: "0 6px 18px rgba(0,0,0,0.6)" }} active={{ mode: "box", color: "#FFD400", textColor: "#111" }} />
      )}
    </AbsoluteFill>
  );
};
