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

/**
 * Las tres cosas, una por golpe (como «PROBLEMA 01/02/03» del lienzo): número grande 01 · 02 · 03 y la pregunta
 * palabra a palabra; arriba, en el marco, el contador «3 COSAS» con tres puntos que se encienden.
 */
export const Lista: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const g = T.golpes;
  if (t < g[0] - 0.05 || t > T.marco.to + 0.1) return null;
  const k = g.filter((a) => t >= a).length - 1; // golpe activo
  const sale = interpolate(t, [T.marco.to - 0.08, T.marco.to + 0.05], [1, 0], clamp);
  const l = LISTA[Math.max(0, k)];
  const a = g[Math.max(0, k)];
  const pn = interpolate(t, [a, a + 0.2], [0, 1], {...clamp, easing: easeOut});
  const linea: Linea = {kind: 'small', words: l.words};
  return (
    <AbsoluteFill style={{opacity: sale}}>
      {/* contador en la franja superior del marco */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 118, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 22}}>
        <div style={{fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: '0.3em', color: P.white, marginRight: 10}}>3 COSAS</div>
        {g.map((ag, j) => {
          const on = interpolate(t, [ag, ag + 0.15], [0, 1], clamp);
          return (
            <div
              key={j}
              style={{
                width: 46,
                height: 46,
                borderRadius: 23,
                border: '3px solid rgba(255,255,255,0.9)',
                background: on > 0 ? `rgba(255,255,255,${on})` : 'transparent',
                color: P.deep,
                fontFamily: SANS,
                fontWeight: 800,
                fontSize: 24,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transform: `scale(${1 + 0.25 * Math.sin(on * Math.PI)})`,
              }}
            >
              {on > 0.5 ? j + 1 : ''}
            </div>
          );
        })}
      </div>
      {/* golpe: número + pregunta */}
      <div
        style={{
          position: 'absolute',
          left: 64,
          top: 1100,
          width: 952,
          height: 470,
          borderRadius: 28,
          background: 'linear-gradient(180deg, rgba(14,0,32,0.72) 0%, rgba(14,0,32,0.9) 100%)',
          boxShadow: '0 0 0 2px rgba(183,1,252,0.45), 0 20px 50px rgba(0,0,0,0.45)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
        }}
      >
        <div
          key={l.n}
          style={{
            fontFamily: SANS,
            fontWeight: 800,
            fontSize: 150,
            lineHeight: 1,
            letterSpacing: '-0.04em',
            color: P.purple,
            textShadow: '0 0 30px rgba(183,1,252,0.55)',
            opacity: pn,
            filter: `blur(${(1 - pn) * 12}px)`,
            transform: `translateY(${(1 - pn) * 20}px) scale(${1.15 - 0.15 * pn})`,
          }}
        >
          {l.n}
        </div>
        <div style={{display: 'flex', gap: 20, alignItems: 'baseline', flexWrap: 'wrap', justifyContent: 'center', maxWidth: 900}}>
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
                size={clave ? 96 : 64}
                weight={clave ? 800 : 400}
                spacing={clave ? '-0.03em' : '0.005em'}
              />
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
