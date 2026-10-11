import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, FONT} from '../theme';
import {E, prog, rand, tw} from '../lib/anim';
import {textStyle} from './base';

const mono: React.CSSProperties = {fontFamily: FONT, fontStyle: 'normal', fontWeight: 600, letterSpacing: '0.02em'};

/* ------------------------------------------------------------------ iconos */
export const IconPlay: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d="M7 4.5v15a1 1 0 0 0 1.5.86l12.5-7.5a1 1 0 0 0 0-1.72L8.5 3.64A1 1 0 0 0 7 4.5z" fill={color} />
  </svg>
);
export const IconHeart: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 4.5 6.8 4.5c2.1 0 3.6 1.2 5.2 3 1.6-1.8 3.1-3 5.2-3 3.8 0 5.9 3.9 4.4 7.3C19.5 16.4 12 21 12 21z" fill={color} />
  </svg>
);
export const IconChat: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d="M12 3C6.5 3 2 6.9 2 11.6c0 2.5 1.3 4.8 3.4 6.4L4.5 21.5l4.3-2.2c1 .3 2.1.4 3.2.4 5.5 0 10-3.9 10-8.6S17.5 3 12 3z" fill={color} />
  </svg>
);
export const IconShare: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d="M13 4l9 8-9 8v-5c-6 0-9.5 1.8-11 6 .6-6.4 4-10.6 11-11.5V4z" fill={color} />
  </svg>
);
export const IconEye: React.FC<{size: number; color?: string}> = ({size, color = C.text}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d="M12 5C6.5 5 2.4 9.1 1 12c1.4 2.9 5.5 7 11 7s9.6-4.1 11-7c-1.4-2.9-5.5-7-11-7z" fill={color} />
    <circle cx={12} cy={12} r={3.6} fill={C.white} />
    <circle cx={12} cy={12} r={1.8} fill={color} />
  </svg>
);
export const IconCursor: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{filter: 'drop-shadow(0 4px 6px rgba(0,0,0,.3))'}}>
    <path d="M4 2.5l15.5 11.2-7 .8 4 7.6-3 1.5-4-7.7-5.5 4.6z" fill={C.black} stroke={C.white} strokeWidth={1.4} strokeLinejoin="round" />
  </svg>
);
export const IconArrowUp: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d="M12 3l8 8h-5v10H9V11H4z" fill={color} />
  </svg>
);
export const IconSend: React.FC<{size: number; color?: string}> = ({size, color = C.white}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d="M2.5 11.2L21 3l-6.8 18.5-3.1-7.6z" fill={color} />
  </svg>
);

/* ------------------------------------------------------------- forma de onda */
export const Waveform: React.FC<{
  f: number;
  bars: number;
  w: number;
  h: number;
  color?: string;
  seed?: number;
  speed?: number;
  barW?: number;
  live?: boolean;
}> = ({f, bars, w, h, color = C.white, seed = 1, speed = 1, barW, live = true}) => {
  const bw = barW ?? (w / bars) * 0.55;
  return (
    <svg width={w} height={h} style={{display: 'block'}}>
      {Array.from({length: bars}).map((_, i) => {
        const base = 0.25 + 0.75 * Math.abs(Math.sin(i * 0.55 + seed) * Math.cos(i * 0.21 + seed * 2));
        const mod = live ? 0.55 + 0.45 * Math.abs(Math.sin(f * 0.35 * speed + i * 0.9 + seed)) : 1;
        const bh = Math.max(4, h * base * mod);
        const x = (i + 0.5) * (w / bars) - bw / 2;
        return <rect key={i} x={x} y={(h - bh) / 2} width={bw} height={bh} rx={bw / 2} fill={color} />;
      })}
    </svg>
  );
};

/* ------------------------------------------------------- interfaz de timeline */
export type Clip = {track: number; x: number; w: number; color: string; label?: string; audio?: boolean};

export const TimelineUI: React.FC<{
  f: number;
  w: number;
  h: number;
  clips: Clip[];
  playhead: number; // 0..1
  previewImg: string;
  previewZoom?: number;
  previewFilter?: string;
  cutFlash?: {x: number; at: number}[];
  timecode: string;
}> = ({f, w, h, clips, playhead, previewImg, previewZoom = 1, previewFilter, cutFlash = [], timecode}) => {
  const top = 40;
  const previewH = h * 0.5;
  const tlTop = top + previewH + 14;
  const trackH = (h - tlTop - 34) / 4;
  const labelW = 64;
  const tlW = w - labelW - 16;
  const trackNames = ['V2', 'V1', 'A1', 'A2'];
  return (
    <div style={{position: 'absolute', inset: 0, background: C.screen, borderRadius: 16, overflow: 'hidden'}}>
      {/* barra superior */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: top, background: '#24162B', display: 'flex', alignItems: 'center', gap: 9, padding: '0 16px'}}>
        {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
          <div key={c} style={{width: 12, height: 12, borderRadius: 6, background: c, opacity: 0.85}} />
        ))}
        <div style={{...mono, fontSize: 17, color: '#B9A6C0', marginLeft: 14}}>Secuencia_01 · 1080×1920 · 30 fps</div>
        <div style={{...mono, fontSize: 17, color: C.white, marginLeft: 'auto'}}>{timecode}</div>
      </div>
      {/* visor */}
      <div style={{position: 'absolute', left: 16, top: top + 12, width: w * 0.6 - 24, height: previewH - 12, borderRadius: 10, overflow: 'hidden', background: '#000'}}>
        <Img
          src={staticFile(previewImg)}
          style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${previewZoom})`, filter: previewFilter}}
        />
      </div>
      {/* panel de efectos con keyframes */}
      <div style={{position: 'absolute', left: w * 0.6 + 4, top: top + 12, width: w * 0.4 - 20, height: previewH - 12, borderRadius: 10, background: '#24162B', padding: 16}}>
        <div style={{...mono, fontSize: 16, color: '#B9A6C0', marginBottom: 14}}>Controles de efecto</div>
        {['Escala', 'Posición', 'Rotación', 'Opacidad', 'Desenfoque'].map((n, i) => {
          const v = 0.3 + 0.6 * Math.abs(Math.sin(f * 0.05 + i * 1.3));
          return (
            <div key={n} style={{display: 'flex', alignItems: 'center', gap: 10, marginBottom: 15}}>
              <div style={{...mono, fontSize: 14, color: '#E7DDEA', width: 86}}>{n}</div>
              <div style={{flex: 1, height: 6, borderRadius: 3, background: '#3A2843', position: 'relative'}}>
                <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${v * 100}%`, borderRadius: 3, background: C.cardLight}} />
              </div>
              <div style={{width: 11, height: 11, transform: 'rotate(45deg)', background: i % 2 ? '#C9A8D4' : C.white}} />
            </div>
          );
        })}
      </div>
      {/* regla */}
      <div style={{position: 'absolute', left: labelW, top: tlTop, width: tlW, height: 24}}>
        {Array.from({length: 25}).map((_, i) => (
          <div key={i} style={{position: 'absolute', left: (i / 24) * tlW, top: i % 4 === 0 ? 4 : 12, width: 2, height: i % 4 === 0 ? 18 : 10, background: '#5B4863'}} />
        ))}
      </div>
      {/* pistas */}
      {trackNames.map((n, i) => (
        <div key={n} style={{position: 'absolute', left: 0, top: tlTop + 28 + i * trackH, width: w, height: trackH - 6}}>
          <div style={{...mono, position: 'absolute', left: 14, top: (trackH - 6) / 2 - 10, fontSize: 16, color: '#B9A6C0'}}>{n}</div>
          <div style={{position: 'absolute', left: labelW, right: 16, top: 0, bottom: 0, background: '#22162A', borderRadius: 6}} />
        </div>
      ))}
      {clips.map((c, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: labelW + c.x * tlW,
            top: tlTop + 28 + c.track * trackH + 3,
            width: Math.max(0, c.w * tlW - 4),
            height: trackH - 12,
            borderRadius: 7,
            background: c.color,
            overflow: 'hidden',
            boxShadow: 'inset 0 0 0 1.5px rgba(255,255,255,0.18)',
          }}
        >
          {c.audio ? (
            <div style={{position: 'absolute', inset: '4px 6px'}}>
              <Waveform f={f} bars={Math.max(4, Math.round(c.w * 60))} w={Math.max(10, c.w * tlW - 16)} h={trackH - 20} color="rgba(255,255,255,0.75)" seed={i * 3} live={false} />
            </div>
          ) : (
            <div style={{...mono, fontSize: 14, color: 'rgba(255,255,255,0.9)', padding: '6px 9px'}}>{c.label}</div>
          )}
        </div>
      ))}
      {/* flashes de corte (cuchilla) */}
      {cutFlash.map((c, i) => {
        const o = f >= c.at ? 1 - prog(f, c.at, 10) : 0;
        return o > 0 ? (
          <div key={i} style={{position: 'absolute', left: labelW + c.x * tlW - 2, top: tlTop + 22, width: 4, height: trackH * 4 + 8, background: C.white, opacity: o, boxShadow: `0 0 ${18 * o}px ${C.white}`}} />
        ) : null;
      })}
      {/* cabezal */}
      <div style={{position: 'absolute', left: labelW + playhead * tlW - 1, top: tlTop, width: 3, height: h - tlTop - 8, background: '#FF4D6D'}}>
        <div style={{position: 'absolute', left: -9, top: -2, width: 21, height: 16, borderRadius: 4, background: '#FF4D6D'}} />
      </div>
    </div>
  );
};

/* ------------------------------------------------------------ editor de curvas */
export const GraphEditor: React.FC<{f: number; at: number; w: number; h: number}> = ({f, at, w, h}) => {
  const p = E.quintOut(prog(f, at + 2, 20));
  const gx = 70;
  const gy = 80;
  const gw = w - 110;
  const gh = h - 150;
  // curva de velocidad tipo "ease" (pico rápido y desaceleración larga)
  const path = `M ${gx} ${gy + gh} C ${gx + gw * 0.12} ${gy + gh} ${gx + gw * 0.18} ${gy} ${gx + gw * 0.36} ${gy} S ${gx + gw * 0.8} ${gy + gh} ${gx + gw} ${gy + gh}`;
  const valuePath = `M ${gx} ${gy + gh * 0.95} C ${gx + gw * 0.25} ${gy + gh * 0.95} ${gx + gw * 0.3} ${gy + gh * 0.1} ${gx + gw} ${gy + gh * 0.08}`;
  const len = gw * 2.1;
  const ball = E.expoOut(prog(f, at + 6, 22));
  const kf = [
    {x: gx, y: gy + gh, t: at + 3},
    {x: gx + gw * 0.36, y: gy, t: at + 9},
    {x: gx + gw, y: gy + gh, t: at + 15},
  ];
  return (
    <div style={{position: 'absolute', inset: 0, background: C.screen, borderRadius: 16, overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 40, background: '#24162B', display: 'flex', alignItems: 'center', padding: '0 18px', gap: 14}}>
        <div style={{...mono, fontSize: 17, color: C.white}}>Editor de gráficos</div>
        <div style={{...mono, fontSize: 15, color: '#B9A6C0'}}>Velocidad · Posición</div>
        <div style={{...mono, fontSize: 15, color: '#B9A6C0', marginLeft: 'auto'}}>Influencia 85 %</div>
      </div>
      <svg width={w} height={h} style={{position: 'absolute', left: 0, top: 0}}>
        {Array.from({length: 9}).map((_, i) => (
          <line key={'v' + i} x1={gx + (i / 8) * gw} y1={gy - 10} x2={gx + (i / 8) * gw} y2={gy + gh} stroke="#2E2036" strokeWidth={2} />
        ))}
        {Array.from({length: 5}).map((_, i) => (
          <line key={'h' + i} x1={gx} y1={gy + (i / 4) * gh} x2={gx + gw} y2={gy + (i / 4) * gh} stroke="#2E2036" strokeWidth={2} />
        ))}
        <path d={valuePath} stroke="#6E5A78" strokeWidth={4} fill="none" strokeDasharray="10 9" opacity={p} />
        <path d={path} stroke="#C9A8D4" strokeWidth={6} fill="none" strokeDasharray={len} strokeDashoffset={len * (1 - p)} strokeLinecap="round" />
        {/* manejadores bezier */}
        {f > at + 9 && (
          <g opacity={prog(f, at + 9, 5)}>
            <line x1={gx + gw * 0.18} y1={gy} x2={gx + gw * 0.54} y2={gy} stroke={C.white} strokeWidth={2.5} />
            <circle cx={gx + gw * 0.18} cy={gy} r={8} fill={C.screen} stroke={C.white} strokeWidth={2.5} />
            <circle cx={gx + gw * 0.54} cy={gy} r={8} fill={C.screen} stroke={C.white} strokeWidth={2.5} />
          </g>
        )}
        {kf.map((k, i) => {
          const s = E.softBack(prog(f, k.t, 8));
          return <rect key={i} x={-11} y={-11} width={22} height={22} fill={i === 1 ? C.white : '#C9A8D4'} transform={`translate(${k.x} ${k.y}) rotate(45) scale(${s})`} />;
        })}
      </svg>
      {/* objeto animado con estela */}
      {[0.12, 0.08, 0.04, 0].map((d, i) => {
        const bp = Math.max(0, ball - d * (1 - ball) * 4);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: gx + bp * (gw - 70),
              top: h - 58,
              width: 46,
              height: 30,
              borderRadius: 10,
              background: C.cardLight,
              opacity: i === 3 ? 1 : 0.18 + i * 0.1,
            }}
          />
        );
      })}
    </div>
  );
};

/* -------------------------------------------------------- ruedas de color */
export const ColorWheel: React.FC<{f: number; at: number; size: number; label: string; puck: [number, number]}> = ({f, at, size, label, puck}) => {
  const s = E.softBack(prog(f, at, 10));
  const pm = E.expoOut(prog(f, at + 6, 18));
  const px = puck[0] * pm * size * 0.3;
  const py = puck[1] * pm * size * 0.3;
  return (
    <div style={{position: 'relative', width: size, transform: `scale(${s})`, opacity: prog(f, at, 4)}}>
      <div
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          background: 'conic-gradient(from 90deg, #ff4d4d, #ffd84d, #4dff88, #4de1ff, #5d4dff, #e14dff, #ff4d4d)',
          boxShadow: '0 10px 26px rgba(20,8,26,0.25)',
          position: 'relative',
        }}
      >
        <div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: 'radial-gradient(circle, rgba(240,240,240,1) 0%, rgba(240,240,240,0.85) 30%, rgba(240,240,240,0) 72%)'}} />
        <div style={{position: 'absolute', inset: size * 0.06, borderRadius: '50%', border: '2px solid rgba(22,22,22,0.12)'}} />
        <div
          style={{
            position: 'absolute',
            left: size / 2 - 11 + px,
            top: size / 2 - 11 + py,
            width: 22,
            height: 22,
            borderRadius: 11,
            border: `4px solid ${C.white}`,
            background: C.black,
            boxShadow: '0 2px 6px rgba(0,0,0,0.4)',
          }}
        />
      </div>
      <div style={{...textStyle(26, C.text, 700), textAlign: 'center', marginTop: 12}}>{label}</div>
    </div>
  );
};

/* -------------------------------------------------------- teléfono vertical */
export const Phone: React.FC<{w: number; h: number; style?: React.CSSProperties; children?: React.ReactNode}> = ({w, h, style, children}) => (
  <div
    style={{
      position: 'absolute',
      width: w,
      height: h,
      borderRadius: w * 0.14,
      background: C.black,
      boxShadow: '0 30px 70px rgba(20,8,26,0.35), 0 8px 16px rgba(20,8,26,0.2), inset 0 0 0 3px #3a3a3e',
      ...style,
    }}
  >
    <div style={{position: 'absolute', inset: 14, borderRadius: w * 0.115, overflow: 'hidden', background: '#000'}}>{children}</div>
    <div style={{position: 'absolute', left: w / 2 - 55, top: 26, width: 110, height: 30, borderRadius: 15, background: C.black}} />
  </div>
);

/* ----------------------------------------- partículas: corazones que suben */
export const Hearts: React.FC<{f: number; at: number; n?: number; x: number; y: number}> = ({f, at, n = 7, x, y}) => (
  <>
    {Array.from({length: n}).map((_, i) => {
      const t0 = at + i * 3;
      const p = prog(f, t0, 30);
      if (p <= 0 || p >= 1) return null;
      const dx = (rand(i + 3) - 0.5) * 120 + Math.sin(p * 6 + i) * 18;
      const dy = -E.quintOut(p) * (260 + rand(i) * 160);
      const s = 0.6 + rand(i + 9) * 0.7;
      return (
        <div key={i} style={{position: 'absolute', left: x + dx, top: y + dy, opacity: 1 - p, transform: `scale(${s * tw(f, t0, 8, 0.2, 1, E.softBack)})`}}>
          <IconHeart size={52} color={i % 3 === 0 ? '#FF4D6D' : C.white} />
        </div>
      );
    })}
  </>
);
