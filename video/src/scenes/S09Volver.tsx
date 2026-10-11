import React from "react";
import { AbsoluteFill } from "remotion";
import { BrushPath } from "../components/BrushPath";
import { Camera } from "../components/Camera";
import { Cutout } from "../components/Cutout";
import { DashedCircle } from "../components/DashedCircle";
import { LoopArrow } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeInOut, kf, kfs } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S09 = { start: 33.75, end: 38.8 };

/** E9–E10 (papel, entra con iris): cerebro "recuerda ESTO" -> baja a las monedas "el dinero PUEDE VOLVER". */
export const S09Volver: React.FC<{ start?: number }> = ({ start = S09.start }) => {
  const { t, g } = useSceneTime(start);
  const cy = kfs(g, [33.75, 35.45, 36.15, 38.8], [960, 990, 2150, 2190]);
  const scale = kf(t, [0, 5], [1.0, 1.06], easeInOut);
  const cx = 540 + Math.sin(t * 0.8) * 8;

  const brainPop = g > 34.94 ? 1 + 0.06 * Math.sin(Math.min(1, (g - 34.94) / 0.3) * Math.PI) : 1;
  const coinsPop = g > 37.5 ? 1 + 0.06 * Math.sin(Math.min(1, (g - 37.5) / 0.35) * Math.PI) : 1;
  const loop = kf(g, [37.5, 38.1], [0, 1], easeInOut);
  const darken = kf(g, [38.35, 38.8], [0, 1], easeInOut);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <Camera cx={cx} cy={cy} scale={scale}>
        <BrushPath id="s09" d="M 880 1320 C 1090 1560, 1030 1770, 960 1990 S 1110 2300, 1010 2620 S 900 2900, 1080 3100" progress={kf(g, [35.3, 37.0], [0, 1], easeInOut)} />
        <DashedCircle cx={540} cy={1020} d={660} t={t} appearAt={0.15} />
        <Cutout name="brain" cx={540} cy={1020 + Math.sin(t * 1.6) * 6} width={480} scale={brainPop} />
        <TextBlock g={g} guide={[68, 68]} keyw={[69, 69]} x={150} y={330} keySize={150} />

        <Cutout name="coins_rising" cx={540} cy={2400} width={820} scale={coinsPop} />
        <LoopArrow cx={560} cy={2400} r={470} progress={loop} />
        <TextBlock g={g} guide={[70, 71]} keyw={[72, 73]} x={130} y={1800} keySize={128} />
      </Camera>
      <AbsoluteFill style={{ backgroundColor: C.night, opacity: darken }} />
    </AbsoluteFill>
  );
};
