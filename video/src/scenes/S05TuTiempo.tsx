import React from "react";
import { AbsoluteFill } from "remotion";
import { Camera } from "../components/Camera";
import { Cutout } from "../components/Cutout";
import { Halo } from "../components/Overlays";
import { TextBlock } from "../components/TextBlock";
import { kf, springy } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S05 = { start: 20.0, end: 21.2 };

/** "TU TIEMPO": golpe a negro, reloj de frente con zoom de impacto y corona de marcas que avanza. */
export const S05TuTiempo: React.FC<{ start?: number }> = ({ start = S05.start }) => {
  const { t, g } = useSceneTime(start);
  const hit = 20.09;
  const s = springy(g, hit, 0.5, 0.0);
  const scale = 1.22 - 0.22 * s + kf(g, [hit + 0.5, 21.2], [0, 0.04]);
  const show = g >= hit;
  const seconds = Math.floor(Math.max(0, g - hit) / 0.32); // avanza una marca en cada tic
  const R = 470;
  const ccx = 540;
  const ccy = 1210;

  return (
    <AbsoluteFill style={{ backgroundColor: C.night }}>
      {show && (
        <Camera cx={540} cy={960} scale={scale} rotate={(1 - s) * -3}>
          <Halo cx={ccx} cy={ccy} w={1000} h={1100} />
          <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
            {new Array(60).fill(0).map((_, i) => {
              const a = (i / 60) * Math.PI * 2 - Math.PI / 2;
              const major = i % 5 === 0;
              const L = major ? 34 : 16;
              const active = i <= (seconds + 1) * 5 && i > seconds * 5 - 1;
              return (
                <line
                  key={i}
                  x1={ccx + Math.cos(a) * R}
                  y1={ccy + Math.sin(a) * R}
                  x2={ccx + Math.cos(a) * (R + L)}
                  y2={ccy + Math.sin(a) * (R + L)}
                  stroke={C.snow}
                  strokeWidth={major ? 6 : 3}
                  opacity={(active ? 0.95 : 0.35) * Math.min(1, t * 5)}
                  strokeLinecap="round"
                />
              );
            })}
          </svg>
          <Cutout name="watch_dark" cx={ccx} cy={ccy - 86} width={700} shadow={false} />
        </Camera>
      )}
      {show && <TextBlock g={g} theme="darkInv" guide={[43, 43]} keyw={[44, 44]} x={120} y={130} guideSize={70} keySize={290} />}
    </AbsoluteFill>
  );
};
