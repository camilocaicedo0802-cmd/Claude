import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, cardGradient, cardShadow} from '../theme';
import {E, mix, prog, tw} from '../lib/anim';
import {Abs, DirBlur, Word, textStyle} from '../components/base';
import {Cam} from '../components/Cam';
import {ColorWheel, Waveform} from '../components/ui';
import {W_} from '../cues';

const IN = 358;
export const S3_PHONE = {cx: 540, cy: 1240, w: 500, h: 1000};

/** Titular de dos niveles (pequeño + grande) que entra palabra a palabra y sale hacia arriba con blur. */
const Head: React.FC<{f: number; small: [string, number][]; big: [string, number]; out: number; top?: number}> = ({f, small, big, out, top = 330}) => {
  const o = E.expoIn(prog(f, out, 6));
  if (f >= out + 6) return null;
  return (
    <Abs style={{left: 110, top, opacity: 1 - o, transform: `translateY(${-110 * o}px)`, filter: o > 0 ? `blur(${o * 16}px)` : undefined}}>
      <div style={{display: 'flex', gap: 16}}>
        {small.map(([w, at]) => (
          <Word key={w} f={f} at={at} size={64} color={C.textSoft} dy={30} dx={0}>
            {w}
          </Word>
        ))}
      </div>
      <Word f={f} at={big[1]} size={176} color={C.text} dy={40} dx={0} style={{marginTop: -6}}>
        {big[0]}
      </Word>
    </Abs>
  );
};

/**
 * 357–466 · "transiciones fluidas" (entra con barrido = la propia transición), "color grading" (antes/después +
 * ruedas de color) y "sound design" (la tarjeta se colapsa en píldora con forma de onda). Sale transformando la
 * píldora en el teléfono de la escena siguiente (match cut).
 */
export const S3Demo: React.FC<{f: number}> = ({f}) => {
  const enter = (fr: number) => 1300 * (1 - E.expoOut(prog(fr, IN, 10)));
  const ex = enter(f);
  const ev = enter(f + 0.5) - enter(f - 0.5);

  // tarjeta → píldora → teléfono
  const card = {x: 160, y: 660, w: 760, h: 960, r: 34};
  const pillT = E.expoInOut(prog(f, 429, 12));
  const pill = {w: 840, h: 230, r: 115};
  const phoneT = E.expoInOut(prog(f, 455, 10));
  let w = mix(card.w, pill.w, pillT);
  let h = mix(card.h, pill.h, pillT);
  let r = mix(card.r, pill.r, pillT);
  w = mix(w, S3_PHONE.w, phoneT);
  h = mix(h, S3_PHONE.h, phoneT);
  r = mix(r, S3_PHONE.w * 0.14, phoneT);
  const cx = 540;
  const cy = mix(card.y + card.h / 2, S3_PHONE.cy, phoneT);

  // contenido de la tarjeta
  const photoOpacity = 1 - prog(f, 429, 6);
  // transición 1: barrido interno con blur (bailarina → estudio)
  const t1 = (fr: number) => E.expoInOut(prog(fr, 371, 8));
  const t1v = Math.abs(t1(f + 0.5) - t1(f - 0.5));
  // transición 2: revelado circular (estudio → paisaje)
  const t2 = E.expoOut(prog(f, W_.fluidas, 12));
  // color grading
  const split = tw(f, W_.color, 22, 1, 0.42, E.expoOut);
  const gradeOn = f >= W_.color - 2;

  return (
    <Cam x={ex} blurX={Math.abs(ev) * 0.12}>
      <Head f={f} small={[['transiciones', W_.transiciones - 1]]} big={['fluidas', W_.fluidas - 1]} out={398} />
      <Head f={f} small={[['color', W_.color - 1]]} big={['grading', W_.grading - 1]} out={428} />
      <Head f={f} small={[['y', W_.y2 - 1], ['sound', W_.sound - 1]]} big={['design', W_.design - 1]} out={456} />

      {/* objeto compartido */}
      <div style={{position: 'absolute', left: cx - w / 2, top: cy - h / 2, width: w, height: h, borderRadius: r, background: cardGradient, boxShadow: cardShadow, overflow: 'hidden'}}>
        <div style={{position: 'absolute', inset: 0, background: C.black, opacity: phoneT}} />
        {photoOpacity > 0 && (
          <div style={{position: 'absolute', inset: 18, borderRadius: Math.max(8, r - 16), overflow: 'hidden', opacity: photoOpacity}}>
            {!gradeOn ? (
              <>
                <DirBlur x={t1v * 60}>
                  <Img src={staticFile('img/bailarina.jpg')} style={{position: 'absolute', height: '100%', left: -420 - t1(f) * 700, transform: `scale(${1.05 + prog(f, IN, 40) * 0.08})`}} />
                  <Img src={staticFile('img/estudio.jpg')} style={{position: 'absolute', height: '100%', left: -380 + (1 - t1(f)) * 900, transform: `scale(${1.15 - t1(f) * 0.1})`}} />
                </DirBlur>
                <div style={{position: 'absolute', inset: 0, clipPath: `circle(${t2 * 120}% at 50% 55%)`}}>
                  <Img src={staticFile('img/paisaje.jpg')} style={{position: 'absolute', height: '100%', left: -300, transform: `scale(${1.25 - t2 * 0.15})`}} />
                </div>
              </>
            ) : (
              <>
                <Img src={staticFile('img/paisaje.jpg')} style={{position: 'absolute', height: '100%', left: -300, transform: 'scale(1.1)', filter: 'saturate(1.45) contrast(1.15) brightness(0.97) hue-rotate(-10deg)'}} />
                <div style={{position: 'absolute', inset: 0, clipPath: `inset(0 0 0 ${split * 100}%)`}}>
                  <Img src={staticFile('img/paisaje.jpg')} style={{position: 'absolute', height: '100%', left: -300, transform: 'scale(1.1)', filter: 'saturate(0.2) contrast(0.7) brightness(1.15)'}} />
                </div>
                <div style={{position: 'absolute', top: 0, bottom: 0, left: `${split * 100}%`, width: 5, marginLeft: -2.5, background: C.white, boxShadow: '0 0 12px rgba(0,0,0,.4)'}}>
                  <div style={{position: 'absolute', top: '50%', left: -27, marginTop: -27, width: 54, height: 54, borderRadius: 27, background: C.white, boxShadow: '0 6px 14px rgba(0,0,0,.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', ...textStyle(26, C.text, 900)}}>
                    ‹›
                  </div>
                </div>
                <div style={{position: 'absolute', left: 22, top: 22, padding: '8px 16px', borderRadius: 12, background: 'rgba(22,22,22,0.55)', ...textStyle(26, C.white, 800), opacity: prog(f, W_.color + 4, 5)}}>DESPUÉS</div>
                <div style={{position: 'absolute', right: 22, top: 22, padding: '8px 16px', borderRadius: 12, background: 'rgba(255,255,255,0.75)', ...textStyle(26, C.text, 800), opacity: prog(f, W_.color, 5)}}>ANTES · LOG</div>
              </>
            )}
          </div>
        )}
        {/* forma de onda en la píldora */}
        {f >= 432 && (
          <div style={{position: 'absolute', left: 0, right: 0, top: '50%', marginTop: -70, display: 'flex', justifyContent: 'center', opacity: prog(f, 433, 6) * (1 - phoneT)}}>
            <Waveform f={f} bars={36} w={700} h={140} color={C.white} seed={7} speed={1.8} />
          </div>
        )}
      </div>

      {/* ruedas de color */}
      {f < 440 && (
        <Abs style={{left: 0, right: 0, top: 1660, display: 'flex', justifyContent: 'center', gap: 70, transform: `scale(${1 - E.expoIn(prog(f, 429, 7))})`, opacity: 1 - prog(f, 431, 5)}}>
          <ColorWheel f={f} at={W_.color + 2} size={150} label="sombras" puck={[0.55, 0.4]} />
          <ColorWheel f={f} at={W_.color + 6} size={150} label="medios" puck={[-0.3, -0.5]} />
          <ColorWheel f={f} at={W_.grading + 2} size={150} label="luces" puck={[0.4, -0.55]} />
        </Abs>
      )}

      {/* pistas de audio */}
      {[
        {label: 'MÚSICA', y: 1340, at: W_.sound + 2, from: -1, seed: 3, col: C.cardLight},
        {label: 'SFX', y: 1440, at: W_.design + 1, from: 1, seed: 9, col: '#9B6BAA'},
      ].map((t) => {
        const p = E.expoOut(prog(f, t.at, 9));
        const o = 1 - prog(f, 454, 5);
        return (
          <Abs key={t.label} style={{left: 120, top: t.y, width: 840, height: 74, transform: `translateX(${(1 - p) * 900 * t.from}px)`, opacity: p * o, display: 'flex', alignItems: 'center', gap: 16}}>
            <div style={{width: 130, ...textStyle(26, C.text, 800)}}>{t.label}</div>
            <div style={{flex: 1, height: 64, borderRadius: 14, background: t.col, padding: '0 14px', display: 'flex', alignItems: 'center', boxShadow: '0 10px 22px rgba(20,8,26,0.18)'}}>
              <Waveform f={f} bars={44} w={660} h={48} color="rgba(255,255,255,0.85)" seed={t.seed} live={false} />
            </div>
          </Abs>
        );
      })}
    </Cam>
  );
};
