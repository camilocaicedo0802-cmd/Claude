import {Video} from '@remotion/media';
import {AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {clamp, easeIn, easeInOut, easeOut} from './ease';
import {C, OUTFIT} from '../v1/theme';
import {SPEECH, T, TOTAL, ws} from './data';
import {Ventana} from './Desktop';

const F = 30;
const pop = (l: number) => interpolate(l, [0, 4, 8], [0, 1.12, 1], clamp);
const typed = (frame: number, text: string, a: number, b: number) => {
  const chars = [...text];
  const n = Math.floor(interpolate(frame, [a * F, b * F], [0, chars.length], clamp));
  return chars.slice(0, n).join('');
};
const caret = (frame: number) => (Math.floor(frame / 8) % 2 ? '|' : ' ');
const money = (n: number) => '$' + Math.round(n).toLocaleString('es-CO');

const BrollVid: React.FC<{src: string; from: number; fit?: 'cover'}> = ({src, from}) => (
  <Sequence from={Math.round(from * F)} layout="none">
    <Video src={staticFile(src)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
  </Sequence>
);

// ---------------------------------------------------------------- 1 · publicar
export const Publicar: React.FC = () => {
  const frame = useCurrentFrame();
  const clickF = (ws(7) + 0.02) * F;
  const done = frame >= clickF;
  const press = interpolate(frame - clickF, [0, 2, 6], [1, 0.94, 1], clamp);
  const toast = frame - (ws(7) + 0.12) * F;
  return (
    <>
      <Ventana x={50} y={100} w={590} h={760} title="Nueva publicación" from={T.win1} to={T.full1} light>
        <div style={{height: 330, overflow: 'hidden'}}>
          <Img src={staticFile('img/b3_bolso.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
        <div style={{display: 'flex', gap: 18, padding: '24px 26px 0'}}>
          <div style={{width: 64, height: 64, borderRadius: 32, background: C.purpleGrad, flexShrink: 0}} />
          <div style={{fontSize: 34, fontWeight: 700, color: '#1A1424', lineHeight: 1.25}}>
            {typed(frame, '¡Nuevo bolso disponible! 👜 Escríbenos', ws(3) + 0.3, ws(7) - 0.15)}
            {frame < (ws(7) - 0.1) * F ? caret(frame) : ''}
          </div>
        </div>
        <div style={{padding: '18px 26px', fontSize: 24, color: '#8A8296', fontWeight: 600}}>📍 Agregar ubicación · # Etiquetas</div>
        <div
          style={{
            position: 'absolute',
            left: 45,
            right: 45,
            top: 590,
            height: 90,
            borderRadius: 22,
            background: done ? '#2A1F3A' : C.purpleGrad,
            display: 'grid',
            placeItems: 'center',
            color: '#fff',
            fontSize: 38,
            fontWeight: 800,
            scale: String(press),
          }}
        >
          {done ? '✓ Publicado' : 'Compartir'}
        </div>
      </Ventana>
      {toast >= 0 && frame < T.full1 * F ? (
        <div
          style={{
            position: 'absolute',
            left: 670,
            top: 110,
            width: 370,
            padding: '20px 24px',
            borderRadius: 26,
            background: 'rgba(245,242,250,0.97)',
            boxShadow: '0 20px 40px rgba(0,0,0,0.45)',
            display: 'flex',
            gap: 16,
            alignItems: 'center',
            fontFamily: OUTFIT,
            translate: `${interpolate(toast, [0, 7], [420, 0], {...clamp, easing: easeOut})}px 0`,
          }}
        >
          <div style={{width: 56, height: 56, borderRadius: 16, background: C.purpleGrad, display: 'grid', placeItems: 'center', color: '#fff', fontSize: 32, fontWeight: 900}}>✓</div>
          <div>
            <div style={{fontSize: 28, fontWeight: 800, color: '#1A1424'}}>Publicado</div>
            <div style={{fontSize: 22, fontWeight: 600, color: '#7A7286'}}>Tu post ya está en el feed</div>
          </div>
        </div>
      ) : null}
    </>
  );
};

/** Nota: «publicar = marketing» → el «=» se tacha y queda «≠». */
export const Nota: React.FC = () => {
  const frame = useCurrentFrame();
  const a = ws(8);
  if (frame < a * F - 1 || frame >= T.full1 * F) return null;
  const l = frame - a * F;
  const strikeF = (ws(11) + 0.05) * F;
  const st = interpolate(frame - strikeF, [0, 5], [0, 1], {...clamp, easing: easeOut});
  const out = interpolate(frame, [T.full1 * F - 5, T.full1 * F], [0, 1], clamp);
  const line1 = typed(frame, 'publicar', a + 0.05, ws(9));
  const line2 = typed(frame, 'marketing', ws(10), ws(11) + 0.02);
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        top: 890,
        width: 560,
        height: 330,
        borderRadius: 18,
        background: '#EADCFF',
        boxShadow: '0 24px 50px rgba(0,0,0,0.5)',
        rotate: '-3deg',
        padding: '34px 40px',
        fontFamily: OUTFIT,
        color: '#1A0033',
        scale: String(pop(l) * (1 - out * 0.1)),
        opacity: 1 - out,
      }}
    >
      <div style={{fontSize: 30, fontWeight: 700, color: '#7A5BA8', marginBottom: 6}}>Nota rápida</div>
      <div style={{fontSize: 84, fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1}}>{line1}</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 8, fontSize: 84, fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1}}>
        {frame >= ws(9) * F ? (
          <span style={{position: 'relative', color: st > 0.5 ? '#7600FC' : '#1A0033'}}>
            =
            <span style={{position: 'absolute', left: -8, top: '50%', width: 70, height: 10, borderRadius: 5, background: '#7600FC', rotate: '-58deg', scale: `${st} 1`, transformOrigin: '50% 50%'}} />
          </span>
        ) : null}
        <span>{line2}</span>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- 2 · pérdida de dinero
export const Perdida: React.FC = () => {
  const frame = useCurrentFrame();
  const a = ws(24) + 0.05;
  const b = ws(26) + 0.25;
  const v = interpolate(frame, [a * F, b * F], [4850000, 0], {...clamp, easing: easeIn});
  const prog = interpolate(frame, [a * F, b * F], [0, 1], clamp);
  const pts = Array.from({length: 24}, (_, i) => {
    const q = i / 23;
    const y = 30 + q * q * 150 + Math.sin(i * 1.7) * 8;
    return `${q * 330},${y}`;
  });
  const shown = pts.slice(0, Math.max(2, Math.ceil(prog * pts.length)));
  return (
    <>
      <Ventana x={40} y={96} w={1000} h={384} title="Fin de mes" from={ws(22)} to={T.win2}>
        <BrollVid src="broll/b3_facturas.mp4" from={ws(22)} />
      </Ventana>
      <Ventana x={30} y={520} w={410} h={470} title="Saldo" from={ws(24) - 0.02} to={T.win2} enter="left">
        <div style={{padding: '24px 28px', fontFamily: OUTFIT}}>
          <div style={{fontSize: 26, fontWeight: 700, color: 'rgba(255,255,255,0.6)'}}>Disponible</div>
          <div style={{fontSize: 64, fontWeight: 900, color: v < 1 ? '#C46BFF' : '#fff', letterSpacing: '-0.03em'}}>{money(v)}</div>
          <svg viewBox="0 0 340 200" style={{width: 354, height: 200, marginTop: 14}}>
            <polyline points={shown.join(' ')} fill="none" stroke="#B701FC" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" style={{filter: 'drop-shadow(0 0 8px rgba(183,1,252,0.8))'}} />
          </svg>
          <div style={{fontSize: 30, fontWeight: 800, color: '#C46BFF', opacity: prog > 0.95 ? 1 : 0}}>−100 % este mes</div>
        </div>
      </Ventana>
    </>
  );
};

// ---------------------------------------------------------------- 3 · estadísticas
const Metric: React.FC<{label: string; value: string; delta?: string; hot?: number; muted?: boolean}> = ({label, value, delta, hot = 0, muted}) => (
  <div
    style={{
      flex: 1,
      height: 230,
      borderRadius: 24,
      padding: '24px 26px',
      background: hot > 0 ? `rgba(150,1,253,${0.12 + hot * 0.2})` : 'rgba(255,255,255,0.05)',
      border: hot > 0 ? `3px solid rgba(183,1,252,${0.4 + hot * 0.6})` : '2px solid rgba(255,255,255,0.08)',
      boxShadow: hot > 0 ? `0 0 ${40 * hot}px rgba(183,1,252,0.6)` : undefined,
      scale: String(1 + hot * 0.1),
      fontFamily: OUTFIT,
    }}
  >
    <div style={{fontSize: 28, fontWeight: 700, color: 'rgba(255,255,255,0.6)'}}>{label}</div>
    <div style={{fontSize: 72, fontWeight: 900, color: muted && hot === 0 ? 'rgba(255,255,255,0.45)' : '#fff', letterSpacing: '-0.03em', marginTop: 10}}>{value}</div>
    {delta ? <div style={{fontSize: 28, fontWeight: 800, color: '#C46BFF'}}>{delta}</div> : null}
  </div>
);

export const Stats: React.FC = () => {
  const frame = useCurrentFrame();
  const f1 = interpolate(frame, [ws(28) * F, ws(30) * F + 10], [0, 12400], {...clamp, easing: easeOut});
  const f2 = interpolate(frame, [ws(29) * F, ws(31) * F], [0, 3200], {...clamp, easing: easeOut});
  const hot = interpolate(frame - ws(38) * F, [0, 4, 10], [0, 1, 0.75], clamp);
  const draw = interpolate(frame, [T.win2 * F + 4, ws(32) * F], [0, 1], {...clamp, easing: easeInOut});
  const W = 920;
  const up = Array.from({length: 20}, (_, i) => `${(i / 19) * W},${200 - Math.pow(i / 19, 1.6) * 170 - Math.sin(i * 1.3) * 8}`);
  const k = Math.max(2, Math.ceil(draw * up.length));
  return (
    <Ventana x={40} y={100} w={1000} h={620} title="Estadísticas · últimos 30 días" from={T.win2} to={T.full2} enter="left">
      <div style={{display: 'flex', gap: 22, padding: '26px 26px 0'}}>
        <Metric label="Seguidores" value={f1 >= 1000 ? `${(f1 / 1000).toFixed(1)}K` : `${Math.round(f1)}`} delta="↑ 18 %" />
        <Metric label="Me gusta" value={Math.round(f2).toLocaleString('es-CO')} delta="↑ 32 %" />
        <Metric label="Ventas" value="$0" delta={hot > 0 ? 'ni un real' : undefined} hot={hot} muted />
      </div>
      <svg viewBox={`0 0 ${W} 220`} style={{position: 'absolute', left: 40, top: 290, width: W, height: 220}}>
        <polyline points={up.slice(0, k).join(' ')} fill="none" stroke="#B701FC" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" style={{filter: 'drop-shadow(0 0 8px rgba(183,1,252,0.8))'}} />
        <line x1="0" y1="205" x2={W * draw} y2="205" stroke="rgba(255,255,255,0.4)" strokeWidth="5" strokeDasharray="14 12" />
        <text x="8" y="40" fill="#C46BFF" fontFamily={OUTFIT} fontSize="26" fontWeight="800">seguidores</text>
        <text x={W - 120} y="192" fill="rgba(255,255,255,0.55)" fontFamily={OUTFIT} fontSize="26" fontWeight="800">ventas</text>
      </svg>
    </Ventana>
  );
};

// ---------------------------------------------------------------- 4 · perfil sin ventas
const TILES = ['b3_bolso', 'b3_cafe', 'b3_flores', 'b3_camisetas', 'b3_cafetera', 'b3_modelo', 'b3_fotografa', 'b3_tienda', 'b3_chica'];

export const Perfil: React.FC = () => {
  const frame = useCurrentFrame();
  const z = frame - ws(50) * F;
  const alert = frame - ws(48) * F;
  const bar = interpolate(frame, [ws(48) * F, ws(49) * F + 6], [0, 0.04], clamp);
  return (
    <>
      <Ventana x={40} y={100} w={600} h={1030} title="@minegocio" from={T.win3} to={T.full3} enter="left">
        <div style={{display: 'flex', alignItems: 'center', gap: 22, padding: '22px 24px', fontFamily: OUTFIT}}>
          <div style={{width: 96, height: 96, borderRadius: 48, background: C.purpleGrad}} />
          <div style={{color: '#fff'}}>
            <div style={{fontSize: 32, fontWeight: 800}}>Mi Negocio</div>
            <div style={{fontSize: 24, fontWeight: 600, color: 'rgba(255,255,255,0.6)'}}>9 publicaciones · 1.240 seguidores</div>
          </div>
        </div>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6, padding: '0 6px'}}>
          {TILES.map((t, i) => {
            const l = frame - ws(46) * F - i * 1.5;
            const zp = interpolate(z - i, [0, 3, 8], [0, 1.25, 1], clamp);
            return (
              <div key={t} style={{position: 'relative', height: 220, overflow: 'hidden', borderRadius: 6, scale: String(pop(l)), opacity: l < 0 ? 0 : 1}}>
                <Img src={staticFile(`img/${t}.jpg`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
                <div
                  style={{
                    position: 'absolute',
                    left: 8,
                    bottom: 8,
                    padding: '4px 12px',
                    borderRadius: 14,
                    background: zp > 0 ? 'rgba(118,0,252,0.92)' : 'rgba(0,0,0,0.6)',
                    color: '#fff',
                    fontFamily: OUTFIT,
                    fontSize: 22,
                    fontWeight: 800,
                    scale: String(zp > 0 ? zp : 1),
                    transformOrigin: '0 100%',
                  }}
                >
                  💰 0
                </div>
              </div>
            );
          })}
        </div>
      </Ventana>
      <Ventana x={660} y={100} w={380} h={600} title="Tu audiencia" from={ws(45)} to={T.full3}>
        <BrollVid src="broll/b3_scroll_cama.mp4" from={ws(45)} />
      </Ventana>
      {alert >= 0 && frame < T.full3 * F ? (
        <div
          style={{
            position: 'absolute',
            left: 130,
            top: 560,
            width: 820,
            padding: '28px 34px',
            borderRadius: 30,
            background: 'rgba(24,20,32,0.97)',
            border: `2px solid ${z >= 0 ? '#B701FC' : 'rgba(255,255,255,0.15)'}`,
            boxShadow: `0 30px 70px rgba(0,0,0,0.6)${z >= 0 ? ', 0 0 50px rgba(183,1,252,0.6)' : ''}`,
            fontFamily: OUTFIT,
            color: '#fff',
            scale: String(pop(alert) * (z >= 0 ? interpolate(z, [0, 3, 7], [1, 1.06, 1], clamp) : 1)),
          }}
        >
          <div style={{fontSize: 30, fontWeight: 700, color: 'rgba(255,255,255,0.65)'}}>{z >= 0 ? 'Resultado' : 'Generando ventas…'}</div>
          {z >= 0 ? (
            <div style={{fontSize: 76, fontWeight: 900, letterSpacing: '-0.03em', color: '#C46BFF'}}>0 ventas este mes</div>
          ) : (
            <div style={{marginTop: 18, height: 26, borderRadius: 13, background: 'rgba(255,255,255,0.1)', overflow: 'hidden'}}>
              <div style={{width: `${bar * 100}%`, height: '100%', background: C.purpleGrad}} />
            </div>
          )}
        </div>
      ) : null}
    </>
  );
};

// ---------------------------------------------------------------- 5 · «lo estás haciendo bien» + «a otro nivel»
export const Nivel: React.FC = () => {
  const frame = useCurrentFrame();
  const closeAt = ws(74) + 0.15;
  const fill = interpolate(frame, [(ws(70) - 0.15) * F, (ws(71) + 0.15) * F], [0.32, 1], {...clamp, easing: easeOut});
  const glitch = frame >= T.close * F ? Math.floor(frame / 2) % 2 : 0;
  return (
    <>
      <Ventana x={40} y={100} w={560} h={370} title="Tu opinión" from={ws(62) - 0.05} to={ws(69)} enter="left">
        <div style={{display: 'flex', gap: 14, justifyContent: 'center', marginTop: 50}}>
          {[0, 1, 2, 3, 4].map((i) => {
            const l = frame - (ws(62) + i * 0.12) * F;
            return (
              <svg key={i} viewBox="0 0 24 24" style={{width: 84, height: 84, scale: String(l >= 0 ? pop(l) : 1)}}>
                <path d="M12 2l3 6.6 7.2.8-5.4 4.9 1.5 7.1L12 17.8 5.7 21.4l1.5-7.1L1.8 9.4 9 8.6z" fill={l >= 0 ? '#B701FC' : 'rgba(255,255,255,0.15)'} style={{filter: l >= 0 ? 'drop-shadow(0 0 8px rgba(183,1,252,0.8))' : undefined}} />
              </svg>
            );
          })}
        </div>
        <div style={{textAlign: 'center', marginTop: 34, fontFamily: OUTFIT, fontSize: 40, fontWeight: 800, color: '#fff', opacity: interpolate(frame - (ws(63)) * F, [0, 5], [0, 1], clamp)}}>«¡Me quedó buenísimo!» 🔥</div>
      </Ventana>
      <Ventana x={630} y={90} w={410} h={390} title="Tus videos" from={ws(67) - 0.05} to={closeAt}>
        <BrollVid src="broll/b3_grabandose.mp4" from={ws(67) - 0.05} />
      </Ventana>
      <Ventana x={40} y={100} w={560} h={370} title="Nivel de tus videos" from={ws(69)} to={closeAt} enter="up">
        <div style={{padding: '36px 34px', fontFamily: OUTFIT, translate: glitch ? '6px 0' : undefined}}>
          <div style={{fontSize: 96, fontWeight: 900, color: '#fff', letterSpacing: '-0.04em'}}>{Math.round(fill * 100)}%</div>
          <div style={{marginTop: 18, height: 40, borderRadius: 20, background: 'rgba(255,255,255,0.1)', overflow: 'hidden'}}>
            <div style={{width: `${fill * 100}%`, height: '100%', background: C.purpleGrad, boxShadow: `0 0 30px ${C.purpleGlow}`}} />
          </div>
          <div style={{marginTop: 18, fontSize: 34, fontWeight: 800, color: '#C46BFF'}}>{fill > 0.98 ? 'A OTRO NIVEL 🚀' : 'subiendo…'}</div>
        </div>
      </Ventana>
    </>
  );
};

// ---------------------------------------------------------------- 6 · monitor de ventas (muere y revive)
const BEATS: {t: number; a: number}[] = [
  {t: ws(79), a: 1},
  {t: ws(82) - 0.05, a: 0.6},
  {t: ws(84), a: 0.3},
  {t: T.on + 0.3, a: 1.25},
  {t: T.on + 0.72, a: 1.25},
  {t: T.on + 1.14, a: 1.2},
  {t: T.on + 1.56, a: 1.2},
];
const ecg = (t: number) => {
  let y = 0;
  for (const b of BEATS) {
    const d = t - b.t;
    if (d > -0.06 && d < 0.2) {
      // P-QRS-T simplificado
      y += b.a * (Math.exp(-Math.pow((d - 0.0) / 0.012, 2)) * 1 - Math.exp(-Math.pow((d - 0.03) / 0.012, 2)) * 0.45 + Math.exp(-Math.pow((d - 0.13) / 0.035, 2)) * 0.2);
    }
  }
  return y;
};

export const Monitor: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const to = T.on + 0.4;
  if (t < T.win4 - 0.04 || t >= to) return null;
  const W = 920;
  const H = 380;
  const span = 2.4;
  const pts: string[] = [];
  for (let i = 0; i <= 240; i++) {
    const s = t - span + (i / 240) * span;
    pts.push(`${(i / 240) * W},${H / 2 - ecg(s) * 150}`);
  }
  const dead = t >= ws(86);
  const alive = t >= T.on;
  const bpm = alive ? 128 : dead ? 0 : t >= ws(84) ? 31 : t >= ws(82) - 0.05 ? 54 : 72;
  const blink = Math.floor(frame / 8) % 2;
  return (
    <Ventana x={40} y={100} w={1000} h={600} title="Monitor de ventas" from={T.win4} to={to} enter="left">
      <AbsoluteFill style={{background: '#06040A'}} />
      <AbsoluteFill style={{backgroundImage: 'linear-gradient(rgba(150,1,253,0.14) 2px, transparent 2px), linear-gradient(90deg, rgba(150,1,253,0.14) 2px, transparent 2px)', backgroundSize: '46px 46px'}} />
      <div style={{position: 'absolute', left: 30, top: 18, fontFamily: OUTFIT, fontSize: 30, fontWeight: 800, color: '#C46BFF', letterSpacing: '0.12em'}}>VENTAS</div>
      <div style={{position: 'absolute', right: 30, top: 10, fontFamily: OUTFIT, fontSize: 80, fontWeight: 900, color: dead && !alive ? (blink ? '#fff' : 'rgba(255,255,255,0.35)') : '#fff', letterSpacing: '-0.03em'}}>
        {bpm}
        <span style={{fontSize: 30, color: 'rgba(255,255,255,0.6)', marginLeft: 8}}>{alive ? '💜' : 'lpm'}</span>
      </div>
      {dead && !alive ? (
        <div style={{position: 'absolute', left: 30, top: 70, fontFamily: OUTFIT, fontSize: 34, fontWeight: 900, color: '#fff', opacity: blink ? 1 : 0.4}}>NEGOCIO SIN PULSO</div>
      ) : null}
      {alive ? <div style={{position: 'absolute', left: 30, top: 70, fontFamily: OUTFIT, fontSize: 34, fontWeight: 900, color: '#C46BFF'}}>¡VUELVE A LA VIDA!</div> : null}
      <svg viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 40, top: 130, width: W, height: H}}>
        <polyline points={pts.join(' ')} fill="none" stroke={alive ? '#C46BFF' : '#B701FC'} strokeWidth="7" strokeLinejoin="round" strokeLinecap="round" style={{filter: 'drop-shadow(0 0 10px rgba(183,1,252,0.95))'}} />
        <circle cx={W} cy={H / 2 - ecg(t) * 150} r="11" fill="#fff" style={{filter: 'drop-shadow(0 0 12px #B701FC)'}} />
      </svg>
    </Ventana>
  );
};

// ---------------------------------------------------------------- 7 · comentario «REVIVIR»
export const Comentario: React.FC = () => {
  const frame = useCurrentFrame();
  const clickF = (ws(98) + 0.36) * F;
  const sent = frame >= clickF;
  const txt = typed(frame, 'REVIVIR', ws(97), ws(98) + 0.25);
  const press = interpolate(frame - clickF, [0, 2, 6], [1, 0.88, 1], clamp);
  return (
    <Ventana x={40} y={150} w={1000} h={180} title="Comentarios" from={ws(95) - 0.05} to={T.end}>
      <div style={{display: 'flex', alignItems: 'center', gap: 22, height: 124, padding: '0 30px', fontFamily: OUTFIT}}>
        <div style={{width: 72, height: 72, borderRadius: 36, background: C.purpleGrad, flexShrink: 0}} />
        <div style={{flex: 1, fontSize: 50, fontWeight: 900, color: sent ? '#C46BFF' : txt ? '#fff' : 'rgba(255,255,255,0.35)', letterSpacing: '0.02em'}}>
          {sent ? 'REVIVIR 💜  ·  enviado' : txt || 'Escribe un comentario…'}
          {!sent && txt ? caret(frame) : ''}
        </div>
        <div style={{width: 96, height: 96, borderRadius: 48, background: C.purpleGrad, display: 'grid', placeItems: 'center', color: '#fff', fontSize: 46, fontWeight: 900, scale: String(press), flexShrink: 0}}>➤</div>
      </div>
    </Ventana>
  );
};

// ---------------------------------------------------------------- cierre
export const CierreC: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame < T.end * F) return null;
  const l = frame - T.end * F;
  const txt = typed(frame, 'REVIVIR', T.end + 0.8, T.end + 1.5);
  const fade = interpolate(frame, [(TOTAL - 0.35) * F, TOTAL * F], [0, 1], clamp);
  return (
    <>
      <Img src={staticFile('img/logo_grow.png')} style={{position: 'absolute', left: 260, top: 130, width: 560, scale: String(pop(l - 4))}} />
      <div
        style={{
          position: 'absolute',
          left: 140,
          top: 420,
          width: 800,
          height: 330,
          borderRadius: 22,
          background: '#EADCFF',
          boxShadow: '0 30px 60px rgba(0,0,0,0.55)',
          rotate: '-2deg',
          padding: '34px 46px',
          fontFamily: OUTFIT,
          color: '#1A0033',
          scale: String(pop(l - 10)),
        }}
      >
        <div style={{fontSize: 40, fontWeight: 800, color: '#7A5BA8'}}>Comenta la palabra 👇</div>
        <div style={{fontSize: 130, fontWeight: 900, letterSpacing: '-0.03em', lineHeight: 1.05, color: '#7600FC'}}>
          {txt}
          {txt.length < 7 ? caret(frame) : ''}
        </div>
        <div style={{fontSize: 34, fontWeight: 700}}>y revivimos tu negocio 💜</div>
      </div>
      <AbsoluteFill style={{background: '#000', opacity: fade}} />
    </>
  );
};

void SPEECH;
void easeInOut;
