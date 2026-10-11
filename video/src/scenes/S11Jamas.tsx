import React from "react";
import { AbsoluteFill, random } from "remotion";
import { Camera } from "../components/Camera";
import { Cutout, IMG } from "../components/Cutout";
import { TextBlock } from "../components/TextBlock";
import { easeOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C, F } from "../theme";

export const S11 = { start: 38.75, end: 41.8 };

const HG = { cx: 540, cy: 1190, h: 1100 };
const KH = HG.h / IMG.hourglass_dark[1];
const HG_W = IMG.hourglass_dark[0] * KH;
const NECK = { x: HG.cx - HG_W / 2 + 350 * KH, y: HG.cy - HG.h / 2 + 448 * KH };
const PILE_Y = HG.cy - HG.h / 2 + 600 * KH;

/**
 * Cierre emocional (oscuro): el reloj de arena llega por la trayectoria de la línea que barrió a negro,
 * con luz y reflejos reforzados. En "pero tu tiempo" todo se aquieta (pausa dramática); en "jamás"
 * el reloj se apaga y la palabra entra a gran escala. Sin objetos nuevos.
 */
export const S11Jamas: React.FC<{ start?: number }> = ({ start = S11.start }) => {
  const { g } = useSceneTime(start);
  const enter = kf(g, [38.78, 39.4], [0, 1], easeOut);
  const hx = 860 + (HG.cx - 860) * enter;
  const hy = 700 + (HG.cy - 700) * enter;
  const hr = 14 * (1 - enter);
  const dim = kf(g, [40.2, 40.6], [1, 0.32]);
  const jdt = g - 40.27;
  const jP = kf(jdt, [0, 0.45], [0, 1], easeOut);

  return (
    <AbsoluteFill style={{ backgroundColor: C.night }}>
      <Camera cx={540} cy={960} scale={1}>
        {/* luz suave detrás para que el cristal se lea sobre negro */}
        <div style={{ position: "absolute", left: hx - 520, top: hy - 640, width: 1040, height: 1280, borderRadius: "50%", background: "radial-gradient(ellipse at 50% 45%, rgba(255,255,255,0.13) 0%, rgba(255,255,255,0.04) 45%, rgba(0,0,0,0) 70%)", opacity: enter * dim }} />
        <Cutout
          name="hourglass_dark"
          cx={hx}
          cy={hy}
          height={HG.h}
          rotate={hr}
          opacity={enter}
          style={{ filter: `brightness(${1.12 * dim}) contrast(1.18) drop-shadow(-4px -4px 10px rgba(255,255,255,${0.18 * dim}))` }}
        />
        {/* reflejos del cristal */}
        {enter > 0.6 && (
          <>
            <div style={{ position: "absolute", left: NECK.x - 120, top: NECK.y - 330, width: 14, height: 200, borderRadius: 10, background: "rgba(255,255,255,0.35)", filter: "blur(4px)", rotate: "8deg", opacity: dim }} />
            <div style={{ position: "absolute", left: NECK.x - 110, top: NECK.y + 90, width: 12, height: 160, borderRadius: 10, background: "rgba(255,255,255,0.28)", filter: "blur(4px)", rotate: "-8deg", opacity: dim }} />
          </>
        )}
        {/* hilo de arena (poca cantidad) */}
        {enter > 0.9 &&
          new Array(30).fill(0).map((_, i) => {
            const ph = ((g - 38.75) * 1.3 + i / 30) % 1;
            const x = NECK.x + (random(`sx-${i}`) - 0.5) * 5;
            const y = NECK.y + ph * (PILE_Y - NECK.y);
            return <div key={i} style={{ position: "absolute", left: x - 1.5, top: y, width: 3, height: 5, borderRadius: 2, background: "#ececec", opacity: 0.9 * Math.max(dim, 0.6) }} />;
          })}
      </Camera>

      <TextBlock g={g} theme="darkInv" guide={[74, 75]} keyw={[76, 76]} x={120} y={140} guideSize={68} keySize={220} />
      {jdt >= 0 && (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 1060,
            textAlign: "center",
            fontFamily: F.script,
            fontSize: 330,
            lineHeight: 1.2,
            color: C.snow,
            opacity: kf(jdt, [0, 0.18], [0, 1]),
            scale: `${1.45 - 0.45 * jP}`,
            filter: jP < 1 ? `blur(${(1 - jP) * 18}px)` : undefined,
            textShadow: "0 0 50px rgba(0,0,0,0.85), -2px 0 rgba(0,190,255,0.3), 2px 0 rgba(255,120,40,0.3)",
          }}
        >
          jamás
        </div>
      )}
    </AbsoluteFill>
  );
};
