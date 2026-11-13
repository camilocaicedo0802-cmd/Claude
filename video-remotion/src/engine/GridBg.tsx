import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {rand} from './helpers';
import {C} from '../v1/theme';

/** Fondo negro con cuadrícula gris y cuadrados sueltos (estilo.md §5, escena "cerebro"). */
export const GridBg: React.FC<{drift?: number}> = ({drift = 0.6}) => {
  const frame = useCurrentFrame();
  const off = (frame * drift) % 90;
  return (
    <AbsoluteFill style={{background: C.black}}>
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${C.grid} 1px, transparent 1px), linear-gradient(90deg, ${C.grid} 1px, transparent 1px)`,
          backgroundSize: '90px 90px',
          backgroundPosition: `0 ${-off}px`,
          opacity: 0.9,
        }}
      />
      {Array.from({length: 14}, (_, i) => {
        const x = Math.floor(rand(i) * 12) * 90;
        const y = Math.floor(rand(i + 50) * 22) * 90 - off;
        const sz = rand(i + 9) > 0.6 ? 90 : 45;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: sz, height: sz, background: C.grid2, opacity: 0.35 + rand(i + 3) * 0.4}} />;
      })}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 35%, rgba(0,0,0,0.75) 100%)'}} />
    </AbsoluteFill>
  );
};
