import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, cardGradient, cardShadow, softShadow} from '../theme';
import {E, mix, prog} from '../lib/anim';
import {Abs, DashLine, Word, textStyle} from '../components/base';
import {Cam} from '../components/Cam';
import {Hearts, IconArrowUp, IconCursor, IconHeart, IconPlay} from '../components/ui';
import {W_} from '../cues';

const IN = 588;
const OUT = 666;

/**
 * 588–676 · "Desde reels que impactan hasta anuncios que venden".
 * Entra desde abajo (continúa el barrido vertical), sale con barrido horizontal.
 */
export const S5Formatos: React.FC<{f: number}> = ({f}) => {
  const en = (fr: number) => 1700 * (1 - E.expoOut(prog(fr, IN, 11)));
  const ex = (fr: number) => -1300 * E.expoIn(prog(fr, OUT, 9));
  const y = en(f);
  const x = ex(f);
  const vy = en(f + 0.5) - en(f - 0.5);
  const vx = ex(f + 0.5) - ex(f - 0.5);

  const headA = E.expoIn(prog(f, 622, 6));
  // tarjeta reel
  const reelIn = E.expoOut(prog(f, W_.rills - 2, 12));
  const reelPunch = 1 + 0.07 * E.expoOut(prog(f, W_.impactan, 4)) * (1 - prog(f, W_.impactan + 4, 12));
  // tarjeta anuncio
  const adIn = E.expoOut(prog(f, W_.hasta + 2, 12));
  // cursor
  const cur = E.expoInOut(prog(f, W_.anuncios + 2, 14));
  const click = W_.venden;
  const press = f >= click ? 1 - 0.07 * Math.sin(Math.PI * prog(f, click, 6)) : 1;
  const ripple = prog(f, click, 14);

  return (
    <Cam y={y} x={x} blurY={Math.abs(vy) * 0.1} blurX={Math.abs(vx) * 0.12}>
      {/* titular A */}
      {f < 630 && (
        <Abs style={{left: 100, top: 300, opacity: 1 - headA, transform: `translateY(${-110 * headA}px)`, filter: headA > 0 ? `blur(${headA * 16}px)` : undefined}}>
          <div>
            <Word f={f} at={W_.desde - 1} size={64} color={C.textSoft}>
              desde
            </Word>
          </div>
          <div style={{display: 'flex', alignItems: 'flex-end', gap: 24}}>
            <Word f={f} at={W_.rills - 1} size={190} color={C.text}>
              reels
            </Word>
            <div style={{display: 'flex', gap: 12, paddingBottom: 24}}>
              <Word f={f} at={W_.que3 - 1} size={58} color={C.textSoft}>
                que
              </Word>
              <Word f={f} at={W_.impactan - 1} size={58} color={C.text}>
                impactan
              </Word>
            </div>
          </div>
        </Abs>
      )}
      {/* titular B */}
      <Abs style={{left: 100, top: 300}}>
        <div>
          <Word f={f} at={W_.hasta - 1} size={64} color={C.textSoft}>
            hasta
          </Word>
        </div>
        <div>
          <Word f={f} at={W_.anuncios - 1} size={176} color={C.text}>
            anuncios
          </Word>
        </div>
        <div style={{display: 'flex', gap: 12, marginLeft: 380, marginTop: 4}}>
          <Word f={f} at={W_.que4 - 1} size={58} color={C.textSoft}>
            que
          </Word>
          <Word f={f} at={W_.venden - 1} size={58} color={C.text}>
            venden
          </Word>
        </div>
      </Abs>

      {/* reel */}
      <div
        style={{
          position: 'absolute',
          left: 70,
          top: 820,
          width: 440,
          height: 780,
          borderRadius: 34,
          background: cardGradient,
          boxShadow: cardShadow,
          padding: 16,
          transform: `translateY(${(1 - reelIn) * 900}px) rotate(${mix(-14, -5, reelIn)}deg) scale(${reelPunch})`,
        }}
      >
        <div style={{position: 'absolute', inset: 16, borderRadius: 22, overflow: 'hidden'}}>
          <Img src={staticFile('img/bailarina.jpg')} style={{position: 'absolute', height: '100%', left: -470, transform: `scale(${1.05 + prog(f, IN, 80) * 0.1})`}} />
          <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(transparent 60%, rgba(22,10,30,.75))'}} />
          <div style={{position: 'absolute', left: 22, bottom: 26, ...textStyle(30, C.white, 800)}}>reel · 0:15</div>
          <div style={{position: 'absolute', left: '50%', top: '45%', marginLeft: -50, marginTop: -50, width: 100, height: 100, borderRadius: 50, background: 'rgba(255,255,255,.22)', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 1 - prog(f, W_.impactan, 6)}}>
            <IconPlay size={52} />
          </div>
          <div style={{position: 'absolute', right: 18, bottom: 90}}>
            <IconHeart size={50} color={f >= W_.impactan ? '#FF4D6D' : C.white} />
          </div>
        </div>
        <Hearts f={f} at={W_.impactan} x={330} y={560} n={9} />
      </div>

      {/* anuncio */}
      <div
        style={{
          position: 'absolute',
          left: 570,
          top: 880,
          width: 440,
          height: 760,
          borderRadius: 34,
          background: C.white,
          boxShadow: cardShadow,
          overflow: 'hidden',
          transform: `translateX(${(1 - adIn) * 700}px) rotate(${mix(14, 5, adIn)}deg)`,
          opacity: f < W_.hasta + 2 ? 0 : 1,
        }}
      >
        <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 420, overflow: 'hidden'}}>
          <Img src={staticFile('img/audifonos.jpg')} style={{position: 'absolute', height: '100%', left: -200, transform: `scale(${1.1 + prog(f, W_.hasta, 50) * 0.08})`}} />
          <div style={{position: 'absolute', left: 20, top: 20, padding: '8px 16px', borderRadius: 999, background: C.cardDark, ...textStyle(30, C.white, 900)}}>-30%</div>
        </div>
        <div style={{position: 'absolute', left: 28, top: 446, ...textStyle(46, C.text, 900)}}>Audio Pro X</div>
        <div style={{position: 'absolute', left: 28, top: 500, ...textStyle(28, C.textSoft, 600), fontStyle: 'normal', letterSpacing: 0}}>Sonido que se siente.</div>
        <div
          style={{
            position: 'absolute',
            left: 28,
            right: 28,
            bottom: 34,
            height: 104,
            borderRadius: 999,
            background: `linear-gradient(120deg, ${C.cardHi}, ${C.cardDark} 55%, ${C.card})`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `scale(${press})`,
            boxShadow: softShadow,
            overflow: 'hidden',
            ...textStyle(40, C.white, 900),
          }}
        >
          comprar ahora
          {ripple > 0 && ripple < 1 && (
            <div style={{position: 'absolute', left: '62%', top: '50%', width: 600 * ripple, height: 600 * ripple, marginLeft: -300 * ripple, marginTop: -300 * ripple, borderRadius: '50%', background: 'rgba(255,255,255,0.25)', opacity: 1 - ripple}} />
          )}
        </div>
      </div>

      {/* cursor */}
      {f >= W_.anuncios && (
        <Abs style={{left: mix(1060, 830, cur), top: mix(1900, 1545, cur), transform: `scale(${f >= click && f < click + 5 ? 0.85 : 1})`}}>
          <IconCursor size={86} />
        </Abs>
      )}
      {/* resultado */}
      <DashLine f={f} at={click + 2} d="M 880 860 L 880 780" len={90} />
      <div
        style={{
          position: 'absolute',
          left: 700,
          top: 690,
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '16px 24px',
          borderRadius: 20,
          background: C.white,
          boxShadow: softShadow,
          transform: `scale(${E.softBack(prog(f, click + 3, 9))})`,
          opacity: prog(f, click + 3, 4),
          ...textStyle(36, C.text, 900),
        }}
      >
        <div style={{width: 46, height: 46, borderRadius: 23, background: C.cardLight, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <IconArrowUp size={30} />
        </div>
        +ventas
      </div>
    </Cam>
  );
};
