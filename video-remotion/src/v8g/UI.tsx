import {Video} from '@remotion/media';
import {AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOut} from '../engine/helpers';
import {INTER, P} from './fonts';
import {Scene, ws} from './data';
import {FondoUI} from './Escenas';

const F = 30;
const typed = (frame: number, text: string, a: number, b: number) => [...text].slice(0, Math.floor(interpolate(frame, [a * F, b * F], [0, [...text].length], clamp))).join('');

/** Tarjeta curvada en 3D (como la caja de búsqueda doblada del referente). */
const Curva: React.FC<{scene: Scene; children: React.ReactNode; zoom?: number; zx?: number; zy?: number}> = ({scene, children, zoom = 1, zx = 50, zy = 50}) => {
  const frame = useCurrentFrame();
  const q = interpolate(frame, [scene.from * F, scene.to * F], [0, 1], clamp);
  const pin = interpolate(frame - scene.from * F, [0, 8], [0, 1], {...clamp, easing: easeOut});
  return (
    <AbsoluteFill style={{perspective: 1300, perspectiveOrigin: '50% 40%'}}>
      <AbsoluteFill
        style={{
          transform: `rotateX(${interpolate(q, [0, 1], [14, 8])}deg) rotateY(${interpolate(q, [0, 1], [-16, -6])}deg) scale(${zoom * interpolate(pin, [0, 1], [0.92, 1])})`,
          transformOrigin: `${zx}% ${zy}%`,
          opacity: pin,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Cursor: React.FC<{x: number; y: number; press?: number}> = ({x, y, press = 1}) => (
  <svg viewBox="0 0 24 24" style={{position: 'absolute', left: x - 8, top: y - 4, width: 70, height: 70, scale: String(press), filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.5))'}}>
    <path d="M5 2 L5 19 L9.5 15 L12.5 22 L15.5 20.8 L12.6 14 L18.5 14 Z" fill="#fff" stroke="#111" strokeWidth="1.3" strokeLinejoin="round" />
  </svg>
);

// ---------------------------------------------------------------- buscador curvado
type Res = {t: string; s: string; icon: string};
const RES: Record<string, Res[]> = {
  'tienda de ropa cerca de mí': [
    {t: 'Moda Urbana · Tienda de ropa', s: '★ 4,8 (320 reseñas) · Abierto ahora', icon: '🛍️'},
    {t: 'Boutique Luna', s: '★ 4,6 (198 reseñas) · Envíos a domicilio', icon: '👗'},
    {t: 'Estilo Total · Ropa y accesorios', s: '★ 4,5 (141 reseñas) · Abierto', icon: '🛍️'},
    {t: 'Tu negocio', s: 'Sin reseñas · Sin fotos', icon: '🏪'},
    {t: 'tiendas de ropa en Chiriquí', s: 'Búsqueda de Google', icon: '🔍'},
    {t: 'tienda de ropa abierta ahora', s: 'Búsqueda de Google', icon: '🔍'},
  ],
  'grow marketing': [
    {t: 'Grow Marketing · Agencia de marketing', s: '@growmarketingpro_ · Hacemos que tu negocio se venda', icon: '🟣'},
    {t: 'growmarketingpro_ · Instagram', s: '10,4 mil seguidores · Videos · Fotos · Reels', icon: '📸'},
    {t: 'grow marketing agencia', s: 'Búsqueda de Google', icon: '🔍'},
    {t: 'grow marketing publicidad en redes', s: 'Búsqueda de Google', icon: '🔍'},
    {t: 'grow marketing reels', s: 'Búsqueda de Google', icon: '🔍'},
  ],
};

export const Google: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const q = scene.query!;
  const a = scene.from + 0.15;
  const b = a + Math.min(1.1, [...q].length * 0.055);
  const txt = typed(frame, q, a, b);
  const open = interpolate(frame, [b * F, b * F + 6], [0, 1], {...clamp, easing: easeOut});
  const res = RES[q];
  // clic en el primer resultado («siguiente comercio» / Grow Marketing)
  const clickT = q === 'grow marketing' ? scene.to - 0.28 : ws(74);
  const cur = interpolate(frame, [(clickT - 0.45) * F, clickT * F], [0, 1], {...clamp, easing: easeInOut});
  const press = interpolate(frame - clickT * F, [0, 2, 5], [1, 0.82, 1], clamp);
  const hl = frame >= clickT * F;
  return (
    <AbsoluteFill>
      <FondoUI />
      <Curva scene={scene}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 470, textAlign: 'center', fontFamily: INTER, fontWeight: 500, fontSize: 124, letterSpacing: '-0.03em', color: '#FFFFFF'}}>Google</div>
        <div style={{position: 'absolute', left: 80, right: 80, top: 650, borderRadius: 34, background: '#FFFFFF', boxShadow: '0 30px 60px rgba(0,0,0,0.45)', overflow: 'hidden', fontFamily: INTER}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 22, height: 110, padding: '0 34px', fontSize: 40, fontWeight: 500, color: '#202124'}}>
            <span style={{fontSize: 44, color: '#5f6368'}}>+</span>
            <span>
              {txt}
              {open < 1 && Math.floor(frame / 8) % 2 ? '|' : ''}
            </span>
          </div>
          <div style={{height: open * res.length * 92, overflow: 'hidden'}}>
            {res.map((r, i) => (
              <div key={i} style={{display: 'flex', alignItems: 'center', gap: 22, height: 92, padding: '0 34px', background: hl && i === 0 ? '#ECE4FA' : i === 0 ? '#F3F0F8' : '#FFFFFF', borderTop: '1px solid #ECECEC'}}>
                <span style={{fontSize: 34, width: 40, textAlign: 'center'}}>{r.icon}</span>
                <div style={{lineHeight: 1.15}}>
                  <div style={{fontSize: 32, fontWeight: 700, color: '#202124'}}>{r.t}</div>
                  <div style={{fontSize: 24, fontWeight: 500, color: r.s.includes('★') || r.s.includes('@') ? '#5B3BB5' : '#70757a'}}>{r.s}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        {cur > 0 ? <Cursor x={interpolate(cur, [0, 1], [980, 520])} y={interpolate(cur, [0, 1], [1500, 820])} press={press} /> : null}
      </Curva>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- perfil flojo de «tu negocio»
export const Perfil: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const z = interpolate(frame, [ws(60) * F, ws(60) * F + 10], [1, 1.75], {...clamp, easing: easeInOut});
  const tap = frame - ws(54) * F;
  const ring = tap >= 0 && tap < 12 ? tap / 12 : 0;
  const tiles = ['¡OFERTA!', 'Hoy abierto', 'foto 📷', 'Nuevo stock', 'Feliz día', '—'];
  return (
    <AbsoluteFill>
      <FondoUI />
      <Curva scene={scene} zoom={z} zx={50} zy={74}>
        <div style={{position: 'absolute', left: 150, right: 150, top: 300, height: 1380, borderRadius: 44, background: '#FFFFFF', boxShadow: '0 40px 80px rgba(0,0,0,0.5)', overflow: 'hidden', fontFamily: INTER, color: '#111'}}>
          <div style={{height: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 34, fontWeight: 700}}>tunegocio</div>
          <div style={{display: 'flex', alignItems: 'center', gap: 36, padding: '20px 40px'}}>
            <div style={{width: 150, height: 150, borderRadius: 75, background: '#D9D9DE', display: 'grid', placeItems: 'center', fontSize: 64}}>🏪</div>
            {[['6', 'publicaciones'], ['48', 'seguidores'], ['12', 'seguidos']].map(([n, l]) => (
              <div key={l} style={{textAlign: 'center'}}>
                <div style={{fontSize: 40, fontWeight: 800}}>{n}</div>
                <div style={{fontSize: 22, fontWeight: 500, color: '#666'}}>{l}</div>
              </div>
            ))}
          </div>
          <div style={{padding: '0 40px 24px', fontSize: 26, fontWeight: 500, color: '#333', lineHeight: 1.35}}>
            Tu Negocio
            <br />
            Ventas por DM 📦 · Última publicación: hace 8 meses
          </div>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 4, padding: '0 4px'}}>
            {tiles.map((tt, i) => (
              <div key={i} style={{height: 250, background: ['#C9C3B6', '#B9C0C7', '#D3CBBF', '#BFB7AE', '#CBC4D0', '#E3E3E6'][i], display: 'grid', placeItems: 'center', fontSize: 30, fontWeight: 800, color: 'rgba(0,0,0,0.35)', filter: 'blur(1.2px) saturate(0.6)'}}>
                {tt}
              </div>
            ))}
          </div>
        </div>
        {ring > 0 ? <div style={{position: 'absolute', left: 540 - 60 * ring, top: 560 - 60 * ring, width: 120 * ring, height: 120 * ring, borderRadius: '50%', border: `5px solid rgba(150,1,253,${1 - ring})`}} /> : null}
      </Curva>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- chat sin respuesta
export const DM: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const bubble = (at: number, text: string, y: number) => {
    const p = interpolate(frame - at * F, [0, 5], [0, 1], {...clamp, easing: easeOut});
    if (p <= 0) return null;
    return (
      <div style={{position: 'absolute', left: 60, top: y, padding: '22px 30px', borderRadius: '10px 34px 34px 34px', background: '#EFEFF2', fontSize: 40, fontWeight: 600, color: '#111', opacity: p, scale: String(interpolate(p, [0, 1], [0.85, 1])), transformOrigin: '0 0'}}>
        {text}
      </div>
    );
  };
  const visto = interpolate(frame - ws(89) * F, [0, 5], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <FondoUI />
      <Curva scene={scene}>
        <div style={{position: 'absolute', left: 150, right: 150, top: 380, height: 1000, borderRadius: 44, background: '#FFFFFF', boxShadow: '0 40px 80px rgba(0,0,0,0.5)', overflow: 'hidden', fontFamily: INTER}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 22, height: 130, padding: '0 36px', borderBottom: '1px solid #EEE'}}>
            <div style={{width: 76, height: 76, borderRadius: 38, background: '#E2D6F7'}} />
            <div>
              <div style={{fontSize: 32, fontWeight: 700, color: '#111'}}>cliente_maria</div>
              <div style={{fontSize: 22, fontWeight: 500, color: '#888'}}>Instagram</div>
            </div>
          </div>
          <div style={{position: 'relative', height: 870}}>
            {bubble(scene.from + 0.1, 'Hola 👋', 60)}
            {bubble(ws(86), '¿Cuánto cuesta? 🙏', 190)}
            {bubble(ws(88), '¿Hacen envíos?', 320)}
            <div style={{position: 'absolute', right: 50, top: 460, fontSize: 26, fontWeight: 600, color: '#9A9A9A', opacity: visto}}>Visto · hace 3 días</div>
            <div style={{position: 'absolute', left: 30, right: 30, bottom: 30, height: 90, borderRadius: 45, border: '2px solid #E5E5E5', display: 'flex', alignItems: 'center', padding: '0 34px', fontSize: 30, color: '#B0B0B0'}}>Escribe un mensaje…</div>
          </div>
        </div>
      </Curva>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- demostración: grabación de Instagram con zooms
const SHOTS: {from: number; to: number; clip: number; x: number; y: number; z: number; rate?: number}[] = [
  {from: 38.3, to: 39.6, clip: 0.05, x: 360, y: 230, z: 1.9},
  {from: 39.6, to: 41.0, clip: 2.0, x: 360, y: 900, z: 1.15},
  {from: 41.0, to: 42.0, clip: 5.95, x: 360, y: 820, z: 1.25, rate: 0.5},
  {from: 42.0, to: 42.95, clip: 9.65, x: 360, y: 700, z: 1.5},
  {from: 42.95, to: 44.36, clip: 8.05, x: 360, y: 650, z: 1.45},
];
export const IGDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const sh = SHOTS.find((s) => t >= s.from && t < s.to);
  if (!sh) return null;
  const k = 1820 / 1564; // la grabación (720×1564) a lo alto de la pantalla
  const zq = interpolate(frame - sh.from * F, [2, 12], [0, 1], {...clamp, easing: easeInOut});
  const z = interpolate(zq, [0, 1], [1, sh.z]);
  // el punto de interés va hacia el centro de la pantalla mientras se hace zoom
  const tx = interpolate(zq, [0, 1], [540 + (sh.x - 360) * k, 540]);
  const ty = interpolate(zq, [0, 1], [960 + (sh.y - 782) * k, 960]);
  const cx = tx - (sh.x - 360) * k * z;
  const cy = ty - (sh.y - 782) * k * z;
  return (
    <AbsoluteFill>
      <FondoUI light />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <div style={{position: 'absolute', left: cx - (720 * k * z) / 2, top: cy - (1564 * k * z) / 2, width: 720 * k * z, height: 1564 * k * z, borderRadius: 50 * z, overflow: 'hidden', boxShadow: '0 30px 70px rgba(0,0,0,0.25)'}}>
          <Sequence from={Math.round(sh.from * F)} layout="none">
            <Video src={staticFile('broll/ig_grow.mp4')} muted trimBefore={Math.round(sh.clip * F)} playbackRate={sh.rate ?? 1} objectFit="cover" style={{width: '100%', height: '100%'}} />
          </Sequence>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export {P};
