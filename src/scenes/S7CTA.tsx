import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, cardGradient, cardShadow, softShadow} from '../theme';
import {E, mix, prog} from '../lib/anim';
import {Abs, DashLine, Pill, Word, textStyle} from '../components/base';
import {Cam} from '../components/Cam';
import {IconCursor, IconSend} from '../components/ui';
import {W_} from '../cues';

const IN = 767;
const FINAL = 840;

/**
 * 767–900 · "¿Listo para llevar tu contenido al siguiente nivel? ¡Hablemos!"
 * Escalones morados que suben (niveles) + recorte de cámara que emerge del último escalón → cierre tipográfico
 * "hablemos." con botón de contacto.
 */
export const S7CTA: React.FC<{f: number}> = ({f}) => {
  const zin = E.expoOut(prog(f, IN, 9));
  const out = E.expoIn(prog(f, FINAL, 8));
  const drift = mix(1, 1.04, prog(f, IN, 80));

  const steps = [
    {x: 110, w: 250, h: 250, at: W_.llevar, label: 'idea'},
    {x: 415, w: 250, h: 420, at: W_.contenido, label: 'edición'},
    {x: 720, w: 250, h: 600, at: W_.siguiente, label: 'impacto'},
  ];
  const base = 1720;
  const emerge = E.expoOut(prog(f, W_.nivel2 + 1, 14));

  // cierre
  const fin = (d: number) => E.expoOut(prog(f, W_.hablemos - 2 + d, 10));
  const click = 868;

  return (
    <>
      <Cam s={mix(1.3, 1, zin) * drift} blurX={(1 - zin) * 18} opacity={zin * (1 - prog(f, FINAL + 4, 4))} y={-900 * out} blurY={out * 40}>
        <Abs style={{left: 100, top: 300}}>
          <div style={{display: 'flex', gap: 14}}>
            {(
              [
                ['¿listo', W_.listo - 1],
                ['para', W_.para3 - 1],
                ['llevar', W_.llevar - 1],
              ] as [string, number][]
            ).map(([w, at]) => (
              <Word key={w} f={f} at={at} size={64} color={C.textSoft}>
                {w}
              </Word>
            ))}
          </div>
          <div style={{display: 'flex', gap: 30, marginTop: 6}}>
            <Word f={f} at={W_.tu3 - 1} size={150} color={C.text}>
              tu
            </Word>
            <Word f={f} at={W_.contenido - 1} size={150} color={C.text}>
              contenido
            </Word>
          </div>
          <div style={{display: 'flex', gap: 14, marginTop: 18}}>
            <Word f={f} at={W_.al - 1} size={64} color={C.textSoft}>
              al
            </Word>
            <Word f={f} at={W_.siguiente - 1} size={64} color={C.textSoft}>
              siguiente
            </Word>
          </div>
        </Abs>
        <Pill f={f} at={W_.nivel2 - 1} text="nivel?" size={130} style={{left: 480, top: 560}} />

        {/* recorte que emerge desde detrás del último escalón */}
        <div style={{position: 'absolute', left: 600, top: base - 600 - 330, width: 480, height: 340, overflow: 'hidden'}}>
          <Img
            src={staticFile('img/camara_manos_bn.png')}
            style={{position: 'absolute', width: 470, left: 10, top: mix(360, 0, emerge), filter: 'drop-shadow(0 16px 24px rgba(10,4,14,.35))'}}
          />
        </div>
        {steps.map((s, i) => {
          const p = E.expoOut(prog(f, s.at, 12));
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: s.x,
                top: base - s.h * p,
                width: s.w,
                height: s.h * p + 40,
                opacity: prog(f, s.at, 3),
                borderRadius: 30,
                background: cardGradient,
                boxShadow: cardShadow,
                overflow: 'hidden',
              }}
            >
              <div style={{position: 'absolute', left: 26, top: 26, ...textStyle(26, 'rgba(255,255,255,.65)', 700)}}>nivel {i + 1}</div>
              <div style={{position: 'absolute', left: 24, top: 60, ...textStyle(52, C.white, 900)}}>{s.label}</div>
            </div>
          );
        })}
        <DashLine f={f} at={W_.siguiente + 2} dur={14} d="M 235 1440 C 300 1300 420 1320 540 1270 S 760 1150 830 1080" len={700} width={4} />
        {/* punta de flecha */}
        <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1} height={1}>
          <path d="M 812 1072 L 842 1072 L 836 1102" stroke={C.text} strokeWidth={5} fill="none" strokeLinecap="round" strokeLinejoin="round" opacity={prog(f, W_.siguiente + 14, 3)} />
        </svg>
      </Cam>

      {/* cierre tipográfico */}
      {f >= W_.hablemos - 3 && (
        <Cam s={mix(1.25, 1, fin(0)) * mix(1, 1.03, prog(f, W_.hablemos, 60))} opacity={prog(f, W_.hablemos - 3, 4)}>
          <Abs style={{left: 0, right: 0, top: 700, display: 'flex', justifyContent: 'center', opacity: fin(2)}}>
            <div style={{padding: '12px 26px', borderRadius: 999, border: `3px solid ${C.text}`, ...textStyle(30, C.text, 800), letterSpacing: '0.04em'}}>EDITOR · MOTION DESIGNER</div>
          </Abs>
          <Abs style={{left: 0, right: 0, top: 800, display: 'flex', justifyContent: 'center'}}>
            <Word f={f} at={W_.hablemos - 3} size={74} color={C.textSoft} dx={0} dy={20}>
              ¿empezamos?
            </Word>
          </Abs>
          <Pill f={f} at={W_.hablemos - 1} text="hablemos." size={160} style={{left: 0, right: 0, top: 900, display: 'flex', justifyContent: 'center'}} />
          {/* botón de contacto */}
          <div
            style={{
              position: 'absolute',
              left: 190,
              top: 1170,
              width: 700,
              height: 140,
              borderRadius: 999,
              background: C.white,
              boxShadow: cardShadow,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 22,
              transform: `scale(${E.softBack(prog(f, W_.hablemos + 8, 10)) * (f >= click ? 1 - 0.06 * Math.sin(Math.PI * prog(f, click, 6)) : 1)})`,
              opacity: prog(f, W_.hablemos + 8, 4),
              overflow: 'hidden',
              ...textStyle(54, C.text, 900),
            }}
          >
            <IconSend size={50} color={C.cardLight} />
            escríbeme hoy
            {f >= click && prog(f, click, 16) < 1 && (
              <div style={{position: 'absolute', left: '70%', top: '50%', width: 900 * prog(f, click, 16), height: 900 * prog(f, click, 16), marginLeft: -450 * prog(f, click, 16), marginTop: -450 * prog(f, click, 16), borderRadius: '50%', background: 'rgba(113,65,129,0.18)', opacity: 1 - prog(f, click, 16)}} />
            )}
          </div>
          {f >= 856 && (
            <Abs style={{left: mix(1000, 700, E.expoInOut(prog(f, 856, 11))), top: mix(1600, 1250, E.expoInOut(prog(f, 856, 11))), transform: `scale(${f >= click && f < click + 5 ? 0.85 : 1})`}}>
              <IconCursor size={90} />
            </Abs>
          )}
          <DashLine f={f} at={W_.hablemos + 14} d="M 540 1330 L 540 1420" len={100} />
          <Abs style={{left: 0, right: 0, top: 1450, display: 'flex', justifyContent: 'center', gap: 14, flexWrap: 'wrap', padding: '0 90px'}}>
            {['edición', 'motion graphics', '3D', 'color', 'sound design'].map((t, i) => (
              <div
                key={t}
                style={{
                  padding: '12px 22px',
                  borderRadius: 16,
                  background: C.white,
                  boxShadow: softShadow,
                  ...textStyle(32, C.text, 800),
                  transform: `scale(${E.softBack(prog(f, W_.hablemos + 16 + i * 3, 9))})`,
                  opacity: prog(f, W_.hablemos + 16 + i * 3, 4),
                }}
              >
                {t}
              </div>
            ))}
          </Abs>
        </Cam>
      )}
    </>
  );
};
