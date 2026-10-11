import React from "react";
import { AbsoluteFill } from "remotion";
import { BrushPath } from "../components/BrushPath";
import { Camera } from "../components/Camera";
import { Cutout } from "../components/Cutout";
import { DashedCircle } from "../components/DashedCircle";
import { TextBlock } from "../components/TextBlock";
import { easeInOut, kf, kfs } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S01 = { start: 0, end: 5.95 };

/**
 * E1 (papel): reloj de arena en círculo discontinuo -> la cámara baja siguiendo el trazo -> monedas.
 * "y si te dijera que TODOS LOS DÍAS / estás perdiendo algo MÁS VALIOSO / que el DINERO"
 */
export const S01Tiempo: React.FC<{ start?: number }> = ({ start = S01.start }) => {
  const { t, g } = useSceneTime(start);

  // cámara: baja del reloj a las monedas (estilo.md §6, tilt-down continuo ease-in-out)
  const cy = kfs(t, [0, 1.9, 3.3, 4.55], [960, 1010, 1600, 2110]);
  const cx = 540 + Math.sin(t * 0.8) * 10;
  const scale = kf(t, [0, 5.95], [1.0, 1.06], easeInOut);

  // entrada del reloj desde la izquierda girando (-40° -> -6°) en 0.75 s
  const hx = kf(t, [0, 0.75], [-260, 560]);
  const hr = kf(t, [0, 0.75], [-40, -6]);
  const bob = Math.sin(t * 1.7) * 6;

  // "dinero": las monedas rebotan
  const pop = g > 5.0 ? 1 + 0.07 * Math.sin(Math.min(1, (g - 5.0) / 0.35) * Math.PI) : 1;
  const coinsIn = kf(t, [2.6, 3.4], [80, 0]);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <Camera cx={cx} cy={cy} scale={scale}>
        <BrushPath
          id="s01"
          d="M 1130 -140 C 960 200, 1100 520, 960 800 S 1000 1270, 700 1395 S 80 1480, 75 1800 S 110 2480, 520 2690 S 980 2760, 1060 3000"
          progress={kf(t, [0.25, 5.4], [0, 1], easeInOut)}
        />
        <DashedCircle cx={560} cy={1030} d={700} t={t} appearAt={0.25} />
        <Cutout name="hourglass_light" cx={hx} cy={1030 + bob} height={570} rotate={hr} />
        <Cutout name="coins_stacks" cx={540} cy={2350 + coinsIn} width={600} scale={pop} />

        <TextBlock g={g} guide={[0, 4]} keyw={[5, 7]} x={150} y={400} keySize={104} />
        <TextBlock g={g} guide={[8, 10]} keyw={[11, 12]} x={950} y={1480} align="right" keySize={122} />
        <TextBlock g={g} guide={[13, 14]} keyw={[15, 15]} x={140} y={1880} keySize={140} />
      </Camera>
    </AbsoluteFill>
  );
};
