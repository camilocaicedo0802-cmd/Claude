import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { BrushPath } from "../components/BrushPath";
import { Camera } from "../components/Camera";
import { Cutout, IMG } from "../components/Cutout";
import { Halo } from "../components/Overlays";
import { Phone, VideoThumb } from "../components/Phone";
import { Particles, WarningSign } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, kf, kfs, springy } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S06 = { start: 20.92, end: 34.05 };

// Busto de Marco Aurelio en coordenadas del mundo
const BUST = { cx: 520, cy: 3150, w: 900 };
const BUST_H = (BUST.w * IMG.bust_marcus[1]) / IMG.bust_marcus[0];
const BUST_TOP = BUST.cy - BUST_H / 2;
const K = BUST.w / IMG.bust_marcus[0];
const EYES = { x: BUST.cx - BUST.w / 2 + 520 * K, y: BUST_TOP + 170 * K };
const HEAD_TOP = BUST_TOP;

const PHONE = { cx: 820, cy: 1500, w: 300 };

/**
 * E6–E8 (equivalente a E2→E3 de la referencia):
 *  A) papel: señal de peligro ("peligroso")
 *  B) papel + banda: busto con zoom; barra de censura en los ojos ("te das cuenta")
 *  C) oscurecimiento y transformación: silueta + móvil que ilumina la cara ("consumes contenido")
 *  D) cerebro sobre la cabeza absorbido por el móvil ("el contenido consume tu atención")
 */
export const S06Atencion: React.FC<{ start?: number }> = ({ start = S06.start }) => {
  const { t, g } = useSceneTime(start);

  // ----- cámara
  const cy = kfs(g, [20.92, 22.85, 23.55, 26.6, 26.75, 27.6, 30.6, 34.05], [960, 990, 2950, 2900, 2900, 2980, 2980, 2960]);
  const scale = kfs(g, [20.92, 23.55, 26.6, 26.75, 27.6, 30.6, 34.05], [1.0, 1.0, 1.12, 1.12, 1.25, 1.25, 1.32]);
  const cx = 540 + Math.sin(t * 0.7) * 8;
  const toScreen = (x: number, y: number) => ({ x: 540 + (x - cx) * scale, y: 960 + (y - cy) * scale });
  const toWorld = (x: number, y: number) => ({ x: cx + (x - 540) / scale, y: cy + (y - 960) / scale });

  // ----- fase A: señal
  const signIn = springy(g, 21.2, 0.6, 0.06);
  const wob = g > 22.04 ? Math.sin((g - 22.04) * 28) * 7 * Math.exp(-(g - 22.04) * 5) : 0;
  const signPop = g > 22.04 ? 1 + 0.06 * Math.sin(Math.min(1, (g - 22.04) / 0.3) * Math.PI) : 1;

  // ----- fase B: busto
  const bustIn = kf(g, [23.2, 23.85], [0, 1]);
  const bandGrow = kf(g, [23.3, 24.2], [0.3, 1]) + kf(g, [26.7, 27.3], [0, 4], easeIn);
  const censor = kf(g, [25.4, 25.6], [0, 1]);

  // ----- fase C: oscurecer
  const dark = kf(g, [26.7, 27.25], [0, 1], easeInOut);
  const bright = 1 - dark * 0.93;
  const phoneIn = springy(g, 27.5, 0.5, 0.05);
  const flash = kf(g, [32.74, 33.2], [1, 0]) * (g >= 32.74 ? 1 : 0);
  const glow = phoneIn * (1 + flash * 1.5);
  const faceLit = phoneIn * (1 - kf(g, [32.74, 33.4], [0, 0.6]));

  // ----- fase D: cerebro
  const brainIn = kf(g, [30.67, 31.1], [0, 1]);
  const suck = kf(g, [31.6, 32.45], [0, 1], easeIn);
  const brainHome = { x: EYES.x - 10, y: HEAD_TOP - 18 };
  const phoneW = toWorld(PHONE.cx, PHONE.cy - 120);
  const bx = brainHome.x + (phoneW.x - brainHome.x) * suck + Math.sin(suck * Math.PI) * 160;
  const by = brainHome.y + (phoneW.y - brainHome.y) * suck;

  const face = toScreen(EYES.x, EYES.y + 40);
  const feedScroll = Math.max(0, g - 27.5) * 0.9;

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      <AbsoluteFill style={{ backgroundColor: C.night, opacity: dark }} />
      <Camera cx={cx} cy={cy} scale={scale}>
        {/* A */}
        <BrushPath id="s06" d="M 760 1380 C 1060 1580, 1050 1900, 1010 2120 S 990 2480, 1060 2720" progress={kf(g, [22.4, 23.6], [0, 1], easeInOut)} opacity={1 - dark} />
        {signIn > 0 && <WarningSign cx={560 + (1 - signIn) * 380} cy={1150 + (1 - signIn) * 900} w={520} rotate={(1 - signIn) * 25 + wob} scale={signPop} post={500} />}
        <TextBlock g={g} guide={[45, 47]} keyw={[48, 48]} x={140} y={330} keySize={132} />

        {/* B */}
        <div style={{ position: "absolute", left: -900, width: 2880, top: 2830 - 130 * bandGrow, height: 260 * bandGrow, background: dark > 0 ? C.night : C.ink }} />
        <Halo cx={BUST.cx} cy={BUST.cy - 120} w={1100} h={1200} opacity={dark} />
        {bustIn > 0 && (
          <>
            <Cutout
              name="bust_marcus"
              cx={BUST.cx - (1 - bustIn) * 700}
              cy={BUST.cy + (1 - bustIn) * 400}
              width={BUST.w}
              rotate={(1 - bustIn) * -10}
              brightness={bright}
              shadowOpacity={0.45 * (1 - dark)}
            />
            {/* cara iluminada por la pantalla */}
            {faceLit > 0 && (
              <Img
                src={staticFile("img/bust_marcus.png")}
                style={{
                  position: "absolute",
                  left: BUST.cx - BUST.w / 2,
                  top: BUST_TOP,
                  width: BUST.w,
                  height: BUST_H,
                  filter: "brightness(0.62)",
                  opacity: faceLit * 0.9,
                  WebkitMaskImage: "radial-gradient(ellipse 26% 22% at 56% 28%, #000 0%, rgba(0,0,0,0.5) 45%, transparent 100%)",
                  maskImage: "radial-gradient(ellipse 26% 22% at 56% 28%, #000 0%, rgba(0,0,0,0.5) 45%, transparent 100%)",
                }}
              />
            )}
          </>
        )}
        {censor > 0 && (
          <div
            style={{
              position: "absolute",
              left: EYES.x - 175,
              top: EYES.y - 38,
              width: 350,
              height: 76,
              background: "#0c0c0c",
              rotate: "-3deg",
              transformOrigin: "0 50%",
              scale: `${censor} 1`,
              boxShadow: "8px 10px 16px rgba(0,0,0,0.35)",
            }}
          />
        )}
        <TextBlock g={g} guide={[49, 54]} keyw={[55, 57]} x={100} y={2170} width={860} keySize={102} exitAt={26.62} />

        {/* D: cerebro sobre la cabeza, absorbido por el móvil */}
        {brainIn > 0 && suck < 1 && (
          <Cutout
            name="brain"
            cx={bx}
            cy={by}
            width={340}
            scale={(0.75 + 0.25 * brainIn) * (1 - suck * 0.94)}
            rotate={suck * 240}
            opacity={brainIn * (1 - kf(suck, [0.8, 1], [0, 1]))}
            shadow={false}
            style={{ filter: `blur(${(1 - brainIn) * 10 + suck * 6}px) drop-shadow(0 0 28px rgba(255,255,255,0.18))` }}
          />
        )}
        <Particles seed="brain" n={70} t={g} start={31.6} cx={brainHome.x} cy={brainHome.y} spreadX={300} spreadY={260} dx={phoneW.x - brainHome.x} dy={phoneW.y - brainHome.y} dur={0.8} color="#cfcfcf" size={7} />
      </Camera>

      {/* C/D en pantalla: móvil y contenidos que vuelan hacia la cara */}
      {phoneIn > 0 && (
        <Phone cx={PHONE.cx} cy={PHONE.cy + (1 - phoneIn) * 800} w={PHONE.w} rotate={-10} screen="#0f0f10" glow={glow}>
          {new Array(4).fill(0).map((_, i) => (
            <VideoThumb key={i} x={0} y={(i - (feedScroll % 1)) * 592} w={277} h={592} tone={((i * 31) % 10) / 10} radius={0} showPlay={false} progress={0.3 + i * 0.15} />
          ))}
          <div style={{ position: "absolute", inset: 0, background: "#fff", opacity: flash }} />
        </Phone>
      )}
      {new Array(6).fill(0).map((_, i) => {
        const s0 = 28.68 + i * 0.17;
        const p = kf(g, [s0, s0 + 0.6], [0, 1], easeIn);
        if (g < s0 || p >= 1) return null;
        const x = PHONE.cx + (face.x - PHONE.cx) * p + Math.sin(p * Math.PI) * (i % 2 ? 160 : -120);
        const y = PHONE.cy - 150 + (face.y - (PHONE.cy - 150)) * p;
        return <VideoThumb key={i} x={x - 60} y={y - 85} w={120} h={170} tone={((i * 41) % 10) / 10} scale={1 - p * 0.7} opacity={1 - p * 0.6} radius={14} />;
      })}

      <TextBlock g={g} theme="dark" guide={[58, 60]} keyw={[61, 62]} x={90} y={1060} width={600} guideSize={50} keySize={118} exitAt={30.45} />
      <TextBlock g={g} theme="dark" guide={[63, 65]} keyw={[66, 67]} x={90} y={1060} width={620} guideSize={50} keySize={124} />
    </AbsoluteFill>
  );
};
