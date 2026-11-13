import {Composition} from 'remotion';
import {TOTAL_SECONDS} from './v1/data';
import {Video1} from './v1/Video1';
import {TalkingOnly} from './Debug';
import {TOTAL as TOTAL9} from './v9/data';
import {Video9} from './v9/Video9';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Video1Grow" component={Video1} durationInFrames={Math.round(TOTAL_SECONDS * 30)} fps={30} width={1080} height={1920} />
      <Composition id="Video9Redes" component={Video9} durationInFrames={Math.round(TOTAL9 * 30)} fps={30} width={1080} height={1920} />
      <Composition id="DebugTalking" component={TalkingOnly} durationInFrames={Math.round(TOTAL_SECONDS * 30)} fps={30} width={1080} height={1920} />
    </>
  );
};
