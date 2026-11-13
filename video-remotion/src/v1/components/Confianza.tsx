import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES} from '../data';
import {clamp, easeInOut, easeOut} from '../helpers';
import {C, OUTFIT} from '../theme';
import {GridBg} from './GridBg';

type Win = {src: string; x: number; y: number; w: number; at: number; par: number};
// corrección §10.2: aquí NO va la cara del protagonista; son clientes y escenas ajenas
const WINS: Win[] = [
  {src: 'img/otros_ojos1.jpg', x: 60, y: 520, w: 430, at: 0.1, par: 1},
  {src: 'img/otros_movil.jpg', x: 660, y: 450, w: 360, at: 0.25, par: -1.4},
  {src: 'img/otros_cara1.jpg', x: 270, y: 700, w: 540, at: 0.0, par: 0.6},
  {src: 'img/otros_sinventas.jpg', x: 70, y: 1180, w: 300, at: 0.4, par: -0.8},
  {src: 'img/otros_cara2.jpg', x: 720, y: 1040, w: 300, at: 0.55, par: 1.2},
];

const Window: React.FC<{w: Win; start: number; end: number}> = ({w, start, end}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(frame - (start + w.at) * fps, [0, 8], [0, 1], {...clamp, easing: easeOut});
  const out = interpolate(frame, [end * fps - 6, end * fps], [0, 1], clamp);
  const t = frame - start * fps;
  return (
    <div
      style={{
        position: 'absolute',
        left: w.x,
        top: w.y + Math.sin(t / 20) * 10 * w.par,
        width: w.w,
        border: '8px solid #FFFFFF',
        boxShadow: '0 20px 50px rgba(0,0,0,0.6)',
        background: '#fff',
        opacity: p * (1 - out),
        scale: String(interpolate(p, [0, 1], [0.8, 1]) * (1 + t * 0.0008)),
        translate: `${t * 0.25 * w.par}px ${interpolate(p, [0, 1], [60, 0])}px`,
        filter: p < 1 ? `blur(${10 * (1 - p)}px)` : undefined,
      }}
    >
      {/* barra de ventana */}
      <div style={{height: 22, background: '#EDEDED', display: 'flex', alignItems: 'center', gap: 6, paddingLeft: 8}}>
        {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <div key={c} style={{width: 9, height: 9, borderRadius: 5, background: c}} />)}
      </div>
      <Img src={staticFile(w.src)} style={{width: '100%', display: 'block'}} />
    </div>
  );
};

const BigWord: React.FC<{text: string; at: number; until: number; size: number}> = ({text, at, until, size}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(frame - at * fps, [0, 6], [0, 1], {...clamp, easing: easeOut});
  const out = interpolate(frame, [until * fps - 4, until * fps], [0, 1], clamp);
  const strike = interpolate(frame - (at + 0.35) * fps, [0, 7], [0, 1], {...clamp, easing: easeInOut});
  if (p <= 0 || out >= 1) return null;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 330, translate: '0 -50%', display: 'flex', justifyContent: 'center', opacity: p * (1 - out), filter: `blur(${16 * (1 - p) + 12 * out}px)`}}>
      <div style={{position: 'relative', scale: String(interpolate(p, [0, 1], [1.3, 1]))}}>
        <span style={{fontFamily: OUTFIT, fontWeight: 900, fontSize: size, letterSpacing: '-0.03em', backgroundImage: C.purpleGrad, WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent', color: 'transparent', filter: `drop-shadow(0 4px 0 ${C.purpleShadow}) drop-shadow(0 0 22px ${C.purpleGlow})`}}>{text}</span>
        <div style={{position: 'absolute', left: -20, right: -20, top: '52%', height: 14, background: C.white, borderRadius: 7, transformOrigin: 'left', scale: `${strike} 1`, rotate: '-3deg', boxShadow: '0 0 14px rgba(255,255,255,0.6)'}} />
      </div>
    </div>
  );
};

/** Escena "CONFIANZA / PROFESIONALISMO": fondo cuadrícula, ventanas B/N con su cara y nota escribiéndose. */
export const Confianza: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sc = SCENES.confianza;
  if (frame < sc.start * fps || frame >= sc.end * fps) return null;
  const chars = Math.floor(Math.max(0, frame / fps - sc.noteStart) * 18);
  const txt = sc.noteText.slice(0, chars);
  const noteIn = interpolate(frame - sc.noteStart * fps, [0, 8], [0, 1], {...clamp, easing: easeOut});
  return (
    <AbsoluteFill style={{fontFamily: OUTFIT}}>
      <GridBg />
      {WINS.map((w) => <Window key={w.src} w={w} start={sc.start} end={sc.end} />)}
      <BigWord text="CONFIANZA" at={sc.t1} until={sc.t2} size={150} />
      <BigWord text="PROFESIONALISMO" at={sc.t2} until={sc.end} size={104} />
      {/* nota tipo macOS */}
      <div
        style={{
          position: 'absolute',
          left: 120,
          right: 120,
          top: 1560,
          borderRadius: 18,
          background: 'rgba(30,30,30,0.92)',
          boxShadow: '0 20px 50px rgba(0,0,0,0.6)',
          padding: '18px 28px 26px',
          opacity: noteIn,
          translate: `0 ${interpolate(noteIn, [0, 1], [60, 0])}px`,
        }}
      >
        <div style={{display: 'flex', gap: 8, marginBottom: 14}}>
          {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <div key={c} style={{width: 14, height: 14, borderRadius: 7, background: c}} />)}
          <div style={{marginLeft: 'auto', color: '#8A8A8A', fontSize: 18, fontWeight: 500}}>Notas · hoy</div>
        </div>
        <div style={{color: '#fff', fontSize: 34, fontWeight: 500, lineHeight: 1.25, minHeight: 86}}>
          {txt}
          <span style={{opacity: Math.floor(frame / 8) % 2 ? 0 : 1, color: '#FEBC2E'}}>|</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
