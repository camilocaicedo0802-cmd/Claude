import {AbsoluteFill, CalculateMetadataFunction, Composition} from 'remotion';

// Ganador 4 · «Los 3 problemas de las redes» — vertical 1080x1920 a 60 fps.
export const FPS = 60;
export const W = 1080;
export const H = 1920;

type Props = Record<string, unknown>;

const calculateMetadata: CalculateMetadataFunction<Props> = () => {
  return {};
};

export const MyComposition = () => {
  return (
    <Composition
      id="Ganador4"
      component={MyComponent}
      durationInFrames={FPS * 45}
      fps={FPS}
      width={W}
      height={H}
      calculateMetadata={calculateMetadata}
    />
  );
};

export const MyComponent: React.FC<Props> = () => {
  return <AbsoluteFill style={{background: '#000'}} />;
};
