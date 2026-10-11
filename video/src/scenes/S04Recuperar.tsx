import React from "react";
import { AbsoluteFill } from "remotion";
import { Cutout } from "../components/Cutout";
import { DashedCircle } from "../components/DashedCircle";
import { DissolveCutout } from "../components/Dissolve";
import { Particles } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeInOut, easeOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S04 = { start: 15.8, end: 20.09 };
export const WATCH_CIRCLE = { x: 540, y: 1060, r: 380 };

/**
 * E4 (papel, entra por match cut circular desde el toque en la pantalla): el reloj gira brevemente al entrar;
 * el texto avanza hacia cámara mientras el reloj retrocede (profundidad = sensación de pérdida);
 * en "recuperar" el reloj se desintegra.
 */
export const S04Recuperar: React.FC<{ start?: number }> = ({ start = S04.start }) => {
  const { t, g } = useSceneTime(start);

  // movimientos opuestos: texto 0.94 -> 1.04 / objeto 1 -> 0.92
  const textScale = kf(g, [16.2, 19.9], [0.94, 1.04], easeInOut);
  const objScale = kf(g, [16.2, 19.9], [1, 0.92], easeInOut);
  const spin = kf(g, [15.85, 16.55], [-20, -4], easeOut);
  const give = kf(g, [16.66, 17.15], [0, 1], easeOut);
  const wx = WATCH_CIRCLE.x + give * 70;
  const wr = spin + give * 10;
  const dis = kf(g, [18.96, 19.85], [0, 1], easeInOut);
  const darken = kf(g, [19.95, 20.09], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <div style={{ position: "absolute", inset: 0, scale: `${objScale}`, transformOrigin: `${WATCH_CIRCLE.x}px ${WATCH_CIRCLE.y}px` }}>
        <DashedCircle id="s04c" cx={WATCH_CIRCLE.x} cy={WATCH_CIRCLE.y} d={WATCH_CIRCLE.r * 2} t={t} appearAt={0.02} drawDur={0.5} spread={dis * 60} opacity={1 - dis} />
        {dis <= 0 ? (
          <Cutout name="watch_light" cx={wx} cy={WATCH_CIRCLE.y} width={600} rotate={wr} style={{ filter: "contrast(1.15) drop-shadow(20px 24px 22px rgba(0,0,0,0.45))" }} />
        ) : (
          <DissolveCutout id="watch" name="watch_light" cx={wx} cy={WATCH_CIRCLE.y} width={600} rotate={wr} progress={dis} />
        )}
        <Particles seed="watch" n={70} t={g} start={18.96} cx={wx} cy={WATCH_CIRCLE.y} spreadX={520} spreadY={420} dx={380} dy={-560} dur={1.0} size={7} />
      </div>
      <TextBlock g={g} guide={[36, 36]} keyw={[37, 37]} x={140} y={420} keySize={150} scale={textScale} />
      <TextBlock g={g} guide={[38, 41]} keyw={[42, 42]} x={950} y={1460} align="right" keySize={136} scale={textScale} />
      <AbsoluteFill style={{ backgroundColor: C.night, opacity: darken }} />
    </AbsoluteFill>
  );
};
