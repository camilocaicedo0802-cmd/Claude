import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeOut, rand} from '../engine/helpers';
import {OUTFIT} from '../v1/theme';

const F = 30;
export const PURPLE = '#B701FC';
export const INK = '#2A0050';

// ---------------------------------------------------------------- papel oscuro con grano
const GRAIN = `url("data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.55 0'/></filter><rect width='400' height='400' filter='url(#n)'/></svg>`,
)}")`;
const FIBRES = `url("data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'><filter id='f'><feTurbulence type='turbulence' baseFrequency='0.012 0.09' numOctaves='2' seed='4'/><feColorMatrix values='0 0 0 0 0.7  0 0 0 0 0.6  0 0 0 0 0.9  0 0 0 0.35 0'/></filter><rect width='600' height='600' filter='url(#f)'/></svg>`,
)}")`;

export const Papel: React.FC = () => (
  <AbsoluteFill style={{background: '#1A1222'}}>
    <AbsoluteFill style={{backgroundImage: FIBRES, opacity: 0.5}} />
    <AbsoluteFill style={{backgroundImage: GRAIN, opacity: 0.12, mixBlendMode: 'screen'}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(118,0,252,0.18) 0%, transparent 55%, rgba(0,0,0,0.55) 100%)'}} />
  </AbsoluteFill>
);

// ---------------------------------------------------------------- borde rasgado (polígono irregular)
export const torn = (w: number, h: number, seed: number, amp = 7, step = 16) => {
  const pts: string[] = [];
  const j = (i: number) => (rand(seed * 31.7 + i * 1.913) - 0.5) * 2 * amp;
  let i = 0;
  for (let x = 0; x <= w; x += step) pts.push(`${x}px ${Math.max(0, amp + j(i++))}px`);
  for (let y = 0; y <= h; y += step) pts.push(`${w - amp - j(i++)}px ${y}px`);
  for (let x = w; x >= 0; x -= step) pts.push(`${x}px ${h - amp - j(i++)}px`);
  for (let y = h; y >= 0; y -= step) pts.push(`${Math.max(0, amp + j(i++))}px ${y}px`);
  return `polygon(${pts.join(',')})`;
};

/** Movimiento stop-motion: el valor solo cambia cada `hold` fotogramas. */
export const stepped = (frame: number, hold = 2) => Math.floor(frame / hold) * hold;
export const jitter = (frame: number, seed: number, amt = 1) => {
  const k = Math.floor(frame / 3);
  return {x: (rand(k * 3.1 + seed) - 0.5) * 3 * amt, y: (rand(k * 5.7 + seed) - 0.5) * 3 * amt, r: (rand(k * 7.3 + seed) - 0.5) * 1.4 * amt};
};

/** Pieza de collage: entra a saltos (stop-motion), vibra un poco y sale. */
export const Pieza: React.FC<{
  at: number;
  until: number;
  x: number;
  y: number;
  w: number;
  h: number;
  rot?: number;
  seed?: number;
  from?: 'drop' | 'left' | 'right' | 'up';
  shadow?: boolean;
  children?: React.ReactNode;
}> = ({at, until, x, y, w, h, rot = 0, seed = 1, from = 'drop', shadow = true, children}) => {
  const frame = useCurrentFrame();
  const a = at * F;
  const b = until * F;
  if (frame < a || frame >= b) return null;
  const sf = stepped(frame - a, 2);
  const p = interpolate(sf, [0, 6], [0, 1], {...clamp, easing: easeOut});
  const out = interpolate(frame, [b - 4, b], [0, 1], clamp);
  const jt = jitter(frame, seed);
  const dx = from === 'left' ? -900 : from === 'right' ? 900 : 0;
  const dy = from === 'up' ? -900 : 0;
  const sc = from === 'drop' ? interpolate(p, [0, 1], [1.35, 1]) : 1;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        rotate: `${rot + (1 - p) * (from === 'drop' ? 9 : 0) + jt.r}deg`,
        translate: `${dx * (1 - p) + jt.x}px ${dy * (1 - p) + jt.y}px`,
        scale: String(sc * (1 - out * 0.15)),
        opacity: Math.min(1, p * 2) * (1 - out),
        filter: shadow ? 'drop-shadow(0 18px 22px rgba(0,0,0,0.55))' : undefined,
      }}
    >
      {children}
    </div>
  );
};

/** Marco de papel rasgado (borde blanco irregular) con contenido dentro. */
export const Rasgado: React.FC<{w: number; h: number; seed?: number; border?: number; children?: React.ReactNode}> = ({w, h, seed = 3, border = 14, children}) => (
  <div style={{position: 'relative', width: w, height: h}}>
    <div style={{position: 'absolute', inset: 0, background: '#F4F1EC', clipPath: torn(w, h, seed, 7)}} />
    <div style={{position: 'absolute', left: border, top: border, width: w - border * 2, height: h - border * 2, overflow: 'hidden', clipPath: torn(w - border * 2, h - border * 2, seed + 7, 3, 22), background: '#000'}}>
      {children}
    </div>
  </div>
);

/** Trozo de cinta adhesiva semitransparente. */
export const Cinta: React.FC<{x: number; y: number; w?: number; rot?: number; seed?: number}> = ({x, y, w = 170, rot = -8, seed = 2}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      width: w,
      height: 48,
      rotate: `${rot}deg`,
      background: 'repeating-linear-gradient(90deg, rgba(245,240,255,0.62) 0 10px, rgba(235,228,250,0.55) 10px 20px)',
      clipPath: torn(w, 48, seed, 4, 8),
      boxShadow: '0 2px 6px rgba(0,0,0,0.25)',
    }}
  />
);

/** Papel blanco rasgado con contenido (tickets, notas, burbujas…). */
export const Papelito: React.FC<{w: number; h: number; seed?: number; tint?: string; children?: React.ReactNode}> = ({w, h, seed = 5, tint = '#F4F1EC', children}) => (
  <div style={{position: 'relative', width: w, height: h}}>
    <div style={{position: 'absolute', inset: 0, background: tint, clipPath: torn(w, h, seed, 6, 14)}} />
    <div style={{position: 'absolute', inset: 0, padding: '22px 28px', fontFamily: OUTFIT, color: INK}}>{children}</div>
  </div>
);

// ---------------------------------------------------------------- garabatos de rotulador
const loop = (seed: number) => {
  const pts: string[] = [];
  const n = 40;
  for (let i = 0; i <= n * 1.15; i++) {
    const a = (i / n) * Math.PI * 2 - Math.PI * 0.6;
    const r = 1 + (rand(seed + i * 0.37) - 0.5) * 0.08 + (i / n) * 0.06;
    pts.push(`${(50 + Math.cos(a) * 46 * r).toFixed(1)} ${(50 + Math.sin(a) * 44 * r).toFixed(1)}`);
  }
  return `M ${pts.join(' L ')}`;
};
export const SHAPES = {
  circle: (seed: number) => loop(seed),
  underline: () => 'M2 60 C 20 40, 35 75, 52 55 S 80 40, 98 52',
  strike: () => 'M2 55 C 25 45, 40 62, 60 50 S 85 44, 98 50',
  arrow: () => 'M8 12 C 30 20, 55 45, 82 82 M82 82 L 60 78 M82 82 L 80 58',
  arrowR: () => 'M6 60 C 30 30, 60 30, 90 52 M90 52 L 70 40 M90 52 L 74 70',
  check: () => 'M10 55 L 38 85 L 94 12',
  cross: () => 'M12 12 L 88 88 M88 14 L 14 86',
  star: () => 'M50 6 L 61 38 L 95 38 L 67 58 L 78 92 L 50 71 L 22 92 L 33 58 L 5 38 L 39 38 Z',
  sparkle: () => 'M50 8 L 50 92 M8 50 L 92 50 M22 22 L 78 78 M78 22 L 22 78',
  bang: () => 'M30 8 L 30 62 M30 80 L 30 84 M70 8 L 70 62 M70 80 L 70 84',
};

/** Garabato que se dibuja solo (trazo de rotulador) y «hierve» un poco cada 3 fotogramas. */
export const Garabato: React.FC<{
  at: number;
  until: number;
  shape: keyof typeof SHAPES;
  x: number;
  y: number;
  w: number;
  h: number;
  color?: string;
  width?: number;
  draw?: number;
  rot?: number;
  seed?: number;
}> = ({at, until, shape, x, y, w, h, color = PURPLE, width = 9, draw = 8, rot = 0, seed = 1}) => {
  const frame = useCurrentFrame();
  const a = at * F;
  if (frame < a || frame >= until * F) return null;
  const p = interpolate(frame - a, [0, draw], [0, 1], {...clamp, easing: easeOut});
  const jt = jitter(frame, seed + 9, 0.6);
  const out = interpolate(frame, [until * F - 4, until * F], [1, 0], clamp);
  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      style={{position: 'absolute', left: x, top: y, width: w, height: h, overflow: 'visible', rotate: `${rot + jt.r}deg`, translate: `${jt.x}px ${jt.y}px`, opacity: out, filter: 'drop-shadow(0 3px 4px rgba(0,0,0,0.4))'}}
    >
      <path d={SHAPES[shape](seed)} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - p} vectorEffect="non-scaling-stroke" />
    </svg>
  );
};

// ---------------------------------------------------------------- sello que golpea
export const Sello: React.FC<{at: number; until: number; x: number; y: number; text: string; size?: number; rot?: number}> = ({at, until, x, y, text, size = 70, rot = -8}) => {
  const frame = useCurrentFrame();
  const l = frame - at * F;
  if (l < 0 || frame >= until * F) return null;
  const s = interpolate(l, [0, 3, 5], [2.4, 0.94, 1], clamp);
  const out = interpolate(frame, [until * F - 4, until * F], [1, 0], clamp);
  return (
    <div style={{position: 'absolute', left: x, top: y, translate: '-50% -50%', rotate: `${rot}deg`, scale: String(s), opacity: Math.min(1, l / 2 + 0.2) * out}}>
      <div
        style={{
          padding: `${size * 0.12}px ${size * 0.35}px ${size * 0.18}px`,
          border: `${Math.max(6, size * 0.1)}px solid ${PURPLE}`,
          borderRadius: size * 0.2,
          color: PURPLE,
          fontFamily: OUTFIT,
          fontWeight: 900,
          fontSize: size,
          letterSpacing: '0.02em',
          whiteSpace: 'nowrap',
          background: 'rgba(26,18,34,0.35)',
        }}
      >
        {text}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- transición: hoja de papel rasgada que pasa
export const Hoja: React.FC<{at: number; dir?: 'up' | 'left'}> = ({at, dir = 'up'}) => {
  const frame = useCurrentFrame();
  const l = frame - at * F;
  if (l < -7 || l > 7) return null;
  const q = interpolate(l, [-7, 7], [0, 1], clamp);
  const W = dir === 'up' ? 1080 : 2600;
  const H = dir === 'up' ? 2600 : 1920;
  const pos = interpolate(q, [0, 1], [dir === 'up' ? 1920 : 1080, dir === 'up' ? -2600 : -2600]);
  return (
    <div
      style={{
        position: 'absolute',
        left: dir === 'up' ? 0 : pos,
        top: dir === 'up' ? pos : 0,
        width: W,
        height: H,
        filter: 'drop-shadow(0 -10px 30px rgba(0,0,0,0.6))',
      }}
    >
      <div style={{position: 'absolute', inset: 0, background: '#F4F1EC', clipPath: torn(W, H, 11, 16, 26)}} />
      <div style={{position: 'absolute', left: 22, top: 22, right: 22, bottom: 22, clipPath: torn(W - 44, H - 44, 17, 12, 30), overflow: 'hidden'}}>
        <Papel />
      </div>
    </div>
  );
};

export const Destello: React.FC<{times: number[]}> = ({times}) => {
  const frame = useCurrentFrame();
  let v = 0;
  for (const t of times) v = Math.max(v, interpolate(frame - t * F, [-1, 0, 3], [0, 0.85, 0], clamp));
  return v > 0.01 ? <AbsoluteFill style={{background: '#fff', opacity: v}} /> : null;
};
