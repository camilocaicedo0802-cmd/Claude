import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {TitleDef, TitleLine} from '../data';
import {clamp, easeInOut, easeOut} from '../helpers';
import {C, OUTFIT} from '../theme';

const wordStyle = (color: TitleLine['color']): React.CSSProperties => {
  switch (color) {
    case 'purple':
      // degradado de la "W" del logo
      return {
        backgroundImage: C.purpleGrad,
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        color: 'transparent',
        filter: `drop-shadow(0 3px 0 ${C.purpleShadow}) drop-shadow(0 0 16px ${C.purpleGlow})`,
      };
    case 'chrome':
      return {
        backgroundImage: C.chrome,
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        color: 'transparent',
        filter: 'drop-shadow(0 0 10px rgba(255,255,255,0.35)) drop-shadow(0 4px 8px rgba(0,0,0,0.35))',
      };
    default:
      return {color: C.white, textShadow: '0 0 14px rgba(255,255,255,0.55), 0 0 40px rgba(255,255,255,0.25), 0 4px 10px rgba(0,0,0,0.25)'};
  }
};

/** Título grande de dos tonos que entra palabra a palabra (estilo.md §3). */
export const Title: React.FC<{t: TitleDef}> = ({t}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const endF = t.end * fps;
  const exit = interpolate(frame, [endF - 5, endF], [0, 1], {...clamp, easing: easeInOut});
  const drift = interpolate(frame, [t.start * fps, endF], [1, 1.04], clamp);
  if (frame < t.start * fps - 2 || frame > endF + 1) return null;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', perspective: 1200}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: t.y,
          translate: '0 -50%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          scale: String(drift),
          rotate: t.tilt ? `x ${t.tilt}deg` : undefined,
          opacity: 1 - exit,
          filter: exit > 0 ? `blur(${16 * exit}px)` : undefined,
        }}
      >
        {t.lines.map((line, li) => (
          <div
            key={li}
            style={{
              display: 'flex',
              gap: `${line.size * 0.2}px`,
              fontFamily: OUTFIT,
              fontWeight: line.upper ? 900 : 800,
              fontSize: line.size,
              lineHeight: 0.88,
              letterSpacing: line.upper ? '-0.03em' : '-0.05em',
              textTransform: line.upper ? 'uppercase' : 'none',
              whiteSpace: 'nowrap',
              marginTop: li === 0 ? 0 : -line.size * 0.04,
            }}
          >
            {line.words.map((w, wi) => {
              const local = frame - w.at * fps;
              const p = interpolate(local, [0, 6], [0, 1], {...clamp, easing: easeOut});
              return (
                <span
                  key={wi}
                  style={{
                    ...wordStyle(line.color),
                    display: 'inline-block',
                    opacity: p,
                    scale: String(interpolate(p, [0, 1], [1.25, 1])),
                    translate: `0 ${interpolate(p, [0, 1], [40, 0])}px`,
                    filter: p < 1 ? `blur(${18 * (1 - p)}px) ${wordStyle(line.color).filter ?? ''}` : wordStyle(line.color).filter,
                  }}
                >
                  {w.text}
                </span>
              );
            })}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
