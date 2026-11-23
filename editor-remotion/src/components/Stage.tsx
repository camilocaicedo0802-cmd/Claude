// Escenario a pantalla completa: recorte vertical del plano horizontal con cámara virtual
// (zoom + ancla que sigue la cara), b-roll vertical y testimonio.
import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { keys } from "../anim";
import { C, H, W } from "../theme";
import { CUTS, SEGMENTS, Segment } from "../timeline";
import { ZOOMS } from "../edit/zooms";
import { BROLL } from "../edit/broll";

/** La voz va 1 dB por debajo de su nivel exportado (−15 LUFS) para dejar margen a música y SFX en la mezcla. */
export const VOICE_VOLUME = 0.9;
// Etalonaje de estilo.md §7: contraste +10–15 %, saturación +5 %, sujeto algo más luminoso.
export const GRADE = "contrast(1.12) saturate(1.06) brightness(1.02)";

export type Layout = { left: number; top: number; vw: number; vh: number; sc: number; z: number };

/** Dónde cae el plano de una toma en el lienzo en el instante `t` (lo comparten la base y el recorte del sujeto). */
export const shotLayout = (s: Segment, t: number): Layout => {
  const z = keys(t, ZOOMS[s.id] ?? [[s.start, 1]]);
  const lt = t - s.start;
  const tr = s.track;
  const fx = tr ? keys(lt, tr.map((k) => [k[0], k[1]] as [number, number]), (v) => v) : s.face.x;
  const fy = tr ? keys(lt, tr.map((k) => [k[0], k[2]] as [number, number]), (v) => v) : s.face.y;
  const sc = (H / s.srcH) * z;
  const vw = s.srcW * sc;
  const vh = s.srcH * sc;
  const left = Math.min(0, Math.max(W - vw, 0.5 * W - fx * vw));
  // Plano cerrado: la cara se mantiene al 31 % de la altura. Plano abierto: se ve toda la altura, con aire arriba.
  // (el plano abierto baja ~250 px: deja aire arriba para la palabra gigante y reparte el negro).
  const top = vh >= H ? Math.min(0, Math.max(H - vh, 0.31 * H - fy * vh)) : Math.max(0, 0.9 - z) * 1050;
  return { left, top, vw, vh, sc, z };
};

const Shot: React.FC<{ s: Segment }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = s.start + frame / fps;
  const { left, top, vw, vh } = shotLayout(s, t);
  const bottom = top + vh;
  return (
    <>
      <Video src={staticFile(s.file)} volume={VOICE_VOLUME} style={{ position: "absolute", left, top, width: vw, height: vh, maxWidth: "none", filter: GRADE }} />
      {/* Plano abierto: el borde inferior e superior del plano se funden con el fondo. */}
      {bottom < H + 1 ? <div style={{ position: "absolute", left: 0, top: bottom - 0.34 * vh, width: W, height: 0.34 * vh + (H - bottom) + 2, background: `linear-gradient(180deg, rgba(6,6,6,0) 0%, ${C.bg} ${Math.round(((0.34 * vh) / (0.34 * vh + (H - bottom) + 2)) * 100)}%, ${C.bg} 100%)` }} /> : null}
      {top > 1 ? <div style={{ position: "absolute", left: 0, top: 0, width: W, height: top + 170, background: `linear-gradient(180deg, ${C.bg} 0%, ${C.bg} ${Math.round((top / (top + 170)) * 100)}%, rgba(6,6,6,0) 100%)` }} /> : null}
    </>
  );
};

const Broll: React.FC<{ file: string; from: number; to: number }> = ({ file, from, to }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = from + frame / fps;
  // Entra al 114 % y se asienta (regla de b-roll de la referencia: entra cerrado y se aleja).
  const z = keys(t, [
    [from, 1.14],
    [from + 0.6, 1.04],
    [to, 1.0],
  ]);
  return <Video src={staticFile(file)} muted objectFit="cover" style={{ position: "absolute", left: (W - W * z) / 2, top: (H - H * z) / 2, width: W * z, height: H * z, filter: "contrast(1.08) saturate(0.96) brightness(0.9)" }} />;
};

export const Stage: React.FC<{ blur: number }> = ({ blur }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, overflow: "hidden", filter: blur > 0.05 ? `blur(${blur}px)` : undefined }}>
      {SEGMENTS.filter((s) => s.id !== "s12_testimonio").map((s) => (
        <Sequence key={s.id} name={`Voz · ${s.id}`} from={Math.round(s.start * fps)} durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps))} layout="none">
          <Shot s={s} />
        </Sequence>
      ))}
      {BROLL.map((b) => (
        <Sequence key={b.file + b.from} name={`B-roll · ${b.file}`} from={Math.round(b.from * fps)} durationInFrames={Math.round((b.to - b.from) * fps)} layout="none">
          <Broll file={b.file} from={b.from} to={b.to} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

/** Degradado inferior para que subtítulos y gráficos se lean sobre el pecho (en la referencia el tercio inferior es casi negro). */
export const Scrim: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const testi = t >= CUTS.testimonio && t < CUTS.cta;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        background: testi
          ? "linear-gradient(180deg, rgba(0,0,0,0.78) 0%, rgba(0,0,0,0.5) 26%, rgba(0,0,0,0) 46%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.6) 100%)"
          : "linear-gradient(180deg, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0) 14%, rgba(0,0,0,0) 44%, rgba(0,0,0,0.6) 66%, rgba(0,0,0,0.9) 100%)",
      }}
    />
  );
};
