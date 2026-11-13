import {Video} from '@remotion/media';
import {AbsoluteFill, Freeze, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {clamp, easeInOut} from './helpers';
import {segLen, segmentAt, useSpec} from './spec';
import {Segment, Spec} from './types';

const FPS = 30;
export const scaleFor = (spec: Spec, seg: Segment, local: number) => {
  const f = spec.framing[seg.idx] ?? {scale: [1, 1]};
  let s = interpolate(local, [0, segLen(seg)], f.scale, clamp);
  if (f.zoom) s *= interpolate(local, [f.zoom.s * FPS, f.zoom.e * FPS], [f.zoom.from, f.zoom.to], {...clamp, easing: easeInOut});
  return s;
};
export const segmentScaleAt = (spec: Spec, frame: number) => {
  const seg = segmentAt(spec, frame);
  return seg ? scaleFor(spec, seg, frame - seg.start) : 1;
};
export const maskUrl = (take: string, srcFrame: number) => staticFile(`mascaras/${take}/a_${String(srcFrame).padStart(5, '0')}.png`);

export const SegmentFrame: React.FC<{seg: Segment; masked?: boolean; extraScale?: number}> = ({seg, masked, extraScale = 1}) => {
  const spec = useSpec();
  const frame = useCurrentFrame();
  const scale = scaleFor(spec, seg, frame) * extraScale;
  const m = masked ? maskUrl(seg.take, seg.srcIn + Math.min(frame, segLen(seg) - 1)) : undefined;
  return (
    <AbsoluteFill
      style={{
        scale: String(scale),
        transformOrigin: '50% 42%',
        ...(m ? {maskImage: `url(${m})`, WebkitMaskImage: `url(${m})`, maskSize: '100% 100%', WebkitMaskSize: '100% 100%'} : {}),
      }}
    >
      <Video src={staticFile(`clips/${spec.clipPrefix}_${seg.take}.mp4`)} trimBefore={seg.srcIn} muted={masked} objectFit="cover" style={{width: '100%', height: '100%'}} />
    </AbsoluteFill>
  );
};

/** Pista base hablada (jump cuts sin pausas). */
export const Talking: React.FC = () => {
  const spec = useSpec();
  return (
    <AbsoluteFill>
      {spec.segments.map((seg) => (
        <Sequence key={seg.idx} name={`Toma ${seg.take} #${seg.idx}`} from={seg.start} durationInFrames={segLen(seg)}>
          <SegmentFrame seg={seg} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

/** Persona recortada (máscara por fotograma) encima de los títulos en escena. */
export const Person: React.FC<{ranges: [number, number][]}> = ({ranges}) => {
  const spec = useSpec();
  const {fps} = useVideoConfig();
  const items: {seg: Segment; from: number; to: number}[] = [];
  for (const [s, e] of ranges) {
    const a = Math.round(s * fps);
    const b = Math.round(e * fps);
    for (const seg of spec.segments) {
      const from = Math.max(a, seg.start);
      const to = Math.min(b, seg.start + segLen(seg));
      if (to > from) items.push({seg, from, to});
    }
  }
  return (
    <AbsoluteFill>
      {items.map(({seg, from, to}, i) => (
        <Sequence key={i} name={`Silueta #${seg.idx}`} from={from} durationInFrames={to - from}>
          <Sequence from={seg.start - from} layout="none">
            <SegmentFrame seg={seg} masked />
          </Sequence>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

/** Persona recortada para el cierre: sigue hablando y, al acabar la voz, se congela en su último fotograma. */
export const EndPerson: React.FC<{from: number}> = ({from}) => {
  const spec = useSpec();
  const frame = useCurrentFrame();
  const last = spec.segments[spec.segments.length - 1];
  const seg = segmentAt(spec, frame);
  if (frame < from) return null;
  if (seg) {
    return (
      <Sequence from={seg.start} durationInFrames={segLen(seg)} layout="none">
        <SegmentFrame seg={seg} masked />
      </Sequence>
    );
  }
  return (
    <Freeze frame={segLen(last) - 1}>
      <SegmentFrame seg={last} masked />
    </Freeze>
  );
};
