import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS, backOut, clamp, easeOut} from './base';
import {T} from './data';

// Equivalente del lingote de oro del referente (estilo.md §4.1, §10.1): móvil 3D del cliente que cae
// abajo a la izquierda con ondas al aterrizar + logos 3D de las redes que aparecen y flotan a los lados de la cabeza.

const Ondas: React.FC<{x: number; y: number; at: number; t: number; n?: number; r0?: number; r1?: number}> = ({x, y, at, t, n = 3, r0 = 50, r1 = 260}) => (
  <>
    {Array.from({length: n}).map((_, k) => {
      const a = at + k * 0.12;
      const p = interpolate(t, [a, a + 0.75], [0, 1], {...clamp, easing: easeOut});
      if (t < a || p >= 1) return null;
      const r = r0 + (r1 - r0) * p;
      return (
        <div
          key={k}
          style={{
            position: 'absolute',
            left: x - r,
            top: y - r,
            width: r * 2,
            height: r * 2,
            borderRadius: '50%',
            border: `${3 - p * 1.5}px solid rgba(214,160,255,${0.9 * (1 - p)})`,
            boxShadow: `0 0 16px rgba(183,1,252,${0.5 * (1 - p)})`,
          }}
        />
      );
    })}
  </>
);

const LOGOS = [
  {src: 'img/logo3d_instagram.png', x: 975, y: 520, w: 190, rot: -14},
  {src: 'img/logo3d_facebook.png', x: 968, y: 815, w: 165, rot: 12},
  {src: 'img/logo3d_tiktok.png', x: 108, y: 640, w: 165, rot: -10},
];

export const Gancho: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const {movil, logos, fin} = T.gancho;
  if (t < movil - 0.05 || t > fin + 0.3) return null;
  const sale = interpolate(t, [fin, fin + 0.24], [0, 1], {...clamp, easing: easeOut});

  // móvil: entra desde arriba a la derecha y aterriza abajo a la izquierda en 0,45 s
  const land = movil + 0.45;
  const p = interpolate(t, [movil, land], [0, 1], {...clamp, easing: easeOut});
  const S = 0.64; // 450x820 → 288x525
  const restX = 20;
  const restY = 1405;
  const x = interpolate(p, [0, 1], [760, restX]);
  const y = interpolate(p, [0, 1], [-520, restY]) + Math.sin((t - land) * 2.4) * (t > land ? 8 : 0) + sale * 420;
  const rot = interpolate(p, [0, 1], [28, -7]) + (t > land ? Math.sin((t - land) * 1.7) * 2 : 0);
  const src = Math.max(0, Math.min(300, Math.round((t - movil + 0.3) * FPS)));
  const cx = restX + (450 * S) / 2;
  const cy = restY + (820 * S) / 2;

  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <Ondas x={cx} y={cy} at={land - 0.04} t={t} r0={90} r1={330} />
      <Img
        src={staticFile(`cel3d/f_${String(src).padStart(3, '0')}.png`)}
        style={{
          position: 'absolute',
          left: x,
          top: y,
          width: 450 * S,
          height: 820 * S,
          transform: `rotate(${rot}deg)`,
          filter: `drop-shadow(0 26px 40px rgba(0,0,0,0.55)) blur(${sale * 10}px)`,
          opacity: 1 - sale,
        }}
      />
      {LOGOS.map((l, k) => {
        const a = logos[k] - 0.06;
        if (t < a) return null;
        const q = interpolate(t, [a, a + 0.38], [0, 1], {...clamp, easing: backOut});
        const life = t - a;
        const dir = l.x > 540 ? 1 : -1;
        return (
          <div key={k} style={{position: 'absolute', left: l.x - l.w / 2, top: l.y - l.w / 2, width: l.w, height: l.w, perspective: 900}}>
            <Ondas x={l.w / 2} y={l.w / 2} at={a + 0.05} t={t} n={2} r0={l.w * 0.35} r1={l.w * 0.95} />
            <Img
              src={staticFile(l.src)}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'contain',
                opacity: Math.min(1, q * 1.4) * (1 - sale),
                filter: `drop-shadow(0 18px 26px rgba(0,0,0,0.5)) blur(${sale * 12}px)`,
                transform: [
                  `translate(${sale * dir * 220}px, ${Math.sin(life * 2.1 + k) * 12 - sale * 60}px)`,
                  `scale(${q * (1 - sale * 0.4)})`,
                  `rotateZ(${l.rot * (1 - q) * 2 + Math.sin(life * 1.6 + k * 2) * 6}deg)`,
                  `rotateY(${Math.sin(life * 1.3 + k) * 22}deg)`,
                  `rotateX(${Math.cos(life * 1.1 + k) * 10}deg)`,
                ].join(' '),
              }}
            />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
