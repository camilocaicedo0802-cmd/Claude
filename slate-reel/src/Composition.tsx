import { Composition } from "remotion";
import { SLATE_REEL_DURATION, SlateReel } from "./SlateReel";
import "./theme";

// Proyecto vertical 1080×1920 a 30 fps.
export const MyComposition = () => {
  return (
    <Composition
      id="SlateReel"
      component={SlateReel}
      durationInFrames={SLATE_REEL_DURATION}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
