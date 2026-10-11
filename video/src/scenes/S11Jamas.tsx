import React from "react";
import { AbsoluteFill, random } from "remotion";
import { Camera } from "../components/Camera";
import { Cutout, IMG } from "../components/Cutout";
import { Halo } from "../components/Overlays";
import { TextBlock } from "../components/TextBlock";
import { easeInOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S11 = { start: 38.55, end: 41.45 };

const HG = { cx: 540, cy: 1190, h: 980 };
const KH = HG.h / IMG.hourglass_dark[1];
const HG_W = IMG.hourglass_dark[0] * KH;
const NECK = { x: HG.cx - HG_W / 2 + 350 * KH, y: HG.cy - HG.h / 2 + 448 * KH };
const PILE_Y = HG.cy - HG.h / 2 + 600 * KH;

/** Cierre emocional (oscuro): reloj de arena cayendo; "pero tu tiempo JAMÁS" con jerarquía invertida. */
export const S11Jamas: React.FC<{ start?: number }> = ({ start = S11.start }) => {
  const { t, g } = useSceneTime(start);
  const fadeIn = kf(t, [0, 0.3], [1, 0]);
  const punch = g > 40.27 ? 0.05 * Math.sin(Math.min(1, (g - 40.27) / 0.4) * Math.PI * 0.5) : 0;
  const scale = kf(t, [0, 2.9], [1.0, 1.1], easeInOut) + punch;

  return (
    <AbsoluteFill style={{ backgroundColor: C.night }}>
      <Camera cx={540} cy={1000} scale={scale}>
        <Halo cx={HG.cx} cy={HG.cy} w={1000} h={1300} />
        <Cutout name="hourglass_dark" cx={HG.cx} cy={HG.cy} height={HG.h} shadow={false} brightness={0.92} />
        {/* hilo de arena que cae */}
        {new Array(46).fill(0).map((_, i) => {
          const ph = (t * 1.4 + i / 46) % 1;
          const x = NECK.x + (random(`sx-${i}`) - 0.5) * 5;
          const y = NECK.y + ph * (PILE_Y - NECK.y);
          return <div key={i} style={{ position: "absolute", left: x - 1.5, top: y, width: 3, height: 5, borderRadius: 2, background: "#e2e2e2", opacity: 0.85 }} />;
        })}
      </Camera>
      <TextBlock g={g} theme="dark" guide={[74, 76]} keyw={[77, 77]} x={130} y={170} guideSize={58} keySize={250} />
      <AbsoluteFill style={{ backgroundColor: C.night, opacity: fadeIn }} />
    </AbsoluteFill>
  );
};
