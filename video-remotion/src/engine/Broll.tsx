import {Video} from '@remotion/media';
import {AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {useSpec} from './spec';
import {BrollDef} from './types';
import {clamp, sec} from './helpers';

const BrollClip: React.FC<{b: BrollDef}> = ({b}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dur = sec(b.end - b.start, fps);
  const z = b.zoom ?? [1, 1.04];
  const scale = interpolate(frame, [0, dur], z, clamp);
  return (
    <AbsoluteFill style={{scale: String(scale), filter: b.bw ? 'grayscale(1) contrast(1.1)' : undefined}}>
      <Video src={staticFile(b.src)} muted trimBefore={sec(b.trim ?? 0, fps)} objectFit="cover" style={{width: '100%', height: '100%'}} />
    </AbsoluteFill>
  );
};

/** B-roll a pantalla completa (la voz sigue sonando debajo). */
export const Broll: React.FC = () => {
  const spec = useSpec();
  const {fps} = useVideoConfig();
  return (
    <>
      {spec.broll.map((b) => (
        <Sequence key={b.src + b.start} name={`B-roll ${b.src}`} from={sec(b.start, fps)} durationInFrames={sec(b.end - b.start, fps)}>
          <BrollClip b={b} />
        </Sequence>
      ))}
    </>
  );
};
