import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOut} from '../engine/helpers';
import {OUTFIT} from '../v1/theme';
import {CHUNKS} from './chunks';
import {KEY, T} from './data';
import {WORDS} from './timeline';

// ------------------------------------------------------------------
// Subtítulo de la propuesta C (estilo.md §10.8):
// - se mantienen la píldora oscura, el BLANCO LISO y el MORADO LISO de las palabras clave;
// - animaciones de la referencia: cada palabra entra «fantasma» al pronunciarla
//   (5 fotogramas: desenfoque 16→0, escala 1,08→1, desplazamiento lateral 26 px)
//   con 2 copias-estela; la frase flota (±5 px) y crece 1→1,04; sale con destello;
// - el hueco de cada palabra queda marcado en gris muy tenue hasta que se dice (karaoke);
// - whoosh corto en cada palabra clave que entra (data.ts).
// ------------------------------------------------------------------

const clean = (i: number) => WORDS[i].text.replace(/[,.]/g, '').toUpperCase();

const CapWord: React.FC<{i: number; dir: number}> = ({i, dir}) => {
  const frame = useCurrentFrame();
  const local = frame - WORDS[i].s * 30;
  const color = KEY.has(i) ? '#C46BFF' : '#FFFFFF';
  const text = clean(i);
  const p = interpolate(local, [0, 5], [0, 1], {...clamp, easing: easeOut});
  const ghost = (k: number, op: number) => {
    const q = interpolate(local, [0, 5 + k * 2], [0, 1], {...clamp, easing: easeOut});
    if (q >= 1 || local < 0) return null;
    return (
      <span
        aria-hidden
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          color,
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
    <span style={{position: 'relative', display: 'inline-block'}}>
      {/* hueco tenue (karaoke) que se apaga cuando entra la palabra */}
      <span style={{color: 'rgba(255,255,255,0.18)', opacity: 1 - p}}>{text}</span>
      {ghost(1, 0.45)}
      {ghost(2, 0.25)}
      <span
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          color,
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

export const Caps: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  if (t >= T.end) return null;
  const k = CHUNKS.findIndex((x) => t >= x.s && t < x.e);
  if (k < 0) return null;
  const c = CHUNKS[k];
  const startF = c.s * 30;
  const endF = c.e * 30;
  const p = interpolate(frame - startF, [0, 4], [0, 1], {...clamp, easing: easeOut});
  const exit = interpolate(frame, [endF - 4, endF], [0, 1], {...clamp, easing: easeInOut});
  const drift = interpolate(frame, [startF, endF], [1, 1.04], clamp);
  const float = Math.sin((frame - startF) / 14) * 5;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1640 + float, display: 'flex', justifyContent: 'center', translate: '0 -50%'}}>
        <div
          style={{
            maxWidth: 980,
            padding: '16px 32px 20px',
            borderRadius: 30,
            background: 'rgba(12,10,16,0.74)',
            border: '1.5px solid rgba(255,255,255,0.12)',
            boxShadow: '0 16px 40px rgba(0,0,0,0.45)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '0 16px',
            fontFamily: OUTFIT,
            fontWeight: 800,
            fontSize: 54,
            letterSpacing: '-0.01em',
            lineHeight: 1.12,
            opacity: p * (1 - exit),
            scale: String(interpolate(p, [0, 1], [0.92, 1]) * drift * (1 + exit * 0.06)),
            translate: `0 ${(1 - p) * 18}px`,
            filter: exit > 0 ? `blur(${12 * exit}px) brightness(${1 + 1.4 * exit})` : undefined,
          }}
        >
          {c.idx.map((i, j) => (
            <CapWord key={i} i={i} dir={j % 2 ? 1 : -1} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
