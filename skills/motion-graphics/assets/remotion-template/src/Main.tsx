import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { Grain, Vignette } from "./components/Overlays";
import { Push } from "./components/Transitions";
import { SFX } from "./data/sfx";
import { ExampleScene } from "./scenes/ExampleScene";
import { DURATION_S } from "./theme";

// Línea de tiempo principal. Una <Sequence> por escena (tiempos en segundos globales, ver storyboard en estilo.md).
// Las transiciones van como envoltorios dentro de cada secuencia; las escenas se solapan lo que dura la transición.
const SCENES = {
  e1: { start: 0, end: 3.0 },
};

export const Main: React.FC = () => {
  const { fps } = useVideoConfig();
  const len = (s: { start: number; end: number }) => Math.round((s.end - s.start) * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Sequence name="E1 · ejemplo" from={Math.round(SCENES.e1.start * fps)} durationInFrames={len(SCENES.e1)} premountFor={fps}>
        <Push mode="out" id="p1" seqDur={SCENES.e1.end - SCENES.e1.start}>
          <ExampleScene start={SCENES.e1.start} />
        </Push>
      </Sequence>

      {/* capas globales medidas en la referencia (quítalas si no aparecen) */}
      <Vignette strength={0.14} />
      <Grain opacity={0.16} />

      {/* sonido: voz, música (bucle de la referencia si se pidió) y SFX */}
      <Audio name="Voz" src={staticFile("audio/voz.mp3")} premountFor={fps} />
      <Audio
        name="Música"
        src={staticFile("audio/musica.wav")}
        premountFor={fps}
        volume={(f) => interpolate(f, [0, 0.6 * fps, (DURATION_S - 1.2) * fps, DURATION_S * fps], [0, 0.5, 0.5, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
      />
      {SFX.map((s, i) => (
        <Audio key={i} name={`SFX ${s.note || s.file}`} from={Math.round(s.t * fps)} src={staticFile(`sfx/${s.file}.wav`)} volume={s.vol} premountFor={fps} />
      ))}
    </AbsoluteFill>
  );
};
