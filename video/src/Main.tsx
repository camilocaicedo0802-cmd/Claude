import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { Grain, Vignette } from "./components/Overlays";
import { FadeIn, IrisMatch, Push } from "./components/Transitions";
import { SFX } from "./data/sfx";
import { S01, S01Tiempo } from "./scenes/S01Tiempo";
import { S02, S02Bolsillo } from "./scenes/S02Bolsillo";
import { S03, S03Pantalla } from "./scenes/S03Pantalla";
import { S04, S04Recuperar, WATCH_CIRCLE } from "./scenes/S04Recuperar";
import { S05, S05TuTiempo } from "./scenes/S05TuTiempo";
import { S06, S06Atencion } from "./scenes/S06Atencion";
import { BRAIN_CIRCLE, S09, S09Volver } from "./scenes/S09Volver";
import { S11, S11Jamas } from "./scenes/S11Jamas";
import { S12, S12Cierre } from "./scenes/S12Cierre";

const len = (s: { start: number; end: number }, fps: number) => Math.round((s.end - s.start) * fps);

/**
 * v2: continuidad entre escenas (cada elemento prepara el siguiente):
 * E1→E2 las monedas arrastran la franja · E2 la franja se convierte en el móvil · E2→E3 el móvil se queda y el
 * entorno pasa a negro · E3→E4 match cut del toque al círculo del reloj · E6 la línea dibuja la señal, la censura
 * se expande a negro, el cerebro baja por el eje del móvil · E6→E9 máscara circular desde la pantalla ·
 * E9→E11 la línea barre a negro y trae el reloj de arena · E11→cierre fundido suave.
 */
export const Main: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Sequence name="E1 · reloj → monedas" from={Math.round(S01.start * fps)} durationInFrames={len(S01, fps)} premountFor={fps}>
        <S01Tiempo />
      </Sequence>
      <Sequence name="E2 · tarjeta → móvil" from={Math.round(S02.start * fps)} durationInFrames={len(S02, fps)} premountFor={fps}>
        <S02Bolsillo />
      </Sequence>
      <Sequence name="E3 · pantalla" from={Math.round(S03.start * fps)} durationInFrames={len(S03, fps)} premountFor={fps}>
        <S03Pantalla />
      </Sequence>
      <Sequence name="E4 · recuperar" from={Math.round(S04.start * fps)} durationInFrames={len(S04, fps)} premountFor={fps}>
        <IrisMatch from={{ x: 540, y: 1028, r: 51 }} mid={WATCH_CIRCLE} grow={0.25} hold={0.15} open={0.3}>
          <S04Recuperar />
        </IrisMatch>
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
        <IrisMatch from={{ x: 540, y: 1250, r: 60 }} mid={BRAIN_CIRCLE} grow={0.25} hold={0.15} open={0.3}>
          <S09Volver />
        </IrisMatch>
      </Sequence>
      <Sequence name="E11 · jamás" from={Math.round(S11.start * fps)} durationInFrames={len(S11, fps)} premountFor={fps}>
        <S11Jamas />
      </Sequence>
      <Sequence name="Cierre" from={Math.round(S12.start * fps)} durationInFrames={len(S12, fps)} premountFor={fps}>
        <FadeIn dur={0.5}>
          <S12Cierre />
        </FadeIn>
      </Sequence>

      <Vignette strength={0.14} />
      <Grain opacity={0.2} />

      {/* sonido: la voz manda; la música baja en las frases finales, deja un silencio antes de "jamás" y cierra con su cola */}
      <Audio name="Voz" src={staticFile("audio/voz.mp3")} premountFor={fps} />
      <Audio
        name="Música (referencia, en bucle, con cola)"
        src={staticFile("audio/musica_ref_final.wav")}
        premountFor={fps}
        volume={(f) =>
          interpolate(f / fps, [0, 0.6, 38.4, 38.9, 40.0, 40.2, 40.6, 41.1, 43.2], [0, 0.6, 0.6, 0.38, 0.38, 0.1, 0.1, 0.5, 0.5], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })
        }
      />
      {SFX.map((s, i) => (
        <Audio key={i} name={`SFX ${s.note || s.file}`} from={Math.round(s.t * fps)} src={staticFile(`sfx/${s.file}.wav`)} volume={s.vol} premountFor={fps} />
      ))}
    </AbsoluteFill>
  );
};
