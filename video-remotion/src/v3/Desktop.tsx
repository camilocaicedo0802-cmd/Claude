import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOut} from '../engine/helpers';
import {C, OUTFIT} from '../v1/theme';
import {CURSOR, CURSOR_ON, MODES, ScreenState, T} from './data';
import {LastFrame, Live} from './Live';
import {SPEECH} from './data';

const F = 30;

// ---------------------------------------------------------------- fondo de escritorio
export const Escritorio: React.FC = () => {
  const frame = useCurrentFrame();
  const a = frame / 40;
  return (
    <AbsoluteFill style={{background: '#07050B', overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 70% 45% at ${30 + Math.sin(a) * 10}% ${25 + Math.cos(a * 0.8) * 6}%, rgba(150,1,253,0.55) 0%, transparent 70%),
            radial-gradient(ellipse 60% 40% at ${75 + Math.cos(a * 0.7) * 8}% ${70 + Math.sin(a * 0.9) * 6}%, rgba(118,0,252,0.45) 0%, transparent 70%),
            radial-gradient(ellipse 50% 30% at 50% 105%, rgba(183,1,252,0.35) 0%, transparent 70%)`,
        }}
      />
      <AbsoluteFill style={{backgroundImage: 'radial-gradient(rgba(255,255,255,0.09) 1.6px, transparent 1.8px)', backgroundSize: '36px 36px'}} />
    </AbsoluteFill>
  );
};

export const MenuBar: React.FC<{opacity: number}> = ({opacity}) => (
  <div
    style={{
      position: 'absolute',
      left: 0,
      right: 0,
      top: 0,
      height: 54,
      background: 'rgba(20,16,28,0.55)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      gap: 34,
      padding: '0 30px',
      fontFamily: OUTFIT,
      fontSize: 24,
      fontWeight: 600,
      color: 'rgba(255,255,255,0.85)',
      opacity,
    }}
  >
    <span style={{fontWeight: 800}}>Grow Marketing</span>
    <span>Archivo</span>
    <span>Editar</span>
    <span>Ver</span>
    <span style={{marginLeft: 'auto'}}>100% ▮</span>
    <span>9:41</span>
  </div>
);

// ---------------------------------------------------------------- ventana de app
export const Ventana: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  title: string;
  from: number;
  to: number;
  enter?: 'pop' | 'left' | 'right' | 'up';
  light?: boolean;
  children?: React.ReactNode;
}> = ({x, y, w, h, title, from, to, enter = 'pop', light = false, children}) => {
  const frame = useCurrentFrame();
  const a = from * F;
  const b = to * F;
  if (frame < a - 1 || frame >= b) return null;
  const p = interpolate(frame - a, [0, 8], [0, 1], {...clamp, easing: easeOut});
  const o = interpolate(frame, [b - 5, b], [0, 1], {...clamp, easing: easeInOut});
  const over = interpolate(frame - a, [0, 5, 9], [0.86, 1.025, 1], clamp);
  const dx = enter === 'left' ? -1 : enter === 'right' ? 1 : 0;
  const dy = enter === 'up' ? 1 : 0;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        borderRadius: 30,
        overflow: 'hidden',
        background: light ? '#F7F5FA' : 'rgba(24,20,32,0.94)',
        border: light ? '1.5px solid rgba(0,0,0,0.08)' : '1.5px solid rgba(255,255,255,0.12)',
        boxShadow: `0 30px 70px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,0,0,0.3), 0 0 60px rgba(150,1,253,${0.18 * p})`,
        opacity: Math.min(p * 1.6, 1) * (1 - o),
        scale: String((enter === 'pop' ? over : 1) * (1 - o * 0.08)),
        translate: `${dx * (1 - p) * 700}px ${dy * (1 - p) * 300 + (enter === 'pop' ? (1 - p) * 30 : 0)}px`,
        filter: p < 1 && enter !== 'pop' ? `blur(${(1 - p) * 12}px)` : undefined,
        fontFamily: OUTFIT,
      }}
    >
      <div
        style={{
          height: 56,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '0 22px',
          background: light ? '#ECE8F2' : 'rgba(255,255,255,0.06)',
          borderBottom: light ? '1px solid rgba(0,0,0,0.08)' : '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <div style={{width: 18, height: 18, borderRadius: 9, background: '#B701FC'}} />
        <div style={{width: 18, height: 18, borderRadius: 9, background: '#9601FD', opacity: 0.75}} />
        <div style={{width: 18, height: 18, borderRadius: 9, background: '#7600FC', opacity: 0.5}} />
        <div style={{flex: 1, textAlign: 'center', marginRight: 80, fontSize: 24, fontWeight: 700, color: light ? '#3A3248' : 'rgba(255,255,255,0.75)'}}>{title}</div>
      </div>
      <div style={{position: 'relative', height: h - 56}}>{children}</div>
    </div>
  );
};

// ---------------------------------------------------------------- cursor
export const Cursor: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (!CURSOR_ON.some(([a, b]) => t >= a && t < b)) return null;
  const pts = CURSOR;
  let x = pts[0].x;
  let y = pts[0].y;
  for (let i = 0; i < pts.length - 1; i++) {
    const A = pts[i];
    const B = pts[i + 1];
    if (t >= A.t && t < B.t) {
      const q = interpolate(t, [A.t, B.t], [0, 1], {...clamp, easing: easeInOut});
      x = A.x + (B.x - A.x) * q;
      y = A.y + (B.y - A.y) * q;
      break;
    }
    if (t >= B.t) {
      x = B.x;
      y = B.y;
    }
  }
  let press = 1;
  let ring = 0;
  for (const p of pts.filter((q) => q.click)) {
    const l = frame - p.t * F;
    press = Math.min(press, interpolate(l, [0, 2, 6], [1, 0.82, 1], clamp));
    if (l >= 0 && l < 12) ring = l / 12;
  }
  const show = CURSOR_ON.find(([a, b]) => t >= a && t < b)!;
  const op = interpolate(t, [show[0], show[0] + 0.12, show[1] - 0.12, show[1]], [0, 1, 1, 0], clamp);
  return (
    <>
      {ring > 0 ? (
        <div style={{position: 'absolute', left: x - 40 * ring - 10, top: y - 40 * ring - 10, width: 20 + 80 * ring, height: 20 + 80 * ring, borderRadius: '50%', border: `4px solid rgba(183,1,252,${1 - ring})`}} />
      ) : null}
      <svg viewBox="0 0 24 24" style={{position: 'absolute', left: x - 8, top: y - 4, width: 76, height: 76, scale: String(press), transformOrigin: '10% 10%', opacity: op, filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.6))'}}>
        <path d="M5 2 L5 19 L9.5 15 L12.5 22 L15.5 20.8 L12.6 14 L18.5 14 Z" fill="#fff" stroke="#111" strokeWidth="1.3" strokeLinejoin="round" />
      </svg>
    </>
  );
};

// ---------------------------------------------------------------- pantalla de la persona
const lerp = (a: ScreenState, b: ScreenState, q: number): ScreenState => ({x: a.x + (b.x - a.x) * q, y: a.y + (b.y - a.y) * q, k: a.k + (b.k - a.k) * q});

export const screenAt = (frame: number): ScreenState => {
  let s = MODES[0].s;
  for (let i = 1; i < MODES.length; i++) {
    const m = MODES[i];
    const a = m.t * F - 4;
    if (frame < a) break;
    const q = interpolate(frame, [a, a + 8], [0, 1], {...clamp, easing: easeInOut});
    s = lerp(s, m.s, q);
  }
  return s;
};

/** La persona hablando, a pantalla completa o en ventana; se apaga como una TV vieja y se enciende con el desfibrilador. */
export const Pantalla: React.FC = () => {
  const frame = useCurrentFrame();
  const s = screenAt(frame);
  const win = interpolate(s.k, [0.6, 1], [1, 0], clamp);
  // apagado: se aplasta a una línea y luego a un punto; encendido: al revés
  const offA = interpolate(frame, [T.off * F, T.off * F + 5], [0, 1], {...clamp, easing: easeInOut});
  const offB = interpolate(frame, [T.off * F + 5, T.off * F + 9], [0, 1], {...clamp, easing: easeInOut});
  const onA = interpolate(frame, [T.on * F, T.on * F + 4], [0, 1], {...clamp, easing: easeOut});
  const onB = interpolate(frame, [T.on * F + 4, T.on * F + 9], [0, 1], {...clamp, easing: easeOut});
  const isOff = frame >= T.off * F && frame < T.on * F + 9;
  const sy = isOff ? (frame < T.on * F ? 1 - offA * 0.994 : 0.006 + onB * 0.994) : 1;
  const sx = isOff ? (frame < T.on * F ? 1 - offB : onA) : 1;
  const glow = isOff ? Math.max(offA * (1 - offB), onA * (1 - onB)) : 0;
  const end = frame >= SPEECH * F;
  return (
    <div
      style={{
        position: 'absolute',
        left: s.x,
        top: s.y,
        width: 1080 * s.k,
        height: 1920 * s.k,
        borderRadius: 44 * win,
        overflow: 'hidden',
        background: '#000',
        boxShadow: win > 0 ? `0 40px 90px rgba(0,0,0,${0.6 * win}), 0 0 0 ${2 * win}px rgba(255,255,255,0.18), 0 0 80px rgba(150,1,253,${0.35 * win})` : undefined,
        scale: `${sx} ${sy}`,
        filter: glow > 0 ? `brightness(${1 + glow * 3})` : undefined,
      }}
    >
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, transformOrigin: '0 0', scale: String(s.k)}}>
        <Live from={0} to={SPEECH} audio />
        {end ? <LastFrame /> : null}
      </div>
      {win > 0.01 ? (
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 0,
            height: 56,
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '0 22px',
            background: 'rgba(14,10,20,0.6)',
            backdropFilter: 'blur(8px)',
            opacity: win,
            fontFamily: OUTFIT,
          }}
        >
          <div style={{width: 18, height: 18, borderRadius: 9, background: '#B701FC'}} />
          <div style={{width: 18, height: 18, borderRadius: 9, background: '#9601FD', opacity: 0.75}} />
          <div style={{width: 18, height: 18, borderRadius: 9, background: '#7600FC', opacity: 0.5}} />
          <div style={{flex: 1, textAlign: 'center', marginRight: 70, fontSize: 22, fontWeight: 700, color: 'rgba(255,255,255,0.8)'}}>● En vivo</div>
        </div>
      ) : null}
    </div>
  );
};

/** Línea brillante que queda cuando la pantalla está apagada. */
export const PuntoApagado: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.off * F + 8 || frame >= T.on * F) return null;
  const s = screenAt(frame);
  const cx = s.x + 540 * s.k;
  const cy = s.y + 960 * s.k;
  const fade = interpolate(frame - (T.off * F + 8), [0, 10], [1, 0], clamp);
  return <div style={{position: 'absolute', left: cx - 10, top: cy - 10, width: 20, height: 20, borderRadius: 10, background: '#fff', boxShadow: '0 0 30px #fff, 0 0 60px #B701FC', opacity: fade}} />;
};

export {C};
