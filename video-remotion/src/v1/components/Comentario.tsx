import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES} from '../data';
import {clamp, easeInOut, easeOut} from '../helpers';
import {C, OUTFIT} from '../theme';

/** Caja de comentario escribiendo "AYUDA" (llamado a la acción). */
export const Comentario: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sc = SCENES.comentario;
  const s = sc.start * fps;
  const e = sc.end * fps;
  if (frame < s || frame >= e) return null;
  const pin = interpolate(frame, [s, s + 10], [0, 1], {...clamp, easing: easeOut});
  const pout = interpolate(frame, [e - 5, e], [0, 1], {...clamp, easing: easeInOut});
  const n = Math.max(0, Math.min(5, Math.floor((frame / fps - sc.typeAt) / 0.09) + 1));
  const typed = 'AYUDA'.slice(0, frame / fps >= sc.typeAt ? n : 0);
  const done = n >= 5;
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <div
        style={{
          position: 'absolute',
          left: 70,
          right: 70,
          top: 1560,
          height: 120,
          borderRadius: 60,
          background: 'rgba(255,255,255,0.96)',
          boxShadow: '0 20px 60px rgba(0,0,0,0.45)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 18px',
          gap: 22,
          opacity: pin * (1 - pout),
          translate: `0 ${interpolate(pin, [0, 1], [160, 0]) + 80 * pout}px`,
        }}
      >
        <div style={{width: 84, height: 84, borderRadius: 42, background: `conic-gradient(${C.purpleTop}, #FFFFFF, ${C.purpleBottom}, ${C.purpleTop})`, padding: 4}}>
          <div style={{width: '100%', height: '100%', borderRadius: 40, background: '#d9d9d9', border: '3px solid #fff'}} />
        </div>
        <div style={{flex: 1, fontSize: 44, fontWeight: typed ? 800 : 500, color: typed ? '#111' : '#9a9a9a', letterSpacing: typed ? '0.02em' : 0}}>
          {typed || 'Añade un comentario…'}
          {typed && !done ? <span style={{color: C.purple}}>|</span> : null}
        </div>
        <div style={{fontSize: 34, fontWeight: 700, color: done ? C.purple : '#c9c9c9', paddingRight: 24}}>Publicar</div>
      </div>
    </AbsoluteFill>
  );
};
