import { Video } from "@remotion/media";
import React from "react";
import { Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BLUR_INS, PUNCH_INS } from "../timeline";
import { H, W } from "../theme";
import { EDL, Segment, clamp01 } from "../util";

const TRANS = 8 / 30; // duración del blur-in (8 fotogramas)

/** Encuadre de un segmento: escala base y posición objetivo de la cara (estilo.md §6). */
const baseFraming = (seg: Segment, idx: number, t: number) => {
  const standing = seg.faceY < 0.4;
  // Gancho con la silla: plano abierto para que se vea el producto.
  if (seg.outIn < 4.5) return { s: 1.0, tx: 0.5, ty: 0.36, fx: seg.faceX, fy: seg.faceY };
  // Silla sola (él sale de cuadro): push-in lento hacia la silla.
  if (seg.outIn >= 4.5 && seg.outIn < 5.7) {
    const p = clamp01((t - seg.outIn) / 1.2);
    return { s: 1.0 + 0.12 * p, tx: 0.42, ty: 0.74, fx: 0.4, fy: 0.76 };
  }
  const base = standing ? 1.1 : 1.16;
  // Alterna un 5 % de escala entre segmentos para disimular los jump cuts.
  const alt = idx % 2 === 1 ? 1.05 : 1.0;
  return { s: base * alt, tx: 0.5, ty: standing ? 0.24 : 0.34, fx: seg.faceX, fy: seg.faceY };
};

const Shot: React.FC<{ seg: Segment; idx: number; fromFrame: number }> = ({ seg, idx, fromFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (fromFrame + frame) / fps;

  let { s, tx, ty } = baseFraming(seg, idx, t);
  const { fx, fy } = baseFraming(seg, idx, t);

  const pi = PUNCH_INS.find((p) => t >= p.t0 && t < p.t1);
  if (pi) {
    s = pi.s;
    tx = 0.5;
    ty = seg.faceY < 0.4 ? 0.26 : 0.32;
  }

  // Blur-in con zoom que se asienta (vuelta del b-roll).
  let blur = 0;
  let bright = 1;
  let shiftX = 0;
  const b = BLUR_INS.find((x) => t >= x && t < x + TRANS);
  if (b !== undefined) {
    const k = 1 - (t - b) / TRANS;
    blur = 26 * k * k;
    s *= 1 + 0.12 * k * k;
  }
  // Arranque con whip (desenfoque de movimiento horizontal).
  if (t < 0.2) {
    const k = 1 - t / 0.2;
    blur = Math.max(blur, 18 * k);
    shiftX = -140 * k * k;
  }
  // Flash de exposición al reaparecer en la silla.
  if (t >= 5.73 && t < 5.73 + 0.1) bright = 1 + 0.9 * (1 - (t - 5.73) / 0.1);

  const ox = Math.min(0, Math.max(W - s * W, tx * W - s * fx * W)) + shiftX;
  const oy = Math.min(0, Math.max(H - s * H, ty * H - s * fy * H));

  return (
    <div
      style={{
        position: "absolute",
        width: W,
        height: H,
        transformOrigin: "0 0",
        translate: `${ox}px ${oy}px`,
        scale: String(s),
        filter: blur > 0.2 || bright !== 1 ? `blur(${blur}px) brightness(${bright})` : undefined,
      }}
    >
      <Video
        src={staticFile("media/base.mp4")}
        trimBefore={Math.round(seg.srcIn * fps)}
        muted
        objectFit="cover"
        style={{ width: W, height: H }}
      />
    </div>
  );
};

export const TalkingHead: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      {EDL.segments.map((seg, idx) => {
        const from = Math.round(seg.outIn * fps);
        const to = Math.round((seg.outIn + seg.srcOut - seg.srcIn) * fps);
        return (
          <Sequence key={idx} name={`Plano ${idx + 1}`} from={from} durationInFrames={to - from} layout="none">
            <Shot seg={seg} idx={idx} fromFrame={from} />
          </Sequence>
        );
      })}
    </>
  );
};
