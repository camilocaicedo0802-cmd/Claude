import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { Grain, Vignette } from "./components/Overlays";
import { Iris, Push } from "./components/Transitions";
import { SFX } from "./data/sfx";
import { S01, S01Tiempo } from "./scenes/S01Tiempo";
import { S02, S02Bolsillo } from "./scenes/S02Bolsillo";
import { S03, S03Pantalla } from "./scenes/S03Pantalla";
import { S04, S04Recuperar } from "./scenes/S04Recuperar";
import { S05, S05TuTiempo } from "./scenes/S05TuTiempo";
import { S06, S06Atencion } from "./scenes/S06Atencion";
import { S09, S09Volver } from "./scenes/S09Volver";
import { S11, S11Jamas } from "./scenes/S11Jamas";
import { S12, S12Cierre } from "./scenes/S12Cierre";
import { DURATION_S } from "./theme";

const len = (s: { start: number; end: number }, fps: number) => Math.round((s.end - s.start) * fps);

export const Main: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Sequence name="E1 · reloj → monedas" from={Math.round(S01.start * fps)} durationInFrames={len(S01, fps)} premountFor={fps}>
        <Push mode="out" id="p1" seqDur={S01.end - S01.start}>
          <S01Tiempo />
        </Push>
      </Sequence>
      <Sequence name="E2 · tarjeta → bolsillo" from={Math.round(S02.start * fps)} durationInFrames={len(S02, fps)} premountFor={fps}>
        <Push mode="in" id="p2">
          <S02Bolsillo />
        </Push>
      </Sequence>
      <Sequence name="E3 · pantalla" from={Math.round(S03.start * fps)} durationInFrames={len(S03, fps)} premountFor={fps}>
        <S03Pantalla />
      </Sequence>
      <Sequence name="E4 · recuperar" from={Math.round(S04.start * fps)} durationInFrames={len(S04, fps)} premountFor={fps}>
        <Iris x={540} y={1180}>
          <S04Recuperar />
        </Iris>
      </Sequence>
      <Sequence name="E5 · tu tiempo" from={Math.round(S05.start * fps)} durationInFrames={len(S05, fps)} premountFor={fps}>
        <Push mode="out" id="p5" dur={0.28} seqDur={S05.end - S05.start}>
          <S05TuTiempo />
        </Push>
      </Sequence>
      <Sequence name="E6–E8 · atención" from={Math.round(S06.start * fps)} durationInFrames={len(S06, fps)} premountFor={fps}>
        <Push mode="in" id="p6" dur={0.28}>
          <S06Atencion />
        </Push>
      </Sequence>
      <Sequence name="E9–E10 · volver" from={Math.round(S09.start * fps)} durationInFrames={len(S09, fps)} premountFor={fps}>
        <Iris x={540} y={960}>
          <S09Volver />
        </Iris>
      </Sequence>
      <Sequence name="E11 · jamás" from={Math.round(S11.start * fps)} durationInFrames={len(S11, fps)} premountFor={fps}>
        <S11Jamas />
      </Sequence>
      <Sequence name="Cierre" from={Math.round(S12.start * fps)} durationInFrames={len(S12, fps)} premountFor={fps}>
        <Iris x={540} y={1500} dur={0.15} soft={20}>
          <S12Cierre />
        </Iris>
      </Sequence>

      <Vignette strength={0.14} />
      <Grain opacity={0.17} />

      {/* sonido */}
      <Audio name="Voz" src={staticFile("audio/voz.mp3")} premountFor={fps} />
      <Audio
        name="Música (referencia, en bucle)"
        src={staticFile("audio/musica_ref_loop.wav")}
        premountFor={fps}
        volume={(f) => interpolate(f, [0, 0.6 * fps, 41.2 * fps, DURATION_S * fps], [0, 0.42, 0.42, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
      />
      {SFX.map((s, i) => (
        <Audio key={i} name={`SFX ${s.note || s.file}`} from={Math.round(s.t * fps)} src={staticFile(`sfx/${s.file}.wav`)} volume={s.vol} premountFor={fps} />
      ))}
    </AbsoluteFill>
  );
};
