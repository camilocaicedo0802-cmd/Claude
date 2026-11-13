import {AbsoluteFill} from 'remotion';
import {Broll} from './Broll';
import {Cards} from './Cards';
import {Defocus} from './Defocus';
import {EndCard} from './EndCard';
import {Sonido} from './Sonido';
import {SpecContext} from './spec';
import {Subtitles} from './Subtitles';
import {Person, Talking} from './Talking';
import {Title} from './Title';
import {Transiciones} from './Transiciones';
import {Spec} from './types';
import {C} from '../v1/theme';

/**
 * Edición estándar (estilo.md): voz con jump cuts → títulos en escena detrás de la persona →
 * B-roll → desenfoque → tarjetas → escenas propias del video → títulos superpuestos →
 * subtítulos → cierre → transiciones → viñeta → sonido.
 */
export const EditVideo: React.FC<{spec: Spec; scenes?: React.ReactNode; underCards?: React.ReactNode}> = ({spec, scenes, underCards}) => {
  const scene = spec.titles.filter((t) => t.scene);
  const front = spec.titles.filter((t) => !t.scene);
  return (
    <SpecContext.Provider value={spec}>
      <AbsoluteFill style={{background: C.black}}>
        <Talking />
        {scene.map((t) => <Title key={t.id} t={t} />)}
        <Person ranges={scene.map((t) => [t.start - 0.1, t.end + 0.1] as [number, number])} />
        <Broll />
        <Defocus />
        {underCards}
        <Cards />
        {scenes}
        {front.map((t) => <Title key={t.id} t={t} />)}
        <Subtitles />
        <EndCard />
        <Transiciones />
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,0.35) 100%)', pointerEvents: 'none'}} />
        <Sonido />
      </AbsoluteFill>
    </SpecContext.Provider>
  );
};
