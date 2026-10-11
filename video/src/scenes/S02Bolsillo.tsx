import React from "react";
import { AbsoluteFill } from "remotion";
import { Camera } from "../components/Camera";
import { Phone } from "../components/Phone";
import { CreditCard } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, kf, springy } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S02 = { start: 5.65, end: 10.4 };

/**
 * E2 (papel + banda negra): la tarjeta entra, se tacha "cuenta bancaria" y cae; el móvil sube "del bolsillo".
 * Al final la cámara se mete en la pantalla del móvil (transición a la escena oscura).
 */
export const S02Bolsillo: React.FC<{ start?: number }> = ({ start = S02.start }) => {
  const { t, g } = useSceneTime(start);

  // zoom lento + entrada final en la pantalla del móvil
  const zoomIn = kf(g, [9.98, 10.4], [0, 1], easeIn);
  const scale = kf(t, [0.3, 4.3], [1.0, 1.12], easeInOut) * (1 + zoomIn * 7);
  const cy = 980 + zoomIn * 20;
  const bandGrow = kf(t, [0.2, 1.2], [0.4, 1]);

  // tarjeta: entra con "cuenta" y cae tras tacharla
  const cardX = kf(g, [6.86, 7.3], [1500, 560]);
  const cardFall = kf(g, [8.15, 8.6], [0, 1], easeIn);
  const cardY = 990 + cardFall * 1500;
  const cardR = kf(g, [6.86, 7.3], [16, -8]) + cardFall * 34;

  // tachado de "cuenta bancaria"
  const strike = kf(g, [7.95, 8.15], [0, 1]);

  // el móvil sube desde abajo
  const ph = springy(g, 8.45, 0.55, 0.06);
  const phoneY = 2600 - ph * 1600;

  const dark = kf(g, [10.22, 10.4], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <Camera cx={540} cy={cy} scale={scale}>
        {/* banda negra horizontal (estilo.md §5.3) */}
        <div style={{ position: "absolute", left: -600, width: 2280, top: 990 - 150 * bandGrow, height: 300 * bandGrow, background: C.ink }} />
        <CreditCard cx={cardX} cy={cardY} w={620} rotate={cardR} />
        <Phone cx={540} cy={phoneY} w={440} rotate={(1 - ph) * 8} screen="#1d1d1e">
          <div style={{ position: "absolute", top: 120, width: "100%", textAlign: "center", fontFamily: "Archivo", fontWeight: 600, color: "#e8e8e8", fontSize: 92, letterSpacing: "-0.02em", opacity: 0.85 }}>
            23:47
          </div>
        </Phone>

        <TextBlock g={g} guide={[16, 19]} keyw={[20, 21]} x={130} y={250} keySize={98} />
        {strike > 0 && (
          <div style={{ position: "absolute", left: 118, top: 368, width: 860 * strike, height: 10, background: C.ink, rotate: "-2deg", transformOrigin: "0 50%", borderRadius: 5 }} />
        )}
        <TextBlock g={g} guide={[22, 24]} keyw={[25, 25]} x={950} y={1500} align="right" keySize={140} />
      </Camera>
      <AbsoluteFill style={{ backgroundColor: C.night, opacity: dark }} />
    </AbsoluteFill>
  );
};
