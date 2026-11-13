import React from "react";
import { AbsoluteFill } from "remotion";
import { AudioLayer } from "./components/AudioLayer";
import { BRollLayer, MatteLayer } from "./components/BRollLayer";
import { Captions } from "./components/Captions";
import { FullScreenScenes, GradeOverlays, Graphics, TopLayer } from "./components/Graphics";
import { TalkingHead } from "./components/TalkingHead";

/** Reel vertical de Macizo editado según estilo.md. Orden de capas de abajo arriba. */
export const Reel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <TalkingHead />
      <BRollLayer />
      {/* Texto detrás de la persona: subtítulo -> persona recortada encima -> etalonaje común */}
      <Captions behind />
      <MatteLayer />
      <GradeOverlays />
      <FullScreenScenes />
      <Graphics />
      <Captions />
      <TopLayer />
      <AudioLayer />
    </AbsoluteFill>
  );
};
