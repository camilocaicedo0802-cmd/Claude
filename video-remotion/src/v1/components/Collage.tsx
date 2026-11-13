import {Video} from '@remotion/media';
import {AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES} from '../data';
import {clamp, easeInOut, easeOut, sec} from '../helpers';
import {C} from '../theme';
import {SEGMENTS} from '../timeline';

const TILES = Array.from({length: 16}, (_, i) => `img/collage/t${String(i + 1).padStart(2, '0')}.jpg`);

const Column: React.FC<{x: number; dir: number; offset: number; local: number}> = ({x, dir, offset, local}) => {
  const tileH = 590;
  const y = -300 + offset + dir * local * 2.2;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: 330, display: 'flex', flexDirection: 'column', gap: 20}}>
      {Array.from({length: 6}, (_, i) => TILES[(((i * 3 + Math.round(offset / 7)) % TILES.length) + TILES.length) % TILES.length]).map((t, i) => (
        <div key={i} style={{height: tileH, borderRadius: 10, overflow: 'hidden'}}>
          <Img src={staticFile(t)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
      ))}
    </div>
  );
};

/** Collage de publicaciones con el protagonista en B/N delante: "cómo te perciben". */
export const Collage: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sc = SCENES.collage;
  const startF = sec(sc.start, fps);
  const seg = SEGMENTS.find((s) => startF >= s.start && startF < s.start + (s.srcOut - s.srcIn))!;
  const endF = Math.min(sec(sc.end, fps), seg.start + (seg.srcOut - seg.srcIn));
  if (frame < startF || frame >= endF) return null;
  const local = frame - startF;
  const pin = interpolate(local, [0, 10], [0, 1], {...clamp, easing: easeOut});
  const pout = interpolate(frame, [endF - 6, endF], [0, 1], {...clamp, easing: easeInOut});
  return (
    <AbsoluteFill style={{background: C.black}}>
      <AbsoluteFill style={{opacity: 0.55, scale: String(interpolate(pin, [0, 1], [1.15, 1.0]) + local * 0.0006), rotate: '-4deg'}}>
        <Column x={-160} dir={1} offset={0} local={local} />
        <Column x={190} dir={-1} offset={-420} local={local} />
        <Column x={540} dir={1} offset={-180} local={local} />
        <Column x={890} dir={-1} offset={-600} local={local} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0.1) 20%, rgba(0,0,0,0.75) 100%)'}} />
      <div
        style={{
          position: 'absolute',
          left: 200,
          top: 600,
          width: 680,
          height: 1100,
          border: '8px solid #FFFFFF',
          boxShadow: '0 30px 80px rgba(0,0,0,0.7)',
          overflow: 'hidden',
          opacity: pin * (1 - pout),
          scale: String(interpolate(pin, [0, 1], [0.86, 1]) * (1 + local * 0.0007)),
          translate: `0 ${interpolate(pin, [0, 1], [80, 0])}px`,
          filter: `grayscale(1) contrast(1.12) ${pin < 1 ? `blur(${10 * (1 - pin)}px)` : ''}`,
        }}
      >
        <Sequence from={startF} durationInFrames={endF - startF} layout="none">
          <Video
            src={staticFile(`clips/v1g_${seg.take}.mp4`)}
            muted
            trimBefore={seg.srcIn + (startF - seg.start)}
            objectFit="cover"
            style={{width: 1080, height: 1920, position: 'absolute', left: -200, top: -460}}
          />
        </Sequence>
      </div>
    </AbsoluteFill>
  );
};
