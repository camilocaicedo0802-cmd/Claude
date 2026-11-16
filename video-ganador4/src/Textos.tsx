import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {FPS, P, SANS, SERIF, clamp, easeOut, we, ws} from './base';
import {BLOQUES, Bloque, LISTA, Linea, T} from './data';
import {WORDS} from './timeline';

// estilo.md §2 — tamaños a 1080x1920
const SMALL = 58;
const BIG = 132;
const SINGLE = 64;
const ENTRA = 8 / FPS; // entrada de palabra: 8 fotogramas
const SALE = 7 / FPS; // salida del bloque: 7 fotogramas
const ANTES = 0.06; // la palabra aparece un poco antes de decirla

const limpio = (s: string) => s.replace(/[.,;:!?]+$/g, '').replace(/^[¿¡]/, '');
const sombra = '0 4px 14px rgba(0,0,0,0.5), 0 1px 3px rgba(0,0,0,0.35)';
const halo = `0 0 18px rgba(183,1,252,0.55), 0 0 36px rgba(150,1,253,0.3), ${sombra}`;

const inicio = (b: Bloque) => ws(b.lines[0].words[0]) - ANTES;
const finDe = (k: number) => {
  const b = BLOQUES[k];
  const sig = BLOQUES[k + 1];
  const natural = sig ? inicio(sig) - 0.02 : Infinity;
  return Math.min(b.end ?? Infinity, natural);
};

/** Una palabra: aparece con opacidad, desenfoque 10→0 px, subida 8 px y escala 0,96→1. */
const Palabra: React.FC<{i: number; t: number; line: Linea; color: string; shadow: string; size: number; weight: number; spacing: string}> = ({i, t, line, color, shadow, size, weight, spacing}) => {
  const texto = line.over?.[i] ?? limpio(WORDS[i].text);
  const serif = line.serif?.includes(i);
  const style: React.CSSProperties = {
    fontFamily: serif ? SERIF : SANS,
    fontStyle: serif ? 'italic' : 'normal',
    fontWeight: serif ? 400 : weight,
    fontSize: serif ? size * 1.12 : size,
    letterSpacing: serif ? '0' : spacing,
    color,
    textShadow: shadow,
    whiteSpace: 'pre',
    display: 'inline-block',
  };
  if (line.typed) {
    // letra a letra al ritmo de la voz (como «uncomfortable» en la referencia)
    const n = texto.length;
    const step = Math.min(0.07, (we(i) - ws(i)) / n);
    return (
      <span style={style}>
        {texto.split('').map((ch, k) => {
          const a = ws(i) - 0.04 + k * step;
          const p = interpolate(t, [a, a + 2 / FPS], [0, 1], clamp);
          return (
            <span key={k} style={{opacity: p, filter: p < 1 ? `blur(${(1 - p) * 6}px)` : undefined}}>
              {ch}
            </span>
          );
        })}
      </span>
    );
  }
  const a = ws(i) - ANTES;
  const p = interpolate(t, [a, a + ENTRA], [0, 1], {...clamp, easing: easeOut});
  return (
    <span
      style={{
        ...style,
        opacity: p,
        filter: p < 1 ? `blur(${(1 - p) * 10}px)` : undefined,
        transform: `translateY(${(1 - p) * 8}px) scale(${0.96 + 0.04 * p})`,
      }}
    >
      {texto}
    </span>
  );
};

const LineaTexto: React.FC<{line: Linea; t: number; box?: boolean}> = ({line, t, box}) => {
  const big = line.kind === 'big';
  const single = line.kind === 'single';
  let size = line.size ?? (big ? BIG : single ? SINGLE : SMALL);
  if (big) {
    // la palabra grande nunca se sale del cuadro: ancho estimado ≤ 960 px (InterDisplay ExtraBold ≈ 0,56 em por letra)
    const letras = line.words.reduce((n, i) => n + (line.over?.[i] ?? limpio(WORDS[i].text)).length, 0) + (line.words.length - 1) * 0.6;
    size = Math.min(size, 960 / (letras * 0.56));
  }
  const color = line.purple ? P.purple : P.white;
  const shadow = line.purple ? halo : sombra;
  const weight = big ? 800 : single ? 500 : 400;
  const spacing = big ? '-0.03em' : '0.005em';
  const lastBig = line.words[line.words.length - 1];
  // caja resaltada (§4.3): trazo 3 px + relleno al 22 % alrededor de la palabra grande
  const pb = box ? interpolate(t, [ws(lastBig) - 0.03, ws(lastBig) + 0.17], [0, 1], {...clamp, easing: easeOut}) : 0;
  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        justifyContent: line.words.length > 1 && !big ? 'space-between' : 'center',
        gap: big ? size * 0.24 : 24,
        lineHeight: 1,
        marginTop: big ? -2 : 0,
        transform: line.dx ? `translateX(${line.dx}px)` : undefined,
      }}
    >
      {box && pb > 0 ? (
        <div
          style={{
            position: 'absolute',
            inset: '-6px -26px -12px -26px',
            border: `3px solid ${P.purple}`,
            background: 'rgba(183,1,252,0.22)',
            borderRadius: 6,
            boxShadow: '0 0 24px rgba(183,1,252,0.45)',
            opacity: pb,
            transform: `scaleX(${0.85 + 0.15 * pb})`,
          }}
        />
      ) : null}
      {line.words.map((i) => (
        <Palabra key={i} i={i} t={t} line={line} color={color} shadow={shadow} size={size} weight={weight} spacing={spacing} />
      ))}
    </div>
  );
};

/** Bloques de 2–3 líneas que se construyen palabra a palabra (estilo.md §2). */
export const Textos: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {BLOQUES.map((b, k) => {
        const a = inicio(b);
        const e = finDe(k);
        if (t < a - 0.02 || t > e + SALE) return null;
        const q = interpolate(t, [e, e + SALE], [1, 0], clamp);
        const vida = interpolate(t, [a, e], [1, 1.03], clamp);
        return (
          <div
            key={k}
            style={{
              position: 'absolute',
              left: b.x ?? 540,
              top: b.y,
              transform: `translate(-50%, -50%) scale(${vida})`,
              opacity: q,
              filter: q < 1 ? `blur(${(1 - q) * 12}px)` : undefined,
              display: 'inline-flex',
              flexDirection: 'column',
              alignItems: 'stretch',
            }}
          >
            {b.lines.map((l, j) => (
              <LineaTexto key={j} line={l} t={t} box={b.box && l.kind === 'big'} />
            ))}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Lista final dentro del marco: 1 · 2 · 3, palabra a palabra. */
export const Lista: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  if (t < ws(LISTA[0].words[0]) - 0.1 || t > T.cierre.from + 0.25) return null;
  const sale = interpolate(t, [T.cierre.from, T.cierre.from + 0.2], [1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: sale}}>
      <div
        style={{
          position: 'absolute',
          left: 64,
          top: 1118,
          width: 952,
          height: 440,
          borderRadius: 28,
          background: 'linear-gradient(180deg, rgba(14,0,32,0.78) 0%, rgba(14,0,32,0.9) 100%)',
          boxShadow: '0 0 0 2px rgba(183,1,252,0.45), 0 20px 50px rgba(0,0,0,0.45)',
          opacity: interpolate(t, [ws(LISTA[0].words[0]) - 0.12, ws(LISTA[0].words[0]) + 0.08], [0, 1], clamp),
        }}
      />
      <div style={{position: 'absolute', left: 102, top: 1162, display: 'flex', flexDirection: 'column', gap: 30}}>
        {LISTA.map((l, k) => {
          const a = ws(l.words[0]) - 0.1;
          const p = interpolate(t, [a, a + 10 / FPS], [0, 1], {...clamp, easing: easeOut});
          const linea: Linea = {kind: 'small', words: l.words};
          return (
            <div key={k} style={{display: 'flex', alignItems: 'center', gap: 26, opacity: p, transform: `translateX(${(1 - p) * -30}px)`}}>
              <div
                style={{
                  width: 74,
                  height: 74,
                  borderRadius: 37,
                  background: P.purple,
                  boxShadow: '0 0 22px rgba(183,1,252,0.6)',
                  color: P.white,
                  fontFamily: SANS,
                  fontWeight: 800,
                  fontSize: 44,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transform: `scale(${0.6 + 0.4 * p})`,
                }}
              >
                {l.n}
              </div>
              <div style={{display: 'flex', gap: 18, alignItems: 'baseline'}}>
                {l.words.map((i, j) => {
                  const clave = i === l.clave;
                  const pre = j === 0 ? l.pre : '';
                  const post = j === l.words.length - 1 ? l.post : '';
                  const over = {[i]: `${pre}${limpio(WORDS[i].text).toLowerCase()}${post}`};
                  return (
                    <Palabra
                      key={i}
                      i={i}
                      t={t}
                      line={{...linea, over}}
                      color={clave ? P.purple : P.white}
                      shadow={clave ? halo : sombra}
                      size={clave ? 70 : 58}
                      weight={clave ? 800 : 400}
                      spacing={clave ? '-0.02em' : '0.005em'}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
