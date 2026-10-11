import React from "react";
import { Composition, Folder } from "remotion";
import "./fonts";
import { Main } from "./Main";
import { ExampleScene } from "./scenes/ExampleScene";
import { DURATION_S, FPS, H, W } from "./theme";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Main" component={Main} durationInFrames={Math.round(DURATION_S * FPS)} fps={FPS} width={W} height={H} />
    <Folder name="Escenas">
      {/* registra cada escena como composición propia para previsualizarla aislada */}
      <Composition id="Ejemplo-editorial" component={ExampleScene} durationInFrames={3 * FPS} fps={FPS} width={W} height={H} defaultProps={{ start: 0, variant: "editorial" as const }} />
      <Composition id="Ejemplo-wordpop" component={ExampleScene} durationInFrames={3 * FPS} fps={FPS} width={W} height={H} defaultProps={{ start: 0, variant: "wordpop" as const }} />
      <Composition id="Ejemplo-karaoke" component={ExampleScene} durationInFrames={3 * FPS} fps={FPS} width={W} height={H} defaultProps={{ start: 0, variant: "karaoke" as const }} />
    </Folder>
  </>
);
