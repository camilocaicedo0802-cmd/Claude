import {Video} from '@remotion/media';
import {AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FRAMING} from '../data';
import {clamp, easeInOut} from '../helpers';
import {SEGMENTS, Segment} from '../timeline';

const FPS = 30;

/** Escala de "cámara" de un segmento en su fotograma local. */
const scaleFor = (seg: Segment, local: number) => {
  const dur = seg.srcOut - seg.srcIn;
  const f = FRAMING[seg.idx] ?? {scale: [1, 1]};
  let s = interpolate(local, [0, dur], f.scale, clamp);
  if (f.zoom) s *= interpolate(local, [f.zoom.s * FPS, f.zoom.e * FPS], [f.zoom.from, f.zoom.to], {...clamp, easing: easeInOut});
  return s;
};

export const segmentAt = (frame: number) => SEGMENTS.find((s) => frame >= s.start && frame < s.start + (s.srcOut - s.srcIn));

/** Escala de cámara en un fotograma global (para que los títulos sigan el zoom). */
export const segmentScaleAt = (frame: number) => {
  const seg = segmentAt(frame);
  return seg ? scaleFor(seg, frame - seg.start) : 1;
};

const SegmentFrame: React.FC<{seg: Segment; masked?: boolean}> = ({seg, masked}) => {
  const frame = useCurrentFrame();
  const scale = scaleFor(seg, frame);
  const maskUrl = masked ? staticFile(`mascaras/${seg.take}/a_${String(seg.srcIn + frame).padStart(5, '0')}.png`) : undefined;
  return (
    <AbsoluteFill
      style={{
        scale: String(scale),
        transformOrigin: '50% 42%',
        ...(maskUrl
          ? {
              maskImage: `url(${maskUrl})`,
              WebkitMaskImage: `url(${maskUrl})`,
              maskSize: '100% 100%',
              WebkitMaskSize: '100% 100%',
            }
          : {}),
      }}
    >
      <Video src={staticFile(`clips/v1g_${seg.take}.mp4`)} trimBefore={seg.srcIn} muted={masked} objectFit="cover" style={{width: '100%', height: '100%'}} />
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

/**
 * Capa de la persona recortada (máscara por fotograma) que va ENCIMA de los títulos
 * "en escena": así el texto queda detrás de él y nunca le tapa la cara.
 * Solo se dibuja en los rangos indicados (para no decodificar el vídeo dos veces de más).
 */
export const Person: React.FC<{ranges: [number, number][]}> = ({ranges}) => {
  const {fps} = useVideoConfig();
  const items: {seg: Segment; from: number; to: number}[] = [];
  for (const [s, e] of ranges) {
    const a = Math.round(s * fps);
    const b = Math.round(e * fps);
    for (const seg of SEGMENTS) {
      const ss = seg.start;
      const se = seg.start + (seg.srcOut - seg.srcIn);
      const from = Math.max(a, ss);
      const to = Math.min(b, se);
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
