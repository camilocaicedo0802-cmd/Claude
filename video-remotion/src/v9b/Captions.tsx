import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOut} from '../engine/helpers';
import {C, OUTFIT} from '../v1/theme';
import {WORDS} from '../v9/timeline';
import {CHUNKS} from './chunks';
import {DISPLAY, KEY, NO_CAPS, capY} from './data';

// ------------------------------------------------------------------
// Subtítulo cinético (estilo.md §10.7):
// - tipografía de la primera versión: Outfit Black 900 en MAYÚSCULAS, 84 px (clave 96 px);
// - letras BLANCAS LISAS: sin cromado, sin degradado, sin contorno interior ni brillo;
//   solo una sombra suave detrás para que se lea sobre cualquier fondo;
// - la palabra clave va dentro del recuadro morado del logo (que se despliega al entrar);
// - animación de la referencia: cada palabra entra «fantasma» al pronunciarla
//   (5 fotogramas, desenfoque 16→0, escala 1,08→1, desplazamiento lateral) con 2 estelas;
//   deriva 1→1,04, flotación ±5 px y salida con destello en 4 fotogramas;
// - whoosh corto en cada palabra clave que entra (data.ts).
// ------------------------------------------------------------------

const clean = (i: number) => (DISPLAY[i] ?? WORDS[i].text.replace(/[,.]/g, '')).toUpperCase();

const TEXT: React.CSSProperties = {color: '#FFFFFF', textShadow: '0 4px 14px rgba(0,0,0,0.5)'};

const CapWord: React.FC<{i: number; dir: number}> = ({i, dir}) => {
  const frame = useCurrentFrame();
  const local = frame - WORDS[i].s * 30;
  const key = KEY.has(i);
  const text = clean(i);
  const p = interpolate(local, [0, 5], [0, 1], {...clamp, easing: easeOut});
  const ghost = (k: number, op: number) => {
    const q = interpolate(local, [0, 5 + k * 2], [0, 1], {...clamp, easing: easeOut});
    if (q >= 1 || local < 0) return null;
    return (
      <span
        aria-hidden
        style={{
          ...TEXT,
          position: 'absolute',
          left: key ? 18 : 0,
          top: 0,
          opacity: op * q * (1 - q) * 4,
          translate: `${dir * (1 - q) * (40 + k * 30)}px ${(1 - q) * 10}px`,
          filter: `blur(${6 + k * 4}px)`,
        }}
      >
        {text}
      </span>
    );
  };
  return (
    <span style={{position: 'relative', display: 'inline-block', fontSize: key ? 96 : 84, padding: key ? '0 18px 6px' : 0}}>
      {key ? (
        <span
          style={{
            position: 'absolute',
            inset: '4px 0 0',
            borderRadius: 16,
            background: C.purpleGrad,
            boxShadow: `0 6px 0 ${C.purpleShadow}, 0 0 30px ${C.purpleGlow}`,
            scale: `${interpolate(local, [0, 4], [0, 1], {...clamp, easing: easeOut})} 1`,
            transformOrigin: '0 50%',
            rotate: '-2deg',
          }}
        />
      ) : null}
      {ghost(1, 0.45)}
      {ghost(2, 0.25)}
      <span
        style={{
          ...TEXT,
          position: 'relative',
          display: 'inline-block',
          opacity: p,
          scale: String(interpolate(p, [0, 1], [1.08, 1])),
          translate: `${dir * (1 - p) * 26}px ${(1 - p) * 14}px`,
          filter: p < 1 ? `blur(${16 * (1 - p)}px)` : undefined,
        }}
      >
        {text}
      </span>
    </span>
  );
};

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  if (NO_CAPS.some(([a, b]) => t >= a && t < b)) return null;
  const k = CHUNKS.findIndex((x) => t >= x.s && t < x.e);
  if (k < 0) return null;
  const c = CHUNKS[k];
  const startF = c.s * 30;
  const endF = c.e * 30;
  const exit = interpolate(frame, [endF - 4, endF], [0, 1], {...clamp, easing: easeInOut});
  const drift = interpolate(frame, [startF, endF], [1, 1.04], clamp);
  const float = Math.sin((frame - startF) / 14) * 5;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 50,
          right: 50,
          top: capY(t) + float,
          translate: '0 -50%',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '0 22px',
          rotate: `${k % 2 ? 1.5 : -1.5}deg`,
          fontFamily: OUTFIT,
          fontWeight: 900,
          letterSpacing: '-0.03em',
          lineHeight: 1.05,
          scale: String(drift * (1 + exit * 0.06)),
          opacity: 1 - exit,
          filter: exit > 0 ? `blur(${12 * exit}px) brightness(${1 + 1.4 * exit})` : undefined,
        }}
      >
        {c.idx.map((i, j) => (
          <CapWord key={i} i={i} dir={j % 2 ? 1 : -1} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
