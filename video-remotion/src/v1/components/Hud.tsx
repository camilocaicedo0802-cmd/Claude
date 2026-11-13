import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {SCENES} from '../data';
import {clamp, easeOut, rand} from '../helpers';
import {C, OUTFIT} from '../theme';

type Pos = 'tl' | 'tr' | 'bl' | 'br';
/** Esquina de visor dibujada dentro de una caja (left/top/width/height). */
const Corners: React.FC<{x: number; y: number; w: number; h: number; size: number; color: string; width?: number}> = ({x, y, w, h, size, color, width = 3}) => {
  const b = `${width}px solid ${color}`;
  const pos: Record<Pos, React.CSSProperties> = {
    tl: {left: 0, top: 0, borderLeft: b, borderTop: b},
    tr: {right: 0, top: 0, borderRight: b, borderTop: b},
    bl: {left: 0, bottom: 0, borderLeft: b, borderBottom: b},
    br: {right: 0, bottom: 0, borderRight: b, borderBottom: b},
  };
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h}}>
      {(Object.keys(pos) as Pos[]).map((k) => (
        <div key={k} style={{position: 'absolute', width: size, height: size, ...pos[k]}} />
      ))}
    </div>
  );
};

/** Visor tipo cámara / escáner sobre el B-roll: "en segundos deciden si confiar en ti". */
export const Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sc = SCENES.hud;
  const s = sc.start * fps;
  const e = sc.end * fps;
  if (frame < s || frame >= e) return null;
  const local = frame - s;
  const pin = interpolate(local, [0, 8], [0, 1], {...clamp, easing: easeOut});
  const secs = Math.min(3, (frame - s) / fps * (3 / ((sc.noConfiar - sc.start) * 0.9)));
  const no = frame >= sc.noConfiar * fps;
  const ok = frame >= sc.confiar * fps && !no;
  const boxColor = no ? C.purpleTop : 'rgba(255,255,255,0.85)';
  // caja de seguimiento sobre la cara
  const bx = 300 + Math.sin(local / 9) * 6;
  const by = 300 + Math.cos(local / 11) * 6;
  const bw = 480;
  const bh = 560;
  const shake = no ? (rand(frame) - 0.5) * 10 * interpolate(frame - sc.noConfiar * fps, [0, 8], [1, 0], clamp) : 0;
  return (
    <AbsoluteFill style={{opacity: pin, fontFamily: OUTFIT}}>
      {/* esquinas del visor */}
      <Corners x={60} y={60} w={960} h={1800} size={70} color="rgba(255,255,255,0.6)" />
      {/* REC + tiempo */}
      <div style={{position: 'absolute', left: 90, top: 92, display: 'flex', alignItems: 'center', gap: 14, color: 'rgba(255,255,255,0.85)', fontSize: 30, fontWeight: 600, letterSpacing: '0.04em'}}>
        <div style={{width: 18, height: 18, borderRadius: 9, background: C.purpleTop, opacity: Math.floor(local / 12) % 2 ? 0.3 : 1}} />
        REC
      </div>
      <div style={{position: 'absolute', right: 90, top: 86, color: '#fff', fontSize: 44, fontWeight: 800, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em'}}>
        00:0{Math.floor(secs)}.{String(Math.floor((secs % 1) * 100)).padStart(2, '0')} s
      </div>
      {/* arco giratorio */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <circle cx={540} cy={580} r={360} fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth={2} strokeDasharray="180 90 40 300" transform={`rotate(${local * 1.6} 540 580)`} />
        <circle cx={540} cy={580} r={410} fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth={1.5} strokeDasharray="60 140" transform={`rotate(${-local * 0.9} 540 580)`} />
      </svg>
      {/* caja de la cara */}
      <div style={{position: 'absolute', left: bx + shake, top: by, width: bw, height: bh}}>
        <Corners x={0} y={0} w={bw} h={bh} size={56} color={boxColor} width={4} />
        <div style={{position: 'absolute', left: 0, top: -54, fontSize: 26, fontWeight: 600, color: boxColor, letterSpacing: '0.06em'}}>
          {no ? '✕  NO CONFÍA' : ok ? 'ANALIZANDO…  CONFIANZA ?' : 'CLIENTE · ANALIZANDO'}
        </div>
        {/* línea de escaneo */}
        <div style={{position: 'absolute', left: 8, right: 8, height: 2, top: ((local * 14) % bh), background: no ? C.purpleTop : 'rgba(255,255,255,0.6)', boxShadow: `0 0 12px ${no ? C.purpleTop : '#fff'}`}} />
      </div>
      {/* números de telemetría */}
      {[0, 1, 2, 3].map((i) => (
        <div key={i} style={{position: 'absolute', left: i % 2 ? 760 : 90, top: 1250 + i * 70, fontFamily: 'monospace', fontSize: 22, color: 'rgba(255,255,255,0.5)'}}>
          {(rand(i + Math.floor(local / 3)) * 180 - 90).toFixed(7)}
        </div>
      ))}
      {/* tinte rojo al "no confiar" */}
      <AbsoluteFill style={{background: C.purple, mixBlendMode: 'multiply', opacity: no ? interpolate(frame - sc.noConfiar * fps, [0, 3, 14], [0, 0.35, 0.12], clamp) : 0}} />
    </AbsoluteFill>
  );
};
