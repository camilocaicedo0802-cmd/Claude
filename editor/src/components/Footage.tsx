import { Audio, Video } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../brand";
import { at, DURATION, HOLD, SEGMENTS } from "../lib/timing";

// Vídeo de trabajo: recorte 1620×2880 del 4K original (crop=1620:2880:270:268), sin escalar.
// null = vista previa con silueta.
export const VIDEO_SRC: string | null = "crudo/video.mp4";
// Centro de la cara en el encuadre (origen de todos los zooms)
const CARA = "52% 43%";

// Palabras que reciben un "golpe" de zoom (+6 %) porque son el dato clave de su frase.
const ENFASIS = [
  at("21 días").start,
  at("3|tres semanas").start,
  at("15 minutos").start,
  at("una guía").end - 0.2,
  at("perfecto").start,
  at("constante").start,
  at("primer día").start,
];

const Placeholder: React.FC = () => (
  <AbsoluteFill style={{ background: "linear-gradient(180deg, #9AA59F 0%, #B9AE9E 55%, #C9B59B 100%)" }}>
    <svg width={1080} height={1920} style={{ position: "absolute", opacity: 0.35 }}>
      <ellipse cx={540} cy={700} rx={175} ry={215} fill={COLORS.petroleo} />
      <path d="M140 1920 C150 1250 330 1020 540 1020 C750 1020 930 1250 940 1920 Z" fill={COLORS.petroleo} />
    </svg>
    <div
      style={{
        position: "absolute",
        bottom: 60,
        width: "100%",
        textAlign: "center",
        fontFamily: FONTS.body,
        fontSize: 26,
        letterSpacing: "0.3em",
        color: COLORS.marfil,
        opacity: 0.7,
      }}
    >
      VISTA PREVIA · AQUÍ VA TU VÍDEO
    </div>
  </AbsoluteFill>
);

const Plano: React.FC<{ index: number; from: number; duration: number; trimBefore: number }> = ({
  index,
  from,
  duration,
  trimBefore,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const global = frame + from;

  // Reencuadre alterno en cada corte (estilo.md §2) + empuje lento para que ningún plano quede estático
  const base = index % 2 === 0 ? 1 : 1.22; // plano medio ↔ plano medio corto
  const empuje = interpolate(frame, [0, duration], [1, 1.025]);
  const golpe = ENFASIS.reduce((acc, t) => {
    const d = global - Math.round(t * fps);
    return acc + interpolate(d, [0, 4, 16], [0, 0.06, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    });
  }, 0);

  return (
    <AbsoluteFill style={{ transform: `scale(${base * empuje + golpe})`, transformOrigin: CARA }}>
      {VIDEO_SRC ? <Video src={staticFile(VIDEO_SRC)} trimBefore={trimBefore} muted objectFit="cover" style={{ width: "100%", height: "100%" }} /> : <Placeholder />}
    </AbsoluteFill>
  );
};

export const Footage: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      {SEGMENTS.map((s, i) => {
        const from = Math.round(s.outStart * fps);
        const next = i < SEGMENTS.length - 1 ? Math.round(SEGMENTS[i + 1].outStart * fps) : Math.ceil((DURATION + HOLD) * fps);
        const trimBefore = Math.round(s.srcStart * fps);
        return (
          <Sequence key={i} from={from} durationInFrames={next - from} name={`Plano ${i + 1}`}>
            <Plano index={i} from={from} duration={next - from} trimBefore={trimBefore} />
            <Audio src={staticFile("crudo/voz.m4a")} trimBefore={trimBefore} />
          </Sequence>
        );
      })}
    </>
  );
};
