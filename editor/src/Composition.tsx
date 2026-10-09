import { AbsoluteFill, Composition } from "remotion";
import { FONT_FACES, VIDEO } from "./brand";
import { Beats } from "./components/Beats";
import { Captions } from "./components/Captions";
import { Footage } from "./components/Footage";
import { DURATION, HOLD } from "./lib/timing";

export const Borrador: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <style>{FONT_FACES}</style>
    <Footage />
    {/* Velo superior en Verde petróleo: legibilidad de los títulos sobre la pared de mármol */}
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(69,89,90,.62) 0%, rgba(69,89,90,.35) 20%, rgba(69,89,90,0) 34%)" }} />
    <Beats />
    <Captions />
  </AbsoluteFill>
);

export const MyComposition = () => (
  <Composition
    id="Borrador"
    component={Borrador}
    durationInFrames={Math.ceil((DURATION + HOLD) * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
