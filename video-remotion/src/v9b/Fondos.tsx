import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeOut} from '../engine/helpers';
import {C, OUTFIT} from '../v1/theme';
import {Live} from './Live';

/** Persona recortada (máscara limpia) con contorno blanco tipo pegatina. */
export const Cutout: React.FC<{from: number; to: number; outline?: boolean}> = ({from, to, outline = true}) => (
  <AbsoluteFill
    style={{
      filter: outline
        ? 'drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 0 40px rgba(150,1,253,0.9))'
        : undefined,
    }}
  >
    <Live from={from} to={to} mask="c" />
  </AbsoluteFill>
);

/** Filas de texto gigante en movimiento sobre degradado morado. */
export const Marquee: React.FC<{rows: string[]; tone?: 'purple' | 'deep'; t0: number}> = ({rows, tone = 'purple', t0}) => {
  const frame = useCurrentFrame();
  const local = frame - t0 * 30;
  const bg =
    tone === 'purple'
      ? 'radial-gradient(ellipse at 50% 38%, #B701FC 0%, #9601FD 28%, #7600FC 52%, #3D0080 82%, #1C003D 100%)'
      : 'radial-gradient(ellipse at 50% 40%, #3D0080 0%, #1C003D 55%, #0B0B0B 100%)';
  return (
    <AbsoluteFill style={{background: bg, overflow: 'hidden'}}>
      {rows.map((r, i) => {
        const dir = i % 2 ? 1 : -1;
        const x = dir * ((local * 7 + i * 260) % 1400) - 700;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: 120 + i * 330,
              left: 0,
              whiteSpace: 'nowrap',
              fontFamily: OUTFIT,
              fontWeight: 900,
              fontSize: 250,
              letterSpacing: '-0.04em',
              lineHeight: 1,
              translate: `${x}px 0`,
              color: i % 2 ? 'rgba(255,255,255,0.13)' : 'transparent',
              WebkitTextStroke: i % 2 ? undefined : '3px rgba(255,255,255,0.45)',
              opacity: interpolate(local, [i * 2, i * 2 + 8], [0, 1], clamp),
            }}
          >
            {`${r} · ${r} · ${r} · ${r} · `}
          </div>
        );
      })}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 55%, transparent 40%, rgba(0,0,0,0.45) 100%)'}} />
    </AbsoluteFill>
  );
};

/** «2» gigante detrás de la persona: golpe de entrada y deriva lenta. */
export const BigNumber: React.FC<{text: string; at: number}> = ({text, at}) => {
  const frame = useCurrentFrame();
  const l = frame - at * 30;
  if (l < -1) return null;
  const p = interpolate(l, [0, 5], [0, 1], {...clamp, easing: easeOut});
  const ext = Array.from({length: 12}, (_, i) => `${i + 1}px ${i + 1}px 0 ${C.purpleShadow}`).join(', ');
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'flex-start'}}>
      <div
        style={{
          marginTop: -40,
          fontFamily: OUTFIT,
          fontWeight: 900,
          fontSize: 1150,
          lineHeight: 1,
          color: '#FFFFFF',
          textShadow: `${ext}, 0 0 80px rgba(183,1,252,0.9)`,
          scale: String(interpolate(p, [0, 1], [2.4, 1]) * (1 + l * 0.0012)),
          rotate: `${interpolate(p, [0, 1], [-14, -5])}deg`,
          opacity: interpolate(l, [0, 2], [0, 1], clamp),
          filter: p < 1 ? `blur(${(1 - p) * 14}px)` : undefined,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

/** Calendario sin publicaciones: días tachados uno a uno + contador «hace N días». */
export const Calendario: React.FC<{t0: number; tCount: [number, number]; days: number}> = ({t0, tCount, days}) => {
  const frame = useCurrentFrame();
  const local = frame - t0 * 30;
  const n = Math.round(interpolate(frame, [tCount[0] * 30, tCount[1] * 30], [0, days], {...clamp, easing: easeOut}));
  const cells = 35;
  const crossed = Math.floor(interpolate(frame, [tCount[0] * 30, tCount[1] * 30], [0, cells], clamp));
  const cw = 136;
  const ch = 150;
  const x0 = (1080 - cw * 7) / 2;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, #1F1F1F 0%, #0B0B0B 70%)', fontFamily: OUTFIT}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 130, textAlign: 'center', color: 'rgba(255,255,255,0.85)', fontSize: 50, fontWeight: 700, letterSpacing: '0.12em', opacity: interpolate(local, [4, 10], [0, 1], clamp)}}>
        ÚLTIMA PUBLICACIÓN
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 200, textAlign: 'center', fontSize: 150, fontWeight: 900, letterSpacing: '-0.04em', color: '#fff', lineHeight: 1, opacity: interpolate(local, [6, 12], [0, 1], clamp)}}>
        hace{' '}
        <span style={{color: '#C873FF', textShadow: `0 6px 0 ${C.purpleShadow}, 0 0 40px ${C.purpleGlow}`}}>{n}</span> días
      </div>
      {Array.from({length: cells}, (_, i) => {
        const r = Math.floor(i / 7);
        const c = i % 7;
        const appear = interpolate(local, [2 + i * 0.35, 8 + i * 0.35], [0, 1], {...clamp, easing: easeOut});
        const x = i < crossed;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x0 + c * cw + 6,
              top: 470 + r * ch + 6,
              width: cw - 12,
              height: ch - 12,
              borderRadius: 18,
              border: '3px solid rgba(255,255,255,0.22)',
              background: 'rgba(255,255,255,0.04)',
              opacity: appear,
              scale: String(interpolate(appear, [0, 1], [0.7, 1])),
              color: 'rgba(255,255,255,0.45)',
              fontSize: 34,
              fontWeight: 700,
              padding: '10px 14px',
            }}
          >
            {i + 1 <= 31 ? i + 1 : ''}
            {x ? (
              <svg viewBox="0 0 100 100" style={{position: 'absolute', inset: 12}}>
                <path d="M18 18 L82 82 M82 18 L18 82" stroke="#B701FC" strokeWidth="11" strokeLinecap="round" style={{filter: 'drop-shadow(0 0 6px rgba(183,1,252,0.9))'}} />
              </svg>
            ) : null}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Fondo negro con foco morado detrás de la cabeza. */
export const Foco: React.FC<{t0: number}> = ({t0}) => {
  const frame = useCurrentFrame();
  const l = frame - t0 * 30;
  return (
    <AbsoluteFill style={{background: '#070707', overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          background: 'radial-gradient(circle at 50% 46%, rgba(183,1,252,0.85) 0%, rgba(118,0,252,0.45) 22%, rgba(61,0,128,0.15) 42%, transparent 60%)',
          scale: String(interpolate(l, [0, 10], [0.4, 1], {...clamp, easing: easeOut}) * (1 + 0.03 * Math.sin(l / 6))),
        }}
      />
      {[
        {x: 70, y: 260, s: 300, r: -14},
        {x: 760, y: 180, s: 380, r: 12},
        {x: 820, y: 1180, s: 260, r: 18},
        {x: 40, y: 1250, s: 220, r: -20},
      ].map((q, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: q.x,
            top: q.y + Math.sin((l + i * 20) / 14) * 16,
            fontFamily: OUTFIT,
            fontWeight: 900,
            fontSize: q.s,
            lineHeight: 1,
            color: 'transparent',
            WebkitTextStroke: '3px rgba(255,255,255,0.35)',
            rotate: `${q.r + l * 0.3}deg`,
            opacity: interpolate(l, [3 + i * 2, 10 + i * 2], [0, 1], clamp),
          }}
        >
          ?
        </div>
      ))}
    </AbsoluteFill>
  );
};
