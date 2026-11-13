import {Video} from '@remotion/media';
import {AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FRAMING} from '../data';
import {clamp, easeInOut} from '../helpers';
import {SEGMENTS, Segment} from '../timeline';

const SegmentFrame: React.FC<{seg: Segment}> = ({seg}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dur = seg.srcOut - seg.srcIn;
  const f = FRAMING[seg.idx] ?? {scale: [1, 1]};
  let scale = interpolate(frame, [0, dur], f.scale, clamp);
  if (f.zoom) {
    scale *= interpolate(frame, [f.zoom.s * fps, f.zoom.e * fps], [f.zoom.from, f.zoom.to], {...clamp, easing: easeInOut});
  }
  return (
    <AbsoluteFill style={{scale: String(scale), transformOrigin: '50% 42%'}}>
      <Video src={staticFile(`clips/v1g_${seg.take}.mp4`)} trimBefore={seg.srcIn} objectFit="cover" style={{width: '100%', height: '100%'}} />
    </AbsoluteFill>
  );
};

/** Pista base: todas las tomas habladas, cortadas sin pausas (jump cuts). */
export const Talking: React.FC = () => {
  return (
    <AbsoluteFill>
      {SEGMENTS.map((seg) => (
        <Sequence key={seg.idx} name={`Toma ${seg.take} #${seg.idx}`} from={seg.start} durationInFrames={seg.srcOut - seg.srcIn}>
          <SegmentFrame seg={seg} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
