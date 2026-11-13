import { Video } from "@remotion/media";
import React from "react";
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame } from "remotion";
import { clamp, easeOut, keyframes } from "../anim";

const linear = (t: number) => t;

const W = 1080;
const H = 1920;

/**
 * Reencuadre de una toma 9:16 en 4K: `zoom` 1 = cuadro completo; 2 = recorte
 * de la mitad (sin perder resolución con fuente 2160×3840). `focus` es el punto
 * de la fuente (0–1) que queremos en `target` (0–1) de la pantalla, normalmente
 * la cara. El recorte se limita para que nunca aparezcan bordes negros.
 */
const frameRect = (zoom: number, focus: readonly [number, number], target: readonly [number, number]) => {
  const w = W * zoom;
  const h = H * zoom;
  const left = Math.min(0, Math.max(W - w, target[0] * W - focus[0] * w));
  const top = Math.min(0, Math.max(H - h, target[1] * H - focus[1] * h));
  return { width: w, height: h, left, top };
};

type TalkingShotProps = {
  readonly name: string;
  readonly src: string;
  readonly from: number;
  readonly durationInFrames: number;
  readonly trimBefore: number;
  readonly focus: readonly [number, number];
  /** Seguimiento opcional de la cara: [fotograma, x, y] relativos al plano. */
  readonly focusTrack?: ReadonlyArray<readonly [number, number, number]>;
  readonly target: readonly [number, number];
  /** Zoom por fotogramas clave relativos al inicio del plano. */
  readonly zoom: ReadonlyArray<readonly [number, number]>;
};

const TalkingFrame: React.FC<Omit<TalkingShotProps, "name" | "from" | "durationInFrames">> = ({
  src,
  trimBefore,
  focus,
  focusTrack,
  target,
  zoom,
}) => {
  const frame = useCurrentFrame();
  const f: readonly [number, number] = focusTrack
    ? [
        keyframes(frame, focusTrack.map(([t, x]) => [t, x] as const), linear),
        keyframes(frame, focusTrack.map(([t, , y]) => [t, y] as const), linear),
      ]
    : focus;
  const r = frameRect(keyframes(frame, zoom), f, target);
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "black" }}>
      <Video
        src={src}
        trimBefore={trimBefore}
        objectFit="cover"
        style={{ position: "absolute", ...r }}
      />
    </AbsoluteFill>
  );
};

/** Plano a cámara: lleva la voz. */
export const TalkingShot: React.FC<TalkingShotProps> = ({ name, from, durationInFrames, ...rest }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames} premountFor={30}>
    <TalkingFrame {...rest} />
  </Sequence>
);

type BRollProps = {
  readonly name: string;
  readonly src: string;
  readonly from: number;
  readonly durationInFrames: number;
  readonly trimBefore: number;
  /** Escala inicial→final (Ken Burns sutil 1.00→1.06 por defecto). */
  readonly scale?: readonly [number, number];
  /** Zoom extra por fotogramas clave (p. ej. asentamiento de arranque). */
  readonly zoom?: ReadonlyArray<readonly [number, number]>;
  /** Fundido de entrada con blur (fotogramas). 0 = corte seco. */
  readonly fadeIn?: number;
  readonly origin?: string;
  /** Desenfoque fijo (para fondos de cierre). */
  readonly blurPx?: number;
};

const BRollFrame: React.FC<Omit<BRollProps, "name" | "from">> = ({
  src,
  trimBefore,
  durationInFrames,
  scale = [1, 1.06],
  zoom,
  fadeIn = 4,
  origin = "50% 45%",
  blurPx = 0,
}) => {
  const frame = useCurrentFrame();
  const kb = interpolate(frame, [0, durationInFrames], [scale[0], scale[1]], clamp);
  const extra = zoom ? keyframes(frame, zoom, easeOut) : 1;
  return (
    <AbsoluteFill
      style={{
        overflow: "hidden",
        opacity: fadeIn > 0 ? interpolate(frame, [0, fadeIn], [0, 1], clamp) : 1,
        filter: fadeIn > 0 ? `blur(${interpolate(frame, [0, fadeIn], [6, 0], clamp)}px)` : undefined,
      }}
    >
      <AbsoluteFill
        style={{
          scale: String(kb * extra),
          transformOrigin: origin,
          filter: blurPx > 0 ? `blur(${blurPx}px)` : undefined,
        }}
      >
        <Video src={src} trimBefore={trimBefore} muted objectFit="cover" style={{ width: W, height: H }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Plano de recurso (b-roll) sin sonido, por encima del plano a cámara. */
export const BRoll: React.FC<BRollProps> = ({ name, from, durationInFrames, ...rest }) => (
  <Sequence name={name} from={from} durationInFrames={durationInFrames} premountFor={30}>
    <BRollFrame durationInFrames={durationInFrames} {...rest} />
  </Sequence>
);
