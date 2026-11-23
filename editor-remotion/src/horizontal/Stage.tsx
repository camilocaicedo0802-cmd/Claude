// Escenario de la opción B: ventana horizontal con cámara virtual, b-roll horizontal y la capa del sujeto
// recortado, que puede sobresalir por ARRIBA de la ventana (pero no por los lados ni por abajo).
import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { keys } from "../anim";
import { GRADE, VOICE_VOLUME } from "../components/Stage";
import fgJson from "../data/fg.json";
import { BEAT_PARTITURA, CUTS, SEGMENTS, Segment, T, seg } from "../timeline";
import { WIN, hLayout, popOf, winY } from "./layout";

/** B-roll en horizontal (mismos momentos que la opción vertical, recortados a 16:10). */
export const BROLL_H: { file: string; from: number; to: number }[] = [
  { file: "media/broll/brh_casting.mp4", from: T("s02", 0) - 0.02, to: T("s02", 6) - 0.04 },
  { file: "media/broll/brh_partitura.mp4", from: BEAT_PARTITURA.start - 0.05, to: BEAT_PARTITURA.end + 0.5 },
  { file: "media/broll/brh_actriz.mp4", from: T("s11", 1) - 0.05, to: T("s11", 5) + 0.35 },
  { file: "media/broll/brh_ojo.mp4", from: T("s11", 10) - 0.1, to: CUTS.testimonio },
];

type Fg = { file: string; from_: number; to: number; x: number; y: number; w: number; h: number };
const FG = fgJson as unknown as Record<string, Fg>;

const Shot: React.FC<{ s: Segment }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { left, top, vw, vh } = hLayout(s, s.start + frame / fps);
  return <Video src={staticFile(s.file)} volume={VOICE_VOLUME} style={{ position: "absolute", left, top, width: vw, height: vh, maxWidth: "none", filter: GRADE }} />;
};

const Broll: React.FC<{ file: string; from: number; to: number }> = ({ file, from, to }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = from + frame / fps;
  // Entra al 116 % y se asienta (regla de b-roll de la referencia: entra cerrado y se aleja).
  const z = keys(t, [
    [from, 1.16],
    [from + 0.6, 1.05],
    [to, 1.0],
  ]);
  return <Video src={staticFile(file)} muted objectFit="cover" style={{ position: "absolute", left: (WIN.w - WIN.w * z) / 2, top: (WIN.h - WIN.h * z) / 2, width: WIN.w * z, height: WIN.h * z, filter: "contrast(1.08) saturate(0.96) brightness(0.94)" }} />;
};

/** La ventana: vídeo base + b-roll, con esquinas redondeadas, sombra y viñeta. */
export const WindowStage: React.FC<{ blur: number }> = ({ blur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t >= CUTS.testimonio && t < CUTS.cta) return null; // el testimonio va a pantalla completa
  return (
    <div
      style={{
        position: "absolute",
        left: WIN.x,
        top: winY(t),
        width: WIN.w,
        height: WIN.h,
        borderRadius: WIN.r,
        overflow: "hidden",
        backgroundColor: "#000",
        boxShadow: "0 40px 120px rgba(0,0,0,0.75), 0 0 0 1px rgba(255,255,255,0.13)",
        filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
      }}
    >
      {SEGMENTS.filter((s) => s.id !== "s12_testimonio").map((s) => (
        <Sequence key={s.id} name={`Voz · ${s.id}`} from={Math.round(s.start * fps)} durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps))} layout="none">
          <Shot s={s} />
        </Sequence>
      ))}
      {BROLL_H.map((b) => (
        <Sequence key={b.file} name={`B-roll · ${b.file}`} from={Math.round(b.from * fps)} durationInFrames={Math.round((b.to - b.from) * fps)} layout="none">
          <Broll file={b.file} from={b.from} to={b.to} />
        </Sequence>
      ))}
      {/* Viñeta: oscurece las esquinas y el lado derecho (el monitor) para que no compitan con la cara. */}
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(120% 110% at 44% 38%, rgba(0,0,0,0) 46%, rgba(0,0,0,0.5) 100%), linear-gradient(90deg, rgba(0,0,0,0) 66%, rgba(0,0,0,0.38) 100%)" }} />
    </div>
  );
};

const Cutout: React.FC<{ id: string; fg: Fg }> = ({ id, fg }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = seg(id);
  const t = s.start + fg.from_ + frame / fps;
  // Solo mientras la toma está en pantalla (el recorte dura un poco más que el plano) y la cabeza sobresale.
  if (t >= s.end || popOf(s, t) <= 0.001) return null;
  const { left, top, sc } = hLayout(s, t);
  return <Video src={staticFile(fg.file)} muted style={{ position: "absolute", left: left + fg.x * sc, top: winY(t) + top + fg.y * sc, width: fg.w * sc, height: fg.h * sc, maxWidth: "none", filter: GRADE }} />;
};

/** Sujeto recortado: se pinta encima de la ventana y de la palabra gigante. Solo puede salirse por arriba. */
export const CutoutLayer: React.FC<{ blur: number }> = ({ blur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <div style={{ position: "absolute", left: WIN.x, top: 0, width: WIN.w, height: winY(t) + WIN.h, overflow: "hidden", borderRadius: `0 0 ${WIN.r}px ${WIN.r}px`, filter: blur > 0.05 ? `blur(${blur}px)` : undefined }}>
      {Object.entries(FG).map(([id, fg]) => (
        <Sequence key={id} name={`Sujeto recortado · ${id}`} from={Math.round((seg(id).start + fg.from_) * fps)} durationInFrames={Math.max(1, Math.round((fg.to - fg.from_) * fps))} layout="none">
          <Cutout id={id} fg={fg} />
        </Sequence>
      ))}
    </div>
  );
};

/** Fondo del lienzo: negro con un resplandor ámbar muy tenue detrás de la ventana. */
export const Backdrop: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#060606", backgroundImage: "radial-gradient(72% 36% at 50% 40%, rgba(255,222,33,0.05) 0%, rgba(0,0,0,0) 100%), radial-gradient(80% 30% at 50% 72%, rgba(138,0,21,0.10) 0%, rgba(0,0,0,0) 100%)" }} />
);
