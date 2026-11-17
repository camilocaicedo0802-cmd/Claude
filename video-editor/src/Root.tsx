import { Composition } from "remotion";
import { EDL } from "./edl";
import { Main } from "./Main";

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Main"
      component={Main}
      durationInFrames={EDL.total}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
