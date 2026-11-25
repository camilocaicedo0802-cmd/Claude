import "./fuentes";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import { ARoll } from "./componentes/ARoll";
import { BRoll, Imagen } from "./componentes/Escenas";
import { ChipCarbohidratos, MGGlucosa, MGGrafica, TarjetaTiempo } from "./componentes/MG";
import { CapaDetras, CapaFrente } from "./componentes/Subtitulos";
import { GraficaGlucosa } from "./componentes/UI";
import { ESCENAS, UI } from "./plan";
import { SFX, volumenMusica } from "./sonido";
import { f } from "./util";

// v3 · UGC sencillo + bloque explicativo de glucosa con b-roll de salud y motion graphics
export const Edicion: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Plano hablando: toma → palabra gigante detrás → persona recortada */}
      <ARoll capa="base" />
      <CapaDetras />
      <ARoll capa="persona" />
      <GraficaGlucosa modo="sube" />

      {/* B-roll, imágenes de apoyo y motion graphics */}
      {ESCENAS.map((e) => (
        <Sequence key={e.desde} name={`${e.tipo} ${e.desde}s`} from={f(e.desde)} durationInFrames={f(e.hasta) - f(e.desde)}>
          {e.tipo === "broll" && <BRoll e={e} />}
          {e.tipo === "imagen" && <Imagen e={e} />}
          {e.tipo === "mg-glucosa" && <MGGlucosa desde={e.desde} />}
          {e.tipo === "mg-grafica" && <MGGrafica desde={e.desde} />}
        </Sequence>
      ))}
      <ChipCarbohidratos desde={UI.carbohidratos.desde} hasta={UI.carbohidratos.hasta} />
      <TarjetaTiempo desde={UI.tiempo.desde} hasta={UI.tiempo.hasta} />

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
