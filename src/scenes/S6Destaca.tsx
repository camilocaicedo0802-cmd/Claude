import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, cardGradient, cardShadow} from '../theme';
import {E, mix, prog} from '../lib/anim';
import {Abs, Pill, Word, textStyle} from '../components/base';
import {Cam} from '../components/Cam';
import {IconPlay} from '../components/ui';
import {W_} from '../cues';

const IN = 672;
const OUT = 763;

// trazos "a lápiz" dentro de cada cuadro del storyboard (coordenadas locales 250×420)
const sketches = [
  ['M 125 120 m -38 0 a 38 38 0 1 0 76 0 a 38 38 0 1 0 -76 0', 'M 125 160 L 125 260', 'M 125 190 L 80 230', 'M 125 190 L 170 225', 'M 125 260 L 90 330', 'M 125 260 L 160 330'],
  ['M 50 150 L 170 150 L 170 250 L 50 250 Z', 'M 170 180 L 215 160 L 215 240 L 170 220', 'M 60 300 C 100 280 150 330 200 300'],
  ['M 40 120 L 210 120', 'M 40 170 L 180 170', 'M 40 220 L 200 220', 'M 40 300 L 120 300 L 120 360 L 40 360 Z'],
];

/**
 * 672–772 · "Tú tienes la idea. Yo la convierto en un video que destaca."
 * Storyboard punteado → los cuadros se fusionan en una tarjeta morada pulida (match cut) → zoom out: la tarjeta
 * destaca entre tarjetas grises. Sale con push-in 3D hacia la tarjeta.
 */
export const S6Destaca: React.FC<{f: number}> = ({f}) => {
  const en = (fr: number) => 1300 * (1 - E.expoOut(prog(fr, IN - 2, 10)));
  const x = en(f);
  const vx = en(f + 0.5) - en(f - 0.5);

  const merge = E.expoInOut(prog(f, W_.yo, 14));
  const fill = E.expoOut(prog(f, W_.yo + 8, 10));
  const zoomOut = E.expoInOut(prog(f, W_.un - 3, 18));
  const stand = E.softBack(prog(f, W_.destaca, 10));
  const pin = E.expoIn(prog(f, OUT, 9));

  const worldS = mix(1, 0.6, zoomOut) * (1 + 2.2 * pin);
  const card = {cx: 540, cy: 1200, w: 700, h: 900};
  const headA = E.expoIn(prog(f, W_.yo - 3, 6));
  const headB = E.expoIn(prog(f, W_.en - 3, 6));

  const frames = [0, 1, 2].map((i) => {
    const fx = 95 + i * 320;
    const fy = 860;
    const fw = 250;
    const fh = 420;
    return {
      x: mix(fx, card.cx - card.w / 2, merge),
      y: mix(fy, card.cy - card.h / 2, merge),
      w: mix(fw, card.w, merge),
      h: mix(fh, card.h, merge),
      at: W_.tu2 + 2 + i * 4,
    };
  });

  // tarjetas grises alrededor (aparecen con el zoom out)
  const ghosts = [
    [-760, -620],
    [0, -1050],
    [760, -620],
    [-760, 380],
    [760, 380],
    [-760, 1380],
    [0, 1100],
    [760, 1380],
  ];

  return (
    <Cam x={x} blurX={Math.abs(vx) * 0.12} opacity={1 - prog(f, OUT + 6, 3)}>
      {/* mundo (escala con zoom out / push-in) */}
      <Cam s={worldS} origin={`${card.cx}px ${card.cy}px`} ry={-18 * pin} blurX={pin * 30}>
        {ghosts.map(([gx, gy], i) => {
          const p = E.expoOut(prog(f, W_.un - 1 + i, 12));
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: card.cx - card.w / 2 + gx,
                top: card.cy - card.h / 2 + gy,
                width: card.w,
                height: card.h,
                borderRadius: 34,
                background: '#E2E1E3',
                opacity: p * 0.95,
                transform: `scale(${0.9 + 0.1 * p})`,
                boxShadow: '0 10px 30px rgba(20,8,26,0.08)',
              }}
            >
              <div style={{position: 'absolute', left: 50, top: 60, width: 300, height: 34, borderRadius: 17, background: '#D2D0D4'}} />
              <div style={{position: 'absolute', left: 50, top: 120, width: 460, height: 22, borderRadius: 11, background: '#D8D6DA'}} />
              <div style={{position: 'absolute', left: 50, right: 50, bottom: 60, height: 460, borderRadius: 22, background: '#D8D6DA'}} />
              <div style={{position: 'absolute', left: card.w / 2 - 50, bottom: 240, opacity: 0.6}}>
                <IconPlay size={100} color="#C4C2C7" />
              </div>
            </div>
          );
        })}

        {/* storyboard → tarjeta */}
        {frames.map((fr, i) => {
          const pop = E.softBack(prog(f, fr.at, 9));
          const isMain = i === 1;
          if (merge > 0.98 && !isMain) return null;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: fr.x,
                top: fr.y,
                width: fr.w,
                height: fr.h,
                transform: `scale(${pop * (isMain ? 1 + 0.06 * stand * (1 - prog(f, W_.destaca + 10, 14)) : 1)}) rotate(${(1 - merge) * (i - 1) * 3}deg)`,
                opacity: Math.min(1, prog(f, fr.at, 4) * 2),
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  borderRadius: mix(22, 34, merge),
                  border: `4px dashed ${C.textSoft}`,
                  opacity: 1 - fill,
                  background: 'rgba(255,255,255,0.55)',
                }}
              />
              <svg width={250} height={420} viewBox="0 0 250 420" style={{position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', opacity: 1 - merge}}>
                {sketches[i].map((d, k) => (
                  <path
                    key={k}
                    d={d}
                    stroke={C.text}
                    strokeWidth={5}
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeDasharray={600}
                    strokeDashoffset={600 * (1 - E.quintOut(prog(f, fr.at + 3 + k * 2, 10)))}
                  />
                ))}
              </svg>
              {isMain && (
                <div style={{position: 'absolute', inset: 0, borderRadius: 34, background: cardGradient, boxShadow: cardShadow, opacity: fill, overflow: 'hidden'}}>
                  <div style={{position: 'absolute', left: 30, right: 30, top: 30, bottom: 210, borderRadius: 20, overflow: 'hidden'}}>
                    <Img src={staticFile('img/claqueta.jpg')} style={{position: 'absolute', height: '100%', left: -300, filter: 'grayscale(1) contrast(1.2)', transform: `scale(${1.15 - fill * 0.1})`}} />
                    <div style={{position: 'absolute', left: '50%', top: '50%', marginLeft: -60, marginTop: -60, width: 120, height: 120, borderRadius: 60, background: 'rgba(53,25,63,.8)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      <IconPlay size={60} />
                    </div>
                  </div>
                  <div style={{position: 'absolute', left: 40, bottom: 110, ...textStyle(80, C.white, 900)}}>tu video</div>
                  <div style={{position: 'absolute', left: 44, bottom: 66, ...textStyle(28, 'rgba(255,255,255,.75)', 700)}}>listo para publicar · 4K · 9:16</div>
                  <div
                    style={{
                      position: 'absolute',
                      inset: 0,
                      background: `linear-gradient(115deg, transparent ${mix(-60, 160, prog(f, W_.destaca, 20)) - 14}%, rgba(255,255,255,0.16) ${mix(-60, 160, prog(f, W_.destaca, 20))}%, transparent ${mix(-60, 160, prog(f, W_.destaca, 20)) + 14}%)`,
                    }}
                  />
                </div>
              )}
            </div>
          );
        })}
        {/* destellos alrededor de la tarjeta destacada */}
        {f >= W_.destaca &&
          Array.from({length: 10}).map((_, i) => {
            const p = prog(f, W_.destaca + (i % 3), 16);
            const a = (i / 10) * Math.PI * 2;
            const r = 560 + p * 160;
            return p > 0 && p < 1 ? (
              <div key={i} style={{position: 'absolute', left: card.cx + Math.cos(a) * r * 0.85 - 9, top: card.cy + Math.sin(a) * r - 9, width: 18, height: 18, borderRadius: 9, background: i % 2 ? C.cardLight : C.text, opacity: 1 - p, transform: `scale(${1.6 - p})`}} />
            ) : null;
          })}
      </Cam>

      {/* titulares (fuera del mundo: no escalan) */}
      {f < W_.yo + 4 && (
        <Abs style={{left: 100, top: 360, opacity: 1 - headA, transform: `translateY(${-110 * headA}px)`, filter: headA > 0 ? `blur(${headA * 16}px)` : undefined}}>
          <div style={{display: 'flex', gap: 16}}>
            <Word f={f} at={W_.tu2 - 1} size={76} color={C.textSoft}>
              tú
            </Word>
            <Word f={f} at={W_.tienes - 1} size={76} color={C.textSoft}>
              tienes
            </Word>
          </div>
          <Pill f={f} at={W_.la2 - 1} text="la idea" size={140} style={{left: 120, top: 92}} />
        </Abs>
      )}
      {f >= W_.yo - 2 && f < W_.en + 4 && (
        <Abs style={{left: 100, top: 330, opacity: 1 - headB, transform: `translateY(${-110 * headB}px)`, filter: headB > 0 ? `blur(${headB * 16}px)` : undefined}}>
          <div style={{display: 'flex', gap: 16}}>
            <Word f={f} at={W_.yo - 1} size={72} color={C.textSoft}>
              yo
            </Word>
            <Word f={f} at={W_.la3 - 1} size={72} color={C.textSoft}>
              la
            </Word>
          </div>
          <Word f={f} at={W_.convierto - 1} size={170} color={C.text}>
            convierto
          </Word>
        </Abs>
      )}
      {f >= W_.en - 2 && (
        <Abs style={{left: 110, top: 290, opacity: 1 - pin}}>
          <div style={{display: 'flex', gap: 14}}>
            {(
              [
                ['en', W_.en - 1],
                ['un', W_.un - 1],
                ['video', W_.video - 1],
                ['que', W_.que5 - 1],
              ] as [string, number][]
            ).map(([w, at]) => (
              <Word key={w} f={f} at={at} size={68} color={w === 'video' ? C.text : C.textSoft}>
                {w}
              </Word>
            ))}
          </div>
          <Pill f={f} at={W_.destaca - 1} text="destaca." size={160} style={{left: 90, top: 92}} />
        </Abs>
      )}
    </Cam>
  );
};

