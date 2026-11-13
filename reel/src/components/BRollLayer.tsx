import { Video } from "@remotion/media";
import React from "react";
import { Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BROLL, BRoll } from "../timeline";
import { H, W } from "../theme";

const Clip: React.FC<{ b: BRoll }> = ({ b }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dur = (b.t1 - b.t0) * fps;
  const [z0, z1] = b.zoom ?? [1, 1.08];
  // Entrada opcional con desenfoque + zoom que se asienta en 8 fotogramas (estilo.md §5).
  const k = b.blurIn ? Math.max(0, 1 - frame / 8) : 0;
  return (
    <div
      style={{
        position: "absolute",
        width: W,
        height: H,
        overflow: "hidden",
        transformOrigin: b.origin ?? "50% 45%",
        scale: String(interpolate(frame, [0, dur], [z0, z1], { extrapolateRight: "clamp" }) * (1 + 0.12 * k * k)),
        filter: k > 0 ? `blur(${24 * k * k}px)` : undefined,
      }}
    >
      {b.kind === "video" ? (
        <Video
          src={staticFile(b.src)}
          trimBefore={Math.round((b.trim ?? 0) * fps)}
          playbackRate={b.rate ?? 1}
          muted
          objectFit="cover"
          style={{ width: W, height: H }}
        />
      ) : (
        <Img
          src={staticFile(b.src)}
          style={{ width: W, height: H, objectFit: "cover", objectPosition: b.pos ?? "50% 50%" }}
        />
      )}
    </div>
  );
};

export const BRollLayer: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      {BROLL.map((b, i) => {
        const from = Math.round(b.t0 * fps);
        return (
          <Sequence
            key={i}
            name={`B-roll ${b.src.replace("media/", "")}`}
            from={from}
            durationInFrames={Math.round(b.t1 * fps) - from}
            layout="none"
          >
            <Clip b={b} />
          </Sequence>
        );
      })}
    </>
  );
};
