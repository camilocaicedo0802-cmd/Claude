import { AbsoluteFill } from "remotion";
import "./fonts";
import { HighlightsLayer } from "./components/Highlight";
import { CardsLayer, LightLeaks, MontageLayer, NeonCoins, Subtitles, TransitionWrap } from "./components/Overlays";
import { SegmentsLayer } from "./components/SegmentVideo";
import { SoundTrack } from "./components/SoundTrack";

/**
 * Orden de capas (de atrás hacia delante), como en la referencia:
 * 1. Tomas habladas (fondo) y montaje de b-roll
 * 2. Lo que va DETRÁS de la persona: tarjetas de b-roll y palabras grandes "behind"
 * 3. Persona recortada (BiRefNet) encima, solo donde hay algo detrás
 * 4. Lo que va DELANTE: palabras grandes, kickers tecleados, neón, subtítulos
 * 5. Destello de luz de la entrada al montaje
 */
export const Main: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <TransitionWrap>
        <SegmentsLayer kind="base" />
        <MontageLayer />
        <CardsLayer />
        <HighlightsLayer layer="behind" />
        <SegmentsLayer kind="fg" />
        <HighlightsLayer layer="front" />
        <NeonCoins />
        <Subtitles />
      </TransitionWrap>
      <LightLeaks />
      <SoundTrack />
    </AbsoluteFill>
  );
};
