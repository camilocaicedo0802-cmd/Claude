import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {TitleDef, TitleLine} from './types';
import {clamp, easeInOut, easeOut} from './helpers';
import {C, OUTFIT} from '../v1/theme';
import {segmentAt, useSpec} from './spec';
import {segmentScaleAt} from './Talking';

// ------------------------------------------------------------------
// Títulos grandes estudiados fotograma a fotograma en la referencia:
// - entrada "fantasma": cada palabra pasa de transparente+desenfocada a nítida
//   en 5 fotogramas, con una estela (2 copias que se quedan atrás y se apagan);
// - brillo (bloom) en el blanco, volumen 3D en morado y cromado;
// - líneas escalonadas (no centradas una sobre otra);
// - deriva lenta mientras están en pantalla;
// - salida con destello: sube el brillo + desenfoque en 4 fotogramas;
// - en planos hablados se mueven con el zoom de cámara y van detrás de la persona.
// ------------------------------------------------------------------

const extrude = (base: string, depth: number) =>
  Array.from({length: depth}, (_, i) => `drop-shadow(0 ${i < 1 ? 1 : 1}px 0 ${base})`).join(' ');

const wordStyle = (color: TitleLine['color']): React.CSSProperties => {
  switch (color) {
    case 'purple':
      return {
        backgroundImage: C.purpleGrad,
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        color: 'transparent',
        filter: `${extrude(C.purpleShadow, 5)} drop-shadow(0 0 2px rgba(255,255,255,0.35)) drop-shadow(0 0 22px ${C.purpleGlow}) drop-shadow(0 10px 18px rgba(0,0,0,0.45))`,
      };
    case 'chrome':
      return {
        backgroundImage: C.chrome,
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        color: 'transparent',
        filter: `${extrude('#7d7d86', 5)} drop-shadow(0 0 14px rgba(255,255,255,0.45)) drop-shadow(0 10px 18px rgba(0,0,0,0.45))`,
      };
    default:
      return {
        color: C.white,
        textShadow:
          '0 0 4px rgba(255,255,255,0.95), 0 0 18px rgba(255,255,255,0.6), 0 0 42px rgba(183,1,252,0.45), 0 6px 18px rgba(0,0,0,0.35)',
      };
  }
};

const Word: React.FC<{text: string; at: number; color: TitleLine['color']; dir: number}> = ({text, at, color, dir}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - at * fps;
  const p = interpolate(local, [0, 5], [0, 1], {...clamp, easing: easeOut});
  const st = wordStyle(color);
  const ghost = (k: number, op: number) => {
    const q = interpolate(local, [0, 5 + k * 2], [0, 1], {...clamp, easing: easeOut});
    if (q >= 1 || local < 0) return null;
    return (
      <span
        aria-hidden
        style={{
          ...st,
          position: 'absolute',
          left: 0,
          top: 0,
          opacity: op * q * (1 - q) * 4,
          translate: `${dir * (1 - q) * (40 + k * 30)}px ${(1 - q) * 10}px`,
          filter: `blur(${6 + k * 4}px) ${st.filter ?? ''}`,
        }}
      >
        {text}
      </span>
    );
  };
  return (
    <span style={{position: 'relative', display: 'inline-block'}}>
      {ghost(1, 0.45)}
      {ghost(2, 0.25)}
      <span
        style={{
          ...st,
          display: 'inline-block',
          opacity: p,
          scale: String(interpolate(p, [0, 1], [1.08, 1])),
          translate: `${dir * (1 - p) * 26}px ${(1 - p) * 14}px`,
          filter: p < 1 ? `blur(${16 * (1 - p)}px) ${st.filter ?? ''}` : st.filter,
        }}
      >
        {text}
      </span>
    </span>
  );
};

/** Título grande de dos tonos (estilo.md §3 + correcciones §10). */
export const Title: React.FC<{t: TitleDef}> = ({t}) => {
  const spec = useSpec();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const startF = t.start * fps;
  const endF = t.end * fps;
  if (frame < startF - 2 || frame > endF + 1) return null;
  const exit = interpolate(frame, [endF - 4, endF], [0, 1], {...clamp, easing: easeInOut});
  const drift = interpolate(frame, [startF, endF], [1, 1.05], clamp);
  const float = Math.sin((frame - startF) / 14) * 5;
  // en planos hablados el título "vive" en la escena: escala con el zoom de cámara
  const cam = t.scene ? segmentScaleAt(spec, frame) : 1;
  // anclaje a la cabeza: el bloque queda encima y solo su parte baja pasa detrás de él
  let y = typeof t.y === 'number' ? t.y : 500;
  if (t.y === 'head') {
    const seg = segmentAt(spec, Math.round(startF));
    const top = seg && spec.faces[seg.idx] ? spec.faces[seg.idx][1] : 600;
    const blockH = t.lines.reduce((a, l) => a + l.size * 0.9, 0);
    y = Math.max(150 + blockH / 2, top + (t.overlap ?? 80) - blockH / 2);
  }
  return (
    <AbsoluteFill style={{pointerEvents: 'none', perspective: 1200, scale: String(cam), transformOrigin: '50% 42%'}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: y + float,
          translate: '0 -50%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          scale: String(drift * (1 + exit * 0.06)),
          rotate: t.tilt ? `x ${t.tilt}deg` : undefined,
          opacity: 1 - exit,
          filter: exit > 0 ? `blur(${12 * exit}px) brightness(${1 + 1.4 * exit})` : undefined,
        }}
      >
        {t.lines.map((line, li) => (
          <div
            key={li}
            style={{
              display: 'flex',
              gap: `${line.size * 0.18}px`,
              fontFamily: OUTFIT,
              fontWeight: line.upper ? 900 : 800,
              fontSize: line.size,
              lineHeight: 0.9,
              letterSpacing: line.upper ? '-0.03em' : '-0.05em',
              textTransform: line.upper ? 'uppercase' : 'none',
              whiteSpace: 'nowrap',
              marginTop: li === 0 ? 0 : -line.size * 0.06,
              translate: `${line.dx ?? (li % 2 ? 50 : -30)}px 0`,
            }}
          >
            {line.words.map((w, wi) => (
              <Word key={wi} text={w.text} at={w.at} color={line.color} dir={li % 2 ? 1 : -1} />
            ))}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
