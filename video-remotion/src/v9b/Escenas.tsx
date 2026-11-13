import {Video} from '@remotion/media';
import {AbsoluteFill, Freeze, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOut, rand} from '../engine/helpers';
import {C, OUTFIT} from '../v1/theme';
import {T, ws} from './data';
import {Bubble, LastFrame, Live} from './Live';
import {Marquee} from './Fondos';

const F = 30;
const pop = (l: number) => interpolate(l, [0, 4, 8], [0, 1.12, 1], clamp);

/** Entrada empujando desde la derecha con desenfoque de movimiento. */
const slideIn = (frame: number, t: number) => {
  const p = interpolate(frame - t * F, [0, 7], [0, 1], {...clamp, easing: easeOut});
  return {translate: `${(1 - p) * 1080}px 0`, filter: p < 1 ? `blur(${(1 - p) * 18}px)` : undefined};
};

// ---------------------------------------------------------------- versus
const Notif: React.FC<{at: number; i: number; title: string; sub: string}> = ({at, i, title, sub}) => {
  const frame = useCurrentFrame();
  const l = frame - at * F;
  if (l < 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: 34,
        width: 472,
        top: 440 + i * 150,
        height: 126,
        borderRadius: 30,
        background: 'rgba(255,255,255,0.96)',
        boxShadow: '0 14px 30px rgba(0,0,0,0.35)',
        display: 'flex',
        alignItems: 'center',
        gap: 20,
        padding: '0 22px',
        scale: String(pop(l)),
        translate: `0 ${interpolate(l, [0, 6], [-30, 0], {...clamp, easing: easeOut})}px`,
      }}
    >
      <div style={{width: 76, height: 76, borderRadius: 22, background: C.purpleGrad, display: 'grid', placeItems: 'center', fontSize: 40}}>💸</div>
      <div>
        <div style={{fontSize: 34, fontWeight: 800, color: '#111', letterSpacing: '-0.02em'}}>{title}</div>
        <div style={{fontSize: 26, fontWeight: 600, color: '#777'}}>{sub}</div>
      </div>
    </div>
  );
};

export const Versus: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.s2 - 0.01 || t >= T.s3 + 0.2) return null;
  // la burbuja crece hasta ser el plano completo (fin = sala con el encuadre del segmento 4)
  const e = interpolate(frame, [(T.s3 - 0.12) * F, (T.s3 + 0.2) * F], [0, 1], {...clamp, easing: easeInOut});
  const s = 1.16;
  const cx = interpolate(e, [0, 1], [540, 540 + 35 * s]);
  const cy = interpolate(e, [0, 1], [1590, 806 + 74 * s]);
  const d = interpolate(e, [0, 1], [380, 2700]);
  const k = interpolate(e, [0, 1], [0.6, s]);
  const right = interpolate(frame - ws(16) * F, [0, 6], [0, 1], {...clamp, easing: easeOut});
  const left = interpolate(frame - ws(12) * F, [-4, 4], [0, 1], {...clamp, easing: easeOut});
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <AbsoluteFill style={slideIn(frame, T.s2)}>
        <div style={{position: 'absolute', left: 0, top: 0, width: 540, height: 1920, background: 'linear-gradient(180deg, #9601FD 0%, #7600FC 45%, #3D0080 100%)'}}>
          <div style={{position: 'absolute', left: 0, right: 0, top: 240, textAlign: 'center', fontSize: 96, fontWeight: 900, letterSpacing: '-0.05em', color: '#fff', opacity: left, scale: String(interpolate(left, [0, 1], [0.6, 1])), textShadow: `0 6px 0 ${C.purpleShadow}`}}>
            ✓ VENDEN
          </div>
          <Notif at={ws(12)} i={0} title="Nueva venta" sub="$ 89.000 · ahora" />
          <Notif at={ws(12) + 0.17} i={1} title="Pedido #1024" sub="Pago confirmado" />
          <Notif at={ws(12) + 0.34} i={2} title="Nueva venta" sub="$ 145.000 · ahora" />
          <Notif at={ws(12) + 0.51} i={3} title="Nuevo cliente" sub="Te escribió por DM" />
        </div>
        <div style={{position: 'absolute', left: 540, top: 0, width: 540, height: 1920, background: 'linear-gradient(180deg, #2A2A2A 0%, #161616 60%, #0B0B0B 100%)'}}>
          <div style={{position: 'absolute', left: 0, right: 0, top: 240, textAlign: 'center', fontSize: 96, fontWeight: 900, letterSpacing: '-0.05em', color: '#9A9A9A', opacity: right, scale: String(interpolate(right, [0, 1], [0.6, 1]))}}>
            ✕ NO VENDEN
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 470, textAlign: 'center', fontSize: 330, fontWeight: 900, lineHeight: 1, color: 'transparent', WebkitTextStroke: '5px #6A6A6A', opacity: right}}>0</div>
          <div style={{position: 'absolute', left: 60, right: 60, top: 860, height: 120, borderRadius: 30, border: '4px dashed #555', display: 'grid', placeItems: 'center', color: '#8A8A8A', fontSize: 34, fontWeight: 700, opacity: right}}>
            Sin notificaciones
          </div>
        </div>
        <div style={{position: 'absolute', left: 540 - 3, top: 0, width: 6, height: 1920, background: 'rgba(255,255,255,0.85)', boxShadow: '0 0 30px rgba(255,255,255,0.6)'}} />
        <div style={{position: 'absolute', left: 540 - 70, top: 1150, width: 140, height: 140, borderRadius: 70, background: '#fff', display: 'grid', placeItems: 'center', fontSize: 62, fontWeight: 900, color: C.purple, boxShadow: `0 0 40px ${C.purpleGlow}`, scale: String(pop(frame - ws(16) * F))}}>
          VS
        </div>
      </AbsoluteFill>
      <Bubble from={T.s2} to={T.s3 + 0.25} cx={cx} cy={cy} d={d} k={k} ring={Math.round(8 * (1 - e))} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- batería
export const Bateria: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.s5 || t >= T.s6) return null;
  const l = frame - T.s5 * F;
  const lvl = interpolate(frame, [(T.s5 + 0.35) * F, ws(46) * F], [86, 4], {...clamp, easing: easeInOut});
  const low = lvl < 20;
  const blink = low ? (Math.floor(l / 4) % 2 ? 0.45 : 1) : 1;
  const out = interpolate(frame, [T.s6 * F - 5, T.s6 * F], [1, 0], clamp);
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 150, display: 'flex', flexDirection: 'column', alignItems: 'center', scale: String(pop(l) * out), rotate: '-3deg'}}>
        <div style={{fontSize: 52, fontWeight: 800, color: '#fff', letterSpacing: '0.06em', textShadow: '0 4px 14px rgba(0,0,0,0.6)'}}>TU RED SOCIAL</div>
        <div style={{display: 'flex', alignItems: 'center', marginTop: 16}}>
          <div style={{position: 'relative', width: 430, height: 180, borderRadius: 36, border: '10px solid #fff', padding: 10, boxShadow: '0 12px 40px rgba(0,0,0,0.5)', background: 'rgba(0,0,0,0.35)'}}>
            <div style={{width: `${lvl}%`, height: '100%', borderRadius: 20, background: low ? '#7A7A7A' : C.purpleGrad, opacity: blink, boxShadow: low ? 'none' : `0 0 30px ${C.purpleGlow}`}} />
            <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', fontSize: 84, fontWeight: 900, color: '#fff', textShadow: '0 4px 0 rgba(0,0,0,0.45)'}}>{Math.round(lvl)}%</div>
          </div>
          <div style={{width: 26, height: 70, borderRadius: '0 12px 12px 0', background: '#fff', marginLeft: 6}} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- chat
const Msg: React.FC<{at: number; i: number; name: string; text: string}> = ({at, i, name, text}) => {
  const frame = useCurrentFrame();
  const l = frame - at * F;
  if (l < 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        top: 470 + i * 215,
        maxWidth: 820,
        padding: '22px 34px 26px',
        borderRadius: '10px 40px 40px 40px',
        background: '#FFFFFF',
        boxShadow: '0 12px 30px rgba(0,0,0,0.4)',
        transformOrigin: '0 0',
        scale: String(pop(l)),
      }}
    >
      <div style={{fontSize: 30, fontWeight: 800, color: C.purple}}>{name}</div>
      <div style={{fontSize: 46, fontWeight: 600, color: '#111', letterSpacing: '-0.02em'}}>{text}</div>
    </div>
  );
};

export const Chat: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.s6 || t >= T.s7) return null;
  const end = interpolate(frame - (ws(59) + 0.25) * F, [0, 5], [0, 1], clamp);
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <AbsoluteFill style={{...slideIn(frame, T.s6), background: 'radial-gradient(ellipse at 50% 30%, #2A0055 0%, #120024 45%, #0B0B0B 100%)'}}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 300, background: 'rgba(255,255,255,0.06)', borderBottom: '2px solid rgba(255,255,255,0.12)', display: 'flex', alignItems: 'flex-end', gap: 28, padding: '0 60px 40px'}}>
          <div style={{width: 110, height: 110, borderRadius: 55, background: C.purpleGrad, display: 'grid', placeItems: 'center', fontSize: 56}}>🏪</div>
          <div>
            <div style={{fontSize: 54, fontWeight: 800, color: '#fff'}}>Mi negocio</div>
            <div style={{fontSize: 32, fontWeight: 600, color: 'rgba(255,255,255,0.6)'}}>Clientes del mes</div>
          </div>
        </div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 360, display: 'flex', justifyContent: 'center', opacity: interpolate(frame - ws(49) * F, [0, 5], [0, 1], clamp)}}>
          <div style={{padding: '10px 30px', borderRadius: 30, background: 'rgba(255,255,255,0.12)', color: 'rgba(255,255,255,0.8)', fontSize: 32, fontWeight: 700}}>Primer mes vendiendo 🎉</div>
        </div>
        <Msg at={ws(54)} i={0} name="Mamá ❤️" text="¡Yo te compro el primero!" />
        <Msg at={ws(57)} i={1} name="Vecina Marta 🏠" text="Te compro uno, vecino 😊" />
        <Msg at={ws(59)} i={2} name="Juan (amigo) 🍻" text="¡Te apoyo, parce! 🔥" />
        <div style={{position: 'absolute', left: 0, right: 0, top: 1150, display: 'flex', justifyContent: 'center', opacity: end, scale: String(interpolate(end, [0, 1], [0.8, 1]))}}>
          <div style={{padding: '12px 34px', borderRadius: 30, background: 'rgba(255,255,255,0.08)', border: '2px dashed rgba(255,255,255,0.35)', color: 'rgba(255,255,255,0.75)', fontSize: 34, fontWeight: 700}}>…y después, nadie más</div>
        </div>
      </AbsoluteFill>
      <div style={{...slideIn(frame, T.s6), position: 'absolute', inset: 0}}>
        <Bubble from={T.s6} to={T.s7} cx={850} cy={1620} d={360} k={0.6} />
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- pantalla dividida
const CLIPS = [
  {src: 'broll/b9_equipo.mp4', from: T.s9, to: ws(81) - 0.08, label: 'EQUIPO', at: ws(73)},
  {src: 'broll/b9_postits.mp4', from: ws(81) - 0.08, to: ws(83) - 0.08, label: 'ESTRATEGIA', at: ws(81)},
  {src: 'broll/b9_aroluz.mp4', from: ws(83) - 0.08, to: T.s10 + 0.3, label: 'CONTENIDO', at: ws(85)},
];

export const Split: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.s9 || t >= T.s10 + 0.3) return null;
  const pin = interpolate(frame, [T.s9 * F, T.s9 * F + 8], [0, 1], {...clamp, easing: easeOut});
  const pout = interpolate(frame, [T.s10 * F - 1, T.s10 * F + 8], [0, 1], {...clamp, easing: easeInOut});
  const p = pin * (1 - pout);
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      {/* mitad de abajo: él, encuadrado de la frente al pecho */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 960 * p, height: 1920 - 960 * p, overflow: 'hidden', background: '#000'}}>
        <div style={{position: 'absolute', left: 0, top: -370 * p, width: 1080, height: 1920}}>
          <Live from={T.s9} to={T.s10 + 0.3} framing={false} />
        </div>
      </div>
      {/* mitad de arriba: B-roll */}
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 960, overflow: 'hidden', translate: `0 ${(p - 1) * 960}px`, background: '#000'}}>
        {CLIPS.map((c, i) => {
          const a = Math.round(c.from * F);
          const b = Math.round(c.to * F);
          const sl = i === 0 ? 1 : interpolate(frame - a, [0, 6], [0, 1], {...clamp, easing: easeOut});
          return (
            <Sequence key={c.src} from={a} durationInFrames={b - a} layout="none">
              <div style={{position: 'absolute', inset: 0, translate: `${(1 - sl) * (i % 2 ? -1080 : 1080)}px 0`, filter: sl < 1 ? `blur(${(1 - sl) * 14}px)` : undefined}}>
                <Video src={staticFile(c.src)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
              </div>
              <div
                style={{
                  position: 'absolute',
                  left: 50,
                  top: 70,
                  padding: '8px 30px 14px',
                  borderRadius: 18,
                  background: '#fff',
                  color: C.purple,
                  fontSize: 60,
                  fontWeight: 900,
                  letterSpacing: '-0.03em',
                  rotate: '-3deg',
                  boxShadow: `0 8px 0 ${C.purpleShadow}, 0 0 30px rgba(0,0,0,0.4)`,
                  transformOrigin: '0 50%',
                  scale: String(pop(frame - Math.max(a, Math.round(c.at * F) - 2))),
                }}
              >
                {c.label}
              </div>
            </Sequence>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 960 - 4, height: 8, background: C.purpleGrad, opacity: p, boxShadow: `0 0 30px ${C.purpleGlow}`}} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- visor de cámara + polaroids
const SHOTS = [
  {t: ws(89), x: 40, y: 120, r: -8},
  {t: ws(90) + 0.22, x: 800, y: 110, r: 7},
];

const Polaroid: React.FC<{t: number; x: number; y: number; r: number}> = ({t, x, y, r}) => {
  const frame = useCurrentFrame();
  const at = Math.round(t * F);
  const l = frame - at;
  if (l < 0) return null;
  const p = interpolate(l, [1, 11], [0, 1], {...clamp, easing: easeInOut});
  const W = 240;
  const s = interpolate(p, [0, 1], [1, (W - 24) / 1080]);
  const left = interpolate(p, [0, 1], [-12 * 0, x]);
  const top = interpolate(p, [0, 1], [0, y]);
  return (
    <div
      style={{
        position: 'absolute',
        left,
        top,
        width: 1080 * s + 24,
        height: 1920 * s * 0.62 + 80,
        background: '#fff',
        padding: 12,
        boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
        rotate: `${r * p}deg`,
        opacity: interpolate(p, [0, 0.15], [0.0, 1], clamp),
      }}
    >
      <div style={{width: 1080 * s, height: 1920 * s * 0.62, overflow: 'hidden', position: 'relative'}}>
        <div style={{position: 'absolute', left: 0, top: -1920 * s * 0.2, width: 1080, height: 1920, transformOrigin: '0 0', scale: String(s)}}>
          <Freeze frame={at}>
            <Live from={0} to={T.end} />
          </Freeze>
        </div>
      </div>
    </div>
  );
};

export const Visor: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.s10 || t >= T.s11) return null;
  const l = frame - T.s10 * F;
  const o = interpolate(l, [0, 5], [0, 1], clamp);
  const corner = (x: number, y: number, rot: number) => (
    <div style={{position: 'absolute', left: x, top: y, width: 90, height: 90, borderLeft: '7px solid #fff', borderTop: '7px solid #fff', rotate: `${rot}deg`, opacity: o, filter: 'drop-shadow(0 0 6px rgba(0,0,0,0.5))'}} />
  );
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      {corner(50, 70, 0)}
      {corner(940, 70, 90)}
      {corner(940, 1760, 180)}
      {corner(50, 1760, 270)}
      <div style={{position: 'absolute', left: 170, top: 92, display: 'flex', alignItems: 'center', gap: 14, fontSize: 36, fontWeight: 800, color: '#fff', opacity: o}}>
        <div style={{width: 22, height: 22, borderRadius: 11, background: '#B701FC', opacity: Math.floor(l / 8) % 2 ? 0.3 : 1, boxShadow: '0 0 14px #B701FC'}} />
        REC
      </div>
      <div style={{position: 'absolute', right: 170, top: 92, fontSize: 32, fontWeight: 700, color: 'rgba(255,255,255,0.9)', opacity: o}}>4K · 30 FPS</div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1700, textAlign: 'center', fontSize: 32, fontWeight: 700, color: 'rgba(255,255,255,0.9)', letterSpacing: '0.08em', opacity: o}}>1/125 &nbsp; f2.8 &nbsp; ISO 400</div>
      {SHOTS.map((s) => (
        <Polaroid key={s.t} {...s} />
      ))}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- embudo + anuncio
const Embudo: React.FC = () => {
  const frame = useCurrentFrame();
  const l = frame - T.s11 * F;
  const n = Math.round(interpolate(frame, [ws(96) * F, ws(98) * F + 10], [0, 127], {...clamp, easing: easeOut}));
  const dots = Array.from({length: 26}, (_, i) => {
    const start = i * 3.2;
    const k = (l - start) / 26;
    if (k < 0 || k > 1) return null;
    const x0 = 200 + rand(i * 7.3) * 680;
    const x = interpolate(k, [0, 0.55, 1], [x0, 540 + (x0 - 540) * 0.22, 540]);
    const y = interpolate(k, [0, 1], [230, 960], {easing: (v) => v * v});
    const out = k > 0.82;
    return (
      <div
        key={i}
        style={{
          position: 'absolute',
          left: x - 22,
          top: y - 22,
          width: 44,
          height: 44,
          borderRadius: 22,
          background: out ? '#FFD95A' : '#fff',
          color: '#3D0080',
          display: 'grid',
          placeItems: 'center',
          fontSize: 28,
          fontWeight: 900,
          boxShadow: out ? '0 0 18px rgba(255,217,90,0.8)' : '0 0 12px rgba(255,255,255,0.6)',
        }}
      >
        {out ? '$' : ''}
      </div>
    );
  });
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 0, right: 0, top: 120, display: 'flex', justifyContent: 'center', scale: String(pop(l - 4))}}>
        <div style={{padding: '10px 34px 14px', borderRadius: 18, background: '#fff', color: C.purple, fontSize: 56, fontWeight: 900, rotate: '-2deg', boxShadow: `0 7px 0 ${C.purpleShadow}`}}>ESTRATEGIA</div>
      </div>
      <svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, opacity: interpolate(l, [0, 6], [0, 1], clamp)}}>
        <defs>
          <linearGradient id="fun" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#B701FC" />
            <stop offset="1" stopColor="#3D0080" />
          </linearGradient>
        </defs>
        <path d="M150 300 L930 300 L640 800 L640 960 L440 960 L440 800 Z" fill="url(#fun)" fillOpacity="0.55" stroke="#fff" strokeWidth="8" strokeLinejoin="round" />
      </svg>
      {dots}
      <div style={{position: 'absolute', left: 0, right: 0, top: 440, textAlign: 'center', color: '#fff', fontWeight: 900, fontSize: 150, lineHeight: 1, letterSpacing: '-0.04em', textShadow: `0 6px 0 ${C.purpleShadow}`, opacity: interpolate(frame - ws(96) * F, [-4, 2], [0, 1], clamp)}}>
        +{n}
        <div style={{fontSize: 48, fontWeight: 800, letterSpacing: '0.1em', marginTop: 6}}>CLIENTES</div>
      </div>
    </AbsoluteFill>
  );
};

const Anuncio: React.FC = () => {
  const frame = useCurrentFrame();
  const a = Math.round((ws(99) - 0.05) * F);
  const l = frame - a;
  const click = Math.round((ws(101) + 0.05) * F);
  const cl = frame - click;
  const cur = interpolate(frame, [click - 12, click - 1], [0, 1], {...clamp, easing: easeInOut});
  const press = interpolate(cl, [0, 2, 6], [1, 0.92, 1], clamp);
  const toast = interpolate(cl, [2, 8], [0, 1], {...clamp, easing: easeOut});
  return (
    <AbsoluteFill style={{translate: `${interpolate(l, [0, 8], [1080, 0], {...clamp, easing: easeOut})}px 0`}}>
      <div style={{position: 'absolute', left: 120, top: 170, width: 840, borderRadius: 40, background: '#fff', overflow: 'hidden', boxShadow: '0 30px 70px rgba(0,0,0,0.6)'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 22, padding: '26px 30px'}}>
          <div style={{width: 84, height: 84, borderRadius: 42, background: C.purpleGrad}} />
          <div>
            <div style={{fontSize: 38, fontWeight: 800, color: '#111'}}>Tu negocio</div>
            <div style={{fontSize: 28, fontWeight: 600, color: '#888'}}>Publicidad</div>
          </div>
        </div>
        <div style={{height: 470, background: '#000'}}>
          <Sequence from={a} layout="none">
            <Video src={staticFile('broll/b9_cliente.mp4')} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
          </Sequence>
        </div>
        <div style={{margin: 26, height: 112, borderRadius: 24, background: C.purpleGrad, display: 'grid', placeItems: 'center', color: '#fff', fontSize: 50, fontWeight: 900, scale: String(press), boxShadow: cl >= 0 ? `0 0 0 ${interpolate(cl, [0, 10], [0, 40], clamp)}px rgba(183,1,252,${interpolate(cl, [0, 10], [0.5, 0], clamp)})` : undefined}}>
          Comprar ahora
        </div>
      </div>
      {/* cursor */}
      <svg viewBox="0 0 24 24" style={{position: 'absolute', width: 110, height: 110, left: interpolate(cur, [0, 1], [980, 600]), top: interpolate(cur, [0, 1], [1260, 900]), scale: String(press), filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.6))', opacity: interpolate(frame, [click - 14, click - 10], [0, 1], clamp)}}>
        <path d="M5 2 L5 19 L9.5 15 L12.5 22 L15.5 20.8 L12.6 14 L18.5 14 Z" fill="#fff" stroke="#111" strokeWidth="1.3" strokeLinejoin="round" />
      </svg>
      <div style={{position: 'absolute', left: 560, top: 90, padding: '16px 30px', borderRadius: 26, background: '#fff', fontFamily: OUTFIT, fontSize: 44, fontWeight: 900, color: C.purple, boxShadow: '0 14px 30px rgba(0,0,0,0.45)', opacity: toast, scale: String(interpolate(toast, [0, 1], [0.6, 1])), rotate: '4deg'}}>
        +1 venta 💸
      </div>
    </AbsoluteFill>
  );
};

export const EmbudoAnuncio: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.s11 || t >= T.s12) return null;
  const l = frame - T.s11 * F;
  const zin = interpolate(l, [0, 7], [0, 1], {...clamp, easing: easeOut});
  const fout = interpolate(frame, [(ws(99) - 0.05) * F, (ws(99) - 0.05) * F + 8], [0, 1], {...clamp, easing: easeInOut});
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 35%, #2A0055 0%, #14002B 45%, #0B0B0B 100%)', opacity: interpolate(l, [0, 3], [0, 1], clamp)}} />
      <AbsoluteFill style={{scale: String(interpolate(zin, [0, 1], [1.35, 1])), filter: zin < 1 ? `blur(${(1 - zin) * 16}px)` : undefined, opacity: zin}}>
        <AbsoluteFill style={{translate: `${-fout * 1080}px 0`}}>
          <Embudo />
        </AbsoluteFill>
        <Anuncio />
      </AbsoluteFill>
      <Bubble from={T.s11} to={T.s12} cx={860} cy={1630} d={340} k={0.58} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- botones A/B
export const Botones: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.s13 || t >= T.end) return null;
  const chip = frame - ws(108) * F;
  const A = frame - ws(114) * F;
  const B = frame - ws(119) * F;
  const click = Math.round((ws(120) + 0.12) * F);
  const cl = frame - click;
  const cur = interpolate(frame, [click - 9, click - 1], [0, 1], {...clamp, easing: easeInOut});
  const chosen = cl >= 0;
  const btn = (l: number, label: string, x: number, on: boolean, good: boolean) =>
    l < 0 ? null : (
      <div
        style={{
          position: 'absolute',
          left: x,
          top: 300,
          width: 460,
          height: 150,
          borderRadius: 34,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 18,
          fontSize: 58,
          fontWeight: 900,
          letterSpacing: '-0.03em',
          color: '#fff',
          background: on ? C.purpleGrad : good ? 'rgba(20,20,20,0.75)' : 'rgba(40,40,40,0.8)',
          border: on ? '5px solid #fff' : `5px solid ${good ? C.purpleTop : '#777'}`,
          boxShadow: on ? `0 8px 0 ${C.purpleShadow}, 0 0 50px ${C.purpleGlow}` : '0 12px 30px rgba(0,0,0,0.5)',
          scale: String(pop(l) * (on ? interpolate(cl, [0, 3, 7], [1, 1.1, 1], clamp) : 1)),
          opacity: !good && chosen ? 0.45 : 1,
        }}
      >
        {good ? '✓' : '✕'} {label}
      </div>
    );
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      {chip >= 0 ? (
        <div style={{position: 'absolute', left: 0, right: 0, top: 170, display: 'flex', justifyContent: 'center', scale: String(pop(chip))}}>
          <div style={{padding: '10px 32px 14px', borderRadius: 40, background: '#fff', color: '#111', fontSize: 50, fontWeight: 900, letterSpacing: '-0.02em', boxShadow: '0 10px 30px rgba(0,0,0,0.4)'}}>¿Tu negocio cuál es?</div>
        </div>
      ) : null}
      {btn(A, 'NO VENDE', 50, false, false)}
      {btn(B, 'SÍ VENDE', 570, chosen, true)}
      {chosen
        ? Array.from({length: 10}, (_, i) => {
            const ang = (i / 10) * Math.PI * 2;
            const r = interpolate(cl, [0, 12], [40, 260], {...clamp, easing: easeOut});
            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: 800 + Math.cos(ang) * r - 12,
                  top: 375 + Math.sin(ang) * r * 0.6 - 12,
                  width: 24,
                  height: 24,
                  borderRadius: 12,
                  background: i % 2 ? '#fff' : '#B701FC',
                  opacity: interpolate(cl, [6, 14], [1, 0], clamp),
                  boxShadow: '0 0 12px rgba(183,1,252,0.9)',
                }}
              />
            );
          })
        : null}
      {B >= 0 ? (
        <svg viewBox="0 0 24 24" style={{position: 'absolute', width: 100, height: 100, left: interpolate(cur, [0, 1], [1000, 820]), top: interpolate(cur, [0, 1], [620, 390]), filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.6))'}}>
          <path d="M5 2 L5 19 L9.5 15 L12.5 22 L15.5 20.8 L12.6 14 L18.5 14 Z" fill="#fff" stroke="#111" strokeWidth="1.3" strokeLinejoin="round" />
        </svg>
      ) : null}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- cierre
export const Cierre: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  if (t < T.end - 0.02) return null;
  const l = frame - T.end * F;
  const text = 'VENDE 🔥';
  const typed = Math.floor(interpolate(frame, [(T.end + 0.45) * F, (T.end + 0.95) * F], [0, [...text].length], clamp));
  const sent = frame - (T.end + 1.05) * F;
  const fade = interpolate(frame, [(T.end + 2.05) * F, (T.end + 2.35) * F], [0, 1], clamp);
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <Marquee rows={['COMENTA', 'VENDE', 'COMENTA', 'VENDE', 'COMENTA']} t0={T.end} tone="deep" />
      <AbsoluteFill style={{translate: `0 ${interpolate(l, [0, 10], [0, 250], {...clamp, easing: easeOut})}px`, scale: String(interpolate(l, [0, 10], [1, 0.86], {...clamp, easing: easeOut})), transformOrigin: '50% 100%'}}>
        <AbsoluteFill style={{filter: 'drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 0 40px rgba(150,1,253,0.9))'}}>
          <LastFrame mask="c" />
        </AbsoluteFill>
      </AbsoluteFill>
      <Img src={staticFile('img/logo_grow.png')} style={{position: 'absolute', left: 260, top: 120, width: 560, scale: String(pop(l - 2))}} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 360, textAlign: 'center', fontSize: 40, fontWeight: 700, color: 'rgba(255,255,255,0.9)', opacity: interpolate(l, [6, 12], [0, 1], clamp)}}>Escríbelo en los comentarios 👇</div>
      <div
        style={{
          position: 'absolute',
          left: 90,
          top: 430,
          width: 900,
          height: 130,
          borderRadius: 65,
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          gap: 24,
          padding: '0 18px 0 22px',
          boxShadow: sent >= 0 ? `0 0 0 6px #B701FC, 0 0 50px ${C.purpleGlow}` : '0 14px 40px rgba(0,0,0,0.45)',
          scale: String(pop(l - 6) * (sent >= 0 ? interpolate(sent, [0, 3, 7], [1, 1.05, 1], clamp) : 1)),
        }}
      >
        <div style={{width: 90, height: 90, borderRadius: 45, background: C.purpleGrad, flexShrink: 0}} />
        <div style={{flex: 1, fontSize: 54, fontWeight: 800, color: typed ? '#111' : '#9A9A9A'}}>
          {typed ? [...text].slice(0, typed).join('') : 'Añade un comentario…'}
          {typed && typed < [...text].length && Math.floor(l / 4) % 2 ? '|' : ''}
        </div>
        <div style={{width: 96, height: 96, borderRadius: 48, background: C.purpleGrad, display: 'grid', placeItems: 'center', color: '#fff', fontSize: 50, fontWeight: 900, flexShrink: 0}}>➤</div>
      </div>
      <AbsoluteFill style={{background: '#000', opacity: fade}} />
    </AbsoluteFill>
  );
};
