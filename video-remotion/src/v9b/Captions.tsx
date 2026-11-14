import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeInOut} from '../engine/helpers';
import {Word as RefWord} from '../engine/Title';
import {OUTFIT} from '../v1/theme';
import {WORDS} from '../v9/timeline';
import {CHUNKS} from './chunks';
import {DISPLAY, KEY, NO_CAPS, capY} from './data';

// ------------------------------------------------------------------
// Subtítulo cinético con el tratamiento de texto de la referencia (estilo.md §3 y §10.3):
// - Outfit ExtraBold 800 en minúsculas, interletrado −0,05 em, interlineado 0,9;
// - dos tonos alternos por bloque: blanco con brillo + morado, o cromado + morado;
//   la palabra clave va en morado degradado con volumen 3D y más grande;
// - cada palabra entra «fantasma» al pronunciarla (5 fotogramas: desenfoque 16→0,
//   escala 1,08→1, desplazamiento lateral) con 2 copias-estela;
// - líneas escalonadas, deriva lenta 1→1,04 y flotación ±5 px;
// - salida con destello (brillo + desenfoque) en 4 fotogramas;
// - whoosh corto en cada palabra clave que entra (ver data.ts).
// ------------------------------------------------------------------

const clean = (i: number) => (DISPLAY[i] ?? WORDS[i].text.replace(/[,.]/g, '')).toLowerCase();

/** Reparte el bloque en líneas: la palabra clave abre línea propia (como los títulos de la referencia). */
const toLines = (idx: number[]) => {
  const p = idx.findIndex((i) => KEY.has(i));
  if (p <= 0) {
    if (p === 0) {
      let q = 0;
      while (q < idx.length && KEY.has(idx[q])) q++;
      return q < idx.length ? [idx.slice(0, q), idx.slice(q)] : [idx];
    }
    return [idx];
  }
  return [idx.slice(0, p), idx.slice(p)];
};

const SMALL = 86;
const BIG = 124;

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  if (NO_CAPS.some(([a, b]) => t >= a && t < b)) return null;
  const k = CHUNKS.findIndex((x) => t >= x.s && t < x.e);
  if (k < 0) return null;
  const c = CHUNKS[k];
  const tone = k % 2 ? 'chrome' : 'white';
  const startF = c.s * 30;
  const endF = c.e * 30;
  const exit = interpolate(frame, [endF - 4, endF], [0, 1], {...clamp, easing: easeInOut});
  const drift = interpolate(frame, [startF, endF], [1, 1.04], clamp);
  const float = Math.sin((frame - startF) / 14) * 5;
  const lines = toLines(c.idx);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: capY(t) + float,
          translate: '0 -50%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          scale: String(drift * (1 + exit * 0.06)),
          opacity: 1 - exit,
          filter: exit > 0 ? `blur(${12 * exit}px) brightness(${1 + 1.4 * exit})` : undefined,
        }}
      >
        {lines.map((line, li) => {
          const sizes = line.map((i) => (KEY.has(i) ? BIG : SMALL));
          // ancho estimado de Outfit 800 ≈ 0,56 em por letra; se reduce si no cabe en 960 px
          const est = line.reduce((w, i, j) => w + clean(i).length * sizes[j] * 0.56 + sizes[j] * 0.18, 0);
          const fit = Math.min(1, 960 / est);
          const dx = lines.length > 1 ? (li % 2 ? 40 : -30) : 0;
          return (
            <div
              key={li}
              style={{
                display: 'flex',
                alignItems: 'baseline',
                fontFamily: OUTFIT,
                fontWeight: 800,
                lineHeight: 0.9,
                letterSpacing: '-0.05em',
                whiteSpace: 'nowrap',
                marginTop: li === 0 ? 0 : -6,
                translate: `${dx}px 0`,
              }}
            >
              {line.map((i, j) => (
                <span key={i} style={{fontSize: sizes[j] * fit, marginRight: j < line.length - 1 ? sizes[j] * fit * 0.18 : 0}}>
                  <RefWord text={clean(i)} at={WORDS[i].s} color={KEY.has(i) ? 'purple' : tone} dir={li % 2 ? 1 : -1} />
                </span>
              ))}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
