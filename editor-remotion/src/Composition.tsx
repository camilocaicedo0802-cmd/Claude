import { AbsoluteFill, Composition } from "remotion";

export const FPS = 60;
export const WIDTH = 1080;
export const HEIGHT = 1920;

export const MyComposition = () => {
  return (
    <Composition
      id="Vertical"
      component={Placeholder}
      durationInFrames={10 * FPS}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};

const Placeholder: React.FC = () => {
  return <AbsoluteFill style={{ backgroundColor: "#0b0b0b" }} />;
};
