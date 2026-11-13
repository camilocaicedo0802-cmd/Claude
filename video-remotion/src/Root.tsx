import {Composition} from 'remotion';
import {TOTAL_SECONDS} from './v1/data';
import {Video1} from './v1/Video1';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Video1Grow" component={Video1} durationInFrames={Math.round(TOTAL_SECONDS * 30)} fps={30} width={1080} height={1920} />
    </>
  );
};
