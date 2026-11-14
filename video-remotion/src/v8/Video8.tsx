import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {rand} from '../engine/helpers';
import {Sonido} from '../engine/Sonido';
import {SpecContext} from '../engine/spec';
import {Title} from '../engine/Title';
import {Destello, Hoja, Papel} from './Collage';
import {DESTELLOS, HOJAS, SHAKES, SPEC_D, TITLES} from './data';
import {Cierre, Escenas, Persona} from './Escenas';
import {PersonCut, SmallSubs} from './Subs';

const F = 30;

export const Video8: React.FC = () => {
  const frame = useCurrentFrame();
  let sx = 0;
  let sy = 0;
  for (const t of SHAKES) {
    const l = frame - t * F;
    if (l >= 0 && l < 9) {
      const a = 16 * (1 - l / 9);
      sx = (rand(frame * 1.7) - 0.5) * 2 * a;
      sy = (rand(frame * 2.3 + 5) - 0.5) * 2 * a;
    }
  }
  return (
    <SpecContext.Provider value={SPEC_D}>
      <AbsoluteFill style={{background: '#000'}}>
        <AbsoluteFill style={{translate: `${sx}px ${sy}px`}}>
          <Papel />
          <Persona />
          {TITLES.filter((t) => t.scene).map((t) => (
            <Title key={t.id} t={t} />
          ))}
          <PersonCut />
          <Escenas />
          <Cierre />
          {TITLES.filter((t) => !t.scene).map((t) => (
            <Title key={t.id} t={t} />
          ))}
          <SmallSubs />
        </AbsoluteFill>
        {HOJAS.map((h) => (
          <Hoja key={h.t} at={h.t} dir={h.dir} />
        ))}
        <Destello times={DESTELLOS} />
        <Sonido />
      </AbsoluteFill>
    </SpecContext.Provider>
  );
};
