import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, cardGradient, cardShadow} from '../theme';
import {E, mix, prog, tw} from '../lib/anim';
import {Abs, Chip, DashLine, Word, textStyle} from '../components/base';
import {Cam} from '../components/Cam';
import {Waveform} from '../components/ui';
import {W_} from '../cues';

/**
 * 0–166 · Gancho: "¿Necesitas editor para tus videos?" → la píldora "editor" se transforma (objeto compartido)
 * en una tarjeta vertical con creadora recortada que rompe el borde superior: "esta fluidez / ritmo / calidad".
 * Sale con push-in 3D (estilo.md §5).
 */
export const S1Intro: React.FC<{f: number}> = ({f}) => {
  // --- cámara: micro-deriva + push-in de salida
  const OUT = 157;
  const pin = E.expoIn(prog(f, OUT, 9));
  const camS = mix(1.0, 1.035, prog(f, 0, 60)) * (1 + 0.025 * E.expoOut(prog(f, W_.editor, 6)) * (1 - prog(f, W_.editor + 6, 14))) * (1 + 1.1 * pin);
  const camRy = -24 * pin;

  // --- morph píldora → tarjeta
  const M0 = 58;
  const m = E.expoInOut(prog(f, M0, 18));
  const pillIn = E.expoOut(prog(f, W_.editor - 2, 4));
  const pillGrow = E.softBack(prog(f, W_.editor, 9));
  const pill = {x: 230, y: 790, w: 580, h: 200, r: 100};
  const card = {x: 120, y: 660, w: 840, h: 720, r: 34};
  const sx = mix(pill.x + (pill.w * (1 - pillGrow)) / 2, card.x, m);
  const sw = mix(pill.w * (0.06 + 0.94 * pillGrow), card.w, m);
  const sy = mix(pill.y + (pill.h * (1 - pillIn)) / 4, card.y, m);
  const sh = mix(pill.h * (0.5 + 0.5 * pillIn), card.h, m);
  const sr = mix(pill.r, card.r, m);
  const shapeOpacity = f < W_.editor - 2 ? 0 : 1;

  // --- vaivén fluido de la tarjeta en "fluidez"
  const sway = f > W_.fluidez ? Math.sin((f - W_.fluidez) / 7) * 7 * Math.exp(-(f - W_.fluidez) / 30) : 0;

  // --- salida de palabras iniciales
  const introOut = E.expoIn(prog(f, M0 - 2, 8));

  // --- recorte que emerge
  const rise = E.expoOut(prog(f, 68, 18));
  const imgH = 900;
  const imgW = (imgH * 734) / 1075;

  const fluidezLetters = 'fluidez'.split('');
  return (
    <Cam s={camS} ry={camRy} blurX={pin * 34} opacity={1 - prog(f, OUT + 6, 3)} origin="50% 52%">
      {/* palabras del gancho */}
      <Abs style={{left: 232, top: 700, opacity: 1 - introOut, transform: `translateY(${-90 * introOut}px)`, filter: introOut > 0 ? `blur(${introOut * 14}px)` : undefined}}>
        <Word f={f} at={W_.necesitas - 1} size={76} color={C.textSoft}>
          ¿necesitas
        </Word>
      </Abs>
      <Abs style={{left: 470, top: 1015, display: 'flex', gap: 14, opacity: 1 - introOut, transform: `translateY(${-60 * introOut}px)`, filter: introOut > 0 ? `blur(${introOut * 14}px)` : undefined}}>
        <Word f={f} at={W_.para - 1} size={64} color={C.textSoft}>
          para tus
        </Word>
        <Word f={f} at={W_.videos - 1} size={64} color={C.text}>
          videos?
        </Word>
      </Abs>
      {/* mini timeline bajo el gancho */}
      <Abs style={{left: 232, top: 1120, width: 620, height: 54, opacity: 1 - introOut, transform: `translateY(${-40 * introOut}px)`}}>
        {[
          {x: 0, w: 0.28, at: W_.para + 2},
          {x: 0.3, w: 0.18, at: W_.tus + 1},
          {x: 0.5, w: 0.34, at: W_.videos},
          {x: 0.86, w: 0.14, at: W_.videos + 3},
        ].map((c, i) => {
          const p = E.expoOut(prog(f, c.at, 8));
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: `${c.x * 100}%`,
                width: `${c.w * 100 - 1}%`,
                top: 0,
                height: 54,
                borderRadius: 12,
                background: i % 2 ? C.cardLight : C.card,
                transform: `scaleX(${p})`,
                transformOrigin: 'left',
                opacity: p,
                boxShadow: '0 8px 18px rgba(20,8,26,0.18)',
              }}
            />
          );
        })}
        <div style={{position: 'absolute', left: tw(f, W_.para, 30, 0, 600, E.cubicInOut), top: -16, width: 4, height: 86, background: '#FF4D6D', borderRadius: 2, opacity: prog(f, W_.para, 4)}} />
      </Abs>

      {/* objeto compartido: píldora → tarjeta */}
      <div
        style={{
          position: 'absolute',
          left: sx,
          top: sy,
          width: sw,
          height: sh,
          opacity: shapeOpacity,
          transform: `perspective(1400px) rotateY(${sway}deg)`,
        }}
      >
        <div style={{position: 'absolute', inset: 0, borderRadius: sr, background: cardGradient, boxShadow: cardShadow, overflow: 'hidden'}}>
          {/* texto de la píldora */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: (1 - prog(f, M0, 5)) * E.expoOut(prog(f, W_.editor + 3, 7)),
              filter: f > W_.editor + 3 && f < W_.editor + 10 ? `blur(${(1 - E.expoOut(prog(f, W_.editor + 3, 7))) * 10}px)` : undefined,
            }}
          >
            <span style={{...textStyle(150, C.white), paddingRight: 8}}>editor</span>
          </div>
          {/* texto grande DETRÁS de la persona */}
          <Abs style={{left: 46, top: 40}}>
            <Word f={f} at={W_.esta - 1} size={58} color="rgba(255,255,255,0.75)">
              esta
            </Word>
          </Abs>
          <Abs style={{left: 36, top: 92, display: 'flex'}}>
            {fluidezLetters.map((l, i) => {
              const wave = f > W_.fluidez ? Math.sin((f - W_.fluidez) / 3.2 - i * 0.7) * 22 * Math.exp(-(f - W_.fluidez) / 18) : 0;
              return (
                <Word key={i} f={f} at={W_.fluidez - 1 + i * 0.6} size={172} color={C.white} dx={16} style={{marginTop: wave, letterSpacing: '-0.05em'}}>
                  {l}
                </Word>
              );
            })}
          </Abs>

        </div>
        {/* recorte de la creadora: recortado a los lados y abajo, libre por arriba */}
        <div style={{position: 'absolute', inset: 0, clipPath: `inset(-600px 0px 0px 0px round 0 0 ${sr}px ${sr}px)`, opacity: m}}>
          <Img
            src={staticFile('img/creador_bn.png')}
            style={{
              position: 'absolute',
              width: imgW,
              height: imgH,
              left: 365,
              top: card.h - imgH + 6 + (1 - rise) * 420,
              filter: `blur(${(1 - rise) * 10}px) drop-shadow(0 18px 30px rgba(10,4,14,0.45))`,
            }}
          />
        </div>
      </div>

      {/* forma de onda bajo la tarjeta: "ritmo" */}
      <Abs style={{left: 300, top: 1440, opacity: E.expoOut(prog(f, W_.ritmo - 2, 8)), transform: `translateY(${(1 - E.expoOut(prog(f, W_.ritmo - 2, 8))) * 50}px)`}}>
        <Waveform f={f} bars={30} w={660} h={120} color={C.card} seed={2} speed={1.4} />
      </Abs>
      <DashLine f={f} at={W_.ritmo - 4} d="M 200 1380 L 200 1500 L 280 1500" len={210} />
      <Chip f={f} at={W_.ritmo} style={{left: 90, top: 1550}}>
        ritmo · 104 bpm
      </Chip>
      {/* chip de calidad conectado a la esquina */}
      <DashLine f={f} at={W_.nivel - 2} d="M 900 660 L 900 560" len={110} />
      <Chip f={f} at={W_.nivel} dark style={{left: 740, top: 480}}>
        <span style={{...textStyle(34, C.white, 900)}}>4K</span>
        <span style={{opacity: 0.8}}>· calidad</span>
      </Chip>
    </Cam>
  );
};
