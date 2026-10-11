import React from 'react';
import {C, cardGradient, cardShadow} from '../theme';
import {E, mix, prog, tw} from '../lib/anim';
import {Abs, DashLine, Word, textStyle} from '../components/base';
import {Cam} from '../components/Cam';
import {Camera3D} from '../components/Camera3D';
import {Clip, GraphEditor, TimelineUI} from '../components/ui';
import {W_} from '../cues';

const IN = 160;
const OUT = 351;

const baseClips: Clip[] = [
  {track: 0, x: 0.05, w: 0.22, color: '#8C5C9C', label: 'Título'},
  {track: 0, x: 0.55, w: 0.25, color: '#8C5C9C', label: 'Gráfico'},
  {track: 1, x: 0.0, w: 0.4, color: C.cardLight, label: 'Clip_01'},
  {track: 1, x: 0.4, w: 0.34, color: '#5E3470', label: 'Clip_02'},
  {track: 1, x: 0.74, w: 0.26, color: C.cardLight, label: 'Clip_03'},
  {track: 2, x: 0.0, w: 0.74, color: '#4E6B8C', audio: true},
  {track: 3, x: 0.1, w: 0.9, color: '#3E5A5C', audio: true},
];

// distribuciones alternativas para "edición dinámica" (los clips se reordenan al ritmo)
const shuffles: Clip[][] = [
  baseClips,
  [
    {track: 0, x: 0.12, w: 0.18, color: '#8C5C9C', label: 'Título'},
    {track: 0, x: 0.42, w: 0.3, color: '#8C5C9C', label: 'Gráfico'},
    {track: 1, x: 0.0, w: 0.2, color: C.cardLight, label: 'Clip_01'},
    {track: 1, x: 0.2, w: 0.16, color: '#5E3470', label: 'Clip_02'},
    {track: 1, x: 0.36, w: 0.64, color: C.cardLight, label: 'Clip_03'},
    {track: 2, x: 0.0, w: 0.5, color: '#4E6B8C', audio: true},
    {track: 3, x: 0.0, w: 1.0, color: '#3E5A5C', audio: true},
  ],
  [
    {track: 0, x: 0.0, w: 0.3, color: '#8C5C9C', label: 'Título'},
    {track: 0, x: 0.66, w: 0.22, color: '#8C5C9C', label: 'Gráfico'},
    {track: 1, x: 0.0, w: 0.12, color: C.cardLight, label: 'Clip_01'},
    {track: 1, x: 0.12, w: 0.5, color: '#5E3470', label: 'Clip_02'},
    {track: 1, x: 0.62, w: 0.38, color: C.cardLight, label: 'Clip_03'},
    {track: 2, x: 0.2, w: 0.8, color: '#4E6B8C', audio: true},
    {track: 3, x: 0.0, w: 0.7, color: '#3E5A5C', audio: true},
  ],
];

const lerpClips = (a: Clip[], b: Clip[], t: number): Clip[] => a.map((c, i) => ({...c, x: mix(c.x, b[i].x, t), w: mix(c.w, b[i].w, t)}));

const previews = ['img/estudio.jpg', 'img/bailarina.jpg', 'img/paisaje.jpg', 'img/claqueta.jpg'];

/**
 * 160–366 · Monitor de edición (objeto compartido entre "simples cortes" y la lista de servicios).
 * Entra con zoom-through, sube a la parte superior y su pantalla demuestra cada servicio de la lista.
 */
export const S2Monitor: React.FC<{f: number}> = ({f}) => {
  // entrada zoom-through (4–6 frames) y salida en barrido a la izquierda
  const zin = E.expoOut(prog(f, IN, 8));
  const swipe = (fr: number) => -1300 * E.expoIn(prog(fr, OUT, 8));
  const sx = swipe(f);
  const sv = swipe(f + 0.5) - swipe(f - 0.5);
  const camS = mix(1.3, 1, zin) * mix(1, 1.03, prog(f, IN, 200));

  // monitor: centrado → sube (reposición de 6 frames, estilo.md §5)
  const up = E.quintOut(prog(f, 250, 10));
  const monW = 920;
  const monH = 620;
  const monX = 80;
  const monY = mix(960, 300, up);
  const monScale = mix(1, 0.98, up);

  // modo de pantalla
  const mode = f < W_.motion - 1 ? (f < W_.edicion - 1 ? 'cortes' : 'dinamica') : f < W_.animaciones - 1 ? 'motion' : 'tres';
  const modeStart = mode === 'cortes' ? IN : mode === 'dinamica' ? W_.edicion - 1 : mode === 'motion' ? W_.motion - 1 : W_.animaciones - 1;
  const swap = E.expoOut(prog(f, modeStart, 6));

  // timeline: cortes con cuchilla en "simples" y "cortes"
  let clips = baseClips;
  const cut1 = W_.simples;
  const cut2 = W_.cortes;
  if (f >= cut1) {
    const g = E.expoOut(prog(f, cut1, 6)) * 0.012;
    clips = clips.map((c) => (c.track === 1 && c.x < 0.3 ? {...c, w: c.w - 0.12} : c.track === 1 && c.x >= 0.3 && c.x < 0.35 ? c : c));
    clips = [...clips, {track: 1, x: 0.28 + g, w: 0.12 - g, color: '#9B6BAA', label: 'B'}];
  }
  if (f >= cut2) {
    const g = E.expoOut(prog(f, cut2, 6)) * 0.012;
    clips = clips.map((c) => (c.label === 'Clip_02' ? {...c, w: 0.17} : c));
    clips = [...clips, {track: 1, x: 0.57 + g, w: 0.17 - g, color: '#9B6BAA', label: 'C'}];
  }
  let preview = 'img/estudio.jpg';
  let pZoom = 1.05;
  if (mode === 'dinamica') {
    const step = Math.floor((f - (W_.edicion - 1)) / 5);
    const idx = Math.min(2, Math.floor((f - (W_.edicion - 1)) / 11));
    const t = E.expoOut(prog(f, W_.edicion - 1 + idx * 11, 5));
    clips = lerpClips(shuffles[idx], shuffles[(idx + 1) % 3], t);
    preview = previews[step % previews.length];
    pZoom = 1.12 - 0.07 * E.expoOut(((f - (W_.edicion - 1)) % 5) / 5);
  }
  const playhead = mode === 'cortes' ? tw(f, IN + 4, 90, 0.02, 0.62, E.cubicInOut) : ((f - 250) / 60) % 1;
  const secs = Math.floor(f / 30);
  const timecode = `00:00:${String(secs).padStart(2, '0')}:${String(f % 30).padStart(2, '0')}`;

  // titular "necesitas algo más que simples cortes" (+ tachado)
  const headOut = E.expoIn(prog(f, 248, 8));
  const strike = E.expoOut(prog(f, 243, 7));

  // lista de servicios
  const items: [string, number][] = [
    ['edición dinámica', W_.edicion - 1],
    ['motion graphics', W_.motion - 1],
    ['animaciones 3D', W_.animaciones - 1],
  ];
  const listX = 140;
  const listY0 = 1020;
  const step = 132;

  // cámara 3D que sale de la pantalla
  const c3 = E.expoOut(prog(f, W_.animaciones + 1, 14));

  return (
    <Cam s={camS} x={sx} blurX={Math.abs(sv) * 0.12 + (1 - zin) * 18} opacity={zin}>
      {/* titular */}
      <Abs style={{left: 100, top: 470, opacity: 1 - headOut, transform: `translateY(${-120 * headOut}px)`, filter: headOut > 0 ? `blur(${headOut * 16}px)` : undefined}}>
        <div style={{display: 'flex', gap: 16}}>
          <Word f={f} at={W_.entonces - 1} size={56} color={C.textSoft}>
            entonces,
          </Word>
          <Word f={f} at={W_.necesitas2 - 1} size={56} color={C.textSoft}>
            necesitas
          </Word>
        </div>
        <div style={{display: 'flex', gap: 16, marginTop: 14}}>
          <Word f={f} at={W_.algo - 1} size={56} color={C.textSoft}>
            algo
          </Word>
          <Word f={f} at={W_.mas - 1} size={56} color={C.text}>
            más
          </Word>
          <Word f={f} at={W_.que2 - 1} size={56} color={C.textSoft}>
            que
          </Word>
        </div>
        <div style={{position: 'relative', display: 'flex', gap: 26, marginTop: 6}}>
          <Word f={f} at={W_.simples - 1} size={128} color={C.text}>
            simples
          </Word>
          <Word f={f} at={W_.cortes - 1} size={128} color={C.text}>
            cortes
          </Word>
          <div style={{position: 'absolute', left: -10, top: 66, height: 15, width: 760 * strike, background: C.cardLight, borderRadius: 8, transform: 'rotate(-3deg)', boxShadow: '0 6px 14px rgba(20,8,26,.25)'}} />
        </div>
      </Abs>

      {/* monitor (tarjeta morada con pantalla) */}
      <div style={{position: 'absolute', left: monX, top: monY, width: monW, height: monH, transform: `scale(${monScale})`}}>
        <div style={{position: 'absolute', inset: 0, borderRadius: 30, background: cardGradient, boxShadow: cardShadow}} />
        <div style={{position: 'absolute', inset: 22, borderRadius: 16, overflow: 'hidden'}}>
          <div style={{position: 'absolute', inset: 0, opacity: swap, transform: `translateY(${(1 - swap) * 40}px)`}}>
            {mode === 'cortes' || mode === 'dinamica' ? (
              <TimelineUI
                f={f}
                w={monW - 44}
                h={monH - 44}
                clips={clips}
                playhead={playhead}
                previewImg={preview}
                previewZoom={pZoom}
                previewFilter="saturate(0.85)"
                cutFlash={[
                  {x: 0.28, at: cut1},
                  {x: 0.57, at: cut2},
                ]}
                timecode={timecode}
              />
            ) : mode === 'motion' ? (
              <GraphEditor f={f} at={W_.motion - 1} w={monW - 44} h={monH - 44} />
            ) : (
              <PerspectiveGrid f={f} w={monW - 44} h={monH - 44} />
            )}
          </div>
        </div>
        {/* pie del monitor */}
        <div style={{position: 'absolute', left: monW / 2 - 70, top: monH - 4, width: 140, height: 40, background: `linear-gradient(${C.cardDark}, ${C.card})`, clipPath: 'polygon(20% 0, 80% 0, 100% 100%, 0 100%)'}} />
      </div>

      {/* conector vertical + lista */}
      <svg style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} width={1} height={1}>
        {items.map(([, at], i) => {
          const y1 = i === 0 ? 930 : listY0 + (i - 1) * step;
          const y2 = listY0 + i * step;
          const p = E.quintOut(prog(f, at - 4, 6));
          return <line key={i} x1={listX} y1={y1} x2={listX} y2={mix(y1, y2, p)} stroke={C.text} strokeWidth={4} opacity={p > 0 ? 1 : 0} />;
        })}
      </svg>
      {items.map(([t, at], i) => {
        const s = E.softBack(prog(f, at, 8));
        return (
          <React.Fragment key={t}>
            <div style={{position: 'absolute', left: listX - 13, top: listY0 + i * step - 13, width: 26, height: 26, borderRadius: 13, background: C.text, transform: `scale(${s})`}} />
            <Abs style={{left: listX + 40, top: listY0 + i * step - 42}}>
              <Word f={f} at={at} size={82} color={C.text}>
                {t}
              </Word>
            </Abs>
          </React.Fragment>
        );
      })}

      {/* cámara 3D que emerge de la pantalla */}
      {f >= W_.animaciones - 2 && (
        <div
          style={{
            position: 'absolute',
            left: mix(260, 360, c3),
            top: mix(330, 1270, c3),
            width: 700,
            height: 620,
            transform: `scale(${mix(0.35, 1, c3)})`,
            opacity: Math.min(1, c3 * 3),
          }}
        >
          <div style={{position: 'absolute', left: 170, top: 500, width: 360, height: 60, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(30,10,40,0.35), transparent 70%)', filter: 'blur(6px)'}} />
          <Camera3D w={700} h={620} scale={1.12} ry={tw(f, W_.animaciones, 40, -1.6, 0.55, E.expoOut) + (f - W_.animaciones) * 0.004} rx={0.22} rz={-0.06} />
        </div>
      )}
      <DashLine f={f} at={W_.n3d - 2} d="M 880 930 C 980 1050 960 1250 900 1400" len={520} />
    </Cam>
  );
};

/** Rejilla en perspectiva (vista 3D) dentro de la pantalla: líneas de fuga hacia el horizonte. */
const PerspectiveGrid: React.FC<{f: number; w: number; h: number}> = ({f, w, h}) => {
  const hz = h * 0.4;
  const vx = w / 2;
  const scroll = (f * 0.04) % 1;
  return (
    <div style={{position: 'absolute', inset: 0, background: C.screen, overflow: 'hidden', borderRadius: 16}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 40, background: '#24162B', display: 'flex', alignItems: 'center', padding: '0 18px'}}>
        <span style={{...textStyle(17, C.white, 600), fontStyle: 'normal', letterSpacing: '0.02em'}}>Vista 3D · Cámara activa · 35 mm</span>
      </div>
      <svg width={w} height={h} style={{position: 'absolute', left: 0, top: 0}}>
        <defs>
          <linearGradient id="fadeGrid" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#7B5A88" stopOpacity="0" />
            <stop offset="1" stopColor="#9C77AA" stopOpacity="0.9" />
          </linearGradient>
        </defs>
        {Array.from({length: 23}).map((_, i) => {
          const x = vx + (i - 11) * 120;
          return <line key={'v' + i} x1={vx + (i - 11) * 6} y1={hz} x2={x} y2={h} stroke="url(#fadeGrid)" strokeWidth={2} />;
        })}
        {Array.from({length: 12}).map((_, i) => {
          const t = (i + scroll) / 12;
          const y = hz + (h - hz) * t * t;
          return <line key={'h' + i} x1={0} y1={y} x2={w} y2={y} stroke="#9C77AA" strokeOpacity={0.15 + 0.7 * t} strokeWidth={2} />;
        })}
        <line x1={0} y1={hz} x2={w} y2={hz} stroke="#C9A8D4" strokeOpacity={0.5} strokeWidth={2} />
      </svg>
    </div>
  );
};
