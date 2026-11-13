import {AbsoluteFill, useVideoConfig} from 'remotion';
import {Broll} from './components/Broll';
import {Cards} from './components/Cards';
import {Collage} from './components/Collage';
import {Comentario} from './components/Comentario';
import {Confianza} from './components/Confianza';
import {Defocus} from './components/Defocus';
import {Final} from './components/Final';
import {Hud} from './components/Hud';
import {Movil} from './components/Movil';
import {Silueta} from './components/Silueta';
import {Sonido} from './components/Sonido';
import {Subtitles} from './components/Subtitles';
import {Tachado} from './components/Tachado';
import {Talking} from './components/Talking';
import {Title} from './components/Title';
import {Transiciones} from './components/Transiciones';
import {TITLES} from './data';
import {sec} from './helpers';
import {C} from './theme';
import {SEGMENTS} from './timeline';

/** Video 1 · "Nadie le compra a tu negocio" — edición al estilo de la referencia (ver estilo.md). */
export const Video1: React.FC = () => {
  const {fps} = useVideoConfig();
  const behind = TITLES.filter((t) => t.behind);
  const front = TITLES.filter((t) => !t.behind);
  const seg23 = SEGMENTS[23];
  return (
    <AbsoluteFill style={{background: C.black}}>
      <Talking />
      <Broll />
      <Defocus />
      <Cards />
      <Tachado />
      <Movil />
      <Hud />
      <Collage />
      <Confianza />
      {/* texto detrás de la persona: título → silueta encima */}
      {behind.map((t) => <Title key={t.id} t={t} />)}
      {behind.map((t) => (
        <Silueta key={`s-${t.id}`} from={sec(t.start, fps)} to={seg23.start + (seg23.srcOut - seg23.srcIn)} />
      ))}
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
