import React from 'react';
import {C, W, H} from '../theme';

/**
 * Fondo editorial: gris claro + retícula de puntos (paso 30 px, Ø3 px, márgenes 120/215 px)
 * + arcos punteados grandes que giran (estilo.md §3).
 */
const arcPath = (r: number, deg: number) => {
  const a = (deg * Math.PI) / 180;
  return `M ${r} 0 A ${r} ${r} 0 0 1 ${r * Math.cos(a)} ${r * Math.sin(a)}`;
};

export const Background: React.FC<{camX: number; camY: number; arcRot: number}> = ({camX, camY, arcRot}) => {
  const gx = camX * 0.3;
  const gy = camY * 0.3;
  const ax = camX * 0.6;
  const ay = camY * 0.6;
  const arcs = [
    {cx: -80, cy: 140, r: 640, dir: 1, a: 0},
    {cx: 1180, cy: 1830, r: 700, dir: -1, a: 40},
    {cx: 1250, cy: -120, r: 560, dir: 1, a: 200},
  ];
  return (
    <div style={{position: 'absolute', inset: 0, background: C.bg, overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          left: 120,
          right: 120,
          top: 215,
          bottom: 215,
          backgroundImage: `radial-gradient(circle, ${C.dot} 1.6px, transparent 2.1px)`,
          backgroundSize: '30px 30px',
          backgroundPosition: `${gx % 30}px ${gy % 30}px`,
          WebkitMaskImage: 'radial-gradient(ellipse 75% 70% at 50% 50%, #000 55%, transparent 100%)',
          maskImage: 'radial-gradient(ellipse 75% 70% at 50% 50%, #000 55%, transparent 100%)',
        }}
      />
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
        {arcs.map((a, i) => (
          <g key={i} transform={`translate(${a.cx + ax} ${a.cy + ay}) rotate(${a.a + arcRot * a.dir})`}>
            <path d={arcPath(a.r, 115)} fill="none" stroke={C.arc} strokeWidth={3.5} strokeDasharray="15 11" strokeLinecap="round" opacity={0.75} />
          </g>
        ))}
      </svg>
    </div>
  );
};
