import {Video} from '@remotion/media';
import {AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CARDS, CardDef} from '../data';
import {clamp, easeInOut, easeOut, sec} from '../helpers';

const Card: React.FC<{c: CardDef}> = ({c}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dur = sec(c.end - c.start, fps);
  const pin = interpolate(frame, [0, 8], [0, 1], {...clamp, easing: easeOut});
  const pout = interpolate(frame, [dur - 6, dur], [0, 1], {...clamp, easing: easeInOut});
  const h = c.width / c.aspect;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          left: (1080 - c.width) / 2,
          top: c.y - h / 2,
          width: c.width,
          height: h,
          border: '8px solid #FFFFFF',
          borderRadius: 14,
          overflow: 'hidden',
          boxShadow: '0 20px 50px rgba(0,0,0,0.6)',
          opacity: pin * (1 - pout),
          scale: String(interpolate(pin, [0, 1], [0.85, 1]) * interpolate(frame, [0, dur], [1, 1.04], clamp)),
          translate: `0 ${interpolate(pin, [0, 1], [90, 0]) - 60 * pout}px`,
          rotate: `${(c.rotate ?? 0) * pin}deg`,
          filter: `${pin < 1 || pout > 0 ? `blur(${14 * (1 - pin) + 14 * pout}px)` : ''} ${c.bw ? 'grayscale(1) contrast(1.12)' : ''}`,
        }}
      >
        <Video src={staticFile(c.src)} muted trimBefore={sec(c.trim ?? 0, fps)} objectFit="cover" style={{width: '100%', height: '100%'}} />
      </div>
    </AbsoluteFill>
  );
};

/** Ventanas con clip horizontal sobre el fondo desenfocado (estilo.md §5). */
export const Cards: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <>
      {CARDS.map((c) => (
        <Sequence key={c.src} name={`Tarjeta ${c.src}`} from={sec(c.start, fps)} durationInFrames={sec(c.end - c.start, fps)}>
          <Card c={c} />
        </Sequence>
      ))}
    </>
  );
};
