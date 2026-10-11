import React from "react";
import { AbsoluteFill } from "remotion";
import { Camera } from "../components/Camera";
import { Cutout } from "../components/Cutout";
import { DashedCircle } from "../components/DashedCircle";
import { DissolveCutout } from "../components/Dissolve";
import { Particles } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeInOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S04 = { start: 15.8, end: 20.09 };

/** E4 (papel, entra con iris): el reloj de bolsillo se "entrega" y se desintegra en "recuperar". */
export const S04Recuperar: React.FC<{ start?: number }> = ({ start = S04.start }) => {
  const { t, g } = useSceneTime(start);
  const scale = kf(t, [0, 4.3], [1.0, 1.08], easeInOut);
  const cy = kf(t, [0, 4.3], [960, 930], easeInOut);

  const give = kf(g, [16.66, 17.15], [0, 1]);
  const wx = 540 + give * 120;
  const wr = -4 + give * 14;
  const dis = kf(g, [18.96, 19.85], [0, 1], easeInOut);
  const darken = kf(g, [19.95, 20.09], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <Camera cx={540} cy={cy} scale={scale}>
        <DashedCircle cx={540} cy={1060} d={760} t={t} appearAt={0.1} spread={dis * 60} opacity={1 - dis} />
        {dis <= 0 ? (
          <Cutout name="watch_light" cx={wx} cy={1060} width={600} rotate={wr} />
        ) : (
          <DissolveCutout id="watch" name="watch_light" cx={wx} cy={1060} width={600} rotate={wr} progress={dis} />
        )}
        <Particles seed="watch" n={140} t={g} start={18.96} cx={wx} cy={1060} spreadX={560} spreadY={460} dx={420} dy={-640} dur={1.0} />
        <TextBlock g={g} guide={[36, 36]} keyw={[37, 37]} x={140} y={330} keySize={130} />
        <TextBlock g={g} guide={[38, 41]} keyw={[42, 42]} x={950} y={1450} align="right" keySize={126} />
      </Camera>
      <AbsoluteFill style={{ backgroundColor: C.night, opacity: darken }} />
    </AbsoluteFill>
  );
};
