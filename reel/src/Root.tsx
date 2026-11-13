import React from "react";
import { Composition } from "remotion";
import { Reel } from "./Reel";
import { FPS, H, W } from "./theme";
import { TOTAL } from "./timeline";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Reel"
      component={Reel}
      durationInFrames={Math.round(TOTAL * FPS)}
      fps={FPS}
      width={W}
      height={H}
    />
  );
};
