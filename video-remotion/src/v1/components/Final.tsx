import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES, TOTAL_SECONDS} from '../data';
import {clamp, easeOut} from '../helpers';
import {OUTFIT} from '../theme';
import {GridBg} from './GridBg';
import {matteIndex, matteSrc} from './Silueta';

const POS = [
  {x: 90, y: 760},
  {x: 600, y: 860},
  {x: 300, y: 960},
];

/** Tarjeta de cierre: logo GROW MARKETING + silueta + palabras sueltas (estilo.md §4). */
export const Final: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = SCENES.final.start * fps;
  if (frame < s) return null;
  const local = frame - s;
  const pin = interpolate(local, [0, 9], [0, 1], {...clamp, easing: easeOut});
  const logoIn = interpolate(local, [3, 13], [0, 1], {...clamp, easing: easeOut});
  const fadeOut = interpolate(frame, [TOTAL_SECONDS * fps - 8, TOTAL_SECONDS * fps], [0, 1], clamp);
  const idx = matteIndex(frame, true);
  return (
    <AbsoluteFill style={{opacity: pin, fontFamily: OUTFIT}}>
      <GridBg drift={0.4} />
      {/* silueta */}
      {idx ? (
        <AbsoluteFill style={{translate: `0 ${interpolate(pin, [0, 1], [120, 230])}px`, scale: '0.92', filter: 'drop-shadow(0 30px 40px rgba(0,0,0,0.7))'}}>
          <Img src={matteSrc(idx)} style={{width: '100%', height: '100%'}} />
        </AbsoluteFill>
      ) : null}
      {/* logo */}
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
      {/* palabras sueltas */}
      {SCENES.final.words.map((w, i) => {
        const p = interpolate(frame - w.at * fps, [0, 6], [0, 1], {...clamp, easing: easeOut});
        return (
          <div
            key={w.t}
            style={{
              position: 'absolute',
              left: POS[i].x,
              top: POS[i].y,
              fontSize: 46,
              fontWeight: 600,
              letterSpacing: '-0.02em',
              color: '#D9D9D9',
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
