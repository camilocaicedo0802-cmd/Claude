import {AbsoluteFill} from 'remotion';
import {Broll} from './components/Broll';
import {Cards} from './components/Cards';
import {Collage} from './components/Collage';
import {Comentario} from './components/Comentario';
import {Confianza} from './components/Confianza';
import {Defocus} from './components/Defocus';
import {Final} from './components/Final';
import {Hud} from './components/Hud';
import {Movil} from './components/Movil';
import {Sonido} from './components/Sonido';
import {Subtitles} from './components/Subtitles';
import {Tachado, TachadoBg} from './components/Tachado';
import {Person, Talking} from './components/Talking';
import {Title} from './components/Title';
import {Transiciones} from './components/Transiciones';
import {TITLES} from './data';
import {C} from './theme';

/** Video 1 · "Nadie le compra a tu negocio" — edición al estilo de la referencia (ver estilo.md). */
export const Video1: React.FC = () => {
  const scene = TITLES.filter((t) => t.scene);
  const front = TITLES.filter((t) => !t.scene);
  return (
    <AbsoluteFill style={{background: C.black}}>
      <Talking />
      {/* títulos en escena: detrás de la persona (corrección §10.2) */}
      {scene.map((t) => <Title key={t.id} t={t} />)}
      <Person ranges={scene.map((t) => [t.start - 0.1, t.end + 0.1] as [number, number])} />
      <Broll />
      <Defocus />
      <TachadoBg />
      <Cards />
      <Tachado />
      <Movil />
      <Hud />
      <Collage />
      <Confianza />
      <Comentario />
      {front.map((t) => <Title key={t.id} t={t} />)}
      <Subtitles />
      <Final />
      <Transiciones />
      {/* viñeta suave */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,0.35) 100%)', pointerEvents: 'none'}} />
      <Sonido />
    </AbsoluteFill>
  );
};
