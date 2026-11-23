// Escenario de vídeo: una «ventana» cuyo rectángulo cambia según el formato (pantalla completa ↔ ventana
// horizontal) y una cámara virtual (zoom + ancla en la cara) dentro de ella.
import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, Freeze, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { keys, lerp, ramp } from "../anim";
import { C, FULL, WINDOW } from "../theme";
import { BEAT_PARTITURA, MODE, SEGMENTS, Segment, T, seg } from "../timeline";
import { ZOOMS } from "../edit/zooms";
import { BROLL } from "../edit/broll";

/** La voz va 1 dB por debajo de su nivel exportado (−15 LUFS) para dejar margen a música y SFX en la mezcla. */
export const VOICE_VOLUME = 0.9;

type Rect = { x: number; y: number; w: number; h: number; r: number };
const mix = (a: Rect, b: Rect, p: number): Rect => ({
  x: lerp(a.x, b.x, p),
  y: lerp(a.y, b.y, p),
  w: lerp(a.w, b.w, p),
  h: lerp(a.h, b.h, p),
  r: lerp(a.r, b.r, p),
});

/** 0 = pantalla completa, 1 = ventana horizontal. */
export const windowAmount = (t: number) => {
  if (t < MODE.toWindow) return 0;
  if (t < MODE.toFull) return 1;
  if (t < MODE.morphStart) return 0;
  return ramp(t, MODE.morphStart, MODE.morphEnd - MODE.morphStart, Easing.inOut(Easing.cubic));
};
export const stageRect = (t: number): Rect => mix(FULL, WINDOW, windowAmount(t));
export const isTestimonio = (t: number) => t >= MODE.toTestimonio && t < MODE.toFull;

const Shot: React.FC<{ s: Segment }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = s.start + frame / fps;
  const rect = stageRect(t);
  const win = windowAmount(t);
  // Zoom base: en ventana se cierra un 45 % sobre el «cover»; a pantalla completa el plano ya es cerrado.
  const base = lerp(1.0, 1.6, win);
  const zoom = base * keys(t, ZOOMS[s.id] ?? [[s.start, 1]]);
  const tx = lerp(0.5, 0.46, win);
  const ty = lerp(0.31, 0.42, win);
  const cover = Math.max(rect.w / s.srcW, rect.h / s.srcH);
  const vw = s.srcW * cover * zoom;
  const vh = s.srcH * cover * zoom;
  // A pantalla completa el plano es muy cerrado: el ancla sigue la cara (suavizada); en ventana basta la media.
  const lt = frame / fps;
  const tr = s.track;
  const fx = tr ? lerp(keys(lt, tr.map((k) => [k[0], k[1]] as [number, number]), (v) => v), s.face.x, win) : s.face.x;
  const fy = tr ? lerp(keys(lt, tr.map((k) => [k[0], k[2]] as [number, number]), (v) => v), s.face.y, win) : s.face.y;
  const left = Math.min(0, Math.max(rect.w - vw, tx * rect.w - fx * vw));
  const top = Math.min(0, Math.max(rect.h - vh, ty * rect.h - fy * vh));
  // Si el montaje pide más imagen de la que tiene el archivo (tarjeta final), se congela el último fotograma.
  // Ojo: <Freeze> silencia el audio, así que solo se usa en ese tramo final.
  const last = Math.floor(s.lastFrameAt * fps);
  const style: React.CSSProperties = {
    position: "absolute",
    left,
    top,
    width: vw,
    height: vh,
    maxWidth: "none",
    // Etalonaje de estilo.md: contraste +10–15 %, saturación +5 %, sujeto algo más luminoso.
    filter: "contrast(1.12) saturate(1.06) brightness(1.02)",
  };
  if (frame > last) {
    return (
      <Freeze frame={last}>
        <Video src={staticFile(s.file)} muted style={style} />
      </Freeze>
    );
  }
  return <Video src={staticFile(s.file)} volume={VOICE_VOLUME} style={style} />;
};

const Broll: React.FC<{ file: string; from: number; to: number }> = ({ file, from, to }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = from + frame / fps;
  const rect = stageRect(t);
  // Entra al 118 % y se asienta (regla de b-roll de la referencia: entra cerrado y se aleja).
  const z = keys(t, [
    [from, 1.18],
    [from + 0.6, 1.06],
    [to, 1.0],
  ]);
  return (
    <Video
      src={staticFile(file)}
      muted
      objectFit="cover"
      style={{
        position: "absolute",
        left: (rect.w - rect.w * z) / 2,
        top: (rect.h - rect.h * z) / 2,
        width: rect.w * z,
        height: rect.h * z,
        filter: "contrast(1.08) saturate(0.96) brightness(0.92)",
      }}
    />
  );
};

export const Stage: React.FC<{ blur: number }> = ({ blur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const rect = stageRect(t);
  const win = windowAmount(t);
  if (isTestimonio(t)) return null;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: rect.x,
          top: rect.y,
          width: rect.w,
          height: rect.h,
          borderRadius: rect.r,
          overflow: "hidden",
          backgroundColor: "#000",
          boxShadow: win > 0 ? `0 40px 120px rgba(0,0,0,${0.75 * win}), 0 0 0 1px rgba(255,255,255,${0.12 * win})` : undefined,
          filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
        }}
      >
        {SEGMENTS.filter((s) => s.id !== "s12_testimonio").map((s) => (
          <Sequence
            key={s.id}
            name={`Voz · ${s.id}`}
            from={Math.round(s.start * fps)}
            durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps))}
            layout="none"
          >
            <Shot s={s} />
          </Sequence>
        ))}
        {BROLL.map((b) => (
          <Sequence
            key={b.file + b.from}
            name={`B-roll · ${b.file}`}
            from={Math.round(b.from * fps)}
            durationInFrames={Math.round((b.to - b.from) * fps)}
            layout="none"
          >
            <Broll file={b.file} from={b.from} to={b.to} />
          </Sequence>
        ))}
        {/* Viñeta: oscurece bordes y el lado derecho (el iMac) para que no compita con la cara. */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `radial-gradient(120% 110% at 42% 40%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%), linear-gradient(90deg, rgba(0,0,0,0) 62%, rgba(0,0,0,${0.5 * win}) 100%)`,
          }}
        />
        {/* A pantalla completa: degradado inferior para que el texto sobre el pecho se lea. */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: 1 - win,
            background: "linear-gradient(180deg, rgba(0,0,0,0) 42%, rgba(0,0,0,0.62) 68%, rgba(0,0,0,0.9) 100%)",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export { C, T, seg, BEAT_PARTITURA };
