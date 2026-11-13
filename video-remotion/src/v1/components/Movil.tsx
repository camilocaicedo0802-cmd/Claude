import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES} from '../data';
import {clamp, easeInOut, easeOut} from '../helpers';
import {C, OUTFIT} from '../theme';

const POSTS = Array.from({length: 15}, (_, i) => `img/collage/t${String((i % 16) + 1).padStart(2, '0')}.jpg`);

/** Móvil con un perfil de negocio genérico que se desplaza: "miran tus redes sociales". */
export const Movil: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = SCENES.movil.start * fps;
  const e = SCENES.movil.end * fps;
  const pin = interpolate(frame, [s, s + 12], [0, 1], {...clamp, easing: easeOut});
  const pout = interpolate(frame, [e - 6, e], [0, 1], {...clamp, easing: easeInOut});
  const scroll = interpolate(frame, [s + 8, e], [0, 520], {...clamp, easing: easeInOut});
  if (frame < s - 1 || frame > e + 1) return null;
  const pw = 600;
  const ph = 1220;
  return (
    <AbsoluteFill style={{perspective: 1600}}>
      <div
        style={{
          position: 'absolute',
          left: (1080 - pw) / 2,
          top: 640,
          width: pw,
          height: ph,
          borderRadius: 78,
          background: '#0E0E0E',
          padding: 18,
          boxShadow: '0 40px 90px rgba(0,0,0,0.7), inset 0 0 0 3px #2b2b2b',
          translate: `0 ${interpolate(pin, [0, 1], [900, 0]) + 200 * pout}px`,
          rotate: `y ${interpolate(pin, [0, 1], [-18, -6])}deg`,
          opacity: 1 - pout,
          filter: pout > 0 ? `blur(${12 * pout}px)` : undefined,
        }}
      >
        <div style={{width: '100%', height: '100%', borderRadius: 62, overflow: 'hidden', background: '#FFFFFF', position: 'relative', fontFamily: OUTFIT}}>
          <div style={{translate: `0 ${-scroll}px`}}>
            <div style={{height: 70, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', fontWeight: 600, fontSize: 26, color: '#111'}}>tunegocio</div>
            <div style={{display: 'flex', alignItems: 'center', gap: 34, padding: '26px 30px'}}>
              <div style={{width: 120, height: 120, borderRadius: 60, background: 'linear-gradient(135deg,#d9d9d9,#a9a9a9)', border: '4px solid #fff', boxShadow: '0 0 0 3px #ddd'}} />
              {[['12', 'publicaciones'], ['58', 'seguidores'], ['31', 'seguidos']].map(([n, l]) => (
                <div key={l} style={{textAlign: 'center', color: '#111'}}>
                  <div style={{fontWeight: 800, fontSize: 30}}>{n}</div>
                  <div style={{fontWeight: 500, fontSize: 18, color: '#666'}}>{l}</div>
                </div>
              ))}
            </div>
            <div style={{padding: '0 30px 20px'}}>
              <div style={{height: 16, width: 220, background: '#e4e4e4', borderRadius: 8, marginBottom: 10}} />
              <div style={{height: 14, width: 360, background: '#eeeeee', borderRadius: 7, marginBottom: 8}} />
              <div style={{height: 14, width: 300, background: '#eeeeee', borderRadius: 7}} />
            </div>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 4}}>
              {POSTS.map((p, i) => (
                <div key={i} style={{aspectRatio: '3 / 4', overflow: 'hidden', background: '#ddd'}}>
                  <Img src={staticFile(p)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
                </div>
              ))}
            </div>
          </div>
          {/* notch */}
          <div style={{position: 'absolute', top: 14, left: '50%', translate: '-50% 0', width: 150, height: 34, borderRadius: 17, background: '#0E0E0E'}} />
        </div>
      </div>
      {/* punto de toque que sube (scroll) */}
      <div
        style={{
          position: 'absolute',
          left: 540 - 36,
          top: 1500 - interpolate(frame, [s + 10, s + 26], [0, 260], {...clamp, easing: easeInOut}),
          width: 72,
          height: 72,
          borderRadius: 36,
          background: 'rgba(255,255,255,0.35)',
          border: `3px solid ${C.white}`,
          opacity: interpolate(frame, [s + 8, s + 12, s + 26, s + 32], [0, 1, 1, 0], clamp) * (1 - pout),
        }}
      />
    </AbsoluteFill>
  );
};
