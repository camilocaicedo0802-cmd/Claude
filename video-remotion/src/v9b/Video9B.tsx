import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {clamp, rand} from '../engine/helpers';
import {Sonido} from '../engine/Sonido';
import {SpecContext} from '../engine/spec';
import {C, OUTFIT} from '../v1/theme';
import {Captions} from './Captions';
import {SHAKES, SPEC_B, SPEECH, T, TOTAL, ws} from './data';
import {Botones, Bateria, Chat, Cierre, EmbudoAnuncio, Split, Versus, Visor} from './Escenas';
import {BigNumber, Calendario, Cutout, Foco, Marquee} from './Fondos';
import {Live} from './Live';

const F = 30;
const easeIn = Easing.in(Easing.cubic);
const STRIPES = [T.s1, T.s7, T.end];
const GLITCH = [T.s4, T.s13];
const FLASH = [T.s5, T.s12, ws(89), ws(90) + 0.22];

/** Fondo sustituido: fondo + elementos detrás + persona recortada encima. */
const Swap: React.FC<{from: number; to: number; children: React.ReactNode}> = ({from, to, children}) => {
  const t = useCurrentFrame() / F;
  if (t < from || t >= to) return null;
  return (
    <AbsoluteFill>
      {children}
      <Cutout from={from} to={to} />
    </AbsoluteFill>
  );
};

/** Pegatina que salta y se balancea. */
const Sticker: React.FC<{at: number; until: number; x: number; y: number; size: number; text: string}> = ({at, until, x, y, size, text}) => {
  const frame = useCurrentFrame();
  const l = frame - at * F;
  if (l < 0 || frame >= until * F) return null;
  const s = interpolate(l, [0, 4, 8], [0, 1.2, 1], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        borderRadius: size / 2,
        background: C.purpleGrad,
        border: '8px solid #fff',
        display: 'grid',
        placeItems: 'center',
        fontFamily: OUTFIT,
        fontWeight: 900,
        fontSize: size * 0.6,
        color: '#fff',
        scale: String(s),
        rotate: `${Math.sin(l / 5) * 8}deg`,
        boxShadow: `0 10px 0 ${C.purpleShadow}, 0 0 40px ${C.purpleGlow}`,
      }}
    >
      {text}
    </div>
  );
};

/** Barrido de barras diagonales que tapa el corte. */
const Stripes: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {STRIPES.map((t) =>
        [0, 1, 2].map((i) => {
          const l = frame - t * F + i * 2 - 2;
          if (l < -8 || l > 9) return null;
          const x = interpolate(l, [-7, 7], [-3300, 1500], {...clamp, easing: easeIn});
          return (
            <div
              key={`${t}-${i}`}
              style={{
                position: 'absolute',
                top: -100,
                height: 2120,
                left: x,
                width: 3000,
                transform: 'skewX(-15deg)',
                background: ['#FFFFFF', '#B701FC', C.purpleGrad][i],
              }}
            />
          );
        }),
      )}
    </>
  );
};

const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  let v = 0;
  for (const t of FLASH) v = Math.max(v, interpolate(frame - t * F, [-1, 0, 4], [0, 0.95, 0], clamp));
  return v > 0.01 ? <AbsoluteFill style={{background: '#fff', opacity: v}} /> : null;
};

const GlitchBars: React.FC = () => {
  const frame = useCurrentFrame();
  const g = GLITCH.find((t) => frame - t * F >= -2 && frame - t * F <= 3);
  if (g === undefined) return null;
  return (
    <AbsoluteFill>
      {Array.from({length: 5}, (_, i) => {
        const r = rand(frame * 13 + i * 7);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: r * 1800,
              height: 20 + rand(frame + i) * 90,
              background: i % 2 ? 'rgba(183,1,252,0.55)' : 'rgba(255,255,255,0.45)',
              translate: `${(rand(frame * 3 + i) - 0.5) * 120}px 0`,
              mixBlendMode: 'screen',
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const w = (frame / (TOTAL * F)) * 1080;
  return <div style={{position: 'absolute', left: 0, top: 0, height: 12, width: w, background: C.purpleGrad, boxShadow: `0 0 18px ${C.purpleGlow}`}} />;
};

/** Pista base (voz + imagen) con el zoom a través hacia el embudo. */
const Base: React.FC = () => {
  const frame = useCurrentFrame();
  const z = frame < T.s11 * F ? interpolate(frame, [T.s11 * F - 6, T.s11 * F], [0, 1], {...clamp, easing: easeIn}) : 0;
  return (
    <AbsoluteFill style={{scale: String(1 + z * 0.35), filter: z > 0 ? `blur(${z * 18}px)` : undefined}}>
      <Live from={0} to={SPEECH} audio />
    </AbsoluteFill>
  );
};

export const Video9B: React.FC = () => {
  const frame = useCurrentFrame();
  // sacudida de cámara en los golpes
  let sx = 0;
  let sy = 0;
  for (const t of SHAKES) {
    const l = frame - t * F;
    if (l >= 0 && l < 9) {
      const a = 18 * (1 - l / 9);
      sx = (rand(frame * 1.7) - 0.5) * 2 * a;
      sy = (rand(frame * 2.3 + 5) - 0.5) * 2 * a;
    }
  }
  // glitch: copias desplazadas morado/blanco
  const g = GLITCH.find((t) => frame - t * F >= -2 && frame - t * F <= 3);
  const gj = g !== undefined ? (rand(frame * 5) - 0.5) * 40 : 0;
  return (
    <SpecContext.Provider value={SPEC_B}>
      <AbsoluteFill style={{background: C.black}}>
        <AbsoluteFill
          style={{
            translate: `${sx + gj}px ${sy}px`,
            filter: g !== undefined ? 'drop-shadow(14px 0 0 rgba(183,1,252,0.85)) drop-shadow(-14px 0 0 rgba(255,255,255,0.55))' : undefined,
          }}
        >
          <Base />
          <Swap from={T.s1} to={T.s2}>
            <Marquee rows={['REDES SOCIALES', 'REDES SOCIALES', 'REDES SOCIALES', 'REDES SOCIALES', 'REDES SOCIALES', 'REDES SOCIALES']} t0={T.s1} />
            <BigNumber text="2" at={ws(5)} />
          </Swap>
          <Swap from={T.s4} to={T.s5}>
            <Calendario t0={T.s4} tCount={[ws(29), ws(35)]} days={238} />
          </Swap>
          <Swap from={T.s7} to={T.s8}>
            <Marquee rows={['SÍ VENDEN', 'SÍ VENDEN', 'SÍ VENDEN', 'SÍ VENDEN', 'SÍ VENDEN', 'SÍ VENDEN']} t0={T.s7} />
          </Swap>
          <Swap from={T.s12} to={T.s13}>
            <Foco t0={T.s12} />
          </Swap>
          <Sticker at={ws(23)} until={T.s4} x={900} y={250} size={200} text="?" />
          <Sticker at={ws(63)} until={T.s8} x={860} y={300} size={200} text="✓" />
          <Bateria />
          <Visor />
          <Botones />
          <Versus />
          <Chat />
          <Split />
          <EmbudoAnuncio />
          <Captions />
          <Cierre />
        </AbsoluteFill>
        <GlitchBars />
        <Stripes />
        <Flash />
        <Progress />
        <Sonido />
      </AbsoluteFill>
    </SpecContext.Provider>
  );
};

