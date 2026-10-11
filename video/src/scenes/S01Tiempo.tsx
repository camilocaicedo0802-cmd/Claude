import React from "react";
import { AbsoluteFill } from "remotion";
import { BrushPath } from "../components/BrushPath";
import { Camera } from "../components/Camera";
import { Cutout } from "../components/Cutout";
import { DashedCircle } from "../components/DashedCircle";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, easeOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { BAND, C } from "../theme";

export const S01 = { start: 0, end: 5.95 };

/**
 * E1 (papel): reloj de arena presente desde el primer frame, círculo que se dibuja, trazo que conduce del reloj
 * a las monedas con una cámara que lo sigue en una sola curva suave. Salida: las monedas se desplazan a la
 * derecha y arrastran la franja negra sobre la que entra la tarjeta (E2) — sin corte visible.
 */
export const S01Tiempo: React.FC<{ start?: number }> = ({ start = S01.start }) => {
  const { t, g } = useSceneTime(start);

  // cámara: un único movimiento ease-in-out del reloj a las monedas, con leve deriva lateral que sigue la curva
  const prog = kf(t, [1.5, 4.8], [0, 1], easeInOut);
  const cy = 960 + 1160 * prog;
  const cx = 540 - Math.sin(prog * Math.PI) * 38;
  const scale = 1 + 0.05 * kf(t, [0, 5.95], [0, 1], easeInOut);

  // reloj: visible desde el frame 0, entrada corta y desaceleración suave
  const hx = kf(t, [0, 0.45], [420, 560], easeOut);
  const hr = kf(t, [0, 0.5], [-22, -6], easeOut);
  const hs = kf(t, [0, 0.45], [0.92, 1], easeOut);
  const bob = Math.sin(t * 1.7) * 5;

  // monedas: rebote contenido en "dinero" y salida hacia la derecha arrastrando la franja
  const pop = g > 5.0 ? 1 + 0.05 * Math.sin(Math.min(1, (g - 5.0) / 0.32) * Math.PI) : 1;
  const slide = kf(g, [5.4, 5.9], [0, 1], easeIn);
  const coinsX = 540 + slide * 1250;
  // posición en pantalla del centro de las monedas
  const coinsScreenX = 540 + (coinsX - cx) * scale;
  const band0 = 540 + (540 - cx) * scale;
  const bandL = band0 + (-60 - band0) * kf(g, [5.4, 5.85], [0, 1], easeOut);
  const bandR = Math.max(bandL, coinsScreenX);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      {/* franja negra que aparece detrás de las monedas (pantalla, coincide con la de E2) */}
      {slide > 0 && <div style={{ position: "absolute", left: bandL, width: bandR - bandL, top: BAND.y - BAND.h / 2, height: BAND.h, background: C.ink }} />}
      <Camera cx={cx} cy={cy} scale={scale}>
        <BrushPath
          id="s01"
          d="M 955 700 C 1100 900, 1085 1250, 840 1370 S 160 1380, 95 1560 S 70 2000, 110 2180 S 200 2330, 250 2345"
          progress={kf(t, [0.35, 5.0], [0, 1], easeInOut)}
          opacity={1 - slide}
        />
        <DashedCircle id="s01c" cx={560} cy={1030} d={760} t={t} appearAt={0.08} drawDur={0.85} />
        <Cutout name="hourglass_light" cx={hx} cy={1030 + bob} height={640} rotate={hr} scale={hs} opacity={kf(t, [0, 0.1], [0, 1])} />
        <Cutout name="coins_stacks" cx={coinsX} cy={2380} width={620} scale={pop} style={{ filter: `drop-shadow(20px 24px 22px rgba(0,0,0,0.45))${slide > 0.05 ? ` blur(${slide * 6}px)` : ""}` }} />

        <TextBlock g={g} guide={[0, 4]} keyw={[5, 7]} x={130} y={360} keySize={126} />
        <TextBlock g={g} guide={[8, 10]} keyw={[11, 12]} x={950} y={1500} align="right" keySize={128} exitAt={5.4} />
        <TextBlock g={g} guide={[13, 14]} keyw={[15, 15]} x={130} y={1880} keySize={140} exitAt={5.5} />
      </Camera>
    </AbsoluteFill>
  );
};
