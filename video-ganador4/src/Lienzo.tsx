import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS, P, SANS, clamp, easeOut} from './base';
import {T} from './data';

// Lienzo del referente (estilo.md §4.2): el vídeo se encoge 1 → 0,74 en 0,45 s a una tarjeta sobre papel cuadriculado
// lavanda, con etiquetas verticales y marcas ▲. Aquí, además, las publicaciones desordenadas del problema nº 1.

const L = T.lienzo;
export const enLienzo = (t: number) => t >= L.from && t < L.to;
export const cardK = (t: number) => (enLienzo(t) ? interpolate(t, [L.from, L.from + 0.45], [1, 0.74], {...clamp, easing: easeOut}) : 1);

/** Envuelve a la persona: tarjeta redondeada con borde y halo morado claro. */
export const Tarjeta: React.FC<{children: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const k = cardK(t);
  if (k === 1) return <>{children}</>;
  return (
    <AbsoluteFill
      style={{
        transform: `scale(${k})`,
        transformOrigin: '540px 960px',
        borderRadius: 34 / k,
        overflow: 'hidden',
        boxShadow: `0 0 0 ${7 / k}px #E2C7FF, 0 0 ${46 / k}px ${12 / k}px rgba(183,1,252,0.45), 0 ${30 / k}px ${60 / k}px rgba(40,0,80,0.35)`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

const vertical = (text: string, x: number, y: number, rot: number): React.ReactNode => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      transform: `rotate(${rot}deg)`,
      transformOrigin: '0 0',
      fontFamily: SANS,
      fontWeight: 600,
      fontSize: 17,
      letterSpacing: '0.22em',
      color: P.ink,
      whiteSpace: 'nowrap',
    }}
  >
    {text}
  </div>
);

export const LienzoFondo: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!enLienzo(t)) return null;
  return (
    <AbsoluteFill
      style={{
        background: P.lav,
        backgroundImage: `linear-gradient(${P.grid} 1.5px, transparent 1.5px), linear-gradient(90deg, ${P.grid} 1.5px, transparent 1.5px)`,
        backgroundSize: '48px 48px',
        backgroundPosition: '12px 0',
      }}
    >
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 70% 60% at 50% 50%, rgba(255,255,255,0.35) 0%, transparent 70%)'}} />
    </AbsoluteFill>
  );
};

// publicaciones que no combinan entre sí (problema nº 1: perfil desordenado)
type Pieza = {x: number; y: number; w: number; rot: number; img?: string; txt?: string; bg?: string; fg?: string; font?: string};
const PIEZAS: Pieza[] = [
  {x: -30, y: 70, w: 250, rot: -12, img: 'img/post_03.jpg'},
  {x: 830, y: 40, w: 240, rot: 9, txt: '¡¡OFERTA!!', bg: '#FFE600', fg: '#E10600', font: 'Impact, Arial Black, sans-serif'},
  {x: -70, y: 720, w: 230, rot: 7, img: 'img/post_08.jpg'},
  {x: 905, y: 610, w: 220, rot: -10, txt: 'Feliz lunes ☀️', bg: '#FF8FC7', fg: '#1A1AFF', font: 'Georgia, serif'},
  {x: 30, y: 1660, w: 250, rot: 10, img: 'img/post_11.jpg'},
  {x: 790, y: 1650, w: 260, rot: -7, txt: '2x1 SOLO HOY', bg: '#18C964', fg: '#FFFFFF', font: 'Arial Black, sans-serif'},
  {x: -45, y: 1210, w: 210, rot: -6, img: 'img/post_05.jpg'},
  {x: 935, y: 1150, w: 205, rot: 12, img: 'img/post_09.jpg'},
];

export const LienzoFrente: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (!enLienzo(t)) return null;
  const k = cardK(t);
  const ent = interpolate(t, [L.from, L.from + 0.45], [0, 1], clamp);
  // número del problema (01 · 02 · 03)
  const n = L.numeros.filter((a) => t >= a - 0.06).length;
  const ultimo = L.numeros[Math.max(0, n - 1)];
  const pn = interpolate(t, [ultimo - 0.06, ultimo + 0.18], [0, 1], {...clamp, easing: easeOut});
  const top = 960 - 960 * k;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {/* etiquetas y marcas de registro */}
      <div style={{opacity: ent}}>
        {vertical('GROW MARKETING · AUDITORÍA DE PERFIL', 60, 1500, -90)}
        {vertical('REDES SOCIALES · 3 PROBLEMAS', 1022, 420, 90)}
        {[
          [140, top - 26],
          [925, top - 26],
          [140, 1920 - top + 8],
          [925, 1920 - top + 8],
        ].map(([x, y], i) => (
          <div key={i} style={{position: 'absolute', left: x, top: y, fontSize: 16, color: P.ink, fontFamily: SANS}}>
            ▲
          </div>
        ))}
        <div style={{position: 'absolute', left: 120, top: 1880, fontFamily: SANS, fontSize: 16, color: P.ink, letterSpacing: '0.2em'}}>22</div>
        <div style={{position: 'absolute', left: 940, top: 1880, fontFamily: SANS, fontSize: 16, color: P.ink, letterSpacing: '0.2em'}}>11</div>
      </div>
      {/* número del problema arriba, sobre la tarjeta */}
      {n > 0 ? (
        <div style={{position: 'absolute', left: 0, right: 0, top: 96, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
          <div style={{fontFamily: SANS, fontWeight: 600, fontSize: 22, letterSpacing: '0.35em', color: P.ink}}>PROBLEMA</div>
          <div
            style={{
              fontFamily: SANS,
              fontWeight: 800,
              fontSize: 118,
              lineHeight: 1,
              letterSpacing: '-0.04em',
              color: P.purple,
              textShadow: '0 0 24px rgba(183,1,252,0.35)',
              opacity: pn,
              filter: `blur(${(1 - pn) * 10}px)`,
              transform: `translateY(${(1 - pn) * 14}px)`,
            }}
          >
            {`0${n}`}
          </div>
        </div>
      ) : null}
      {/* publicaciones desordenadas */}
      {PIEZAS.map((p, i) => {
        const a = L.desorden - 0.04 + i * 0.045;
        const q = interpolate(t, [a, a + 0.32], [0, 1], {...clamp, easing: easeOut});
        if (q <= 0) return null;
        const desde = p.x < 540 ? -420 : 420;
        const jit = Math.sin((t - a) * 5 + i) * 2.2;
        const salida = interpolate(t, [L.to - 0.12, L.to], [0, 1], clamp);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: p.x + desde * (1 - q),
              top: p.y,
              width: p.w,
              height: p.w,
              background: '#FFFFFF',
              padding: 7,
              boxShadow: '0 16px 30px rgba(30,0,60,0.35)',
              transform: `rotate(${p.rot + jit + (1 - q) * 30}deg) scale(${1 - salida * 0.1})`,
              opacity: q * (1 - salida),
            }}
          >
            {p.img ? (
              <Img src={staticFile(p.img)} style={{width: '100%', height: '100%', objectFit: 'cover', filter: i % 2 ? 'saturate(1.8) hue-rotate(25deg)' : 'sepia(0.6) contrast(1.2)'}} />
            ) : (
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  background: p.bg,
                  color: p.fg,
                  fontFamily: p.font,
                  fontSize: p.w * 0.17,
                  fontWeight: 900,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center',
                  lineHeight: 1.05,
                  padding: 10,
                }}
              >
                {p.txt}
              </div>
            )}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Transición de rayas verticales (estilo.md §5): 6 fotogramas. */
export const Rayas: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const k = Math.round((t - at) * FPS);
  if (k < -3 || k > 3) return null;
  const op = [0.55, 0.85, 1, 1, 0.85, 0.6, 0.3][k + 3];
  return (
    <AbsoluteFill
      style={{
        backgroundImage: 'repeating-linear-gradient(90deg, #0A0A0A 0px, #0A0A0A 5px, #F2F2F7 5px, #F2F2F7 10px)',
        backgroundPosition: `${k * 7}px 0`,
        opacity: op,
        mixBlendMode: k < 0 ? 'normal' : 'hard-light',
      }}
    />
  );
};
