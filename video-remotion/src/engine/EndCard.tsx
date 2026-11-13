import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {clamp, easeOut} from './helpers';
import {useSpec} from './spec';
import {EndPerson} from './Talking';
import {GridBg} from './GridBg';
import {OUTFIT} from '../v1/theme';

// Palabras entre el logo y la cabeza (estilo.md §10.2): nunca encima de la cara
const POS = [
  {x: 80, y: 640},
  {x: 600, y: 690},
  {x: 250, y: 750},
  {x: 560, y: 600},
];

/** Cierre: cuadrícula oscura, logo GROW MARKETING, persona recortada y palabras sueltas. */
export const EndCard: React.FC = () => {
  const spec = useSpec();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!spec.end) return null;
  const s = spec.end.start * fps;
  if (frame < s) return null;
  const local = frame - s;
  const pin = interpolate(local, [0, 9], [0, 1], {...clamp, easing: easeOut});
  const logoIn = interpolate(local, [3, 13], [0, 1], {...clamp, easing: easeOut});
  const fadeOut = interpolate(frame, [spec.total * fps - 8, spec.total * fps], [0, 1], clamp);
  return (
    <AbsoluteFill style={{opacity: pin, fontFamily: OUTFIT}}>
      <GridBg drift={0.4} />
      <AbsoluteFill style={{translate: `0 ${interpolate(pin, [0, 1], [120, 230])}px`, scale: '0.92', filter: 'drop-shadow(0 30px 40px rgba(0,0,0,0.7))'}}>
        <EndPerson from={Math.round(s)} />
      </AbsoluteFill>
      <div style={{position: 'absolute', left: 0, right: 0, top: 380, display: 'flex', justifyContent: 'center'}}>
        <Img
          src={staticFile('img/logo_grow.png')}
          style={{
            width: 700,
            opacity: logoIn,
            scale: String(interpolate(logoIn, [0, 1], [1.25, 1]) * interpolate(local, [0, 90], [1, 1.04], clamp)),
            filter: `blur(${14 * (1 - logoIn)}px) drop-shadow(0 0 30px rgba(170,0,255,0.35))`,
          }}
        />
      </div>
      {spec.end.words.map((w, i) => {
        const p = interpolate(frame - w.at * fps, [0, 6], [0, 1], {...clamp, easing: easeOut});
        return (
          <div
            key={w.t}
            style={{
              position: 'absolute',
              left: POS[i % POS.length].x,
              top: POS[i % POS.length].y,
              fontSize: 46,
              fontWeight: 600,
              letterSpacing: '-0.02em',
              color: '#E6E6E6',
              opacity: p,
              filter: `blur(${10 * (1 - p)}px)`,
              translate: `0 ${interpolate(p, [0, 1], [24, 0])}px`,
            }}
          >
            {w.t}
          </div>
        );
      })}
      <AbsoluteFill style={{background: '#000', opacity: fadeOut}} />
    </AbsoluteFill>
  );
};
