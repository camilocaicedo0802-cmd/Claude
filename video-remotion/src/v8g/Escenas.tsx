import {Audio, Video} from '@remotion/media';
import {AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOut, rand} from '../engine/helpers';
import {segLen, segmentAt, useSpec} from '../engine/spec';
import {WORDS} from '../v8/timeline';
import {ANTON, GOTHIC, INTER, P} from './fonts';
import {CUT_SCALE, GIANTS, HOOKS, ONES, SCENES, SLIDES, SPEECH, TOTAL, TWOLINES, Scene, sceneAt, ws} from './data';
import {Live} from './Live';

const F = 30;
const word = (i: number) => WORDS[i].text.replace(/[,]/g, '');
const lower = (i: number) => word(i).toLowerCase();

// ---------------------------------------------------------------- voz continua (una sola pista)
export const Voz: React.FC = () => {
  const spec = useSpec();
  return (
    <>
      {spec.segments.map((s) => (
        <Sequence key={s.idx} from={s.start} durationInFrames={segLen(s)}>
          <Audio src={staticFile(`clips/${spec.clipPrefix}_${s.take}.mp4`)} trimBefore={s.srcIn} />
        </Sequence>
      ))}
    </>
  );
};

// ---------------------------------------------------------------- fondos de cada escenario
export const FondoEstudio: React.FC = () => (
  <AbsoluteFill style={{background: 'radial-gradient(ellipse 80% 55% at 50% 38%, #A43BFF 0%, #7A06E6 32%, #3E0080 68%, #16002E 100%)'}}>
    <AbsoluteFill style={{background: 'linear-gradient(180deg, transparent 62%, rgba(10,0,25,0.55) 100%)'}} />
  </AbsoluteFill>
);
export const FondoBlanco: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, #FFFFFF 0%, #F4F4F6 60%, #E6E6EA 100%)'}} />;
export const FondoEscenario: React.FC = () => (
  <AbsoluteFill style={{background: '#06040C'}}>
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(190,160,255,0.28) 0%, rgba(120,80,220,0.10) 40%, transparent 70%)', clipPath: 'polygon(38% 0, 62% 0, 92% 100%, 8% 100%)', filter: 'blur(30px)'}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 48% 9% at 50% 86%, rgba(215,205,255,0.85) 0%, rgba(150,120,230,0.35) 55%, transparent 100%)'}} />
  </AbsoluteFill>
);
export const FondoLamina: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, #B01CFF 0%, #8A00F0 40%, #5600B0 100%)'}} />;
export const FondoUI: React.FC<{light?: boolean}> = ({light}) => <AbsoluteFill style={{background: light ? '#EEF0F3' : P.ui}} />;
export const Fondo3D: React.FC = () => (
  <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, #FFFFFF 0%, #E9EDF1 55%, #C9D1D8 100%)'}}>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 40% 6% at 50% 95%, rgba(60,70,80,0.35) 0%, transparent 100%)'}} />
  </AbsoluteFill>
);

// ---------------------------------------------------------------- la persona
const maskUrl = (take: string, f: number) => staticFile(`mascaras/${take}/c_${String(f).padStart(5, '0')}.png`);

/** Recorte de la persona en un escenario (escala anclada abajo al centro). */
export const Recorte: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const s = CUT_SCALE[scene.kind] ?? 1;
  const push = interpolate(frame, [scene.from * F, scene.to * F], [1, 1.04], clamp);
  return (
    <AbsoluteFill style={{scale: String(s * push), transformOrigin: '50% 100%'}}>
      {/* la parte baja (mesa, portátil, restos de pared) se funde con el escenario */}
      <AbsoluteFill style={{maskImage: 'linear-gradient(180deg, #000 0%, #000 72%, transparent 90%)', WebkitMaskImage: 'linear-gradient(180deg, #000 0%, #000 72%, transparent 90%)'}}>
        <Live from={scene.from} to={scene.to} mask="c" />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Arranque del referente: f2-5 silueta blanca de la persona. */
export const Silueta: React.FC = () => {
  const spec = useSpec();
  const frame = useCurrentFrame();
  if (frame < 2 || frame > 5) return null;
  const seg = segmentAt(spec, frame)!;
  const m = maskUrl(seg.take, seg.srcIn + frame - seg.start);
  return (
    <AbsoluteFill style={{scale: String(CUT_SCALE.estudio), transformOrigin: '50% 100%'}}>
      <AbsoluteFill style={{background: '#FFFFFF', maskImage: `url(${m})`, WebkitMaskImage: `url(${m})`, maskSize: '100% 100%', WebkitMaskSize: '100% 100%'}} />
    </AbsoluteFill>
  );
};

/** Plano en la sala (su grabación), con oscurecido para los subtítulos de una palabra. */
export const Sala: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const push = interpolate(frame, [scene.from * F, scene.to * F], [1, 1.03], clamp);
  return (
    <AbsoluteFill style={{scale: String(push), transformOrigin: '50% 42%'}}>
      <Live from={scene.from} to={scene.to} />
      {scene.dim ? <AbsoluteFill style={{background: 'rgba(0,0,0,0.4)'}} /> : null}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- textos
const enter = (frame: number, at: number, n = 4) => interpolate(frame - at * F, [0, n], [0, 1], {...clamp, easing: easeOut});
const glowW = (g: number) => `0 0 ${6 * g}px rgba(255,255,255,0.9), 0 0 ${18 * g}px rgba(255,255,255,0.55), 0 0 ${42 * g}px rgba(255,255,255,0.3)`;

/** Palabras del gancho alrededor de la cabeza. layer: detrás o delante de la persona. */
export const Ganchos: React.FC<{layer: 'behind' | 'front'}> = ({layer}) => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const sc = sceneAt(t);
  if (sc.kind !== 'estudio') return null;
  return (
    <AbsoluteFill>
      {HOOKS.filter((h) => !!h.behind === (layer === 'behind') && ws(h.i[0]) >= sc.from - 0.1 && ws(h.i[0]) < sc.to).map((h) => {
        const at = Math.max(ws(h.i[0]), sc.from);
        const p = enter(frame, at, 4);
        if (frame < at * F - 1) return null;
        return (
          <div
            key={h.i[0]}
            style={{
              position: 'absolute',
              left: h.x,
              top: h.y,
              translate: '-50% -50%',
              fontFamily: INTER,
              fontWeight: 700,
              fontSize: h.size,
              letterSpacing: '-0.035em',
              whiteSpace: 'nowrap',
              color: '#FFFFFF',
              textShadow: glowW(h.glow ?? 1),
              opacity: p,
              scale: String(interpolate(p, [0, 1], [1.06, 1])),
              filter: p < 1 ? `blur(${10 * (1 - p)}px)` : undefined,
            }}
          >
            {h.i.map(lower).join(' ')}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Título gigante ultracondensado detrás de la persona, con palabra pequeña encima. */
export const Gigantes: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const sc = sceneAt(t);
  const g = GIANTS.find((x) => ws(x.big) >= sc.from && ws(x.big) < sc.to);
  if (!g || (sc.kind !== 'blanco' && sc.kind !== 'escenario')) return null;
  const sAt = Math.max(ws(g.small[0]), sc.from);
  const ps = enter(frame, sAt, g.flip ? 6 : 4);
  const big = frame >= ws(g.big) * F;
  const pb = interpolate(frame - ws(g.big) * F, [0, 3], [0, 1], clamp);
  const purple = g.color === 'purple';
  return (
    <AbsoluteFill style={{alignItems: 'center'}}>
      <div style={{position: 'absolute', top: g.y, translate: '0 -50%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start'}}>
        <div
          style={{
            fontFamily: INTER,
            fontWeight: 700,
            fontSize: 56,
            letterSpacing: '-0.03em',
            color: purple ? '#FFFFFF' : P.gray,
            marginLeft: 10,
            marginBottom: -10,
            opacity: ps,
            transform: g.flip ? `perspective(600px) rotateX(${(1 - ps) * 70}deg) rotateY(${(1 - ps) * -40}deg) translateY(${(1 - ps) * -30}px)` : undefined,
            filter: ps < 1 ? `blur(${8 * (1 - ps)}px)` : undefined,
            textShadow: purple ? glowW(0.8) : undefined,
          }}
        >
          {g.small.map(lower).join(' ')}
        </div>
        {big ? (
          <div
            style={{
              fontFamily: GOTHIC,
              fontVariationSettings: "'wdth' 75",
              fontSize: g.size ?? 470,
              lineHeight: 0.86,
              letterSpacing: '-0.01em',
              color: purple ? P.purpleHi : P.gray,
              transform: `scaleY(1.2) scale(${interpolate(pb, [0, 1], [1.05, 1])})`,
              transformOrigin: '50% 30%',
              textShadow: purple ? '0 0 22px rgba(183,1,252,0.95), 0 0 70px rgba(150,1,253,0.7)' : undefined,
              filter: pb < 1 ? `blur(${3 * (1 - pb)}px)` : undefined,
            }}
          >
            {g.bigText}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Lámina morada a pantalla completa con palabras condensadas que entran de golpe. */
export const Laminas: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const s = SLIDES.find((x) => t >= x.from && t < x.to);
  if (!s) return null;
  const push = interpolate(frame, [s.from * F, s.to * F], [1, 1.05], clamp);
  return (
    <AbsoluteFill>
      <FondoLamina />
      <AbsoluteFill style={{perspective: 1400, alignItems: 'center', justifyContent: 'center'}}>
        <div style={{transform: `rotateY(-7deg) rotateX(5deg) scale(${push})`, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0}}>
          {s.words.map((w) => {
            const at = Math.max(ws(w.i), s.from);
            if (frame < at * F) return <div key={w.i} style={{height: 290}} />;
            const p = interpolate(frame - at * F, [0, 3], [0, 1], clamp);
            return (
              <div
                key={w.i}
                style={{
                  fontFamily: ANTON,
                  fontSize: Math.min(330, 1700 / Math.max(...s.words.map((x) => x.text.length))),
                  lineHeight: 0.9,
                  letterSpacing: '0.01em',
                  color: '#FFFFFF',
                  textShadow: '0 0 18px rgba(255,255,255,0.9), 0 0 50px rgba(255,255,255,0.55), 0 0 110px rgba(255,255,255,0.3)',
                  scale: String(interpolate(p, [0, 1], [1.08, 1])),
                }}
              >
                {w.text}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Subtítulo de dos líneas a la izquierda (blanco + lavanda). */
export const DosLineas: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const sc = sceneAt(t);
  const all = TWOLINES.map((b) => {
    const ids = [...b.l1, ...b.l2];
    const s = WORDS[ids[0]].s - 0.04;
    return {b, s, e: Math.min(WORDS[ids[ids.length - 1]].e + 0.4, sc.to)};
  });
  const cur = all.find((x, k) => t >= x.s && t < Math.min(x.e, all[k + 1]?.s ?? 999));
  if (!cur || sc.kind !== 'sala') return null;
  const line = (ids: number[], color: string, dx: number, y: number) => (
    <div style={{position: 'absolute', left: 90 + dx, top: y, display: 'flex', gap: 16, fontFamily: INTER, fontWeight: 700, fontSize: 66, letterSpacing: '-0.035em', color, textShadow: '0 3px 14px rgba(0,0,0,0.55)'}}>
      {ids.map((i) => {
        const p = enter(frame, WORDS[i].s, 4);
        if (frame < WORDS[i].s * F - 1) return <span key={i} style={{opacity: 0}}>{lower(i)}</span>;
        return (
          <span key={i} style={{opacity: p, translate: `${(1 - p) * -14}px 0`, filter: p < 1 ? `blur(${8 * (1 - p)}px)` : undefined, display: 'inline-block'}}>
            {lower(i)}
          </span>
        );
      })}
    </div>
  );
  return (
    <AbsoluteFill>
      {line(cur.b.l1, '#FFFFFF', 0, 1385)}
      {line(cur.b.l2, P.lavender, 110, 1458)}
    </AbsoluteFill>
  );
};

/** Una palabra cada vez: la nueva aparece abajo-centro y la anterior sube y se desvanece. */
const SIZES = [56, 80, 116];
export const UnaPalabra: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / F;
  const sc = sceneAt(t);
  const k = ONES.findIndex((o, j) => t >= ws(o.i[0]) - 0.03 && t < Math.min(ONES[j + 1] ? ws(ONES[j + 1].i[0]) - 0.03 : 999, WORDS[o.i[o.i.length - 1]].e + 0.6, sc.to));
  if (k < 0 || ws(ONES[k].i[0]) < sc.from - 0.05) return null;
  const render = (j: number, role: 'cur' | 'prev') => {
    const o = ONES[j];
    const at = ws(o.i[0]);
    const p = enter(frame, at, 3);
    const out = role === 'prev' ? interpolate(frame - (ws(ONES[j + 1].i[0]) - 0.03) * F, [0, 4], [0, 1], clamp) : 0;
    if (role === 'prev' && out >= 1) return null;
    const lav = o.w === 2 && j % 2 === 1;
    return (
      <div
        key={j}
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 1460 - out * 70,
          translate: '0 -50%',
          textAlign: 'center',
          fontFamily: INTER,
          fontWeight: 700,
          fontSize: SIZES[o.w],
          letterSpacing: '-0.035em',
          color: lav ? P.lavender : '#FFFFFF',
          textShadow: '0 0 14px rgba(255,255,255,0.25), 0 4px 16px rgba(0,0,0,0.55)',
          opacity: (role === 'cur' ? p : 1) * (1 - out),
          scale: String(interpolate(p, [0, 1], [1.05, 1]) * (1 - out * 0.15)),
          filter: role === 'cur' && p < 1 ? `blur(${7 * (1 - p)}px)` : undefined,
        }}
      >
        {o.i.map(lower).join(' ')}
      </div>
    );
  };
  const prevOk = k > 0 && ws(ONES[k].i[0]) - ws(ONES[k - 1].i[0]) < 1.2 && ws(ONES[k - 1].i[0]) >= sc.from;
  return (
    <AbsoluteFill>
      {prevOk ? render(k - 1, 'prev') : null}
      {render(k, 'cur')}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- palabras 3D voladoras
const FIELD = Array.from({length: 46}, (_, i) => ({
  x: (rand(i * 3.1) - 0.5) * 1700,
  y: (rand(i * 5.3 + 1) - 0.5) * 2100,
  z: -1700 + rand(i * 7.7 + 2) * 2300,
  ry: (rand(i * 2.3 + 3) - 0.5) * 140,
  rx: (rand(i * 4.1 + 4) - 0.5) * 50,
  rz: (rand(i * 6.7 + 5) - 0.5) * 30,
  size: 70 + rand(i * 8.9 + 6) * 150,
  spin: (rand(i * 9.1 + 7) - 0.5) * 40,
}));
export const Palabras3D: React.FC<{scene: Scene; layer: 'behind' | 'front'}> = ({scene, layer}) => {
  const frame = useCurrentFrame();
  const q = interpolate(frame, [scene.from * F, scene.to * F], [0, 1], clamp);
  const orbit = interpolate(q, [0, 1], [-22, 28]);
  const dolly = interpolate(q, [0, 1], [0, 380]);
  const items = FIELD.filter((w) => (layer === 'front' ? w.z + dolly >= 0 && (Math.abs(w.x) > 560 || w.y > 650) : w.z + dolly < 0 || !(Math.abs(w.x) > 560 || w.y > 650)));
  return (
    <AbsoluteFill style={{perspective: 1100, perspectiveOrigin: '50% 45%'}}>
      <div style={{position: 'absolute', left: 540, top: 900, transformStyle: 'preserve-3d', transform: `translateZ(${dolly}px) rotateY(${orbit}deg)`}}>
        {items.map((w, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              transform: `translate3d(${w.x}px, ${w.y}px, ${w.z}px) rotateY(${w.ry + w.spin * q}deg) rotateX(${w.rx}deg) rotateZ(${w.rz}deg)`,
              translate: '-50% -50%',
              fontFamily: ANTON,
              fontSize: w.size,
              whiteSpace: 'nowrap',
              color: '#8C939B',
              textShadow: Array.from({length: 9}, (_, k) => `${k + 1}px ${k + 1}px 0 ${k < 4 ? '#6F767E' : '#575D64'}`).join(', '),
              filter: layer === 'front' ? 'blur(3px)' : w.z < -1100 ? 'blur(2px)' : undefined,
              opacity: 0.95,
            }}
          >
            {scene.word3d}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- B-roll a pantalla completa
export const Broll: React.FC<{scene: Scene}> = ({scene}) => (
  <AbsoluteFill>
    <Sequence from={Math.round(scene.from * F)} layout="none">
      <Video src={staticFile(scene.src!)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
    </Sequence>
    <AbsoluteFill style={{background: 'rgba(0,0,0,0.25)'}} />
  </AbsoluteFill>
);

// ---------------------------------------------------------------- cierre
export const Cierre: React.FC = () => {
  const frame = useCurrentFrame();
  const l = frame - SPEECH * F;
  if (l < 0) return null;
  const p = interpolate(l, [0, 8], [0, 1], {...clamp, easing: easeOut});
  const fade = interpolate(frame, [(TOTAL - 0.4) * F, TOTAL * F], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <FondoEstudio />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <Img src={staticFile('img/logo_grow.png')} style={{width: 780, opacity: p, scale: String(interpolate(p, [0, 1], [1.08, 1]) * (1 + l * 0.0012)), filter: `blur(${(1 - p) * 10}px) drop-shadow(0 0 30px rgba(255,255,255,0.35))`}} />
        <div style={{marginTop: 30, fontFamily: INTER, fontWeight: 700, fontSize: 46, letterSpacing: '-0.02em', color: '#FFFFFF', opacity: interpolate(l, [8, 14], [0, 1], clamp), textShadow: glowW(0.7)}}>@growmarketingpro_</div>
      </AbsoluteFill>
      <AbsoluteFill style={{background: '#000', opacity: fade}} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- transición: destello blanco del gancho al plano blanco
export const Destello: React.FC = () => {
  const frame = useCurrentFrame();
  const a = SCENES[1].from * F;
  const v = Math.max(interpolate(frame, [a - 2, a], [0, 1], clamp) * (frame < a ? 1 : 0), frame >= a ? interpolate(frame - a, [0, 6], [1, 0], {...clamp, easing: easeInOut}) : 0);
  return v > 0.01 ? <AbsoluteFill style={{background: '#FFFFFF', opacity: v}} /> : null;
};

export {SPEECH, rand};
