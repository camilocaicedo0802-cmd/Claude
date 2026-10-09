import { AbsoluteFill, Composition } from "remotion";
import { FONT_FACES, VIDEO } from "../brand";
import { Beats } from "./Beats";
import { Footage } from "./Footage";
import { Sonido } from "./Sonido";
import { DURATION, HOLD } from "./timing";

// Reto de 21 días · Vídeo 2 "Punto de partida". El día 1 (composición "Borrador") no se toca.
export const Dia2Video: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <style>{FONT_FACES}</style>
    <Footage />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(69,89,90,.55) 0%, rgba(69,89,90,.3) 24%, rgba(69,89,90,0) 38%)" }} />
    <Beats />
    <Sonido />
  </AbsoluteFill>
);

export const Dia2 = () => (
  <Composition id="Dia2" component={Dia2Video} durationInFrames={Math.ceil((DURATION + HOLD) * VIDEO.fps)} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
);
