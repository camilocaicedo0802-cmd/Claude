import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, cardGradient, softShadow} from '../theme';
import {E, prog, tw} from '../lib/anim';
import {Abs, DashLine, Pill, Word, textStyle} from '../components/base';
import {Cam} from '../components/Cam';
import {Hearts, IconChat, IconEye, IconHeart, IconShare, Phone} from '../components/ui';
import {S3_PHONE} from './S3Demo';
import {W_} from '../cues';

const OUT = 586;

/** Subtítulo animado dentro del teléfono (demostración de captions dinámicos). */
const PhoneCaption: React.FC<{f: number; words: [string, number][]}> = ({f, words}) => {
  const active = words.reduce((acc, [, at], i) => (f >= at ? i : acc), -1);
  return (
    <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 10, width: 420}}>
      {words.map(([w, at], i) => {
        const s = E.softBack(prog(f, at, 6));
        return (
          <span
            key={i}
            style={{
              ...textStyle(46, C.white, 900),
              fontStyle: 'italic',
              textTransform: 'uppercase',
              padding: '4px 10px',
              borderRadius: 10,
              background: i === active ? C.cardLight : 'transparent',
              transform: `scale(${f >= at ? s : 0})`,
              textShadow: '0 3px 10px rgba(0,0,0,.5)',
              display: 'inline-block',
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

/**
 * 462–594 · "Cada detalle pensado para captar la atención y mantener a tu audiencia mirando".
 * Teléfono (heredado de la píldora) con un reel editado + tarjeta de retención + contador de vistas.
 */
export const S4Atencion: React.FC<{f: number}> = ({f}) => {
  const out = (fr: number) => -1700 * E.expoIn(prog(fr, OUT, 9));
  const oy = out(f);
  const ov = out(f + 0.5) - out(f - 0.5);
  const drift = tw(f, 462, 130, 1, 1.04, (t) => t);
  const punch = 1 + 0.03 * E.expoOut(prog(f, W_.atencion, 5)) * (1 - prog(f, W_.atencion + 5, 12));

  const ph = S3_PHONE;
  const reelZoom = 1.08 + prog(f, 462, 130) * 0.12;
  const retention = Math.round(tw(f, W_.mantener + 4, 34, 0, 92, E.quintOut));
  const views = tw(f, W_.audiencia, 34, 0, 1.2, E.quintOut);
  const curveP = E.quintOut(prog(f, W_.mantener + 4, 30));

  return (
    <Cam y={oy} blurY={Math.abs(ov) * 0.1} s={drift * punch}>
      {/* titular */}
      <Abs style={{left: 100, top: 300}}>
        <div style={{display: 'flex', gap: 14}}>
          {(
            [
              ['cada', W_.cada - 1],
              ['detalle', W_.detalle - 1],
              ['pensado', W_.pensado - 1],
              ['para', W_.para2 - 1],
            ] as [string, number][]
          ).map(([w, at]) => (
            <Word key={w} f={f} at={at} size={56} color={w === 'detalle' ? C.text : C.textSoft}>
              {w}
            </Word>
          ))}
        </div>
        <Word f={f} at={W_.captar - 1} size={176} color={C.text} style={{marginTop: 4}}>
          captar
        </Word>
      </Abs>
      <Pill f={f} at={W_.la - 1} text="la atención" size={104} style={{left: 300, top: 552}} />

      {/* teléfono con reel */}
      <Phone w={ph.w} h={ph.h} style={{left: ph.cx - ph.w / 2, top: ph.cy - ph.h / 2}}>
        <div style={{position: 'absolute', inset: 0, background: cardGradient}} />
        <Img
          src={staticFile('img/creador_recorte.png')}
          style={{position: 'absolute', height: '84%', bottom: 0, left: -48, transform: `scale(${reelZoom})`, transformOrigin: '50% 100%'}}
        />
        {/* barra de progreso */}
        <div style={{position: 'absolute', left: 24, right: 24, top: 64, height: 6, borderRadius: 3, background: 'rgba(255,255,255,.3)'}}>
          <div style={{width: `${prog(f, 462, 130) * 100}%`, height: '100%', borderRadius: 3, background: C.white}} />
        </div>
        {/* iconos laterales */}
        <div style={{position: 'absolute', right: 20, bottom: 210, display: 'flex', flexDirection: 'column', gap: 30, alignItems: 'center'}}>
          <div style={{transform: `scale(${1 + 0.35 * E.expoOut(prog(f, W_.atencion, 4)) * (1 - prog(f, W_.atencion + 4, 10))})`}}>
            <IconHeart size={54} color={f >= W_.atencion ? '#FF4D6D' : C.white} />
          </div>
          <IconChat size={50} />
          <IconShare size={50} />
        </div>
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 120, display: 'flex', justifyContent: 'center'}}>
          <PhoneCaption
            f={f}
            words={[
              ['cada', W_.cada],
              ['detalle', W_.detalle],
              ['cuenta', W_.pensado + 2],
            ]}
          />
        </div>
        <div style={{position: 'absolute', left: 26, bottom: 50, ...textStyle(26, C.white, 700)}}>@tu.marca · reel</div>
        <Hearts f={f} at={W_.atencion} x={ph.w - 120} y={ph.h - 330} />
      </Phone>

      {/* tarjeta de retención */}
      <DashLine f={f} at={W_.mantener - 2} d="M 790 1060 L 790 980" len={90} />
      <div
        style={{
          position: 'absolute',
          left: 640,
          top: 1040,
          width: 400,
          height: 300,
          borderRadius: 26,
          background: C.white,
          boxShadow: softShadow,
          transform: `rotate(3deg) scale(${E.softBack(prog(f, W_.mantener, 10))})`,
          opacity: prog(f, W_.mantener, 4),
          padding: 26,
        }}
      >
        <div style={{...textStyle(28, C.textSoft, 700)}}>retención</div>
        <div style={{...textStyle(84, C.text, 900), marginTop: 4}}>{retention}%</div>
        <svg width={350} height={120} style={{position: 'absolute', left: 25, bottom: 22}}>
          <path d="M 0 14 C 40 16 60 22 100 24 S 200 26 250 27 S 330 28 350 29" stroke={C.cardLight} strokeWidth={7} fill="none" strokeLinecap="round" strokeDasharray={400} strokeDashoffset={400 * (1 - curveP)} />
          <path d="M 0 14 C 40 16 60 22 100 24 S 200 26 250 27 S 330 28 350 29 L 350 120 L 0 120 Z" fill={C.cardLight} opacity={0.12 * curveP} />
        </svg>
      </div>

      {/* contador de vistas */}
      <DashLine f={f} at={W_.audiencia - 3} d="M 300 1560 L 300 1500" len={70} />
      <div
        style={{
          position: 'absolute',
          left: 40,
          top: 1560,
          padding: '20px 30px',
          borderRadius: 24,
          background: C.white,
          boxShadow: softShadow,
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          transform: `rotate(-3deg) scale(${E.softBack(prog(f, W_.audiencia, 10))})`,
          opacity: prog(f, W_.audiencia, 4),
        }}
      >
        <IconEye size={58} />
        <span style={{...textStyle(64, C.text, 900)}}>{views.toFixed(1)}M</span>
        <span style={{...textStyle(30, C.textSoft, 700)}}>mirando</span>
      </div>
    </Cam>
  );
};
