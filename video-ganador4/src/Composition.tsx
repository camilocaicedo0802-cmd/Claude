import {Composition} from 'remotion';
import {FPS, H, TOTAL, W} from './base';
import {Ganador4} from './Ganador4';

// Ganador 4 · «Los 3 problemas de las redes» — vertical 1080x1920 a 60 fps.
export const MyComposition = () => {
  return <Composition id="Ganador4" component={Ganador4} durationInFrames={Math.round(TOTAL * FPS)} fps={FPS} width={W} height={H} />;
};
