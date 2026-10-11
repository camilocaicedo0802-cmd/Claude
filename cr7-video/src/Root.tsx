import { Composition } from "remotion";
import { CR7, CR7_DURACION } from "./CR7";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CR7"
      component={CR7}
      durationInFrames={CR7_DURACION}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
