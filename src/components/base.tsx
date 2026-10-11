import React, {useId} from 'react';
import {C, FONT, cardGradient, cardShadow, softShadow} from '../theme';
import {E, prog, tw} from '../lib/anim';

export const Abs: React.FC<{style?: React.CSSProperties; children?: React.ReactNode}> = ({style, children}) => (
  <div style={{position: 'absolute', ...style}}>{children}</div>
);

/**
 * Desenfoque direccional (motion blur) con filtro SVG. La estructura del árbol es siempre la misma
 * para no re-montar hijos (imágenes, canvas 3D) cuando el blur cambia.
 */
export const DirBlur: React.FC<{x?: number; y?: number; style?: React.CSSProperties; children?: React.ReactNode}> = ({
  x = 0,
  y = 0,
  style,
  children,
}) => {
  const id = 'b' + useId().replace(/[^a-zA-Z0-9]/g, '');
  const bx = Math.min(Math.abs(x), 80);
  const by = Math.min(Math.abs(y), 80);
  const active = bx > 0.25 || by > 0.25;
  return (
    <div style={{position: 'absolute', inset: 0, filter: active ? `url(#${id})` : undefined, ...style}}>
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <filter id={id} x="-30%" y="-30%" width="160%" height="160%" colorInterpolationFilters="sRGB">
          <feGaussianBlur stdDeviation={`${bx.toFixed(2)} ${by.toFixed(2)}`} />
        </filter>
      </svg>
      {children}
    </div>
  );
};

export const textStyle = (size: number, color: string, weight = 800): React.CSSProperties => ({
  fontFamily: FONT,
  fontStyle: 'italic',
  fontWeight: weight,
  fontSize: size,
  color,
  letterSpacing: '-0.045em',
  lineHeight: 0.92,
  whiteSpace: 'nowrap',
});

/** Palabra con entrada blur-in (estilo.md §2): 7 frames, blur 12→0, x +24→0, escala .94→1. */
export const Word: React.FC<{
  f: number;
  at: number;
  size: number;
  color?: string;
  weight?: number;
  dur?: number;
  dx?: number;
  dy?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({f, at, size, color = C.text, weight = 800, dur = 7, dx = 24, dy = 0, style, children}) => {
  const p = prog(f, at, dur);
  const e = E.expoOut(p);
  if (f < at) return <span style={{...textStyle(size, color, weight), display: 'inline-block', opacity: 0, ...style}}>{children}</span>;
  return (
    <span
      style={{
        ...textStyle(size, color, weight),
        display: 'inline-block',
        opacity: Math.min(1, p * 2.2),
        filter: e < 0.995 ? `blur(${(1 - e) * 12}px)` : undefined,
        transform: `translate(${(1 - e) * dx}px, ${(1 - e) * dy}px) scale(${0.94 + 0.06 * e})`,
        transformOrigin: 'left bottom',
        ...style,
      }}
    >
      {children}
    </span>
  );
};

/** Línea de varias palabras con tiempos individuales. */
export const Words: React.FC<{
  f: number;
  items: [string, number][];
  size: number;
  color?: string;
  gap?: number;
  weight?: number;
  style?: React.CSSProperties;
}> = ({f, items, size, color, gap = 0.22, weight, style}) => (
  <div style={{display: 'flex', alignItems: 'baseline', gap: size * gap, ...style}}>
    {items.map(([w, at], i) => (
      <Word key={i} f={f} at={at} size={size} color={color} weight={weight}>
        {w}
      </Word>
    ))}
  </div>
);

/** Tarjeta morada con degradado, brillo especular que barre y sombra suave. */
export const Card: React.FC<{
  w: number;
  h: number;
  r?: number;
  f?: number;
  sheenAt?: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  background?: string;
  shadow?: string;
}> = ({w, h, r = 30, f = 0, sheenAt = -100, style, children, background = cardGradient, shadow = cardShadow}) => {
  const sheen = tw(f, sheenAt, 26, -60, 160, E.cubicInOut);
  return (
    <div
      style={{
        position: 'absolute',
        width: w,
        height: h,
        borderRadius: r,
        background,
        boxShadow: shadow,
        overflow: 'hidden',
        ...style,
      }}
    >
      {children}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(115deg, transparent ${sheen - 14}%, rgba(255,255,255,0.13) ${sheen}%, transparent ${sheen + 14}%)`,
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};

/**
 * Píldora destacada: nace como cápsula vertical, se expande en horizontal con overshoot suave y escribe el texto.
 */
export const Pill: React.FC<{
  f: number;
  at: number;
  text: string;
  size: number;
  padX?: number;
  padY?: number;
  style?: React.CSSProperties;
  color?: string;
  textColor?: string;
}> = ({f, at, text, size, padX, padY, style, color, textColor = C.white}) => {
  const px = padX ?? size * 0.42;
  const py = padY ?? size * 0.2;
  const appear = E.expoOut(prog(f, at, 4));
  const grow = E.softBack(prog(f, at + 2, 8));
  const txt = E.expoOut(prog(f, at + 4, 7));
  if (f < at) return <div style={{position: 'absolute', ...style, opacity: 0}} />;
  return (
    <div style={{position: 'absolute', ...style}}>
      <div
        style={{
          position: 'relative',
          display: 'inline-flex',
          padding: `${py}px ${px}px`,
          borderRadius: 999,
          background: color ?? `linear-gradient(120deg, ${C.cardHi}, ${C.cardDark} 55%, ${C.card})`,
          boxShadow: softShadow,
          transform: `scaleX(${0.06 + 0.94 * grow}) scaleY(${0.5 + 0.5 * appear})`,
          opacity: appear,
          overflow: 'hidden',
        }}
      >
        <span
          style={{
            ...textStyle(size, textColor),
            opacity: txt,
            filter: txt < 0.99 ? `blur(${(1 - txt) * 10}px)` : undefined,
            transform: `translateX(${(1 - txt) * 30}px)`,
            display: 'inline-block',
            paddingRight: size * 0.06,
          }}
        >
          {text}
        </span>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: `linear-gradient(110deg, transparent ${tw(f, at + 6, 18, -30, 150, E.cubicInOut) - 12}%, rgba(255,255,255,0.18) ${tw(f, at + 6, 18, -30, 150, E.cubicInOut)}%, transparent ${tw(f, at + 6, 18, -30, 150, E.cubicInOut) + 12}%)`,
          }}
        />
      </div>
    </div>
  );
};

/** Etiqueta blanca pequeña (UI) con sombra suave. */
export const Chip: React.FC<{f: number; at: number; style?: React.CSSProperties; children: React.ReactNode; dark?: boolean}> = ({
  f,
  at,
  style,
  children,
  dark,
}) => {
  const s = E.softBack(prog(f, at, 9));
  const o = prog(f, at, 4);
  return (
    <div
      style={{
        position: 'absolute',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '14px 22px',
        borderRadius: 18,
        background: dark ? C.cardDark : C.white,
        boxShadow: softShadow,
        transform: `scale(${s})`,
        opacity: o,
        ...textStyle(30, dark ? C.white : C.text, 700),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Línea punteada que se dibuja entre dos puntos (conector). */
export const DashLine: React.FC<{
  f: number;
  at: number;
  dur?: number;
  d: string;
  len: number;
  color?: string;
  width?: number;
  dash?: string;
}> = ({f, at, dur = 10, d, len, color = C.text, width = 3.5, dash = '12 10'}) => {
  const p = E.quintOut(prog(f, at, dur));
  const id = 'm' + useId().replace(/[^a-zA-Z0-9]/g, '');
  return (
    <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1} height={1}>
      <defs>
        <mask id={id} maskUnits="userSpaceOnUse" x={-3000} y={-3000} width={6000} height={6000}>
          <path d={d} stroke="#fff" strokeWidth={width + 6} fill="none" strokeDasharray={`${len}`} strokeDashoffset={len * (1 - p)} />
        </mask>
      </defs>
      <path d={d} stroke={color} strokeWidth={width} fill="none" strokeDasharray={dash} strokeLinecap="round" mask={`url(#${id})`} opacity={0.85} />
    </svg>
  );
};
