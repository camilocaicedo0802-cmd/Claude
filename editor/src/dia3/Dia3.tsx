import { AbsoluteFill, Composition } from "remotion";
import { FONT_FACES, VIDEO } from "../brand";
import { Beats } from "./Beats";
import { Footage } from "./Footage";
import { Sonido } from "./Sonido";
import { DURATION, HOLD } from "./timing";

// Reto de 21 días · Vídeo 3 "Preparación y uso seguro". Días 1 y 2 no se tocan.
export const Dia3Video: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <style>{FONT_FACES}</style>
    <Footage />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(69,89,90,.55) 0%, rgba(69,89,90,.3) 24%, rgba(69,89,90,0) 38%)" }} />
    <Beats />
    <Sonido />
  </AbsoluteFill>
);

export const Dia3 = () => (
  <Composition id="Dia3" component={Dia3Video} durationInFrames={Math.ceil((DURATION + HOLD) * VIDEO.fps)} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
);
