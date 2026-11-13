import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES} from '../data';
import {clamp, easeInOut, easeOut} from '../helpers';
import {C, OUTFIT} from '../theme';

const Word: React.FC<{text: string; at: number; strike: number; y: number; end: number}> = ({text, at, strike, y, end}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(frame - at * fps, [0, 6], [0, 1], {...clamp, easing: easeOut});
  const s = interpolate(frame - strike * fps, [0, 7], [0, 1], {...clamp, easing: easeInOut});
  const out = interpolate(frame, [end * fps - 5, end * fps], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, translate: '0 -50%', display: 'flex', justifyContent: 'center', opacity: p * (1 - out), filter: `blur(${18 * (1 - p) + 14 * out}px)`}}>
      <div style={{position: 'relative', scale: String(interpolate(p, [0, 1], [1.25, 1]))}}>
        <span
          style={{
            fontFamily: OUTFIT,
            fontWeight: 800,
            fontSize: 170,
            letterSpacing: '-0.05em',
            lineHeight: 1,
            backgroundImage: C.chrome,
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            color: 'transparent',
            filter: `drop-shadow(0 0 12px rgba(255,255,255,0.35)) ${s > 0.5 ? 'brightness(0.7)' : ''}`,
          }}
        >
          {text}
        </span>
        <div
          style={{
            position: 'absolute',
            left: -24,
            right: -24,
            top: '54%',
            height: 18,
            borderRadius: 9,
            background: C.purpleGrad,
            boxShadow: `0 0 18px ${C.purpleGlow}`,
            transformOrigin: 'left center',
            scale: `${s} 1`,
            rotate: '-4deg',
          }}
        />
      </div>
    </div>
  );
};

/** "precios" y "producto" tachados: no son el problema. */
export const Tachado: React.FC = () => {
  const sc = SCENES.tachado;
  return (
    <AbsoluteFill>
      <Word text="precios" at={sc.precios} strike={sc.strike1} y={1150} end={sc.end} />
      <Word text="producto" at={sc.producto} strike={sc.strike2} y={1340} end={sc.end} />
    </AbsoluteFill>
  );
};
