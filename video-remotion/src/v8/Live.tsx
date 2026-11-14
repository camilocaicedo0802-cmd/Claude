import {Video} from '@remotion/media';
import {AbsoluteFill, Freeze, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {clamp} from '../engine/helpers';
import {scaleFor} from '../engine/Talking';
import {segLen, useSpec} from '../engine/spec';
import {Segment} from '../engine/types';
import {SNAPS} from './data';

const FPS = 30;

/** Factor de zoom de golpe en el fotograma absoluto f (se mantiene hasta el corte siguiente). */
export const snapAt = (seg: Segment, f: number) => {
  let k = 1;
  for (const s of SNAPS) {
    const at = Math.round(s.t * FPS);
    if (at >= seg.start && at < seg.start + segLen(seg)) k *= interpolate(f - at, [0, 2], [1, s.f], clamp);
  }
  return k;
};

const maskOf = (kind: 'a' | 'c', take: string, srcFrame: number) => staticFile(`mascaras/${take}/${kind}_${String(srcFrame).padStart(5, '0')}.png`);

const Frame: React.FC<{seg: Segment; mask?: 'a' | 'c'; framing: boolean; audio: boolean}> = ({seg, mask, framing, audio}) => {
  const spec = useSpec();
  const local = useCurrentFrame();
  const scale = framing ? scaleFor(spec, seg, local) * snapAt(seg, seg.start + local) : 1;
  const m = mask ? maskOf(mask, seg.take, seg.srcIn + Math.min(local, segLen(seg) - 1)) : undefined;
  return (
    <AbsoluteFill
      style={{
        scale: String(scale),
        transformOrigin: '50% 42%',
        ...(m ? {maskImage: `url(${m})`, WebkitMaskImage: `url(${m})`, maskSize: '100% 100%', WebkitMaskSize: '100% 100%'} : {}),
      }}
    >
      <Video src={staticFile(`clips/${spec.clipPrefix}_${seg.take}.mp4`)} trimBefore={seg.srcIn} muted={!audio} objectFit="cover" style={{width: '100%', height: '100%'}} />
    </AbsoluteFill>
  );
};

/**
 * La persona hablando entre `from` y `to` (s), con los mismos cortes que la voz.
 * mask 'c' = recorte limpio (sin TV ni silla) para cambiar el fondo.
 */
export const Live: React.FC<{from: number; to: number; mask?: 'a' | 'c'; framing?: boolean; audio?: boolean}> = ({from, to, mask, framing = true, audio = false}) => {
  const spec = useSpec();
  const a = Math.round(from * FPS);
  const b = Math.round(to * FPS);
  const items = spec.segments
    .map((seg) => ({seg, s: Math.max(a, seg.start), e: Math.min(b, seg.start + segLen(seg))}))
    .filter((x) => x.e > x.s);
  return (
    <AbsoluteFill>
      {items.map(({seg, s, e}) => (
        <Sequence key={seg.idx} name={`Toma ${seg.take} #${seg.idx}`} from={s} durationInFrames={e - s}>
          <Sequence from={seg.start - s} layout="none">
            <Frame seg={seg} mask={mask} framing={framing} audio={audio} />
          </Sequence>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

/** Último fotograma de la voz congelado (para el cierre). */
export const LastFrame: React.FC<{mask?: 'a' | 'c'}> = ({mask}) => {
  const spec = useSpec();
  const last = spec.segments[spec.segments.length - 1];
  return (
    <Freeze frame={segLen(last) - 1}>
      <Frame seg={last} mask={mask} framing={false} audio={false} />
    </Freeze>
  );
};
