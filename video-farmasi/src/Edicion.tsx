import "./fuentes";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import { ARoll, Vineta } from "./componentes/ARoll";
import { BRoll, MGCierre, MGGrafica, MGInvestigar, MGReloj, Montaje } from "./componentes/Escenas";
import { LightLeak } from "./componentes/LightLeak";
import { CapaDetras, CapaFrente } from "./componentes/Subtitulos";
import { GraficaSube, TarjetaAlmuerzo, WidgetGomitas } from "./componentes/UI";
import { ESCENAS, LIGHT_LEAK } from "./plan";
import { SFX, volumenMusica } from "./sonido";
import { f } from "./util";

export const Edicion: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* 1. Plano hablando: toma → palabra gigante detrás → persona recortada */}
      <ARoll capa="base" />
      <CapaDetras />
      <ARoll capa="persona" />
      <Vineta />

      {/* 2. Interfaz de cristal sobre el plano hablando */}
      <TarjetaAlmuerzo />
      <GraficaSube />
      <WidgetGomitas />

      {/* 3. Escenas a pantalla completa */}
      {ESCENAS.map((e) => (
        <Sequence key={e.desde} name={`${e.tipo} ${e.desde}s`} from={f(e.desde)} durationInFrames={f(e.hasta) - f(e.desde)}>
          {e.tipo === "broll" && <BRoll e={e} />}
          {e.tipo === "montaje" && <Montaje e={e} />}
          {e.tipo === "mg-investigar" && <MGInvestigar desde={e.desde} />}
          {e.tipo === "mg-reloj" && <MGReloj desde={e.desde} />}
          {e.tipo === "mg-grafica" && <MGGrafica desde={e.desde} />}
          {e.tipo === "mg-cierre" && <MGCierre />}
        </Sequence>
      ))}

      {/* 4. Subtítulos y textos */}
      <CapaFrente />

      {/* 5. Light leak en el giro del guion */}
      <Sequence name="Light leak" from={f(LIGHT_LEAK) - 18} durationInFrames={36}>
        <LightLeak />
      </Sequence>

      {/* 6. Sonido */}
      <Audio src={staticFile("audio/voz.wav")} />
      <Audio src={staticFile("audio/musica.wav")} volume={(fr) => volumenMusica(fr)} />
      {SFX.map((s, i) => (
        <Sequence key={i} from={s.at} durationInFrames={Math.round((s.dur ?? 3) * fps)} name={`sfx ${s.src}`}>
          <Audio src={staticFile(`sfx_sel/${s.src}.wav`)} volume={s.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
