import "./fuentes";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import { ARoll } from "./componentes/ARoll";
import { BRoll } from "./componentes/Escenas";
import { CapaDetras, CapaFrente } from "./componentes/Subtitulos";
import { GraficaGlucosa } from "./componentes/UI";
import { ESCENAS } from "./plan";
import { SFX, volumenMusica } from "./sonido";
import { f } from "./util";

// v2 · estilo UGC sencillo
export const Edicion: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Plano hablando: toma → palabra gigante detrás → persona recortada */}
      <ARoll capa="base" />
      <CapaDetras />
      <ARoll capa="persona" />

      {/* Única superposición: tarjeta de glucosa */}
      <GraficaGlucosa modo="sube" />
      <GraficaGlucosa modo="baja" />

      {/* B-roll propio con corte seco */}
      {ESCENAS.map((e) => (
        <Sequence key={e.desde} name={`b-roll ${e.desde}s`} from={f(e.desde)} durationInFrames={f(e.hasta) - f(e.desde)}>
          <BRoll e={e} />
        </Sequence>
      ))}

      {/* Subtítulos palabra a palabra */}
      <CapaFrente />

      {/* Sonido */}
      <Audio src={staticFile("audio/voz.wav")} />
      <Audio src={staticFile("audio/musica.wav")} volume={(fr) => volumenMusica(fr)} />
      {SFX.map((s, i) => (
        <Sequence key={i} from={s.at} durationInFrames={Math.round((s.dur ?? 2) * fps)} name={`sfx ${s.src}`}>
          <Audio src={staticFile(`sfx_sel/${s.src}.wav`)} volume={s.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
