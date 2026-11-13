import {Video} from '@remotion/media';
import {AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {GridBg} from '../engine/GridBg';
import {clamp, easeInOut, easeOut, sec} from '../engine/helpers';
import {C, OUTFIT} from '../v1/theme';
import {SC} from './data';

/** Pantalla partida: arriba "las que venden" (color, cobro con tarjeta), abajo "las que no venden" (B/N, negocio vacío). */
export const Versus: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = sec(SC.versus.start, fps);
  const e = sec(SC.versus.end, fps);
  if (frame < s || frame >= e) return null;
  const pin = interpolate(frame, [s, s + 5], [0, 1], clamp);
  const out = interpolate(frame, [e - 5, e], [0, 1], clamp);
  const panel = (enter: number, at: number, dir: number, top: number, src: string, trim: number, label: string, ok: boolean) => {
    const p = interpolate(frame - enter, [0, 8], [0, 1], {...clamp, easing: easeOut});
    const lp = interpolate(frame - at * fps, [0, 6], [0, 1], {...clamp, easing: easeOut});
    const lit = interpolate(frame - at * fps, [0, 4], [0, 1], clamp);
    return (
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top,
          height: 760,
          border: `8px solid ${ok ? '#FFFFFF' : '#BDBDBD'}`,
          borderRadius: 18,
          overflow: 'hidden',
          boxShadow: ok ? `0 0 50px ${C.purpleGlow}, 0 20px 50px rgba(0,0,0,0.6)` : '0 20px 50px rgba(0,0,0,0.6)',
          translate: `${dir * (1 - p) * 1100}px 0`,
          rotate: `${dir * (1 - p) * 4}deg`,
          filter: `${ok ? `saturate(${0.3 + 0.7 * lit}) brightness(${0.75 + 0.25 * lit})` : `grayscale(1) contrast(1.1) brightness(${0.85 - 0.15 * lit})`} ${p < 1 ? `blur(${10 * (1 - p)}px)` : ''}`,
        }}
      >
        <Sequence from={enter} layout="none">
          <Video src={staticFile(src)} muted trimBefore={sec(trim, fps)} objectFit="cover" style={{width: '100%', height: '100%'}} />
        </Sequence>
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 260, background: 'linear-gradient(transparent, rgba(0,0,0,0.75))'}} />
        <div style={{position: 'absolute', left: 40, bottom: 34, display: 'flex', alignItems: 'center', gap: 22, fontFamily: OUTFIT}}>
          <div
            style={{
              width: 84,
              height: 84,
              borderRadius: 42,
              display: 'grid',
              placeItems: 'center',
              fontSize: 54,
              fontWeight: 900,
              color: '#fff',
              background: ok ? C.purpleGrad : '#5a5a5a',
              boxShadow: ok ? `0 0 26px ${C.purpleGlow}` : 'none',
              scale: String(interpolate(frame - at * fps, [0, 5, 8], [0, 1.2, 1], clamp)),
            }}
          >
            {ok ? '✓' : '✕'}
          </div>
          <span
            style={{
              fontSize: 78,
              fontWeight: 800,
              letterSpacing: '-0.05em',
              color: '#FFFFFF',
              padding: '6px 28px 12px',
              borderRadius: 20,
              background: ok ? C.purpleGrad : 'rgba(40,40,40,0.9)',
              boxShadow: ok ? `0 6px 0 ${C.purpleShadow}, 0 0 30px ${C.purpleGlow}` : '0 6px 0 #111',
              clipPath: `inset(0 ${100 - 100 * lp}% 0 0 round 20px)`,
            }}
          >
            {label}
          </span>
        </div>
      </div>
    );
  };
  return (
    <AbsoluteFill style={{opacity: pin * (1 - out)}}>
      <GridBg />
      {panel(s, SC.versus.top, -1, 140, 'broll/pago_tarjeta.mp4', 1.5, 'sí venden', true)}
      {panel(s + 6, SC.versus.bottom, 1, 1000, 'broll/sin_ventas.mp4', 0.5, 'no venden', false)}
    </AbsoluteFill>
  );
};

/** Móvil con un perfil abandonado: "ni siquiera suben ninguna publicación". */
export const PerfilVacio: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = sec(SC.vacio.start, fps);
  const e = sec(SC.vacio.end, fps);
  if (frame < s || frame >= e) return null;
  const pin = interpolate(frame, [s, s + 12], [0, 1], {...clamp, easing: easeOut});
  const pout = interpolate(frame, [e - 6, e], [0, 1], {...clamp, easing: easeInOut});
  const pw = 600;
  return (
    <AbsoluteFill style={{perspective: 1600}}>
      <div
        style={{
          position: 'absolute',
          left: (1080 - pw) / 2,
          top: 600,
          width: pw,
          height: 1220,
          borderRadius: 78,
          background: '#0E0E0E',
          padding: 18,
          boxShadow: '0 40px 90px rgba(0,0,0,0.7), inset 0 0 0 3px #2b2b2b',
          translate: `0 ${interpolate(pin, [0, 1], [900, 0]) + 200 * pout}px`,
          rotate: `y ${interpolate(pin, [0, 1], [18, 6])}deg`,
          opacity: 1 - pout,
          fontFamily: OUTFIT,
        }}
      >
        <div style={{width: '100%', height: '100%', borderRadius: 62, overflow: 'hidden', background: '#FFFFFF', position: 'relative'}}>
          <div style={{height: 70, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', fontWeight: 600, fontSize: 26, color: '#111'}}>minegocio</div>
          <div style={{display: 'flex', alignItems: 'center', gap: 34, padding: '26px 30px'}}>
            <div style={{width: 120, height: 120, borderRadius: 60, background: '#e6e6e6', border: '4px solid #fff', boxShadow: '0 0 0 3px #ddd'}} />
            {[['0', 'publicaciones'], ['14', 'seguidores'], ['3', 'seguidos']].map(([n, l]) => (
              <div key={l} style={{textAlign: 'center', color: '#111'}}>
                <div style={{fontWeight: 800, fontSize: 30}}>{n}</div>
                <div style={{fontWeight: 500, fontSize: 18, color: '#666'}}>{l}</div>
              </div>
            ))}
          </div>
          <div style={{padding: '0 30px 20px'}}>
            <div style={{height: 16, width: 180, background: '#e4e4e4', borderRadius: 8, marginBottom: 10}} />
            <div style={{height: 14, width: 260, background: '#eeeeee', borderRadius: 7}} />
          </div>
          <div style={{borderTop: '1px solid #eee', display: 'grid', placeItems: 'center', paddingTop: 120, color: '#8a8a8a'}}>
            <div style={{width: 120, height: 120, borderRadius: 60, border: '4px solid #bdbdbd', display: 'grid', placeItems: 'center', fontSize: 56}}>📷</div>
            <div style={{marginTop: 26, fontSize: 34, fontWeight: 800, color: '#222'}}>Aún no hay publicaciones</div>
            <div style={{marginTop: 10, fontSize: 22}}>Última actividad: hace 8 meses</div>
          </div>
          <div style={{position: 'absolute', top: 14, left: '50%', translate: '-50% 0', width: 150, height: 34, borderRadius: 17, background: '#0E0E0E'}} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Lista de lo que hace un equipo de marketing; se marca "Estrategia" al decirlo. */
export const Checklist: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = sec(SC.checklist.start, fps);
  const e = sec(SC.checklist.end, fps);
  if (frame < s || frame >= e) return null;
  const pin = interpolate(frame, [s, s + 5], [0, 1], clamp);
  const out = interpolate(frame, [e - 5, e], [0, 1], clamp);
  return (
    <AbsoluteFill style={{opacity: pin * (1 - out), fontFamily: OUTFIT}}>
      <GridBg />
      <div style={{position: 'absolute', left: 0, right: 0, top: 280, textAlign: 'center', fontSize: 64, fontWeight: 800, letterSpacing: '-0.04em', color: '#fff', textShadow: '0 0 18px rgba(255,255,255,0.5)'}}>
        un equipo que te ayuda con:
      </div>
      {SC.checklist.items.map((it, i) => {
        const appear = interpolate(frame - s - 3 - i * 3, [0, 6], [0, 1], {...clamp, easing: easeOut});
        const checked = frame >= it.at * fps;
        const pop = interpolate(frame - it.at * fps, [0, 4, 8], [0, 1.25, 1], clamp);
        return (
          <div
            key={it.t}
            style={{
              position: 'absolute',
              left: 110,
              right: 110,
              top: 520 + i * 230,
              height: 180,
              borderRadius: 28,
              background: checked ? 'rgba(150,1,253,0.18)' : 'rgba(255,255,255,0.06)',
              border: `3px solid ${checked ? C.purpleTop : 'rgba(255,255,255,0.18)'}`,
              boxShadow: checked ? `0 0 40px ${C.purpleGlow}` : 'none',
              display: 'flex',
              alignItems: 'center',
              gap: 36,
              padding: '0 40px',
              opacity: appear,
              translate: `${(1 - appear) * (i % 2 ? 120 : -120)}px 0`,
              filter: appear < 1 ? `blur(${8 * (1 - appear)}px)` : undefined,
            }}
          >
            <div
              style={{
                width: 96,
                height: 96,
                borderRadius: 48,
                border: `4px solid ${checked ? 'transparent' : 'rgba(255,255,255,0.35)'}`,
                background: checked ? C.purpleGrad : 'transparent',
                display: 'grid',
                placeItems: 'center',
                fontSize: 58,
                fontWeight: 900,
                color: '#fff',
                scale: checked ? String(pop) : '1',
              }}
            >
              {checked ? '✓' : ''}
            </div>
            <span style={{fontSize: 66, fontWeight: 800, letterSpacing: '-0.04em', color: checked ? '#fff' : 'rgba(255,255,255,0.55)'}}>{it.t}</span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Encuesta tipo historia encima de la cabeza: "¿tu negocio cuál es?" → se marca "SÍ VENDE". */
export const Encuesta: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = sec(SC.encuesta.start, fps);
  const e = sec(SC.encuesta.end, fps);
  if (frame < s || frame >= e) return null;
  const pin = interpolate(frame, [s, s + 9], [0, 1], {...clamp, easing: easeOut});
  const pout = interpolate(frame, [e - 5, e], [0, 1], clamp);
  const optIn = (at: number) => interpolate(frame - at * fps, [-4, 4], [0, 1], {...clamp, easing: easeOut});
  const voted = interpolate(frame - (SC.encuesta.si + 0.12) * fps, [0, 7], [0, 1], {...clamp, easing: easeInOut});
  const opt = (label: string, at: number, pct: number, mine: boolean) => {
    const p = optIn(at);
    return (
      <div style={{position: 'relative', height: 108, borderRadius: 54, background: '#F1F1F1', overflow: 'hidden', opacity: p, translate: `0 ${(1 - p) * 20}px`, marginTop: 22}}>
        <div style={{position: 'absolute', inset: 0, width: `${voted * pct}%`, background: mine ? C.purpleGrad : '#CFCFCF'}} />
        <div style={{position: 'relative', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 40px', fontSize: 44, fontWeight: 800, color: mine && voted > 0.5 ? '#fff' : '#222'}}>
          <span>{label}</span>
          <span style={{opacity: voted}}>{Math.round(voted * pct)}%</span>
        </div>
      </div>
    );
  };
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <div
        style={{
          position: 'absolute',
          left: 110,
          right: 110,
          top: 110,
          borderRadius: 40,
          background: '#FFFFFF',
          padding: '36px 40px 44px',
          boxShadow: '0 30px 80px rgba(0,0,0,0.5)',
          opacity: pin * (1 - pout),
          scale: String(interpolate(pin, [0, 1], [0.7, 1]) * (1 + 0.03 * Math.sin((frame - s) / 10))),
          rotate: `${interpolate(pin, [0, 1], [-6, -2])}deg`,
        }}
      >
        <div style={{textAlign: 'center', fontSize: 50, fontWeight: 800, letterSpacing: '-0.03em', color: '#111'}}>¿Tu negocio cuál es?</div>
        {opt('NO VENDE', SC.encuesta.no, 8, false)}
        {opt('SÍ VENDE', SC.encuesta.si, 92, true)}
      </div>
    </AbsoluteFill>
  );
};
