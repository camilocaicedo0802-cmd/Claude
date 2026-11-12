import { AbsoluteFill, Composition } from "remotion";

// Proyecto vertical 1080x1920 a 30 fps. La composición real del reel se añade en el paso 3.
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;

export const MyComposition = () => {
  return (
    <Composition
      id="SlateReel"
      component={Placeholder}
      durationInFrames={FPS * 5}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};

export const Placeholder: React.FC = () => {
  return <AbsoluteFill style={{ backgroundColor: "#f4efe9" }} />;
};
