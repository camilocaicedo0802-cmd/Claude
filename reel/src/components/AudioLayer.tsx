import { Audio } from "@remotion/media";
import React from "react";
import { Sequence, interpolate, staticFile, useVideoConfig } from "remotion";
import { SFX, TOTAL, VOICE_END } from "../timeline";

/** Voz editada + música (ANBR - Quantum desde 24,4 s) ~11 dB por debajo de la voz + SFX. */
export const AudioLayer: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      <Audio name="Voz" src={staticFile("audio/voz.wav")} volume={1} />
      <Audio
        name="Música"
        src={staticFile("audio/musica.wav")}
        volume={(f) =>
          interpolate(
            f / fps,
            [0, 0.4, VOICE_END - 0.2, VOICE_END + 0.3, TOTAL - 0.9, TOTAL],
            [0.2, 0.3, 0.3, 0.6, 0.55, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          )
        }
      />
      {SFX.map((s, i) => (
        <Sequence
          key={i}
          name={`SFX ${s.src.replace("sfx/", "").replace(".wav", "")}`}
          from={Math.round(s.t * fps)}
          durationInFrames={s.dur ? Math.max(2, Math.round(s.dur * fps)) : undefined}
          layout="none"
        >
          <Audio
            src={staticFile(s.src)}
            volume={
              s.dur
                ? (f) => s.vol * interpolate(f / fps, [0, (s.dur ?? 1) - 0.06, s.dur ?? 1], [1, 1, 0], { extrapolateRight: "clamp" })
                : s.vol
            }
          />
        </Sequence>
      ))}
    </>
  );
};
