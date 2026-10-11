import React from "react";
import { AbsoluteFill } from "remotion";
import { BrushPath } from "../components/BrushPath";
import { Camera } from "../components/Camera";
import { Cutout } from "../components/Cutout";
import { DashedCircle } from "../components/DashedCircle";
import { LoopArrow } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, easeOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S09 = { start: 33.75, end: 38.8 };
export const BRAIN_CIRCLE = { x: 540, y: 1240, r: 350 };
const COINS = { cx: 540, cy: 2600, w: 820 };

/**
 * E9–E10 (papel, entra por máscara circular desde la pantalla del móvil): el cerebro "vuelve" del móvil;
 * la cámara sigue bajando; las pilas de monedas aparecen de mayor a menor con la voz; "puede volver" avanza
 * mientras las monedas retroceden; la línea final barre a negro y conduce al reloj de arena (E11).
 */
export const S09Volver: React.FC<{ start?: number }> = ({ start = S09.start }) => {
  const { t, g } = useSceneTime(start);
  const cy = 960 + (2310 - 960) * kf(g, [35.45, 36.2], [0, 1], easeInOut);
  const scale = 1 + 0.04 * kf(t, [0, 5], [0, 1], easeInOut);

  const brainPop = g > 34.94 ? 1 + 0.05 * Math.sin(Math.min(1, (g - 34.94) / 0.3) * Math.PI) : 1;
  const circleOp = 1 - kf(g, [35.45, 35.9], [0, 1]); // el círculo cede protagonismo al bajar

  // monedas: aparición progresiva de mayor a menor (izquierda -> derecha) sincronizada con la voz
  const reveal = kf(g, [36.04, 36.3], [0, 0.42], easeOut) + kf(g, [36.36, 36.6], [0, 0.3], easeOut) + kf(g, [36.9, 37.15], [0, 0.28], easeOut);
  const recede = kf(g, [36.9, 38.3], [1, 0.9], easeInOut);
  const advance = kf(g, [36.9, 38.3], [0.96, 1.05], easeInOut);
  const loop = kf(g, [37.5, 38.1], [0, 1], easeInOut);

  // barrido final: el trazo engorda hasta cubrir el cuadro de negro
  const wipeDraw = kf(g, [38.25, 38.45], [0, 1], easeOut);
  const wipeW = 30 + kf(g, [38.38, 38.75], [0, 2700], easeIn);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <Camera cx={540} cy={cy} scale={scale}>
        <BrushPath id="s09" d="M 830 1480 C 1010 1680, 1050 1880, 985 2140 S 1070 2480, 1000 2760" progress={kf(g, [35.4, 36.9], [0, 1], easeInOut)} />
        <DashedCircle id="s09c" cx={BRAIN_CIRCLE.x} cy={BRAIN_CIRCLE.y} d={BRAIN_CIRCLE.r * 2} t={t} appearAt={0.05} drawDur={0.5} opacity={circleOp} />
        <Cutout
          name="brain"
          cx={BRAIN_CIRCLE.x}
          cy={BRAIN_CIRCLE.y + Math.sin(t * 1.6) * 6}
          width={520}
          rotate={Math.sin(t * 0.9) * 2}
          scale={brainPop}
          style={{ filter: "drop-shadow(24px 30px 28px rgba(0,0,0,0.5))" }}
        />
        <TextBlock g={g} guide={[68, 68]} keyw={[69, 69]} x={150} y={560} keySize={160} />

        <div style={{ position: "absolute", inset: 0, scale: `${recede}`, transformOrigin: `${COINS.cx}px ${COINS.cy}px` }}>
          {reveal > 0 && (
            <Cutout
              name="coins_rising"
              cx={COINS.cx}
              cy={COINS.cy}
              width={COINS.w}
              style={{ WebkitMaskImage: reveal < 0.999 ? `linear-gradient(90deg, #000 ${reveal * 112 - 12}%, transparent ${reveal * 112}%)` : undefined, maskImage: reveal < 0.999 ? `linear-gradient(90deg, #000 ${reveal * 112 - 12}%, transparent ${reveal * 112}%)` : undefined, filter: "drop-shadow(20px 24px 22px rgba(0,0,0,0.45))" }}
            />
          )}
          <LoopArrow cx={560} cy={COINS.cy} r={470} progress={loop} />
        </div>
        <TextBlock g={g} guide={[70, 71]} keyw={[72, 73]} x={130} y={1880} keySize={170} scale={advance} />
      </Camera>
      {wipeDraw > 0 && <BrushPath id="s09w" d="M 1250 250 C 760 640, 420 1180, -160 1760" progress={wipeDraw} width={wipeW} color={C.night} plain />}
    </AbsoluteFill>
  );
};
