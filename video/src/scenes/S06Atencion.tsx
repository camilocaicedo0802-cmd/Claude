import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { BrushPath } from "../components/BrushPath";
import { Camera } from "../components/Camera";
import { Cutout, IMG } from "../components/Cutout";
import { Halo } from "../components/Overlays";
import { Phone, VideoThumb } from "../components/Phone";
import { Particles, WarningSign } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, easeOut, kf, kfs } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S06 = { start: 20.92, end: 34.05 };

// Señal de peligro (el trazo dibuja su contorno antes de que aparezca)
const SIGN = { cx: 540, cy: 1180, w: 520 };
const SIGN_H = SIGN.w * 0.88;
const SL = SIGN.cx - SIGN.w / 2;
const ST = SIGN.cy - SIGN_H / 2;
const k = SIGN.w / 100;
const TRI = { top: [SL + 50 * k, ST + 3 * k], br: [SL + 97 * k, ST + 84 * k], bl: [SL + 3 * k, ST + 84 * k] };
const SIGN_PATH = `M 1150 -120 C 980 220, 1060 560, 760 760 S 560 900, ${TRI.top[0]} ${TRI.top[1]} L ${TRI.br[0]} ${TRI.br[1]} L ${TRI.bl[0]} ${TRI.bl[1]} L ${TRI.top[0]} ${TRI.top[1]}`;

// Busto (coordenadas del mundo = pantalla a escala 1)
const BUST = { cx: 540, cy: 1250, w: 820 };
const BUST_H = (BUST.w * IMG.bust_marcus[1]) / IMG.bust_marcus[0];
const BUST_TOP = BUST.cy - BUST_H / 2;
const KB = BUST.w / IMG.bust_marcus[0];
const EYES = { x: BUST.cx - BUST.w / 2 + 520 * KB, y: BUST_TOP + 170 * KB };
const BAND2 = { y: 1430, h: 220 }; // franja detrás del pecho: la cara queda libre

const PHONE_X = 540;

/**
 * E6–E8 (equivalente a E2→E3 de la referencia), con continuidad entre todos los elementos:
 *  A) el trazo dibuja el contorno de la señal y de él surge la señal ("peligroso")
 *  B) pausa breve; la franja barre y la escultura entra siguiendo su dirección; acercamiento de cámara
 *  C) la franja de censura cruza los ojos y se expande hasta ser el fondo negro (luz de contorno en la escultura)
 *  D) el cerebro baja por el mismo eje por el que baja el móvil, y el móvil lo absorbe ("tu atención")
 */
export const S06Atencion: React.FC<{ start?: number }> = ({ start = S06.start }) => {
  const { t, g } = useSceneTime(start);

  // ----- cámara
  const scale = kfs(g, [20.92, 23.75, 26.6, 26.75, 27.6, 30.6, 34.05], [1, 1, 1.1, 1.1, 1.18, 1.18, 1.22]);
  const cy = kfs(g, [20.92, 26.75, 27.6, 34.05], [960, 960, 1195, 1195]);
  const cx = 540;
  const toScreen = (x: number, y: number) => ({ x: 540 + (x - cx) * scale, y: 960 + (y - cy) * scale });

  // ----- A: trazo -> señal
  const draw = kf(g, [21.15, 22.0], [0, 1], easeInOut);
  const pdt = g - 22.04;
  const signS = pdt < 0 ? 0 : pdt < 0.12 ? kf(pdt, [0, 0.12], [0.6, 1.05]) : kf(pdt, [0.12, 0.24], [1.05, 1]);
  const wob = pdt > 0 ? Math.sin(pdt * 26) * 4 * Math.exp(-pdt * 6) : 0;
  const aOut = kf(g, [22.62, 22.98], [0, 1], easeIn); // salida tranquila de la fase A

  // ----- B: franja y escultura
  const bandP = kf(g, [22.9, 23.3], [0, 1], easeOut);
  const bustIn = kf(g, [23.05, 23.75], [0, 1], easeOut);
  const censor = kf(g, [25.4, 25.62], [0, 1], easeOut);

  // ----- C: la franja de censura se expande hasta ser el fondo
  const ex = kf(g, [26.7, 27.25], [0, 1], easeInOut);
  const dark = ex;
  const bright = 1 - dark * 0.8;
  const exL = EYES.x - 190 + (-1600 - (EYES.x - 190)) * ex;
  const exR = EYES.x + 190 + (2700 - (EYES.x + 190)) * ex;
  const exT = EYES.y - 40 + (-1600 - (EYES.y - 40)) * ex;
  const exB = EYES.y + 40 + (3600 - (EYES.y + 40)) * ex;

  const phoneIn = kf(g, [27.5, 27.95], [0, 1], easeOut);
  const phoneY = 2300 + (1180 - 2300) * phoneIn + 70 * kf(g, [30.6, 31.0], [0, 1], easeInOut);
  const flash = g >= 32.74 ? kf(g, [32.74, 33.2], [1, 0]) : 0;
  const faceLit = phoneIn * (1 - kf(g, [32.74, 33.4], [0, 0.6]));

  // ----- D: cerebro por el eje vertical compartido con el móvil
  const brainIn = kf(g, [30.6, 31.1], [0, 1], easeOut);
  const suck = kf(g, [31.6, 32.45], [0, 1], easeIn);
  const brainHomeY = 405;
  const target = { x: PHONE_X, y: phoneY - 40 };
  const bY = -260 + (brainHomeY + 260) * brainIn + Math.sin(t * 1.5) * 5 * (1 - suck);
  const brainX = PHONE_X + (target.x - PHONE_X) * suck;
  const brainY = bY + (target.y - bY) * suck;

  const face = toScreen(EYES.x, EYES.y + 30);
  const feedScroll = Math.max(0, g - 27.5) * 0.9;

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <Camera cx={cx} cy={cy} scale={scale}>
        {/* A: trazo -> contorno -> señal, y salida tranquila */}
        {aOut < 1 && (
          <div style={{ position: "absolute", inset: 0, opacity: 1 - aOut, translate: `0px ${-140 * aOut}px` }}>
            <BrushPath id="s06" d={SIGN_PATH} progress={draw} opacity={1 - kf(g, [22.04, 22.3], [0, 1])} />
            {signS > 0 && <WarningSign cx={SIGN.cx} cy={SIGN.cy} w={SIGN.w} rotate={wob} scale={signS} post={480} />}
            <TextBlock g={g} guide={[45, 47]} keyw={[48, 48]} x={140} y={560} keySize={136} />
          </div>
        )}

        {/* B: franja que barre y escultura que entra en su dirección */}
        {bandP > 0 && <div style={{ position: "absolute", left: -1300 + 1300 * bandP, width: 1400, top: BAND2.y - BAND2.h / 2, height: BAND2.h, background: C.ink }} />}
        {/* C: negro que se expande desde la franja de censura (detrás de la escultura) */}
        {ex > 0 && <div style={{ position: "absolute", left: exL, top: exT, width: exR - exL, height: exB - exT, background: C.night }} />}
        <Halo cx={BUST.cx} cy={BUST.cy - 120} w={1100} h={1200} opacity={dark * 0.8} />
        {bustIn > 0 && (
          <>
            <Cutout
              name="bust_marcus"
              cx={BUST.cx - (1 - bustIn) * 940}
              cy={BUST.cy}
              width={BUST.w}
              scale={0.9 + 0.1 * bustIn}
              style={{
                // volumen: sombra marcada en claro; luz de contorno blanca suave en oscuro
                filter:
                  dark > 0
                    ? `brightness(${bright}) drop-shadow(-5px -4px 8px rgba(255,255,255,${0.42 * dark})) drop-shadow(5px 4px 10px rgba(255,255,255,${0.12 * dark}))`
                    : "drop-shadow(26px 32px 30px rgba(0,0,0,0.5))",
              }}
            />
            {faceLit > 0 && (
              <Img
                src={staticFile("img/bust_marcus.png")}
                style={{
                  position: "absolute",
                  left: BUST.cx - BUST.w / 2,
                  top: BUST_TOP,
                  width: BUST.w,
                  height: BUST_H,
                  filter: "brightness(0.66)",
                  opacity: faceLit * 0.9,
                  WebkitMaskImage: "radial-gradient(ellipse 26% 22% at 56% 30%, #000 0%, rgba(0,0,0,0.5) 45%, transparent 100%)",
                  maskImage: "radial-gradient(ellipse 26% 22% at 56% 30%, #000 0%, rgba(0,0,0,0.5) 45%, transparent 100%)",
                }}
              />
            )}
          </>
        )}
        {censor > 0 && (
          <div
            style={{
              position: "absolute",
              left: EYES.x - 190 - (1 - censor) * 900,
              top: EYES.y - 40,
              width: 380,
              height: 80,
              background: "#0c0c0c",
              rotate: "-3deg",
              boxShadow: "8px 10px 16px rgba(0,0,0,0.35)",
              opacity: 1 - kf(g, [27.2, 27.6], [0, 0.85]),
            }}
          />
        )}
        <TextBlock g={g} guide={[49, 54]} keyw={[55, 57]} x={110} y={230} keySize={120} exitAt={26.62} />
      </Camera>

      {/* C/D en pantalla: móvil centrado (eje vertical compartido con el cerebro) */}
      {phoneIn > 0 && (
        <Phone cx={PHONE_X} cy={phoneY} w={300} rotate={-5} screen="#0f0f10" glow={phoneIn * (1 + flash * 1.5)} rim={1}>
          {new Array(4).fill(0).map((_, i) => (
            <VideoThumb key={i} x={0} y={(i - (feedScroll % 1)) * 592} w={277} h={592} tone={0.5 + ((i * 31) % 10) / 20} radius={0} showPlay={false} progress={0.3 + i * 0.15} />
          ))}
          <div style={{ position: "absolute", inset: 0, background: "#fff", opacity: flash }} />
        </Phone>
      )}
      {new Array(6).fill(0).map((_, i) => {
        const s0 = 28.68 + i * 0.17;
        const p = kf(g, [s0, s0 + 0.6], [0, 1], easeIn);
        if (g < s0 || p >= 1) return null;
        const x = PHONE_X + (face.x - PHONE_X) * p + Math.sin(p * Math.PI) * (i % 2 ? 150 : -150);
        const y = phoneY - 150 + (face.y - (phoneY - 150)) * p;
        return <VideoThumb key={i} x={x - 60} y={y - 85} w={120} h={170} tone={0.5 + ((i * 41) % 10) / 20} scale={1 - p * 0.7} opacity={1 - p * 0.6} radius={14} />;
      })}
      {brainIn > 0 && suck < 1 && (
        <Cutout
          name="brain"
          cx={brainX}
          cy={brainY}
          width={400}
          scale={1 - suck * 0.94}
          rotate={suck * 90}
          opacity={brainIn * (1 - kf(suck, [0.85, 1], [0, 1]))}
          style={{ filter: `blur(${suck * 5}px) drop-shadow(14px 18px 18px rgba(0,0,0,0.75)) drop-shadow(0 0 22px rgba(255,255,255,0.16))` }}
        />
      )}
      <Particles seed="brain" n={36} t={g} start={31.6} cx={PHONE_X} cy={brainHomeY} spreadX={260} spreadY={220} dx={0} dy={target.y - brainHomeY} dur={0.8} color="#cfcfcf" size={6} />

      <TextBlock g={g} theme="dark" guide={[58, 61]} keyw={[62, 62]} x={540} y={1575} width={960} align="center" keySize={140} exitAt={30.45} />
      <TextBlock g={g} theme="dark" guide={[63, 65]} keyw={[66, 67]} x={540} y={1575} width={960} align="center" keySize={140} />
    </AbsoluteFill>
  );
};
